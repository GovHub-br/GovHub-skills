# Marca d'água em PDF: opcional, pergunte antes

Os elementos gráficos do Lab Livre (`graphic-elements-catalog.md`) podem
aparecer nas páginas de conteúdo de um documento como marca d'água. **Não é
obrigatório** e o padrão é **sem**. Pressupõe a arquitetura `.gh-page` de
[`print-pages.md`](print-pages.md).

## Pergunta obrigatória

Antes de gerar qualquer documento (relatório, e-book, framework, dicionário
de dados), pergunte ao usuário, literalmente:

> Quer marca d'água com os elementos gráficos do Lab Livre nas páginas de
> conteúdo? (padrão: não)

Só aplique com "sim" explícito. Se a pessoa não responder ou disser "tanto
faz", gere **sem**.

## O que é

Uma única forma isolada (quarto de anel ou quarto de círculo, do catálogo)
sangrando pelo canto inferior direito de cada página de conteúdo, em roxo
com `opacity: .07`. Fica atrás de todo o conteúdo e não interfere na
leitura: é um leve relevo de marca, não uma ilustração.

## CSS

```css
.gh-page { position: relative; overflow: hidden; }
.gh-band, .gh-page-body, .gh-footer-bar, .gh-footer { z-index: 1; }

.gh-watermark {
  position: absolute; z-index: 0; pointer-events: none;
  right: -10%; bottom: -7%; width: 55%;   /* % de largura e de altura da página: com mais deslocamento o furo do anel sai da página e vira quarto de círculo cheio */
  color: var(--primary-purple);
  opacity: .07;                         /* padrão; máximo .10 */
  transform: rotate(180deg);            /* canto reto do quarto de anel vai para o inferior direito */
}
.gh-watermark--topo { bottom: auto; top: -7%; transform: rotate(90deg); }    /* página só de tabela larga: canto reto no superior direito */
.gh-watermark--navy { color: var(--dark-navy); }
.gh-page--peach .gh-watermark { opacity: .05; }                               /* sobre fundo pêssego */
```

`.gh-page--peach` é um hook: acrescente essa classe na `.gh-page` específica
cuja página tem fundo pêssego. Nenhum arquivo desta skill declara
`.gh-page--peach` sozinho, é o autor do documento que soma essa classe à
página quando o fundo for pêssego.

## HTML (por página de conteúdo)

```html
<section class="gh-page">
  <svg class="gh-watermark" viewBox="0 0 100 100" aria-hidden="true"><path fill="currentColor" fill-rule="evenodd" d="M0 0h100a100 100 0 0 1-100 100zM0 0h48.7a48.7 48.7 0 0 1-48.7 48.7z"/></svg>
  <div class="gh-band">
    <!-- cabeçalho de capítulo (branco, navy, barra abaixo), só na 1ª página; ver print-header.md -->
  </div>
  <div class="gh-page-body">
    <!-- CONTEÚDO -->
  </div>
  <div class="gh-footer-bar"></div>
  <div class="gh-footer">
    <!-- nome do documento + logo; ver print-footer.md -->
  </div>
</section>
```

A rotação fica **só no CSS** (`transform: rotate(180deg)` na classe base,
`rotate(90deg)` no `--topo`); não use o atributo `transform` do SVG junto,
porque nos navegadores o `transform` do CSS substitui o atributo em vez de
somar, e a forma vira para o canto errado. Para o quarto de círculo cheio
troque o `d` por `M0 0h100a100 100 0 0 1-100 100z` (sem `fill-rule`).

## Restrições

- **Nunca** na capa, folha de identificação do projeto, índice e página de
  encerramento; só em páginas de conteúdo.
- **Uma** forma por página, sempre a mesma ao longo do documento (não
  alterne formas página a página).
- Opacidade máxima `.10`; sobre pêssego, `.05`. Cor: roxo ou navy, nada
  além.
- Página que é só uma tabela larga: use `gh-watermark--topo` (canto superior
  direito) para não competir com as últimas linhas; a tabela cobrindo parte
  da forma é aceitável.
- `.gh-band` (cabeçalho de capítulo, `print-header.md`), `.gh-page-body`
  (corpo da página, `print-header.md`) e o rodapé (`.gh-footer-bar` /
  `.gh-footer`, `print-footer.md`) já são `position: absolute` mas não
  declaram `z-index`; acrescente `z-index: 1` a eles (`.gh-band,
  .gh-page-body, .gh-footer-bar, .gh-footer { z-index: 1; }`) para ficarem
  por cima da marca d'água. Sem isso a ordem de empilhamento depende só da
  ordem no DOM.

## Conferência

Rasterize duas páginas (uma de texto corrido, uma com tabela) e confirme:
a forma é perceptível mas o texto por cima lê normalmente; nenhuma linha de
tabela ficou com contraste reduzido; a forma não aparece em capa/índice.

## Erros a evitar

- Aplicar sem perguntar, ou por "tanto faz".
- Opacidade acima de `.10` ("pra aparecer mais"): vira ilustração e compete com o conteúdo.
- Mosaico `outros-elementos-graficos.svg` de fundo em documento: não é o padrão; se o usuário pedir, `opacity` ≤ `.04`.
- Esquecer `z-index: 1` em `.gh-page-body` e no cabeçalho/rodapé: a forma passa por cima de imagens e tabelas.
