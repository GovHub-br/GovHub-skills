---
name: dashboard-builder
description: >-
  Planeja um dashboard antes de construí-lo: levanta o perfil de quem vai usar,
  define a hierarquia da informação, produz um esboço estruturado em markdown com
  um wireframe do layout, e exige validação humana explícita antes de qualquer
  criação real. A criação em si fica com a skill conectora da ferramenta escolhida
  (Superset, Power BI ou Metabase). Use sempre que o usuário pedir para "montar um
  dashboard", "planejar um dashboard", "esboçar um dashboard", "criar um painel",
  "construir um dashboard" ou "recriar um dashboard com outra organização".
---

# Dashboard Builder

Esta skill conduz o **raciocínio de design** de um dashboard, do pedido inicial
até um esboço aprovado por um humano. Ela não fala com nenhuma ferramenta de BI:
sempre que precisa de dados reais ou de criar algo de verdade, invoca a **skill
conectora** da ferramenta escolhida.

**Nenhuma criação ou alteração acontece antes da Fase 3 (validação humana) ser
concluída com uma aprovação explícita.** Essa é uma barreira dura: se a resposta
do dev não for uma aprovação clara, não libere a execução — mesmo que pareça
óbvio que ele ia aprovar.

## Fase 0 — Contexto e escolha da ferramenta

Pergunte ao dev (só o que ainda não estiver claro na conversa):

1. **Perfil do usuário final do dashboard** — nível de experiência digital
   (iniciante / intermediário / avançado / especialista) e nível de conhecimento
   de negócio (leigo / técnico / especialista / gestor). Ver
   [`references/diretrizes-dashboard.md`](references/diretrizes-dashboard.md)
   seção "Perfil do usuário" para o que cada combinação implica em densidade e
   volume de informação.
2. **Dispositivo principal** (desktop / tablet / mobile) — dashboard corporativo
   tende a desktop, mas confirme.
3. **Qual pergunta o dashboard precisa responder em 5 segundos** — essa é a
   informação primária, a que recebe maior destaque no wireframe.
4. **Qual ferramenta de BI** — Superset, Power BI ou Metabase. Hoje só o Superset
   tem conector implementado (`dashboard-superset-builder`); para as outras duas,
   avise que o conector ainda não existe e não prossiga.

## Handoff — descoberta no conector

Com a ferramenta escolhida, **invoque a skill conectora correspondente**
(`dashboard-superset-builder` para Superset). Ela faz as perguntas específicas
da ferramenta (qual dataset, dashboard novo ou existente, se parte de um
dashboard fonte) e a descoberta somente leitura que devolve os **nomes reais** de
dataset, colunas e métricas.

Volte para a Fase 2 com esses nomes em mãos. Não monte o esboço com nomes
inventados: se a descoberta não achou algo, o esboço marca o item como pendente
e a Fase 3 não libera a execução.

## Vocabulário compartilhado

Estes literais atravessam a fronteira entre o núcleo e o conector. Escreva-os
exatamente assim dos dois lados — uma variação de grafia quebra o gate em
silêncio.

`dashboard alvo:` aceita exatamente três formas:

- `novo: "<título>"`
- `existente: <slug ou id>`
- `novo a partir de: <slug ou id do fonte> → "<título novo>"`

Marcadores de pendência que o conector escreve e este gate procura:

- `# viz_type a escolher`
- `# config a confirmar`
- `# filtro do fonte a reconstruir`

## Fase 2 — Montar o esboço (markdown + wireframe)

