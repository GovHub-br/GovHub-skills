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
decide o design do dashboard — isso é do núcleo. Ela responde por duas coisas:
descobrir o que existe, e depois criar o que foi aprovado.

**Nenhum subcomando de escrita (`create-chart`, `create-dashboard`,
`add-chart-to-dashboard`) roda antes de uma aprovação humana explícita.** Barreira
dura, sem exceção, nos dois modos de uso:

- **Chamado pelo núcleo `dashboard-builder`:** a aprovação é o gate da Fase 3
  dele. Só avance para a Fase 4 depois que o núcleo confirmar que passou.
- **Chamado direto, sem o núcleo** (ex.: "cria um chart no Superset"): *você* é o
  gate. Antes de qualquer escrita, mostre ao dev exatamente o que será criado ou
  alterado — nome, dataset, tipo de visualização e o dashboard alvo — e peça
  aprovação explícita. Uma resposta vaga ("ok", "bacana", silêncio) **não** conta
  como aprovação; peça confirmação direta. Use `--dry-run` para mostrar o efeito
  real antes de perguntar.

Todas as chamadas passam por `scripts/superset_client.py`. **Não monte `curl` à
mão** e não invente endpoints: o script já encapsula autenticação, paginação e as
armadilhas documentadas em
[`references/superset-api.md`](references/superset-api.md).

Os caminhos dos comandos abaixo (`scripts/…`, `references/…`) são **relativos ao
diretório desta skill**, não ao cwd do agente — que costuma ser a raiz do repo.
Rode a partir do diretório da skill ou prefixe o caminho dela.

## Pré-requisitos

O script precisa de `requests` e das credenciais no ambiente:

```bash
python3 -c "import requests" || pip install requests
# SUPERSET_URL, SUPERSET_USERNAME, SUPERSET_PASSWORD no ambiente ou .env local
```

Se faltar variável, o script sai com a lista do que falta. **Nunca** coloque
credenciais em arquivo versionado — peça ao dev que exporte no ambiente.

Se você mexeu no `superset_client.py`, rode o ciclo real antes de confiar nele:

```bash
python3 scripts/superset_client.py smoke --dataset <id de qualquer dataset>
```

Ele cria um chart e um dashboard descartáveis, confere que os dados voltam e que
a associação existe, e apaga tudo. O `--dataset` precisa apontar para um dataset
com ao menos uma linha e uma coluna — sem isso a smoke não tem como provar que um
filtro aplicou, e ela mesma avisa que não conseguiu. Os testes de
`test_superset_client.py` são todos mockados — foi assim que quatro defeitos
chegaram a um Superset real.

## Fase 0-conector — perguntas específicas do Superset

1. **Dataset alvo**, se já existir (nome ou ID). Se o dev não souber, a Fase 1
   lista os candidatos.
2. **De onde vem o dashboard?** A resposta vira a linha `dashboard alvo:` do
   esboço, e ela tem exatamente três formas — escreva **verbatim**, do jeito que
   a seção "Vocabulário compartilhado" do núcleo declara; variar a grafia quebra
   o gate em silêncio:
   - `novo: "<título>"` — a Fase 4 cria com `create-dashboard`.
   - `existente: <slug ou id>` — a Fase 4 usa `add-chart-to-dashboard`.
   - `novo a partir de: <slug ou id do fonte> → "<título novo>"` — a Fase 1b lê o
     dashboard fonte antes, e a Fase 4 cria um dashboard **novo** (o fonte nunca
     é tocado).

   O identificador é **slug ou id**, nunca uuid ou título: `get-dashboard`
   resolve só esses dois, e um uuid dá 404 — lido como "não existe".

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

Roda só quando o `dashboard alvo:` é `novo a partir de:`.
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

Só depois da aprovação explícita: o gate da Fase 3 do núcleo quando chamado por
ele, ou o seu próprio gate quando chamado direto, sem o núcleo (barreira no
topo desta skill).

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

   Os campos de `params` são o `form_data` nativo do Superset e mudam com o
   `viz_type` (ex.: pizza usa `groupby` + `metric`; tabela usa `groupby`/
   `all_columns`). Para saber a forma de `params` de um `viz_type`, leia um chart
   existente daquele tipo com `get-chart` e use o `params` dele como referência —
   a API REST não publica schema por `viz_type` (ver
   [`references/superset-api.md`](references/superset-api.md)). Filtro entra como
   `adhoc_filters`, no formato que o chart de referência mostrar; não escreva SQL
   cru.

   `create-chart` **recusa** um `viz_type` que não saiba transformar em
   `query_context` e lista no erro os que aceita. É de propósito: um tipo sem a
   derivação verificada geraria uma query silenciosamente errada. Para liberar um
   tipo novo, confira a forma real dele contra um chart existente daquele tipo
   (`get-chart`) e verifique a derivação antes de ampliar a lista — não contorne
   o erro.

