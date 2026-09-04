#!/usr/bin/env python3
"""Cliente REST do Superset para a skill dashboard-superset-builder.

Autenticação por cookie de sessão (nunca JWT) — o porquê está em
`references/superset-api.md`. Credenciais vêm do ambiente:
SUPERSET_URL, SUPERSET_USERNAME, SUPERSET_PASSWORD.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

import requests

TIMEOUT = 30


def rison_q(page: int = 0, page_size: int = 100, filters=None) -> str:
    """Monta o parâmetro `q` em Rison.

    `filters` é uma lista de triplas (coluna, operador, valor). A API ignora
    `page`/`page_size` soltos e devolve 20 itens em silêncio — daí o Rison.
    """
    partes = []
    if filters:
        clausulas = ",".join(f"(col:{c},opr:{o},value:{v})" for c, o, v in filters)
        partes.append(f"filters:!({clausulas})")
    partes.append(f"page:{page}")
    partes.append(f"page_size:{page_size}")
    return "(" + ",".join(partes) + ")"


LARGURA_COLUNA = 6  # o grid do Superset tem 12 colunas; 2 colunas => 6 cada
ALTURA_CHART = 50
COLUNAS_DO_GRID = 12


def build_position_json(charts: list) -> dict:
    """Monta ROOT → GRID → ROW → CHART com `meta` em TODO nó.

    Omitir `meta` em qualquer nó quebra a página inteira do Superset 6 com
    `n.meta is undefined`. Duas colunas por linha.
    """
    pos = {
        "DASHBOARD_VERSION_KEY": "v2",
        "ROOT_ID": {"type": "ROOT", "id": "ROOT_ID", "children": ["GRID_ID"], "meta": {}},
        "GRID_ID": {"type": "GRID", "id": "GRID_ID", "children": [],
                    "parents": ["ROOT_ID"], "meta": {}},
    }
    for i in range(0, len(charts), 2):
        linha = f"ROW-{i // 2}"
        pos["GRID_ID"]["children"].append(linha)
        pos[linha] = {
            "type": "ROW", "id": linha, "children": [],
            "parents": ["ROOT_ID", "GRID_ID"],
            "meta": {"background": "BACKGROUND_TRANSPARENT"},
        }
        for chart in charts[i:i + 2]:
            no = f"CHART-{chart['id']}"
            pos[linha]["children"].append(no)
            pos[no] = {
                "type": "CHART", "id": no, "children": [],
                "parents": ["ROOT_ID", "GRID_ID", linha],
                "meta": {
                    "chartId": chart["id"],
                    "width": LARGURA_COLUNA,
                    "height": ALTURA_CHART,
                    "sliceName": chart.get("slice_name", ""),
                },
            }
    return pos


# --- splice no layout já publicado ----------------------------------------
#
# `build_position_json` só serve para dashboard que ainda não tem layout.
# Quando já existe um, ele é a fonte da verdade: abas, markdown, colunas,
# divisores, larguras e alturas foram ajustados na interface e regenerar um
# grid canônico apagaria tudo isso. Daí o splice abaixo, que muta a árvore
# original e não toca em nenhum nó além da ROW que recebe o chart (e do pai
# que eventualmente ganha uma ROW nova).


def _nos(pos: dict) -> list:
    """Pares (id, nó) do layout, ignorando chaves escalares como a de versão."""
    if not isinstance(pos, dict):
        return []
    return [(k, v) for k, v in pos.items() if isinstance(v, dict) and "type" in v]


def _chart_ids_do_layout(pos: dict) -> set:
    """`chartId` de todo nó CHART. Nó sem `meta`/`chartId` é ignorado, não quebra."""
    ids = set()
    for _, no in _nos(pos):
        if no.get("type") != "CHART":
            continue
        chart_id = (no.get("meta") or {}).get("chartId")
        if chart_id is not None:
            ids.add(chart_id)
    return ids


def _ordem_da_arvore(pos: dict) -> list:
    """Ids na ordem em que aparecem nos `children`, descendo a partir do ROOT.

    É essa ordem que define qual é a "última" ROW. Nós órfãos (não alcançáveis
    pela raiz) vão para o fim, na ordem de inserção do dicionário.
    """
    ordem, vistos = [], set()

    def desce(id_):
        if id_ in vistos or not isinstance(pos.get(id_), dict):
            return
        vistos.add(id_)
        ordem.append(id_)
        for filho in pos[id_].get("children") or []:
            desce(filho)

    raizes = [k for k, no in _nos(pos) if no.get("type") == "ROOT"] or ["ROOT_ID"]
    for raiz in raizes:
        desce(raiz)
    for chave, _ in _nos(pos):
        if chave not in vistos:
            ordem.append(chave)
    return ordem


def _id_livre(pos: dict, prefixo: str) -> str:
    """`<prefixo><n>` com o menor `n` que ainda não existe — determinístico."""
    n = 0
    while f"{prefixo}{n}" in pos:
        n += 1
    return f"{prefixo}{n}"


def _pai_de(pos: dict, id_: str):
    """Quem tem `id_` em `children`. Cai para `parents[-1]` se ninguém tiver."""
    for chave, no in _nos(pos):
        if id_ in (no.get("children") or []):
            return chave
    parents = (pos.get(id_) or {}).get("parents") or []
    return parents[-1] if parents else None


def _container_para_row(pos: dict, ordem: list):
    """Onde pendurar uma ROW quando o layout não tem nenhuma: GRID, senão TAB."""
    for tipo in ("GRID", "TAB"):
        for chave in ordem:
            if (pos.get(chave) or {}).get("type") == tipo:
                return chave
    return None


def inserir_chart_no_layout(pos: dict, chart_id: int, slice_name: str = "") -> dict:
    """Insere um CHART na árvore existente sem tocar em nenhum outro nó."""
    if not isinstance(pos, dict):
        pos = {}
    if chart_id in _chart_ids_do_layout(pos):
        return pos
    if not _nos(pos):
        return build_position_json([{"id": chart_id, "slice_name": slice_name}])

    ordem = _ordem_da_arvore(pos)
    linhas = [i for i in ordem if (pos.get(i) or {}).get("type") == "ROW"]

    destino, largura = None, LARGURA_COLUNA
    if linhas:
        ultima = linhas[-1]
        usada = 0
        for filho in pos[ultima].get("children") or []:
            meta = (pos.get(filho) or {}).get("meta") or {}
            usada += meta.get("width") or LARGURA_COLUNA
        sobra = COLUNAS_DO_GRID - usada
        if sobra >= LARGURA_COLUNA:
            destino, largura = ultima, min(LARGURA_COLUNA, sobra)

    if destino is None:
        if linhas:
            pai = _pai_de(pos, linhas[-1])
            parents_row = list(pos[linhas[-1]].get("parents") or [])
            if not parents_row and pai:
                parents_row = list((pos.get(pai) or {}).get("parents") or []) + [pai]
        else:
            pai = _container_para_row(pos, ordem)
            parents_row = (list((pos.get(pai) or {}).get("parents") or []) + [pai]
                           if pai else [])
        if not isinstance(pos.get(pai), dict):
            # Árvore sem lugar reconhecível para uma ROW: melhor um layout
            # canônico com o chart novo do que um PUT que o Superset não abre.
            return build_position_json([{"id": chart_id, "slice_name": slice_name}])
        destino = _id_livre(pos, "ROW-")
        pos[destino] = {
            "type": "ROW", "id": destino, "children": [],
            "parents": parents_row,
            "meta": {"background": "BACKGROUND_TRANSPARENT"},
        }
        pos[pai]["children"] = list(pos[pai].get("children") or []) + [destino]

    chave = f"CHART-{chart_id}"
    if chave in pos:  # id ocupado por outro nó: não sobrescreve, arruma outro
        chave = _id_livre(pos, f"CHART-{chart_id}-")
    pos[destino]["children"] = list(pos[destino].get("children") or []) + [chave]
    pos[chave] = {
        "type": "CHART", "id": chave, "children": [],
        "parents": list(pos[destino].get("parents") or []) + [destino],
        "meta": {
            "chartId": chart_id,
            "width": largura,
            "height": ALTURA_CHART,
            "sliceName": slice_name,
        },
    }
    return pos


def _layout_do_dashboard(dash: dict):
    """Devolve (layout, valido). `position_json` ilegível => (…, False).

    Layout ausente ou vazio é normal (dashboard novo) e vale `({}, True)`.
    JSON quebrado não pode virar rebuild silencioso: não dá para preservar o
    que não dá para ler, então o chamador recusa a escrita em vez de apagar.
    """
    bruto = (dash or {}).get("position_json") or ""
    if not str(bruto).strip():
        return {}, True
    try:
        pos = json.loads(bruto)
    except (TypeError, ValueError):
        return {}, False
    if pos is None:
        return {}, True
    if not isinstance(pos, dict):
        return {}, False
    return pos, True


def _params_iguais(a, b) -> bool:
    """Compara `params` como JSON; se algum lado não for JSON, compara string."""
    try:
        return json.loads(a) == json.loads(b)
    except (TypeError, ValueError):
        return a == b


class SupersetClient:
    def __init__(self, base_url: str, username: str, password: str, session=None):
        self.base = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.s = session if session is not None else requests.Session()

    # --- autenticação ------------------------------------------------------

    def login(self) -> None:
        """Autentica por formulário e fixa X-CSRFToken e Referer na sessão."""
        pagina = self.s.get(f"{self.base}/login/", timeout=TIMEOUT)
        campo = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', pagina.text or "")
        self.s.post(
            f"{self.base}/login/",
            timeout=TIMEOUT,
            data={
                "username": self.username,
                "password": self.password,
                "csrf_token": campo.group(1) if campo else "",
            },
        )
        token = self.s.get(
            f"{self.base}/api/v1/security/csrf_token/", timeout=TIMEOUT
        ).json()["result"]
        self.s.headers["X-CSRFToken"] = token
        # O Superset recusa escrita sem Referer.
        self.s.headers["Referer"] = self.base

    # --- leitura -----------------------------------------------------------

    def list_all(self, resource: str, filters=None) -> list:
        """Percorre todas as páginas de /api/v1/<resource>/."""
        pagina, saida = 0, []
        while True:
            r = self.s.get(
                f"{self.base}/api/v1/{resource}/",
                params={"q": rison_q(pagina, 100, filters)},
                timeout=TIMEOUT,
            )
            corpo = r.json()
            resultados = corpo.get("result", [])
            saida += resultados
            if not resultados or len(saida) >= corpo.get("count", 0):
                return saida
            pagina += 1

    def _get_result(self, caminho: str):
        """GET que devolve `result`, ou None em 404 (não é erro: é 'não existe')."""
        r = self.s.get(f"{self.base}{caminho}", timeout=TIMEOUT)
        if r.status_code == 404:
            return None
        return r.json()["result"]

    def get_dataset(self, id_):
        return self._get_result(f"/api/v1/dataset/{id_}")

    def get_dashboard(self, ref):
        """Aceita slug ou id. Nunca usa a listagem: ela pode omitir dashboards."""
        return self._get_result(f"/api/v1/dashboard/{ref}")

    def get_chart(self, id_):
        return self._get_result(f"/api/v1/chart/{id_}")

    # --- escrita (nunca antes da aprovação humana da Fase 3) ---------------

    @staticmethod
    def _validar_datasource(payload: dict) -> None:
        """`params.datasource` tem que bater com `datasource_id`.

        Divergentes, o Superset aceita o POST e cria um chart que não carrega.
        Falhar alto é o certo: cada componente é uma invocação separada do CLI,
        então o erro para só este e os outros seguem.
        """
        datasource_id = payload.get("datasource_id")
        if datasource_id is None:
            return
        try:
            params = json.loads(payload.get("params") or "null")
        except (TypeError, ValueError):
            return
        if not isinstance(params, dict) or not params.get("datasource"):
            return
        esperado = f"{datasource_id}__table"
        if params["datasource"] != esperado:
            raise ValueError(
                f"params.datasource ({params['datasource']}) não bate com "
                f"datasource_id ({datasource_id}); esperado {esperado}"
            )

    def _resumo_do_chart(self, chart_id: int) -> dict:
        return {"id": chart_id,
                "slice_name": (self.get_chart(chart_id) or {}).get("slice_name", "")}

    def create_chart(self, payload: dict, dry_run: bool = False) -> dict:
        """POST idempotente: procura por slice_name e compara o conteúdo.

        Achar pelo nome e seguir adiante não basta — um chart cujo dataset
        mudou continua na tela e só para de carregar, sem avisar ninguém.
        """
        self._validar_datasource(payload)
        nome = payload["slice_name"]
        atual = next(
            (c for c in self.list_all("chart") if c.get("slice_name") == nome), None
        )
        if atual is None:
            if dry_run:
                return {"acao": "criaria", "slice_name": nome, "id": None}
            novo = self.s.post(
                f"{self.base}/api/v1/chart/", json=payload, timeout=TIMEOUT
            ).json()
            return {"acao": "criado", "slice_name": nome, "id": novo["id"]}

        detalhe = self.get_chart(atual["id"]) or {}
        igual = (
            atual.get("datasource_id") == payload.get("datasource_id")
            # como JSON: o Superset reserializa `params` e a comparação de
            # string crua forçaria um PUT a cada execução.
            and _params_iguais(detalhe.get("params"), payload.get("params"))
        )
        if igual:
            return {"acao": "inalterado", "slice_name": nome, "id": atual["id"]}
        if dry_run:
            return {"acao": "atualizaria", "slice_name": nome, "id": atual["id"]}
        # Payload inteiro: mandar só datasource/params deixaria viz_type,
        # slice_name e description velhos num run que se reporta "atualizado".
        self.s.put(
            f"{self.base}/api/v1/chart/{atual['id']}",
            json=dict(payload),
            timeout=TIMEOUT,
        )
        return {"acao": "atualizado", "slice_name": nome, "id": atual["id"]}

    def _achar_dashboard(self, payload: dict):
        """Procura por slug; sem slug, pelo `dashboard_title` na listagem.

        Sem essa segunda busca não há idempotência nenhuma para dashboard sem
        slug: cada execução criaria uma cópia.
        """
        slug = payload.get("slug")
        if slug:
            return self.get_dashboard(slug)
        titulo = payload.get("dashboard_title")
        if not titulo:
            return None
        achado = next(
            (d for d in self.list_all("dashboard")
             if d.get("dashboard_title") == titulo),
            None,
        )
        if achado is None:
            return None
        # A listagem não traz position_json; o detalhe traz.
        detalhe = self.get_dashboard(achado["id"])
        return detalhe if isinstance(detalhe, dict) else achado

    def create_dashboard(self, payload: dict, chart_ids: list, dry_run: bool = False) -> dict:
        """POST/PUT idempotente: compara conteúdo, não só existência.

        Achar pelo nome e seguir adiante não basta aqui tampouco — um dashboard
        cujo título ou cujos charts mudaram nunca seria atualizado.
        """
        slug = payload.get("slug")
        existente = self._achar_dashboard(payload)

        if existente is None:
            corpo = dict(payload)
            corpo["position_json"] = json.dumps(
                build_position_json([self._resumo_do_chart(i) for i in chart_ids])
            )
            if dry_run:
                return {"acao": "criaria", "slug": slug, "id": None}
            novo = self.s.post(
                f"{self.base}/api/v1/dashboard/", json=corpo, timeout=TIMEOUT
            ).json()
            return {"acao": "criado", "slug": slug, "id": novo["id"]}

        id_ = existente.get("id")
        pos, valido = _layout_do_dashboard(existente)
        if not valido:
            return {"acao": "layout_invalido", "slug": slug, "id": id_}

        publicados = _chart_ids_do_layout(pos)
        faltando = [i for i in chart_ids if i not in publicados]
        titulo = payload.get("dashboard_title")
        titulo_igual = not titulo or existente.get("dashboard_title") == titulo
        if titulo_igual and not faltando:
            return {"acao": "inalterado", "slug": slug, "id": id_}
        if dry_run:
            return {"acao": "atualizaria", "slug": slug, "id": id_}

        corpo = dict(payload)
        if pos:
            # Mesmo motivo do add_chart_to_dashboard: o layout publicado é a
            # fonte da verdade, o novo chart entra nele.
            for i in faltando:
                pos = inserir_chart_no_layout(
                    pos, i, self._resumo_do_chart(i)["slice_name"])
        else:
            pos = build_position_json([self._resumo_do_chart(i) for i in chart_ids])
        corpo["position_json"] = json.dumps(pos)
        self.s.put(f"{self.base}/api/v1/dashboard/{id_}", json=corpo, timeout=TIMEOUT)
        return {"acao": "atualizado", "slug": slug, "id": id_}

    def add_chart_to_dashboard(self, dashboard_ref, chart_id: int,
                               dry_run: bool = False) -> dict:
        """Lê o layout publicado, insere o chart nele e dá PUT na árvore mutada.

        Ler antes é obrigatório: reescrever do zero apaga ajustes feitos na
        interface do Superset (abas, markdown, colunas, larguras, alturas).
        """
        dash = self.get_dashboard(dashboard_ref)
        if dash is None:
            return {"acao": "dashboard_nao_encontrado", "id": None}
        pos, valido = _layout_do_dashboard(dash)
        if not valido:
            return {"acao": "layout_invalido", "id": dash.get("id")}
        if chart_id in _chart_ids_do_layout(pos):
            return {"acao": "inalterado", "id": dash["id"]}
        novo = self.get_chart(chart_id) or {}
        if dry_run:
            return {"acao": "adicionaria", "id": dash["id"]}
        pos = inserir_chart_no_layout(pos, chart_id, novo.get("slice_name", ""))
        self.s.put(
            f"{self.base}/api/v1/dashboard/{dash['id']}",
            json={"position_json": json.dumps(pos)},
            timeout=TIMEOUT,
        )
        return {"acao": "adicionado", "id": dash["id"]}


def cliente_do_ambiente() -> SupersetClient:
    """Constrói o cliente a partir do ambiente e já autentica."""
    url = os.environ.get("SUPERSET_URL") or os.environ.get("SUPERSET_HOST_PORT")
    usuario = os.environ.get("SUPERSET_USERNAME")
    senha = os.environ.get("SUPERSET_PASSWORD")
    faltando = [
        nome
        for nome, valor in (
            ("SUPERSET_URL", url),
            ("SUPERSET_USERNAME", usuario),
            ("SUPERSET_PASSWORD", senha),
        )
        if not valor
    ]
    if faltando:
        sys.exit(f"Variáveis de ambiente ausentes: {', '.join(faltando)}")
    c = SupersetClient(url, usuario, senha)
    c.login()
    return c


def _imprimir(valor) -> None:
    print(json.dumps(valor, indent=2, ensure_ascii=False))


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Cliente REST do Superset.")
    sub = p.add_subparsers(dest="comando", required=True)

    q = sub.add_parser("list-datasets", help="Lista datasets (paginação Rison).")
    q.add_argument("--filtro", help="Substring do table_name.")

    q = sub.add_parser("get-dataset", help="Colunas e métricas de um dataset.")
    q.add_argument("id")

    q = sub.add_parser("get-dashboard", help="Dashboard por slug ou id.")
    q.add_argument("ref")

    q = sub.add_parser("get-chart", help="params/form_data reais de um chart.")
    q.add_argument("id")

    q = sub.add_parser("create-chart", help="Cria/atualiza um chart (idempotente).")
    q.add_argument("--file", required=True, help="JSON com o payload do chart.")
    q.add_argument("--dry-run", action="store_true")

    q = sub.add_parser("create-dashboard", help="Cria um dashboard novo.")
    q.add_argument("--file", required=True,
                   help='JSON com {"payload": {…}, "chart_ids": [1,2]}.')
    q.add_argument("--dry-run", action="store_true")

    q = sub.add_parser("add-chart-to-dashboard", help="Acrescenta um chart a um dashboard.")
    q.add_argument("ref")
    q.add_argument("chart_id", type=int)
    q.add_argument("--dry-run", action="store_true")

    args = p.parse_args(argv)
    c = cliente_do_ambiente()

    if args.comando == "list-datasets":
        filtros = [("table_name", "ct", args.filtro)] if args.filtro else None
        _imprimir(c.list_all("dataset", filtros))
    elif args.comando == "get-dataset":
        _imprimir(c.get_dataset(args.id))
    elif args.comando == "get-dashboard":
        _imprimir(c.get_dashboard(args.ref))
    elif args.comando == "get-chart":
        _imprimir(c.get_chart(args.id))
    elif args.comando == "create-chart":
        with open(args.file, encoding="utf-8") as fh:
            _imprimir(c.create_chart(json.load(fh), dry_run=args.dry_run))
    elif args.comando == "create-dashboard":
        with open(args.file, encoding="utf-8") as fh:
            entrada = json.load(fh)
        _imprimir(c.create_dashboard(entrada["payload"], entrada["chart_ids"],
                                     dry_run=args.dry_run))
    elif args.comando == "add-chart-to-dashboard":
        _imprimir(c.add_chart_to_dashboard(args.ref, args.chart_id,
                                           dry_run=args.dry_run))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
