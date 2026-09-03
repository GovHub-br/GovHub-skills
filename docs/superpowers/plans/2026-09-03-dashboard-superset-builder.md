# Dashboard Superset Builder Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar a skill `dashboard-superset-builder` no repositório GovHub-skills, cobrindo o fluxo completo esboço → wireframe → validação humana → criação real do dashboard no Superset via MCP.

**Architecture:** Skill de conteúdo (SKILL.md + `references/`) registrada em `01-govhub`, sem código-aplicação — a "implementação" é o texto de instruções que o Claude segue, mais um arquivo de referência com schema real do Superset obtido ao vivo via MCP durante a implementação. Não há suite de testes automatizada neste repositório (é conteúdo markdown/JSON, não código executável); a verificação de cada tarefa é funcional: `scripts/validar-plugins.sh`, inspeção do JSON gerado, e uma leitura de conformidade do SKILL.md contra o design.

**Tech Stack:** Markdown (SKILL.md + references), JSON (`.claude-plugin/*.json` gerados por `scripts/atualizar-manifestos.py`), Bash (`scripts/validar-plugins.sh`), MCP (`call_tool`/`search_tools` contra um servidor Superset MCP escolhido interativamente, sem endereço fixo).

## Global Constraints

- Nenhuma chamada MCP de mutação (`generate_chart` com `save_chart=True`, `add_chart_to_existing_dashboard`, `generate_dashboard`) pode ocorrer antes de uma aprovação humana explícita do esboço — barreira dura, sem exceção.
- Nenhum arquivo do repositório referencia endereço ou token de nenhum servidor MCP — o servidor a usar é sempre perguntado ao usuário na sessão.
- O token do Superset nunca entra em arquivo versionado. `.env` e `.token` (hoje presentes na raiz sem estar versionados) precisam estar no `.gitignore`.
- `generate_dashboard` nunca é usado como fallback de `add_chart_to_existing_dashboard` — só para o primeiro lote de charts de um dashboard novo.
- Skill fica em `01-govhub/dashboard-superset-builder/` (categoria `govhub-core`), ao lado de `govhub-pipeline-guide`.
- Fora de escopo (não implementar): edição de dashboards não criados por esta skill; `create_virtual_dataset`.

Spec completa: [`docs/superpowers/specs/2026-09-03-dashboard-superset-builder-design.md`](../specs/2026-09-03-dashboard-superset-builder-design.md).

---

## File Structure

```
.gitignore                                              # novo — .env e .token
01-govhub/dashboard-superset-builder/
├── SKILL.md                                             # novo
└── references/
    ├── diretrizes-dashboard.md                          # novo
    └── superset-schema.md                               # novo — schema real, obtido ao vivo
01-govhub/.claude-plugin/plugin.json                     # regenerado por script (Tarefa 5)
.claude-plugin/plugin.json                               # regenerado por script (Tarefa 5)
.claude-plugin/marketplace.json                          # regenerado por script (Tarefa 5)
README.md                                                # editado à mão (Tarefa 5) — tabela + contagens
```

---

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

### Task 3: Escrever `references/diretrizes-dashboard.md`

**Files:**
- Create: `01-govhub/dashboard-superset-builder/references/diretrizes-dashboard.md`

**Interfaces:**
- Consumes: conteúdo de `/home/joaoegewarth/GovHub-skills/markdowm-devs.md` (capítulos 2.1, 2.2, 2.3, 3.2, 4.1–4.4).
- Produces: arquivo referenciado por `SKILL.md` (Tarefa 2) nas seções "Perfil do usuário",
  "Hierarquia de informação" e "Densidade visual" — os títulos das seções abaixo
  precisam bater com esses nomes.

- [ ] **Step 1: Criar o arquivo com o resumo curado**

Conteúdo de `01-govhub/dashboard-superset-builder/references/diretrizes-dashboard.md`:

