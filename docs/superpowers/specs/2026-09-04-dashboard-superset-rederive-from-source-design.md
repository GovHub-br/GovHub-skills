# Design — `dashboard-superset-builder`: re-derivar de um dashboard fonte

Data: 2026-09-04
Skill afetada: `01-govhub/dashboard-superset-builder/`
Depende de: skill já existente (design de 2026-09-03), `references/superset-schema.md`,
`references/diretrizes-dashboard.md`.

## Problema

A skill `dashboard-superset-builder` só monta dashboards a partir de um pedido
"do zero" ou acrescentando charts a um dashboard existente. Não sabe **partir de um
dashboard que já existe** para produzir um **novo** com as mesmas informações, mas
outra organização e outros tipos de gráfico. E não sabe **alterar** um dashboard
existente.

## Escopo

### Feature A — re-derivar de um dashboard fonte (implementar agora)

A skill passa a ler um dashboard existente como **fonte** e produzir um dashboard
**novo** a partir dele.

Regras:

- Entram **todos** os charts do fonte. O operador remove o que não quiser na Fase 3,
  como em qualquer esboço.
- De cada chart do fonte carrega-se **só os dados**: `dataset`, métricas,
  dimensões, filtros. `viz_type`, títulos, layout e filtros nativos do dashboard
  são **redecididos do zero** nas Fases 2–3.
- O layout do fonte e os filtros nativos entram no esboço apenas como **referência
  textual** ("Estado atual do fonte: …"), nunca como ponto de partida.
- O dashboard fonte é **somente leitura** — nunca é alterado. A saída é sempre um
  dashboard `novo:`. Isso preserva a regra da v1: a skill não edita dashboards que
  não criou.

### Feature B — alterar um dashboard existente (só documentar)

"Alterar um dashboard existente" (editar charts no lugar via `update_chart`, mexer
no layout, remover chart, mudar título/filtros do dashboard) fica registrada como
**planejada, bloqueada pelo MCP**: não existe uma tool `update_dashboard`. O que o
MCP oferece hoje (`update_chart` + `add_chart_to_existing_dashboard`) não cobre
layout nem remoção, e `update_chart` sobrescreve o objeto do chart salvo — que pode
ser compartilhado por outros dashboards. Quando o MCP ganhar `update_dashboard`,
a Feature B é reavaliada num novo ciclo.

### Fora de escopo (permanece)

- `create_virtual_dataset` (criar dataset virtual via SQL).
- Editar/atualizar qualquer dashboard existente (ver Feature B).

## Abordagem escolhida

**Sub-ramo "Fase 1b" + pergunta 5 da Fase 0 em 3 vias.** Menor superfície nova:
as Fases 2–4 ficam intactas; só a Fase 0 ganha uma opção na pergunta 5 e a Fase 1
ganha um ramo rotulado que roda quando essa opção é escolhida. A lista de
componentes que a Fase 1b produz entra na Fase 2 exatamente como um esboço montado
à mão.

