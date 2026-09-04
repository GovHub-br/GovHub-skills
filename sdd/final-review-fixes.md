# Final-review fix list — dashboard-superset-builder

One fix pass over the branch. All paths relative to the worktree root
`/home/joaoegewarth/GovHub-skills/.claude/worktrees/dashboard-superset-builder`.
Branch: `worktree-dashboard-superset-builder`.

User decisions already made:
- Do ALL of the below in one pass.
- Critical 1: the **real Superset schema governs** — rewrite the example with real
  `xy` field names AND fix the plan's Task 6 Step 2 so the manual check doesn't
  re-bless the old names.

The real `xy` chart-config schema (from `references/superset-schema.md`, captured
live, service v6.1.0) — top-level properties:
`chart_type` (const "xy"), `x` (ColumnRef), `y` (array of ColumnRef, min 1),
`kind` (line|bar|area|scatter, default line), `time_grain` (P1D/P1W/P1M/P1Y/…),
`orientation`, `stacked`, `group_by` (array of ColumnRef — SERIES breakdown, not
the x axis), `x_axis`/`y_axis` (AxisConfig), `legend` (LegendConfig),
`filters` (array of FilterConfig), `row_limit`. Required: `x`, `y`.
- `ColumnRef` = `{name (required), label?, dtype?, aggregate? (SUM|COUNT|AVG|MIN|MAX|COUNT_DISTINCT|STDDEV|VAR|MEDIAN|PERCENTILE), saved_metric? (bool)}`
- `FilterConfig` = `{column, op (= > < >= <= != LIKE ILIKE "NOT LIKE" IN "NOT IN"), value}`
- `filters` description in the schema literally says: **"Do NOT use adhoc_filters or raw SQL expressions."**
- `dataset_id` is NOT part of the chart-config schema — it is a parameter of the
  `generate_chart` tool itself (the wrapper), passed alongside `request` and `save_chart`.

---

## Critical 1 — `01-govhub/dashboard-superset-builder/SKILL.md` Fase 2 example (lines ~88-101)

Replace the fenced example block AND its parenthetical caveat. New block must use
real `xy` fields. Keep the `## Componente:` heading style, keep `prioridade:`, keep
a `dataset:` line but label it clearly as the wrapper param, not a config field.
Suggested replacement (adjust prose to match the file's voice):

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

Then update the wireframe legend/example if it references the old field vocabulary
(it doesn't — it uses "linha"/"pizza"/"tabela", fine).

## Critical 1 (part 2) — `docs/superpowers/plans/2026-09-03-dashboard-superset-builder.md` Task 6 Step 2

Find Task 6 "Step 2: Confirmar que o esboço usa nomes de campo reais". It currently
says to confirm names like `dataset_id`, `metrics`, `groupby`. Rewrite so it says:
confirm the `config:` block of each component uses the exact property names from
`references/superset-schema.md` for that component's `viz_type` (e.g. `xy` → `x`,
`y`, `kind`, `filters`; never `metrics`/`groupby`/`adhoc_filters`), and that
`filters` entries are structured `{column, op, value}`.

---

## Important 2 — Fase 4 wrapper is undefined (`SKILL.md` ~line 129-135)

`generate_chart`'s own parameters (how the dataset is passed, chart name/title,
`save_chart`) are not in the schema cache (which only covers the inner `config`).
Add a step 0 to Fase 4, before the per-component loop:

> Antes da primeira chamada, descubra a assinatura real de `generate_chart` (e de
> `add_chart_to_existing_dashboard` / `generate_dashboard`) via `search_tools` +
> uma inspeção do `inputSchema` — não presuma os nomes dos parâmetros wrapper
> (dataset, título do chart, `save_chart`). O cache em `references/superset-schema.md`
> cobre só o objeto `config`/`request` interno, não os parâmetros da tool.

Also reword Fase 4 item 1 so it's clear the component's `config:` block goes into
the tool's request object and `dataset` + chart title + `save_chart=True` are
wrapper params.

## Important 3 — dashboard target never collected (`SKILL.md` Fase 0 + Fase 2 + Fase 3)

Fase 4 must choose between `add_chart_to_existing_dashboard` and `generate_dashboard`
but no phase collects which. Fix:
- Add a Fase 0 question 5: **"Dashboard novo ou já existente? Se existente, qual
  (ID, UUID ou título)?"**
- Add a line to the Fase 2 sketch header (before the component blocks): a
  `dashboard alvo:` field (`novo: "<título>"` ou `existente: <id/uuid/título>`),
  so it passes through the Fase 3 gate.
- In Fase 4 item 2, branch on that field explicitly: `existente` →
  `add_chart_to_existing_dashboard`; `novo` → `generate_dashboard` with the list of
  chart IDs from this run (first batch only). Keep the existing "nunca use
  generate_dashboard como fallback" sentence.

