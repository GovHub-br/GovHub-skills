# Dashboard Superset — Re-derivar de um Dashboard Fonte — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fazer a skill `dashboard-superset-builder` ler um dashboard existente como fonte e produzir um dashboard **novo** a partir dele (Feature A), e registrar "alterar dashboard existente" (Feature B) como planejada/bloqueada.

**Architecture:** Skill de conteúdo — a "implementação" é o texto de `01-govhub/dashboard-superset-builder/SKILL.md`. Nenhum código executável, nenhuma suíte de testes. A integração é a abordagem "Fase 1b + pergunta 5 da Fase 0 em 3 vias" do design: as Fases 2–4 ficam intactas; a Fase 0 ganha uma opção de roteamento e a Fase 1 ganha um ramo (`Fase 1b`) que roda só nessa opção. Os arquivos de referência (`references/superset-schema.md`, `references/diretrizes-dashboard.md`) **não mudam**. Manifestos e README **não mudam** (a skill já está registrada; muda só o conteúdo dela). Verificação de cada tarefa é funcional: `scripts/validar-plugins.sh`, checagens `grep`/YAML, e uma leitura de conformidade da `SKILL.md` contra o design.

**Tech Stack:** Markdown (`SKILL.md`), Bash (`scripts/validar-plugins.sh`), MCP do Superset (tools de leitura `get_dashboard_info` / `get_chart_info`, já existentes no servidor — usadas em tempo de execução da skill, não durante esta implementação).

## Global Constraints

- O dashboard **fonte** é **somente leitura** — nunca alterado. A saída da re-derivação é sempre um dashboard `novo:` criado com `generate_dashboard`. Preserva a regra da v1: a skill não escreve em dashboard que não criou.
- De cada chart do fonte carrega-se **só os dados**: `dataset`, métricas, dimensões, filtros. `viz_type`, títulos, layout e filtros nativos do dashboard são **redecididos do zero** nas Fases 2–3.
- Entram **todos** os charts do fonte no esboço pré-preenchido; o operador remove o que não quer na Fase 3.
- O layout e os filtros nativos do fonte entram no esboço **só como referência textual** (`Estado atual do fonte:`), nunca como ponto de partida.
- Fase 1b é **somente leitura** (tools com tag `discovery`) → **sem gate humano** nessa fase. O gate humano obrigatório da Fase 3 e a barreira "nenhuma mutação antes da Fase 3" continuam valendo sem exceção.
- Casos de borda da Fase 1b (viz_type exótico, `get_chart_info` falha, filtro adhoc/SQL) → **registrar no esboço e seguir**, nunca abortar a fase.
- Componente marcado na Fase 1b (`# viz_type a escolher`, `# config a confirmar`, `# filtro do fonte a reconstruir`) **não libera a Fase 4** — resolver antes, como no caso dos nomes placeholder.
- Feature B ("alterar dashboard existente") é **só documentação** nesta rodada: planejada, bloqueada pela falta de `update_dashboard` no MCP. Não implementar nada de escrita em dashboard existente além do `add_chart_to_existing_dashboard` que já existe.
- `create_virtual_dataset` continua fora de escopo.
- Nenhum arquivo do repositório ganha endereço ou token de servidor MCP.

Spec completa: [`docs/superpowers/specs/2026-09-04-dashboard-superset-rederive-from-source-design.md`](../specs/2026-09-04-dashboard-superset-rederive-from-source-design.md).

---

## File Structure

```
01-govhub/dashboard-superset-builder/SKILL.md    # ÚNICO arquivo modificado
docs/superpowers/plans/2026-09-04-...             # este plano (já existe ao executar)
```

Toda a implementação é edição de `01-govhub/dashboard-superset-builder/SKILL.md`.
As duas tarefas de conteúdo editam esse mesmo arquivo em regiões diferentes:

