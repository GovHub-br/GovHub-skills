# Elementos gráficos Gov Hub na skill de identidade visual — plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Documentar na skill `01-govhub/govhub-visual-identity` os 8 elementos gráficos (já publicados no CDN) como catálogo, templates obrigatórios de slide, referência para comunicação e marca d'água opcional em documentos.

**Architecture:** Três referências novas em `references/` (`graphic-elements-catalog.md`, `slides.md`, `print-watermark.md`), seguindo o padrão dos `print-*.md` (código exato + erros a evitar), mais edições pontuais no `SKILL.md`. Nada de código executável entra na skill; a "suíte de testes" de cada task é um script no scratchpad que renderiza o código documentado (WeasyPrint → PDF → pypdfium2 → PNG) e uma inspeção visual do resultado.

**Tech Stack:** Markdown, HTML/CSS, SVG. Verificação: `python3 -m weasyprint`, `pypdfium2`, `cairosvg`, `curl`.

Spec: `docs/superpowers/specs/2026-09-16-govhub-graphic-elements-design.md`.

## Global Constraints

- URL-base do CDN (já publicada, HTTP 200 verificado): `https://cdn.jsdelivr.net/gh/GovHub-br/skills-assets@main/graphic-elements/<nome>.svg`. Os 8 nomes: `capa`, `encerramento`, `capa-capitulo`, `capa-capitulo-alternativa`, `pagina-comum`, `pagina-comum-com-enfase`, `elementos-graficos`, `outros-elementos-graficos`.
- A pasta local `references/graphic-elements/` **já foi removida** da skill; nenhum arquivo novo deve referenciar caminho local.
- Paleta oficial (sem outras cores): navy `#0A005A`, roxo `#613EFF`, magenta `#EF41FF`, rosa `#F9006F`, pêssego `#FFE7E1`, branco.
- Fontes: Oswald (títulos, uppercase) e Reddit Sans (corpo). Sem travessão (—) em texto corrido dos arquivos novos: use dois-pontos, vírgula ou ponto.
- Slides: canvas `1920×1080px`, um template por slide, sem gradiente e sem fundo sólido inventado.
- Marca d'água: padrão **não**; só com "sim" explícito do usuário; opacidade máxima 10 % (5 % sobre pêssego); nunca em capa, folha de identificação, índice, encerramento.
- Idioma dos arquivos: português, mesmo tom dos `print-*.md`.
- Commits: mensagem em português, terminando com `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`.
- Scratchpad para arquivos temporários: `/tmp/claude-1000/-home-joaoegewarth-GovHub-skills/3d30e7bd-45fc-4a77-9391-fbd2f2d4c167/scratchpad` (abaixo, `$OUT`).
- Ambiente: `python3 -m weasyprint` e `pypdfium2` já instalados (`pip install --user weasyprint pypdfium2` se faltar). Chrome headless do Playwright **não funciona** aqui (falta `libnspr4`).

---

### Task 1: Catálogo de elementos gráficos

**Files:**
- Create: `01-govhub/govhub-visual-identity/references/graphic-elements-catalog.md`
- Test: `$OUT/test-catalog.sh` (temporário)

**Interfaces:**
- Produces: nomes das classes de forma usadas em `slides.md` e `print-watermark.md`: os snippets SVG `gh-shape-*` (círculo, anel, semicírculo, quarto de círculo, pílula, semi-pílula, meio-anel, quarto de anel), todos com `fill="currentColor"` e `viewBox` próprio.

- [ ] **Step 1: Escrever o teste (script) que valida URLs e renderiza as formas**

```bash
cat > $OUT/test-catalog.sh <<'EOF'
#!/usr/bin/env bash
set -e
CAT=01-govhub/govhub-visual-identity/references/graphic-elements-catalog.md
OUT=/tmp/claude-1000/-home-joaoegewarth-GovHub-skills/3d30e7bd-45fc-4a77-9391-fbd2f2d4c167/scratchpad
# 1) toda URL do CDN citada no catálogo responde 200
grep -o 'https://cdn.jsdelivr.net/gh/GovHub-br/skills-assets@main/graphic-elements/[a-z-]*\.svg' "$CAT" | sort -u | while read u; do
  code=$(curl -s -o /dev/null -w '%{http_code}' "$u"); echo "$code $u"; [ "$code" = 200 ]
done
# 2) os 8 nomes aparecem na tabela
for n in capa encerramento capa-capitulo capa-capitulo-alternativa pagina-comum pagina-comum-com-enfase elementos-graficos outros-elementos-graficos; do
  grep -q "\`$n.svg\`" "$CAT" || { echo "faltou $n"; exit 1; }
done
# 3) extrai cada bloco ```svg do catálogo, renderiza com cairosvg em roxo e monta folha de contato
python3 - <<'PY'
import re, cairosvg, os
from PIL import Image, ImageDraw
OUT=os.environ.get('OUT') or '/tmp/claude-1000/-home-joaoegewarth-GovHub-skills/3d30e7bd-45fc-4a77-9391-fbd2f2d4c167/scratchpad'
src=open('01-govhub/govhub-visual-identity/references/graphic-elements-catalog.md').read()
blocks=re.findall(r'```svg\n(.*?)```', src, re.S)
assert len(blocks)==8, f'esperava 8 snippets svg, achei {len(blocks)}'
tiles=[]
for i,b in enumerate(blocks):
    svg=b.replace('currentColor','#613EFF')
    png=f'{OUT}/shape-{i}.png'
    cairosvg.svg2png(bytestring=svg.encode(), write_to=png, output_width=200, background_color='#FFE7E1')
    tiles.append(Image.open(png))
