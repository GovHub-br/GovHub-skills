---
name: dashboard-superset-builder
description: >-
  Planeja e cria dashboards no Superset: gera um esboço estruturado em markdown (com
  nomes de campo já compatíveis com o schema do Superset) e um wireframe do layout,
  pede validação humana explícita, e só depois cria de fato os charts e o dashboard
  no Superset via MCP. Use sempre que o usuário pedir para "montar um dashboard no
  Superset", "criar um gráfico/chart no Superset", "planejar um dashboard", "esboçar
  um dashboard", "adicionar um chart a um dashboard existente do Superset",
  "construir um dashboard", "recriar / reconstruir um dashboard", "um dashboard
  novo baseado em outro" ou "o mesmo dashboard com outra organização / outros
  gráficos".
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
5. **De onde vem o dashboard?** Três respostas possíveis:
   - `novo do zero` — Fase 4 usa `generate_dashboard`; Fase 1 faz descoberta de
     dataset normal.
   - `acrescentar a existente: <id/uuid/título>` — Fase 4 usa
     `add_chart_to_existing_dashboard`; Fase 1 faz descoberta de dataset normal.
   - `novo a partir do fonte: <id/uuid/título>` — Fase 4 usa `generate_dashboard`
     (o resultado é um dashboard **novo**); a **Fase 1b** lê o dashboard fonte
     antes da Fase 2.

   A escolha é registrada no cabeçalho do esboço da Fase 2 como `dashboard alvo:`.

   **Oferta proativa:** se o dev mencionar um dashboard que já existe com intenção
   de "melhorar", "reorganizar" ou "mudar a cara", responda que a skill **não
   edita** o original, mas pode criar um **novo a partir dele** — e, se ele
   aceitar, trate a pergunta 5 como `novo a partir do fonte`.

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

Se o dataset **não existe ainda** no Superset, entregue o esboço como artefato de
design e avise o dev de que a Fase 4 só roda depois que o dataset existir na
instância — criar o dataset (inclusive dataset virtual via SQL) está fora do escopo
desta skill. Não fique em loop Fase 1 ↔ Fase 3: pare aqui e devolva a pendência ao
dev.

Essas chamadas são somente leitura — não têm a tag `mutate` — então não precisam de
aprovação humana.

## Fase 1b — Ler o dashboard fonte (somente leitura)

Roda **só** quando a pergunta 5 da Fase 0 foi `novo a partir do fonte:
<id/uuid/título>`. Todas as chamadas aqui são somente leitura (tools com tag
`discovery`) — **não precisam de aprovação humana**. Nenhuma escreve no dashboard
fonte.

1. `get_dashboard_info(<ref do fonte>)` (via `call_tool`) → título, lista de charts
   com seus IDs, e o layout.
2. Para cada chart: `get_chart_info(<chart_id>)` → recupere `dataset`, `viz_type`
   original, métricas, dimensões/`groupby` e filtros (do `form_data`/params do
   chart).
3. Monte a lista de componentes pré-preenchida para a Fase 2 — um bloco
   `## Componente: <nome>` por chart, com **só os campos de dados**: a linha
   `dataset:` e o miolo de `config` que mapeia limpo (métricas, dimensões,
   `filters` estruturados `column`/`op`/`value`). **Não** preencha `viz_type`,
   título nem posição — isso fica para a Fase 2 redecidir do zero.
4. Capture o **layout original** e os **filtros nativos do dashboard** como um
   bloco de referência textual para o topo do esboço, com o rótulo
   `Estado atual do fonte:` — explicitamente uma referência ("era assim"), nunca um
   ponto de partida.

Casos de borda — **registre no esboço e siga**, nunca aborte a fase:

- Chart com `viz_type` fora dos 7 do cache (`references/superset-schema.md`), ou
  `form_data` que não mapeia limpo → traga o que der (dataset, métricas, filtros) e
  marque o bloco com `# viz_type a escolher / config a confirmar na Fase 3`.
