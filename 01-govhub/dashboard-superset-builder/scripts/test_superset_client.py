"""Testes do cliente REST do Superset. HTTP mockado — nenhum servidor ao vivo."""
import json
from unittest.mock import MagicMock

import pytest
import requests

from superset_client import (
    LayoutSemLugarParaRow,
    SupersetClient,
    build_position_json,
    build_query_context,
    inserir_chart_no_layout,
    rison_q,
)


def resposta(status=200, corpo=None, texto=""):
    """Fabrica uma resposta HTTP falsa no formato que o `requests` devolve."""
    r = MagicMock()
    r.status_code = status
    r.text = texto
    r.json.return_value = corpo if corpo is not None else {}
    return r


def cliente(session):
    return SupersetClient("https://superset.exemplo/", "usuario", "senha", session=session)


# --- rison_q ---------------------------------------------------------------

def test_rison_q_paginacao_simples():
    assert rison_q(0) == "(page:0,page_size:100)"
    assert rison_q(2, 50) == "(page:2,page_size:50)"


def test_rison_q_com_filtro():
    q = rison_q(0, 100, filters=[("table_name", "ct", "gld_boletim")])
    assert q == "(filters:!((col:table_name,opr:ct,value:'gld_boletim')),page:0,page_size:100)"


def test_rison_q_escapa_valor_com_espaco_e_aspas():
    # sem aspas, "consumo de agua" produz Rison malformado -> 400 -> a busca
    # seria lida como "o dataset não existe"
    q = rison_q(0, 100, filters=[("table_name", "ct", "consumo de agua")])
    assert "value:'consumo de agua'" in q

    q = rison_q(0, 100, filters=[("table_name", "ct", "d'agua")])
    assert "value:'d!'agua'" in q

    q = rison_q(0, 100, filters=[("table_name", "ct", "a!b")])
    assert "value:'a!!b'" in q


def test_rison_q_nao_poe_aspas_em_numero_e_booleano():
    q = rison_q(0, 100, filters=[("id", "eq", 42), ("published", "eq", True)])
    assert "value:42" in q and "value:!t" in q


# --- login -----------------------------------------------------------------

def test_login_usa_formulario_e_fixa_csrf_e_referer():
    s = MagicMock()
    s.headers = {}
    s.get.side_effect = [
        resposta(texto='<input name="csrf_token" value="TOKEN-DA-PAGINA">'),
        resposta(corpo={"result": "TOKEN-DA-API"}),
    ]
    s.post.return_value = resposta()

    c = cliente(s)
    c.login()

    # autenticou por formulário, levando o csrf da página
    url_post, kwargs = s.post.call_args[0][0], s.post.call_args[1]
    assert url_post == "https://superset.exemplo/login/"
    assert kwargs["data"] == {
        "username": "usuario", "password": "senha", "csrf_token": "TOKEN-DA-PAGINA",
    }
    # fixou o csrf da API e o Referer na sessão
    assert s.headers["X-CSRFToken"] == "TOKEN-DA-API"
    assert s.headers["Referer"] == "https://superset.exemplo"


def test_base_url_perde_a_barra_final():
    assert cliente(MagicMock()).base == "https://superset.exemplo"


# --- listagem paginada -----------------------------------------------------

def test_list_all_percorre_todas_as_paginas():
    s = MagicMock()
    s.get.side_effect = [
        resposta(corpo={"count": 3, "result": [{"id": 1}, {"id": 2}]}),
        resposta(corpo={"count": 3, "result": [{"id": 3}]}),
    ]
    assert cliente(s).list_all("dataset") == [{"id": 1}, {"id": 2}, {"id": 3}]
    assert s.get.call_args_list[0][1]["params"] == {"q": "(page:0,page_size:100)"}
    assert s.get.call_args_list[1][1]["params"] == {"q": "(page:1,page_size:100)"}


