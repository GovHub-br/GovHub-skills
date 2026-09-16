# Marca d'água em PDF: opcional, pergunte antes

Os elementos gráficos do Gov Hub (`graphic-elements-catalog.md`) podem
aparecer nas páginas de conteúdo de um documento como marca d'água. **Não é
obrigatório** e o padrão é **sem**. Pressupõe a arquitetura `.gh-page` de
[`print-pages.md`](print-pages.md).

## Pergunta obrigatória

Antes de gerar qualquer documento (relatório, e-book, framework, dicionário
de dados), pergunte ao usuário, literalmente:

> Quer marca d'água com os elementos gráficos do Gov Hub nas páginas de
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
.gh-page__content { position: relative; z-index: 1; }

.gh-watermark {
  position: absolute; z-index: 0; pointer-events: none;
  right: -15%; bottom: -15%; width: 55%;
  color: var(--primary-purple);
  opacity: .07;                         /* padrão; máximo .10 */
}
.gh-watermark--topo { bottom: auto; top: -15%; transform: rotate(-90deg); }   /* página só de tabela larga */
.gh-watermark--navy { color: var(--dark-navy); }
.gh-page--peach .gh-watermark { opacity: .05; }                               /* sobre fundo pêssego */
```

## HTML (por página de conteúdo)

```html
<section class="gh-page">
  <svg class="gh-watermark" viewBox="0 0 100 100" aria-hidden="true"><path fill="currentColor" fill-rule="evenodd" d="M0 0h100a100 100 0 0 1-100 100zM0 0h48.7a48.7 48.7 0 0 1-48.7 48.7z" transform="rotate(180 50 50)"/></svg>
  <div class="gh-page__content">
    <!-- CONTEÚDO -->
  </div>
</section>
```

O `rotate(180 50 50)` vira o quarto de anel para o canto reto ficar no
inferior direito. Para o quarto de círculo cheio troque o `d` por
`M0 0h100a100 100 0 0 1-100 100z` (sem `fill-rule`).

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
- Cabeçalho de capítulo (`print-header.md`) e rodapé (`print-footer.md`)
  ficam por cima da marca d'água: mantenha-os com `position: relative;
  z-index: 1` como o `.gh-page__content`.

## Conferência

Rasterize duas páginas (uma de texto corrido, uma com tabela) e confirme:
a forma é perceptível mas o texto por cima lê normalmente; nenhuma linha de
tabela ficou com contraste reduzido; a forma não aparece em capa/índice.

## Erros a evitar

- Aplicar sem perguntar, ou por "tanto faz".
- Opacidade acima de `.10` ("pra aparecer mais"): vira ilustração e compete com o conteúdo.
- Mosaico `outros-elementos-graficos.svg` de fundo em documento: não é o padrão; se o usuário pedir, `opacity` ≤ `.04`.
- Esquecer `z-index: 1` no conteúdo: a forma passa por cima de imagens e tabelas.
