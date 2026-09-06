# Correções D1–D4 do cliente Superset — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Corrigir os quatro defeitos que a primeira execução contra um Superset real expôs — `query_context` não gravado, idempotência que não o repara, colisão de nome que sobrescreveria charts do dashboard fonte, e charts nunca associados ao dashboard novo — e instrumentar o cliente para que a próxima falha desse tipo apareça sozinha.

**Architecture:** Tudo em `scripts/superset_client.py`, um módulo de ~674 linhas com funções puras no topo e a classe `SupersetClient` embaixo. A derivação do `query_context` entra como função pura testável (`build_query_context`), chamada de dentro de `create_chart`. A associação chart↔dashboard entra como método privado (`_associar_chart`) chamado por `create_dashboard`. A conferência pós-escrita entra como método de leitura (`dados_do_chart`) cujo resultado vai num campo `verificacao` do retorno. O `smoke` é um subcomando novo que exercita o ciclo inteiro contra um Superset real e limpa o que criou.

**Tech Stack:** Python 3.10+, `requests` (runtime), `pytest` + `unittest.mock` (testes mockados). Sem dependências novas.

## Global Constraints

- **A lista `VIZ_SUPORTADOS` é a única porta de entrada da derivação.** Um `viz_type` fora dela faz `create_chart` levantar `ValueError` nomeando o tipo e a lista — nunca gerar uma query pela metade. Lista inicial exata: `big_number_total`, `country_map`, `echarts_timeseries_bar`, `mixed_timeseries`, `pie`.
- **Associação de chart a dashboard sempre acrescenta, nunca substitui.** `PUT {"dashboards": [novo]}` substitui a lista inteira e arrancaria o chart dos outros dashboards a que pertence.
- **A conferência pós-escrita nunca derruba a escrita.** Se a leitura de dados falhar, o resultado traz `"verificacao": {"erro": "..."}` — a criação já aconteceu e o comando não pode fingir que não.
- **A capacidade de apagar existe só dentro do `smoke`.** Não vira subcomando de CLI: não se expõe superfície de deleção numa ferramenta que um agente opera.
- **Nenhuma escrita antes da aprovação humana** continua valendo — o `smoke` é a única exceção, e só porque cria e apaga objetos descartáveis que ele mesmo nomeia.
- `SUPERSET_URL`/`SUPERSET_USERNAME`/`SUPERSET_PASSWORD` nunca em arquivo versionado.
- `recusado_e_do_fonte` (chart pertence ao fonte) é **deliberadamente diferente** de `recusado_e_o_fonte` (dashboard é o fonte), que já existe. Não "corrigir" um para o outro.
- Fora de escopo: filtros nativos de dashboard, subcomando de deleção, rodar o `smoke` em CI.

Spec completa: [`docs/superpowers/specs/2026-09-06-superset-client-query-context-e-associacao.md`](../specs/2026-09-06-superset-client-query-context-e-associacao.md).

---

## File Structure

```
01-govhub/dashboard-superset-builder/
├── references/superset-api.md      Tarefa 1 — seção nova (o conhecimento que faltava)
├── scripts/superset_client.py      Tarefas 2-6
├── scripts/test_superset_client.py Tarefas 2-5
└── SKILL.md                        Tarefa 7
```

Estado atual de `superset_client.py` (nomes que as tarefas consomem): `TIMEOUT`,
`rison_valor`, `rison_q`, `build_position_json`, `inserir_chart_no_layout`,
`_layout_do_dashboard`, `_params_iguais`, `LayoutSemLugarParaRow`,
`ChartNaoEncontrado`, e a classe `SupersetClient` com `login`, `list_all`,
`_get_result`, `get_dataset`, `get_dashboard`, `get_chart`, `_validar_datasource`,
`_resumo_do_chart`, `create_chart`, `create_dashboard`, `add_chart_to_dashboard`;
depois `cliente_do_ambiente`, `_imprimir`, `main`.

Testes rodam de dentro de `scripts/`:
`python3 -m pytest test_superset_client.py -v`
Hoje: **43 passando**.

---

### Task 1: Documentar `query_context` e layout ≠ associação

**Files:**
- Modify: `01-govhub/dashboard-superset-builder/references/superset-api.md`

**Interfaces:**
- Consumes: nada.
- Produces: as duas seções que as Tarefas 2 e 3 implementam, e que o `SKILL.md` (Tarefa 7) cita. Títulos exatos: `## query_context` e `## Layout não é associação`.

- [ ] **Step 1: Ler o arquivo atual para achar onde inserir**

Run: `cat /home/joaoegewarth/GovHub-skills/01-govhub/dashboard-superset-builder/references/superset-api.md`
As duas seções novas entram **depois** da seção `## Idempotência` e **antes** de
`## \`position_json\``.

- [ ] **Step 2: Inserir as duas seções**

````markdown
## `query_context`

`params` **não basta**. O Superset guarda a configuração de um chart em dois
campos, e eles servem a consumidores diferentes:

- `params` — o `form_data` que o **front** usa para renderizar e para reabrir o
  chart no Explore.
- `query_context` — o que a **API de dados** (`/api/v1/chart/<id>/data/`) usa para
  montar a consulta.