def test_list_all_para_em_pagina_vazia():
    s = MagicMock()
    s.get.side_effect = [resposta(corpo={"count": 99, "result": []})]
    assert cliente(s).list_all("chart") == []


def test_list_all_estoura_em_erro_http_em_vez_de_devolver_vazio():
    s = MagicMock()
    erro = resposta(status=500, corpo={"message": "boom"})
    erro.raise_for_status.side_effect = requests.HTTPError("500")
    s.get.return_value = erro

    with pytest.raises(requests.HTTPError):
        cliente(s).list_all("chart")


# --- leitura por id/slug ---------------------------------------------------

def test_get_dashboard_devolve_result():
    s = MagicMock()
    s.get.return_value = resposta(corpo={"result": {"id": 3, "dashboard_title": "Painel"}})
    assert cliente(s).get_dashboard("painel")["id"] == 3
    assert s.get.call_args[0][0] == "https://superset.exemplo/api/v1/dashboard/painel"


def test_get_dashboard_404_devolve_none_sem_levantar():
    s = MagicMock()
    s.get.return_value = resposta(status=404)
    assert cliente(s).get_dashboard("nao-existe") is None


def test_get_chart_devolve_result():
    s = MagicMock()
    s.get.return_value = resposta(corpo={"result": {"id": 1, "slice_name": "X"}})
    assert cliente(s).get_chart(1)["slice_name"] == "X"


# --- build_position_json ---------------------------------------------------

def test_position_json_tem_meta_em_todo_no():
    pos = build_position_json([{"id": 7, "slice_name": "A"}, {"id": 8, "slice_name": "B"}])
    nos = [v for k, v in pos.items() if k != "DASHBOARD_VERSION_KEY"]
    assert nos, "position_json não pode ser só a chave de versão"
    for no in nos:
        assert "meta" in no, f"nó sem meta quebra o front do Superset 6: {no['id']}"


def test_position_json_encadeia_root_grid_row_chart():
    pos = build_position_json([{"id": 7, "slice_name": "A"}])
    assert pos["ROOT_ID"]["children"] == ["GRID_ID"]
    linha = pos["GRID_ID"]["children"][0]
    assert pos[linha]["type"] == "ROW"
    chart = pos[linha]["children"][0]
    assert pos[chart]["type"] == "CHART"
    assert pos[chart]["meta"]["chartId"] == 7
    assert pos[chart]["parents"] == ["ROOT_ID", "GRID_ID", linha]


def test_position_json_usa_duas_colunas_por_linha():
    pos = build_position_json([{"id": i, "slice_name": str(i)} for i in range(1, 4)])
    linhas = pos["GRID_ID"]["children"]
    assert len(linhas) == 2, "3 charts em grid de 2 colunas => 2 linhas"
    assert len(pos[linhas[0]]["children"]) == 2
    assert len(pos[linhas[1]]["children"]) == 1
    primeiro = pos[linhas[0]]["children"][0]
    assert pos[primeiro]["meta"]["width"] == 6, "grid do Superset tem 12 colunas"


# --- create_chart idempotente ---------------------------------------------

PAYLOAD = {
    "slice_name": "Consumo Total",
    "viz_type": "table",
    "datasource_id": 42,
    "datasource_type": "table",
    "params": json.dumps({"datasource": "42__table", "viz_type": "pie"}),
}


def test_create_chart_cria_quando_nao_existe():
    s = MagicMock()
    s.get.return_value = resposta(corpo={"count": 0, "result": []})
    s.post.return_value = resposta(corpo={"id": 99})

    r = cliente(s).create_chart(PAYLOAD)

    assert r == {"acao": "criado", "slice_name": "Consumo Total", "id": 99}
    assert s.post.call_args[0][0] == "https://superset.exemplo/api/v1/chart/"


