# Elementos gráficos Gov Hub na skill `govhub-visual-identity` — design

Data: 2026-09-16. Branch: `feat/govhub-visual-identity`.

## Objetivo

Incorporar à skill `01-govhub/govhub-visual-identity` os 8 elementos gráficos
propostos pela equipe de design (SVGs 1920×1080 na paleta oficial) para:

1. **Slides** — todo slide de apresentação Gov Hub usa obrigatoriamente um dos
   6 templates; a nomenclatura do arquivo define quando usar.
2. **Comunicação** (Instagram, poster, banner) — as formas isoladas servem de
   referência de composição, sem esticar os templates 16:9.
3. **Documentos** (PDF/e-book/relatório) — marca d'água **opcional**, com
   transparência; a skill pergunta ao usuário antes de aplicar.

O catálogo é extensível: novos elementos entram subindo o SVG no CDN e
adicionando uma linha na tabela do catálogo.

## Decisões tomadas com o usuário

| Decisão | Escolha |
|---|---|
| Formato de slides | HTML 16:9 (`div` 1920×1080 por slide) exportado para PDF via Chrome headless, mesma arquitetura de `print-pages.md`. Sem PPTX, sem Figma. |
| Hospedagem dos SVGs | CDN `GovHub-br/skills-assets` (jsDelivr), igual aos ícones. Pasta `graphic-elements/` no repo, commit preparado no clone local `~/skills-assets` para o usuário dar push. |
| Pasta local `references/graphic-elements/` | Removida da skill após publicação (mesmo padrão dos ícones). |
| Marca d'água padrão | Uma forma isolada por página (quarto de círculo ou anel grande sangrando num canto), roxo com opacidade baixa. Mosaico não é o padrão. |
| Organização na skill | Opção A: 3 referências novas + edições pontuais no `SKILL.md`. |

## Inventário dos elementos

Todos `1920×1080`, `viewBox="0 0 1920 1080"`, sem `<image>` embutida, só
`<rect>`/`<path>` com fills da paleta (`#0A005A`, `#613EFF`, `#EF41FF`,
`#F9006F`, `#FFE7E1`).

| Arquivo | Descrição visual | Classificação |
|---|---|---|
| `capa.svg` | Fundo navy; grande quarto de círculo roxo na direita; meio-anel magenta sangrando pelo topo; pílula pêssego sangrando pela direita no rodapé. Lado esquerdo livre. | Slide 1 (capa) |
| `encerramento.svg` | Espelho da capa: formas na esquerda, lado direito livre. | Último slide |
| `capa-capitulo.svg` | Fundo roxo; moldura arredondada fina **magenta** inset ~75px; quarto de círculo navy no canto superior esquerdo; meio-anel pêssego no topo; quarto de anel magenta no canto inferior direito. | Abertura de seção |
| `capa-capitulo-alternativa.svg` | Igual, com moldura e quarto de anel **pêssego** e meio-anel magenta. | Abertura de seção (alternar com a anterior) |
| `pagina-comum.svg` | Fundo pêssego; pílula magenta no topo esquerdo (`x 0–688, y 74–147`). | Slide de conteúdo |
| `pagina-comum-com-enfase.svg` | Fundo pêssego; pílula magenta mais larga (`x 0–899`); quarto de anel roxo no canto superior direito; quarto de círculo navy no canto inferior direito (`y ≥ 798, x ≥ 1171`); meio-anel magenta no rodapé (`x 925–1410`). | Slide de destaque |
| `elementos-graficos.svg` | Folha de referência: pílula, quarto de círculo, círculo, anel, semi-pílula, pílula rosa, sobre pêssego. | **Não é slide** — fonte das formas isoladas |
| `outros-elementos-graficos.svg` | Mosaico de ~98 formas pequenas (navy/roxo/magenta) sobre pêssego. | **Não é slide** — textura para comunicação |

## Arquitetura da mudança

### 1. CDN — `~/skills-assets/graphic-elements/`

- Copiar os 8 SVGs com os nomes atuais. Commit no clone local; push é do usuário.
- URL-base: `https://cdn.jsdelivr.net/gh/GovHub-br/skills-assets@main/graphic-elements/<nome>.svg`.