Um chart criado por `POST /api/v1/chart/` só com `params` abre normalmente na
interface, roda sem erro, e **devolve o número errado** pela API: os
`adhoc_filters` do `params` são simplesmente ignorados.

Foi assim que um KPI mostrou 262.998 em vez de 131.499 — o dobro exato, porque o
dataset guardava linhas em dois níveis (`nivel` = `uf` e `regiao`) e o filtro
`nivel = 'uf'`, presente no `params`, não valeu. Nenhum erro em lugar nenhum.

Forma do `query_context` (de um chart criado pela interface):

```json
{"datasource": {"id": 35, "type": "table"},
 "force": false,
 "form_data": { … o mesmo objeto do params … },
 "result_format": "json",
 "result_type": "full",
 "queries": [{"filters": [{"col": "nivel", "op": "==", "val": "uf"}],
              "metrics": [ … ],
              "columns": [ … ],
              "extras": {"having": "", "where": ""},
              "annotation_layers": [], "series_limit": 0, "order_desc": true,
              "url_params": {}, "custom_params": {}, "custom_form_data": {},
              "applied_time_extras": {}}]}
```

Os `adhoc_filters` do `params` (formato `{expressionType, subject, operator,
comparator}`) viram `filters` do `query_context` (formato `{col, op, val}`).

`mixed_timeseries` tem **duas** queries: uma para `metrics`/`adhoc_filters` e
outra para `metrics_b`/`adhoc_filters_b`.

As colunas saem de `entity` (mapas), de `x_axis` (séries) ou de `groupby`, nessa
ordem de precedência.

## Layout não é associação

Um dashboard guarda os charts que exibe em **dois lugares independentes**, e
escrever só um deles produz uma página vazia:

- `position_json` — o **layout**: onde cada chart fica, em que linha, com que
  largura. Referencia os charts por `meta.chartId`.
- `dashboard_slices` — a **associação**: quais charts pertencem ao dashboard. A
  API expõe isso como o campo `charts` do dashboard e o campo `dashboards` do
  chart.

Um dashboard criado com `position_json` correto e sem associação abre **vazio**:
o layout aponta para charts que não estão anexados.

Como conferir, e o sintoma quando falta:

```
dashboard novo:  charts associados=0   charts no position_json=8   <- vazio na tela
dashboard bom:   charts associados=24  charts no position_json=24
```

A associação se escreve pelo chart: `PUT /api/v1/chart/<id>` com
`{"dashboards": [...]}`.

**Cuidado: esse PUT substitui a lista inteira.** Mandar `{"dashboards": [18]}`
num chart que também estava no dashboard 3 o arranca do 3. Sempre ler a lista
atual e acrescentar.
````

- [ ] **Step 3: Conferir que os dois títulos existem e que a ordem das seções ficou certa**

Run:
```bash
cd /home/joaoegewarth/GovHub-skills
grep -n '^## ' 01-govhub/dashboard-superset-builder/references/superset-api.md
```
Expected: a ordem contém `## Idempotência`, depois `## query_context`, depois
`## Layout não é associação`, depois `` ## `position_json` ``.

- [ ] **Step 4: Commit**