def test_create_chart_nao_faz_nada_quando_identico():
    s = MagicMock()
    s.get.side_effect = [
        resposta(corpo={"count": 1, "result": [{"id": 5, "slice_name": "Consumo Total",
                                                "datasource_id": 42}]}),
        resposta(corpo={"result": {"id": 5, "params": PAYLOAD["params"],
                                   "query_context": build_query_context(PAYLOAD)}}),
    ]

    r = cliente(s).create_chart(PAYLOAD)

    assert r == {"acao": "inalterado", "slice_name": "Consumo Total", "id": 5}
    s.post.assert_not_called()
    s.put.assert_not_called()


def test_create_chart_cria_novo_quando_o_dataset_mudou():
    # contrato novo (I8): "o mesmo chart" é nome + dataset. Um chart homônimo
    # sobre outro dataset não é este, então vira criação, não update.
    s = MagicMock()
    s.get.return_value = resposta(corpo={"count": 1, "result": [
        {"id": 5, "slice_name": "Consumo Total", "datasource_id": 7}]})
    s.post.return_value = resposta(corpo={"id": 123})

    r = cliente(s).create_chart(PAYLOAD)

    assert r == {"acao": "criado", "slice_name": "Consumo Total", "id": 123}
    s.put.assert_not_called()


def test_create_chart_nao_sobrescreve_chart_homonimo_de_outro_dataset():
    s = MagicMock()
    s.get.return_value = resposta(corpo={"count": 1, "result": [
        {"id": 5, "slice_name": "Consumo Total", "datasource_id": 99}]})
    s.post.return_value = resposta(corpo={"id": 123})

    r = cliente(s).create_chart(PAYLOAD)  # PAYLOAD usa datasource_id 42

    assert r["acao"] == "criado", "nome igual em outro dataset não é o mesmo chart"
    s.put.assert_not_called()


def test_create_chart_nao_posta_quando_a_listagem_falha():
    s = MagicMock()
    erro = resposta(status=500, corpo={"message": "boom"})
    erro.raise_for_status.side_effect = requests.HTTPError("500")
    s.get.return_value = erro

    with pytest.raises(requests.HTTPError):
        cliente(s).create_chart(PAYLOAD)
    # erro na busca não pode virar duplicata
    s.post.assert_not_called()


def test_create_chart_dry_run_le_mas_nao_escreve():
    s = MagicMock()
    s.get.return_value = resposta(corpo={"count": 0, "result": []})

    r = cliente(s).create_chart(PAYLOAD, dry_run=True)

    assert r == {"acao": "criaria", "slice_name": "Consumo Total", "id": None}
    s.get.assert_called()  # dry-run lê de verdade
    s.post.assert_not_called()


def test_update_de_chart_manda_o_payload_completo():
    s = MagicMock()
    s.get.side_effect = [
        resposta(corpo={"count": 1, "result": [{"id": 5, "slice_name": "Consumo Total",
                                                "datasource_id": 42}]}),
        resposta(corpo={"result": {"id": 5, "params": json.dumps({"datasource": "42__table",
                                                                  "viz_type": "pie"})}}),
    ]
    s.put.return_value = resposta(corpo={"id": 5})

    cliente(s).create_chart(PAYLOAD)

    enviado = s.put.call_args[1]["json"]
    assert enviado["viz_type"] == "table", "viz_type alterado tem que ir no PUT"
    assert enviado["slice_name"] == "Consumo Total"


def test_params_equivalentes_com_chaves_reordenadas_nao_geram_put():
    s = MagicMock()
    reordenado = json.dumps({"viz_type": "pie", "datasource": "42__table"})
    s.get.side_effect = [
        resposta(corpo={"count": 1, "result": [{"id": 5, "slice_name": "Consumo Total",
                                                "datasource_id": 42}]}),
        resposta(corpo={"result": {"id": 5, "params": reordenado,
                                   "query_context": build_query_context(PAYLOAD)}}),
    ]

    r = cliente(s).create_chart(PAYLOAD)

    assert r["acao"] == "inalterado", "mesma config em outra ordem não é mudança"
    s.put.assert_not_called()