- **Tarefa 1** — frontmatter `description:`, Fase 0 (pergunta 5), Fase 2 (linha do cabeçalho `dashboard alvo:`), Fase 4 (item 2 da ramificação), seção "Fora de escopo".
- **Tarefa 2** — nova seção `## Fase 1b` (inserida entre Fase 1 e Fase 2), parágrafo novo no corpo da Fase 2, bullet novo na Fase 3.
- **Tarefa 3** — verificação manual ponta a ponta (não edita arquivo).

Regiões disjuntas de propósito: um revisor pode rejeitar o roteamento (Tarefa 1) aprovando o corpo do fluxo (Tarefa 2), e vice-versa.

---

### Task 1: Roteamento e escopo (Fase 0, cabeçalho do esboço, ramificação da Fase 4, "Fora de escopo")

**Files:**
- Modify: `01-govhub/dashboard-superset-builder/SKILL.md` (frontmatter; Fase 0 pergunta 5; Fase 2 parágrafo do `dashboard alvo:`; Fase 4 item 2; seção "Fora de escopo (v1)")

**Interfaces:**
- Consumes: nada de outras tarefas.
- Produces: o vocabulário de roteamento que a Tarefa 2 referencia — os literais exatos `novo do zero`, `acrescentar a existente: <id/uuid/título>`, `novo a partir do fonte: <id/uuid/título>` (pergunta 5); o valor de cabeçalho `novo a partir de: <id/uuid/título do fonte> → "<título novo>"` (linha `dashboard alvo:`); a referência textual `Estado atual do fonte:` (mencionada aqui como forward-reference, definida na Tarefa 2 / Fase 1b).

- [ ] **Step 1: Ler o arquivo atual inteiro**

Run: `cat /home/joaoegewarth/GovHub-skills/01-govhub/dashboard-superset-builder/SKILL.md`
Objetivo: confirmar os textos-âncora exatos citados nos steps abaixo antes de editar (o arquivo pode ter mudado desde a escrita do plano).

- [ ] **Step 2: Editar o `description:` do frontmatter — acrescentar gatilhos de re-derivação**

Localize, no bloco `description: >-`, a linha que termina a lista de gatilhos:

```
  "adicionar um chart a um dashboard existente do Superset" ou
  "construir um dashboard".
```

Substitua por:

```
  "adicionar um chart a um dashboard existente do Superset",
  "construir um dashboard", "recriar / reconstruir um dashboard", "um dashboard
  novo baseado em outro" ou "o mesmo dashboard com outra organização / outros
  gráficos".
```

- [ ] **Step 3: Reescrever a pergunta 5 da Fase 0 (2 vias → 3 vias) e adicionar a oferta proativa**

Localize o item atual da pergunta 5 na "## Fase 0" (bloco que começa com `5. **Dashboard novo ou já existente?`). Substitua o item inteiro por:

```markdown
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
```

- [ ] **Step 4: Ampliar a linha `dashboard alvo:` no início da Fase 2**

Localize, na "## Fase 2", o parágrafo que descreve o cabeçalho do esboço (começa com `Produza um único arquivo markdown. Antes dos blocos de componente, um cabeçalho`). Substitua esse parágrafo por:

```markdown
Produza um único arquivo markdown. Antes dos blocos de componente, um cabeçalho do
esboço com uma linha `dashboard alvo:`, conforme a resposta da pergunta 5 da Fase 0:

- `novo: "<título>"`
- `existente: <id/uuid/título>`
- `novo a partir de: <id/uuid/título do fonte> → "<título novo>"`

Esse campo passa pelo gate da Fase 3 junto com o resto do esboço e decide a
ramificação da Fase 4. Quando for `novo a partir de:`, o esboço também começa com
o bloco de referência `Estado atual do fonte:` produzido pela Fase 1b (ver Fase 1b
e o parágrafo de re-derivação mais abaixo nesta fase).
```

- [ ] **Step 5: Adicionar a variante `novo a partir de:` na ramificação da Fase 4**

Localize, na "## Fase 4", o item `2.` (`Ramifique pelo campo `dashboard alvo:``). Substitua o item `2.` inteiro por:

