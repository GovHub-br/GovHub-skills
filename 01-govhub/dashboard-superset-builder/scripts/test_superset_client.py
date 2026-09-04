"""Testes do cliente REST do Superset. HTTP mockado — nenhum servidor ao vivo."""
import json
from unittest.mock import MagicMock

from superset_client import SupersetClient, rison_q


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
    assert q == "(filters:!((col:table_name,opr:ct,value:gld_boletim)),page:0,page_size:100)"


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
    from superset_client import build_position_json

    pos = build_position_json([{"id": 7, "slice_name": "A"}, {"id": 8, "slice_name": "B"}])
    nos = [v for k, v in pos.items() if k != "DASHBOARD_VERSION_KEY"]
    assert nos, "position_json não pode ser só a chave de versão"
    for no in nos:
        assert "meta" in no, f"nó sem meta quebra o front do Superset 6: {no['id']}"


def test_position_json_encadeia_root_grid_row_chart():
    from superset_client import build_position_json

    pos = build_position_json([{"id": 7, "slice_name": "A"}])
    assert pos["ROOT_ID"]["children"] == ["GRID_ID"]
    linha = pos["GRID_ID"]["children"][0]
    assert pos[linha]["type"] == "ROW"
    chart = pos[linha]["children"][0]
    assert pos[chart]["type"] == "CHART"
    assert pos[chart]["meta"]["chartId"] == 7
    assert pos[chart]["parents"] == ["ROOT_ID", "GRID_ID", linha]


def test_position_json_usa_duas_colunas_por_linha():
    from superset_client import build_position_json

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
    "params": json.dumps({"datasource": "42__table", "viz_type": "table"}),
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
        resposta(corpo={"result": {"id": 5, "params": PAYLOAD["params"]}}),
    ]

    r = cliente(s).create_chart(PAYLOAD)

    assert r == {"acao": "inalterado", "slice_name": "Consumo Total", "id": 5}
    s.post.assert_not_called()
    s.put.assert_not_called()


def test_create_chart_atualiza_quando_o_dataset_mudou():
    s = MagicMock()
    s.get.side_effect = [
        resposta(corpo={"count": 1, "result": [{"id": 5, "slice_name": "Consumo Total",
                                                "datasource_id": 7}]}),
        resposta(corpo={"result": {"id": 5, "params": PAYLOAD["params"]}}),
    ]
    s.put.return_value = resposta(corpo={"id": 5})

    r = cliente(s).create_chart(PAYLOAD)

    assert r == {"acao": "atualizado", "slice_name": "Consumo Total", "id": 5}
    assert s.put.call_args[0][0] == "https://superset.exemplo/api/v1/chart/5"


def test_create_chart_dry_run_le_mas_nao_escreve():
    s = MagicMock()
    s.get.return_value = resposta(corpo={"count": 0, "result": []})

    r = cliente(s).create_chart(PAYLOAD, dry_run=True)

    assert r == {"acao": "criaria", "slice_name": "Consumo Total", "id": None}
    s.get.assert_called()  # dry-run lê de verdade
    s.post.assert_not_called()


# --- create_dashboard ------------------------------------------------------

def test_create_dashboard_nao_recria_quando_o_slug_ja_existe():
    s = MagicMock()
    s.get.return_value = resposta(corpo={"result": {"id": 3, "slug": "painel"}})

    r = cliente(s).create_dashboard({"dashboard_title": "Painel", "slug": "painel"}, [7])

    assert r == {"acao": "inalterado", "slug": "painel", "id": 3}
    s.post.assert_not_called()


# --- add_chart_to_dashboard ------------------------------------------------

def test_add_chart_to_dashboard_preserva_o_layout_existente():
    from superset_client import build_position_json

    atual = build_position_json([{"id": 7, "slice_name": "A"}])
    s = MagicMock()
    s.get.return_value = resposta(corpo={"result": {"id": 3,
                                                    "position_json": json.dumps(atual)}})
    s.put.return_value = resposta(corpo={"id": 3})

    r = cliente(s).add_chart_to_dashboard("3", 8)

    assert r["acao"] == "adicionado"
    enviado = json.loads(s.put.call_args[1]["json"]["position_json"])
    chart_ids = [n["meta"]["chartId"] for n in enviado.values()
                 if isinstance(n, dict) and n.get("type") == "CHART"]
    assert sorted(chart_ids) == [7, 8], "o chart antigo tem que continuar lá"
