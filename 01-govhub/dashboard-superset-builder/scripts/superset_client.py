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

    def create_chart(self, payload: dict, dry_run: bool = False) -> dict:
        """POST idempotente: procura por slice_name e compara o conteúdo.

        Achar pelo nome e seguir adiante não basta — um chart cujo dataset
        mudou continua na tela e só para de carregar, sem avisar ninguém.
        """
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
            and detalhe.get("params") == payload.get("params")
        )
        if igual:
            return {"acao": "inalterado", "slice_name": nome, "id": atual["id"]}
        if dry_run:
            return {"acao": "atualizaria", "slice_name": nome, "id": atual["id"]}
        self.s.put(
            f"{self.base}/api/v1/chart/{atual['id']}",
            json={
                "datasource_id": payload["datasource_id"],
                "datasource_type": payload["datasource_type"],
                "params": payload["params"],
            },
            timeout=TIMEOUT,
        )
        return {"acao": "atualizado", "slice_name": nome, "id": atual["id"]}

    def create_dashboard(self, payload: dict, chart_ids: list, dry_run: bool = False) -> dict:
        """POST de dashboard novo, com position_json montado a partir dos charts."""
        slug = payload.get("slug")
        if slug:
            existente = self.get_dashboard(slug)
            if existente:
                return {"acao": "inalterado", "slug": slug, "id": existente["id"]}
        charts = [{"id": i, "slice_name": (self.get_chart(i) or {}).get("slice_name", "")}
                  for i in chart_ids]
        corpo = dict(payload)
        corpo["position_json"] = json.dumps(build_position_json(charts))
        if dry_run:
            return {"acao": "criaria", "slug": slug, "id": None}
        novo = self.s.post(
            f"{self.base}/api/v1/dashboard/", json=corpo, timeout=TIMEOUT
        ).json()
        return {"acao": "criado", "slug": slug, "id": novo["id"]}

    def add_chart_to_dashboard(self, dashboard_ref, chart_id: int,
                               dry_run: bool = False) -> dict:
        """Lê o layout publicado, acrescenta o chart e reescreve.

        Ler antes é obrigatório: reescrever do zero apaga ajustes feitos na
        interface do Superset.
        """
        dash = self.get_dashboard(dashboard_ref)
        if dash is None:
            return {"acao": "dashboard_nao_encontrado", "id": None}
        atual = json.loads(dash.get("position_json") or "{}")
        existentes = [
            {"id": no["meta"]["chartId"], "slice_name": no["meta"].get("sliceName", "")}
            for no in atual.values()
            if isinstance(no, dict) and no.get("type") == "CHART"
        ]
        if any(c["id"] == chart_id for c in existentes):
            return {"acao": "inalterado", "id": dash["id"]}
        novo = self.get_chart(chart_id) or {}
        existentes.append({"id": chart_id, "slice_name": novo.get("slice_name", "")})
        if dry_run:
            return {"acao": "adicionaria", "id": dash["id"]}
        self.s.put(
            f"{self.base}/api/v1/dashboard/{dash['id']}",
            json={"position_json": json.dumps(build_position_json(existentes))},
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