### 2. `references/graphic-elements-catalog.md` (novo)

Mesmo formato do `icons-catalog.md`:

- URL-base e padrão de nome; nota sobre `@main` vs tag/SHA.
- Tabela do inventário acima com "quando usar".
- Uso sem internet: `git clone --depth 1` do `skills-assets` e `src`/`url()` relativo.
- **Formas isoladas**: os 6 `<path>` de `elementos-graficos.svg` transcritos
  como snippets SVG independentes (cada um num `<svg viewBox>` próprio, com
  `fill="currentColor"` para recolorir via CSS dentro da paleta).
- **Comunicação**: formatos canônicos (feed 1080×1080, retrato 1080×1350,
  stories 1080×1920, poster A4/A3 retrato) e regras de recomposição:
  - Nunca esticar um template 16:9 para outra proporção.
  - Fundo sólido em navy, roxo ou pêssego; 2 a 4 formas sangrando pelas
    bordas; forma principal ≈ 40–50 % do lado menor do canvas; demais formas
    menores; cores só da paleta; sem gradiente, sem rotação fora de 0/90/180/270°.
  - Texto na zona livre (oposta às formas); Oswald uppercase para chamada,
    Reddit Sans para apoio; rosa só num destaque.
  - Mosaico `outros-elementos-graficos` como faixa de fundo (stories, rodapé
    de poster) ou textura de página inteira com opacidade ≤ 40 % sob texto.
- **Regras de uso** (espelham as da logo): não recolorir fora da paleta, não
  aplicar sombra/3D/contorno, não sobrepor logo a uma forma de cor próxima.
- **Extensão**: como adicionar um elemento novo (subir SVG 1920×1080 no CDN,
  linha na tabela, se for template de slide adicionar zona segura em `slides.md`).

### 3. `references/slides.md` (novo)

- **Arquitetura**: `@page { size: 1920px 1080px; margin: 0 }`;
  `.gh-slide { width:1920px; height:1080px; position:relative; overflow:hidden;
  page-break-after: always; background: url(<CDN>/<template>.svg) center/cover no-repeat; }`
  com uma classe modificadora por template (`.gh-slide--cover`, `--section`,
  `--section-alt`, `--content`, `--emphasis`, `--closing`). Fontes via o mesmo
  `@import` de `tokens.css`. Exportação com Chrome headless (`--print-to-pdf`,
  `--no-pdf-header-footer`) e conferência visual obrigatória de cada página
  rasterizada (referência cruzada a `print-pages.md`).