def test_create_chart_recusa_datasource_divergente():
    s = MagicMock()
    ruim = dict(PAYLOAD)
    ruim["params"] = json.dumps({"datasource": "7__table", "viz_type": "table"})

    with pytest.raises(ValueError) as erro:
        cliente(s).create_chart(ruim)

    assert "7__table" in str(erro.value) and "42" in str(erro.value)


# --- create_dashboard ------------------------------------------------------

def test_create_dashboard_nao_recria_quando_o_slug_ja_existe():
    s = MagicMock()
    s.get.return_value = resposta(corpo={"result": {
        "id": 3, "slug": "painel", "dashboard_title": "Painel",
        "position_json": json.dumps(build_position_json([{"id": 7, "slice_name": "A"}])),
    }})

    r = cliente(s).create_dashboard({"dashboard_title": "Painel", "slug": "painel"}, [7])

    assert r == {"acao": "inalterado", "slug": "painel", "id": 3}
    s.post.assert_not_called()


def test_create_dashboard_atualiza_quando_os_charts_mudaram():
    s = MagicMock()
    s.get.side_effect = [
        resposta(corpo={"result": {"id": 3, "dashboard_title": "Painel", "slug": "painel",
                                   "position_json": json.dumps(
                                       build_position_json([{"id": 7, "slice_name": "A"}]))}}),
        resposta(corpo={"result": {"id": 9, "slice_name": "C"}}),
    ]
    s.put.return_value = resposta(corpo={"id": 3})

    r = cliente(s).create_dashboard(
        {"dashboard_title": "Painel", "slug": "painel"}, [7, 9])

    assert r["acao"] == "atualizado"
    s.put.assert_called_once()


def test_create_dashboard_sem_slug_falha_alto():
    # contrato novo (I9): a listagem omite dashboards, então decidir existência
    # por ela produz cópias. Sem slug não há busca confiável — falha alto.
    s = MagicMock()

    with pytest.raises(ValueError) as erro:
        cliente(s).create_dashboard({"dashboard_title": "Painel"}, [])

    assert "slug" in str(erro.value)
    s.get.assert_not_called()
    s.post.assert_not_called()


def test_create_dashboard_normaliza_chart_ids_string():
    s = MagicMock()
    layout = build_position_json([{"id": 7, "slice_name": "A"}])
    s.get.side_effect = [
        resposta(corpo={"result": {"id": 3, "dashboard_title": "Painel", "slug": "painel",
                                   "position_json": json.dumps(layout)}}),
    ]

    r = cliente(s).create_dashboard(
        {"dashboard_title": "Painel", "slug": "painel"}, ["7"])

    assert r["acao"] == "inalterado", "'7' e 7 são o mesmo chart"
    s.put.assert_not_called()


def test_create_dashboard_recusa_quando_resolve_no_proprio_fonte():
    s = MagicMock()
    s.get.return_value = resposta(corpo={"result": {
        "id": 3, "slug": "painel-fonte", "dashboard_title": "Outro título",
        "position_json": json.dumps(build_position_json([{"id": 7, "slice_name": "A"}])),
    }})

    r = cliente(s).create_dashboard(
        {"dashboard_title": "Painel derivado", "slug": "painel-fonte"}, [7],
        fonte_id=3)

    assert r == {"acao": "recusado_e_o_fonte", "slug": "painel-fonte", "id": 3}
    # o dashboard fonte nunca é reescrito
    s.put.assert_not_called()
    s.post.assert_not_called()