W=max(t.width for t in tiles); H=max(t.height for t in tiles)
sheet=Image.new('RGB',(4*(W+20)+20, 2*(H+20)+20),'white')
for i,t in enumerate(tiles): sheet.paste(t,(20+(i%4)*(W+20),20+(i//4)*(H+20)))
sheet.save(f'{OUT}/shapes-sheet.png'); print('shapes ok ->', f'{OUT}/shapes-sheet.png')
PY
echo "CATALOG OK"
EOF
chmod +x $OUT/test-catalog.sh
```

- [ ] **Step 2: Rodar o teste e confirmar que falha**

Run: `cd /home/joaoegewarth/GovHub-skills && $OUT/test-catalog.sh`
Expected: falha em `grep` (arquivo não existe).

- [ ] **Step 3: Escrever o catálogo**

Criar `01-govhub/govhub-visual-identity/references/graphic-elements-catalog.md` com este conteúdo:

````markdown
# Catálogo de elementos gráficos Gov Hub

Elementos gráficos propostos pela equipe de design para a identidade visual
atual. Como os ícones, **não ficam nesta skill**: vivem no repo público
[`GovHub-br/skills-assets`](https://github.com/GovHub-br/skills-assets) e são
servidos por CDN. Todos são SVG `1920×1080` (16:9), só formas vetoriais nas
cores da paleta, sem imagem embutida.

## URL

```
https://cdn.jsdelivr.net/gh/GovHub-br/skills-assets@main/graphic-elements/<nome>.svg
```

`@main` acompanha o repo (cache CDN de ~12 h). Para congelar uma versão
exata, troque `@main` por uma tag ou pelo SHA do commit.

Exemplo como fundo de slide:

```css
.gh-slide--content {
  background: url("https://cdn.jsdelivr.net/gh/GovHub-br/skills-assets@main/graphic-elements/pagina-comum.svg") center / cover no-repeat;
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
cp -r skills-assets/graphic-elements ./graphic-elements
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
4. Cores só da paleta; cada forma numa cor diferente do fundo. Rosa `#F9006F` no máximo numa forma pequena ou num número.
5. Texto na zona livre, oposta às formas. Chamada em **Oswald uppercase**; apoio em **Reddit Sans**. Sobre navy/roxo, texto branco; sobre pêssego, navy.
6. Logo Gov Hub na zona livre, respeitando a área de não-interferência (`SKILL.md`). Nunca sobre uma forma da mesma cor.
7. Rotação de formas só em múltiplos de 90°. Sem sombra, sem contorno, sem 3D.
8. Mosaico `outros-elementos-graficos.svg`: como **faixa** (topo ou rodapé de stories/poster, cortado com `object-fit: cover`) ou como textura de fundo inteira com `opacity` ≤ 0.4 e um bloco sólido atrás do texto.

Exemplo de feed quadrado (1080×1080):

```html
<div class="gh-post" style="position:relative;width:1080px;height:1080px;overflow:hidden;background:#0A005A;color:#fff;font-family:'Reddit Sans',sans-serif">
  <svg class="gh-shape" viewBox="0 0 100 100" style="position:absolute;right:-10%;top:-10%;width:52%;color:#613EFF"><path fill="currentColor" d="M0 0h100a100 100 0 0 1-100 100z" transform="rotate(90 50 50)"/></svg>
  <svg class="gh-shape" viewBox="0 0 100 50" style="position:absolute;left:8%;bottom:0;width:26%;color:#EF41FF"><path fill="currentColor" fill-rule="evenodd" d="M0 0h100a50 50 0 0 1-100 0zM25.6 0h48.8a24.4 24.4 0 0 1-48.8 0z" transform="rotate(180 50 25)"/></svg>
  <svg class="gh-shape" viewBox="0 0 197 100" style="position:absolute;right:0;bottom:14%;width:22%;color:#FFE7E1"><path fill="currentColor" d="M197 0H50a50 50 0 0 0 0 100h147z"/></svg>
  <div style="position:absolute;left:80px;top:120px;width:560px">
    <h1 style="font:700 88px/1.05 'Oswald',sans-serif;text-transform:uppercase;margin:0 0 24px">Chamada da arte</h1>
    <p style="font-size:30px;line-height:1.4;margin:0;opacity:.92">Texto de apoio curto, uma ou duas linhas.</p>
  </div>
</div>
```

## Regras de uso (valem para todos os elementos)

- Não recolorir fora da paleta oficial; não aplicar sombra, contorno, 3D ou gradiente.
- Não esticar nem distorcer a proporção de um template; rotação só em múltiplos de 90°.
- Nunca usar `elementos-graficos.svg` ou `outros-elementos-graficos.svg` como fundo de slide.
- Texto sempre na zona livre do template (`slides.md`), nunca sobre uma forma de cor próxima à do texto.
- Em documentos (PDF/e-book), os elementos entram só como marca d'água **opcional**: `print-watermark.md`.

## Como adicionar um elemento novo

1. Subir o SVG `1920×1080` (ou o formato da peça) em `skills-assets/graphic-elements/` e dar push.
2. Acrescentar uma linha na tabela acima com categoria e "quando usar".
3. Se for um template de slide novo, adicionar a zona segura e o código do tipo em `slides.md`.
````

- [ ] **Step 4: Rodar o teste e confirmar que passa; inspecionar a folha de formas**

Run: `cd /home/joaoegewarth/GovHub-skills && $OUT/test-catalog.sh`
Expected: 8 linhas `200 https://...`, `shapes ok`, `CATALOG OK`.
Depois abrir `$OUT/shapes-sheet.png` (Read) e confirmar: círculo, anel com furo, semicírculo com lado reto em cima, quarto de círculo com canto reto no superior esquerdo, pílula, semi-pílula com lado reto à direita, meio-anel, quarto de anel. Se alguma forma sair errada (furo preenchido, arco invertido), corrigir o `d` do snippet e rodar de novo.

- [ ] **Step 5: Commit**

```bash
git add 01-govhub/govhub-visual-identity/references/graphic-elements-catalog.md
git commit -m "feat(visual-identity): catálogo de elementos gráficos servidos pelo CDN

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 2: Referência de slides

**Files:**
- Create: `01-govhub/govhub-visual-identity/references/slides.md`
- Test: `$OUT/deck/deck.html`, `$OUT/test-slides.sh` (temporários)

**Interfaces:**
- Consumes: URLs e nomes de template do catálogo (Task 1).
- Produces: classes `.gh-deck`, `.gh-slide`, modificadores `--cover`, `--section`, `--section-alt`, `--content`, `--emphasis`, `--closing`, e elementos `.gh-slide__title`, `.gh-slide__body`, `.gh-slide__logo`, `.gh-slide__num`, `.gh-slide__eyebrow`, `.gh-slide__kpi`. `SKILL.md` (Task 4) aponta para este arquivo.

- [ ] **Step 1: Escrever o teste: deck de 7 slides que usa o CSS do arquivo de referência**

O teste extrai o bloco ```css e o bloco ```html de `slides.md`, monta o deck, gera PDF com WeasyPrint e rasteriza cada página.

```bash
mkdir -p $OUT/deck && cat > $OUT/test-slides.sh <<'EOF'
#!/usr/bin/env bash
set -e
OUT=/tmp/claude-1000/-home-joaoegewarth-GovHub-skills/3d30e7bd-45fc-4a77-9391-fbd2f2d4c167/scratchpad
REF=01-govhub/govhub-visual-identity/references/slides.md
python3 - <<'PY'
import re, os, subprocess
OUT='/tmp/claude-1000/-home-joaoegewarth-GovHub-skills/3d30e7bd-45fc-4a77-9391-fbd2f2d4c167/scratchpad'
src=open('01-govhub/govhub-visual-identity/references/slides.md').read()
css=re.findall(r'```css\n(.*?)```', src, re.S)
html=re.findall(r'```html\n(.*?)```', src, re.S)
assert len(css)>=1 and len(html)>=6, f'css={len(css)} html={len(html)}'
page=f"<!doctype html><html><head><meta charset='utf-8'><style>{''.join(css)}</style></head><body><main class='gh-deck'>{''.join(html)}</main></body></html>"
open(f'{OUT}/deck/deck.html','w').write(page)
subprocess.run(['python3','-m','weasyprint',f'{OUT}/deck/deck.html',f'{OUT}/deck/deck.pdf'],check=True)
import pypdfium2 as pdfium
pdf=pdfium.PdfDocument(f'{OUT}/deck/deck.pdf')
n=len(pdf); print('pages',n)
assert n==len(html), f'{n} páginas para {len(html)} slides: algum slide estourou a página'
for i in range(n):
    w,h=pdf[i].get_size(); assert abs(w/h-16/9)<0.01, f'página {i+1} não é 16:9: {w}x{h}'
    pdf[i].render(scale=0.5).to_pil().save(f'{OUT}/deck/slide-{i+1}.png')
print('SLIDES OK')
PY
EOF
chmod +x $OUT/test-slides.sh
```

- [ ] **Step 2: Rodar e confirmar que falha**

Run: `cd /home/joaoegewarth/GovHub-skills && $OUT/test-slides.sh`
Expected: `FileNotFoundError` em `slides.md`.

- [ ] **Step 3: Escrever `slides.md`**

Conteúdo completo de `01-govhub/govhub-visual-identity/references/slides.md`:

````markdown
# Slides Gov Hub: código exato validado

Toda apresentação Gov Hub é um **HTML com uma `section.gh-slide` por
slide**, cada uma com **um dos seis templates** do
[catálogo de elementos gráficos](graphic-elements-catalog.md) como fundo,
exportado para PDF. Sem gradiente, sem fundo sólido inventado, sem
`elementos-graficos.svg` / `outros-elementos-graficos.svg` como fundo.

## Arquitetura

Canvas fixo `1920×1080px`, `@page` do mesmo tamanho e margem zero (mesma
ideia da `.gh-page` de `print-pages.md`: cada slide é uma caixa de tamanho
fixo que a impressão respeita). O template entra como `background` via URL
do CDN.

```css
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=Reddit+Sans:wght@400;500;600;700;800&display=swap');

:root {
  --primary-purple: #613EFF;
  --dark-navy:      #0A005A;
  --accent-magenta: #EF41FF;
  --accent-pink:    #F9006F;
  --bg-peach:       #FFE7E1;
  --text-body:      #2D3748;
  --font-family-base:    'Reddit Sans', 'Open Sans', sans-serif;
  --font-family-heading: 'Oswald', 'Reddit Sans', sans-serif;
}

@page { size: 1920px 1080px; margin: 0; }
html, body { margin: 0; padding: 0; }
body { font-family: var(--font-family-base); color: var(--text-body); }

.gh-slide {
  position: relative; width: 1920px; height: 1080px; overflow: hidden;
  page-break-after: always; break-after: page;
  background-position: center; background-size: cover; background-repeat: no-repeat;
}
.gh-slide:last-child { page-break-after: auto; break-after: auto; }

/* um template por tipo de slide (URLs literais: WeasyPrint/Chrome não resolvem var() dentro de url()) */
.gh-slide--cover       { background-image: url("https://cdn.jsdelivr.net/gh/GovHub-br/skills-assets@main/graphic-elements/capa.svg"); color: #fff; }
.gh-slide--section     { background-image: url("https://cdn.jsdelivr.net/gh/GovHub-br/skills-assets@main/graphic-elements/capa-capitulo.svg"); color: #fff; }
.gh-slide--section-alt { background-image: url("https://cdn.jsdelivr.net/gh/GovHub-br/skills-assets@main/graphic-elements/capa-capitulo-alternativa.svg"); color: #fff; }
.gh-slide--content     { background-image: url("https://cdn.jsdelivr.net/gh/GovHub-br/skills-assets@main/graphic-elements/pagina-comum.svg"); }
.gh-slide--emphasis    { background-image: url("https://cdn.jsdelivr.net/gh/GovHub-br/skills-assets@main/graphic-elements/pagina-comum-com-enfase.svg"); }
.gh-slide--closing     { background-image: url("https://cdn.jsdelivr.net/gh/GovHub-br/skills-assets@main/graphic-elements/encerramento.svg"); color: #fff; }

/* ---- capa e encerramento ---- */
.gh-slide--cover .gh-slide__block,
.gh-slide--closing .gh-slide__block {
  position: absolute; top: 50%; transform: translateY(-45%);
}
.gh-slide--cover   .gh-slide__block { left: 120px; width: 1000px; }
.gh-slide--closing .gh-slide__block { left: 900px; right: 120px; }
.gh-slide__logo-big { display: block; height: 72px; width: auto; margin-bottom: 56px; }
.gh-slide__h1 {
  font-family: var(--font-family-heading); font-weight: 700; text-transform: uppercase;
  font-size: 96px; line-height: 1.05; margin: 0 0 28px; color: #fff;
}
.gh-slide__lead { font-size: 36px; line-height: 1.4; margin: 0; opacity: .92; max-width: 30ch; }
.gh-slide__partners { position: absolute; right: 120px; bottom: 64px; display: flex; gap: 40px; align-items: center; }
.gh-slide__partners img { height: 56px; width: auto; }

/* ---- abertura de seção ---- */
.gh-slide--section .gh-slide__block,
.gh-slide--section-alt .gh-slide__block {
  position: absolute; left: 160px; right: 160px; top: 380px; bottom: 160px;
}
.gh-slide__num {
  font-family: var(--font-family-heading); font-weight: 700;
  font-size: 200px; line-height: 1; color: #fff; opacity: .75; margin: 0 0 8px;
}
.gh-slide__eyebrow {
  font-size: 28px; font-weight: 600; letter-spacing: .12em; text-transform: uppercase;
  margin: 0 0 16px; opacity: .85;
}
.gh-slide--section .gh-slide__h1,
.gh-slide--section-alt .gh-slide__h1 { font-size: 88px; max-width: 18ch; }

/* ---- conteúdo e ênfase ---- */
.gh-slide__title {
  position: absolute; left: 60px; top: 74px; height: 73px;
  font-family: var(--font-family-heading); font-weight: 600; text-transform: uppercase;
  font-size: 34px; line-height: 73px; color: var(--dark-navy);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.gh-slide--content  .gh-slide__title { max-width: 600px; }
.gh-slide--emphasis .gh-slide__title { max-width: 820px; }
.gh-slide__body {
  position: absolute; top: 220px; left: 120px; right: 120px; bottom: 100px;
  font-size: 30px; line-height: 1.45; color: var(--text-body);
}
.gh-slide--emphasis .gh-slide__body { right: 760px; bottom: 260px; }
.gh-slide__body h2 { font-family: var(--font-family-heading); text-transform: uppercase; font-size: 44px; color: var(--primary-purple); margin: 0 0 24px; }
.gh-slide__body ul { margin: 0; padding-left: 1.1em; }
.gh-slide__body li { margin-bottom: .5em; }
.gh-slide__body table { border-collapse: collapse; width: 100%; font-size: 26px; background: #fff; }
.gh-slide__body th { background: var(--primary-purple); color: #fff; text-align: left; padding: 14px 20px; }
.gh-slide__body td { padding: 12px 20px; border-bottom: 1px solid #e6dcd8; }
.gh-slide__kpi {
  font-family: var(--font-family-heading); font-weight: 700;
  font-size: 150px; line-height: 1; color: var(--accent-pink); margin: 0 0 16px;
}
.gh-slide__quote { font-size: 44px; line-height: 1.35; font-weight: 500; color: var(--dark-navy); margin: 0; max-width: 24ch; }
.gh-slide__logo-small { position: absolute; right: 120px; bottom: 48px; height: 40px; width: auto; }
```

## Ordem canônica de um deck

1. `--cover` (1 slide).
2. Para cada seção: `--section` na 1ª, `--section-alt` na 2ª, `--section` na 3ª... (alternando), seguido de `--content` × N e, se a seção tiver um destaque, **um** `--emphasis`.
3. `--closing` (1 slide).

Um deck sem seções (curto) é `--cover` → `--content` × N → `--closing`.

## HTML de cada tipo (copie e troque só o texto)

Capa. Logo branca (`references/logo/`, versão light) acima do título, como
na capa PDF:

```html
<section class="gh-slide gh-slide--cover">
  <div class="gh-slide__block">
    <img class="gh-slide__logo-big" src="logo/horizontal-light.svg" alt="Gov Hub">
    <h1 class="gh-slide__h1">Título da apresentação</h1>
    <p class="gh-slide__lead">Subtítulo ou contexto em uma ou duas linhas. Evento, data, equipe.</p>
  </div>
</section>
```

Abertura de seção (numeral + eyebrow + título, o mesmo padrão de
`print-header.md`):

```html
<section class="gh-slide gh-slide--section">
  <div class="gh-slide__block">
    <p class="gh-slide__num">01</p>
    <p class="gh-slide__eyebrow">Seção</p>
    <h1 class="gh-slide__h1">Título da primeira seção</h1>
  </div>
</section>
```

Abertura de seção alternativa (a próxima seção):

```html
<section class="gh-slide gh-slide--section-alt">
  <div class="gh-slide__block">
    <p class="gh-slide__num">02</p>
    <p class="gh-slide__eyebrow">Seção</p>
    <h1 class="gh-slide__h1">Título da segunda seção</h1>
  </div>
</section>
```

Conteúdo padrão. O título vai **dentro da pílula** (cabe ~28 caracteres em
Oswald 34px; se passar disso, encurte o título, não diminua a fonte):

```html
<section class="gh-slide gh-slide--content">
  <div class="gh-slide__title">Título curto na pílula</div>
  <div class="gh-slide__body">
    <h2>Subtítulo opcional</h2>
    <ul>
      <li>Primeiro ponto do slide, uma frase objetiva.</li>
      <li>Segundo ponto, com o mesmo tamanho de frase.</li>
      <li>Terceiro ponto. No máximo cinco por slide.</li>
    </ul>
  </div>
  <img class="gh-slide__logo-small" src="logo/horizontal-dark.svg" alt="">
</section>
```

Conteúdo com tabela (mesmo template; tabela com fundo branco sobre o pêssego):

```html
<section class="gh-slide gh-slide--content">
  <div class="gh-slide__title">Resultados por etapa</div>
  <div class="gh-slide__body">
    <table>
      <thead><tr><th>Etapa</th><th>Entregas</th><th>Status</th></tr></thead>
      <tbody>
        <tr><td>Diagnóstico</td><td>3</td><td>Concluído</td></tr>
        <tr><td>Pipeline</td><td>5</td><td>Em andamento</td></tr>
        <tr><td>Painel</td><td>2</td><td>Planejado</td></tr>
      </tbody>
    </table>
  </div>
  <img class="gh-slide__logo-small" src="logo/horizontal-dark.svg" alt="">
</section>
```

Ênfase (número-chave ou citação; corpo limitado aos ~60 % da esquerda):

```html
<section class="gh-slide gh-slide--emphasis">
  <div class="gh-slide__title">Título curto na pílula</div>
  <div class="gh-slide__body">
    <p class="gh-slide__kpi">87%</p>
    <p class="gh-slide__quote">das bases integradas passaram a ter documentação de colunas.</p>
  </div>
</section>
```

Encerramento (texto na metade direita; logos dos parceiros na ordem fixa
Lab Livre → UnB, de `references/logo/parceiros/`):

```html
<section class="gh-slide gh-slide--closing">
  <div class="gh-slide__block">
    <h1 class="gh-slide__h1">Obrigado</h1>
    <p class="gh-slide__lead">gov-hub.io<br>contato@gov-hub.io</p>
  </div>
  <div class="gh-slide__partners">
    <img src="logo/parceiros/lab-livre.png" alt="Lab Livre">
    <img src="logo/parceiros/unb.png" alt="UnB">
  </div>
</section>
```

## Zonas seguras (px no canvas 1920×1080)

Derivadas da geometria dos SVGs. Texto **fora** delas colide com as formas.

| Template | Zona de texto | Ocupada pelas formas |
|---|---|---|
| `capa` | `x 120–1120`, altura toda | `x > 1280` (quarto de círculo roxo), topo `x 1107–1608, y < 274` (meio-anel), rodapé `x > 1167, y > 782` (pílula) |
| `capa-capitulo` / `alternativa` | `x 160–1760, y 380–920` (dentro da moldura inset 75px) | canto superior esquerdo `x < 749, y < 283`; topo `x 510–995, y < 186`; canto inferior direito `x > 1670, y > 860` |
| `pagina-comum` | título `x 60–660, y 74–147`; corpo `x 120–1800, y 220–980` | só a pílula do título |
| `pagina-comum-com-enfase` | título `x 60–880, y 74–147`; corpo `x 120–1160, y 220–820` | canto superior direito `x > 1700, y < 250`; rodapé direito `x > 925, y > 798` |
| `encerramento` | `x 900–1800`, altura toda | `x < 640` (quarto de círculo roxo), topo `x < 753, y < 298` (pílula), rodapé `x 312–813, y > 806` (meio-anel) |

## Tipografia e cor nos slides

- Títulos e numerais: **Oswald**, uppercase. Corpo: **Reddit Sans**.
- Sobre pêssego (`--content`, `--emphasis`): texto navy/`--text-body`, subtítulos roxo. Sobre navy e roxo (`--cover`, `--section*`, `--closing`): texto branco.
- Rosa `#F9006F` só no número-chave do slide de ênfase (um por slide).
- Tabelas e cards com fundo **branco** sobre o pêssego (o pêssego não é fundo de tabela).
- Logo: grande só na capa (branca); pequena no canto inferior direito dos slides de conteúdo (navy sobre pêssego). Sem logo nas aberturas de seção e no slide de ênfase (as formas já ocupam o canto).

## Exportar para PDF

WeasyPrint (funciona sem navegador; renderiza SVG de fundo e fontes do Google):

```bash
pip install --user weasyprint pypdfium2
python3 -m weasyprint deck.html deck.pdf
```

Chrome headless, se disponível:

```bash
chrome --headless --no-pdf-header-footer --print-to-pdf=deck.pdf deck.html
```

## Conferência visual obrigatória

Como em `print-pages.md`: rasterize **todas** as páginas e olhe cada uma.
Erros que só aparecem olhando: título maior que a pílula (cortado com
reticências), corpo invadindo as formas do slide de ênfase, slide que virou
duas páginas por overflow.

```python
import pypdfium2 as pdfium
pdf = pdfium.PdfDocument("deck.pdf")
for i, page in enumerate(pdf):
    page.render(scale=0.5).to_pil().save(f"slide-{i+1}.png")
```

Checklist por slide: (1) número de páginas do PDF = número de `.gh-slide`;
(2) texto inteiro dentro da zona segura do template; (3) template certo para
o papel do slide (capa/seção/conteúdo/ênfase/encerramento); (4) seções
consecutivas alternando `--section` / `--section-alt`.

## Erros a evitar

- Fundo sólido ou gradiente no lugar de um template (instrução antiga desta skill, revogada).
- Usar `elementos-graficos.svg` ou `outros-elementos-graficos.svg` como fundo de slide.
- Título de conteúdo maior que a pílula (reduzir o texto, não a fonte).
- Dois slides de ênfase seguidos, ou ênfase sem número/citação (vira slide comum).
- Texto do slide de ênfase passando de `x 1160` ou `y 820`.
- `var()` dentro de `url()`: os motores de PDF não resolvem; use a URL literal.
````

- [ ] **Step 4: Rodar o teste, inspecionar os 7 PNGs**

Run: `cd /home/joaoegewarth/GovHub-skills && $OUT/test-slides.sh`
Expected: `pages 7`, `SLIDES OK`. As `<img src="logo/...">` vão dar `WARNING: Failed to load image` (caminho relativo ao scratchpad): aceitável no teste, ou copiar `references/logo` para `$OUT/deck/logo` antes de rodar para ver as logos. Abrir `$OUT/deck/slide-1.png` … `slide-7.png` (Read) e checar o checklist da seção "Conferência visual": texto dentro das zonas seguras, pílula com o título inteiro, ênfase sem colisão com as formas. Ajustar valores de CSS no `slides.md` se algo colidir e rodar de novo até passar.

- [ ] **Step 5: Commit**

```bash
git add 01-govhub/govhub-visual-identity/references/slides.md
git commit -m "feat(visual-identity): referência de slides com os templates oficiais

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 3: Marca d'água opcional em documentos

**Files:**
- Create: `01-govhub/govhub-visual-identity/references/print-watermark.md`
- Test: `$OUT/wm/wm.html`, `$OUT/test-watermark.sh` (temporários)

**Interfaces:**
- Consumes: snippets `gh-shape--quartoanel` / `gh-shape--quarto` do catálogo (Task 1); arquitetura `.gh-page` de `print-pages.md` (existente).
- Produces: classe `.gh-watermark` e modificadores `--topo`; pergunta padrão que `SKILL.md` (Task 4) manda fazer.

- [ ] **Step 1: Escrever o teste: duas páginas A4 (texto e tabela) com a marca d'água do arquivo**

```bash
mkdir -p $OUT/wm && cat > $OUT/test-watermark.sh <<'EOF'
#!/usr/bin/env bash
set -e
python3 - <<'PY'
import re, subprocess
OUT='/tmp/claude-1000/-home-joaoegewarth-GovHub-skills/3d30e7bd-45fc-4a77-9391-fbd2f2d4c167/scratchpad'
src=open('01-govhub/govhub-visual-identity/references/print-watermark.md').read()
css=''.join(re.findall(r'```css\n(.*?)```', src, re.S))
html=re.findall(r'```html\n(.*?)```', src, re.S)
assert html, 'sem bloco html no arquivo'
assert 'opacity: .07' in css or 'opacity:.07' in css, 'opacidade padrão deve ser .07'
assert 'Quer marca d' in src, 'falta a pergunta obrigatória'
base="""@page{size:210mm 297mm;margin:0}html,body{margin:0}
.gh-page{position:relative;width:210mm;height:297mm;overflow:hidden;page-break-after:always;background:#fff;font-family:sans-serif;color:#2D3748}
.gh-page__content{position:relative;z-index:1;padding:25mm 20mm;font-size:11pt;line-height:1.5}
table{border-collapse:collapse;width:100%}th{background:#613EFF;color:#fff;padding:6px}td{padding:6px;border-bottom:1px solid #ddd}"""
lorem='<p>'+('Texto corrido de exemplo para conferir a legibilidade sobre a marca d\'água. '*12)+'</p>'
rows=''.join(f'<tr><td>Linha {i}</td><td>{i*3}</td><td>ok</td></tr>' for i in range(1,30))
p1=html[0].replace('<!-- CONTEÚDO -->', lorem*4)
p2=html[0].replace('<!-- CONTEÚDO -->', f'<table><tr><th>Item</th><th>Valor</th><th>Status</th></tr>{rows}</table>').replace('gh-watermark"','gh-watermark gh-watermark--topo"')
open(f'{OUT}/wm/wm.html','w').write(f"<!doctype html><html><head><meta charset='utf-8'><style>{base}{css}</style></head><body>{p1}{p2}</body></html>")
subprocess.run(['python3','-m','weasyprint',f'{OUT}/wm/wm.html',f'{OUT}/wm/wm.pdf'],check=True)
import pypdfium2 as pdfium
pdf=pdfium.PdfDocument(f'{OUT}/wm/wm.pdf'); assert len(pdf)==2, len(pdf)
for i in range(2): pdf[i].render(scale=1).to_pil().save(f'{OUT}/wm/page-{i+1}.png')
print('WATERMARK OK')
PY
EOF
chmod +x $OUT/test-watermark.sh
```

- [ ] **Step 2: Rodar e confirmar que falha**

Run: `cd /home/joaoegewarth/GovHub-skills && $OUT/test-watermark.sh`
Expected: `FileNotFoundError` em `print-watermark.md`.

- [ ] **Step 3: Escrever `print-watermark.md`**

````markdown
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
````

- [ ] **Step 4: Rodar o teste e inspecionar as 2 páginas**

Run: `cd /home/joaoegewarth/GovHub-skills && $OUT/test-watermark.sh`
Expected: `WATERMARK OK`. Abrir `$OUT/wm/page-1.png` e `page-2.png`: forma roxa discreta no canto inferior direito (p.1) e superior direito (p.2); texto e tabela legíveis; forma atrás da tabela.

- [ ] **Step 5: Commit**

```bash
git add 01-govhub/govhub-visual-identity/references/print-watermark.md
git commit -m "feat(visual-identity): marca d'água opcional com elementos gráficos em PDF

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 4: Integrar no `SKILL.md`

**Files:**
- Modify: `01-govhub/govhub-visual-identity/SKILL.md` (frontmatter `description`; bullet "Elementos gráficos de apoio" ~linha 30; seção "### 3. Slides / e-mail / dashboard" ~linha 120; seção 4 passo 0 ~linha 129; seção "## Diretrizes de marca" último bullet; lista "## Referências")
- Test: `$OUT/test-skill.sh`

**Interfaces:**
- Consumes: os três arquivos das Tasks 1 a 3.

- [ ] **Step 1: Escrever o teste**

```bash
cat > $OUT/test-skill.sh <<'EOF'
#!/usr/bin/env bash
set -e
S=01-govhub/govhub-visual-identity/SKILL.md
R=01-govhub/govhub-visual-identity/references
for f in graphic-elements-catalog.md slides.md print-watermark.md; do
  [ -f "$R/$f" ] || { echo "falta $R/$f"; exit 1; }
  grep -q "references/$f" "$S" || { echo "SKILL.md não referencia $f"; exit 1; }
done
grep -q "slides Gov Hub" "$S" || { echo "falta gatilho 'slides Gov Hub'"; exit 1; }
grep -q "marca d'água govhub" "$S" || { echo "falta gatilho marca d'água"; exit 1; }
grep -q "post instagram govhub" "$S" || { echo "falta gatilho instagram"; exit 1; }
grep -qi "capa com o gradiente da marca" "$S" && { echo "instrução antiga de gradiente ainda presente"; exit 1; }
grep -q "references/graphic-elements/" "$S" "$R"/*.md && { echo "referência a pasta local removida"; exit 1; }
grep -q "Quer marca d" "$S" || { echo "falta a pergunta de marca d'água"; exit 1; }
grep -q "### 5. Comunicação" "$S" || { echo "falta seção 5"; exit 1; }
head -1 "$S" | grep -q '^---$' || { echo "frontmatter quebrado"; exit 1; }
[ "$(wc -l < "$S")" -lt 400 ] || { echo "SKILL.md longo demais"; exit 1; }
echo "SKILL OK"
EOF
chmod +x $OUT/test-skill.sh
```

- [ ] **Step 2: Rodar e confirmar que falha**

Run: `cd /home/joaoegewarth/GovHub-skills && $OUT/test-skill.sh`
Expected: `SKILL.md não referencia graphic-elements-catalog.md`.

- [ ] **Step 3: Editar o frontmatter**

Na `description`, trocar o trecho final

```
  estilo do livro do Gov Hub", "e-book com capítulos Gov Hub". Cobre
  estilização de relatório, site, PDF, e-book, framework numerado, slide,
  componente, e-mail e dashboard.
```

por

```
  estilo do livro do Gov Hub", "e-book com capítulos Gov Hub", "slides Gov
  Hub", "apresentação govhub", "post instagram govhub", "poster govhub",
  "elementos gráficos govhub", "marca d'água govhub". Cobre estilização de
  relatório, site, PDF, e-book, framework numerado, slides (templates
  oficiais), peças de comunicação (Instagram, poster, banner), componente,
  e-mail e dashboard.
```

- [ ] **Step 4: Editar o bullet de elementos gráficos no topo**

Trocar

```
- **Elementos gráficos de apoio:** círculo, anel/donut, semicírculo, quarto
  de círculo e pílula (retângulo 100% arredondado) — nunca ilustrações
  figurativas.
```

por

```
- **Elementos gráficos de apoio:** círculo, anel/donut, semicírculo, quarto
  de círculo e pílula (retângulo 100% arredondado), nunca ilustrações
  figurativas. Os arquivos oficiais (6 templates de slide + folha de formas
  + padrão) são servidos por CDN e catalogados em
  [`references/graphic-elements-catalog.md`](references/graphic-elements-catalog.md).
```

- [ ] **Step 5: Reescrever a seção 3 e adicionar a seção 5**

Trocar a seção inteira

```
### 3. Slides / e-mail / dashboard

- **Slides:** capa com o gradiente da marca + Reddit Sans no corpo, Oswald uppercase nos títulos de impacto; roxo nos títulos; rosa num único destaque por slide.
- **E-mail:** cores inline (clientes de e-mail ignoram variáveis CSS) — use os hexadecimais literais: cabeçalho `#613EFF`, texto `#2D3748`, botão CTA `#F9006F`.
- **Dashboard:** roxo nos headers/KPIs principais; verde `#10B981` para positivo; fundos `#F7F7F7`/`#F8F9FA`/`#FFE7E1`.
```

por

```
### 3. Slides / e-mail / dashboard

- **Slides:** siga [`references/slides.md`](references/slides.md) ao pé da
  letra. **Todo slide usa um dos 6 templates oficiais** do CDN como fundo
  (`capa`, `capa-capitulo`, `capa-capitulo-alternativa`, `pagina-comum`,
  `pagina-comum-com-enfase`, `encerramento`); o nome diz o papel. Sem
  gradiente, sem fundo inventado. HTML 1920×1080 por slide → PDF, com
  conferência visual de todas as páginas.
- **E-mail:** cores inline (clientes de e-mail ignoram variáveis CSS): use os hexadecimais literais: cabeçalho `#613EFF`, texto `#2D3748`, botão CTA `#F9006F`.
- **Dashboard:** roxo nos headers/KPIs principais; verde `#10B981` para positivo; fundos `#F7F7F7`/`#F8F9FA`/`#FFE7E1`.
```

E, logo **antes** de `## Acessibilidade (obrigatório)`, inserir:

```
### 5. Comunicação: Instagram, poster, banner

Peças fora do 16:9 **não esticam** os templates de slide: recomponha com as
formas isoladas (snippets prontos) e as regras de composição da seção
"Comunicação" de
[`references/graphic-elements-catalog.md`](references/graphic-elements-catalog.md):
fundo sólido navy/roxo/pêssego, 2 a 4 formas sangrando pelas bordas, forma
principal com 40 a 50 % do lado menor, texto na zona livre, Oswald na
chamada e Reddit Sans no apoio.
```

- [ ] **Step 6: Adicionar o passo da marca d'água na seção 4**

Logo após o item `0.` (que termina em `[`references/print-frontmatter.md`](references/print-frontmatter.md).`), inserir um novo item antes do `1.`:

```
0b. **Pergunte também** se quer marca d'água com os elementos gráficos do
   Gov Hub nas páginas de conteúdo ("Quer marca d'água com os elementos
   gráficos do Gov Hub nas páginas de conteúdo? (padrão: não)"). Só aplique
   com "sim" explícito; código, opacidade e restrições em
   [`references/print-watermark.md`](references/print-watermark.md).
```

- [ ] **Step 7: Atualizar o último bullet de "Diretrizes de marca" e a lista de referências**

Trocar

```
- Elementos gráficos de apoio: círculo, anel/donut, semicírculo, quarto de círculo e pílula — derivados de "círculos, semicírculos e retângulos arredondados" (ver `component-recipes.md`).
```

por

```
- Elementos gráficos de apoio: círculo, anel/donut, semicírculo, quarto de círculo e pílula, derivados de "círculos, semicírculos e retângulos arredondados" (ver `component-recipes.md`). Arquivos oficiais e snippets em `graphic-elements-catalog.md`; em documento, só como marca d'água opcional (`print-watermark.md`).
```

Na lista `## Referências (progressive disclosure)`, inserir logo após a entrada de `print-table.md`:

```
- [`references/print-watermark.md`](references/print-watermark.md) — marca d'água **opcional** em páginas de conteúdo de PDF (uma forma isolada no canto, roxo a 7 %). Pergunte antes; padrão sem. Nunca em capa, folha de identificação, índice ou encerramento.
- [`references/slides.md`](references/slides.md) — **comece por aqui para qualquer apresentação**: arquitetura HTML 1920×1080 → PDF, os 6 templates oficiais como fundo (um por tipo de slide, ordem canônica capa → seção/seção-alt → conteúdo → ênfase → encerramento), zonas seguras de texto de cada template, código exato de cada tipo, exportação e conferência visual.
- [`references/graphic-elements-catalog.md`](references/graphic-elements-catalog.md) — os 8 elementos gráficos oficiais (**servidos por CDN** a partir de `GovHub-br/skills-assets`, não são arquivos locais): tabela de quando usar cada um, snippets SVG das formas isoladas, formatos e regras de recomposição para Instagram/poster/banner, e como adicionar um elemento novo.
```

- [ ] **Step 8: Rodar o teste**

Run: `cd /home/joaoegewarth/GovHub-skills && $OUT/test-skill.sh`
Expected: `SKILL OK`.

- [ ] **Step 9: Commit**

```bash
git add 01-govhub/govhub-visual-identity/SKILL.md
git commit -m "feat(visual-identity): integra elementos gráficos, slides e marca d'água no SKILL.md

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 5: Verificação final ponta a ponta

**Files:**
- Nenhum arquivo novo. Reexecuta os testes das Tasks 1 a 4 e a inspeção visual.

- [ ] **Step 1: Rodar todos os scripts**

Run:
```bash
cd /home/joaoegewarth/GovHub-skills && $OUT/test-catalog.sh && $OUT/test-slides.sh && $OUT/test-watermark.sh && $OUT/test-skill.sh
```
Expected: `CATALOG OK`, `SLIDES OK`, `WATERMARK OK`, `SKILL OK`.

- [ ] **Step 2: Inspeção visual final**

Abrir (Read) `$OUT/shapes-sheet.png`, `$OUT/deck/slide-1.png` a `slide-7.png`, `$OUT/wm/page-1.png` e `page-2.png`. Registrar no relatório final o que foi visto, página por página, e qualquer ajuste feito.

- [ ] **Step 3: Conferir a árvore de git**

Run: `git status --short && git log --oneline main..HEAD`
Expected: árvore limpa; 4 commits de feature + 1 de spec + 1 de plano na branch `feat/govhub-visual-identity`.