- **Regra dura**: todo slide usa exatamente um dos 6 templates; sem fundo
  sólido inventado, sem gradiente (revoga a instrução antiga "capa com
  gradiente da marca").
- **Ordem canônica**: `capa` → [`capa-capitulo` / `capa-capitulo-alternativa`
  alternando a cada seção] → `pagina-comum` × N → `pagina-comum-com-enfase`
  para no máximo 1 destaque por seção (número-chave, citação, síntese) →
  `encerramento`.
- **Zonas seguras** (px no canvas 1920×1080), com o código exato de cada tipo:
  - `capa`: bloco de texto `left:120px; width:1000px`, centrado verticalmente
    (`top:50%; transform:translateY(-40%)`); logo branca acima do título;
    título Oswald 800 uppercase ~96px branco; subtítulo Reddit Sans ~36px
    branco `opacity:.92`.
  - `capa-capitulo` / `alternativa`: conteúdo `left:160px; right:160px;
    top:380px; bottom:160px`; numeral grande branco `opacity:.75` + eyebrow +
    título, mesmo padrão de `print-header.md`.
  - `pagina-comum`: título **dentro** da pílula: `position:absolute;
    left:60px; top:74px; height:73px; max-width:600px; line-height:73px;`
    Oswald 600 uppercase ~34px, cor navy. Corpo `top:220px; left:120px;
    right:120px; bottom:100px`, Reddit Sans ~30px, cor `--text-body`.
  - `pagina-comum-com-enfase`: título na pílula com `max-width:820px`; corpo
    `top:220px; left:120px; right:760px; bottom:260px`. Número-chave/citação
    pode usar `--accent-pink` ou navy em Oswald ~140px.
  - `encerramento`: bloco `left:900px; right:120px`, centrado verticalmente,
    branco; título + linhas de contato; logos de parceiros
    (`references/logo/parceiros/`, ordem Lab Livre → UnB) no rodapé direito.
- **Tipografia/cor**: Oswald uppercase em títulos, Reddit Sans no corpo;
  navy sobre pêssego, branco sobre navy/roxo; rosa só num destaque por slide;
  tabelas/cards conforme `component-recipes.md`, com fundo branco quando
  sobre pêssego.
- **Logo**: grande na capa; pequena (altura ~40px) no canto inferior direito
  dos slides de conteúdo (`right:120px; bottom:48px`), navy sobre pêssego e
  branca sobre navy/roxo. Nota de que os arquivos de logo seguem pendentes.
- **Erros a evitar** (lista curta): texto fora da zona segura colidindo com
  as formas; usar `elementos-graficos`/`outros-elementos-graficos` como fundo
  de slide; pílula do título com texto maior que a largura da pílula; mais
  de um slide de ênfase seguido.

### 4. `references/print-watermark.md` (novo)

- **Pergunta obrigatória** antes de gerar um documento com a skill: "Quer
  marca d'água com os elementos gráficos do Gov Hub nas páginas de conteúdo?"
  Padrão: **não**. Só aplica com "sim" explícito.
- **Implementação**: dentro de cada `.gh-page` de conteúdo, um `<svg
  class="gh-watermark">` com um dos paths isolados (quarto de círculo ou
  anel), `position:absolute; right:-15%; bottom:-15%; width:55%;
  fill:var(--primary-purple); opacity:.07; z-index:0; pointer-events:none;`
  conteúdo da página com `position:relative; z-index:1`.
- **Restrições**: nunca na capa, folha de identificação, índice ou
  encerramento; opacidade máxima 10 % (5 % sobre pêssego); em página que é
  só tabela larga, mover para o canto superior direito; um único elemento por
  página; cor só roxo ou navy.
- Inclui o procedimento de conferência: rasterizar 2 páginas (uma de texto,
  uma com tabela) e confirmar que a marca d'água não reduz legibilidade.

### 5. Edições no `SKILL.md`

- Frontmatter `description`: acrescentar gatilhos "slides Gov Hub",
  "apresentação govhub", "post instagram govhub", "poster govhub",
  "marca d'água govhub", "elementos gráficos govhub".
- Bloco "Elementos gráficos de apoio" no topo: apontar para o catálogo.
- Seção "3. Slides / e-mail / dashboard": trocar a linha de slides por
  "siga `references/slides.md`: cada slide usa um dos 6 templates do CDN;
  nunca gradiente". E-mail e dashboard ficam como estão.
- Seção 4 (documento longo): novo passo **0b** "pergunte se quer marca
  d'água (padrão não) → `print-watermark.md`".
- Nova subseção "5. Comunicação (Instagram, poster, banner)" apontando para a
  seção de comunicação do catálogo.
- Lista de referências: entradas para `graphic-elements-catalog.md`,
  `slides.md`, `print-watermark.md`.
- Remover a pasta `references/graphic-elements/` do repo da skill.

## Verificação

1. Deck de exemplo com 7 slides (capa, capítulo, capítulo-alt, 2 conteúdo,
   ênfase, encerramento) gerado em HTML seguindo `slides.md` ao pé da letra,
   exportado para PDF com Chrome headless (ou rasterizado com cairosvg/PIL se
   o Chrome não estiver disponível no ambiente), páginas rasterizadas e
   inspecionadas: texto dentro das zonas seguras, sem colisão com as formas.
2. Uma página `.gh-page` A4 de teste com marca d'água a 7 % rasterizada e
   inspecionada.
3. Todas as URLs do catálogo resolvem no CDN após o push do usuário (até lá,
   validar com os arquivos locais do clone).
4. `SKILL.md` continua abaixo do tamanho razoável (< ~350 linhas) e as
   referências novas seguem o padrão dos `print-*.md`.

## Fora de escopo

- PPTX, Figma Slides.
- Regerar ícones na paleta nova; atualizar arquivos de logo.
- Novos elementos gráficos (o usuário vai adicionar depois; o catálogo
  documenta como).