```bash
cd /home/joaoegewarth/GovHub-skills
git add 01-govhub/dashboard-superset-builder/references/superset-api.md
git commit -m "docs(dashboard-superset-builder): documentar query_context e associação

Os dois conceitos que faltavam no conhecimento da API e que causaram os defeitos
D1 e D4: params não basta (a API de dados lê filtros do query_context), e layout
não é associação (position_json sem dashboard_slices renderiza vazio).

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 2: D1 + D2 — derivar, gravar e comparar `query_context`

**Files:**
- Modify: `01-govhub/dashboard-superset-builder/scripts/superset_client.py`
- Modify: `01-govhub/dashboard-superset-builder/scripts/test_superset_client.py`

**Interfaces:**
- Consumes: `_params_iguais(a, b)` (já existe), `TIMEOUT`, `SupersetClient.list_all`, `SupersetClient.get_chart`.
- Produces, para as Tarefas 4, 5 e 6 (nomes exatos):
  - `VIZ_SUPORTADOS: set[str]`
  - `build_query_context(payload: dict) -> str`
  - `create_chart` passa a gravar `query_context` no POST e no PUT, e a comparar `params` **e** `query_context` na idempotência.

- [ ] **Step 1: Escrever os testes que falham**

Acrescentar ao final de `test_superset_client.py`:

```python
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
```

- [ ] **Step 2: Rodar e confirmar que os novos falham**

Run:
```bash
cd /home/joaoegewarth/GovHub-skills/01-govhub/dashboard-superset-builder/scripts
python3 -m pytest test_superset_client.py -v
```
Expected: os 43 existentes passam; os 7 novos falham com
`ImportError: cannot import name 'build_query_context'` e `KeyError: 'query_context'`.

- [ ] **Step 3: Implementar a derivação**

Em `superset_client.py`, logo **depois** de `_params_iguais` e **antes** de
`class SupersetClient:`, acrescentar:

```python
VIZ_SUPORTADOS = {
    "big_number_total",
    "country_map",
    "echarts_timeseries_bar",
    "mixed_timeseries",
    "pie",
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


def _filtro_simples(adhoc: dict):
    """Converte um adhoc_filter SIMPLE para o `{col, op, val}` do query_context."""
    if adhoc.get("expressionType") != "SIMPLE":
        return None
    if not adhoc.get("operator") or adhoc.get("subject") is None:
        return None
    return {"col": adhoc["subject"], "op": adhoc["operator"],
            "val": adhoc.get("comparator")}


def _colunas_do_params(fd: dict) -> list:
    """Colunas da query: `entity` (mapas) > `x_axis` (séries) > `groupby`."""
    if fd.get("entity"):
        return [fd["entity"]]
    colunas = list(fd.get("groupby") or [])
    if fd.get("x_axis"):
        colunas = [fd["x_axis"]] + [c for c in colunas if c != fd["x_axis"]]
    return colunas


def _query(metrics, colunas, filtros, row_limit=None) -> dict:
    q = dict(BASE_QUERY)
    q.update({"filters": filtros, "metrics": metrics, "columns": colunas})
    if row_limit:
        q["row_limit"] = row_limit
    return q


def build_query_context(payload: dict) -> str:
    """Deriva o query_context do params.

    Sem ele, a API de dados do Superset ignora os adhoc_filters: o chart é
    criado, abre sem erro e devolve o número errado. Ver
    `references/superset-api.md`, seção "query_context".
    """
    fd = json.loads(payload["params"])
    viz = fd.get("viz_type")
    if viz not in VIZ_SUPORTADOS:
        raise ValueError(
            f"viz_type {viz!r} não está na lista que sabemos montar "
            f"({sorted(VIZ_SUPORTADOS)}). Confira a forma real de um chart desse "
            f"tipo (get-chart num que já exista) antes de acrescentá-lo à lista — "
            f"adivinhar gera uma query silenciosamente errada."
        )
    filtros = [f for f in (_filtro_simples(a)
                           for a in fd.get("adhoc_filters") or []) if f]
    colunas = _colunas_do_params(fd)
    if viz == "mixed_timeseries":
        filtros_b = [f for f in (_filtro_simples(a)
                                 for a in fd.get("adhoc_filters_b") or []) if f]
        queries = [
            _query(fd.get("metrics") or [], colunas, filtros, fd.get("row_limit")),
            _query(fd.get("metrics_b") or [], colunas, filtros_b,
                   fd.get("row_limit_b")),
        ]
    else:
        metrics = fd.get("metrics") or ([fd["metric"]] if fd.get("metric") else [])
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
```

- [ ] **Step 4: Ligar no `create_chart`**

Em `create_chart`, logo **depois** de `self._validar_datasource(payload)`,
acrescentar:

```python
        payload = dict(payload)
        payload["query_context"] = build_query_context(payload)
```

E trocar a linha da comparação de idempotência — hoje:

```python
        if _params_iguais(detalhe.get("params"), payload.get("params")):
```

por:

```python
        # `query_context` entra na comparação: um chart com o contexto ausente
        # ou velho tem params idêntico e mesmo assim precisa de PUT — sem isto,
        # ele fica para sempre "inalterado" e nunca é reparado.
        if (_params_iguais(detalhe.get("params"), payload.get("params"))
                and _params_iguais(detalhe.get("query_context"),
                                   payload.get("query_context"))):
```

- [ ] **Step 5: Rodar a suíte**

Run:
```bash
cd /home/joaoegewarth/GovHub-skills/01-govhub/dashboard-superset-builder/scripts
python3 -m pytest test_superset_client.py -v
```
Expected: 50 passed, sem warnings.

- [ ] **Step 6: Commit**

```bash
cd /home/joaoegewarth/GovHub-skills
git add 01-govhub/dashboard-superset-builder/scripts/
git commit -m "fix(dashboard-superset-builder): gravar e comparar query_context

D1: create-chart gravava só params, e a API de dados lê os filtros do
query_context — os charts abriam sem erro e devolviam número errado (um KPI
mostrou o dobro). Agora o cliente deriva o query_context do params, com uma
lista de viz_types conhecidos que recusa alto o que não sabe montar.

D2: a idempotência comparava só params, então um chart com query_context
ausente ficava 'inalterado' para sempre e não podia ser reparado.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 3: D4 — associar os charts ao dashboard

**Files:**
- Modify: `01-govhub/dashboard-superset-builder/scripts/superset_client.py`
- Modify: `01-govhub/dashboard-superset-builder/scripts/test_superset_client.py`

**Interfaces:**
- Consumes: `SupersetClient.get_chart`, `ChartNaoEncontrado`, `TIMEOUT`, `create_dashboard` (já existe, com assinatura `create_dashboard(self, payload, chart_ids, dry_run=False, fonte_id=None)`).
- Produces, para a Tarefa 6: `SupersetClient._associar_chart(chart_id: int, dashboard_id: int) -> None`.

- [ ] **Step 1: Escrever os testes que falham**

Acrescentar ao final de `test_superset_client.py`:

```python
# --- associação chart <-> dashboard (D4) -----------------------------------

def test_associar_chart_acrescenta_sem_remover_os_outros():
    s = MagicMock()
    s.get.return_value = resposta(corpo={"result": {"id": 7, "slice_name": "A",
                                                    "dashboards": [{"id": 3}]}})
    s.put.return_value = resposta(corpo={"id": 7})

    cliente(s)._associar_chart(7, 18)

    enviado = s.put.call_args[1]["json"]["dashboards"]
    assert sorted(enviado) == [3, 18], "substituir a lista arrancaria o chart do 3"


def test_associar_chart_nao_repete_dashboard_ja_presente():
    s = MagicMock()
    s.get.return_value = resposta(corpo={"result": {"id": 7, "slice_name": "A",
                                                    "dashboards": [{"id": 18}]}})

    cliente(s)._associar_chart(7, 18)

    s.put.assert_not_called()


def test_create_dashboard_associa_os_charts_depois_de_criar():
    s = MagicMock()
    s.get.side_effect = [
        resposta(status=404),                                    # slug não existe
        resposta(corpo={"result": {"id": 7, "slice_name": "A"}}),  # _resumo_do_chart
        resposta(corpo={"result": {"id": 7, "slice_name": "A",
                                   "dashboards": []}}),           # _associar_chart lê
    ]
    s.post.return_value = resposta(corpo={"id": 18})
    s.put.return_value = resposta(corpo={"id": 7})

    r = cliente(s).create_dashboard(
        {"dashboard_title": "P", "slug": "p"}, [7])

    assert r["acao"] == "criado"
    assert s.put.call_args[1]["json"]["dashboards"] == [18], \
        "sem isto o dashboard nasce vazio: layout aponta para chart não associado"
```

- [ ] **Step 2: Rodar e confirmar que os novos falham**

Run:
```bash
cd /home/joaoegewarth/GovHub-skills/01-govhub/dashboard-superset-builder/scripts
python3 -m pytest test_superset_client.py -v
```
Expected: os 50 anteriores passam; os 3 novos falham com
`AttributeError: 'SupersetClient' object has no attribute '_associar_chart'` e,
no terceiro, `assert s.put.call_args[1]...` porque nenhum PUT acontece.

- [ ] **Step 3: Implementar `_associar_chart`**

Na classe `SupersetClient`, logo **depois** de `_resumo_do_chart`, acrescentar:

```python
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
        self.s.put(
            f"{self.base}/api/v1/chart/{chart_id}",
            json={"dashboards": atuais + [dashboard_id]},
            timeout=TIMEOUT,
        )
```

- [ ] **Step 4: Chamar da criação e da atualização em `create_dashboard`**

Em `create_dashboard`, no ramo de criação, logo **depois** da linha que obtém o
id do dashboard novo do POST e **antes** do `return` de `"criado"`, acrescentar:

```python
        for cid in chart_ids:
            self._associar_chart(cid, novo_id)
```

(`novo_id` é o id que veio do POST — use o nome de variável que já existe ali.)

E no ramo de atualização, logo **antes** do `return` de `"atualizado"`,
acrescentar o mesmo laço usando o id do dashboard existente:

```python
        for cid in chart_ids:
            self._associar_chart(cid, achado["id"])
```

(`achado` é o dashboard resolvido — use o nome de variável que já existe ali.)

- [ ] **Step 5: Rodar a suíte**

Run:
```bash
cd /home/joaoegewarth/GovHub-skills/01-govhub/dashboard-superset-builder/scripts
python3 -m pytest test_superset_client.py -v
```
Expected: 53 passed, sem warnings.

- [ ] **Step 6: Commit**

```bash
cd /home/joaoegewarth/GovHub-skills
git add 01-govhub/dashboard-superset-builder/scripts/
git commit -m "fix(dashboard-superset-builder): associar os charts ao dashboard

D4: create-dashboard montava o position_json e nunca escrevia a associação
(dashboard_slices). O dashboard nascia com o layout certo e a página vazia,
porque o layout apontava para charts que não estavam anexados.

A associação acrescenta à lista dashboards de cada chart, nunca substitui:
substituir arrancaria o chart dos outros dashboards a que pertence.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 4: D3 — `--fonte` no `create-chart`

**Files:**
- Modify: `01-govhub/dashboard-superset-builder/scripts/superset_client.py`
- Modify: `01-govhub/dashboard-superset-builder/scripts/test_superset_client.py`

**Interfaces:**
- Consumes: `create_chart` (Tarefa 2, já grava `query_context`), `SupersetClient.get_chart`, e o padrão de resolução de `--fonte` que `create-dashboard` já usa no `main()`.
- Produces: `create_chart(payload, dry_run=False, fonte_id=None)` devolvendo `{"acao": "recusado_e_do_fonte", ...}`; subcomando `create-chart` com `--fonte`.

- [ ] **Step 1: Escrever o teste que falha**

Acrescentar ao final de `test_superset_client.py`:

```python
# --- create_chart recusa chart do dashboard fonte (D3) ---------------------

def test_create_chart_recusa_sobrescrever_chart_do_fonte():
    p = payload_xy()
    s = MagicMock()
    s.get.side_effect = [
        resposta(corpo={"count": 1, "result": [{"id": 64, "slice_name": "X",
                                                "datasource_id": 35}]}),
        resposta(corpo={"result": {"id": 64, "params": "{}",
                                   "dashboards": [{"id": 3}]}}),
    ]

    r = cliente(s).create_chart(p, fonte_id=3)

    assert r["acao"] == "recusado_e_do_fonte"
    s.put.assert_not_called()
    s.post.assert_not_called()
```

- [ ] **Step 2: Rodar e confirmar que falha**

Run:
```bash
cd /home/joaoegewarth/GovHub-skills/01-govhub/dashboard-superset-builder/scripts
python3 -m pytest test_superset_client.py::test_create_chart_recusa_sobrescrever_chart_do_fonte -v
```
Expected: FAIL — `TypeError: create_chart() got an unexpected keyword argument 'fonte_id'`.

- [ ] **Step 3: Implementar**

Trocar a assinatura de `create_chart`:

```python
    def create_chart(self, payload: dict, dry_run: bool = False,
                     fonte_id: int | None = None) -> dict:
```

E, logo **depois** da linha que busca `detalhe = self.get_chart(atual["id"]) or {}`
(no ramo em que `atual` não é `None`), **antes** da comparação de idempotência,
acrescentar:

```python
        # Re-derivar um dashboard propõe nomes parecidos com os do fonte. Como a
        # idempotência casa por (nome + dataset), um nome repetido atualizaria o
        # chart do fonte — alterando por dentro o dashboard que prometemos não
        # tocar. O `dashboard alvo:` protege o objeto dashboard; isto protege os
        # charts dele.
        if fonte_id is not None:
            donos = [d.get("id") for d in (detalhe.get("dashboards") or [])]
            if fonte_id in donos:
                return {"acao": "recusado_e_do_fonte", "slice_name": nome,
                        "id": atual["id"]}
```

- [ ] **Step 4: Acrescentar `--fonte` ao subcomando `create-chart`**

Em `main()`, no bloco que registra o subcomando `create-chart`, acrescentar a
mesma flag que `create-dashboard` já tem:

```python
    q.add_argument("--fonte", help="slug ou id do dashboard fonte; recusa "
                                   "sobrescrever um chart que pertença a ele.")
```

E no despacho do `create-chart`, resolver a flag do mesmo jeito que o
`create-dashboard` já resolve a dele (buscando o dashboard e saindo fatalmente se
o ref não resolver ou não trouxer `id`), passando o id resolvido como
`fonte_id=` para `c.create_chart(...)`.

- [ ] **Step 5: Rodar a suíte e conferir o `--help`**

Run:
```bash
cd /home/joaoegewarth/GovHub-skills/01-govhub/dashboard-superset-builder/scripts
python3 -m pytest test_superset_client.py -v
python3 superset_client.py create-chart --help
```
Expected: 54 passed; o `--help` do `create-chart` mostra `--file`, `--dry-run` e
`--fonte`.

- [ ] **Step 6: Commit**

```bash
cd /home/joaoegewarth/GovHub-skills
git add 01-govhub/dashboard-superset-builder/scripts/
git commit -m "fix(dashboard-superset-builder): --fonte também no create-chart

D3: re-derivar um dashboard propõe nomes parecidos com os do fonte, e a
idempotência casa por (nome + dataset) — três dos oito charts de uma
re-derivação real teriam atualizado charts do dashboard fonte, alterando por
dentro o dashboard que a skill promete não tocar.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 5: Camada 2 — conferência pós-escrita

**Files:**
- Modify: `01-govhub/dashboard-superset-builder/scripts/superset_client.py`
- Modify: `01-govhub/dashboard-superset-builder/scripts/test_superset_client.py`

**Interfaces:**
- Consumes: `create_chart` (Tarefas 2 e 4), `TIMEOUT`.
- Produces, para a Tarefa 6: `SupersetClient.dados_do_chart(chart_id: int) -> dict` devolvendo `{"rowcount": int, "amostra": dict | None}`; e o campo `verificacao` no retorno de `create_chart` nas ações `criado` e `atualizado`.

- [ ] **Step 1: Escrever os testes que falham**

Acrescentar ao final de `test_superset_client.py`:

```python
# --- conferência pós-escrita (camada 2) ------------------------------------

def test_dados_do_chart_resume_rowcount_e_amostra():
    s = MagicMock()
    s.get.return_value = resposta(corpo={"result": [
        {"rowcount": 1, "data": [{"UHs": 131499}]}]})

    assert cliente(s).dados_do_chart(355) == {"rowcount": 1,
                                              "amostra": {"UHs": 131499}}


def test_create_chart_inclui_verificacao_no_retorno():
    s = MagicMock()
    s.get.side_effect = [
        resposta(corpo={"count": 0, "result": []}),                 # list_all
        resposta(corpo={"result": [{"rowcount": 1,
                                    "data": [{"UHs": 131499}]}]}),  # dados_do_chart
    ]
    s.post.return_value = resposta(corpo={"id": 99})

    r = cliente(s).create_chart(payload_xy())

    assert r["verificacao"] == {"rowcount": 1, "amostra": {"UHs": 131499}}


def test_verificacao_que_falha_nao_derruba_a_criacao():
    s = MagicMock()
    erro = resposta(status=500)
    erro.raise_for_status.side_effect = requests.HTTPError("500")
    s.get.side_effect = [resposta(corpo={"count": 0, "result": []}), erro]
    s.post.return_value = resposta(corpo={"id": 99})

    r = cliente(s).create_chart(payload_xy())

    assert r["acao"] == "criado", "o chart já foi criado; não dá para fingir que não"
    assert "erro" in r["verificacao"]


def test_dry_run_nao_tenta_verificar():
    s = MagicMock()
    s.get.return_value = resposta(corpo={"count": 0, "result": []})

    r = cliente(s).create_chart(payload_xy(), dry_run=True)

    assert r["acao"] == "criaria"
    assert "verificacao" not in r, "não há chart para conferir num dry-run"
```

- [ ] **Step 2: Rodar e confirmar que falham**

Run:
```bash
cd /home/joaoegewarth/GovHub-skills/01-govhub/dashboard-superset-builder/scripts
python3 -m pytest test_superset_client.py -v
```
Expected: os 54 anteriores passam; os 4 novos falham com
`AttributeError: ... 'dados_do_chart'` e `KeyError: 'verificacao'`.

- [ ] **Step 3: Implementar `dados_do_chart`**

Na classe `SupersetClient`, logo **depois** de `get_chart`, acrescentar:

```python
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
```

- [ ] **Step 4: Ligar no `create_chart`**

Na classe `SupersetClient`, logo **depois** de `dados_do_chart`, acrescentar o
auxiliar:

```python
    def _verificacao(self, chart_id: int) -> dict:
        """Confere o que o chart devolve; um erro aqui não invalida a escrita."""
        try:
            return self.dados_do_chart(chart_id)
        except Exception as e:  # a escrita já aconteceu: reportar, não mascarar
            return {"erro": f"{type(e).__name__}: {e}"}
```

E nos dois `return` de `create_chart` que reportam escrita concluída, acrescentar
o campo. O de criação passa de:

```python
            return {"acao": "criado", "slice_name": nome, "id": novo["id"]}
```

para:

```python
            return {"acao": "criado", "slice_name": nome, "id": novo["id"],
                    "verificacao": self._verificacao(novo["id"])}
```

E o de atualização passa de:

```python
        return {"acao": "atualizado", "slice_name": nome, "id": atual["id"]}
```

para:

```python
        return {"acao": "atualizado", "slice_name": nome, "id": atual["id"],
                "verificacao": self._verificacao(atual["id"])}
```

Os retornos de `criaria`, `atualizaria`, `inalterado` e `recusado_e_do_fonte`
**não** ganham o campo: nos dois primeiros não há chart para conferir, e nos dois
últimos nada foi escrito.

- [ ] **Step 5: Rodar a suíte**

Run:
```bash
cd /home/joaoegewarth/GovHub-skills/01-govhub/dashboard-superset-builder/scripts
python3 -m pytest test_superset_client.py -v
```
Expected: 58 passed, sem warnings.

- [ ] **Step 6: Commit**

```bash
cd /home/joaoegewarth/GovHub-skills
git add 01-govhub/dashboard-superset-builder/scripts/
git commit -m "feat(dashboard-superset-builder): conferir o chart depois de escrever

Camada 2 das duas proteções contra derivação errada: depois de criar ou
atualizar, o cliente lê os dados do chart e devolve rowcount + amostra no campo
verificacao. Uma query errada aparece no próprio retorno do comando, em vez de
só quando alguém abre a página.

Falha na leitura vira verificacao.erro e não derruba a escrita, que já aconteceu.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 6: Subcomando `smoke`

**Files:**
- Modify: `01-govhub/dashboard-superset-builder/scripts/superset_client.py`

**Interfaces:**
- Consumes: `SupersetClient.create_chart` (Tarefas 2, 4, 5), `create_dashboard` (Tarefa 3), `_associar_chart` (Tarefa 3), `dados_do_chart` (Tarefa 5), `get_dashboard`, `get_chart`, `cliente_do_ambiente`, `_imprimir`, `TIMEOUT`.
- Produces: subcomando `smoke --dataset <id>`; nada consumido por tarefas posteriores.

- [ ] **Step 1: Implementar o ciclo**

Em `superset_client.py`, logo **antes** de `def main(`, acrescentar:

```python
def _smoke(c: "SupersetClient", dataset_id: int) -> dict:
    """Exercita o ciclo inteiro contra o Superset real e limpa o que criou.

    Existe porque os quatro defeitos que a primeira execução real expôs passaram
    por uma suíte inteiramente mockada: nada nunca tinha falado com um Superset.

    Cria um chart e um dashboard descartáveis, confere as duas coisas que o
    `position_json` sozinho não garante (dados certos e associação de fato), e
    apaga tudo — inclusive se um passo falhar.
    """
    marca = f"__smoke__ {int(time.time())}"
    params = json.dumps({"datasource": f"{dataset_id}__table",
                         "viz_type": "big_number_total",
                         "metric": {"expressionType": "SQL",
                                    "sqlExpression": "COUNT(*)",
                                    "label": "linhas"},
                         "adhoc_filters": []}, ensure_ascii=False)
    payload = {"slice_name": marca, "viz_type": "big_number_total",
               "datasource_id": dataset_id, "datasource_type": "table",
               "params": params}
    passos, chart_id, dash_id = [], None, None
    try:
        r = c.create_chart(payload)
        chart_id = r["id"]
        passos.append(("chart criado", r["acao"] == "criado"))
        passos.append(("dados do chart",
                       (r.get("verificacao") or {}).get("rowcount") == 1))

        d = c.create_dashboard({"dashboard_title": marca, "slug": marca.replace(" ", "-")},
                               [chart_id])
        dash_id = d["id"]
        passos.append(("dashboard criado", d["acao"] == "criado"))

        dash = c.get_dashboard(dash_id) or {}
        pos = json.loads(dash.get("position_json") or "{}")
        no_layout = sum(1 for v in pos.values()
                        if isinstance(v, dict) and v.get("type") == "CHART")
        # As duas metades que o defeito D4 separou: layout e associação.
        passos.append(("chart no layout", no_layout == 1))
        passos.append(("chart associado", len(dash.get("charts") or []) == 1))

        donos = [x.get("id") for x in (c.get_chart(chart_id) or {}).get("dashboards") or []]
        passos.append(("dashboard na lista do chart", dash_id in donos))
    finally:
        for caminho, id_ in (("dashboard", dash_id), ("chart", chart_id)):
            if id_ is None:
                continue
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
```

E acrescentar `import time` ao bloco de imports do topo do arquivo (junto de
`import json`, `import os`, `import re`, `import sys`).

- [ ] **Step 2: Registrar o subcomando**

Em `main()`, junto aos outros `sub.add_parser(...)`, acrescentar:

```python
    q = sub.add_parser("smoke", help="Ciclo completo contra o Superset real "
                                     "(cria, confere e apaga).")
    q.add_argument("--dataset", required=True, type=int,
                   help="id de um dataset qualquer, usado para um COUNT(*).")
```

E no despacho:

```python
    elif args.comando == "smoke":
        r = _smoke(c, args.dataset)
        _imprimir(r)
        return 0 if r["ok"] else 1
```

- [ ] **Step 3: Conferir que a suíte mockada não quebrou e que o subcomando aparece**

Run:
```bash
cd /home/joaoegewarth/GovHub-skills/01-govhub/dashboard-superset-builder/scripts
python3 -m pytest test_superset_client.py -q
python3 superset_client.py --help
```
Expected: 58 passed; o `--help` lista `smoke` junto dos outros oito subcomandos.

- [ ] **Step 4: Rodar o `smoke` de verdade**

Este passo precisa de credenciais no ambiente e de acesso ao Superset. Se não
estiverem disponíveis, pare e reporte — **não** marque a tarefa como concluída
sem esta execução, porque é o único passo do plano inteiro que exercita o
caminho real.

Run:
```bash
cd /home/joaoegewarth/GovHub-skills
set -a; . ./.env; set +a
cd 01-govhub/dashboard-superset-builder/scripts
python3 superset_client.py smoke --dataset 35; echo "exit=$?"
```
Expected: `"ok": true`, todos os passos com `"ok": true`, e `exit=0`. Confira que
não sobrou nada com `__smoke__` no nome:

```bash
python3 superset_client.py list-datasets --filtro __smoke__ | head -5
```

- [ ] **Step 5: Commit**

```bash
cd /home/joaoegewarth/GovHub-skills
git add 01-govhub/dashboard-superset-builder/scripts/
git commit -m "feat(dashboard-superset-builder): subcomando smoke

Ciclo completo contra um Superset real: cria chart e dashboard descartáveis,
confere que os dados voltam e que o chart está associado de fato (não só no
position_json), e apaga tudo. A capacidade de apagar fica dentro do smoke, não
vira subcomando — não se expõe deleção numa ferramenta que um agente opera.

Existe porque os quatro defeitos corrigidos aqui passaram por uma suíte
inteiramente mockada.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 7: Documentar no `SKILL.md`

**Files:**
- Modify: `01-govhub/dashboard-superset-builder/SKILL.md`

**Interfaces:**
- Consumes: `--fonte` no `create-chart` (Tarefa 4), o campo `verificacao` (Tarefa 5), o subcomando `smoke` (Tarefa 6), e as seções `## query_context` e `## Layout não é associação` de `references/superset-api.md` (Tarefa 1).
- Produces: nada.

- [ ] **Step 1: Ler o arquivo atual**

Run: `cat /home/joaoegewarth/GovHub-skills/01-govhub/dashboard-superset-builder/SKILL.md`
Localize a Fase 4 e a tabela de valores de `acao`.

- [ ] **Step 2: Acrescentar `--fonte` ao comando `create-chart` da Fase 4**

No passo da Fase 4 que mostra `create-chart --file componente.json`, troque o
bloco de comando por:

````markdown
   ```bash
   # re-derivando de um fonte, passe --fonte: recusa sobrescrever um chart que
   # pertença ao dashboard fonte (nomes parecidos colidem com facilidade)
   python3 scripts/superset_client.py create-chart --file componente.json --fonte <slug ou id>

   # dashboard novo do zero, sem fonte:
   python3 scripts/superset_client.py create-chart --file componente.json
   ```
````

- [ ] **Step 3: Documentar o campo `verificacao`**

Logo **depois** desse bloco, acrescentar:

````markdown
   A resposta traz `acao`, o `id` e — quando houve escrita — `verificacao`, com o
   que o chart devolve de verdade:

   ```json
   {"acao": "criado", "id": 355, "slice_name": "…",
    "verificacao": {"rowcount": 1, "amostra": {"UHs Contratadas": 131499}}}
   ```

   **Compare a amostra com o que você esperava.** Ela mostra o número que saiu,
   não se ele está certo — é instrumentação, não oráculo. Um filtro que não pegou
   costuma aparecer como um valor grande demais (uma soma que dobrou, por
   exemplo). Se `verificacao` trouxer `erro`, o chart foi criado mesmo assim:
   confira à mão antes de seguir.
````

- [ ] **Step 4: Acrescentar `smoke` à seção de pré-requisitos**

Na seção `## Pré-requisitos`, ao final, acrescentar:

````markdown
Se você mexeu no `superset_client.py`, rode o ciclo real antes de confiar nele:

```bash
python3 scripts/superset_client.py smoke --dataset <id de qualquer dataset>
```

Ele cria um chart e um dashboard descartáveis, confere que os dados voltam e que
a associação existe, e apaga tudo. Os testes de `test_superset_client.py` são
todos mockados — foi assim que quatro defeitos chegaram a um Superset real.
````

- [ ] **Step 5: Atualizar a tabela de valores de `acao`**

Na tabela que lista os valores de `acao`, acrescentar a linha:

```markdown
| `recusado_e_do_fonte` | O chart encontrado por (nome + dataset) pertence ao dashboard fonte. Nada foi escrito. Renomeie o componente — prefixar com o nome do dashboard novo resolve. |
```

- [ ] **Step 6: Conferir que os comandos citados existem**

Run:
```bash
cd /home/joaoegewarth/GovHub-skills
for cmd in list-datasets get-dataset get-dashboard get-chart create-chart \
           create-dashboard add-chart-to-dashboard smoke; do
  grep -q -- "\"$cmd\"" 01-govhub/dashboard-superset-builder/scripts/superset_client.py \
    && echo "ok $cmd" || echo "DIVERGENTE $cmd"
done
grep -c 'recusado_e_do_fonte\|verificacao\|--fonte' 01-govhub/dashboard-superset-builder/SKILL.md
```
Expected: oito linhas `ok`; o `grep -c` devolve ao menos `4`.

- [ ] **Step 7: Validar os manifestos**

Run: `cd /home/joaoegewarth/GovHub-skills && bash scripts/validar-plugins.sh`
Expected: exit 0, contagem inalterada (53 skills / govhub-core 5).

- [ ] **Step 8: Commit**

```bash
cd /home/joaoegewarth/GovHub-skills
git add 01-govhub/dashboard-superset-builder/SKILL.md
git commit -m "docs(dashboard-superset-builder): documentar --fonte, verificacao e smoke

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Self-Review (feito na escrita do plano)

**1. Cobertura da spec:**
- D1 (derivar e gravar `query_context`) → Tarefa 2 Steps 3–4. ✅
- D2 (idempotência inclui `query_context`) → Tarefa 2 Step 4. ✅
- D3 (`--fonte` no `create-chart`) → Tarefa 4. ✅
- D4 (associar acrescentando) → Tarefa 3. ✅
- Camada 1 (lista `VIZ_SUPORTADOS`, recusa alta) → Tarefa 2 Step 3 + teste em Step 1. ✅
- Camada 2 (conferência pós-escrita, erro não derruba) → Tarefa 5. ✅
- Subcomando `smoke` (5 passos + limpeza no `finally`) → Tarefa 6. ✅
- Seção nova em `superset-api.md` → Tarefa 1. ✅
- `SKILL.md` documentando o novo → Tarefa 7. ✅
- Testes mockados listados na spec → distribuídos nas Tarefas 2 (derivação, recusa de tipo, D2), 3 (append), 4 (recusa do fonte), 5 (verificação e seu erro). ✅
- Fora de escopo (filtros nativos, deleção no CLI, smoke em CI) → Global Constraints. ✅

**2. Placeholders:** nenhum "TBD/TODO". Onde o texto diz "use o nome de variável
que já existe ali" (Tarefa 3 Step 4), é porque o implementador lê o arquivo no
Step 1 da tarefa e o nome é local àquele bloco — a instrução é precisa sobre
*onde* e *o quê*, e o Step 5 verifica por teste.

**3. Consistência de nomes:** `VIZ_SUPORTADOS`, `BASE_QUERY`, `_filtro_simples`,
`_colunas_do_params`, `_query`, `build_query_context`, `_associar_chart`,
`dados_do_chart`, `_verificacao`, `_smoke`, e as chaves `acao`, `verificacao`,
`rowcount`, `amostra`, `recusado_e_do_fonte` aparecem idênticas entre as tarefas
que as produzem e as que as consomem. Contagens de teste encadeiam:
43 → 50 (T2) → 53 (T3) → 54 (T4) → 58 (T5) → 58 (T6, sem teste mockado novo). ✅
