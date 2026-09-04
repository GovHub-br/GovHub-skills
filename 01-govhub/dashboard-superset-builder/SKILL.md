---
name: dashboard-superset-builder
description: >-
  Planeja e cria dashboards no Superset: gera um esboço estruturado em markdown (com
  nomes de campo já compatíveis com o schema do Superset) e um wireframe do layout,
  pede validação humana explícita, e só depois cria de fato os charts e o dashboard
  no Superset via MCP. Use sempre que o usuário pedir para "montar um dashboard no
  Superset", "criar um gráfico/chart no Superset", "planejar um dashboard", "esboçar
  um dashboard", "adicionar um chart a um dashboard existente do Superset" ou
  "construir um dashboard".
---

# Dashboard Superset Builder

Esta skill leva um dashboard do pedido inicial do dev até os charts criados de
verdade no Superset, em 5 fases. **Nenhuma chamada que cria ou altera algo no
Superset acontece antes da Fase 3 (validação humana) ser concluída com uma
aprovação explícita.** Essa é uma barreira dura: se a resposta do dev não for uma
aprovação clara, não avance para a Fase 4 — mesmo que pareça óbvio que ele ia
aprovar.

## Fase 0 — Contexto e escolha do servidor MCP

Pergunte ao dev (só o que ainda não estiver claro na conversa):

1. **Perfil do usuário final do dashboard** — nível de experiência digital
   (iniciante / intermediário / avançado / especialista) e nível de conhecimento de
   negócio (leigo / técnico / especialista / gestor). Ver
   [`references/diretrizes-dashboard.md`](references/diretrizes-dashboard.md) seção
   "Perfil do usuário" para o que cada combinação implica em densidade e volume de
   informação.
2. **Dispositivo principal** (desktop / tablet / mobile) — dashboard corporativo
   tende a desktop, mas confirme.
3. **Qual pergunta o dashboard precisa responder em 5 segundos** — essa é a
   informação primária, a que recebe maior destaque no wireframe.
4. **Dataset alvo no Superset**, se já existir (nome, ID ou UUID). Se o dev não
   souber, a Fase 1 chama `list_datasets` (somente leitura) para ajudar a escolher;
   só se ainda assim não der para escolher é que o esboço segue com nomes
   descritivos a confirmar antes da Fase 4.
5. **Dashboard novo ou já existente? Se existente, qual (ID, UUID ou título)?** —
   define a ramificação da Fase 4 (`add_chart_to_existing_dashboard` x
   `generate_dashboard`). Registrado no cabeçalho do esboço da Fase 2 como
   `dashboard alvo:`.

**Nunca assuma o endereço de um servidor MCP do Superset.** Diferentes sessões e
ambientes têm servidores diferentes, e o endereço pode mudar a qualquer momento.
Em vez disso:

- Liste os servidores MCP conectados na sessão atual.
- Se houver **exatamente um** com o padrão de tools de um Superset MCP
  (`get_instance_info`, `health_check`, `search_tools`, `call_tool` como camada
  fixa, tools reais de chart/dashboard/dataset aparecendo via `search_tools`),
  confirme com o dev que é esse antes de usar — não assuma sozinho.
- Se houver mais de um, ou nenhum com esse padrão, pergunte explicitamente ao dev
  qual servidor usar.
- Se nenhum servidor adequado estiver conectado, explique que é preciso conectar
  um servidor MCP do Superset (token em variável de ambiente ou secret manager —
  **nunca em arquivo do repositório**) e não prossiga sem confirmação de que a
  conexão existe.

Com o servidor escolhido, confirme que está acessível chamando `health_check` ou
`get_instance_info` (via `call_tool`) antes de seguir para a Fase 1.

## Fase 1 — Descoberta no Superset (somente leitura)

Se o dev indicou um dataset existente, chame `get_dataset_info` e/ou `get_schema`
(via `call_tool`) para obter as colunas, métricas e dimensões **reais** daquele
dataset. Use esses nomes reais no esboço da Fase 2 em vez de inventar nomes.

Se o dev não sabe qual dataset usar, chame `list_datasets` (somente leitura) e
mostre os candidatos para ele escolher um; então chame `get_dataset_info` /
`get_schema` no escolhido para pegar os nomes reais. Só se o dev ainda assim não
conseguir escolher (ou o dataset ainda não existir) é que a Fase 2 segue com nomes
descritivos — nesse caso **sinalize explicitamente no esboço** que esses nomes
(dataset e colunas) são placeholders e precisam ser confirmados antes da Fase 4.

Essas chamadas são somente leitura — não têm a tag `mutate` — então não precisam de
aprovação humana.

## Fase 2 — Montar o esboço (markdown + wireframe)

Produza um único arquivo markdown. Antes dos blocos de componente, um cabeçalho do
esboço com uma linha `dashboard alvo:` — `novo: "<título>"` ou
`existente: <id/uuid/título>`, conforme a resposta da pergunta 5 da Fase 0. Esse
campo passa pelo gate da Fase 3 junto com o resto do esboço e decide a ramificação
da Fase 4.

Depois do cabeçalho, um bloco `## Componente: <nome>` por chart. Para cada
componente:

- Aplique a hierarquia de informação (Primária / Secundária / Complementar /
  Descartável) e a densidade visual — "média" é o padrão para dashboard corporativo,
  a não ser que o perfil de usuário da Fase 0 sugira outra coisa. Ver
  [`references/diretrizes-dashboard.md`](references/diretrizes-dashboard.md) seções
  "Hierarquia de informação" e "Densidade visual".