Abordagens descartadas: seção separada "Modo re-derivação" (duplica orientação das
Fases 1–4, tende a divergir); dashboard fonte como input implícito da Fase 1 sem
pergunta nova (não-determinístico, enfraquece o gate "estou re-derivando ou
acrescentando?").

## Mudanças na `SKILL.md`

### Frontmatter `description:`

Acrescentar gatilhos: "recriar dashboard", "reconstruir dashboard", "novo dashboard
baseado em outro", "dashboard existente com outra organização / outros gráficos".

### Fase 0 — pergunta 5 vira 3 vias

Hoje: "Dashboard novo ou já existente?". Passa a ser:

| Resposta | Fase 4 faz | Fase 1 faz |
|---|---|---|
| `novo do zero` | `generate_dashboard` | descoberta de dataset normal |
| `acrescentar a existente: <id/uuid/título>` | `add_chart_to_existing_dashboard` | descoberta de dataset normal |
| `novo a partir do fonte: <id/uuid/título>` | `generate_dashboard` | **Fase 1b** (lê o fonte) |

O cabeçalho do esboço na Fase 2 (`dashboard alvo:`) ganha a variante
`novo a partir de: <ref do fonte> → "<título novo>"`.

**Oferta proativa:** se o operador mencionar um dashboard existente com intenção de
"melhorar / reorganizar / mudar a cara", a skill responde que não edita o original,
mas pode criar um novo a partir dele; se aceito, marca a pergunta 5 como
`novo a partir do fonte`.

### Fase 1b — ler o dashboard fonte (novo)

Roda só quando a pergunta 5 é `novo a partir do fonte`. Tudo somente leitura (tools
com tag `discovery`) → **sem gate humano** nesta fase.

Passos:

1. `get_dashboard_info(<ref do fonte>)` → título, lista de charts (com IDs), layout.
2. Para cada chart: `get_chart_info(<chart_id>)` → recuperar `dataset`, `viz_type`
   original, métricas, dimensões/`groupby`, filtros (do `form_data`/params).
3. Montar a lista de componentes pré-preenchida para a Fase 2: um bloco por chart,
   com **só** os campos de dados — `dataset:` mais o miolo de `config` que mapeia
   limpo (métricas, dimensões, `filters` estruturados). **Sem** `viz_type`, sem
   título, sem posição.
4. Capturar o **layout original** e os **filtros nativos do dashboard** como bloco
   de **referência textual** no topo do esboço ("Estado atual do fonte: …"),
   marcado explicitamente como referência, não ponto de partida.

Casos de borda (todos: registrar no esboço, nunca abortar a fase):

- Chart com `viz_type` fora dos 7 conhecidos, ou `form_data` que não mapeia limpo →
  traz o que der (dataset, métricas, filtros) e marca o bloco como
  **"viz_type a escolher / config a confirmar na Fase 3"**.
- `get_chart_info` falha (permissão, chart órfão, dataset removido) → pula o chart,
  segue nos outros, **lista as falhas** ao fim da Fase 1b.
- Vários charts no mesmo dataset → normal, sem tratamento especial.
- Filtro do chart que é expressão SQL/adhoc → não inventar equivalente estruturado;
  marcar como **"filtro do fonte a reconstruir"**.

Saída: o esboço pré-preenchido entra na Fase 2 como qualquer esboço.

Nota: o `dataset` recuperado via `get_chart_info` já é uma referência real (vem de
um chart vivo), então o gate de "nomes placeholder" da Fase 3 não se aplica a
componentes re-derivados — a não ser que o dataset tenha sido removido, caso já
coberto pelo caso de borda de `get_chart_info` falhar.

### Fase 2

Ganha só o bloco de referência "Estado atual do fonte" no topo (layout + filtros
nativos do fonte, como texto). Blocos de componente pré-preenchidos são tratados
como qualquer esboço. Componente marcado "viz_type a escolher" tem que ser resolvido
antes da Fase 3.

### Fase 3

Gate não muda. Reforço de uma linha: componentes ainda marcados "viz_type a
escolher / config a confirmar / filtro a reconstruir" **não** liberam a Fase 4 —
resolver primeiro, igual ao tratamento de nomes placeholder.

### Fase 4

Não muda. `novo a partir do fonte` cai na ramificação `generate_dashboard`. O fonte
nunca é tocado.

### Seção "Fora de escopo (v1)" — reescrever

- Trocar *"Editar ou atualizar dashboards que não foram criados por esta skill"*
  por: a skill **lê** dashboards existentes como fonte para criar um novo, mas
  **não altera** dashboard que não criou. *Alterar dashboard existente* (editar
  charts no lugar, mexer no layout, remover chart) é **planejado, bloqueado**:
  falta `update_dashboard` no MCP.
- `create_virtual_dataset` continua fora.

## Arquivos de referência

`references/superset-schema.md` e `references/diretrizes-dashboard.md` **não mudam**.
Só `SKILL.md` (Fase 0, Fase 1b nova, ajustes pontuais nas Fases 2–3, "Fora de
escopo") e o `description:` do frontmatter.

## Verificação (tarefa de teste, ponta a ponta)

Com um dashboard fonte real:

1. Fase 1b recupera `dataset`, métricas e filtros dos charts do fonte.
2. O esboço mostra o layout do fonte **só como referência**, não como ponto de
   partida.
3. Chart com `viz_type` exótico é marcado e **barra a Fase 3** até ser resolvido.
4. O dashboard fonte fica **intocado** depois da Fase 4 (conferir no Superset).
5. O dashboard novo nasce com os dados certos (dataset, métricas, dimensões,
   filtros por chart).
6. Gate da Fase 3: resposta vaga não libera a Fase 4 (regra herdada, revalidar).

## Impacto em manifestos

Nenhum — a skill já está registrada; muda só o conteúdo de `SKILL.md`. Sem mudança
de contagem no README/manifestos.
