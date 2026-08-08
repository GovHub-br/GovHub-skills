# Procedência e licenças

Este repositório **reúne** skills do Claude Code de origens diferentes. Ele não é obra única do GovHub BR / lablivre, e por isso **não declara uma licença única na raiz** — cada skill mantém os termos de quem a escreveu.

Este arquivo registra o que se sabe hoje sobre a procedência de cada skill. Ele é incompleto de propósito: o que não foi rastreado está listado abaixo como pendência, e não como se fosse do GovHub.

## Skills com licença identificada

| Skill | Origem | Licença |
|-------|--------|---------|
| [`jupyter-notebook`](02-dados-e-bancos/jupyter-notebook/) | `author: openai` (frontmatter) | Apache-2.0 — [`LICENSE.txt`](02-dados-e-bancos/jupyter-notebook/LICENSE.txt) na pasta |
| [`postgres-schema-design`](02-dados-e-bancos/postgres-schema-design/) | autor não declarado | Apache-2.0 — [`LICENSE.txt`](02-dados-e-bancos/postgres-schema-design/LICENSE.txt) na pasta |
| [`security-best-practices`](05-qualidade-testes/security-best-practices/) | `author: openai` (frontmatter) | Apache-2.0 — [`LICENSE.txt`](05-qualidade-testes/security-best-practices/LICENSE.txt) na pasta |
| [`spreadsheet`](06-docs-relatorios/spreadsheet/) | `author: openai` (frontmatter) | Apache-2.0 — [`LICENSE.txt`](06-docs-relatorios/spreadsheet/LICENSE.txt) na pasta |
| [`postgres-best-practices`](02-dados-e-bancos/postgres-best-practices/) | `author: supabase` (frontmatter) | MIT — declarada no frontmatter |
| [`dependency-updater`](05-qualidade-testes/dependency-updater/) | autor não declarado | MIT — declarada no frontmatter |

## Skills com autor conhecido, mas licença não declarada

Estas trazem `author:` no frontmatter e nenhuma licença. Precisam ser rastreadas até o repositório de origem para confirmar sob que termos podem ser redistribuídas.

| Skill | `author:` |
|-------|-----------|
| [`linux-shell-scripting`](04-infra-devops/linux-shell-scripting/) | `zebbern` |
| [`k6-load-testing`](05-qualidade-testes/k6-load-testing/) | `Kairo Official` |

## Skills removidas deste repositório

As skills abaixo já estiveram aqui e foram removidas por serem **proprietárias da Anthropic** — o `LICENSE.txt` delas vinculava o uso ao contrato de cada pessoa com a Anthropic, o que não autoriza redistribuição por terceiros.

- `docx`, `xlsx`, `pdf-processing`

Elas não fazem falta: a Anthropic publica as mesmas skills no marketplace oficial dela, no plugin `document-skills` (Word, Excel, PowerPoint e PDF). Use a fonte original em vez de uma cópia:

```bash
claude plugin marketplace add anthropics/skills
```

```bash
claude plugin install document-skills@anthropic-agent-skills
```

## Pendência conhecida

Das 51 skills que restam, **43 não trazem qualquer indicação de origem ou licença**. Elas foram reunidas de coleções públicas da comunidade, mas o repositório de origem não foi registrado no momento em que entraram aqui.

Isso significa que o GovHub **não pode afirmar** sob que termos essas skills estão, nem relicenciá-las. Enquanto a procedência não for rastreada:

- não adicione um `LICENSE` na raiz declarando uma licença única para o repositório;
- ao trazer uma skill nova de fora, registre no frontmatter o `author:` e a `license:`, e traga o arquivo de licença original junto quando existir;
- ao escrever uma skill própria do GovHub, deixe isso explícito no frontmatter — é o que separa o que é do time do que foi apenas reunido aqui.

Skills escritas pelo próprio GovHub BR / lablivre (as de [`01-govhub/`](01-govhub/), por exemplo) são do time e podem ser licenciadas por ele a qualquer momento.
