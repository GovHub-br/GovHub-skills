### Task 1: Proteger credenciais locais (`.gitignore`)

**Files:**
- Create: `.gitignore`

**Interfaces:** nenhuma (arquivo de configuração do git, não consumido por outras tarefas).

- [ ] **Step 1: Confirmar que `.env` e `.token` não estão rastreados pelo git**

Run: `git -C /home/joaoegewarth/GovHub-skills ls-files -- .env .token`
Expected: saída vazia (nenhum dos dois arquivos rastreado).

- [ ] **Step 2: Criar `.gitignore` na raiz do repositório**

```gitignore
# Credenciais locais — nunca versionar (ver docs/superpowers/specs/2026-09-03-dashboard-superset-builder-design.md)
.env
.token
```

- [ ] **Step 3: Confirmar que o git agora ignora os dois arquivos**

Run: `git -C /home/joaoegewarth/GovHub-skills status --porcelain --ignored -- .env .token`
Expected: as duas linhas aparecem prefixadas com `!!` (ignorados), não com `??`.

- [ ] **Step 4: Commit**

```bash
cd /home/joaoegewarth/GovHub-skills
git add .gitignore
git commit -m "chore: ignorar .env e .token (credenciais locais)

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

