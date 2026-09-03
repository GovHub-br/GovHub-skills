### Task 5: Registrar a skill nos manifestos e no README

**Files:**
- Modify: `01-govhub/.claude-plugin/plugin.json` (via script, não à mão)
- Modify: `.claude-plugin/plugin.json` (via script)
- Modify: `.claude-plugin/marketplace.json` (via script)
- Modify: `README.md:54-55` (contagens) e `README.md:130-136` (tabela da seção "01 · Específicas do GovHub")

**Interfaces:**
- Consumes: `01-govhub/dashboard-superset-builder/SKILL.md` deve existir com
  frontmatter válido (Tarefa 2) para `skills_de()` do script encontrá-la.

- [ ] **Step 1: Regenerar os manifestos**

Run:
```bash
cd /home/joaoegewarth/GovHub-skills
python3 scripts/atualizar-manifestos.py
```
Expected: saída lista `dashboard-superset-builder` dentro dos skills de
`01-govhub`, e a última linha muda de "Total: 51 skills" para "Total: 52 skills".

- [ ] **Step 2: Validar a coerência dos manifestos**

Run: `bash scripts/validar-plugins.sh`
Expected: script termina sem erro (exit code 0).

- [ ] **Step 3: Atualizar as contagens no `README.md`**

Em `README.md`, troque:
```diff
-| `govhub-skills` | **Tudo** — as 51 skills de todas as categorias | 51 |
-| `govhub-core` | [01 · Específicas do GovHub](#01--específicas-do-govhub) — pipelines, identidade visual, prestação de contas | 3 |
+| `govhub-skills` | **Tudo** — as 52 skills de todas as categorias | 52 |
+| `govhub-core` | [01 · Específicas do GovHub](#01--específicas-do-govhub) — pipelines, identidade visual, prestação de contas, dashboards Superset | 4 |
```

- [ ] **Step 4: Adicionar a linha da skill na tabela da seção "01 · Específicas do GovHub"**

Depois da linha de `accountability-report` (`README.md:136`), adicione:
```diff
 | [`accountability-report`](01-govhub/accountability-report/) | Relatório de prestação de contas de um repositório a partir do git. Saída em Markdown, HTML e PDF A4 pronto para entrega oficial. |
+| [`dashboard-superset-builder`](01-govhub/dashboard-superset-builder/) | Planeja (esboço + wireframe), valida com o dev, e cria de fato dashboards e charts no Superset via MCP. |
```

- [ ] **Step 5: Commit**

```bash
cd /home/joaoegewarth/GovHub-skills
git add .claude-plugin/plugin.json .claude-plugin/marketplace.json 01-govhub/.claude-plugin/plugin.json README.md
git commit -m "feat: registrar dashboard-superset-builder nos manifestos e no README

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