2. Crie o chart (idempotente — rodar de novo não duplica):

   ```bash
   # re-derivando de um fonte:
   python3 scripts/superset_client.py create-chart --file componente.json --fonte <slug ou id>

   # dashboard novo do zero, sem fonte:
   python3 scripts/superset_client.py create-chart --file componente.json
   ```

   `--fonte` é **obrigatório** quando o `dashboard alvo:` é `novo a partir de:`.
   A idempotência casa por `slice_name` + `datasource_id`, e re-derivar propõe
   nomes parecidos com os do fonte: sem `--fonte`, um nome repetido atualiza o
   chart do fonte e altera por dentro o dashboard que prometemos não tocar —
   corrupção silenciosa, ninguém é avisado. Com ele, o comando recusa
   (`recusado_e_do_fonte`) em vez de escrever.

   A resposta traz `acao`, o `id` e — quando houve escrita — `verificacao`, com o
   que o chart devolve de verdade:

   ```json
   {"acao": "criado", "id": 355, "slice_name": "…",
    "verificacao": {"rowcount": 1, "amostra": {"UHs Contratadas": 131499}}}
   ```

   **Compare a amostra com o que você esperava.** Ela mostra o número que saiu,
   não se ele está certo — é instrumentação, não oráculo. Um filtro que não pegou
   costuma aparecer como um valor grande demais (uma soma que dobrou, por
   exemplo). Se `verificacao` trouxer `erro`, o chart foi criado mesmo assim:
   confira à mão antes de seguir.

   "O mesmo chart" é `slice_name` **mais** `datasource_id`: um chart homônimo
   sobre outro dataset é criado como novo, nunca sobrescrito.

3. Ligue os charts ao dashboard, conforme o `dashboard alvo:`:

   ```bash
   # dashboard alvo: novo: "<título>"
   python3 scripts/superset_client.py create-dashboard --file dashboard.json
   # onde dashboard.json = {"payload": {"dashboard_title": "...", "slug": "...",
   #                                     "published": true}, "chart_ids": [1, 2]}

   # dashboard alvo: novo a partir de: <slug ou id do fonte> → "<título novo>"
   python3 scripts/superset_client.py create-dashboard --file dashboard.json \
       --fonte <slug ou id do fonte>

   # dashboard alvo: existente: <slug ou id> — um chart por vez
   python3 scripts/superset_client.py add-chart-to-dashboard <slug ou id> <chart_id>
   ```

   `slug` é **obrigatório** dentro de `payload`: a listagem do Superset omite
   dashboards, então sem slug não há como decidir existência e cada execução
   criaria uma cópia. Sem ele o comando falha alto.

   `--fonte` é **obrigatório** quando o `dashboard alvo:` é `novo a partir de:`.
   Nada além dele distingue o dashboard novo do fonte: se o slug ou o título
   derivado coincidir com o do fonte — movimento natural ao re-derivar — o
   comando reescreveria o fonte. Com `--fonte`, ele recusa
   (`recusado_e_o_fonte`) em vez de escrever.

Use `--dry-run` primeiro se quiser mostrar ao dev o que mudaria — ele lê de
verdade e só pula a escrita.

### Os valores de `acao` na resposta

Toda resposta devolve `acao`; `id` vem junto sempre que o objeto existe (nos
caminhos de `--dry-run` que ainda iam criar, e em `chart_nao_encontrado` /
`dashboard_nao_encontrado`, ele vem `null` — não há id para dar). Uma escrita de
chart traz também `verificacao`. O que fazer com cada valor:

| `acao` | quando aparece | o que fazer |
|---|---|---|
| `criado` | chart ou dashboard novo, escrito | siga; use o `id` no resumo. Numa escrita de chart, confira a `verificacao` |
| `atualizado` | já existia, o conteúdo mudou, foi reescrito | siga; use o `id`. Numa escrita de chart, confira a `verificacao` |
| `adicionado` | `add-chart-to-dashboard` inseriu o chart no layout publicado **e** o associou ao dashboard | siga; use o `id` |
| `associado` | o dashboard já tinha o layout certo mas os charts não estavam anexados — o run reparou isso. **É escrita bem-sucedida**, não no-op: o dashboard abria em branco e agora não | siga; use o `id` |
| `inalterado` | já estava exatamente como pedido | siga, nada a fazer |
| `criaria` / `atualizaria` / `adicionaria` / `associaria` | só `--dry-run`: anuncia a escrita (ou o reparo) que faria | rode de novo sem `--dry-run` depois da aprovação |
| `recusado_e_do_fonte` | o chart achado por (nome + dataset) pertence ao dashboard passado em `--fonte`. Nada foi escrito | renomeie o componente — prefixar com o nome do dashboard novo resolve — e rode de novo |
| `recusado_e_o_fonte` | o alvo e o `--fonte` resolveram no **mesmo** dashboard: escrever reescreveria o fonte. Nada foi escrito | escolha slug e título distintos do fonte e rode de novo |
| `chart_nao_encontrado` | algum `chart_id` passado não existe. Nada foi escrito | confira o `id` que a etapa 2 devolveu; não invente |
| `dashboard_nao_encontrado` | o slug/id do `add-chart-to-dashboard` não existe. Nada foi escrito | confira o `dashboard alvo:` com o dev |
| `layout_invalido` | o `position_json` publicado do dashboard é ilegível. Nada foi escrito | não dá para preservar o que não dá para ler; devolva ao dev |
| `layout_sem_lugar_para_row` | o layout publicado não tem GRID nem TAB onde pendurar uma linha. Nada foi escrito | inserir exigiria descartar o conteúdo publicado, fora de escopo; devolva ao dev |

As seis últimas linhas — os dois `recusado_*`, os dois `*_nao_encontrado` e os
dois `layout_*` — **não** são sucesso: registre e devolva ao dev, não tente
contornar. `recusado_e_do_fonte` (o chart pertence ao fonte) e
`recusado_e_o_fonte` (o dashboard **é** o fonte) são casos distintos.

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