```markdown
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
```

- [ ] **Step 6: Reescrever a seção "Fora de escopo (v1)"**

Localize a seção `## Fora de escopo (v1)` e substitua seus bullets por:

```markdown
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
```

- [ ] **Step 7: Verificar frontmatter YAML válido e `name` intacto**

Run:
```bash
python3 - <<'PY'
import pathlib, re
p = pathlib.Path("/home/joaoegewarth/GovHub-skills/01-govhub/dashboard-superset-builder/SKILL.md")
t = p.read_text(encoding="utf-8")
m = re.match(r'^---\n(.*?)\n---\n', t, re.S)
assert m, "frontmatter não encontrado"
fm = m.group(1)
assert re.search(r'^name:\s*dashboard-superset-builder\s*$', fm, re.M), "name mudou ou sumiu"
import yaml  # PyYAML pode não estar instalado; se ImportError, cair no teste manual abaixo
yaml.safe_load(fm)
print("OK: frontmatter YAML válido, name = dashboard-superset-builder")
PY
```
Expected: `OK: frontmatter YAML válido, name = dashboard-superset-builder`
Se `yaml` não estiver instalado (ImportError): confirme manualmente que o bloco entre os `---` continua sendo `key: value` por linha, sem tabs, e que `name: dashboard-superset-builder` está lá.

- [ ] **Step 8: Verificar os literais de roteamento e a seção reescrita**

Run:
```bash
cd /home/joaoegewarth/GovHub-skills
grep -n 'novo a partir do fonte:\|novo a partir de:\|Oferta proativa:\|update_dashboard' \
  01-govhub/dashboard-superset-builder/SKILL.md
```
Expected: aparecem — `novo a partir do fonte:` (Fase 0), `novo a partir de:` (Fase 2 e Fase 4), `Oferta proativa:` (Fase 0), `update_dashboard` (Fora de escopo). Pelo menos 1 ocorrência de cada.

- [ ] **Step 9: Rodar o validador de plugins**

Run: `cd /home/joaoegewarth/GovHub-skills && bash scripts/validar-plugins.sh`
Expected: termina sem erro (exit 0); a linha de coerência mostra `govhub-core 4` (contagem inalterada).

- [ ] **Step 10: Leitura de conformidade contra o design**

Abra `docs/superpowers/specs/2026-09-04-dashboard-superset-rederive-from-source-design.md` seções "Fase 0 — pergunta 5 vira 3 vias", "Seção 'Fora de escopo (v1)' — reescrever" e confira, lendo a `SKILL.md` editada:
- a pergunta 5 tem exatamente as 3 respostas com o mapeamento de Fase 4 e Fase 1 da tabela do design;
- a oferta proativa está presente e diz "não edita o original";
- "Fora de escopo" descreve a Feature B como planejada/bloqueada por `update_dashboard` e diz que a skill lê fonte mas não escreve em dashboard que não criou.
Anote qualquer divergência antes de commitar.

- [ ] **Step 11: Commit**

```bash
cd /home/joaoegewarth/GovHub-skills
git add 01-govhub/dashboard-superset-builder/SKILL.md
git commit -m "feat(dashboard-superset-builder): rotear re-derivação de dashboard fonte

Fase 0 pergunta 5 vira 3 vias (novo do zero / acrescentar a existente /
novo a partir do fonte); cabeçalho do esboço e ramificação da Fase 4 ganham
a variante 'novo a partir de:'; 'Fora de escopo' registra a Feature B
(alterar dashboard existente) como planejada e bloqueada pela falta de
update_dashboard no MCP.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 2: Fase 1b (ler o dashboard fonte) e ajustes nas Fases 2–3

**Files:**
- Modify: `01-govhub/dashboard-superset-builder/SKILL.md` (nova seção `## Fase 1b` entre `## Fase 1` e `## Fase 2`; parágrafo novo no corpo da `## Fase 2`; bullet novo na `## Fase 3`)

