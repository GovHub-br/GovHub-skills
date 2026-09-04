# Design — Separar núcleo de planejamento e conectores; migrar Superset de MCP para API REST

Data: 2026-09-04
Skills afetadas: `01-govhub/dashboard-superset-builder/` (existente, vira conector) +
`01-govhub/dashboard-builder/` (nova, núcleo).
Contexto: o servidor MCP do Superset usado até aqui tem um bug real e isolado em
`get_dashboard_info`/`list_dashboards` (erro ao serializar `RoleInfo.permissions` —
recebe objetos `PermissionView` em vez de strings). A equipe de infra do usuário já
usa a API REST do Superset diretamente por esse motivo, e vai migrar de vez. Este
design aproveita a migração para também separar a skill em núcleo (agnóstico de
ferramenta) + conectores (um por ferramenta de BI), preparando terreno para Power
BI e Metabase em ciclos futuros.

## Sub-projetos e ordem

Este pedido cobre 3 subsistemas independentes: núcleo + conector Superset (este
design), conector Power BI (futuro), conector Metabase (futuro). Só o primeiro é
desenhado agora — os outros dois ficam registrados aqui como próximos, sem design.

## Escopo deste sub-projeto

**Entra:**
- Nova skill `dashboard-builder` (núcleo): Fases de perfil/dispositivo/pergunta-
  dos-5-segundos, esboço + wireframe, e gate humano — hoje misturadas com lógica
  específica de Superset em `dashboard-superset-builder`, extraídas para ficarem
  reutilizáveis pelos futuros conectores. Pergunta na Fase 0 qual ferramenta usar.
- `dashboard-superset-builder` fica só o **conector**: as perguntas específicas
  de dataset/dashboard alvo, a descoberta (dataset, dashboard fonte) e a criação
  real — tudo via **API REST do Superset**, sem MCP.
- `references/diretrizes-dashboard.md` migra para `dashboard-builder`.
- `references/superset-schema.md` (cache de JSON Schema vindo do MCP) é
  **removido** — não tem equivalente na API REST (ver seção "Schema de chart").
- `references/superset-api.md` (novo, no conector): curadoria de `api.md` — um
  documento de conhecimento operacional do usuário, baseado em dois scripts de
  produção reais (`bootstrap_conjuntura.py`, `build_boletim.py`), cobrindo
  autenticação, paginação, ordem de criação, idempotência, `position_json` e uma
  lista de armadilhas já sofridas.
- `scripts/superset_client.py` (novo, no conector): cliente REST com autenticação
  por cookie de sessão + CSRF, e subcomandos que cobrem descoberta e criação.
- Manifestos e README atualizados (nova skill; descrição do conector ajustada).

**Fora de escopo (fica pra depois, sem design agora):**
- `dashboard-powerbi-builder`, `dashboard-metabase-builder`.
- Qualquer funcionalidade nova além da migração de MCP→REST e da separação
  núcleo/conector (a Fase 1b de re-derivar de um dashboard fonte, já construída,
  é preservada — só troca a chamada de `call_tool` pro script).
- Uso de `--dry-run`/CLI do script fora dos subcomandos já listados.

## Decisão herdada da conversa

O MCP do Superset é abandonado para este conector — não como workaround
temporário, mas como decisão definitiva, alinhada com a migração que a infra do
usuário já está fazendo.

## Arquitetura: núcleo orquestrador + skills conectoras

`dashboard-builder` (núcleo) não sabe nada sobre Superset, Power BI ou Metabase.
Ela conduz a parte de raciocínio de design (perfil de usuário, hierarquia de
informação, densidade visual, esboço, wireframe, gate humano) e, nos dois pontos
em que precisa de dados ou ações reais de uma ferramenta de BI, instrui o agente a
invocar a skill conectora correspondente — o mesmo mecanismo de handoff que já
existe entre skills desta sessão (brainstorming → writing-plans): uma skill, ao
ser seguida, pode dizer "invoque a skill X agora", e o agente invoca via seu
mecanismo normal de skills, carregando as duas instruções na mesma tarefa
contínua (não é um subagente isolado).

### Coreografia (ordem de execução)

1. **`dashboard-builder` Fase 0 (núcleo):** perfil do usuário, dispositivo,
   pergunta dos 5 segundos, e **qual ferramenta usar** (Superset / Power BI /
   Metabase — hoje só Superset tem conector).
