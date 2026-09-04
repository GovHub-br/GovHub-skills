---
name: dashboard-superset-builder
description: >-
  Conector Superset para a skill dashboard-builder: descobre datasets, colunas e
  métricas reais, lê dashboards existentes (inclusive para re-derivar um novo a
  partir de um dashboard fonte), e cria charts e dashboards de verdade via API
  REST do Superset. Use quando a ferramenta de BI escolhida for o Superset, ou
  quando o usuário pedir para "criar um chart no Superset", "publicar um dashboard
  no Superset", "ler um dashboard do Superset" ou "adicionar um chart a um
  dashboard do Superset".
---

# Conector Superset

Esta skill é o **braço de execução** da skill
[`dashboard-builder`](../dashboard-builder/SKILL.md) para o Superset. Ela não
decide o design do dashboard — isso é do núcleo. Ela responde por três coisas:
descobrir o que existe, e depois criar o que foi aprovado.

**Nenhum subcomando de escrita (`create-chart`, `create-dashboard`,
`add-chart-to-dashboard`) pode ser chamado antes de o núcleo confirmar que a
Fase 3 foi aprovada explicitamente.** Barreira dura, sem exceção.

Todas as chamadas passam por `scripts/superset_client.py`. **Não monte `curl` à
mão** e não invente endpoints: o script já encapsula autenticação, paginação e as
armadilhas documentadas em
[`references/superset-api.md`](references/superset-api.md).

## Pré-requisitos

O script precisa de `requests` e das credenciais no ambiente:

```bash
python3 -c "import requests" || pip install requests
# SUPERSET_URL, SUPERSET_USERNAME, SUPERSET_PASSWORD no ambiente ou .env local
```

Se faltar variável, o script sai com a lista do que falta. **Nunca** coloque
credenciais em arquivo versionado — peça ao dev que exporte no ambiente.

## Fase 0-conector — perguntas específicas do Superset

1. **Dataset alvo**, se já existir (nome ou ID). Se o dev não souber, a Fase 1
   lista os candidatos.
2. **De onde vem o dashboard?**
   - `novo do zero` — a Fase 4 cria com `create-dashboard`.
   - `acrescentar a existente: <slug ou id>` — a Fase 4 usa
     `add-chart-to-dashboard`.
   - `novo a partir do fonte: <slug ou id>` — a Fase 1b lê o dashboard fonte
     antes, e a Fase 4 cria um dashboard **novo** (o fonte nunca é tocado).

Devolva as respostas ao núcleo: elas viram a linha `dashboard alvo:` no cabeçalho
do esboço da Fase 2.

## Fase 1 — Descoberta (somente leitura)

Se o dev indicou um dataset, pegue as colunas e métricas reais:

```bash
python3 scripts/superset_client.py get-dataset <id>
```

Se ele não souber qual usar, liste os candidatos e deixe-o escolher:

```bash
python3 scripts/superset_client.py list-datasets --filtro <parte-do-nome>
```

Use esses nomes reais no esboço, em vez de inventar. Se o dataset ainda não
existe no Superset, avise: criar dataset está **fora do escopo** desta skill, e
a Fase 4 só roda depois que ele existir. Não fique em loop — devolva a pendência
ao dev.

## Fase 1b — Ler o dashboard fonte (somente leitura)

Roda só quando a resposta da Fase 0-conector foi `novo a partir do fonte`.
Somente leitura: **não precisa de aprovação humana** e não escreve no fonte.

1. `python3 scripts/superset_client.py get-dashboard <slug ou id>` → título,
   charts e `position_json`. Se devolver `null`, o dashboard não existe: avise o
   dev e pare.
2. Para cada chart: `python3 scripts/superset_client.py get-chart <id>` →
   recupere `datasource_id`, `viz_type` original, e o `params`/`form_data` com
   métricas, dimensões e filtros.
3. Monte a lista de componentes pré-preenchida para a Fase 2 do núcleo — um
   bloco por chart, com **só os campos de dados** (dataset e o miolo de
   `params`). **Não** preencha `viz_type`, título nem posição: isso a Fase 2
   redecide do zero.
4. Capture o layout do fonte como bloco de referência textual
   `Estado atual do fonte:` — referência ("era assim"), nunca ponto de partida.

Casos de borda — **registre no esboço e siga**, nunca aborte a fase:

- `params` que não mapeia limpo → traga o que der e marque o bloco com
  `# viz_type a escolher` e `# config a confirmar`.
- `get-chart` devolve `null` (chart órfão, sem permissão) → pule o chart, siga
  nos outros, e **liste as falhas** ao fim da fase.
- Filtro em `adhoc_filters` com expressão SQL → não invente equivalente
  estruturado; marque com `# filtro do fonte a reconstruir`.

Um componente com qualquer um desses marcadores **não libera a Fase 4** — o
núcleo resolve antes, no gate.

## Fase 4 — Criação real

Só depois da aprovação explícita da Fase 3 do núcleo.

Para cada componente aprovado, na ordem do esboço:

1. Monte o payload do chart num arquivo JSON. `params` é **string JSON**, e o
   `datasource` de dentro dele repete o id no formato `<id>__table`:

   ```json
   {
     "slice_name": "Consumo Total do Período",
     "viz_type": "table",
     "datasource_id": 42,
     "datasource_type": "table",
     "params": "{\"datasource\":\"42__table\",\"viz_type\":\"table\",\"groupby\":[\"unidade\"],\"metrics\":[\"count\"],\"row_limit\":1000}"
   }
   ```

   Para saber a forma de `params` de um `viz_type`, leia um chart existente
   daquele tipo com `get-chart` e use o `params` dele como referência — a API
   REST não publica schema por `viz_type` (ver
   [`references/superset-api.md`](references/superset-api.md)).

2. Crie o chart (idempotente — rodar de novo não duplica):

   ```bash
   python3 scripts/superset_client.py create-chart --file componente.json
   ```

   A resposta traz `acao` (`criado`, `atualizado` ou `inalterado`) e o `id`.

3. Ligue os charts ao dashboard, conforme o `dashboard alvo:`:

   ```bash
   # novo (inclusive "novo a partir de"):
   python3 scripts/superset_client.py create-dashboard --file dashboard.json
   # onde dashboard.json = {"payload": {"dashboard_title": "...", "slug": "...",
   #                                     "published": true}, "chart_ids": [1, 2]}

   # acrescentar a um existente, um chart por vez:
   python3 scripts/superset_client.py add-chart-to-dashboard <slug ou id> <chart_id>
   ```

Use `--dry-run` primeiro se quiser mostrar ao dev o que mudaria — ele lê de
verdade e só pula a escrita.

Se um componente falhar, registre o erro e continue nos demais. Ao final,
devolva ao núcleo um resumo com o resultado de cada componente (ação, id e link)
e o link do dashboard.

## Fora de escopo

- **Alterar um dashboard existente** além de acrescentar charts — mexer no
  layout publicado, remover chart, mudar título ou filtros nativos. Reescrever o
  `position_json` inteiro apagaria ajustes feitos na interface.
- Criar dataset (físico ou virtual, via SQL) e criar conexão de banco.

## Referências

- [`references/superset-api.md`](references/superset-api.md) — autenticação,
  paginação, ordem de criação, idempotência, `position_json` e as armadilhas da
  API REST do Superset.
- `scripts/superset_client.py` — o cliente que implementa tudo isso.
