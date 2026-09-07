#!/usr/bin/env python3
"""Cliente REST do Superset para a skill dashboard-superset-builder.

Autenticação por cookie de sessão (nunca JWT) — o porquê está em
`references/superset-api.md`. Credenciais vêm do ambiente:
SUPERSET_URL, SUPERSET_USERNAME, SUPERSET_PASSWORD.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import re
import sys
import time

import requests

TIMEOUT = 30


def rison_valor(valor) -> str:
    """Serializa um valor Python para Rison.

    String vai entre aspas simples, com `!` e `'` internos escapados (`!!` e
    `!'`) — sem isso um valor com espaço ("consumo de agua") produz Rison
    malformado, a API devolve 400 e a busca é lida como "não existe".
    Números vão nus; booleanos e `None` viram os literais `!t`/`!f`/`!n`.
    """
    if valor is None:
        return "!n"
    if isinstance(valor, bool):
        return "!t" if valor else "!f"
    if isinstance(valor, (int, float)):
        return str(valor)
    return "'" + str(valor).replace("!", "!!").replace("'", "!'") + "'"


def rison_q(page: int = 0, page_size: int = 100, filters=None) -> str:
    """Monta o parâmetro `q` em Rison.

    `filters` é uma lista de triplas (coluna, operador, valor). A API ignora
    `page`/`page_size` soltos e devolve 20 itens em silêncio — daí o Rison.
    Todo valor passa por `rison_valor`; colunas e operadores são identificadores
    e vão crus.
    """
    partes = []
    if filters:
        clausulas = ",".join(
            f"(col:{c},opr:{o},value:{rison_valor(v)})" for c, o, v in filters
        )
        partes.append(f"filters:!({clausulas})")
    partes.append(f"page:{rison_valor(page)}")
    partes.append(f"page_size:{rison_valor(page_size)}")
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


class LayoutSemLugarParaRow(Exception):
    """O layout publicado não tem GRID nem TAB onde pendurar uma ROW.

    Regenerar um grid canônico aqui apagaria o conteúdo publicado (markdown,
    abas, divisores). Recusar a escrita é estritamente melhor: o chamador
    devolve `layout_sem_lugar_para_row` sem tocar no dashboard.
    """


class ChartNaoEncontrado(Exception):
    """Chart id não existe (404 em `get_chart`).

    Deixar passar viraria um nó CHART fantasma na position_json publicada —
    a mesma razão pela qual `add_chart_to_dashboard` já recusa esse caso.
    """

    def __init__(self, chart_id):
        self.chart_id = chart_id
        super().__init__(f"chart {chart_id} não encontrado")


def _container_para_row(pos: dict, ordem: list):
    """Onde pendurar uma ROW quando o layout não tem nenhuma: GRID, senão TAB."""
    for tipo in ("GRID", "TAB"):
        for chave in ordem:
            if (pos.get(chave) or {}).get("type") == tipo:
                return chave
    return None


def inserir_chart_no_layout(pos: dict, chart_id: int, slice_name: str = "") -> dict:
    """Insere um CHART na árvore existente sem tocar em nenhum outro nó.

    Levanta `LayoutSemLugarParaRow` quando a árvore existe mas não tem nenhum
    container onde uma ROW caiba.
    """
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
            destino, largura = ultima, LARGURA_COLUNA

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
            # Árvore sem lugar reconhecível para uma ROW. Regenerar o grid
            # canônico aqui descartaria o conteúdo publicado — recusa.
            raise LayoutSemLugarParaRow(
                "layout publicado não tem GRID nem TAB onde inserir uma ROW"
            )
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


VIZ_SUPORTADOS = {
    "big_number_total",
    "country_map",
    "echarts_timeseries_bar",
    "mixed_timeseries",
    "pie",
    "table",
}

BASE_QUERY = {
    "annotation_layers": [],
    "applied_time_extras": {},
    "custom_form_data": {},
    "custom_params": {},
    "extras": {"having": "", "where": ""},
    "order_desc": True,
    "series_limit": 0,
    "url_params": {},
}


def _filtro_simples(adhoc: dict, campo: str) -> dict:
    """Converte um adhoc_filter SIMPLE para o `{col, op, val}` do query_context.

    Recusa alto o que não sabe converter — expressão SQL (`expressionType:
    "SQL"`), ou SIMPLE sem `subject`/`operator`. Descartar em silêncio (o
    contrato anterior) era o mesmo defeito que o query_context existe para
    evitar: o chart era criado, abria sem erro, o filtro não aplicava e o
    número saía errado — e como o query_context derivado ficava estável, a
    idempotência reportava "inalterado" para sempre e nunca reparava nada.
    """
    if (adhoc.get("expressionType") != "SIMPLE"
            or not adhoc.get("operator")
            or adhoc.get("subject") is None):
        raise ValueError(
            f"{campo} tem um filtro que não sabemos converter para o "
            f"query_context: {json.dumps(adhoc, ensure_ascii=False)}. Só filtro "
            f"SIMPLE com `subject` e `operator` vira `{{col, op, val}}` — um "
            f"`sqlExpression` (expressionType SQL) precisa ser reescrito como "
            f"filtro SIMPLE no params antes de criar o chart. Descartá-lo daria "
            f"um chart que abre, não aplica o filtro e devolve o número errado."
        )
    return {"col": adhoc["subject"], "op": adhoc["operator"],
            "val": adhoc.get("comparator")}


def _filtros_do_params(fd: dict, campo: str) -> list:
    return [_filtro_simples(a, campo) for a in fd.get(campo) or []]


def _modo_raw(fd: dict) -> bool:
    """`True` quando a tabela roda em modo `raw` (não agrega, colunas vêm de
    `all_columns`).

    Só `table` tem modo `raw` — `query_mode` é controle de tabela no Superset, e
    honrá-lo em qualquer outro viz_type não tem uso legítimo. Para todo tipo que
    não seja `table` a resposta é `False`: `query_mode` é ignorado por completo e
    a query segue a precedência normal `entity` > `x_axis` > `groupby` com as
    métricas intactas. Sem essa porta fechada um `query_mode` órfão vazava para
    outros tipos — o Explore mantém chaves estranhas no `form_data` quando se
    troca o tipo de visualização, e uma troca `table`→`pie` carrega `query_mode`
    junto de `all_columns`; o `SKILL.md` ainda manda usar o `params` de um chart
    existente como referência. Um `pie` assim perdia a métrica e agrupava pela
    coluna errada — query que abre sem erro e devolve número errado.

    Dentro de `table`: com `query_mode` explícito a resposta é ele mesmo. Sem a
    chave, espelha o `get_query_mode` do Superset: um `all_columns` não-vazio é
    modo `raw`. O `SKILL.md` orienta o autor a mexer em `groupby`/`all_columns` e
    nunca cita `query_mode`, então tabelas raw reais chegam sem a chave — sem
    esta inferência elas derivariam as colunas de `groupby` (vazio), manteriam as
    métricas, e o chart abriria devolvendo as linhas erradas sem erro nenhum.
    """
    if fd.get("viz_type") != "table":
        return False
    modo = fd.get("query_mode")
    if modo:
        return modo == "raw"
    return bool(fd.get("all_columns"))


def _colunas_do_params(fd: dict, chave_groupby: str = "groupby") -> list:
    """Colunas da query.

    `query_mode` só conta em `table` (é controle de tabela no Superset); em
    qualquer outro viz_type a chave é ignorada por completo. Numa tabela ele
    manda: `raw` lê `all_columns`, `aggregate` lê o groupby — que pode trazer
    colunas adhoc (`{label, sqlExpression, expressionType}`), repassadas como
    estão porque o query_context as aceita. Sem `query_mode` (ou fora de
    `table`), um `all_columns` não-vazio numa tabela ainda é modo `raw` (o
    Superset infere assim); só então vale a precedência `entity` (mapas) >
    `x_axis` (séries) > groupby. `chave_groupby` existe para a série B do
    `mixed_timeseries`, que agrupa por `groupby_b` — usar o groupby da série A
    agruparia a série B pela dimensão errada; a inferência de `raw` não se
    aplica a ela.
    """
    modo = fd.get("query_mode") if fd.get("viz_type") == "table" else None
    if modo == "raw" or (chave_groupby == "groupby" and _modo_raw(fd)):
        return list(fd.get("all_columns") or [])
    if modo == "aggregate":
        return list(fd.get(chave_groupby) or [])
    if fd.get("entity"):
        return [fd["entity"]]
    colunas = list(fd.get(chave_groupby) or [])
    if fd.get("x_axis"):
        colunas = [fd["x_axis"]] + [c for c in colunas if c != fd["x_axis"]]
    return colunas


def _query(metrics, colunas, filtros, row_limit=None) -> dict:
    # deepcopy: `dict(BASE_QUERY)` é cópia rasa e todas as queries emitidas
    # passariam a compartilhar o mesmo objeto `extras`, então um caller que
    # mutasse uma query corromperia o global do módulo.
    q = copy.deepcopy(BASE_QUERY)
    q.update({"filters": filtros, "metrics": metrics, "columns": colunas})
    if row_limit:
        q["row_limit"] = row_limit
    return q


def build_query_context(payload: dict) -> str:
    """Deriva o query_context do params.

    Sem ele, a API de dados do Superset ignora os adhoc_filters: o chart é
    criado, abre sem erro e devolve o número errado. Ver
    `references/superset-api.md`, seção "query_context".

    Recusa alto tudo o que não sabe derivar (viz_type fora da lista, filtro que
    não vira `{col, op, val}`, `percent_metrics` não verificado): como isto roda
    antes de qualquer HTTP do `create_chart`, o chart errado nem chega a existir.
    """
    if payload.get("params") is None:
        raise ValueError(
            "payload sem `params`: ele é obrigatório para montar o query_context "
            "— colunas, métricas e filtros saem todos de lá. Inclua o `params` "
            "(form_data do chart, como string JSON) no payload."
        )
    if payload.get("datasource_id") is None:
        raise ValueError(
            "payload sem `datasource_id`: ele é obrigatório para montar o "
            "query_context — a API de dados precisa saber sobre qual dataset "
            "rodar a query. Inclua o id do dataset no payload."
        )
    fd = json.loads(payload["params"])
    viz = fd.get("viz_type")
    if viz not in VIZ_SUPORTADOS:
        raise ValueError(
            f"viz_type {viz!r} não está na lista que sabemos montar "
            f"({sorted(VIZ_SUPORTADOS)}). Confira a forma real de um chart desse "
            f"tipo (get-chart num que já exista) antes de acrescentá-lo à lista — "
            f"adivinhar gera uma query silenciosamente errada."
        )
    if fd.get("percent_metrics"):
        raise ValueError(
            f"percent_metrics não-vazio "
            f"({json.dumps(fd['percent_metrics'], ensure_ascii=False)}) e a forma "
            f"dele no query_context não foi verificada em nenhum chart real. "
            f"Tire-o do params, ou leia um chart existente que use percent_metrics "
            f"(get-chart) e ensine a derivação antes de usá-lo — adivinhar gera "
            f"uma query silenciosamente errada."
        )
    filtros = _filtros_do_params(fd, "adhoc_filters")
    colunas = _colunas_do_params(fd)
    if viz == "mixed_timeseries":
        queries = [
            _query(fd.get("metrics") or [], colunas, filtros, fd.get("row_limit")),
            _query(fd.get("metrics_b") or [],
                   _colunas_do_params(fd, "groupby_b"),
                   _filtros_do_params(fd, "adhoc_filters_b"),
                   fd.get("row_limit_b")),
        ]
    else:
        # Modo `raw` não agrega: o query_context real desses charts traz
        # `metrics: []` mesmo quando o params carrega métricas de resto. Vale
        # também para o `raw` inferido — `all_columns` não-vazio sem
        # `query_mode` — senão a query sairia agregando o que o chart lista cru.
        if _modo_raw(fd):
            metrics = []
        else:
            metrics = fd.get("metrics") or (
                [fd["metric"]] if fd.get("metric") else [])
        queries = [_query(metrics, colunas, filtros, fd.get("row_limit"))]
    return json.dumps(
        {
            "datasource": {"id": payload["datasource_id"],
                           "type": payload.get("datasource_type", "table")},
            "force": False,
            "form_data": fd,
            "queries": queries,
            "result_format": "json",
            "result_type": "full",
        },
        ensure_ascii=False,
    )


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
        """Percorre todas as páginas de /api/v1/<resource>/.

        Erro HTTP estoura: o corpo de erro do Superset não tem `result` nem
        `count`, então engolir o status devolveria lista vazia e a busca de
        idempotência concluiria "não existe" — duplicando o que já está lá.
        """
        pagina, saida = 0, []
        while True:
            r = self.s.get(
                f"{self.base}/api/v1/{resource}/",
                params={"q": rison_q(pagina, 100, filters)},
                timeout=TIMEOUT,
            )
            r.raise_for_status()
            corpo = r.json()
            resultados = corpo.get("result", [])
            saida += resultados
            if not resultados or len(saida) >= corpo.get("count", 0):
                return saida
            pagina += 1

    def _get_result(self, caminho: str):
        """GET que devolve `result`, ou None em 404 (não é erro: é 'não existe').

        Qualquer outro erro HTTP estoura: 401 de sessão expirada ou 500 não
        podem ser lidos como "não existe" e virar uma criação duplicada.
        """
        r = self.s.get(f"{self.base}{caminho}", timeout=TIMEOUT)
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()["result"]

    def get_dataset(self, id_):
        return self._get_result(f"/api/v1/dataset/{id_}")

    def get_dashboard(self, ref):
        """Aceita slug ou id. Nunca usa a listagem: ela pode omitir dashboards."""
        return self._get_result(f"/api/v1/dashboard/{ref}")

    def get_chart(self, id_):
        return self._get_result(f"/api/v1/chart/{id_}")

    def dados_do_chart(self, chart_id: int) -> dict:
        """Lê o que o chart devolve de verdade, para conferir o que foi escrito.

        `GET /api/v1/chart/<id>/data/` responde `result[0].rowcount` e
        `result[0].data`. Timeout maior que o padrão: aqui roda uma consulta.
        """
        r = self.s.get(f"{self.base}/api/v1/chart/{chart_id}/data/", timeout=60)
        r.raise_for_status()
        primeiro = (r.json().get("result") or [{}])[0]
        dados = primeiro.get("data") or []
        return {"rowcount": primeiro.get("rowcount", len(dados)),
                "amostra": dados[0] if dados else None}

    def _verificacao(self, chart_id: int) -> dict:
        """Confere o que o chart devolve; um erro aqui não invalida a escrita."""
        try:
            return self.dados_do_chart(chart_id)
        except Exception as e:  # a escrita já aconteceu: reportar, não mascarar
            return {"erro": f"{type(e).__name__}: {e}"}

    # --- escrita (nunca antes de uma aprovação humana explícita) -----------

    def _escrever(self, metodo: str, caminho: str, corpo: dict):
        """POST/PUT que **estoura** quando a API recusa.

        Sem `raise_for_status`, um 422 (sessão expirada ou CSRF vencido no meio
        de uma rodada de componentes) passava em silêncio e virava coisa pior
        que silêncio: `create_chart` devolvia `atualizado` com uma `verificacao`
        lida do chart **velho** — número plausível, conteúdo antigo — e o
        `SKILL.md` diz ao agente que esse campo é a evidência de que a escrita
        entrou. A salvaguarda confirmava a escrita que não aconteceu.

        Vale também para os POSTs, que sem isto quebravam como `KeyError: 'id'`
        cru ao tentar ler o corpo de erro.
        """
        r = getattr(self.s, metodo)(
            f"{self.base}{caminho}", json=corpo, timeout=TIMEOUT)
        r.raise_for_status()
        return r

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
        """Resolve nome do chart para a position_json — falha se o id não existe.

        `get_chart(i) or {}` (contrato anterior) engolia um 404 e deixava um
        `chart_id` inexistente virar nó CHART fantasma no layout publicado. É
        o mesmo defeito que `add_chart_to_dashboard` já recusa; aqui é o ponto
        único por onde passam tanto o caminho de criação quanto o de
        atualização de `create_dashboard`, então a checagem entra uma vez só.
        """
        chart = self.get_chart(chart_id)
        if chart is None:
            raise ChartNaoEncontrado(chart_id)
        return {"id": chart_id, "slice_name": chart.get("slice_name", "")}

    def _charts_do_fonte(self, fonte_id: int) -> set:
        """Ids de chart que aparecem no `position_json` do dashboard fonte.

        A lista `dashboards` do chart seria a fonte natural, mas é exatamente o
        campo que o defeito D4 deixava vazio: um dashboard construído por esta
        ferramenta **antes** daquele fix tem o layout cheio e o
        `dashboard_slices` vazio, então todos os charts dele reportam
        `dashboards: []` e a guarda do `--fonte` não dispararia — justo no caso
        em que re-derivar é mais provável. O layout não depende da associação.
        """
        fonte = self.get_dashboard(fonte_id)
        if fonte is None:
            return set()
        pos, valido = _layout_do_dashboard(fonte)
        return _chart_ids_do_layout(pos) if valido else set()

    def _associar_chart(self, chart_id: int, dashboard_id: int) -> None:
        """Anexa o chart ao dashboard, acrescentando à lista existente.

        Layout e associação são coisas separadas: o `position_json` diz onde o
        chart fica, mas quem o anexa é `dashboard_slices` — sem isto o dashboard
        abre vazio. Ver `references/superset-api.md`, "Layout não é associação".

        Acrescenta, nunca substitui: `PUT {"dashboards": [novo]}` num chart que
        também estava em outro dashboard o arrancaria de lá.
        """
        chart = self.get_chart(chart_id)
        if chart is None:
            raise ChartNaoEncontrado(chart_id)
        atuais = [d.get("id") for d in (chart.get("dashboards") or [])
                  if d.get("id") is not None]
        if dashboard_id in atuais:
            return
        self._escrever("put", f"/api/v1/chart/{chart_id}",
                       {"dashboards": atuais + [dashboard_id]})

    def create_chart(self, payload: dict, dry_run: bool = False,
                     fonte_id: int | None = None) -> dict:
        """POST idempotente: procura por slice_name + datasource_id.

        Só é "o mesmo chart" quando nome e dataset batem: um `slice_name`
        genérico ("Total do Período") que já existe em outro dashboard, sobre
        outro dataset, não pode ser sobrescrito em silêncio. Consequência
        aceita: um chart cujo dataset mudou é criado como novo, não atualizado.
        """
        self._validar_datasource(payload)
        payload = dict(payload)
        payload["query_context"] = build_query_context(payload)
        nome = payload["slice_name"]
        datasource_id = payload.get("datasource_id")
        atual = next(
            (c for c in self.list_all("chart")
             if c.get("slice_name") == nome
             and c.get("datasource_id") == datasource_id),
            None,
        )
        if atual is None:
            if dry_run:
                return {"acao": "criaria", "slice_name": nome, "id": None}
            novo = self._escrever("post", "/api/v1/chart/", payload).json()
            return {"acao": "criado", "slice_name": nome, "id": novo["id"],
                    "verificacao": self._verificacao(novo["id"])}

        detalhe = self.get_chart(atual["id"]) or {}
        # Re-derivar um dashboard propõe nomes parecidos com os do fonte. Como a
        # idempotência casa por (nome + dataset), um nome repetido atualizaria o
        # chart do fonte — alterando por dentro o dashboard que prometemos não
        # tocar. O `dashboard alvo:` protege o objeto dashboard; isto protege os
        # charts dele.
        if fonte_id is not None:
            donos = [d.get("id") for d in (detalhe.get("dashboards") or [])]
            if fonte_id in donos or atual["id"] in self._charts_do_fonte(fonte_id):
                return {"acao": "recusado_e_do_fonte", "slice_name": nome,
                        "id": atual["id"]}
        # O dataset já bate (foi critério da busca); resta o conteúdo. Compara
        # como JSON: o Superset reserializa `params` e a comparação de string
        # crua forçaria um PUT a cada execução.
        # `query_context` entra na comparação: um chart com o contexto ausente
        # ou velho tem params idêntico e mesmo assim precisa de PUT — sem isto,
        # ele fica para sempre "inalterado" e nunca é reparado.
        if (_params_iguais(detalhe.get("params"), payload.get("params"))
                and _params_iguais(detalhe.get("query_context"),
                                   payload.get("query_context"))):
            return {"acao": "inalterado", "slice_name": nome, "id": atual["id"]}
        if dry_run:
            return {"acao": "atualizaria", "slice_name": nome, "id": atual["id"]}
        # Payload inteiro: mandar só datasource/params deixaria viz_type,
        # slice_name e description velhos num run que se reporta "atualizado".
        self._escrever("put", f"/api/v1/chart/{atual['id']}", dict(payload))
        return {"acao": "atualizado", "slice_name": nome, "id": atual["id"],
                "verificacao": self._verificacao(atual["id"])}

    def create_dashboard(self, payload: dict, chart_ids: list,
                         dry_run: bool = False, fonte_id: int | None = None) -> dict:
        """POST/PUT idempotente: compara conteúdo, não só existência.

        Achar pelo nome e seguir adiante não basta aqui tampouco — um dashboard
        cujo título ou cujos charts mudaram nunca seria atualizado.

        `slug` é obrigatório: a listagem do Superset omite dashboards (ver
        `references/superset-api.md`), então decidir existência por ela produz
        cópias. Só `GET /api/v1/dashboard/<slug>` responde com confiança.

        `fonte_id`, quando o dashboard está sendo re-derivado de outro, é o id
        do fonte: se a resolução cair nele, a escrita é recusada em vez de
        reescrever o dashboard que serviu de referência.
        """
        slug = payload.get("slug")
        if not slug:
            raise ValueError(
                "dashboard sem `slug`: a listagem do Superset omite dashboards, "
                "então não há como decidir existência sem ele e cada execução "
                "criaria uma cópia. Inclua `slug` no payload."
            )
        # `chartId` no layout é int; um "7" vindo do JSON não casaria com o 7
        # já publicado e acrescentaria um nó CHART a cada execução.
        chart_ids = [int(i) for i in chart_ids]
        existente = self.get_dashboard(slug)

        if existente is not None and fonte_id is not None \
                and existente.get("id") == fonte_id:
            return {"acao": "recusado_e_o_fonte", "slug": slug,
                    "id": existente.get("id")}

        if existente is None:
            corpo = dict(payload)
            try:
                corpo["position_json"] = json.dumps(
                    build_position_json([self._resumo_do_chart(i) for i in chart_ids])
                )
            except ChartNaoEncontrado:
                return {"acao": "chart_nao_encontrado", "slug": slug, "id": None}
            if dry_run:
                return {"acao": "criaria", "slug": slug, "id": None}
            novo = self._escrever("post", "/api/v1/dashboard/", corpo).json()
            for cid in chart_ids:
                self._associar_chart(cid, novo["id"])
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
            # Layout completo não quer dizer "nada a fazer": o bug que
            # `_associar_chart` corrige deixa dashboards com a `position_json`
            # inteira e `dashboard_slices` vazio — abrem em branco. Re-rodar a
            # tool nesse dashboard tem que reparar a associação, não devolver
            # `inalterado` para sempre e nunca anexar nada (mesmo defeito, e
            # mesma correção, do query_context ausente em `create_chart`).
            try:
                pendentes = []
                for i in chart_ids:
                    chart = self.get_chart(i)
                    if chart is None:
                        raise ChartNaoEncontrado(i)
                    anexados = [d.get("id") for d in (chart.get("dashboards") or [])]
                    if id_ not in anexados:
                        pendentes.append(i)
            except ChartNaoEncontrado:
                return {"acao": "chart_nao_encontrado", "slug": slug, "id": id_}
            if not pendentes:
                return {"acao": "inalterado", "slug": slug, "id": id_}
            if dry_run:
                # Um dry-run não escreve nada nem aqui: só anuncia o reparo.
                return {"acao": "associaria", "slug": slug, "id": id_}
            for i in pendentes:
                self._associar_chart(i, id_)
            # `associado`, não `inalterado`: houve escrita e o dashboard saiu
            # de "em branco" para populado. Reportar `inalterado` aqui seria a
            # mesma mentira que escondeu o bug original.
            return {"acao": "associado", "slug": slug, "id": id_}

        # Tenta a splice (ou o rebuild) antes do dry-run: um layout sem lugar
        # para ROW, ou um chart_id inexistente, têm que aparecer no dry-run
        # também — senão ele promete uma escrita que o run de verdade recusa.
        try:
            if pos:
                # Mesmo motivo do add_chart_to_dashboard: o layout publicado é
                # a fonte da verdade, o novo chart entra nele.
                for i in faltando:
                    pos = inserir_chart_no_layout(
                        pos, i, self._resumo_do_chart(i)["slice_name"])
            else:
                pos = build_position_json([self._resumo_do_chart(i) for i in chart_ids])
        except LayoutSemLugarParaRow:
            return {"acao": "layout_sem_lugar_para_row", "slug": slug, "id": id_}
        except ChartNaoEncontrado:
            return {"acao": "chart_nao_encontrado", "slug": slug, "id": id_}

        if dry_run:
            return {"acao": "atualizaria", "slug": slug, "id": id_}

        corpo = dict(payload)
        corpo["position_json"] = json.dumps(pos)
        self._escrever("put", f"/api/v1/dashboard/{id_}", corpo)
        for cid in chart_ids:
            self._associar_chart(cid, id_)
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
        novo = self.get_chart(chart_id)
        if novo is None:
            # Sem isso o 404 vira um nó CHART fantasma no layout publicado, e
            # remover nó de layout está fora do escopo da skill.
            return {"acao": "chart_nao_encontrado", "id": None}
        if chart_id in _chart_ids_do_layout(pos):
            # O chart já está no layout, mas isso não quer dizer "nada a fazer":
            # até há pouco este subcomando escrevia só a `position_json` e nunca
            # a associação, deixando o chart no layout com `dashboards: []` — ele
            # não renderiza. Re-rodar a tool nesse dashboard tem que reparar a
            # associação, não devolver `inalterado` para sempre (mesmo defeito, e
            # mesma correção, do branch `associado`/`associaria` do
            # `create_dashboard`).
            anexados = [d.get("id") for d in (novo.get("dashboards") or [])]
            if dash["id"] in anexados:
                return {"acao": "inalterado", "id": dash["id"]}
            if dry_run:
                # Um dry-run não escreve nada: só anuncia o reparo.
                return {"acao": "associaria", "id": dash["id"]}
            self._associar_chart(chart_id, dash["id"])
            # `associado`, não `inalterado`: houve escrita e o chart saiu de
            # "no layout mas não anexado" para renderizável.
            return {"acao": "associado", "id": dash["id"]}
        # Tenta a splice antes do dry-run: um layout sem lugar para ROW tem
        # que aparecer no dry-run também — senão ele promete uma escrita que
        # o run de verdade recusa.
        try:
            pos = inserir_chart_no_layout(pos, chart_id, novo.get("slice_name", ""))
        except LayoutSemLugarParaRow:
            return {"acao": "layout_sem_lugar_para_row", "id": dash["id"]}
        if dry_run:
            return {"acao": "adicionaria", "id": dash["id"]}
        self._escrever("put", f"/api/v1/dashboard/{dash['id']}",
                       {"position_json": json.dumps(pos)})
        # Layout primeiro, associação depois — a mesma ordem do
        # `create_dashboard`. Só o `position_json` era o defeito D4 por outra
        # porta: o chart entra no layout, o dashboard não o anexa em
        # `dashboard_slices`, e ele não renderiza. `_associar_chart` é a única
        # fonte da regra "acrescenta, nunca substitui".
        self._associar_chart(chart_id, dash["id"])
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


_VALOR_INEXISTENTE = "__smoke_valor_inexistente__"


def _coluna_para_filtro(dataset: dict):
    """Escolhe, em tempo de execução, uma coluna do dataset para o filtro.

    Fixar um nome no código amarraria a smoke a um dataset só. Prefere coluna
    textual porque o comparador é uma string: num campo numérico ou de data o
    banco pode recusar a comparação e devolver erro em vez do 0 que a asserção
    espera. Sem coluna textual, a primeira serve. `None` quando o dataset não
    declara coluna nenhuma — aí a smoke não tem como montar o filtro.
    """
    colunas = [c for c in (dataset or {}).get("columns") or []
               if isinstance(c, dict) and c.get("column_name")]
    textuais = [c for c in colunas
                if any(t in str(c.get("type") or "").upper()
                       for t in ("TEXT", "VARCHAR", "STRING"))]
    candidatas = textuais + colunas
    return candidatas[0]["column_name"] if candidatas else None


def _valor_do_big_number(r: dict):
    """O número que um `big_number_total` devolveu, ou `None` se não deu para ler.

    `verificacao.amostra` é a primeira linha como dict; num COUNT(*) ela tem uma
    chave só, o rótulo da métrica.
    """
    amostra = (r.get("verificacao") or {}).get("amostra")
    if not isinstance(amostra, dict) or len(amostra) != 1:
        return None
    valor = next(iter(amostra.values()))
    return valor if isinstance(valor, (int, float)) else None


def _smoke_ciclo(c: "SupersetClient", dataset_id: int, marca: str,
                 passos: list, limpar: list) -> None:
    """Corpo da smoke: acrescenta os passos em `passos`, e em `limpar` o que
    este run criou.

    Separado de `_smoke` para poder desistir com um `return` (dataset vazio,
    dataset sem colunas) sem pular a limpeza nem o relatório.
    """
    def payload(filtros, nome=None):
        params = json.dumps({"datasource": f"{dataset_id}__table",
                             "viz_type": "big_number_total",
                             "metric": {"expressionType": "SQL",
                                        "sqlExpression": "COUNT(*)",
                                        "label": "linhas"},
                             "adhoc_filters": filtros}, ensure_ascii=False)
        return {"slice_name": nome or marca, "viz_type": "big_number_total",
                "datasource_id": dataset_id, "datasource_type": "table",
                "params": params}

    def rotulo(base: str, r: dict) -> str:
        # A verificação já produz a mensagem quando a leitura de dados falha;
        # jogá-la fora deixaria o operador com um `ok: false` sem motivo.
        erro = (r.get("verificacao") or {}).get("erro")
        return f"{base} — {erro}" if erro else base

    # 1. COUNT(*) sem filtro: o valor de referência.
    r = c.create_chart(payload([]))
    chart_id = r["id"]
    # Só apaga o que este run criou: numa colisão de `marca` no mesmo segundo,
    # apagar por id arrancaria o chart do outro run.
    if r["acao"] == "criado":
        limpar.append(("chart", chart_id))
    passos.append(("chart criado", r["acao"] == "criado"))

    total = _valor_do_big_number(r)
    passos.append((rotulo("dados do chart", r), total is not None))
    if total is None:
        return
    if total <= 0:
        passos.append((f"dataset tem linhas (COUNT(*) = {total}): dataset vazio: "
                       "a smoke não consegue provar que o filtro aplicou", False))
        return
    passos.append((f"dataset tem linhas (COUNT(*) = {total})", True))

    coluna = _coluna_para_filtro(c.get_dataset(dataset_id) or {})
    if coluna is None:
        passos.append((f"coluna para o filtro: o dataset {dataset_id} não declara "
                       "coluna nenhuma: a smoke não consegue provar que o filtro "
                       "aplicou", False))
        return

    # 2. Mesmo chart (mesmo slice_name + dataset => `atualizado`), agora com um
    #    filtro SIMPLE que não casa nada — resultado previsível em qualquer
    #    tabela não-vazia, sem precisar conhecer nenhum valor real.
    filtro = {"expressionType": "SIMPLE", "subject": coluna, "operator": "==",
              "comparator": _VALOR_INEXISTENTE, "clause": "WHERE"}
    r2 = c.create_chart(payload([filtro]))
    if r2["acao"] == "criado" and ("chart", r2["id"]) not in limpar:
        limpar.append(("chart", r2["id"]))
    passos.append(("mesmo chart atualizado com o filtro",
                   r2["acao"] == "atualizado" and r2["id"] == chart_id))

    # 3. O passo que dá sentido à smoke. Contar linhas não discriminava nada:
    #    um big_number_total com COUNT(*) devolve sempre uma linha — com filtro,
    #    sem filtro, ou com filtro que não casa nada. Comparar valores, sim: com
    #    o D1 (query_context sem os filtros derivados) o filtro é ignorado e o
    #    valor volta a ser `total`.
    filtrado = _valor_do_big_number(r2)
    passos.append((rotulo(f"filtro aplicou em `{coluna}`: {total} -> {filtrado}", r2),
                   filtrado == 0 and filtrado != total))

    d = c.create_dashboard({"dashboard_title": marca,
                            "slug": marca.replace(" ", "-")}, [chart_id])
    dash_id = d.get("id")
    if d["acao"] == "criado" and dash_id is not None:
        limpar.append(("dashboard", dash_id))
    passos.append(("dashboard criado", d["acao"] == "criado"))
    if dash_id is None:
        return

    dash = c.get_dashboard(dash_id) or {}
    pos = json.loads(dash.get("position_json") or "{}")
    no_layout = sum(1 for v in pos.values()
                    if isinstance(v, dict) and v.get("type") == "CHART")
    # As duas metades que o defeito D4 separou: layout e associação.
    passos.append(("chart no layout", no_layout == 1))
    passos.append(("chart associado", len(dash.get("charts") or []) == 1))

    donos = [x.get("id") for x in (c.get_chart(chart_id) or {}).get("dashboards") or []]
    passos.append(("dashboard na lista do chart", dash_id in donos))

    # 4. `add-chart-to-dashboard`, a terceira forma de `dashboard alvo:`
    #    (`existente:`). Ela não tinha cobertura ao vivo, e foi por isso que o
    #    D4 sobreviveu nela: o subcomando escrevia o `position_json` e nunca
    #    associava, então o chart aparecia no layout e não renderizava. Este
    #    passo confere as duas metades, como o passo do `create_dashboard`.
    rb = c.create_chart(payload([], nome=f"{marca} b"))
    chart_b = rb["id"]
    if rb["acao"] == "criado" and ("chart", chart_b) not in limpar:
        limpar.append(("chart", chart_b))
    passos.append(("segundo chart criado", rb["acao"] == "criado"))
    if chart_b is None:
        return

    a = c.add_chart_to_dashboard(dash_id, chart_b)
    passos.append((f"add-chart-to-dashboard: {a['acao']}", a["acao"] == "adicionado"))

    dash_b = c.get_dashboard(dash_id) or {}
    pos_b = json.loads(dash_b.get("position_json") or "{}")
    passos.append(("segundo chart no layout", chart_b in _chart_ids_do_layout(pos_b)))
    donos_b = [x.get("id") for x in (c.get_chart(chart_b) or {}).get("dashboards") or []]
    passos.append(("segundo chart associado", dash_id in donos_b))


def _smoke(c: "SupersetClient", dataset_id: int) -> dict:
    """Exercita o ciclo inteiro contra o Superset real e limpa o que criou.

    Existe porque os quatro defeitos que a primeira execução real expôs passaram
    por uma suíte inteiramente mockada: nada nunca tinha falado com um Superset.

    Cria um chart e um dashboard descartáveis e confere o que o `position_json`
    sozinho não garante: que um filtro declarado no `params` **de fato aplicou**
    (o valor cai para 0 quando o filtro não casa nada — com o D1 ele não cairia)
    e que o chart ficou mesmo associado ao dashboard, não só desenhado no
    layout. Um segundo chart descartável entra pelo `add-chart-to-dashboard`,
    que é a terceira forma de `dashboard alvo:` e a única que não tinha
    cobertura ao vivo — o D4 sobreviveu nela justamente por isso. Não confere
    que os números estejam certos: isso ela continua sem saber. Apaga tudo no
    fim, inclusive se um passo falhar.
    """
    marca = f"__smoke__ {int(time.time())}"
    passos, limpar = [], []
    try:
        _smoke_ciclo(c, dataset_id, marca, passos, limpar)
    except Exception as e:
        # Sem isto, uma falha composta (um passo estoura E o DELETE seguinte
        # também falha) descartaria o dict inteiro junto com a linha
        # `LIMPEZA FALHOU`: o operador veria o traceback e nenhuma indicação de
        # que sobrou um objeto `__smoke__`, nem o id dele.
        passos.append((f"passo estourou: {type(e).__name__}: {e}", False))
    finally:
        for caminho, id_ in reversed(limpar):
            try:
                c.s.delete(f"{c.base}/api/v1/{caminho}/{id_}", timeout=TIMEOUT)
                passos.append((f"{caminho} apagado",
                               (c.get_dashboard(id_) if caminho == "dashboard"
                                else c.get_chart(id_)) is None))
            except Exception as e:
                passos.append((f"{caminho} apagado", False))
                passos.append((f"LIMPEZA FALHOU ({caminho} {id_}): {e}", False))
    return {"marca": marca,
            "passos": [{"passo": p, "ok": ok} for p, ok in passos],
            "ok": all(ok for _, ok in passos)}


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
    q.add_argument("--fonte", help="slug ou id do dashboard fonte; recusa "
                                   "sobrescrever um chart que pertença a ele.")

    q = sub.add_parser("create-dashboard", help="Cria um dashboard novo.")
    q.add_argument("--file", required=True,
                   help='JSON com {"payload": {…}, "chart_ids": [1,2]}; '
                        "`slug` é obrigatório dentro de payload.")
    q.add_argument("--dry-run", action="store_true")
    q.add_argument("--fonte", help="Slug ou id do dashboard fonte, quando este "
                                   "dashboard é re-derivado de outro: protege o "
                                   "fonte de ser reescrito por engano.")

    q = sub.add_parser("add-chart-to-dashboard", help="Acrescenta um chart a um dashboard.")
    q.add_argument("ref")
    q.add_argument("chart_id", type=int)
    q.add_argument("--dry-run", action="store_true")

    q = sub.add_parser("smoke", help="Ciclo completo contra o Superset real "
                                     "(cria, confere e apaga).")
    q.add_argument("--dataset", required=True, type=int,
                   help="id de um dataset qualquer, usado para um COUNT(*).")

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
        fonte_id = None
        if args.fonte:
            fonte = c.get_dashboard(args.fonte)
            if fonte is None:
                sys.exit(f"dashboard fonte não encontrado: {args.fonte}")
            fonte_id = fonte.get("id")
            if fonte_id is None:
                # `id` ausente desligaria a proteção contra reescrever um
                # chart do fonte em silêncio (fonte_id=None equivale a "sem fonte").
                sys.exit(
                    f"dashboard fonte ({args.fonte}) resolveu mas o payload "
                    "não trouxe `id`: não dá para proteger os charts do fonte "
                    "contra reescrita sem ele"
                )
        with open(args.file, encoding="utf-8") as fh:
            _imprimir(c.create_chart(json.load(fh), dry_run=args.dry_run,
                                     fonte_id=fonte_id))
    elif args.comando == "create-dashboard":
        with open(args.file, encoding="utf-8") as fh:
            entrada = json.load(fh)
        fonte_id = None
        if args.fonte:
            fonte = c.get_dashboard(args.fonte)
            if fonte is None:
                sys.exit(f"dashboard fonte não encontrado: {args.fonte}")
            fonte_id = fonte.get("id")
            if fonte_id is None:
                # `id` ausente desligaria a proteção contra reescrever o
                # fonte em silêncio (fonte_id=None equivale a "sem fonte").
                sys.exit(
                    f"dashboard fonte ({args.fonte}) resolveu mas o payload "
                    "não trouxe `id`: não dá para proteger o fonte contra "
                    "reescrita sem ele"
                )
        _imprimir(c.create_dashboard(entrada["payload"], entrada["chart_ids"],
                                     dry_run=args.dry_run, fonte_id=fonte_id))
    elif args.comando == "add-chart-to-dashboard":
        _imprimir(c.add_chart_to_dashboard(args.ref, args.chart_id,
                                           dry_run=args.dry_run))
    elif args.comando == "smoke":
        r = _smoke(c, args.dataset)
        _imprimir(r)
        return 0 if r["ok"] else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
