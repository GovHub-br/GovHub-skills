# Design — Skill `dashboard-superset-builder`

## Contexto

O time de dev do GovHub quer planejar dashboards antes de implementá-los no Superset,
e depois criá-los de fato lá, sem tradução manual entre "o que o dev pensou" e "o
que o Superset MCP espera". Uma tentativa anterior dessa skill (`esboco-dashboard-superset`)
foi construída numa sessão de chat que foi apagada antes de ser salva no repositório —
este documento reconstrói o design do zero, incorporando o que sobreviveu em
`handoff-skill-mcp.md` e ampliando o escopo conforme decidido nesta sessão.

Duas fontes de entrada já existem no repositório e servem de insumo direto:

- `markdowm-devs.md` — guia de diretrizes de design ("Guia para Markdown", 17
  capítulos) fornecido pelo time de design, para estruturar interfaces geradas por IA.
- Um servidor **Superset MCP** (lazy-loading: `get_instance_info`, `health_check`,
  `search_tools`, `call_tool` como camada fixa; as tools reais do Superset — chart,
  dashboard, dataset — aparecem via `search_tools`/`call_tool`), já usado em uma
  sessão anterior contra `http://10.0.0.32:30508/mcp` com Bearer token JWT.

## Escopo

A skill cobre o fluxo **completo**: esboço → wireframe → validação humana → criação
real do dashboard no Superset. Isso foi uma decisão explícita do usuário (não um
default do design): o risco de ações `mutate` no Superset é aceito, desde que
protegido por um gate humano obrigatório entre o esboço e a criação real.

Fora de escopo desta primeira versão: edição/atualização de dashboards já existentes
que não foram criados por esta skill; criação de datasets virtuais via SQL
(`create_virtual_dataset`) — fica anotado como extensão futura, não bloqueia o v1.

## Arquitetura — 5 fases

```
Fase 0 — Contexto      Fase 1 — Descoberta     Fase 2 — Esboço          Fase 3 — GATE          Fase 4 — Criação real
(perfil usuário,   →   MCP: get_dataset_info  → markdown formal     →   humano aprova      →   MCP: generate_chart
objetivo, dataset)     get_schema (read-only)    + wireframe ASCII      esboço + wireframe      + generate_dashboard /
                                                                          (edita se pedir)        add_chart_to_existing
```

Nenhuma chamada `mutate` (`generate_chart` com `save_chart=True`,
`add_chart_to_existing_dashboard`, `generate_dashboard`) acontece antes da Fase 3
ser concluída com aprovação explícita do dev. Essa é uma barreira dura da skill, não
uma sugestão: se a Fase 3 não teve uma resposta afirmativa e explícita, a skill não
avança para a Fase 4 sob nenhuma circunstância (nem "parece que ele ia aprovar").

### Fase 0 — Contexto

A skill pergunta ao dev (seguindo o checklist de perfil de usuário e contexto de uso
do `markdowm-devs.md`, cap. 2), só o que ainda não estiver claro na conversa:

- Perfil do usuário final do dashboard: nível de experiência digital (iniciante/
  intermediário/avançado/especialista) + nível de conhecimento de negócio (leigo/
  técnico/especialista/gestor).
- Dispositivo principal (desktop/tablet/mobile) — dashboard corporativo tende a
  desktop, mas confirmar.
- Qual pergunta o dashboard precisa responder em 5 segundos (a informação primária,
  cap. 2.2 do guia).
- Dataset alvo no Superset, se já existir (nome, ID ou UUID).

Antes de prosseguir, a skill verifica que o Superset MCP está acessível na sessão
(`health_check`/`get_instance_info` via `call_tool`). Se não estiver conectado, a
skill explica como conectar (servidor MCP com Bearer token em variável de
ambiente/secret manager — nunca em arquivo do repositório) e não prossegue sem
confirmação de que a conexão existe.

### Fase 1 — Descoberta no Superset (somente leitura)

Se o dev já indicou um dataset existente, a skill chama `get_dataset_info` e/ou
`get_schema` (via `call_tool`) para obter as colunas, métricas e dimensões **reais**
daquele dataset, e usa esses nomes no esboço em vez de texto livre inventado pelo
dev. Se o dataset ainda não existe ou o dev não sabe qual usar, a skill segue com
nomes descritivos no esboço e sinaliza explicitamente que precisam ser confirmados
antes da Fase 4.

Essas chamadas são somente leitura (não têm a tag `mutate`), então acontecem sem
gate humano.

### Fase 2 — Montar o esboço (markdown + wireframe)

A skill produz um único arquivo markdown com um bloco `## Componente: <nome>` por
chart, aplicando a hierarquia de informação do guia (Primária/Secundária/
Complementar/Descartável — cap. 2.2) e densidade "média" (padrão para dashboards
corporativos, cap. 2.2), com campos que já usam a nomenclatura do Superset:

```markdown
## Componente: Consumo Total do Período
- dataset_id: 42 (consumo_energia)
- viz_type: xy (linha)
- metrics: [SUM(consumo_kwh)]
- groupby: [data_referencia]
- adhoc_filters: [unidade = "Matriz"]
- prioridade: primária
```

Os nomes exatos de campo (`dataset_id`, `metrics`, `groupby`, `adhoc_filters`,
`viz_type` etc.) variam por `viz_type` e vêm do cache de schema (ver seção
"Cache de schema do Superset" abaixo) — a skill não inventa nomes de campo.