def test_create_dashboard_recusa_layout_sem_lugar_para_row():
    s = MagicMock()
    patologico = {
        "DASHBOARD_VERSION_KEY": "v2",
        "ROOT_ID": {"type": "ROOT", "id": "ROOT_ID", "children": ["MARKDOWN-1"],
                    "meta": {}},
        "MARKDOWN-1": {"type": "MARKDOWN", "id": "MARKDOWN-1", "children": [],
                       "parents": ["ROOT_ID"], "meta": {"code": "# Só isto"}},
    }
    s.get.side_effect = [
        resposta(corpo={"result": {"id": 3, "dashboard_title": "Painel", "slug": "painel",
                                   "position_json": json.dumps(patologico)}}),
        resposta(corpo={"result": {"id": 9, "slice_name": "C"}}),
    ]

    r = cliente(s).create_dashboard(
        {"dashboard_title": "Painel", "slug": "painel"}, [9])

    assert r == {"acao": "layout_sem_lugar_para_row", "slug": "painel", "id": 3}
    # recusar é melhor que descartar o conteúdo publicado
    s.put.assert_not_called()


def test_create_dashboard_dry_run_tambem_recusa_layout_sem_lugar_para_row():
    # Fix residual 1: um dry-run que promete "atualizaria" quando o run de
    # verdade recusaria mentiria sobre o efeito real mostrado ao dev.
    s = MagicMock()
    patologico = {
        "DASHBOARD_VERSION_KEY": "v2",
        "ROOT_ID": {"type": "ROOT", "id": "ROOT_ID", "children": ["MARKDOWN-1"],
                    "meta": {}},
        "MARKDOWN-1": {"type": "MARKDOWN", "id": "MARKDOWN-1", "children": [],
                       "parents": ["ROOT_ID"], "meta": {"code": "# Só isto"}},
    }
    s.get.side_effect = [
        resposta(corpo={"result": {"id": 3, "dashboard_title": "Painel", "slug": "painel",
                                   "position_json": json.dumps(patologico)}}),
        resposta(corpo={"result": {"id": 9, "slice_name": "C"}}),
    ]

    r = cliente(s).create_dashboard(
        {"dashboard_title": "Painel", "slug": "painel"}, [9], dry_run=True)

    assert r == {"acao": "layout_sem_lugar_para_row", "slug": "painel", "id": 3}
    s.put.assert_not_called()
    s.post.assert_not_called()


def test_create_dashboard_recusa_chart_inexistente():
    # Fix residual 2: mesmo defeito do add_chart_to_dashboard, no caminho de
    # atualização de create_dashboard — um chart_id que 404 não pode virar
    # nó fantasma na position_json publicada.
    s = MagicMock()
    s.get.side_effect = [
        resposta(corpo={"result": {"id": 3, "dashboard_title": "Painel", "slug": "painel",
                                   "position_json": json.dumps(
                                       build_position_json([{"id": 7, "slice_name": "A"}]))}}),
        resposta(status=404),
    ]

    r = cliente(s).create_dashboard(
        {"dashboard_title": "Painel", "slug": "painel"}, [7, 99999])

    assert r["acao"] == "chart_nao_encontrado"
    s.post.assert_not_called()
    s.put.assert_not_called()


# --- add_chart_to_dashboard ------------------------------------------------

def layout_ajustado_na_interface():
    """Layout como fica depois de alguém mexer no Superset: aba, markdown, larguras 4."""
    return {
        "DASHBOARD_VERSION_KEY": "v2",
        "ROOT_ID": {"type": "ROOT", "id": "ROOT_ID", "children": ["TABS-1"], "meta": {}},
        "TABS-1": {"type": "TABS", "id": "TABS-1", "children": ["TAB-1"],
                   "parents": ["ROOT_ID"], "meta": {}},
        "TAB-1": {"type": "TAB", "id": "TAB-1", "children": ["MARKDOWN-1", "ROW-A"],
                  "parents": ["ROOT_ID", "TABS-1"], "meta": {"text": "Visão geral"}},
        "MARKDOWN-1": {"type": "MARKDOWN", "id": "MARKDOWN-1", "children": [],
                       "parents": ["ROOT_ID", "TABS-1", "TAB-1"],
                       "meta": {"code": "# Título", "width": 12, "height": 20}},
        "ROW-A": {"type": "ROW", "id": "ROW-A", "children": ["CHART-7"],
                  "parents": ["ROOT_ID", "TABS-1", "TAB-1"], "meta": {}},
        "CHART-7": {"type": "CHART", "id": "CHART-7", "children": [],
                    "parents": ["ROOT_ID", "TABS-1", "TAB-1", "ROW-A"],
                    "meta": {"chartId": 7, "width": 4, "height": 80, "sliceName": "A"}},
    }