**Interfaces:**
- Consumes: da Tarefa 1 — o literal da pergunta 5 `novo a partir do fonte: <id/uuid/título>` e o valor de cabeçalho `novo a partir de: <...> → "<...>"` (a Fase 1b só roda quando a pergunta 5 tem esse valor; o parágrafo da Fase 2 referencia `Estado atual do fonte:` que a Fase 1b define).
- Produces: nada para tarefas posteriores (Tarefa 3 é verificação manual).

- [ ] **Step 1: Ler o arquivo atual inteiro (pós-Tarefa 1)**

Run: `cat /home/joaoegewarth/GovHub-skills/01-govhub/dashboard-superset-builder/SKILL.md`
Objetivo: confirmar as âncoras (`## Fase 1`, o parágrafo final dela, `## Fase 2`, `## Fase 3`) e o texto exato que a Tarefa 1 deixou.

- [ ] **Step 2: Inserir a seção `## Fase 1b` entre a Fase 1 e a Fase 2**

Localize o fim da `## Fase 1` — o parágrafo `Essas chamadas são somente leitura — não têm a tag `mutate` — então não precisam de aprovação humana.` — e a linha `## Fase 2 — Montar o esboço (markdown + wireframe)` logo depois. Insira, **entre** esse parágrafo e o `## Fase 2`, o bloco:

```markdown

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
```

- [ ] **Step 3: Adicionar o parágrafo de re-derivação no corpo da Fase 2**

Na `## Fase 2`, logo **depois** do parágrafo do cabeçalho `dashboard alvo:` (que a Tarefa 1 reescreveu, termina com "... ver Fase 1b e o parágrafo de re-derivação mais abaixo nesta fase.") e **antes** do parágrafo `Depois do cabeçalho, um bloco `## Componente: <nome>` por chart.`, insira:

```markdown
**Se o `dashboard alvo:` for `novo a partir de:`** — comece o arquivo com o bloco
`Estado atual do fonte:` produzido pela Fase 1b (layout + filtros nativos do fonte,
como texto), deixando claro que é referência, não ponto de partida. Trate os blocos
de componente que a Fase 1b pré-preencheu como qualquer esboço: escolha `viz_type`,
hierarquia (Primária/Secundária/Complementar/Descartável) e posição **do zero** —
os dados (dataset, métricas, dimensões, filtros) vêm do fonte, a forma não. Qualquer
componente ainda marcado `# viz_type a escolher`, `# config a confirmar` ou
`# filtro do fonte a reconstruir` tem que ser resolvido antes de apresentar o
esboço na Fase 3.
```

- [ ] **Step 4: Adicionar o bullet de marcadores não resolvidos na Fase 3**

Na `## Fase 3`, localize o bullet que trata de nomes placeholder (começa com `- Se o esboço ainda contém nomes placeholder de dataset ou de coluna`). Logo **depois** dele, adicione o bullet:

```markdown
- Se algum componente ainda está marcado `# viz_type a escolher`,
  `# config a confirmar` ou `# filtro do fonte a reconstruir` (vindo da Fase 1b),
  isso **não** libera a Fase 4 — resolva primeiro, como no caso dos nomes
  placeholder.
```

- [ ] **Step 5: Verificar a nova seção e as âncoras de fase**

Run:
```bash
cd /home/joaoegewarth/GovHub-skills
grep -n '^## Fase' 01-govhub/dashboard-superset-builder/SKILL.md
```
Expected (nesta ordem): `## Fase 0`, `## Fase 1 —`, `## Fase 1b —`, `## Fase 2 —`, `## Fase 3 —`, `## Fase 4 —`.