Junto ao markdown, a skill gera um wireframe em **ASCII/Mermaid embutido no próprio
arquivo**, mostrando a posição relativa dos componentes num grid de 2 colunas (o
mesmo padrão de auto-posicionamento do `add_chart_to_existing_dashboard`).

### Fase 3 — Gate de validação humana

A skill apresenta o esboço completo (markdown + wireframe) e pergunta explicitamente
se o dev aprova, quer ajustar algo, ou quer cancelar. Ajustes voltam para a Fase 2
(a skill não corrige e segue sozinha — reapresenta a versão ajustada para nova
aprovação). Só uma resposta afirmativa e explícita libera a Fase 4.

### Fase 4 — Criação real no Superset

Para cada componente aprovado, na ordem em que aparecem no esboço:

1. `generate_chart` com `save_chart=True`, montando o `request` conforme o schema
   real do `viz_type` (do cache, ou consultado ao vivo via `get_chart_type_schema`
   se o tipo não estiver cacheado).
2. `add_chart_to_existing_dashboard` para adicionar o chart criado a um dashboard
   já existente — **ou** `generate_dashboard` (com a lista de chart IDs criados
   nesta rodada) apenas se for a primeira leva de charts de um dashboard novo.
   `generate_dashboard` nunca é usado como fallback de
   `add_chart_to_existing_dashboard`.

Ao final, a skill lista os IDs/links dos charts e do dashboard criados/atualizados,
e qualquer erro de criação é reportado por componente (um componente falhar não
deve impedir a tentativa dos demais, mas todos os resultados — sucesso e falha —
precisam aparecer no resumo final).

## Cache de schema do Superset (`references/superset-schema.md`)

Para o planejamento (Fases 0–3) não depender de uma chamada ao vivo ao MCP a cada
uso, o schema de cada `viz_type` relevante é consultado uma vez durante a
implementação desta skill (`get_chart_type_schema` para `xy`, `table`, `pie`,
`pivot_table`, `mixed_timeseries`, e qualquer outro tipo confirmado na lista
completa — o handoff registrou pelo menos um tipo cujo nome veio cortado numa
resposta anterior) e salvo como arquivo de referência estático. O MCP só é chamado
ao vivo nas Fases 1 (leitura de dataset) e 4 (criação), e como fallback na Fase 4
se aparecer um `viz_type` ainda não cacheado.

Descobrir a lista completa de `viz_type` válidos faz parte do trabalho de
implementação (uma chamada com `chart_type` inválido de propósito tende a devolver
a lista completa no erro, conforme observado no handoff).

## Guia de design (`references/diretrizes-dashboard.md`)

Resumo curado do `markdowm-devs.md`, focado no que a Fase 0/2 realmente usa: perfil
de usuário (cap. 2.1), hierarquia de informação e densidade visual (cap. 2.2),
contexto de uso (cap. 2.3), cores institucionais/neutras/semânticas (cap. 4) e
tipografia/hierarquia (cap. 3.2).

**Ressalva registrada explicitamente na skill**: os capítulos do guia mais
específicos de dashboard — 13 (Estruturação de Dashboards), 14 (Tabelas), boa parte
do 15 (Catálogo de Componentes) e 4.5 (Cores para Visualização de Dados) — estão,
na versão atual do `markdowm-devs.md`, só com os títulos das subseções, sem
conteúdo escrito. A skill não deve inventar conteúdo para preencher essas lacunas:
nesses pontos ela se apoia nos princípios gerais que **estão** completos (hierarquia
de informação, densidade visual, cores semânticas, contraste, tipografia) e, quando
uma decisão de fato dependeria de uma diretriz específica ainda não escrita (ex.:
regra exata de cor por tipo de gráfico do cap. 4.5), sinaliza isso no esboço em vez
de decidir sozinha.

## Segurança do token Superset

O token Superset (Bearer JWT) não entra em nenhum arquivo da skill nem do
repositório. A skill assume que o MCP já está conectado na sessão (configurado via
`claude mcp add`, com o token em variável de ambiente/secret manager) e apenas
verifica a conexão no início da Fase 0. Como trabalho de implementação avulso
(não faz parte do conteúdo da skill em si): adicionar `.env` e `.token` ao
`.gitignore` deste repositório, já que ambos existem hoje na raiz sem estar
versionados por sorte, não por proteção.

## Estrutura de arquivos e integração ao repositório

```
01-govhub/dashboard-superset-builder/
├── SKILL.md
└── references/
    ├── diretrizes-dashboard.md      # resumo curado do markdowm-devs.md
    └── superset-schema.md           # schema real cacheado por viz_type
```

- Registrada em `01-govhub/.claude-plugin/plugin.json` (lista `skills`).
- `scripts/atualizar-manifestos.py` roda ao final para regenerar
  `.claude-plugin/marketplace.json` e manter a contagem de skills do `README.md`
  coerente.
- Categoria escolhida (`01-govhub`) por ser específica do stack GovHub/Superset,
  mesma categoria da `govhub-pipeline-guide`.

## Testes / verificação

Não há suite de testes automatizada neste repositório de skills (é conteúdo
markdown, não código executável) — a verificação é funcional:

1. `scripts/validar-plugins.sh` deve passar depois de registrar a skill no
   `plugin.json` (confere coerência entre manifestos e pastas).
2. Uma execução manual ponta a ponta da skill (Fase 0 a 4) contra o Superset real,
   usando um dataset de teste, confirmando que:
   - o esboço gerado usa nomes de campo que batem com o schema cacheado;
   - o gate da Fase 3 de fato bloqueia a Fase 4 sem aprovação explícita;
   - o chart e o dashboard aparecem no Superset com os dados esperados.
