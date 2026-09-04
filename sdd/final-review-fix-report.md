# Final-review fix report — dashboard-superset-builder

Branch: `worktree-dashboard-superset-builder`
Commit: `806950da5f332136576e2c5020bb61a74faf9d2a`
Data: 2026-09-03

Uma passada única de correções sobre o branch, conforme
`sdd/final-review-fixes.md`. Todas as seções **Critical**, **Important** e **Minor**
foram aplicadas; nada da seção "NOT in this pass" (Minor 7 / frontmatter) foi
tocado.

## O que foi alterado (6 arquivos, 1 commit)

| Item | Arquivo | Mudança |
|------|---------|---------|
| Critical 1 | `01-govhub/dashboard-superset-builder/SKILL.md` (Fase 2) | Bloco de exemplo reescrito com os campos reais do schema `xy` (`chart_type`, `kind`, `x`, `y`, `filters`); `dataset` rotulado como parâmetro do `generate_chart`, não campo de `config`; caveat troca `adhoc_filters`/SQL cru por filtros estruturados. |
| Critical 1 (parte 2) | `docs/superpowers/plans/2026-09-03-dashboard-superset-builder.md` (Task 6 Step 2) | Passo reescrito: confere o bloco `config:` de cada componente contra `references/superset-schema.md` pelo `viz_type` (`xy` → `x`/`y`/`kind`/`filters`; nunca `metrics`/`groupby`/`adhoc_filters`); `filters` estruturado `{column, op, value}`; `dataset`/título/`save_chart` são wrapper. |
| Important 2 | `SKILL.md` (Fase 4) | Novo **Passo 0**: descobrir a assinatura wrapper de `generate_chart` / `add_chart_to_existing_dashboard` / `generate_dashboard` via `search_tools` + `inputSchema` antes da 1ª chamada. Item 1 reescrito deixando claro que `config:` vai no `request` e `dataset`/título/`save_chart` são wrapper. |
| Important 3 | `SKILL.md` (Fase 0, Fase 2, Fase 4) | Fase 0 ganha pergunta 5 (dashboard novo x existente); Fase 2 ganha linha `dashboard alvo:` no cabeçalho do esboço; Fase 4 item 2 ramifica explicitamente nesse campo. Frase "nunca use `generate_dashboard` como fallback" mantida. |
| Important 4 | `SKILL.md` (Fase 1, Fase 3) | Fase 1: `list_datasets` (somente leitura) para o dev escolher quando não sabe o dataset; placeholder só como último recurso. Fase 3: aprovação do design com nomes placeholder **não** libera a Fase 4 — volta para a Fase 1 vincular nomes reais. |
| Important 5 | `references/diretrizes-dashboard.md` | Não aponta mais para "arquivo original na raiz do repositório"; descreve o guia como documento interno de trabalho do time, não distribuído com a skill. Caveat de cobertura reescrito como "no guia interno usado como fonte". |
| Minor 6 | `NOTICE.md` | "Das 51 skills que restam" → "Das 52 skills que restam". Figura "43 sem procedência" mantida. |
| Minor 8 | `SKILL.md` (wireframe ASCII) | Redesenhado: as três réguas horizontais têm largura 59 e os `│` alinham nas colunas 0 / 29 / 58. Grid 2 colunas + linha full-width abaixo. |
| Minor 10 | `references/superset-schema.md` (header) | "cada bloco abaixo é o retorno bruto de `get_chart_type_schema(...)`" → "o objeto `schema` retornado por `get_chart_type_schema(...)` (mais o(s) `examples`)", esclarecendo que não é o `{chart_type, schema, examples}` completo. |
| Minor 11 | `.gitignore` | Adicionada a linha `handoff-skill-mcp.md` (contém o endereço MCP `10.0.0.32:30508`). `markdowm-devs.md` deixado de fora, como instruído. |

Propriedades de segurança preservadas (não alteradas): gate duro da Fase 3,
"Nenhuma chamada que cria ou altera algo no Superset acontece antes da Fase 3",
"nunca use `generate_dashboard` como fallback de `add_chart_to_existing_dashboard`",
o bloco "Nunca assuma o endereço de um servidor MCP do Superset", e a seção
"Fora de escopo (v1)".

---

## Verificação (os 6 itens do fixes file)

### 1. `bash scripts/validar-plugins.sh; echo exit=$?` → 0

```
==> Coerência entre manifestos e pastas de skill
  govhub-skills       52 skills  <- ./
  govhub-core          4 skills  <- ./01-govhub
  govhub-dados         9 skills  <- ./02-dados-e-bancos
  govhub-backend       6 skills  <- ./03-backend-apis
  govhub-infra         8 skills  <- ./04-infra-devops
  govhub-qualidade    18 skills  <- ./05-qualidade-testes
  govhub-docs          7 skills  <- ./06-docs-relatorios

  ok — manifestos e pastas batem.

==> Validação oficial da CLI do Claude Code
Validating marketplace manifest: .../.claude-plugin/marketplace.json
✔ Validation passed
Validating plugin manifest: .../01-govhub/.claude-plugin/plugin.json
✔ Validation passed
Validating plugin manifest: .../02-dados-e-bancos/.claude-plugin/plugin.json
✔ Validation passed
Validating plugin manifest: .../03-backend-apis/.claude-plugin/plugin.json
✔ Validation passed
Validating plugin manifest: .../04-infra-devops/.claude-plugin/plugin.json
✔ Validation passed
Validating plugin manifest: .../05-qualidade-testes/.claude-plugin/plugin.json
✔ Validation passed
Validating plugin manifest: .../06-docs-relatorios/.claude-plugin/plugin.json
✔ Validation passed

exit=0
```

