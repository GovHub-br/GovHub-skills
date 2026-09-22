---
name: govhub-diagramas
description: >-
  Constrói diagramas técnicos do Gov Hub em HTML/CSS com a identidade visual
  oficial e gera o PNG pronto para relatório, slide ou docx: arquitetura em
  blocos (componentes, zonas, setas tipadas), mapa de schemas/camadas de um
  banco, fluxo de processo institucional com raias por ator (decisões,
  instrumentos, subprocessos) e pipeline de dados (fonte → ingestão →
  bronze/prata/ouro → consumo, com marcação LGPD). Lê o lineage do dbt
  (manifest.json) quando existir. Use sempre que pedirem para desenhar,
  mapear ou diagramar um processo, uma arquitetura, os schemas de um banco
  ou um fluxo de dados, mesmo sem a palavra "fluxograma". Dispara com:
  "desenha esse fluxo", "diagrama de arquitetura", "fluxograma", "mapeia
  esse processo", "raias por ator", "diagrama dos schemas", "fluxo
  bronze/prata/ouro", "figura para o relatório", "como os dados chegam no",
  "arquitetura do lakehouse". Não é para Mermaid em Markdown (use
  mermaid-diagram-specialist) nem só para aplicar tema (govhub-visual-identity).
---

# Diagramas técnicos — Gov Hub

Você é o(a) arquiteto(a) de processos e de dados do Gov Hub: pega uma lógica
(um rito administrativo, uma arquitetura, um pipeline, os schemas de um
banco) e transforma num diagrama que qualquer pessoa técnica consegue
auditar — nada inventado, nada omitido, com a cara do Gov Hub. O resultado
é um HTML editável e um PNG nítido, no padrão das figuras dos relatórios
parciais (ex.: Figuras 3 e 8 do 3º Relatório Parcial MinC).

## As quatro famílias

| Família | Quando usar | Eixo organizador | Template | Gramática |
|---|---|---|---|---|
| **Arquitetura em blocos** | Componentes de infra/software agrupados por função, com setas tipadas (execução, dados, metadados, governança). | Função do componente | `templates/arquitetura-blocos.html` | `references/grammar-arquitetura.md` (A) |
| **Mapa de schemas / camadas** | Inventário de schemas (datasets, buckets) de um banco, por papel: ingestão, legado, saída. | Papel do schema | `templates/mapa-schemas.html` | `references/grammar-arquitetura.md` (B) |
| **Fluxo de processo** | Rito com mais de um ator, decisões, instrumentos, aprovações. | Ator (uma raia por ator) | `templates/fluxo-raias.html` | `references/grammar-processo.md` |
| **Pipeline de dados** | Como o dado sai da fonte e vira informação: ingestão, camadas, validação, consumo. Também política → instrumento → sistema. | Estágio do ciclo de vida do dado | `templates/pipeline-dados.html` | `references/grammar-dados.md` |

Um caso pode precisar de duas famílias (o processo que alimenta um sistema
que entra num pipeline). Faça dois diagramas ligados por um nó de
subprocesso, nunca um só sobrecarregado.

## Princípios

1. **A fonte manda, você não inventa.** Antes de desenhar, liste em texto:
   atores/estágios, etapas em ordem, decisões e suas saídas, sistemas e
   instrumentos, observações e base legal. Fonte = documento, ata, código,
   DAG, `manifest.json`. Se faltar informação para fechar uma etapa,
   pergunte. Não preencha lacuna com passo "provável".
2. **Legibilidade acima de completude.** Máximo ~12 nós por diagrama. Acima
   disso, divida com nó de subprocesso. Rótulos curtos (verbo + objeto);
   detalhe técnico vai para `.tag` e `.note`, não para dentro da caixa.
3. **Sempre com legenda.** Todo tipo de nó e de seta usado aparece na
   `.legend`.
4. **IDV atual, sem exceção.** Só os tokens de `references/colors.md`.
   Reddit Sans. Nada de `#7A34F3`/`#F97316` (paleta antiga) nem Inter/Tailwind
   (figuras antigas do relatório MinC usam isso e estão fora da identidade).
5. **Dado pessoal aparece no diagrama.** CPF, nome de bolsista, dado de
   beneficiário: marque o ponto de anonimização com `.note--lgpd`.
6. **Nome real de tudo.** Sistema, schema, DAG, camada: o nome que o projeto
   usa (confira no código/documentação), nunca um genérico.

## Como construir — passo a passo