2. **Handoff →** invoca a skill conectora escolhida.
3. **Conector — Fase 0-conector:** perguntas específicas da ferramenta (para
   Superset: dataset alvo se já existir; dashboard novo, existente, ou a partir
   de um dashboard fonte).
4. **Conector — Fase 1 / Fase 1b:** descoberta real (dataset; dashboard fonte,
   se aplicável) via `superset_client.py`.
5. **Handoff ←** volta para `dashboard-builder` **Fase 2** (monta esboço +
   wireframe com os nomes reais descobertos) e **Fase 3** (gate humano) —
   **inalteradas** em relação ao que já existe hoje.
6. **Handoff →** conector **Fase 4**: execução real via `superset_client.py`.

### Constraints globais (mesmo espírito de antes, mecanismo novo)

- Nenhuma chamada de escrita (`create-chart`, `create-dashboard`,
  `add-chart-to-dashboard`) antes da aprovação explícita da Fase 3 do núcleo —
  barreira dura, sem exceção. Substitui a antiga regra sobre tools com tag
  `mutate`.
- `SUPERSET_URL`, `SUPERSET_USERNAME`, `SUPERSET_PASSWORD` nunca em arquivo
  versionado — variável de ambiente/`.env` local. Substitui a antiga regra sobre
  endereço/token de MCP.
- Idempotência é obrigatória em toda operação de escrita: procurar por
  nome/slug antes de criar; ao achar, conferir o **conteúdo** (não só a
  existência) antes de decidir se atualiza.
- `position_json` sempre com `meta` em todo nó da árvore; cadeia mínima
  `ROOT → GRID → ROW → CHART`.
- A Fase 1b (re-derivar de um dashboard fonte) continua somente leitura e sem
  gate humano — regra herdada de
  [`2026-09-04-dashboard-superset-rederive-from-source-design.md`](2026-09-04-dashboard-superset-rederive-from-source-design.md),
  sem mudança de substância: só troca `get_dashboard_info`/`get_chart_info` (MCP)
  por `get-dashboard`/`get-chart` (subcomandos do script).
- `create_virtual_dataset`/criar datasets continua fora de escopo do conector
  (igual já era fora de escopo no design MCP).

## Autenticação (corrigida por `api.md` — cookie de sessão, não JWT)

`api.md` documenta, com evidência real desta instância, que o bearer JWT de
`/api/v1/security/login` **não enxerga todos os dashboards** (`GET
/api/v1/dashboard/<slug>` retorna 404 com bearer e 200 com cookie de sessão; a
listagem com bearer omite os mesmos dashboards). Por isso o cliente usa sessão:

1. `GET /login/` → extrai o `csrf_token` (campo oculto no HTML).
2. `POST /login/` com `username`, `password`, `csrf_token` — autenticação por
   formulário, guarda o cookie de sessão.
3. `GET /api/v1/security/csrf_token/` → fixa `X-CSRFToken` e `Referer` nos
   headers da sessão (o Superset recusa escrita sem `Referer`).

Credenciais em `SUPERSET_URL`/`SUPERSET_USERNAME`/`SUPERSET_PASSWORD` (variável
de ambiente/`.env` local, nunca versionado).

## `scripts/superset_client.py` — subcomandos

| Subcomando | Fase | Escrita? | O que faz |
|---|---|---|---|
| `list-datasets [--filtro TEXT]` | 1 | não | Lista datasets, paginando em Rison (`q=(page:N,page_size:100)`) |
| `get-dataset <id>` | 1 | não | Colunas/métricas reais de um dataset |
| `get-dashboard <slug_ou_id>` | 1b | não | Aceita slug ou id numérico; usa sempre `GET /api/v1/dashboard/<ref>` direto, **nunca a listagem** (que pode omitir dashboards — armadilha documentada no `api.md`). Devolve título, charts e `position_json`; 404 vira "não existe", não erro fatal |
| `get-chart <id>` | 1b | não | `params`/`form_data` reais de um chart |
| `create-chart --file chart.json [--dry-run]` | 4 | sim | `POST /api/v1/chart/` idempotente: procura por `slice_name`, compara `datasource_id`, só cria/atualiza se necessário |
| `create-dashboard --file dashboard.json [--dry-run]` | 4 | sim | `POST /api/v1/dashboard/`; monta `position_json` com `meta` em todo nó |
| `add-chart-to-dashboard <dashboard_id> <chart_id> [--dry-run]` | 4 | sim | Lê o `position_json` atual, acrescenta o chart num novo slot de grid, `PUT` |

