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
abaixo dela, nome curto do documento à esquerda + marca circular da Gov Hub
(símbolo isolado) à direita, em tamanho pequeno-mas-legível.

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
.gh-footer__text { font-size: 9pt; color: var(--text-muted); }  /* nota de rodapé — ver escala em print-header.md */
.gh-footer__logo { height: 9.5mm; width: auto; }
```

## HTML

```html
<div class="gh-footer-bar"></div>
<div class="gh-footer">
  <span class="gh-footer__text">Nome curto do documento &middot; Nome curto do projeto/frente &middot; Gov Hub &middot; Lab Livre - UnB</span>
  <img class="gh-footer__logo" alt="" src="logo/icone-none-default.svg">
</div>
```

## Padrão do texto (`.gh-footer__text`)

```
Nome curto do documento · Nome curto do projeto ou frente · Gov Hub · Lab Livre - UnB
```

Sempre as 4 partes nessa ordem, mesmo separador (`&middot;`) entre todas.
Exemplo real: `Relatório de Diagnóstico · MGI · Gov Hub · Lab Livre - UnB`.

## O que varia por documento

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
