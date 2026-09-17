# Variações dos templates de post Gov Hub (galeria HTML)

## Objetivo

Gerar variações dos 5 quadros 1080×1350 de `social-posts.md` (capa,
conteúdo, ênfase, convite, fechamento) para o usuário comparar visualmente:
fundos em cada uma das 5 cores da paleta e novas composições dos elementos
gráficos. Entrega: uma galeria HTML publicada como artifact, sem conteúdo
real (texto de exemplo discreto, opcional).

## Matriz

5 estruturas × 5 fundos (roxo `#613EFF`, navy `#0A005A`, pêssego `#FFE7E1`,
rosa `#F9006F`, magenta `#EF41FF`) × 4 composições (a atual de
`social-posts.md` + 3 novas por estrutura) = 100 quadros, todos gerados por
JS a partir de uma spec declarativa (`estruturas[]`, `composicoes[]`,
`fundos{}`), com as formas do `graphic-elements-catalog.md` como SVG inline.

## Regras de cor por fundo

| Fundo | Texto | Logo | Cores de forma permitidas | Pílula de rótulo | Chip |
|---|---|---|---|---|---|
| navy | branco | white | roxo, magenta, pêssego, rosa | magenta / navy | navy sobre roxo |
| roxo | branco | white | navy, pêssego, magenta, rosa | pêssego / navy | navy |
| pêssego | navy | navy | roxo, navy, magenta, rosa | magenta / navy | rosa |
| rosa | branco (peso ≥ 600) | white | navy, pêssego, roxo | navy / branco | navy |
| magenta | navy | navy | navy, pêssego, roxo | pêssego / navy | navy |

Pares evitados: rosa sobre magenta, magenta sobre rosa, pêssego como forma
principal sobre rosa (contraste e vibração). Rosa continua acento: no
máximo 1 forma pequena por quadro, salvo quando é o fundo.

## Composições

Cada composição define: 2 a 4 formas (tipo, cor por papel `principal`/
`secundária`/`detalhe`, posição, tamanho, rotação em múltiplos de 90°) e a
zona livre de texto (retângulo). Forma principal com 40–50 % do lado menor
(430–540 px), sangrando por pelo menos uma borda. Por estrutura:

- **Capa**: A atual (quarto TR + meio-anel base + semi-pílula direita);
  B círculo grande sangrando TL + pílula base direita + texto embaixo à
  direita; C semicírculo largo no topo centro + anel direita + texto centro
  inferior; D semi-pílula vertical colada à esquerda + quarto BR + texto no
  topo direito.
- **Conteúdo**: A atual (quarto TR 470 + anel BL); B quarto BL + meio-anel
  topo direita, título à direita; C faixa de 3 formas pequenas na base
  (círculo, anel, pílula) + topo livre; D círculo grande sangrando à
  direita no meio + pílula de rótulo.
- **Ênfase**: A atual (quarto BL + semicírculo topo + anel direita);
  B círculo enorme centrado atrás do texto (cor secundária), texto
  centralizado; C quarto TL + quarto BR (diagonal), texto na faixa central;
  D meio-anel grande sangrando pela direita + pílula na base esquerda.
- **Convite**: A atual (quarto BR + anel BL); B semicírculo na base
  full-width + anel TR, conteúdo no topo; C círculo TR sangrando + pílula
  BL; D quatro formas pequenas nos cantos, centro livre.
- **Fechamento**: A atual (quarto TL + meio-anel base direita + semi-pílula
  esquerda); B espelho da capa B; C anel grande centrado atrás da logo;
  D semicírculo topo + semi-pílula base direita.

## Galeria

Página única: cabeçalho com filtros (estrutura, fundo, composição), toggles
"zonas de texto" (retângulo tracejado) e "texto de exemplo", grade de
quadros renderizados em 1080×1350 e escalados por `transform`, clique abre
em tamanho grande com o nome `estrutura · composição · fundo`. Fontes via
Google Fonts. Logos publicadas como arquivos do artifact
(`logo/logomarca-horizontal-white.svg`, `-navy.svg`, `icone-none-white.svg`).
Sem ícones de produto (chips vazios) e sem os blocos A/B/C reais (um bloco
genérico de 2 cards no conteúdo).

## Fora do escopo

Conteúdo real, exportação PNG, alteração da skill (só depois de o usuário
aprovar quais variações ficam).