def test_inserir_chart_preserva_abas_markdown_e_larguras():
    antes = layout_ajustado_na_interface()
    depois = inserir_chart_no_layout(antes, 8, "B")

    tipos = {no["type"] for no in depois.values() if isinstance(no, dict)}
    assert "TABS" in tipos and "TAB" in tipos and "MARKDOWN" in tipos, \
        "aba e markdown não podem sumir"
    assert depois["CHART-7"]["meta"]["width"] == 4, "largura ajustada à mão foi resetada"
    assert depois["CHART-7"]["meta"]["height"] == 80, "altura ajustada à mão foi resetada"
    assert depois["MARKDOWN-1"]["meta"]["code"] == "# Título"
    assert depois["CHART-8"]["meta"]["chartId"] == 8


def test_inserir_chart_encaixa_na_ultima_row_com_espaco():
    depois = inserir_chart_no_layout(layout_ajustado_na_interface(), 8, "B")
    # ROW-A usava 4 de 12; o chart novo cabe lá.
    assert depois["ROW-A"]["children"] == ["CHART-7", "CHART-8"]
    assert depois["CHART-8"]["parents"] == ["ROOT_ID", "TABS-1", "TAB-1", "ROW-A"]


def test_inserir_chart_cria_row_nova_quando_nao_cabe():
    cheio = layout_ajustado_na_interface()
    cheio["CHART-7"]["meta"]["width"] = 12  # ROW-A lotada
    depois = inserir_chart_no_layout(cheio, 8, "B")

    assert depois["ROW-A"]["children"] == ["CHART-7"], "não podia mexer na ROW cheia"
    novas = [k for k, v in depois.items()
             if isinstance(v, dict) and v.get("type") == "ROW" and k != "ROW-A"]
    assert len(novas) == 1, "devia ter criado exatamente uma ROW nova"
    nova = novas[0]
    # a ROW nova entra sob o mesmo pai da ROW-A (a TAB), não sob um GRID inventado
    assert nova in depois["TAB-1"]["children"]
    assert depois[nova]["children"] == ["CHART-8"]


def test_add_chart_to_dashboard_faz_put_da_arvore_mutada():
    s = MagicMock()
    s.get.side_effect = [
        resposta(corpo={"result": {"id": 3,
                                   "position_json": json.dumps(layout_ajustado_na_interface())}}),
        resposta(corpo={"result": {"id": 8, "slice_name": "B"}}),
    ]
    s.put.return_value = resposta(corpo={"id": 3})

    r = cliente(s).add_chart_to_dashboard("3", 8)

    assert r["acao"] == "adicionado"
    enviado = json.loads(s.put.call_args[1]["json"]["position_json"])
    assert enviado["MARKDOWN-1"]["meta"]["code"] == "# Título", "markdown sumiu no PUT"
    assert enviado["CHART-8"]["meta"]["sliceName"] == "B"


def test_add_chart_to_dashboard_nao_repete_chart_ja_presente():
    s = MagicMock()
    s.get.return_value = resposta(corpo={"result": {
        "id": 3, "position_json": json.dumps(layout_ajustado_na_interface())}})

    r = cliente(s).add_chart_to_dashboard("3", 7)

    assert r == {"acao": "inalterado", "id": 3}
    s.put.assert_not_called()