```markdown
# Diretrizes de Design para Dashboards

Resumo curado de `markdowm-devs.md` (Guia para Markdown, 17 capítulos), focado no
que a skill `dashboard-superset-builder` usa nas Fases 0 e 2. Para o guia completo,
veja o arquivo original na raiz do repositório.

**Aviso de cobertura:** os capítulos do guia mais específicos de dashboard — 13
(Estruturação de Dashboards), 14 (Tabelas), boa parte do 15 (Catálogo de
Componentes) e 4.5 (Cores para Visualização de Dados) — estão, na versão atual do
`markdowm-devs.md`, só com os títulos das subseções, sem conteúdo escrito. Não
invente conteúdo para preencher essas lacunas: quando uma decisão do esboço
dependeria de uma diretriz específica ainda não escrita (ex.: regra exata de cor
por tipo de gráfico), sinalize isso no esboço em vez de decidir sozinho.

## Perfil do usuário

Duas perguntas definem a complexidade permitida na interface:

**Experiência digital:**
- **Iniciante** — precisa de mais orientação visual, fluxos simples, baixa
  densidade, ações e informações importantes bem destacadas.
- **Intermediário** — entende padrões comuns de navegação, lida com mais
  informação, precisa de equilíbrio entre clareza e produtividade.
- **Avançado** — prefere velocidade, tolera densidade visual alta, precisa de
  acesso rápido, dispensa explicações excessivas.
- **Especialista** — busca produtividade máxima, quer dados detalhados, tolera
  interfaces complexas, prefere acesso direto a recursos avançados.

**Conhecimento de negócio:**
- **Leigo** (clientes finais, consumidores) — linguagem simples, explicações
  claras.
- **Técnico** (operadores, analistas) — pode usar terminologia da área.
- **Especialista** (engenheiros, consultores) — informação mais detalhada e
  técnica.
- **Gestor** (coordenadores, gerentes, diretores) — prioriza indicadores, resumos
  e informação que apoie decisão, não necessariamente detalhe operacional.

Exemplo prático: **Iniciante + Leigo** pede menos informação por tela, mais
contexto, navegação simples, baixa densidade. **Avançado + Especialista** se
beneficia de mais informação simultânea, menos texto explicativo, menos etapas.
**Avançado + Gestor** pede poucos detalhes operacionais mas muitos indicadores e
comparativos.

## Hierarquia de informação

Toda informação exibida tem custo visual e cognitivo. Antes de incluir algo,
pergunte: "a ausência desta informação impede o usuário de concluir a tarefa?" —
se não, ela deve ser removida, reduzida ou movida para um local secundário.

Camadas, da mais para a menos destacada:

1. **Primária** (~60% da atenção) — o motivo principal de acessar a tela. Maior
   tamanho, maior contraste, maior peso tipográfico, posição prioritária.
   Exemplos: consumo total, quantidade de alertas ativos, receita do período, KPI
   principal.
2. **Secundária** (~25%) — ajuda a interpretar a informação primária, sem competir
   visualmente com ela. Exemplos: comparativo com período anterior, percentual de
   crescimento, categoria do alerta.
3. **Complementar** (~10%) — aprofundamento, acessível quando necessário, sem
   gerar ruído. Exemplos: observações, histórico detalhado, logs, data da última
   atualização.
4. **Opcional/descartável** (~5%) — só em situações específicas (tooltip, drawer,
   modal, tela de detalhe) ou removível de vez. Exemplos: campos técnicos
   avançados, configurações, ilustrações decorativas, texto institucional.

Regra de ouro: se tudo recebe destaque, nada recebe destaque.

## Densidade visual

- **Alta densidade** — usuários avançados, operações técnicas, monitoramento,
  backoffice.
- **Média densidade** — **padrão para dashboards corporativos**, produtos SaaS,
  gestão.
- **Baixa densidade** — público geral, autoatendimento, mobile.

## Contexto de uso

- **Desktop** — mais informação simultânea, tabelas completas, múltiplos
  gráficos, filtros avançados. Mesmo assim, não adicione informação só porque há
  espaço.
- **Tablet** — botões maiores, menor densidade, interações otimizadas para toque,
  considerar retrato e paisagem.
- **Mobile** — priorizar ações principais, alertas, indicadores críticos;
  evitar tabelas complexas e muitos filtros simultâneos.
- **Ambiente corporativo** — priorizar produtividade, reduzir cliques, favorecer
  atalhos.
- **Ambiente operacional/industrial** — leitura rápida, status facilmente
  identificáveis, mínimo de navegação.
- **Uso diário** vs. **uso ocasional** — usuário frequente tolera mais informação
  e fluxos especializados; usuário ocasional precisa de mais suporte visual e
  terminologia simples.

## Cores

**Institucionais:**
- **Primária** — a cor da ação principal da plataforma (botão principal, links,
  estados ativos, seleções, foco). Deve ter escala tonal (100–900) para hover,
  focus, bordas, backgrounds.
- **Secundária** — apoio visual (categorias, destaques específicos, gráficos),
  nunca competindo com a primária.

**Neutras** — sustentam a maior parte da interface (>80% em sistemas
corporativos): branco/off-white para superfícies, tons claros para bordas e
divisores, tons médios para texto secundário/rebaixado, tons escuros para texto
principal. Evite preto e branco absolutos em textos/grandes blocos.

**Semânticas** — significado reconhecido universalmente, nunca usar como
decoração nem trocar de significado entre telas:
- **Verde** — sucesso, aprovado, concluído, saudável, disponível.
- **Vermelho** — erro, falha, alerta, bloqueio, crítico.
- **Amarelo** — atenção, aviso, monitoramento, pendência.
- **Azul** — informação, navegação, ação, referência.
- **Cinza** — desabilitado/desativado.

Nunca usar cor como único indicador de estado — combine sempre com ícone e/ou
texto (redundância visual), importante para acessibilidade (daltonismo, baixa
visão).

## Tipografia e hierarquia

- Poucos tamanhos e poucos pesos tipográficos = mais consistência.
- H1 é o assunto principal da tela (um só por tela); em dashboards, o "H1" visual
  muitas vezes é o KPI/big number, não um texto — mesmo assim, use estrutura
  semântica correta (H1–H6) para acessibilidade (WCAG/eMAG), não só peso/tamanho.
- Fatores que aumentam destaque visual: cor mais saturada, mais contraste, maior
  tamanho, mais espaço em branco ao redor. Quanto mais desses recursos um
  elemento recebe, mais atenção atrai — use com intenção, não em tudo.
- Em um dado dentro de um dashboard, o valor (big number) é o que recebe o maior
  peso/tamanho — o rótulo/chapéu acima dele fica discreto (ex.: rótulo Regular
  10px, valor Bold 15px+).
```