Run:
```bash
grep -n 'get_dashboard_info\|get_chart_info\|Estado atual do fonte:\|viz_type a escolher\|filtro do fonte a reconstruir' \
  01-govhub/dashboard-superset-builder/SKILL.md
```
Expected: `get_dashboard_info` e `get_chart_info` aparecem na Fase 1b; `Estado atual do fonte:` aparece na Fase 1b, na Fase 2 (parágrafo do cabeçalho, da Tarefa 1) e no parágrafo de re-derivação; `viz_type a escolher` e `filtro do fonte a reconstruir` aparecem na Fase 1b, na Fase 2 e na Fase 3.

- [ ] **Step 6: Confirmar que a barreira de mutação continua intacta**

Run:
```bash
grep -n 'antes da Fase 3\|não têm a tag `mutate`\|somente leitura' \
  01-govhub/dashboard-superset-builder/SKILL.md
```
Expected: o parágrafo introdutório ("Nenhuma chamada que cria ou altera algo no Superset acontece antes da Fase 3 ...") continua presente e inalterado; a Fase 1b afirma explicitamente ser somente leitura e sem aprovação humana. A Fase 1b **não** chama nenhuma tool com tag `mutate`.

- [ ] **Step 7: Rodar o validador de plugins**

Run: `cd /home/joaoegewarth/GovHub-skills && bash scripts/validar-plugins.sh`
Expected: exit 0; `govhub-core 4` inalterado.

- [ ] **Step 8: Leitura de conformidade contra o design**

Abra `docs/superpowers/specs/2026-09-04-dashboard-superset-rederive-from-source-design.md` seções "Fase 1b — ler o dashboard fonte (novo)", "Fase 2" e "Fase 3" e confira contra a `SKILL.md`:
- Fase 1b: os 4 passos, os 4 casos de borda com os marcadores exatos, a nota sobre `dataset` recuperado ser real, o "somente leitura / sem gate";
- Fase 2: o parágrafo de re-derivação diz "dados vêm do fonte, a forma não" e exige resolver marcadores antes da Fase 3;
- Fase 3: o bullet novo cita os três marcadores e equipara ao caso dos nomes placeholder.
Anote qualquer divergência antes de commitar.

- [ ] **Step 9: Commit**

```bash
cd /home/joaoegewarth/GovHub-skills
git add 01-govhub/dashboard-superset-builder/SKILL.md
git commit -m "feat(dashboard-superset-builder): Fase 1b — ler dashboard fonte e re-derivar

Nova Fase 1b (somente leitura) lê o dashboard fonte via get_dashboard_info +
get_chart_info por chart, monta blocos de componente só com os dados
(dataset/métricas/dimensões/filtros) e captura o layout do fonte como
referência textual. Fase 2 redecide viz_type/hierarquia/posição do zero;
Fase 3 não libera a Fase 4 com marcadores da Fase 1b pendentes.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 3: Verificação manual ponta a ponta

Esta tarefa **não produz arquivo** — é a checagem funcional final da seção "Verificação" da spec. **Não pode ser delegada a um subagente isolado:** precisa de um servidor MCP do Superset conectado, de um **dashboard fonte real** no ambiente do usuário, e da participação do usuário no gate da Fase 3.

**Files:** nenhum.

- [ ] **Step 1: Preparar**

Com a skill carregada (plugin instalado ou pasta em `~/.claude/skills/dashboard-superset-builder/`) e um servidor MCP do Superset conectado, escolha um **dashboard existente real** com pelo menos 2 charts (idealmente incluindo um chart de um `viz_type` fora dos 7 do cache, para exercitar o caso de borda). Anote o ID/UUID e o estado atual (título, charts, layout) — para comparar depois.

- [ ] **Step 2: Rodar a skill em modo re-derivação**

Peça: "cria um dashboard novo a partir do dashboard `<id/uuid>`, com outra organização". Acompanhe: a Fase 0 deve rotear a pergunta 5 para `novo a partir do fonte` (ou a oferta proativa deve aparecer se você descrever a intenção como "melhorar/reorganizar").

- [ ] **Step 3: Conferir a Fase 1b**

No esboço gerado, confirme:
- há um bloco `Estado atual do fonte:` no topo, com o layout do fonte, marcado como referência;
- há um bloco `## Componente:` por chart do fonte, com `dataset:` real e `config` só com dados (sem `viz_type`, sem título herdado);
- charts com `viz_type` exótico ou filtro adhoc estão marcados (`# viz_type a escolher` / `# filtro do fonte a reconstruir`);
- se algum `get_chart_info` falhou, as falhas estão listadas.