def test_add_chart_to_dashboard_recusa_position_json_ilegivel():
    s = MagicMock()
    s.get.return_value = resposta(corpo={"result": {"id": 3,
                                                    "position_json": "{isso não é json"}})

    r = cliente(s).add_chart_to_dashboard("3", 8)

    assert r == {"acao": "layout_invalido", "id": 3}
    # não dá para preservar o que não dá para ler: recusa em vez de apagar
    s.put.assert_not_called()


def test_add_chart_to_dashboard_recusa_chart_inexistente():
    s = MagicMock()
    s.get.side_effect = [
        resposta(corpo={"result": {"id": 3, "position_json": json.dumps(
            build_position_json([{"id": 7, "slice_name": "A"}]))}}),
        resposta(status=404),
    ]

    r = cliente(s).add_chart_to_dashboard("3", 99999)

    assert r["acao"] == "chart_nao_encontrado"
    # nó fantasma não pode entrar no layout
    s.put.assert_not_called()


def test_add_chart_to_dashboard_recusa_layout_sem_lugar_para_row():
    s = MagicMock()
    patologico = {
        "DASHBOARD_VERSION_KEY": "v2",
        "ROOT_ID": {"type": "ROOT", "id": "ROOT_ID", "children": ["MARKDOWN-1"],
                    "meta": {}},
        "MARKDOWN-1": {"type": "MARKDOWN", "id": "MARKDOWN-1", "children": [],
                       "parents": ["ROOT_ID"], "meta": {"code": "# Só isto"}},
    }
    s.get.side_effect = [
        resposta(corpo={"result": {"id": 3, "position_json": json.dumps(patologico)}}),
        resposta(corpo={"result": {"id": 8, "slice_name": "B"}}),
    ]

    r = cliente(s).add_chart_to_dashboard("3", 8)

    assert r == {"acao": "layout_sem_lugar_para_row", "id": 3}
    # o markdown publicado não pode ser descartado
    s.put.assert_not_called()


def test_add_chart_to_dashboard_dry_run_tambem_recusa_layout_sem_lugar_para_row():
    # Fix residual 1: um dry-run que promete "adicionaria" quando o run de
    # verdade recusaria mentiria sobre o efeito real mostrado ao dev.
    s = MagicMock()
    patologico = {
        "DASHBOARD_VERSION_KEY": "v2",
        "ROOT_ID": {"type": "ROOT", "id": "ROOT_ID", "children": ["MARKDOWN-1"],
                    "meta": {}},
        "MARKDOWN-1": {"type": "MARKDOWN", "id": "MARKDOWN-1", "children": [],
                       "parents": ["ROOT_ID"], "meta": {"code": "# Só isto"}},
    }
    s.get.side_effect = [
        resposta(corpo={"result": {"id": 3, "position_json": json.dumps(patologico)}}),
        resposta(corpo={"result": {"id": 8, "slice_name": "B"}}),
    ]

    r = cliente(s).add_chart_to_dashboard("3", 8, dry_run=True)

    assert r == {"acao": "layout_sem_lugar_para_row", "id": 3}
    s.put.assert_not_called()
    s.post.assert_not_called()


def test_inserir_chart_levanta_quando_nao_ha_container_para_row():
    patologico = {
        "DASHBOARD_VERSION_KEY": "v2",
        "ROOT_ID": {"type": "ROOT", "id": "ROOT_ID", "children": ["MARKDOWN-1"],
                    "meta": {}},
        "MARKDOWN-1": {"type": "MARKDOWN", "id": "MARKDOWN-1", "children": [],
                       "parents": ["ROOT_ID"], "meta": {"code": "# Só isto"}},
    }

    with pytest.raises(LayoutSemLugarParaRow):
        inserir_chart_no_layout(patologico, 8, "B")

    assert patologico["MARKDOWN-1"]["meta"]["code"] == "# Só isto"


def test_inserir_chart_ignora_no_chart_sem_chart_id():
    quebrado = layout_ajustado_na_interface()
    quebrado["CHART-7"]["meta"] = {}  # nó CHART sem chartId não pode derrubar o run

    depois = inserir_chart_no_layout(quebrado, 8, "B")

    assert depois["CHART-8"]["meta"]["chartId"] == 8