- Use os nomes de campo exatos que o Superset espera para o `viz_type` escolhido —
  consulte [`references/superset-schema.md`](references/superset-schema.md). Se o
  `viz_type` não estiver nesse cache, chame `get_chart_type_schema` (via
  `call_tool`, com `chart_type` e `include_examples: true`) para obter o schema ao
  vivo antes de montar o bloco — não invente nomes de campo.

Formato de cada bloco (os campos **dentro de `config`** são exatamente os do schema
do `viz_type` escolhido — veja [`references/superset-schema.md`](references/superset-schema.md)):

```markdown
## Componente: Consumo Total do Período
- dataset: consumo_energia (id 42)   # vai no parâmetro do generate_chart, não em config
- viz_type: xy
- prioridade: primária
- config:
    chart_type: xy
    kind: line
    x: { name: data_referencia }
    y: [ { name: consumo_kwh, aggregate: SUM } ]
    filters: [ { column: unidade, op: "=", value: "Matriz" } ]
```

Os campos de `config` mudam por `viz_type` (ex.: `pie` usa `dimension` + `metric`;
`table` usa `columns`; `big_number` usa `metric`). Nunca use `adhoc_filters` nem
SQL cru em `filters` — o schema exige filtros estruturados `column`/`op`/`value`.

Depois do último bloco, gere um **wireframe em ASCII ou Mermaid**, embutido no
mesmo arquivo markdown, mostrando a posição relativa dos componentes num grid de 2
colunas (mesmo padrão de auto-posicionamento do `add_chart_to_existing_dashboard`).
Exemplo de wireframe ASCII:

```
┌────────────────────────────┬────────────────────────────┐
│ Consumo Total do Período   │ Distribuição por Unidade   │
│ (linha · primária)         │ (pizza · secundária)       │
├────────────────────────────┴────────────────────────────┤
│ Histórico Detalhado (tabela · complementar)             │
└─────────────────────────────────────────────────────────┘
```

## Fase 3 — Validação humana (gate obrigatório)

Apresente o esboço completo (markdown + wireframe) ao dev e pergunte explicitamente:
aprovar como está, ajustar algo, ou cancelar.

- Se pedir ajuste: volte para a Fase 2, gere a versão ajustada, e apresente de novo
  para nova aprovação. Não "corrija e siga sozinho".
- Se cancelar: pare aqui.
- **Só uma resposta afirmativa e explícita libera a Fase 4.** Uma resposta vaga
  ("ok", "bacana", silêncio) não conta como aprovação — peça confirmação direta
  antes de prosseguir.
- Se o esboço ainda contém nomes placeholder de dataset ou de coluna não
  confirmados, o humano pode aprovar o **design**, mas essa aprovação **não**
  libera a Fase 4: volte para a Fase 1 e vincule os nomes reais primeiro (a Fase 4
  precisa de um `dataset` real e nomes de coluna reais para sequer rodar).

## Fase 4 — Criação real no Superset

**Passo 0 (antes da primeira chamada):** descubra a assinatura real de
`generate_chart` (e de `add_chart_to_existing_dashboard` / `generate_dashboard`)
via `search_tools` + uma inspeção do `inputSchema` — não presuma os nomes dos
parâmetros wrapper (como o dataset é passado, título/nome do chart, `save_chart`).
O cache em [`references/superset-schema.md`](references/superset-schema.md) cobre só
o objeto `config`/`request` interno, não os parâmetros da tool.

Para cada componente aprovado, na ordem em que aparecem no esboço:

1. `generate_chart`: o bloco `config:` do componente vai no objeto `request` da
   tool, montado conforme o schema real do `viz_type` (do cache em
   [`references/superset-schema.md`](references/superset-schema.md), ou consultado
   ao vivo via `get_chart_type_schema` se o tipo não estiver cacheado). O `dataset`
   do componente, o título do chart e `save_chart=True` são parâmetros wrapper da
   tool (nomes exatos vindos do Passo 0), não campos de `config`.
2. Ramifique pelo campo `dashboard alvo:` do cabeçalho do esboço:
   - `existente: <id/uuid/título>` → `add_chart_to_existing_dashboard` para cada
     chart criado.
   - `novo: "<título>"` → `generate_dashboard` (passando a lista de chart IDs
     criados nesta rodada) **apenas** na primeira leva de charts do dashboard novo.
   Nunca use `generate_dashboard` como fallback de
   `add_chart_to_existing_dashboard`.

Se um componente falhar, registre o erro e continue tentando os demais — não pare
a rodada inteira por causa de um componente. Ao final, apresente um resumo com o
resultado de cada componente (sucesso com ID/link, ou erro com a mensagem) e o
link do dashboard final.

## Fora de escopo (v1)

- Editar ou atualizar dashboards que não foram criados por esta skill.
- Criar datasets virtuais via SQL (`create_virtual_dataset`) — se o dev precisar
  disso, avise que está fora do escopo atual desta skill.

## Referências

- [`references/diretrizes-dashboard.md`](references/diretrizes-dashboard.md) —
  resumo curado do guia de design (perfil de usuário, hierarquia de informação,
  densidade visual, contexto de uso, cores, tipografia) aplicado a dashboard.
- [`references/superset-schema.md`](references/superset-schema.md) — schema real
  do Superset por `viz_type`, obtido ao vivo via `get_chart_type_schema` durante a
  construção desta skill, para o planejamento (Fases 0–3) não depender de uma
  chamada ao MCP a cada uso.
