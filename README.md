# GovHub-skills

Coleção curada de **skills do Claude Code** úteis para o trabalho do **GovHub BR / lablivre** — engenharia de dados governamentais, relatórios oficiais e o stack de pipelines (Airflow + dbt + Postgres, containerizado), além de backend Python/API, infra, qualidade de código e documentação.

O repositório é também um **marketplace de plugins do Claude Code**: instala com um comando e atualiza com outro, sem copiar arquivo.

```bash
claude plugin marketplace add GovHub-br/GovHub-skills
claude plugin install govhub-skills@govhub
```

## O que é uma skill?

Uma **skill** é um pacote de conhecimento e instruções que o Claude carrega **sob demanda** para executar bem uma tarefa específica. Na prática, é uma pasta com um arquivo `SKILL.md` (e, opcionalmente, scripts, templates e arquivos de referência).

O `SKILL.md` tem duas partes:

- Um cabeçalho (frontmatter YAML) com `name` e `description`. A `description` diz **quando** a skill deve ser usada — é por ela que o Claude decide, sozinho, acionar a skill no momento certo.
- O corpo, em Markdown, com as instruções, boas práticas e passo a passo que o Claude segue quando a skill é ativada.

```
minha-skill/
├── SKILL.md          ← obrigatório (frontmatter + instruções)
├── scripts/          ← opcional (código auxiliar)
└── references/       ← opcional (docs de apoio)
```

A vantagem é que o conhecimento fica fora do contexto até ser necessário: o Claude só carrega a skill inteira quando a tarefa combina com a `description`. Isso mantém o contexto enxuto e as respostas consistentes com o padrão do time.

## Como instalar

Este repositório é um **marketplace de plugins do Claude Code**. Você não precisa copiar pasta nenhuma: registra o marketplace uma vez e instala o que quiser por comando.

**1. Registre o marketplace** (só na primeira vez):

```bash
claude plugin marketplace add GovHub-br/GovHub-skills
```

**2. Instale tudo de uma vez:**

```bash
claude plugin install govhub-skills@govhub
```

**Ou instale só as categorias que interessam:**

```bash
claude plugin install govhub-core@govhub
```