- `get_chart_info` falha (permissão, chart órfão, dataset removido) → pule o chart,
  siga nos outros, e **liste as falhas** ao fim da Fase 1b.
- Vários charts no mesmo dataset → normal, sem tratamento especial.
- Filtro do chart que é expressão SQL/adhoc → não invente equivalente estruturado;
  marque o bloco com `# filtro do fonte a reconstruir`.

O `dataset` recuperado por `get_chart_info` já é uma referência real (vem de um
chart vivo), então o gate de "nomes placeholder" da Fase 3 não se aplica a
componentes re-derivados — a menos que o dataset tenha sido removido, caso já
coberto pelo caso de borda acima.

A saída (o bloco `Estado atual do fonte:` + os blocos de componente pré-preenchidos)
entra na Fase 2 exatamente como um esboço montado à mão.

## Fase 2 — Montar o esboço (markdown + wireframe)

Produza um único arquivo markdown. Antes dos blocos de componente, um cabeçalho do
esboço com uma linha `dashboard alvo:`, conforme a resposta da pergunta 5 da Fase 0:

- `novo: "<título>"`
- `existente: <id/uuid/título>`
- `novo a partir de: <id/uuid/título do fonte> → "<título novo>"`

Esse campo passa pelo gate da Fase 3 junto com o resto do esboço e decide a
ramificação da Fase 4. Quando for `novo a partir de:`, o esboço também começa com
o bloco de referência `Estado atual do fonte:` produzido pela Fase 1b (ver Fase 1b
e o parágrafo de re-derivação mais abaixo nesta fase).

**Se o `dashboard alvo:` for `novo a partir de:`** — comece o arquivo com o bloco
`Estado atual do fonte:` produzido pela Fase 1b (layout + filtros nativos do fonte,
como texto), deixando claro que é referência, não ponto de partida. Trate os blocos
de componente que a Fase 1b pré-preencheu como qualquer esboço: escolha `viz_type`,
hierarquia (Primária/Secundária/Complementar/Descartável) e posição **do zero** —
os dados (dataset, métricas, dimensões, filtros) vêm do fonte, a forma não. Qualquer
componente ainda marcado `# viz_type a escolher`, `# config a confirmar` ou
`# filtro do fonte a reconstruir` tem que ser resolvido antes de apresentar o
esboço na Fase 3.

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
- Se algum componente ainda está marcado `# viz_type a escolher`,
  `# config a confirmar` ou `# filtro do fonte a reconstruir` (vindo da Fase 1b),
  isso **não** libera a Fase 4 — resolva primeiro, como no caso dos nomes
  placeholder.

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
   - `novo: "<título>"` **ou** `novo a partir de: <fonte> → "<título novo>"` →
     `generate_dashboard` (passando a lista de chart IDs criados nesta rodada)
     **apenas** na primeira leva de charts do dashboard novo. Nos dois casos o
     resultado é um dashboard novo; no caso `novo a partir de:`, o dashboard
     **fonte não é tocado** em nenhuma chamada.
   Nunca use `generate_dashboard` como fallback de
   `add_chart_to_existing_dashboard`.

Se um componente falhar, registre o erro e continue tentando os demais — não pare
a rodada inteira por causa de um componente. Ao final, apresente um resumo com o
resultado de cada componente (sucesso com ID/link, ou erro com a mensagem) e o
link do dashboard final.

## Fora de escopo (v1)

- **Alterar um dashboard existente** — editar charts no lugar, mexer no layout,
  remover chart, mudar título ou filtros nativos do dashboard. É **planejado, mas
  bloqueado**: o MCP não tem uma tool `update_dashboard`, e `update_chart`
  sobrescreve o objeto do chart salvo (que pode ser compartilhado por outros
  dashboards). Reavaliar quando o MCP ganhar `update_dashboard`. A skill **lê**
  dashboards existentes como fonte (Fase 1b) para criar um dashboard **novo**, mas
  nunca escreve num dashboard que não criou.
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
