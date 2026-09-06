# API REST do Superset — o que a skill precisa saber

Conhecimento operacional destilado de scripts de produção que publicam
dashboards no Superset por API. As armadilhas da última seção custaram tempo
real e **não estão na documentação oficial**.

Quem implementa isto em código é `scripts/superset_client.py`; este documento é
o "porquê" por trás daquele script.

## Autenticação

Credenciais em variável de ambiente (nunca em arquivo versionado):

```
SUPERSET_URL=https://…
SUPERSET_USERNAME=…
SUPERSET_PASSWORD=…
```

**Use o cookie de sessão, não o JWT.** O Superset oferece os dois caminhos, mas
nesta classe de instância o bearer de `/api/v1/security/login` é **cego para
parte dos dashboards**: `GET /api/v1/dashboard/<slug>` devolve 404 com bearer e
200 com cookie, e a listagem com bearer omite os mesmos dashboards. Isso já fez
um script relatar "já existente, preservado" para um dashboard que ele podia e
precisava atualizar. O cookie enxerga estritamente mais.

O fluxo tem três passos:

1. `GET /login/` — o `csrf_token` é um campo oculto no HTML.
2. `POST /login/` com `username`, `password` e `csrf_token` — autenticação por
   **formulário**, que devolve o cookie de sessão.
3. `GET /api/v1/security/csrf_token/` — o token daí vai no header `X-CSRFToken`
   da sessão, junto com `Referer` apontando para a base. **O Superset recusa
   escrita sem `Referer`.**

## Paginação

A API **ignora `page` e `page_size` soltos** e devolve 20 itens em silêncio. O
parâmetro correto é `q`, em [Rison](https://github.com/Nanonid/rison):

```
GET /api/v1/dataset/?q=(page:0,page_size:100)
```

Com filtro:

```
q=(filters:!((col:table_name,opr:ct,value:'gld_boletim')),page:0,page_size:100)
```

O valor vai entre **aspas simples de Rison**, com `!` e `'` internos escapados
como `!!` e `!'`. Sem as aspas, um valor com espaço (`consumo de agua`) produz
Rison malformado e a API responde 400 — que, engolido, viraria "não existe".
Números vão nus; booleanos e nulo são os literais `!t`, `!f` e `!n`.

Para percorrer tudo: avance `page` até que a soma dos resultados alcance o
`count` da resposta, ou até vir uma página vazia.

## Ordem de criação

Cada recurso depende do anterior; criar fora de ordem devolve erro sem
explicação útil.

```
database  →  dataset  →  chart  →  dashboard
 conexão     tabela ou    visual    layout +
 ao banco    SQL virtual            filtros
```

A skill entra a partir de **chart** — criar database e dataset está fora do
escopo dela.

**Chart** — `POST /api/v1/chart/`:

```json
{
  "slice_name": "PIB da Construção Civil",
  "viz_type": "table",
  "datasource_id": 42,
  "datasource_type": "table",
  "params": "{\"datasource\":\"42__table\",\"viz_type\":\"table\",…}"
}
```

`params` é **string JSON**, não objeto. E o `datasource` de dentro dele repete o
id no formato `<id>__table` — os dois precisam concordar.

**Dashboard** — `POST /api/v1/dashboard/`:

```json
{
  "dashboard_title": "Boletim de Conjuntura",
  "slug": "boletim-conjuntura",
  "published": true,
  "json_metadata": "{…}",
  "position_json": "{…}"
}
```

`json_metadata` e `position_json` também são **strings JSON**.

## Idempotência

Rodar duas vezes não pode duplicar nada. O padrão é **procurar antes de criar** e
**conferir o conteúdo** quando já existe — achar pelo nome e seguir adiante não
basta (ver a primeira armadilha):

1. Procurar o existente. Para **chart**, na listagem, pela dupla `slice_name` +
   `datasource_id`: só os dois juntos identificam o chart. `slice_name` sozinho
   é genérico o bastante ("Total do Período") para casar com um chart de outro
   dashboard, sobre outro dataset, e sobrescrevê-lo em silêncio. Para
   **dashboard**, pelo slug, com `GET /api/v1/dashboard/<slug>` — nunca pela
   listagem (ver a segunda armadilha), e por isso o slug é obrigatório.
2. Se não existe → criar.
3. Se existe → comparar o conteúdo relevante (para chart, `params`). Igual → não
   fazer nada. Diferente → `PUT`.

Consequência aceita da busca por nome + dataset: um chart cujo dataset mudou é
criado como novo em vez de atualizado. É o lado seguro do erro — o chart antigo
continua visível e auditável, em vez de ser sobrescrito.

E erro HTTP na busca **estoura**, nunca vira lista vazia: o corpo de erro do
Superset não tem `result` nem `count`, então um 500 ou um 401 de sessão expirada
lido como "não achei nada" faz a etapa 2 duplicar tudo que já existe.

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

## `position_json`

O front do Superset 6 lê `node.meta.width` ao montar a página. Ligar um chart
direto no `ROOT_ID`, ou omitir `meta` em qualquer nó estrutural, quebra a página
inteira com `n.meta is undefined`.

A cadeia mínima é `ROOT → GRID → ROW → CHART`, e **todos os nós levam `meta`**,
mesmo vazio. O grid do Superset tem 12 colunas de largura; um layout de duas
colunas usa `width: 6` por chart.

Num dashboard que já tem layout, o publicado é a fonte da verdade e o chart novo
entra nele por splice. Quando a árvore publicada não oferece lugar para uma ROW —
nem GRID nem TAB, um `ROOT → MARKDOWN` por exemplo — a escrita é **recusada**.
Gerar o grid canônico ali descartaria o conteúdo publicado, e remover nó de
layout está fora do escopo da skill: não haveria como desfazer.

## Armadilhas

**O chart não some quando o dataset some.** Ele continua na tela e apenas para de
carregar — ninguém é avisado. Uma renomeação de schema já deixou 27 charts órfãos
porque o script achava o chart pelo nome, reaproveitava o id e nunca conferia o
dataset.

**A listagem não revela todos os dashboards.** `GET /api/v1/dashboard/` pode
omitir dashboards que `GET /api/v1/dashboard/<slug>` devolve normalmente. Para
saber se existe, **busque pelo slug e devolva o id**, não um booleano — é o id
que permite atualizar em vez de só constatar.

**Dataset virtual guarda as colunas antigas.** Se o SQL passa a devolver outras
colunas, o dataset segue pedindo as de antes e o chart quebra com
`column "…" does not exist`.

**Execução completa sobrescreve ajustes feitos na interface.** Quem mexeu no
layout pelo Superset perde. Leia o layout publicado antes de reescrevê-lo.

**Apagar dataset exige que nenhum chart aponte para ele.** Confira na hora, não
com uma listagem de dez minutos atrás.

**Recorte de período é filtro, não dashboard.** Três dashboards que só diferem no
`default_filters` são três cópias para manter em dia; um dashboard com filtro
nativo na coluna resolve.

## Sobre schema de chart por `viz_type`

A API REST **não expõe** uma abstração tipada por `viz_type` (não há equivalente
ao `get_chart_type_schema` que o MCP oferecia). O campo `params` é o `form_data`
nativo do Superset, específico de cada `viz_type` e sem schema formal publicado.

A técnica de substituição é **exemplo-guiado**: leia um chart existente do
`viz_type` desejado (`get-chart <id>`) e use o `params` dele como referência de
forma. Não invente nomes de campo.
