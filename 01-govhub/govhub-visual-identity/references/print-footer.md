# Rodapé de PDF — código exato validado

Pressupõe a arquitetura de [`print-pages.md`](print-pages.md) (`.gh-page`
fixa 210×297mm, `@page { margin: 0 }`). Validado com o usuário em agosto de
2026, depois de duas rodadas de ajuste — leia "Erros já cometidos" no fim
antes de alterar valores de tamanho/posição.

Aparece em **toda página de conteúdo** (com ou sem cabeçalho de capítulo),
nunca na capa (a capa tem seu próprio rodapé pequeno, ver
[`print-cover.md`](print-cover.md)).

## O que é

Uma barra fina divisória **alinhada à margem do conteúdo** (não vai até a
borda física da página — só até onde o texto do documento também vai) e,
abaixo dela, à esquerda o **número da página** em navy bold seguido do
nome curto do documento, e à direita a marca circular da Gov Hub (símbolo
isolado), em tamanho pequeno-mas-legível. O símbolo é
`icone-none-navy.svg` (navy sólido), a pedido do usuário em 2026-09-17: a
versão `default` (multicolor) competia com a sobriedade do documento e é
a única que embute PNGs (ver `editorial-report.md` seção 1). Sobre fundo
escuro, `icone-none-white.svg`.

## CSS

```css
.gh-footer-bar {
  position: absolute; left: 20mm; right: 20mm; bottom: 23mm;  /* mesma margem do conteúdo, NÃO left/right:0 */
  height: 2px; background: var(--border-soft);
}
.gh-footer {
  position: absolute; left: 20mm; right: 20mm; bottom: 12mm;
  display: flex; align-items: center; justify-content: space-between;
}
.gh-footer__text { font-size: 9pt; color: var(--text-muted); display: flex; align-items: baseline; gap: 10px; }  /* nota de rodapé — ver escala em print-header.md */
.gh-footer__page { font-size: 9pt; font-weight: 800; color: var(--dark-navy); font-variant-numeric: tabular-nums; min-width: 14px; }
.gh-footer__logo { height: 9.5mm; width: auto; }
```

## HTML

```html
<div class="gh-footer-bar"></div>
<div class="gh-footer">
  <span class="gh-footer__text"><span class="gh-footer__page">4</span>Nome curto do documento &middot; Nome curto do projeto/frente &middot; Gov Hub &middot; Lab Livre - UnB</span>
  <img class="gh-footer__logo" alt="" src="logo/icone-none-navy.svg">
</div>
```

## Padrão do texto (`.gh-footer__text`)

```
N   Nome curto do documento · Nome curto do projeto ou frente · Gov Hub · Lab Livre - UnB
```

Sempre as 4 partes nessa ordem, mesmo separador (`&middot;`) entre todas.
Exemplo real: `4   Relatório de Diagnóstico · MGI · Gov Hub · Lab Livre - UnB`.

## Número da página (`.gh-footer__page`)

Pedido do usuário em 2026-09-17 ("a paginação sumiu"): número físico da
página, em `--dark-navy` bold, à esquerda do texto, separado por 10px. É
**texto fixo digitado por você**, como tudo na paginação manual desta
skill: a capa é a página 1 (e não leva rodapé, então o primeiro número
impresso é 2, na folha de identificação, ou 2 no capítulo 01 quando não há
front matter). Toda vez que uma página entra, sai ou muda de lugar, renumere
todos os rodapés e o índice juntos (ver "Números de página são manuais" em
`print-frontmatter.md`); os dois precisam bater, confira no PDF final.

## O que varia por documento

- O número da página (um por página, sequencial, capa = 1).
- As duas primeiras partes do texto — nome curto do documento e nome curto
  do projeto/frente a que ele pertence. As duas últimas (`Gov Hub · Lab
  Livre - UnB`) são fixas da marca, assim como o símbolo e a barra.

## Erros já cometidos (não repita)

1. **"De ponta a ponta" não significa até a borda física da página.** A
   primeira versão usava `left:0; right:0` na barra, fazendo-a sangrar até
   a borda — o usuário corrigiu: a barra deve ir só até onde o conteúdo
   (texto, tabelas) também vai, ou seja, `left`/`right` iguais à margem do
   corpo (20mm neste caso), não zero. "De ponta a ponta" = a largura útil
   do conteúdo, não a folha inteira.
2. **Logo grande demais.** Primeira tentativa validada tinha
   `height: 15mm` — grande o suficiente para competir visualmente com o
   texto do rodapé. Reduzida para `9.5mm` a pedido do usuário. Se for
   ajustar de novo, mude em passos pequenos (1-2mm) e confira antes de
   seguir.
3. **Barra colada no texto.** A distância entre a barra (`bottom: 23mm`) e
   a linha de texto do rodapé (`bottom: 12mm`) precisa ser visivelmente
   maior que a altura de uma linha de texto — um gap de ~11mm entre as duas
   posições (não a distância literal entre os elementos, que é menor por
   causa da própria altura da barra/texto) foi o que funcionou.
4. **Símbolo cortado.** Até 2026-09-17 os `icone-none-*.svg` tinham o
   `viewBox` colado no extremo esquerdo do círculo (x = 21,0 exato) e o
   rasterizador achatava 1 unidade do arco: o símbolo saía com um corte
   fino à esquerda, visível só com zoom. Os arquivos foram regravados com
   2 unidades de folga (`viewBox="19 -2 295 337"`). Se reexportar a logo
   do Figma, confira o corte antes de substituir os arquivos.
