# Design — Corrigir o cliente Superset: `query_context`, associação de charts, colisão com o fonte

Data: 2026-09-06
Skill afetada: `01-govhub/dashboard-superset-builder/`
Origem: a primeira execução ponta a ponta contra um Superset real (re-derivação do
dashboard 3 "FAR" no dashboard 18 "FAR — Visão Executiva", 2026-09-06). Quatro
defeitos apareceram que 43 testes não pegaram, porque todos mockam HTTP e nenhum
exercitou o caminho real até o Superset.

## Os quatro defeitos

### D1 (Crítico) — `create-chart` não grava `query_context`, e os filtros não valem

Os charts nasceram com `adhoc_filters` corretos em `params`, mas sem
`query_context`. A API de dados do Superset lê os filtros do `query_context`, não
do `params`. O KPI "UHs Contratadas" mostrou **262.998** em vez de 131.499 — o
dobro exato, porque `gold_mapa_nacional` guarda linhas em dois níveis (`nivel` =
`uf` e `regiao`) e o filtro `nivel = 'uf'` simplesmente não aplicou.

Número errado, plausível, sem nenhum erro na tela. Controle que provou a causa: o
chart 64 do fonte, criado pela interface, tem `query_context` com
`filters: [{col: nivel, op: '==', val: 'uf'}]` e devolve 131.499.

### D2 (Importante) — a idempotência ignora `query_context`, então não conserta

Ao reaplicar os payloads já com `query_context`, o cliente devolveu `inalterado`
nos 8 charts: `create_chart` compara só `datasource_id` e `params`, e o `params`
não tinha mudado. Um chart com `query_context` ausente ou velho **nunca pode ser
reparado** pela ferramenta.

### D3 (Importante) — re-derivar pode sobrescrever os charts do dashboard fonte

Três dos oito nomes que o esboço propôs colidiam com os charts 64, 65 e 93 — que
pertencem ao dashboard 3 — no mesmo dataset. Como `create_chart` é idempotente por
(nome + dataset), ele os teria **atualizado**, alterando o fonte por dentro. A
promessa "o fonte nunca é tocado" protegia o objeto dashboard, não os charts dele.

### D4 (Crítico) — `create-dashboard` não associa os charts, e o dashboard nasce vazio

Layout e associação são coisas separadas no Superset. O `position_json` diz onde
cada chart fica; a associação real vive em `dashboard_slices` (exposta como o campo
`charts` do dashboard e `dashboards` do chart). `create_dashboard` monta o layout e
nunca escreve a associação:

```
dashboard 18 (novo):  charts associados=0   charts no position_json=8
dashboard  3 (fonte): charts associados=24  charts no position_json=24
```

O usuário abriu a página e estava vazia. A verificação da execução tinha conferido
o `position_json` e dado por bom — o campo que denunciaria (`charts`) não foi
comparado.

## Causa raiz comum

O `api.md` que originou `references/superset-api.md` **não menciona**
`query_context` nem `dashboard_slices`. Sem esse conhecimento, os dois conceitos
não entraram no design, nem no plano, nem em três rodadas de review. E como toda a
suíte mocka HTTP, nada exercitou o caminho real onde a ausência aparece.

## Correções

### D1 — derivar o `query_context` do `params`

`create_chart` passa a montar o `query_context` a partir do `params` e gravá-lo
junto: filtros a partir dos `adhoc_filters` do tipo `SIMPLE` (convertidos para
`{col, op, val}`), métricas de `metric`/`metrics`, colunas de
`groupby`/`x_axis`/`entity`. `mixed_timeseries` gera **duas** queries, uma para
`metrics` e outra para `metrics_b`, cada uma com seus próprios filtros.

Forma do `query_context` (copiada do chart 64, criado pela interface):

```json
{"datasource": {"id": 35, "type": "table"}, "force": false,
 "form_data": {…o params…}, "result_format": "json", "result_type": "full",
 "queries": [{"filters": [...], "metrics": [...], "columns": [...],
              "extras": {"having": "", "where": ""}, "annotation_layers": [],
              "series_limit": 0, "order_desc": true, "url_params": {},
              "custom_params": {}, "custom_form_data": {}, "applied_time_extras": {}}]}
```

Decisão: **o cliente deriva**, em vez de exigir que quem chama forneça. Uma fonte
de verdade (o `params`), e o agente que monta o payload não precisa escrever a
mesma informação duas vezes.

### D2 — incluir `query_context` na comparação de idempotência

A comparação passa a olhar `datasource_id`, `params` **e** `query_context`, os dois
últimos comparados como JSON parseado (não string crua), como já é feito hoje para
`params`.

