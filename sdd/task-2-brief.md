### Task 2: Escrever `SKILL.md`

**Files:**
- Create: `01-govhub/dashboard-superset-builder/SKILL.md`

**Interfaces:**
- Consumes: nada de outras tarefas (o texto referencia `references/diretrizes-dashboard.md` e `references/superset-schema.md` pelo nome do arquivo, criados nas Tarefas 3 e 4 — a ordem de criação não importa para o conteúdo deste arquivo).
- Produces: o arquivo `SKILL.md` que a Tarefa 5 (`scripts/validar-plugins.sh`) valida (frontmatter `name: dashboard-superset-builder` tem que bater com o nome da pasta).

- [ ] **Step 1: Criar a pasta e o arquivo com o conteúdo completo**

```bash
mkdir -p /home/joaoegewarth/GovHub-skills/01-govhub/dashboard-superset-builder/references
```

Conteúdo de `01-govhub/dashboard-superset-builder/SKILL.md`:

````markdown
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
4. **Dataset alvo no Superset**, se já existir (nome, ID ou UUID). Se não existir
   ou o dev não souber, siga sem isso — a Fase 1 é pulada e o esboço usa nomes
   descritivos.

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

Se o dataset ainda não existe ou o dev não sabe qual usar, siga para a Fase 2 com
nomes descritivos e **sinalize explicitamente no esboço** que esses nomes precisam
ser confirmados antes da Fase 4.

Essas chamadas são somente leitura — não têm a tag `mutate` — então não precisam de
aprovação humana.

## Fase 2 — Montar o esboço (markdown + wireframe)

Produza um único arquivo markdown com um bloco `## Componente: <nome>` por chart.
Para cada componente:

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

Formato de cada bloco:

```markdown
## Componente: Consumo Total do Período
- dataset_id: 42 (consumo_energia)
- viz_type: xy (linha)
- metrics: [SUM(consumo_kwh)]
- groupby: [data_referencia]
- adhoc_filters: [unidade = "Matriz"]
- prioridade: primária
```

(Os campos exatos variam por `viz_type` — o exemplo acima é ilustrativo para `xy`;
siga o schema real do tipo escolhido.)

Depois do último bloco, gere um **wireframe em ASCII ou Mermaid**, embutido no
mesmo arquivo markdown, mostrando a posição relativa dos componentes num grid de 2
colunas (mesmo padrão de auto-posicionamento do `add_chart_to_existing_dashboard`).
Exemplo de wireframe ASCII:

```
┌─────────────────────────────┬─────────────────────────────┐
│ Consumo Total do Período     │ Distribuição por Unidade     │
│ (linha · primária)           │ (pizza · secundária)         │
├─────────────────────────────┴─────────────────────────────┤
│ Histórico Detalhado (tabela · complementar)                 │
└──────────────────────────────────────────────────────────────┘
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

## Fase 4 — Criação real no Superset

Para cada componente aprovado, na ordem em que aparecem no esboço:

1. `generate_chart` com `save_chart=True`, montando o `request` conforme o schema
   real do `viz_type` (do cache em `references/superset-schema.md`, ou consultado
   ao vivo via `get_chart_type_schema` se o tipo não estiver cacheado).
2. `add_chart_to_existing_dashboard` para adicionar o chart criado a um dashboard
   já existente — **ou** `generate_dashboard` (passando a lista de chart IDs
   criados nesta rodada) **apenas** se for a primeira leva de charts de um
   dashboard novo. Nunca use `generate_dashboard` como fallback de
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
````

- [ ] **Step 2: Verificar que o frontmatter é YAML válido e o `name` bate com a pasta**

Run:
```bash
python3 - <<'PY'
import pathlib, re
p = pathlib.Path("/home/joaoegewarth/GovHub-skills/01-govhub/dashboard-superset-builder/SKILL.md")
texto = p.read_text(encoding="utf-8")
m = re.search(r'^name:\s*([^\n]+)$', texto, re.M)
assert m, "frontmatter sem 'name:'"
nome = m.group(1).strip()
assert nome == p.parent.name, f"name={nome!r} não bate com a pasta {p.parent.name!r}"
print("OK:", nome)
PY
```
Expected: `OK: dashboard-superset-builder`

- [ ] **Step 3: Commit**

```bash
cd /home/joaoegewarth/GovHub-skills
git add 01-govhub/dashboard-superset-builder/SKILL.md
git commit -m "feat(dashboard-superset-builder): adicionar SKILL.md

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