| Plugin | O que traz | Skills |
|--------|-----------|--------|
| `govhub-skills` | **Tudo** — as 52 skills de todas as categorias | 52 |
| `govhub-core` | [01 · Específicas do GovHub](#01--específicas-do-govhub) — pipelines, identidade visual, prestação de contas | 3 |
| `govhub-dados` | [02 · Dados & Bancos](#02--dados--bancos) — Postgres, SQL, BigQuery, Jupyter | 9 |
| `govhub-backend` | [03 · Backend / Python / APIs](#03--backend--python--apis) — Python, FastAPI, design e segurança de API | 6 |
| `govhub-infra` | [04 · Infra / DevOps](#04--infra--devops--observabilidade) — Docker, CI/CD, Prometheus, Grafana | 8 |
| `govhub-qualidade` | [05 · Qualidade & arquitetura](#05--qualidade-testes--arquitetura) — TDD, debug, clean code, ADR, segurança | 18 |
| `govhub-docs` | [06 · Docs & relatórios](#06--documentação-relatórios--escritório) — planilhas, PDF, changelog, README, Mermaid | 7 |
| `govhub-lablivre` | [07 · Lab Livre](#07--lab-livre) — identidade visual do Lab Livre, mesma arquitetura da do Gov Hub | 1 |

> Instale **o `govhub-skills` ou os plugins por categoria** — não os dois, senão as mesmas skills entram duas vezes.

Dentro de uma sessão do Claude Code dá para fazer o mesmo pelo comando `/plugin`, que abre o navegador de marketplaces e mostra as skills de cada plugin antes de instalar.

**Manter atualizado** — os plugins não declaram `version` de propósito: o Claude Code usa o commit do repositório como versão, então **todo push na `main` é uma atualização** (skill nova ou skill editada). Para receber:

```bash
claude plugin marketplace update govhub   # baixa o commit mais novo
claude plugin update govhub-core@govhub   # aplica ao plugin instalado (ou govhub-skills@govhub)
```

Dentro de uma sessão, `/plugin marketplace update` e `/plugin update` fazem o mesmo, e o Claude Code também checa o marketplace em segundo plano. Depois de atualizar, reinicie a sessão (ou `/reload-plugins`) para ele reler as skills.

**Quem edita as skills** (mantenedores): não instale o plugin na sua máquina; aponte um symlink de `~/.claude/skills/` para a pasta da skill no seu clone. Cada edição vale na próxima sessão, sem commit nem update (registrar o clone como marketplace local não serve: por ser um repositório git, o Claude Code copia o plugin para o cache e o prende ao commit):

```bash
ln -s ~/GovHub-skills/01-govhub/govhub-visual-identity ~/.claude/skills/govhub-visual-identity
```

Não tenha a mesma skill instalada por plugin **e** em `~/.claude/skills/`, senão ela entra duas vezes. Para conferir o que entrou (e quanto custa de contexto):

```bash
claude plugin details govhub-skills@govhub
```

<details>
<summary>Prefere não usar plugin? Dá para copiar as pastas na mão</summary>

Cada skill é autocontida, então copiar a pasta dela para `~/.claude/skills/` também funciona:

```bash
cp -r 02-dados-e-bancos/pdf-postgres-extractor ~/.claude/skills/
```

O Claude Code procura as skills diretamente em `~/.claude/skills/<nome-da-skill>/`, sem os prefixos de categoria (`01-`, `02-`…) — por isso se copia a pasta da skill, e não a da categoria. A desvantagem em relação ao plugin é que a atualização passa a ser manual.

</details>

## Como usar (acionar) uma skill

Você **não precisa** chamar a skill pelo nome. Depois de instalada, o Claude a aciona automaticamente quando o seu pedido casa com a `description` dela. Exemplos:

- *"cria uma DAG nova pra ingerir dados do SIAPE"* → dispara a `govhub-pipeline-guide`.
- *"extrai os CNPJs desse PDF e joga no banco"* → dispara a `pdf-postgres-extractor`.
- *"gera o relatório de prestação de contas do último ano"* → dispara a `accountability-report`.

Se quiser **forçar** o uso de uma skill, é só citá-la: *"use a skill `sql-pro` para otimizar essa query"*.

## Como criar ou editar uma skill

Existe uma skill dedicada a isso — a `skill-creator` (disponível na coleção geral). Você também pode criar manualmente: basta uma pasta com um `SKILL.md` contendo o frontmatter (`name`, `description`) e as instruções no corpo. O ponto mais importante é escrever uma `description` clara e específica, listando os gatilhos ("use quando o usuário pedir X, Y, Z"), porque é ela que determina se a skill será acionada na hora certa.

**Ao contribuir uma skill nova para este repositório**, três coisas precisam bater, senão ela não é carregada pelo plugin:

1. O `name:` do frontmatter tem que ser **idêntico ao nome da pasta**, em `kebab-case` minúsculo (`postgres-schema-design`, não `Postgres Schema Design`).
2. A pasta entra dentro de uma das categorias `NN-...`, e os manifestos precisam ser regerados para incluí-la (isso atualiza o `plugin.json` da categoria e o da raiz de uma vez):

```bash
./scripts/atualizar-manifestos.py
```

3. Rode o validador antes de abrir o PR — ele confere frontmatter, pastas e manifestos, e falha se alguma skill ficou de fora:

```bash
./scripts/validar-plugins.sh
```

**Se a skill veio de fora**, registre a procedência: `author:` e `license:` no frontmatter, o arquivo de licença original junto na pasta quando existir, e uma linha no [`NOTICE.md`](NOTICE.md). Skill de terceiro sem licença conhecida não deveria entrar — veja abaixo por quê.

## Licenças

Este repositório **reúne** skills de origens diferentes e por isso **não tem um `LICENSE` na raiz**: uma licença única seria o GovHub licenciando código que não é dele. O [`NOTICE.md`](NOTICE.md) registra o que se sabe sobre cada skill — hoje 8 têm licença ou autoria identificada e 43 ainda não. É uma dívida conhecida, não um descuido.

---

As skills abaixo estão organizadas em pastas por categoria.

## 01 · Específicas do GovHub

| Skill | O que faz |
|-------|-----------|
| [`govhub-pipeline-guide`](01-govhub/govhub-pipeline-guide/) | Implementar uma nova fonte de dados no Gov Hub BR — DAG Airflow, cliente de API, transformações dbt (bronze → silver → gold), testes e PR. Cobre SIAPE, SIAFI, SICONV, TransfereGov, IBGE, PNCP. |
| [`govhub-visual-identity`](01-govhub/govhub-visual-identity/) | Aplica a identidade visual oficial do Gov Hub (gov-hub.io) em relatórios e PDFs, slides, posts, dashboards e temas CSS. Roxo `#613EFF`, navy `#0A005A`. |
| [`accountability-report`](01-govhub/accountability-report/) | Relatório de prestação de contas de um repositório a partir do git. Saída em Markdown, HTML e PDF A4 pronto para entrega oficial. |

## 02 · Dados & Bancos

| Skill | O que faz |
|-------|-----------|
| [`data-engineer`](02-dados-e-bancos/data-engineer/) | Persona de engenharia de dados — pipelines, ETL/ELT, modelagem dimensional, qualidade de dados, orquestração. |
| [`data-scientist`](02-dados-e-bancos/data-scientist/) | Analytics avançada, machine learning, modelagem estatística e BI. |
| [`bigquery-basics`](02-dados-e-bancos/bigquery-basics/) | Datasets, tabelas e jobs no BigQuery + BigQuery ML. |
| [`sql-pro`](02-dados-e-bancos/sql-pro/) | SQL avançado, OLTP/OLAP, tuning de queries e modelagem. |
| [`postgres-best-practices`](02-dados-e-bancos/postgres-best-practices/) | Boas práticas de PostgreSQL — modelagem, tipos, índices, queries, transações. |
| [`postgresql-optimization`](02-dados-e-bancos/postgresql-optimization/) | Otimização de PostgreSQL — `EXPLAIN`/`ANALYZE`, índices, queries lentas, vacuum. |
| [`postgres-schema-design`](02-dados-e-bancos/postgres-schema-design/) | Design de schema — normalização, constraints, particionamento. |
| [`jupyter-notebook`](02-dados-e-bancos/jupyter-notebook/) | Criar e editar notebooks Jupyter (.ipynb) para exploração e análise de dados. |
| [`pdf-postgres-extractor`](02-dados-e-bancos/pdf-postgres-extractor/) | Extrai dados estruturados de PDFs (CNPJ, datas, valores) e grava no PostgreSQL. |

## 03 · Backend / Python / APIs

| Skill | O que faz |
|-------|-----------|
| [`python-pro`](03-backend-apis/python-pro/) | Python 3.12+ — async, uv, ruff, pydantic, boas práticas de produção. |
| [`fastapi-pro`](03-backend-apis/fastapi-pro/) | APIs async com FastAPI, SQLAlchemy 2.0 e Pydantic V2. |
| [`api-design-principles`](03-backend-apis/api-design-principles/) | Princípios de design de APIs REST e GraphQL. |
| [`api-documentation-generator`](03-backend-apis/api-documentation-generator/) | Gera documentação de API a partir do código. |
| [`api-integration-specialist`](03-backend-apis/api-integration-specialist/) | Integrar APIs de terceiros com auth, retry, rate limiting e webhooks. |
| [`api-security-best-practices`](03-backend-apis/api-security-best-practices/) | Design seguro de API — auth, autorização, validação de input, proteção contra vulnerabilidades. |

## 04 · Infra / DevOps / Observabilidade

| Skill | O que faz |
|-------|-----------|
| [`devops-iac-engineer`](04-infra-devops/devops-iac-engineer/) | Infra como código, CI/CD, observabilidade e práticas SRE. |
| [`github-actions-creator`](04-infra-devops/github-actions-creator/) | Cria workflows CI/CD — testes, deploy, lint, security scanning, Docker builds. |
| [`docker-expert`](04-infra-devops/docker-expert/) | Docker — Dockerfiles, docker-compose, multi-stage builds, networking. |
| [`grafana-dashboards`](04-infra-devops/grafana-dashboards/) | Dashboards Grafana de observabilidade. |
| [`prometheus-configuration`](04-infra-devops/prometheus-configuration/) | Setup Prometheus — métricas, scrape, recording rules. |
| [`observability-engineer`](04-infra-devops/observability-engineer/) | Estratégia de monitoring, logging e tracing — SLI/SLO e resposta a incidentes. |
| [`bash-pro`](04-infra-devops/bash-pro/) | Bash defensivo para automação de produção, CI/CD e utilitários de sistema. |
| [`linux-shell-scripting`](04-infra-devops/linux-shell-scripting/) | Scripts bash para automação Linux — monitoramento, backup, gestão de usuários. |

## 05 · Qualidade, testes & arquitetura

| Skill | O que faz |
|-------|-----------|
| [`python-testing-patterns`](05-qualidade-testes/python-testing-patterns/) | pytest, fixtures, mocking e TDD em Python. |
| [`systematic-debugging`](05-qualidade-testes/systematic-debugging/) | Método sistemático de debug antes de propor correções. |
| [`clean-code`](05-qualidade-testes/clean-code/) | Padrões de código pragmáticos, sem over-engineering. |
| [`code-simplifier`](05-qualidade-testes/code-simplifier/) | Refatora para clareza preservando o comportamento. |
| [`architecture-decision-records`](05-qualidade-testes/architecture-decision-records/) | Criar e manter ADRs — registro de decisões técnicas. |
| [`security-best-practices`](05-qualidade-testes/security-best-practices/) | Review de segurança por linguagem/framework. |
| [`secrets-management`](05-qualidade-testes/secrets-management/) | Gestão de segredos em CI/CD (Vault, AWS Secrets Manager). |
| [`lint-and-validate`](05-qualidade-testes/lint-and-validate/) | Controle de qualidade automático — linting e análise estática após cada modificação. |
| [`dependency-updater`](05-qualidade-testes/dependency-updater/) | Gestão de dependências multi-linguagem — updates seguros e diagnóstico de conflitos. |
| [`commit-smart`](05-qualidade-testes/commit-smart/) | Commits semânticos (conventional) com contexto do "porquê", detectando tipo/escopo do diff. |
| [`tdd`](05-qualidade-testes/tdd/) | Test-driven development com ciclo red-green-refactor. |
| [`test-fixing`](05-qualidade-testes/test-fixing/) | Roda testes e corrige falhas sistematicamente com agrupamento de erros. |
| [`performance-profiling`](05-qualidade-testes/performance-profiling/) | Medição, análise e otimização de performance. |
| [`k6-load-testing`](05-qualidade-testes/k6-load-testing/) | Load testing de APIs com k6 — cenários realistas e integração com CI/CD. |
| [`software-architecture`](05-qualidade-testes/software-architecture/) | Arquitetura de software focada em qualidade e análise de código. |
| [`architecture-patterns`](05-qualidade-testes/architecture-patterns/) | Clean Architecture, Hexagonal Architecture e DDD para sistemas manuteníveis. |
| [`domain-driven-design`](05-qualidade-testes/domain-driven-design/) | DDD — modelagem estratégica, implementação tática e arquitetura orientada a eventos. |
| [`security-compliance`](05-qualidade-testes/security-compliance/) | Defense-in-depth e compliance (SOC2, ISO27001, GDPR/LGPD) para o setor. |

## 06 · Documentação, relatórios & escritório

| Skill | O que faz |
|-------|-----------|
| [`crafting-effective-readmes`](06-docs-relatorios/crafting-effective-readmes/) | READMEs eficazes por tipo de projeto e audiência. |
| [`mermaid-diagram-specialist`](06-docs-relatorios/mermaid-diagram-specialist/) | Diagramas Mermaid — fluxos, sequência, ERDs, arquitetura. |
| [`changelog-generator`](06-docs-relatorios/changelog-generator/) | Gera changelog a partir do histórico de commits. |
| [`to-issues`](06-docs-relatorios/to-issues/) | Quebra um plano/PRD em issues no tracker do projeto. |
| [`web-to-markdown`](06-docs-relatorios/web-to-markdown/) | Converte páginas web (URLs) em Markdown limpo — útil para extrair conteúdo de fontes gov. |
| [`pdf-processing-pro`](06-docs-relatorios/pdf-processing-pro/) | PDF em produção — forms, tabelas, OCR, validação e operações em lote. |
| [`spreadsheet`](06-docs-relatorios/spreadsheet/) | Criar/editar/analisar planilhas via Python (openpyxl, pandas) com fórmulas. |

## 07 · Lab Livre

| Skill | O que faz |
|-------|-----------|
| [`lablivre-visual-identity`](07-lablivre/lablivre-visual-identity/) | Aplica a identidade visual oficial do Lab Livre (UnB) em relatórios e PDFs, slides, posts, dashboards e temas CSS. Cópia da `govhub-visual-identity` com a paleta do Lab Livre (roxo `#7023E8`, azul profundo `#080056`); assets do CDN ainda nas cores do Gov Hub. |

> **Word, Excel, PowerPoint e PDF:** as skills `docx`, `xlsx` e `pdf` não estão aqui — são proprietárias da Anthropic e não podem ser redistribuídas por terceiros (ver [`NOTICE.md`](NOTICE.md)). Elas vêm da fonte oficial:
>
> ```bash
> claude plugin marketplace add anthropics/skills
> claude plugin install document-skills@anthropic-agent-skills
> ```