### D3 — `--fonte` também no `create-chart`

`create_chart` ganha `fonte_id: int | None`. Se o chart encontrado por (nome +
dataset) pertencer ao dashboard fonte, devolve `{"acao": "recusado_e_do_fonte"}`
sem escrever. O CLI ganha `--fonte <slug ou id>`, resolvido para id, igual ao
`create-dashboard`.

### D4 — associar os charts, acrescentando à lista

`create_dashboard` passa a associar cada chart ao dashboard depois de criá-lo. Para
cada chart: lê a lista `dashboards` atual, **acrescenta** o novo id e faz `PUT`.
Nunca substitui — `PUT {"dashboards": [18]}` numa lista que já continha o 3 teria
arrancado o chart do dashboard 3.

## Duas camadas de proteção

### Camada 1 — lista de `viz_type` conhecidos

A derivação só aceita tipos que sabe montar. Lista inicial, os cinco exercitados na
execução real: `big_number_total`, `country_map`, `echarts_timeseries_bar`,
`mixed_timeseries`, `pie`. Um tipo fora dela faz `create_chart` levantar
`ValueError` nomeando o tipo e a lista, em vez de gerar uma query pela metade.

Ampliar a lista é uma linha — mas exige que alguém confira a forma real daquele
tipo antes, que é a disciplina que faltou.

### Camada 2 — conferência pós-escrita

Depois de criar ou atualizar, o cliente lê `GET /api/v1/chart/{id}/data/`
(verificado: devolve `result[0].rowcount` e `result[0].data`) e inclui no
resultado:

```json
{"acao": "criado", "id": 355, "slice_name": "…",
 "verificacao": {"rowcount": 1, "amostra": {"UHs Contratadas": 131499}}}
```

Se a leitura falhar, vira `{"verificacao": {"erro": "…"}}` — não derruba a criação,
que já aconteceu, mas fica registrado.

Limite honesto: a conferência mostra **o número que saiu**, não se ele está certo.
Teria pego o D1 (262.998 salta aos olhos contra 131.499 esperado) só porque alguém
compara com o que esperava. É instrumentação, não oráculo.

## Subcomando `smoke`

`superset_client.py smoke --dataset <id>` — ciclo completo contra o Superset real:

1. cria um `big_number_total` com `COUNT(*)` sobre o dataset (funciona em qualquer
   dataset, sem precisar conhecer coluna), nome `__smoke__ <timestamp>`;
2. confere que `GET /chart/{id}/data/` devolve `rowcount: 1`;
3. cria um dashboard com esse chart e confere as **duas** coisas que o D4 separou:
   `len(charts) == 1` **e** um nó CHART no `position_json`;
4. confere que a lista `dashboards` do chart contém o dashboard novo;
5. apaga dashboard e chart, e confere que sumiram.

A capacidade de apagar fica **dentro do `smoke`**, não vira subcomando de CLI — não
se expõe superfície de deleção numa ferramenta que um agente opera. A limpeza roda
mesmo se um passo falhar.

Não entra em CI: exige VPN e credenciais. É uma checagem de 30 segundos que alguém
roda antes de confiar numa mudança no cliente.

## Testes

Mockados, onde mock é o certo (lógica pura):

- derivação do `query_context` por `viz_type`, incluindo as duas queries do
  `mixed_timeseries` e a conversão de `adhoc_filters` para `{col, op, val}`;
- recusa de `viz_type` fora da lista;
- idempotência enxergando mudança **só** no `query_context` (o caso do D2);
- `create_chart` recusando quando o chart encontrado é do fonte (D3);
- associação acrescentando à lista `dashboards` em vez de substituir (D4);
- a conferência pós-escrita registrando `erro` quando a leitura de dados falha, sem
  derrubar a criação.

## Arquivos

```
01-govhub/dashboard-superset-builder/
├── SKILL.md                        Fase 4: --fonte no create-chart, o campo
│                                   verificacao, e quando rodar o smoke
├── scripts/superset_client.py      D1–D4, camadas 1 e 2, smoke
├── scripts/test_superset_client.py testes das partes deriváveis
└── references/superset-api.md      NOVO: seção sobre query_context e sobre
                                    layout ≠ associação
```

A seção nova em `superset-api.md` é o que impede o conhecimento de se perder de
novo — os dois conceitos que faltavam ali são exatamente os que causaram D1 e D4.

## Fora de escopo

- Filtros nativos de dashboard (`native_filter_configuration`) — continua fora.
- Subcomando de deleção exposto no CLI.
- Rodar o `smoke` em CI.