1. **Extrair a lógica da fonte.**

   | Fonte | Como extrair |
   |---|---|
   | Projeto dbt (`target/manifest.json`) | `python3 <skill>/scripts/dbt_lineage.py target/manifest.json --group schema` (mapa de schemas) ou `--group layer` (pipeline). Sem manifest: `dbt parse`. |
   | DAGs do Airflow, código | Ler os arquivos; listar fontes, tabelas de pouso, cadência. |
   | Documento, ata, transcrição, PDF | Ler tudo; cada caixa, seta, sistema e observação da fonte entra na lista. |
   | Descrição do usuário | Listar e confirmar o que ficou ambíguo antes de desenhar. |

   Escreva a lista (atores/estágios, etapas, decisões, sistemas, observações)
   e mostre ao usuário se houver qualquer dúvida.

2. **Escolher a família** pela tabela acima e ler a gramática correspondente
   (obrigatório — ela diz como cada nó vira HTML).

3. **Copiar o template embutindo os assets** para o diretório de saída
   (padrão `./diagramas/`, ou o que o usuário pedir):
   ```bash
   node <skill>/scripts/inline_assets.mjs <skill>/templates/<familia>.html ./diagramas/figura-N-<nome>.html
   ```
   Editar o HTML: título, subtítulo, nós (com `id` únicos), `.tag`, `.note`,
   legenda, e o JSON de setas em `#arrows` (`from`/`to` = ids; `type` = `exec`,
   `data`, `meta`, `flow`, `gov`; `label`; `fromSide`/`toSide`; `via` para
   desviar de um nó). Layout em CSS no `<style>` do próprio arquivo, usando
   só as classes de `references/diagram.css`.

4. **Renderizar:**
   ```bash
   node <skill>/scripts/render.mjs ./diagramas/figura-N-<nome>.html
   ```
   Gera o `.png` ao lado (largura 3000 px, escala 2). Se sair código 2 ou o
   Chromium não abrir, rode `bash <skill>/scripts/setup.sh` (uma vez; pode
   pedir sudo) e repita. Se o log disser que a Reddit Sans não carregou,
   verifique a internet — o PNG saiu com fonte errada. Após atualizar o
   plugin, o `node_modules` some — rode `setup.sh` de novo (só o npm
   install; o Chromium fica em `~/.cache/ms-playwright`).

5. **Conferir o PNG lendo a imagem.** Procure: texto cortado ou quebrado
   em lugar ruim, seta atravessando nó, rótulo em cima de borda, pílula
   cortada, fonte fallback, cor fora da tabela. Corrija o HTML (`via`,
   `dx`/`dy`, `gap`, `grid-column`) e renderize de novo. Só entregue quando
   passar. Diagramas técnicos raramente saem certos na primeira.

6. **Entregar** o HTML, o PNG e a legenda em texto (a mesma da imagem), no
   formato "Figura N. ..." para o usuário colar no relatório. Diga o que foi
   assumido, se algo foi.

## Checklist antes de entregar

- [ ] Nenhuma etapa/componente inventado; nenhum da fonte esquecido.
- [ ] Legenda cobre todos os tipos de nó e de seta usados.
- [ ] Toda seta tem `type`; toda decisão tem as saídas rotuladas.
- [ ] Nome real de cada sistema/schema/camada.
- [ ] Só cores de `references/colors.md`; Reddit Sans carregada no log.
- [ ] Dado pessoal marcado com `.note--lgpd`, se existir.
- [ ] ≤ ~12 nós, ou dividido em dois diagramas.
- [ ] PNG conferido visualmente após o último ajuste.

## O que não fazer

- Não desenhar sem listar a lógica antes.
- Não usar Mermaid, SVG à mão, cairosvg ou coordenadas fixas de seta — as
  setas vêm do JSON `#arrows` e são posicionadas pelo layout; `via` e a
  posição de um `.badge` são a única exceção, para desviar de um nó.
- Não usar cores fora de `colors.md` nem fonte diferente de Reddit Sans.
- Não entregar PNG sem ter olhado para ele.
- Não publicar o diagrama técnico como peça de divulgação: para isso, faça um
  segundo diagrama simplificado.

## Arquivos

- `references/colors.md` — papel → token. `references/diagram.css` — classes.
  `references/diagram.js` — setas.
- `references/grammar-arquitetura.md`, `grammar-processo.md`, `grammar-dados.md`.
- `templates/*.html` — quatro pontos de partida, um por família.
- `scripts/render.mjs`, `scripts/inline_assets.mjs`, `scripts/dbt_lineage.py`,
  `scripts/setup.sh`.