**PASS.**

### 2. `grep -nE 'adhoc_filters|groupby|\bmetrics:' 01-govhub/dashboard-superset-builder/SKILL.md`

```
119:`table` usa `columns`; `big_number` usa `metric`). Nunca use `adhoc_filters` nem
```

Único hit é a frase que proíbe `adhoc_filters`. Nenhum hit apresentando
`adhoc_filters` / `groupby` / `metrics:` como nome de campo real. **PASS.**

### 3. `git grep -n '10.0.0.32\|Bearer\|eyJ' -- ':!sdd/'` → sem NOVOS hits em arquivos versionados

Nenhum dos 6 arquivos do commit aparece no resultado. Hits pré-existentes (não
tocados nesta passada), todos placeholders/documentação em skills não relacionadas:

```
01-govhub/govhub-pipeline-guide/SKILL.md:93                       headers = {"Authorization": f"Bearer {self.token}"}
03-backend-apis/api-design-principles/assets/api-design-checklist.md:65
03-backend-apis/api-design-principles/references/rest-best-practices.md:127,132,237,240
03-backend-apis/api-documentation-generator/SKILL.md:100,148,162,183,273,290,301
03-backend-apis/api-integration-specialist/SKILL.md:58,218
03-backend-apis/api-security-best-practices/SKILL.md:187
05-qualidade-testes/k6-load-testing/SKILL.md:153,183,577
05-qualidade-testes/security-best-practices/references/javascript-express-web-server-security.md:379
05-qualidade-testes/security-best-practices/references/python-fastapi-web-server-security.md:235,969
05-qualidade-testes/security-compliance/reference/application-security.md:760,761
05-qualidade-testes/security-compliance/reference/security-operations.md:365
docs/superpowers/specs/2026-09-03-dashboard-superset-builder-design.md:172  "O token Superset (Bearer JWT) não entra em nenhum arquivo da skill..."
```

Nenhuma ocorrência literal de `10.0.0.32` em arquivo versionado (só no
`handoff-skill-mcp.md` não-versionado, agora coberto pelo `.gitignore`). **PASS.**

### 4. `grep -n 'handoff-skill-mcp.md' .gitignore`

```
4:handoff-skill-mcp.md
```

**PASS.**

### 5. `git diff --stat` (commit `806950d`)

```
 .gitignore                                         |  1 +
 01-govhub/dashboard-superset-builder/SKILL.md      | 93 +++++++++++++++-------
 .../references/diretrizes-dashboard.md             | 14 ++--
 .../references/superset-schema.md                  |  2 +-
 NOTICE.md                                          |  2 +-
 .../plans/2026-09-03-dashboard-superset-builder.md | 11 ++-
 6 files changed, 82 insertions(+), 41 deletions(-)
```

Exatamente os 6 arquivos previstos, nada além. `sdd/final-review-fixes.md`
(o próprio arquivo de tarefas) e este relatório ficam fora do commit — não
foram versionados. **PASS.**

### 6. Trechos novos (para conferência sem re-diff)

#### Nova lista de perguntas da Fase 0

```markdown
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
```

#### Novo bloco de exemplo da Fase 2

````markdown
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
````

Cabeçalho do esboço (antes dos blocos de componente):

```markdown
Produza um único arquivo markdown. Antes dos blocos de componente, um cabeçalho do
esboço com uma linha `dashboard alvo:` — `novo: "<título>"` ou
`existente: <id/uuid/título>`, conforme a resposta da pergunta 5 da Fase 0. Esse
campo passa pelo gate da Fase 3 junto com o resto do esboço e decide a ramificação
da Fase 4.
```

Wireframe ASCII realinhado (réguas de 59 col., `│` em 0 / 29 / 58):

```
┌────────────────────────────┬────────────────────────────┐
│ Consumo Total do Período   │ Distribuição por Unidade   │
│ (linha · primária)         │ (pizza · secundária)       │
├────────────────────────────┴────────────────────────────┤
│ Histórico Detalhado (tabela · complementar)             │
└─────────────────────────────────────────────────────────┘
```

#### Novos passos da Fase 4

```markdown
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
```

Adição ao gate da Fase 3:

```markdown
- Se o esboço ainda contém nomes placeholder de dataset ou de coluna não
  confirmados, o humano pode aprovar o **design**, mas essa aprovação **não**
  libera a Fase 4: volte para a Fase 1 e vincule os nomes reais primeiro (a Fase 4
  precisa de um `dataset` real e nomes de coluna reais para sequer rodar).
```

---

## Concerns

Nenhuma. Todos os 6 itens de verificação passam. `sdd/final-review-fixes.md`
permanece não-versionado (fora do commit, como o item 5 exige); se o time quiser
versioná-lo, é uma decisão separada.