# --- build_query_context (D1) ----------------------------------------------

def payload_xy(viz="big_number_total", **extra):
    fd = {"datasource": "35__table", "viz_type": viz,
          "metric": {"expressionType": "SQL", "sqlExpression": "SUM(total_uhs)",
                     "label": "UHs"},
          "adhoc_filters": [{"expressionType": "SIMPLE", "subject": "nivel",
                             "operator": "==", "comparator": "uf", "clause": "WHERE"}]}
    fd.update(extra)
    return {"slice_name": "X", "viz_type": viz, "datasource_id": 35,
            "datasource_type": "table", "params": json.dumps(fd)}


def test_query_context_converte_adhoc_filter_para_col_op_val():
    from superset_client import build_query_context

    qc = json.loads(build_query_context(payload_xy()))
    assert qc["queries"][0]["filters"] == [{"col": "nivel", "op": "==", "val": "uf"}]
    assert qc["datasource"] == {"id": 35, "type": "table"}
    assert qc["result_type"] == "full"


def test_query_context_usa_entity_como_coluna_em_mapa():
    from superset_client import build_query_context

    qc = json.loads(build_query_context(payload_xy("country_map", entity="iso_3166_2")))
    assert qc["queries"][0]["columns"] == ["iso_3166_2"]


def test_query_context_usa_x_axis_como_coluna_em_serie():
    from superset_client import build_query_context

    qc = json.loads(build_query_context(
        payload_xy("echarts_timeseries_bar", x_axis="regiao_nome")))
    assert qc["queries"][0]["columns"] == ["regiao_nome"]


def test_query_context_de_mixed_timeseries_tem_duas_queries():
    from superset_client import build_query_context

    p = payload_xy("mixed_timeseries", x_axis="mes",
                   metrics=[{"expressionType": "SQL", "sqlExpression": "AVG(a)",
                             "label": "A"}],
                   metrics_b=[{"expressionType": "SQL", "sqlExpression": "AVG(b)",
                               "label": "B"}],
                   adhoc_filters_b=[])
    qc = json.loads(build_query_context(p))
    assert len(qc["queries"]) == 2
    assert qc["queries"][0]["metrics"][0]["label"] == "A"
    assert qc["queries"][1]["metrics"][0]["label"] == "B"
    assert qc["queries"][1]["filters"] == []


def test_query_context_recusa_viz_type_desconhecido():
    from superset_client import build_query_context

    with pytest.raises(ValueError) as erro:
        build_query_context(payload_xy("deck_scatter"))
    assert "deck_scatter" in str(erro.value)


# --- create_chart grava e compara query_context (D1 + D2) ------------------

def test_create_chart_grava_query_context_no_post():
    s = MagicMock()
    s.get.return_value = resposta(corpo={"count": 0, "result": []})
    s.post.return_value = resposta(corpo={"id": 99})

    cliente(s).create_chart(payload_xy())

    enviado = s.post.call_args[1]["json"]
    qc = json.loads(enviado["query_context"])
    assert qc["queries"][0]["filters"] == [{"col": "nivel", "op": "==", "val": "uf"}]


def test_create_chart_atualiza_quando_so_o_query_context_falta():
    p = payload_xy()
    s = MagicMock()
    s.get.side_effect = [
        resposta(corpo={"count": 1, "result": [{"id": 5, "slice_name": "X",
                                                "datasource_id": 35}]}),
        # params idêntico, query_context ausente: é o chart quebrado do D2
        resposta(corpo={"result": {"id": 5, "params": p["params"],
                                   "query_context": None}}),
    ]
    s.put.return_value = resposta(corpo={"id": 5})

    r = cliente(s).create_chart(p)

    assert r["acao"] == "atualizado", "params igual mas query_context ausente é mudança"
    assert "query_context" in s.put.call_args[1]["json"]
