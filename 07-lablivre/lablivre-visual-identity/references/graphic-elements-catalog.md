# Catálogo de elementos gráficos Lab Livre

Os 8 arquivos existem **na paleta do Lab Livre**, na pasta
`lablivre/graphic-elements/` do `skills-assets` (recoloridos a partir dos
do Gov Hub em 2026-09-21: mesma geometria e composição, só os hex
trocados). A linguagem gráfica é a mesma que o MIV do Lab Livre prescreve
(círculos, semicírculos, retângulos arredondados). Como os ícones, **não
ficam nesta skill**: vivem no repo público
[`GovHub-br/skills-assets`](https://github.com/GovHub-br/skills-assets) e são
servidos por CDN. Todos são SVG `1920×1080` (16:9), só formas vetoriais nas
cores da paleta, sem imagem embutida.

## URL

```
https://cdn.jsdelivr.net/gh/GovHub-br/skills-assets@main/lablivre/graphic-elements/<nome>.svg
```

`@main` acompanha o repo (cache CDN de ~12 h). Para congelar uma versão
exata, troque `@main` por uma tag ou pelo SHA do commit.

Exemplo como fundo de slide:

```css
.gh-slide--content {
  background: url("https://cdn.jsdelivr.net/gh/GovHub-br/skills-assets@main/lablivre/graphic-elements/pagina-comum.svg") center / cover no-repeat;
}
```

## Os elementos e quando usar cada um

Três categorias: **template de slide** (fundo pronto, o texto vai por cima),
**folha de formas** (referência para recompor em outros formatos) e
**padrão** (textura). Só os templates viram fundo de slide.

| Arquivo | O que tem | Categoria | Quando usar |
|---|---|---|---|
| `capa.svg` | Fundo navy; quarto de círculo roxo grande na direita; meio-anel magenta sangrando pelo topo; pílula pêssego sangrando pela direita no rodapé. Lado esquerdo livre. | template | **Slide 1** de toda apresentação. Título, subtítulo e logo na metade esquerda. |
| `encerramento.svg` | Espelho da capa: formas na esquerda, lado direito livre. | template | **Último slide** (obrigado, contato, parceiros). Texto na metade direita. |
| `capa-capitulo.svg` | Fundo roxo; moldura arredondada fina **magenta**; quarto de círculo navy no canto superior esquerdo; meio-anel pêssego no topo; quarto de anel magenta no canto inferior direito. | template | **Abertura de seção/capítulo.** Numeral + eyebrow + título dentro da moldura. |
| `capa-capitulo-alternativa.svg` | Igual à anterior, com moldura e quarto de anel **pêssego** e meio-anel magenta. | template | Abertura de seção. **Alterne** com `capa-capitulo` a cada seção consecutiva para dar ritmo (1ª seção normal, 2ª alternativa, 3ª normal...). |
| `pagina-comum.svg` | Fundo pêssego; pílula magenta no canto superior esquerdo. | template | **Slide de conteúdo padrão** (texto, bullets, tabela, imagem). O título vai **dentro** da pílula. |
| `pagina-comum-com-enfase.svg` | Fundo pêssego; pílula magenta mais larga; quarto de anel roxo no canto superior direito; quarto de círculo navy e meio-anel magenta no canto inferior direito. | template | **Slide de destaque**: número-chave, citação, síntese de seção. No máximo 1 por seção. Conteúdo fica nos ~60 % da esquerda. |
| `elementos-graficos.svg` | Folha com as formas isoladas (pílula, quarto de círculo, círculo, anel, semi-pílula, pílula rosa) sobre pêssego. | folha de formas | **Não é slide.** Referência de proporção e cor para recompor em Instagram, poster, banner. Os snippets prontos estão abaixo. |
| `outros-elementos-graficos.svg` | Mosaico de ~100 formas pequenas (navy, roxo, magenta) sobre pêssego. | padrão | **Não é slide.** Textura de fundo ou faixa em materiais de comunicação. |

Regras de composição e zonas seguras de texto por template: `slides.md`.

## Sem internet no ambiente de geração

Baixe a pasta e troque as URLs por caminho relativo (`graphic-elements/<nome>.svg`):

```bash
git clone --depth 1 https://github.com/GovHub-br/skills-assets.git
cp -r skills-assets/lablivre/graphic-elements ./graphic-elements
```

## Formas isoladas (snippets)

As seis formas da folha `elementos-graficos.svg`, mais duas derivadas que
aparecem nos templates (meio-anel e quarto de anel), reescritas como
primitivas SVG limpas. Todas usam `fill="currentColor"`: defina `color` no
CSS com uma cor da paleta. Proporções copiadas da folha (anel com furo de
~49 % do raio; pílula 2,66:1; semi-pílula 1,97:1).

Círculo:

```svg
<svg class="gh-shape gh-shape--circulo" viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="50" fill="currentColor"/></svg>
```

Anel (donut):

```svg
<svg class="gh-shape gh-shape--anel" viewBox="0 0 100 100" aria-hidden="true"><path fill="currentColor" fill-rule="evenodd" d="M50 0a50 50 0 1 0 0 100a50 50 0 1 0 0-100zM50 25.6a24.4 24.4 0 1 1 0 48.8a24.4 24.4 0 1 1 0-48.8z"/></svg>
```

Semicírculo (lado reto em cima, para sangrar pela borda superior):

```svg
<svg class="gh-shape gh-shape--semicirculo" viewBox="0 0 100 50" aria-hidden="true"><path fill="currentColor" d="M0 0h100a50 50 0 0 1-100 0z"/></svg>
```

Quarto de círculo (canto reto no canto superior esquerdo):

```svg
<svg class="gh-shape gh-shape--quarto" viewBox="0 0 100 100" aria-hidden="true"><path fill="currentColor" d="M0 0h100a100 100 0 0 1-100 100z"/></svg>
```

Pílula:

```svg
<svg class="gh-shape gh-shape--pilula" viewBox="0 0 266 100" aria-hidden="true"><rect width="266" height="100" rx="50" fill="currentColor"/></svg>
```

Semi-pílula (lado reto à direita, para sangrar pela borda):

```svg
<svg class="gh-shape gh-shape--semipilula" viewBox="0 0 197 100" aria-hidden="true"><path fill="currentColor" d="M197 0H50a50 50 0 0 0 0 100h147z"/></svg>
```

Meio-anel (lado reto em cima):

```svg
<svg class="gh-shape gh-shape--meioanel" viewBox="0 0 100 50" aria-hidden="true"><path fill="currentColor" fill-rule="evenodd" d="M0 0h100a50 50 0 0 1-100 0zM25.6 0h48.8a24.4 24.4 0 0 1-48.8 0z"/></svg>
```

Quarto de anel (canto reto no canto superior esquerdo):

```svg
<svg class="gh-shape gh-shape--quartoanel" viewBox="0 0 100 100" aria-hidden="true"><path fill="currentColor" fill-rule="evenodd" d="M0 0h100a100 100 0 0 1-100 100zM0 0h48.7a48.7 48.7 0 0 1-48.7 48.7z"/></svg>
```

Para virar a forma (sangrar por outra borda), use `transform: rotate(90deg)`
/ `180deg` / `270deg` ou `scaleX(-1)` no CSS. Só múltiplos de 90°.

```css
.gh-shape { display: block; }
.gh-shape--sangra-direita { position: absolute; right: -12%; bottom: -12%; width: 48%; color: var(--primary-purple); }
```

## Comunicação: Instagram, poster, banner

Os templates 16:9 **não são esticados** para outras proporções. Recomponha
com as formas isoladas acima.

Formatos canônicos:

| Peça | Canvas |
|---|---|
| Feed quadrado | 1080×1080 px |
| Feed retrato | 1080×1350 px |
| Stories / Reels capa | 1080×1920 px |
| Poster A4 retrato | 210×297 mm (2480×3508 px a 300 dpi) |
| Poster A3 retrato | 297×420 mm (3508×4961 px a 300 dpi) |
| Banner web | 1920×600 px |

Regras de recomposição (as mesmas proporções dos templates):

1. Fundo sólido em **navy**, **roxo** ou **pêssego**. Nunca gradiente, nunca branco puro como fundo de arte.
2. De **2 a 4 formas**, sempre sangrando por pelo menos uma borda (nenhuma forma "flutuando" inteira no meio, exceto o anel pequeno como pontuação).
3. Forma principal com **40 a 50 % do lado menor** do canvas; as demais entre 15 e 30 %.
4. Cores só da paleta; cada forma numa cor diferente do fundo. Rosa `#F46B2F` no máximo numa forma pequena ou num número.
5. Texto na zona livre, oposta às formas. Chamada em **Oswald uppercase**; apoio em **Reddit Sans**. Sobre navy/roxo, texto branco; sobre pêssego, navy.
6. Logo Lab Livre na zona livre, respeitando a área de não-interferência (`SKILL.md`). Nunca sobre uma forma da mesma cor.
7. Rotação de formas só em múltiplos de 90°. Sem sombra, sem contorno, sem 3D.
8. Mosaico `outros-elementos-graficos.svg`: como **faixa** (topo ou rodapé de stories/poster, cortado com `object-fit: cover`) ou como textura de fundo inteira com `opacity` ≤ 0.4 e um bloco sólido atrás do texto.

Exemplo de feed quadrado (1080×1080):

```html
<div class="gh-post" style="position:relative;width:1080px;height:1080px;overflow:hidden;background:#080056;color:#fff;font-family:'Reddit Sans',sans-serif">
  <svg class="gh-shape" viewBox="0 0 100 100" style="position:absolute;right:-10%;top:-10%;width:48%;color:#7023E8;transform:rotate(90deg)"><path fill="currentColor" d="M0 0h100a100 100 0 0 1-100 100z"/></svg>
  <svg class="gh-shape" viewBox="0 0 100 50" style="position:absolute;left:8%;bottom:0;width:26%;color:#E52E70;transform:rotate(180deg)"><path fill="currentColor" fill-rule="evenodd" d="M0 0h100a50 50 0 0 1-100 0zM25.6 0h48.8a24.4 24.4 0 0 1-48.8 0z"/></svg>
  <svg class="gh-shape" viewBox="0 0 197 100" style="position:absolute;right:0;bottom:14%;width:22%;color:#FFE7E1"><path fill="currentColor" d="M197 0H50a50 50 0 0 0 0 100h147z"/></svg>
  <div style="position:absolute;left:80px;top:120px;width:560px">
    <h1 style="font:700 88px/1.05 'Oswald',sans-serif;text-transform:uppercase;margin:0 0 24px">Chamada da arte</h1>
    <p style="font-size:30px;line-height:1.4;margin:0;opacity:.92">Texto de apoio curto, uma ou duas linhas.</p>
  </div>
  <img src="logo/logomarca-horizontal-white.svg" alt="Lab Livre" style="position:absolute;left:80px;bottom:80px;height:56px">
</div>
```

## Regras de uso (valem para todos os elementos)

- Não recolorir fora da paleta oficial; não aplicar sombra, contorno, 3D ou gradiente.
- Não esticar nem distorcer a proporção de um template; rotação só em múltiplos de 90°.
- Nunca usar `elementos-graficos.svg` ou `outros-elementos-graficos.svg` como fundo de slide.
- Texto sempre na zona livre do template (`slides.md`), nunca sobre uma forma de cor próxima à do texto.
- Em documentos (PDF/e-book), os elementos entram só como marca d'água **opcional**: `print-watermark.md`.

## Como adicionar um elemento novo

1. Subir o SVG `1920×1080` (ou o formato da peça) em `skills-assets/lablivre/graphic-elements/` e dar push.
2. Acrescentar uma linha na tabela acima com categoria e "quando usar".
3. Se for um template de slide novo, adicionar a zona segura e o código do tipo em `slides.md`.