`--dry-run` sempre lê de verdade, só pula a escrita — nunca reporta "criaria X"
sem antes checar se X já existe.

## Schema de chart: de JSON Schema (MCP) para exemplo-guiado (REST)

A API REST não expõe uma abstração tipada por `viz_type` como o
`get_chart_type_schema` do MCP dava (`ColumnRef`, `FilterConfig`, etc.). O campo
`params` de um chart é uma **string JSON** no formato nativo do Superset
(`form_data`), específico de cada `viz_type` e sem schema formal exposto pela
API. `references/superset-api.md` documenta esse fato e a técnica de
substituição: capturar exemplos reais via `get-chart <id>` em charts existentes
de cada `viz_type` relevante, do mesmo jeito que o cache MCP foi construído
"ao vivo" na Tarefa 4 do design anterior — só que agora contra a API REST, como
uma tarefa de implementação (não escrita neste design).

## Testes de `superset_client.py`

Diferente do resto do repositório (conteúdo puro), este é código executável de
verdade — ganha testes automatizados com HTTP mockado (sem precisar de Superset
ao vivo), cobrindo:
- construção da query Rison de paginação;
- decisão de idempotência (busca por nome/slug → compara conteúdo → cria só se
  necessário);
- montagem do `position_json` (cadeia `ROOT → GRID → ROW → CHART`, `meta` em
  todo nó);
- o fluxo de login (CSRF da página → `POST` de formulário → CSRF da API →
  headers da sessão).

Depende de `requests` (já usada nos scripts de produção que originaram o
`api.md`); a skill declara essa dependência e instrui instalar se faltar. A
verificação **ao vivo** contra o Superset real (criar um chart/dashboard de
teste de verdade) continua sendo uma tarefa manual no fim do plano de
implementação, como já era com o MCP.

## Estrutura de arquivos

```
01-govhub/dashboard-builder/                      # novo — núcleo
├── SKILL.md                                       # Fase 0(perfil/dispositivo/pergunta) + escolha de ferramenta + Fase 2(esboço) + Fase 3(gate)
└── references/
    └── diretrizes-dashboard.md                    # movido de dashboard-superset-builder

01-govhub/dashboard-superset-builder/              # existente — vira conector
├── SKILL.md                                       # reescrito: Fase 0-conector, Fase 1, Fase 1b, Fase 4 — via REST
├── scripts/
│   ├── superset_client.py                         # cliente REST (auth cookie+CSRF, subcomandos da tabela acima)
│   └── test_superset_client.py                    # testes com HTTP mockado
└── references/
    └── superset-api.md                            # curadoria de api.md
    # superset-schema.md (cache MCP) removido
```

## Manifestos e README

`dashboard-builder` entra como skill nova (contagem +1). Descrição de
`dashboard-superset-builder` no README/manifesto passa a refletir o papel de
conector (descoberta e execução reais via API REST do Superset — não "planeja e
cria" sozinho, isso agora é do núcleo).

## Verificação (tarefa de teste, ponta a ponta)

Igual em espírito ao design anterior, adaptado pro fluxo com dois skills:

1. `dashboard-builder` roteia corretamente para `dashboard-superset-builder`
   quando a ferramenta escolhida é Superset.
2. `superset_client.py` autentica (sessão + CSRF) contra a instância real.
3. Descoberta (`list-datasets`/`get-dataset`/`get-dashboard`/`get-chart`)
   recupera dados reais — incluindo o caso de dashboard-fonte (Fase 1b),
   confirmando que a busca por slug funciona mesmo quando a listagem omitiria o
   dashboard.
4. Esboço e gate da Fase 3 funcionam como hoje (resposta vaga não libera Fase 4).
5. `create-chart`/`create-dashboard`/`add-chart-to-dashboard` criam de verdade,
   de forma idempotente (rodar duas vezes não duplica).
6. Confirmar no Superset que o resultado bate com o esboço aprovado.