## Important 4 — "dataset desconhecido" has no resolution point (`SKILL.md` Fase 1 + Fase 3)

- Fase 1: when the dev has no dataset / doesn't know which, add: call
  `list_datasets` (read-only) and show the dev the candidates so they can pick one;
  only fall back to descriptive placeholder names if the dev still can't choose.
- Fase 3: add to the gate — if the sketch still contains unconfirmed placeholder
  field/dataset names, the human may approve the *design*, but that approval does
  NOT release Fase 4; loop back to Fase 1 to bind real names first. Fase 4 needs a
  real `dataset` and real column names to run at all.

## Important 5 — dangling pointer in `references/diretrizes-dashboard.md` (lines ~4-5)

It says "Para o guia completo, veja o arquivo original na raiz do repositório"
referring to `markdowm-devs.md`, which is NOT committed (untracked, user's local
copy only). Reword to describe it as an internal team document that is not shipped
with the skill — do not claim the reader can open it from the repo. Keep the
coverage caveat (chapters 13/14/15/4.5 are titles-only) but phrase it as
"no guia interno usado como fonte" rather than implying the file is present.
Do NOT commit `markdowm-devs.md` (user has not asked to ship it).

---

## Minor 6 — `NOTICE.md` stale count

Line ~45: "Das 51 skills que restam" → 52. Only change the total that this branch
made stale; leave the "43 sem procedência" figure (still correct — new skill is
GovHub-authored).

## Minor 8 — ASCII wireframe borders misaligned (`SKILL.md` ~108-115)

The `┌ ┬ ┐ / ├ ┴ ┤ / └ ┘` rules are three different widths. Redraw so all three
horizontal rules are the same width and the `│` separators line up. Keep it a
2-column grid with a full-width row below.

## Minor 10 — `references/superset-schema.md` header wording (line ~5)

"cada bloco abaixo é o retorno bruto de `get_chart_type_schema(...)`" — the blocks
store only the inner `schema` object, not the full `{chart_type, schema, examples}`
return. Reword to "o objeto `schema` retornado por `get_chart_type_schema(...)`
(mais o(s) `examples`)".

## Minor 11 — `.gitignore` doesn't cover `handoff-skill-mcp.md`

That file (repo root, untracked) contains the MCP address `10.0.0.32:30508`.
Add `handoff-skill-mcp.md` to `.gitignore` so `git add .` can't stage it. (Do not
add `markdowm-devs.md` to `.gitignore` — leave that decision to the user; it has no
address/token.) Actually: only add `handoff-skill-mcp.md`.

---

## NOT in this pass (leave alone)

- Minor 7 (missing `author:`/`license:` frontmatter) — repo-wide gap across all
  `01-govhub` skills; user is handling separately. Do not touch frontmatter.

## Verification for your report

1. `bash scripts/validar-plugins.sh; echo exit=$?` → 0.
2. `grep -nE 'adhoc_filters|groupby|\bmetrics:' 01-govhub/dashboard-superset-builder/SKILL.md`
   → the only hits allowed are ones explicitly saying "não use adhoc_filters"; no
   hit presenting them as real field names.
3. `git grep -n '10.0.0.32\|Bearer\|eyJ' -- ':!sdd/'` → no NEW hits in tracked files
   (pre-existing placeholder hits in unrelated skills are fine; list them).
4. `grep -n 'handoff-skill-mcp.md' .gitignore` → present.
5. `git diff --stat` before commit → only: SKILL.md, references/diretrizes-dashboard.md,
   references/superset-schema.md, .gitignore, NOTICE.md, and the plan .md. Nothing else.
6. Show the new Fase 0 question list, the new Fase 2 example block, and the new
   Fase 4 steps in your report so the reviewer can check them without re-diffing.

Commit everything as ONE commit:

```
fix(dashboard-superset-builder): alinhar SKILL.md ao schema real e cobrir inputs da Fase 4

Correções do review final do branch:
- exemplo da Fase 2 usa os campos reais do viz_type xy (não mais metrics/groupby/adhoc_filters)
- Fase 0 passa a coletar o dashboard alvo (novo x existente); Fase 4 ramifica nisso
- Fase 4 descobre a assinatura wrapper de generate_chart antes da 1a chamada
- Fase 1 usa list_datasets p/ ajudar a escolher; Fase 3 não libera Fase 4 com nomes placeholder
- diretrizes-dashboard.md não aponta mais p/ arquivo não versionado
- Task 6 Step 2 do plano deixa de re-abençoar os nomes de campo antigos
- NOTICE.md 51->52; wireframe ASCII alinhado; .gitignore cobre handoff-skill-mcp.md

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
```

Append your fix report to `sdd/task-5-report.md`? No — write it to
`sdd/final-review-fix-report.md` (new file).
