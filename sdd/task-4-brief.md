### Task 4: Descobrir e cachear o schema real do Superset (`references/superset-schema.md`)

Esta tarefa depende de uma conexão MCP viva com um servidor Superset — **não pode
ser executada por um subagente isolado sem acesso à sessão do usuário**. Execute-a
na sessão principal, com o usuário disponível para responder a pergunta do Step 1.

**Files:**
- Create: `01-govhub/dashboard-superset-builder/references/superset-schema.md`

**Interfaces:**
- Consumes: um servidor MCP do Superset conectado na sessão (tools
  `search_tools`/`call_tool`), escolhido interativamente — nenhum endereço
  hardcoded.
- Produces: arquivo referenciado por `SKILL.md` (Tarefa 2) nas Fases 2 e 4 como
  fonte do schema por `viz_type`.

- [ ] **Step 1: Perguntar ao usuário qual servidor MCP do Superset usar**

Liste os servidores MCP disponíveis na sessão (o comando exato depende do
ambiente — em Claude Code, `claude mcp list`) e pergunte ao usuário qual deles é o
Superset, a menos que só exista um com o padrão de tools esperado
(`get_instance_info`/`health_check`/`search_tools`/`call_tool`), caso em que
confirme antes de prosseguir. Não segure o resto da tarefa sem essa resposta.

- [ ] **Step 2: Confirmar conectividade**

Via `call_tool` no servidor escolhido, chame `health_check` (ou `get_instance_info`
se `health_check` não existir). Expected: resposta de sucesso (status ok / info da
instância), sem erro de autenticação.

- [ ] **Step 3: Descobrir a lista completa de `viz_type` válidos**

Chame `get_chart_type_schema` com um `chart_type` intencionalmente inválido (ex.:
`"__invalid__"`). O erro retornado costuma listar todos os tipos válidos
aceitos — registre essa lista completa (vai para o cabeçalho do arquivo no Step
5).

- [ ] **Step 4: Obter o schema de cada `viz_type` relevante para dashboard corporativo**

Para cada um de `xy`, `table`, `pie`, `pivot_table`, `mixed_timeseries`, e
qualquer outro tipo da lista do Step 3 que faça sentido para dashboard corporativo
(ex.: big number/KPI, se existir um tipo dedicado), chame:

```json
{"name": "get_chart_type_schema", "arguments": {"chart_type": "<tipo>", "include_examples": true}}
```

via `call_tool`. Guarde o JSON Schema completo e o exemplo retornado para cada
tipo.

- [ ] **Step 5: Escrever `references/superset-schema.md` com os schemas reais obtidos**

Estrutura do arquivo (preencha cada bloco ` ```json ` com o schema **real**
retornado no Step 4 — não com um schema inventado):

````markdown
# Schema do Superset por `viz_type`

Cache estático do schema real de `generate_chart`, obtido via `get_chart_type_schema`
do MCP do Superset. Evita depender de uma chamada ao vivo ao MCP durante o
planejamento (Fases 0–3 da skill); a criação real (Fase 4) ainda pode consultar o
MCP ao vivo para um `viz_type` que não esteja aqui.

## Tipos válidos (`viz_type`)

<lista completa obtida no Step 3>

## xy

```json
<schema real obtido no Step 4 para "xy">
```

Exemplo:
```json
<exemplo real, se `include_examples` retornou um>
```

## table

```json
<schema real obtido no Step 4 para "table">
```

## pie

```json
<schema real obtido no Step 4 para "pie">
```

## pivot_table

```json
<schema real obtido no Step 4 para "pivot_table">
```

## mixed_timeseries

```json
<schema real obtido no Step 4 para "mixed_timeseries">
```
````

Repita uma seção `## <viz_type>` para cada tipo adicional coletado no Step 4.

- [ ] **Step 6: Verificar que o arquivo não contém nenhum endereço ou token**

Run:
```bash
grep -inE 'bearer|token|http://|https://[0-9]' \
  /home/joaoegewarth/GovHub-skills/01-govhub/dashboard-superset-builder/references/superset-schema.md
```
Expected: nenhuma saída (o schema JSON não deve conter URLs de servidor nem
tokens — só nomes de campo e tipos).

- [ ] **Step 7: Commit**

```bash
cd /home/joaoegewarth/GovHub-skills
git add 01-govhub/dashboard-superset-builder/references/superset-schema.md
git commit -m "feat(dashboard-superset-builder): cachear schema real do Superset por viz_type

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