- [ ] **Step 2: Conferir que as três seções que o `SKILL.md` referencia existem com o nome exato**

Run:
```bash
grep -n '^## Perfil do usuário$\|^## Hierarquia de informação$\|^## Densidade visual$' \
  /home/joaoegewarth/GovHub-skills/01-govhub/dashboard-superset-builder/references/diretrizes-dashboard.md
```
Expected: as três linhas aparecem, uma por seção.

- [ ] **Step 3: Commit**

```bash
cd /home/joaoegewarth/GovHub-skills
git add 01-govhub/dashboard-superset-builder/references/diretrizes-dashboard.md
git commit -m "feat(dashboard-superset-builder): adicionar diretrizes-dashboard.md

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

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

### Task 6: Verificação ponta a ponta manual

Esta tarefa não produz arquivo novo — é a checagem funcional final descrita na
seção "Testes / verificação" da spec, e também não deve ser delegada a um
subagente isolado: precisa da participação do usuário (para aprovar/reprovar o
esboço na Fase 3) e do mesmo servidor MCP escolhido na Tarefa 4.

**Files:** nenhum (verificação, não implementação).

- [ ] **Step 1: Rodar a skill de ponta a ponta com um dataset de teste real**

Com a skill instalada/carregada (pasta em `~/.claude/skills/dashboard-superset-builder/`
ou o plugin instalado), peça para "montar um dashboard no Superset" usando um
dataset de teste existente no ambiente do usuário. Acompanhe as 5 fases.

- [ ] **Step 2: Confirmar que o esboço usa nomes de campo reais**

No arquivo de esboço gerado (Fase 2), confirme visualmente que os nomes de campo
(`dataset_id`, `metrics`, `groupby` etc.) batem com o que está em
`references/superset-schema.md` para o `viz_type` escolhido — não são nomes
inventados.

- [ ] **Step 3: Confirmar que o gate da Fase 3 bloqueia mesmo sem aprovação clara**

Responda de forma vaga ("ok", "bacana") à pergunta de aprovação da Fase 3.
Expected: a skill **não** avança para chamadas de criação no Superset — pede uma
confirmação mais direta.

- [ ] **Step 4: Aprovar explicitamente e confirmar a criação real**

Responda com uma aprovação explícita ("aprovado, pode criar"). Expected: a skill
chama `generate_chart` (`save_chart=True`) e depois
`add_chart_to_existing_dashboard` ou `generate_dashboard` (conforme o caso), e ao
final apresenta os IDs/links criados.

- [ ] **Step 5: Confirmar no próprio Superset**

Abra o Superset e confirme que o(s) chart(s) e o dashboard aparecem com os dados
esperados (dataset, métricas e dimensões corretos).

- [ ] **Step 6: Registrar o resultado da verificação**

Se tudo passou, não é necessário nenhum commit adicional — a spec e o plano já
estão commitados. Se algo falhou, volte à tarefa correspondente (2, 3 ou 4),
corrija, e repita esta Tarefa 6 antes de considerar a skill pronta.
