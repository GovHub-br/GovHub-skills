# Arquitetura em blocos e mapa de schemas

Duas famílias que não têm "fluxo" no sentido de sequência: mostram **o que
existe e como se conecta**. Exemplos de referência: Figura 3 (arquitetura do
Data Lakehouse) e Figura 8 (schemas do banco) do 3º Relatório Parcial MinC.

## A. Arquitetura em blocos (template `arquitetura-blocos.html`)

Quando usar: componentes de infraestrutura/software agrupados por função,
com setas tipadas entre eles (execução, dados, metadados, governança).

### Gramática

| Elemento | Marcação | Regra |
|---|---|---|
| Zona | `<section class="zone">` com `<span class="pill">NOME</span>` | Agrupa componentes por função (ex.: "Orquestração e armazenamento"). `zone--dashed` para o que ainda não existe ou é lógico. Máximo 3 zonas. |
| Componente | `<div class="node" id="x">` com `<span class="pill">N. PAPEL</span>`, `<h3>Nome real</h3>`, `<p>o que é</p>` e uma descrição do que faz | Numere as pílulas na ordem de leitura. Nome real do software (Airflow, MinIO, Trino), nunca genérico. |
| Sub-bloco | `.node` dentro de `.node` (ex.: formato de tabela dentro do armazenamento) | Só um nível de aninhamento. |
| Status | `<span class="note"><strong>implantado</strong></span>` ou `<strong>previsto</strong> — pendente` | Sempre que o diagrama misturar o que existe e o que é proposto, marque cada um. |
| Seta | `#arrows` com `type` em `exec` (orquestra), `data` (transfere dados), `meta` (consulta metadados), `flow` (leitura/resultado), `gov` (governança) | Toda seta tem um tipo e o tipo aparece na legenda. Rótulo curto na seta quando a relação não for óbvia. |
| Legenda | `<div class="legend">` com um `.item` por tipo de seta usado | Obrigatória. |
| Composição | `<div class="composition">` — barra numerada dos componentes | Opcional; resume "do que é feito" em uma linha. |

### Layout

- Duas colunas (`display:grid`) com a zona de origem à esquerda e a de
  consumo à direita; o dado "anda" da esquerda para a direita.
- Dentro da zona, empilhe os componentes na ordem em que o dado passa por
  eles (`.stack` com `gap` ≥ 52px, para as setas e rótulos caberem).
- Um componente transversal (governança) fica numa coluna lateral, com
  setas `gov` para o que ele controla.

## B. Mapa de schemas / camadas (template `mapa-schemas.html`)

Quando usar: inventário de schemas (ou datasets, buckets, tópicos) de um
mesmo banco, organizado por **papel** (ingestão, legado, saída), com as
convenções ao lado.

### Gramática

| Elemento | Marcação | Regra |
|---|---|---|
| Container | Uma `.zone` com pílula "PostgreSQL · banco X" | O que está dentro pertence ao mesmo banco/instância. |
| Coluna por papel | `<div class="col"><h2>PAPEL</h2>…</div>` | Ingestão ativa · cargas pontuais/legado · saída da transformação. Não organize por camada técnica se o banco é organizado por domínio (regra "schema por domínio"). |
| Schema | `.node` (ingestão ativa), `.node.node--legacy` (pontual/legado), `.node.node--out` (saída) com `<h3>nome_físico</h3><p>conteúdo · frequência</p>` | Nome físico exato, minúsculo. Uma linha de conteúdo e uma de cadência. |
| Convenções | `<div class="conv"><h2>Convenções</h2><dl>…</dl></div>` | Cada convenção = `dt` (nome) + `dd` (uma frase). Só as que valem para o banco inteiro. |
| Seta | Uma única seta `flow` "a transformação consome os schemas de pouso" da coluna de ingestão para a de saída, com `via` na calha entre colunas | Não desenhe uma seta por schema — o detalhe fino vem do lineage do dbt num diagrama de pipeline. |
| Legenda | Três `.swatch`: borda sólida, tracejada, preenchida | Obrigatória. |

### Fonte dos dados

`python3 scripts/dbt_lineage.py target/manifest.json --group schema` devolve
os schemas com seus modelos e a descrição de cada um; use as descrições para
a linha de conteúdo, e o `materialization`/frequência da DAG para a cadência.
Schemas sem produtor no dbt (legado) entram na coluna do meio.

## Checklist (as duas famílias)

- Nome real de cada componente/schema, sem genérico.
- Toda seta tem tipo e o tipo está na legenda.
- Estado (implantado / previsto) marcado quando houver mistura.
- Máximo ~12 nós; acima disso, dois diagramas.