Produza um único arquivo markdown. Antes dos blocos de componente, um cabeçalho do
esboço com uma linha `dashboard alvo:`, com um dos três valores do
[Vocabulário compartilhado](#vocabulário-compartilhado), conforme a resposta da
segunda pergunta da Fase 0-conector:

- `novo: "<título>"`
- `existente: <slug ou id>`
- `novo a partir de: <slug ou id do fonte> → "<título novo>"`

Esse campo passa pelo gate da Fase 3 junto com o resto do esboço e decide a
ramificação da Fase 4. Quando for `novo a partir de:`, o esboço também começa com
o bloco de referência `Estado atual do fonte:` produzido pela Fase 1b (ver Fase 1b
e o parágrafo de re-derivação mais abaixo nesta fase).

**Se o `dashboard alvo:` for `novo a partir de:`** — comece o arquivo com o bloco
`Estado atual do fonte:` produzido pela Fase 1b (layout + filtros nativos do fonte,
como texto), deixando claro que é referência, não ponto de partida. Trate os blocos
de componente que a Fase 1b pré-preencheu como qualquer esboço: escolha o tipo de
visualização, hierarquia (Primária/Secundária/Complementar/Descartável) e posição
**do zero** — os dados (dataset, métricas, dimensões, filtros) vêm do fonte, a
forma não. Qualquer componente ainda marcado `# viz_type a escolher`,
`# config a confirmar` ou `# filtro do fonte a reconstruir` tem que ser resolvido
antes de apresentar o esboço na Fase 3.

Depois do cabeçalho, um bloco `## Componente: <nome>` por chart. Para cada
componente:

- Aplique a hierarquia de informação (Primária / Secundária / Complementar /
  Descartável) e a densidade visual — "média" é o padrão para dashboard corporativo,
  a não ser que o perfil de usuário da Fase 0 sugira outra coisa. Ver
  [`references/diretrizes-dashboard.md`](references/diretrizes-dashboard.md) seções
  "Hierarquia de informação" e "Densidade visual".
- use os nomes de campo que a fase de descoberta do conector devolveu; se faltar
  algum, peça ao conector antes de montar o bloco — não invente nomes de campo.

Formato de cada bloco (os campos **dentro de `config`** são exatamente os que a
descoberta do conector indicou para o tipo de visualização escolhido):

```markdown
## Componente: Consumo Total do Período
- dataset: <o que a descoberta do conector devolveu>
- prioridade: primária
- config:
    <campos da ferramenta escolhida — o conector diz quais são e como se chamam>
```

O envelope (`## Componente:`, `dataset:`, `prioridade:`, `config:`) é o mesmo
para qualquer ferramenta. O conteúdo de `config:` **não é**: cada ferramenta
tem seu próprio vocabulário, e quem fornece os nomes corretos é o conector, na
fase de descoberta. Não invente nomes de campo e não reaproveite os de outra
ferramenta.

Os campos de `config` também mudam conforme o tipo de visualização escolhido — um
gráfico de proporção não pede os mesmos campos que uma tabela. Quem diz quais são
e como se chamam é o conector, na descoberta; não deduza a partir de outra
ferramenta.

Depois do último bloco, gere um **wireframe em ASCII ou Mermaid**, embutido no
mesmo arquivo markdown, mostrando a posição relativa dos componentes num grid de 2
colunas (o conector posiciona em grid de 2 colunas). Exemplo de wireframe ASCII:

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
  libera a Fase 4: volte para o handoff de descoberta no conector e vincule os
  nomes reais primeiro (a Fase 4
  precisa de um `dataset` real e nomes de coluna reais para sequer rodar).
- Se algum componente ainda está marcado `# viz_type a escolher`,
  `# config a confirmar` ou `# filtro do fonte a reconstruir` (vindo da Fase 1b),
  isso **não** libera a Fase 4 — resolva primeiro, como no caso dos nomes
  placeholder.

## Handoff — execução no conector

Só depois de uma aprovação explícita na Fase 3: **invoque de novo a skill
conectora** e peça a execução real do esboço aprovado. É o conector que sabe
traduzir cada bloco `## Componente:` em chamadas concretas da ferramenta.

Ao final, apresente ao dev o resumo que o conector devolveu: o que foi criado,
com links, e o que falhou, com a mensagem de erro.

## Referências

- [`references/diretrizes-dashboard.md`](references/diretrizes-dashboard.md) —
  resumo curado do guia de design (perfil de usuário, hierarquia de informação,
  densidade visual, contexto de uso, cores, tipografia) aplicado a dashboard.