- [ ] **Step 4: Confirmar que os marcadores barram a Fase 3**

Se o esboço tem componentes marcados, tente aprovar assim mesmo. Expected: a skill **não** avança para a Fase 4 — pede para resolver os marcadores primeiro.

- [ ] **Step 5: Confirmar que resposta vaga não libera a Fase 4**

Resolvidos os marcadores, responda de forma vaga ("ok", "bacana") ao pedido de aprovação. Expected: a skill pede confirmação explícita (regra herdada da v1).

- [ ] **Step 6: Aprovar e conferir a criação**

Aprove explicitamente. Expected: a skill chama `generate_chart` (`save_chart=True`) por componente e depois `generate_dashboard` com os IDs criados; ao final apresenta os links.

- [ ] **Step 7: Confirmar no Superset que o fonte ficou intocado**

Abra o dashboard **fonte** no Superset e compare com o estado anotado no Step 1: título, lista de charts e layout **idênticos**. Nenhuma chamada de escrita deve ter tocado nele.

- [ ] **Step 8: Confirmar o dashboard novo**

Abra o dashboard **novo**: os dados de cada chart (dataset, métricas, dimensões, filtros) batem com os do fonte; `viz_type` e layout são os redecididos nas Fases 2–3, não os do fonte.

- [ ] **Step 9: Registrar o resultado**

Se tudo passou, nenhum commit adicional é necessário — spec e plano já estão commitados. Se algo falhou, volte à Tarefa 1 ou 2, corrija, e repita esta Tarefa 3.

---

## Self-Review (feito na escrita do plano)

**1. Cobertura da spec:**
- "Frontmatter `description:`" → Tarefa 1 Step 2. ✅
- "Fase 0 — pergunta 5 vira 3 vias" (tabela de roteamento + oferta proativa) → Tarefa 1 Steps 3. ✅
- "cabeçalho do esboço ... variante `novo a partir de:`" → Tarefa 1 Step 4. ✅
- "Fase 1b — ler o dashboard fonte" (4 passos + 4 casos de borda + nota do dataset real) → Tarefa 2 Step 2. ✅
- "Fase 2" (bloco `Estado atual do fonte`, redecidir forma, resolver marcadores) → Tarefa 2 Step 3. ✅
- "Fase 3" (bullet de marcadores não resolvidos) → Tarefa 2 Step 4. ✅
- "Fase 4" (`novo a partir de:` → `generate_dashboard`, fonte intocado) → Tarefa 1 Step 5. ✅
- "Seção 'Fora de escopo' — reescrever" (Feature B planejada/bloqueada) → Tarefa 1 Step 6. ✅
- "Arquivos de referência não mudam" → File Structure + nenhuma tarefa toca `references/`. ✅
- "Impacto em manifestos: nenhum" → Tarefa 1 Step 9 / Tarefa 2 Step 7 confirmam `govhub-core 4` inalterado; nenhuma tarefa edita manifesto/README. ✅
- "Verificação (ponta a ponta)" (6 itens) → Tarefa 3 Steps 3–8. ✅

**2. Placeholders:** nenhum "TBD/TODO"; todo texto a inserir está literal nos steps; comandos com expected. ✅

**3. Consistência de tipos/literais:** os literais de roteamento (`novo do zero`, `acrescentar a existente:`, `novo a partir do fonte:`, `novo a partir de:`, `Estado atual do fonte:`, `# viz_type a escolher`, `# config a confirmar`, `# filtro do fonte a reconstruir`) aparecem idênticos entre Tarefa 1 (produz) e Tarefa 2 (consome) e nas checagens `grep`. ✅
