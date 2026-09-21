---
name: lablivre-visual-identity
description: >-
  Use quando o usuário pedir para aplicar a identidade visual, cores, paleta,
  tema, estilo, marca ou "cara" do Lab Livre em qualquer artefato: relatório
  HTML/PDF, e-book ou framework numerado no estilo do livro Lab Livre, slides,
  post ou carrossel de Instagram/LinkedIn, poster, banner, página web,
  componente, dashboard, e-mail, tema CSS. Dispara com: "identidade visual
  lab livre", "tema lab livre", "cores/paleta do lab livre", "roxo do lab livre",
  "deixar com a cara do lab livre", "padrão lab livre", "slides lab livre", "post
  instagram lab livre", "elementos gráficos lab livre", "logo lab livre",
  "borboleta do lab livre", "lablivre".
---

# Lab Livre — Identidade Visual

Aplique a identidade visual **oficial** do Lab Livre (Laboratório de
Software Livre da UnB), definida no Manual de Identidade Visual (MIV) da
marca, em qualquer artefato. A marca é definida por um ícone de folha
estilizado (a "borboleta"), uma paleta em rampa do frio para o quente e a
combinação de uma tipografia geométrica pesada com uma condensada de apoio:

- **Roxo `#7023E8` como cor primária/assinatura** (o mais usado no ícone e
  em destaques).
- **Laranja `#F46B2F` como acento quente pontual** (CTA, contraponto ao
  roxo/azul; não abusar).
- **Azul profundo `#080056`** como cor-base: textos escuros, fundos
  institucionais sérios, contraste máximo.
- **Rosa-choque `#E52E70`** como acento secundário (transições de gradiente,
  rampa editorial).
- **Fundos claros** (neutros ou rosa claro `#FFE7E1`) e as fontes **Reddit
  Sans** (principal; logotipo em Black; Open Sans no Canva gratuito) +
  **Oswald** (apoio, só títulos/chamadas de impacto, uppercase + bold).
- **Elementos gráficos de apoio:** círculos, semicírculos e retângulos
  arredondados (círculo, anel/donut, semicírculo, quarto de círculo e
  pílula), repetidos em padronagem, nunca ilustrações figurativas.

> **Origem desta skill (2026-09-18):** é uma cópia da
> `govhub-visual-identity` com a paleta trocada pela do Lab Livre, feita
> porque o Lab Livre e o Gov Hub compartilham tipografia, elementos
> gráficos e toda a arquitetura de PDF/slides/posts. Os **nomes dos
> tokens** (`--dark-navy`, `--primary-purple`, `--accent-magenta`,
> `--accent-pink`, `--bg-peach`) e os prefixos de classe (`gh-`) foram
> mantidos de propósito: o código das referências funciona nas duas
> marcas, e um artefato troca de marca trocando só o `:root`. Nos textos,
> "navy" = azul profundo, "magenta" = rosa-choque, "rosa"/"pink" =
> laranja, "pêssego" = rosa claro.
>
> **O que ainda é do Gov Hub:** os assets do CDN (`skills-assets`: 8
> elementos gráficos, 332 ícones de produto, 100 templates de post) estão
> nas cores do Gov Hub; os catálogos avisam. E a pasta `references/logo/`
> tem só o que já existia em SVG (Lab Livre completa e borboleta em preto,
> azul e branco); as demais versões chegam depois, ver `partners.md`
> seção "Logo do Lab Livre: o que existe e o que falta".

## Antes de começar: pergunte pelo formato dos arquivos de origem

Quando o usuário fornecer arquivos para servirem de base ou serem
incorporados ao artefato (imagens, diagramas, tabelas, texto), **antes de
processá-los**, pare e pergunte se a pessoa tem esse mesmo conteúdo em um
formato mais fácil de processar — evita retrabalho e conversões frágeis.
Casos comuns:

- **Diagramas/fluxogramas/imagens em PDF**: peça PNG ou SVG se existir. Um
  PDF de diagrama pode exigir um motor de renderização externo pra extrair
  a imagem com fidelidade (aconteceu neste projeto: duas páginas de PDF
  exportadas do Figma vinham em branco em conversores nativos, e só
  renderizaram corretamente depois de instalar o Poppler) — enquanto um
  PNG ou SVG do mesmo diagrama é direto, sem conversão nenhuma.
- **Texto em `.docx`**: peça PDF ou `.md`/`.txt` se a pessoa tiver — a
  extração de texto de PDF ou Markdown é direta; `.docx` exige passos
  extras.
- **Regra geral**: se o arquivo que chegou é de um formato "difícil"
  (PDF de diagrama, `.docx`, planilha complexa, etc.), pergunte antes de
  começar a converter. Só siga direto com o formato recebido se a pessoa
  não tiver alternativa mais simples ou se o formato já for direto (PNG,
  SVG, `.md`, `.txt`, CSV).

## Design Tokens (fonte da verdade)

Injete este bloco no `:root` do artefato (dentro de `<style>` no `<head>`, ou no
topo do CSS). O arquivo completo e comentado está em
[`references/tokens.css`](references/tokens.css) — copie de lá quando quiser tudo.

```css
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=Reddit+Sans:wght@300;400;500;600;700;800;900&display=swap');

:root {
  /* Paleta oficial (MIV) */
  --primary-purple: #7023E8; /* ROXO — cor-assinatura */
  --dark-navy:      #080056; /* contraste máximo, títulos grandes, fundos escuros */
  --accent-magenta: #E52E70; /* acento secundário */
  --accent-pink:    #F46B2F; /* acento pontual (CTA) */
  --bg-peach:       #FFE7E1; /* fundo claro "de marca" */
  --text-white:     #FFFFFF;

  /* Estados derivados do primário */
  --purple-600: #5F1EC5; /* hover/foco */
  --purple-700: #4A17A0; /* active/pressionado */

  /* Neutros / texto */
  --text-strong: #202020;
  --text-body:   #2D3748;
  --text-muted:  #666666;

  /* Fundos */
  --bg-white:  #FFFFFF;
  --bg-light:  #F7F7F7;
  --bg-subtle: #F8F9FA;

  /* Semânticas */
  --color-success:   #10B981;
  --color-highlight: #FFD700;

  /* Tipografia: Reddit Sans (principal) + Oswald (apoio, só títulos/uppercase) */
  --font-family-base:    'Reddit Sans', 'Open Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-family-heading: 'Oswald', 'Reddit Sans', 'Open Sans', sans-serif;

  /* Sombras */
  --shadow-md: 0 2px 10px rgba(8,0,86,0.10);
  --shadow-lg: 0 4px 20px rgba(8,0,86,0.12);
  --shadow-xl: 0 8px 30px rgba(8,0,86,0.16);

  /* Transição padrão */
  --transition-normal: all 0.3s ease;

  --radius-sm: 6px; --radius-md: 10px; --radius-lg: 16px;
}
```

### Cor primária e como derivar estados

`--primary-purple` (`#7023E8`) é **sempre** a cor primária. Para estados:

- **Hover/foco:** `--purple-600` (`#5F1EC5`).
- **Active/pressionado:** `--purple-700` (`#4A17A0`).
- **Gradiente da marca:** `linear-gradient(135deg, #7023E8, #E52E70)` (roxo →
  rosa-choque) ou, no degradê completo do MIV, `linear-gradient(135deg,
  #080056, #7023E8, #E52E70, #F46B2F)`. Sempre do frio para o quente.

## Como aplicar por alvo

**O entregável final vai virar PDF?** Isso vale pra qualquer gênero de
documento — relatório técnico, dicionário de dados, e-book, framework
numerado — não só pros casos "estilo livro" da seção 4. Antes de desenhar
capa ou cabeçalho de página do zero, vá direto para
[`references/print-pages.md`](references/print-pages.md): ele define a
arquitetura de página (`.gh-page` full-bleed) que capa e cabeçalho de
capítulo usam **sempre**, mesmo quando o corpo do documento é longo demais
pra paginar à mão — nesse caso a dificuldade está em paginar o corpo, não
em desenhar a capa/cabeçalho, e o próprio arquivo documenta uma técnica
validada pra isso. Antes de gerar, pergunte também sobre a marca d'água
(padrão: não), ver [`references/print-watermark.md`](references/print-watermark.md).

### 1. HTML / relatório já existente

1. Adicione o bloco `:root` (acima) dentro de um `<style>` no `<head>`.
2. Aplique a fonte: `body { font-family: var(--font-family-base); color: var(--text-body); background: var(--bg-light); }`.
3. Troque a cor de **títulos** (`h1..h3`) para `var(--primary-purple)`; para chamadas de grande impacto, use `var(--font-family-heading)` + uppercase + bold.
4. Em **tabelas**, pinte o `thead th` com `background: var(--primary-purple); color: var(--text-white);` e alterne linhas com `var(--bg-subtle)`.
5. Em **badges/tags**, use `background: var(--primary-purple); color: var(--text-white);`.
6. Em **cards**, aplique `box-shadow: var(--shadow-md)` e `border-radius: var(--radius-md)`.
7. Use o **rosa** (`--accent-pink`) só em 1 CTA ou número-chave por seção.

### 2. CSS / tema novo (do zero)

Comece copiando **todo** o `references/tokens.css` (já traz o `@import` da
Reddit Sans + Oswald e o `body` base). Depois use as receitas de
`references/component-recipes.md`.

### 3. Slides / e-mail / dashboard

- **Slides:** há duas variantes, e as duas são HTML 1920×1080 por slide
  → PDF, com conferência visual de todas as páginas. **Pergunte qual**
  quando o pedido não deixar claro; não misture as duas no mesmo deck.
  - **Sóbria** ([`references/slides-sober.md`](references/slides-sober.md)):
    fundo branco, navy + roxo + pêssego, cabeçalho e tabela iguais aos do
    relatório em PDF, formas oficiais só na capa/seção/encerramento. Para
    apresentação institucional (ministério, banca, comitê) ou que
    acompanha um relatório de entrega. Validada em 2026-09-18.
  - **Colorida** ([`references/slides.md`](references/slides.md)): **todo
    slide usa um dos 6 templates oficiais** do CDN como fundo (`capa`,
    `capa-capitulo`, `capa-capitulo-alternativa`, `pagina-comum`,
    `pagina-comum-com-enfase`, `encerramento`); o nome diz o papel. Sem
    gradiente, sem fundo inventado. Para evento, divulgação, aula.
- **E-mail:** cores inline (clientes de e-mail ignoram variáveis CSS): use os hexadecimais literais: cabeçalho `#7023E8`, texto `#2D3748`, botão CTA `#F46B2F`.
- **Dashboard:** roxo nos headers/KPIs principais; verde `#10B981` para positivo; fundos `#F7F7F7`/`#F8F9FA`/`#FFE7E1`.

### 4. Relatório longo / e-book / framework numerado (estilo do livro Lab Livre)

Quando o pedido for um **documento longo com seções numeradas** (ex:
"framework de briefing", "guia prático", "tutorial + framework", um e-book
institucional) — não um dashboard nem uma página de produto — siga o estilo
editorial documentado em
[`references/editorial-report.md`](references/editorial-report.md), validado
na prática com o Framework de Briefing:

0. **Pergunte primeiro** se é um **relatório de entrega de produto**
   (vinculado formalmente a um projeto de pesquisa/contrato, com meta e
   produto identificados) ou um **relatório comum**. Só o de entrega leva
   folha de identificação do projeto + índice logo após a capa — e, nesse
   caso, peça ao usuário as informações pra preencher a folha (lista de
   instituições/responsáveis, dados do projeto/entrega, autores) antes de
   escrever a página. Código exato e a lista completa do que perguntar em
   [`references/print-frontmatter.md`](references/print-frontmatter.md).
   - **Pergunte também** se quer marca d'água com os elementos gráficos do
     Lab Livre nas páginas de conteúdo ("Quer marca d'água com os elementos
     gráficos do Lab Livre nas páginas de conteúdo? (padrão: não)"). Só
     aplique com "sim" explícito; código, opacidade e restrições em
     [`references/print-watermark.md`](references/print-watermark.md).
1. Capa **branca** (`print-cover.md`, herdada do Gov Hub, validada lá em
   2026-09-17): logo Lab Livre azul (`lab-livre-blue.svg`) no alto à
   esquerda, título em Oswald uppercase azul profundo, três elementos
   gráficos sangrando pelas bordas (quarto roxo, pílula rosa claro, anel
   azul profundo), parceiros pretos (UnB outlined e, se for projeto Gov
   Hub, a logo do Gov Hub; 34px) no rodapé. Sem moldura, sem gradiente,
   sem kicker.
2. Cabeçalho de capítulo **sóbrio** (`print-header.md`): sobre o branco da
   página, numeral e eyebrow em navy, **título em roxo**, barra de 2px
   `--border-soft` abaixo, alinhado às margens de 20mm. Sem faixa colorida,
   sem chip de ícone. Corpo começa 12mm abaixo da barra; `h3` em navy.
3. Cor de seção (`--section-color`) **sempre navy**, em todos os capítulos
   (`palette.md`). Ela pinta header e legenda de tabela (`print-table.md`)
   e o contorno dos callouts; magenta e rosa não entram em texto nem
   tabela de PDF, e o roxo fica só no título do capítulo, capa e índice.
4. Rodapé em toda página de conteúdo com a borboleta `borboleta-blue.svg`
   (`print-footer.md`); em relatório de entrega, folha de identificação
   com hierarquia por recuo (`print-frontmatter.md`).
5. Callouts usam ícones de produto oficiais (não ícones de linha genéricos)
   em caixa de contorno fino na cor da seção (badge 46px / ícone 32px).
6. Sem travessão (—) no texto corrido — troque por dois-pontos, vírgula ou
   ponto final.

Em PDF o documento inteiro fica em navy + roxo + pêssego. Produto, site e
dashboard continuam só com roxo+rosa (`--primary-purple` + `--accent-pink`).

### 5. Comunicação: Instagram, poster, banner

Peças fora do 16:9 **não esticam** os templates de slide: recomponha com as
formas isoladas (snippets prontos) e as regras de composição da seção
"Comunicação" de
[`references/graphic-elements-catalog.md`](references/graphic-elements-catalog.md):
fundo sólido navy/roxo/pêssego, 2 a 4 formas sangrando pelas bordas, forma
principal com 40 a 50 % do lado menor, texto na zona livre, Oswald na
chamada e Reddit Sans no apoio.

**Post ou carrossel de feed (1080×1350):** não componha do zero. Use uma
das **5 estruturas de quadro validadas** em
[`references/social-posts.md`](references/social-posts.md) (capa,
conteúdo com 3 variantes de bloco, ênfase, convite, fechamento), na ordem
canônica `capa → conteúdo → ênfase → conteúdo → convite → fechamento`.
Texto corrido justificado, sem travessão e sem traço decorativo; cards
no padrão "título forte + descrição discreta + ícone de produto em chip".
Cada estrutura existe também nos 5 fundos da paleta e em 4 composições de
formas, como **100 HTMLs prontos no CDN** (`post-templates/` do
`skills-assets`, seção "Variações" de `social-posts.md`): parta de um
deles em vez de recompor.

## Acessibilidade (obrigatório)

- Texto **branco sobre `#7023E8`**: OK.
- Texto **roxo sobre branco**: para textos pequenos, use `--purple-700` (`#4A17A0`) para garantir contraste AA.
- Rosa (`--accent-pink`) em áreas grandes: prefira texto escuro; se usar texto branco, `font-weight >= 600`.
- Magenta (`--accent-magenta`) e pêssego (`--bg-peach`) são claros/vibrantes demais para texto branco pequeno em cima — use `--dark-navy` nesses casos (ver `palette.md`).

## Logo: as três assinaturas, redução mínima e área de não-interferência (MIV)

| Assinatura | O que é | Redução máxima (tamanho mínimo) |
|---|---|---|
| Horizontal | Borboleta + "Lab Livre" lado a lado | 3 cm de largura |
| Tipográfica | Só o texto "Lab Livre" | 2 cm de largura |
| Ícone | Só a borboleta | 0,5 cm de largura |

Nunca aplique a marca abaixo desses tamanhos. **Área de não-interferência:**
espaço livre ao redor da marca igual à altura do ícone da folha (medida
"x" do manual); nenhum texto, imagem ou borda entra nesse perímetro.

**Cor da aplicação:** 1) dentro da paleta oficial, roxo `#7023E8` de
preferência; 2) se não for viável, branco sobre fundo escuro ou preto/azul
profundo sobre fundo claro. Arquivos disponíveis e pendentes em
`partners.md`.

## Usos indevidos (MIV)

- Não alterar as proporções (esticar, achatar), não rotacionar, inclinar ou
  distorcer.
- Não recolorir fora da paleta, não aplicar contorno em cor diferente da
  versão preenchida, nem duotone fora do padrão.
- Sem sombra projetada, profundidade ou extrusão 3D.
- Não trocar a tipografia do logotipo por serifada, script ou condensada.
- Não separar o ícone do texto na assinatura horizontal de forma
  descoordenada (ícone solto, girado).

## Diretrizes de marca

- **Roxo (`#7023E8`) = assinatura** (domina a identidade). **Laranja (`#F46B2F`) = acento quente** (~10%, só CTA/destaque; **não abusar**). Rosa-choque e azul profundo são acentos secundários; o azul profundo também é a cor-base de texto escuro.
- **Fundos claros** (neutros ou rosa claro `#FFE7E1`) para respiro; `#FFE7E1` nunca como cor de destaque. **Reddit Sans** no corpo/logotipo; **Oswald** só em títulos/chamadas de impacto (uppercase + bold).
- Verde/amarelo apenas como status semântico, nunca como cor de marca.
- Elementos gráficos de apoio: círculo, anel/donut, semicírculo, quarto de círculo e pílula, derivados de "círculos, semicírculos e retângulos arredondados" (ver `component-recipes.md`). Arquivos oficiais e snippets em `graphic-elements-catalog.md`; em documento, só como marca d'água opcional (`print-watermark.md`).

## Referências (progressive disclosure)

- [`references/tokens.css`](references/tokens.css) — tokens completos e comentados, prontos para copiar.
- [`references/partners.md`](references/partners.md) — logos dos parceiros institucionais: catálogo por fundo claro/escuro, quem entra em cada peça e em que ordem, e o ciclo eleitoral (arquivos `-defeso` valem no defeso; sem sufixo, no governo em exercício).
- [`references/palette.md`](references/palette.md) — paleta detalhada, quando usar cada cor, regras de contraste e a rampa editorial (em PDF: tabelas navy, título de capítulo roxo, desde 2026-09-18).
- [`references/component-recipes.md`](references/component-recipes.md) — receitas prontas: botão, card, navbar, tabela zebrada, badge, capa de relatório, gradiente.
- [`references/editorial-report.md`](references/editorial-report.md) — estilo editorial geral (ícones de produto, callouts outline, convenção de escrita sem travessão) para relatórios/e-books longos no estilo do livro Lab Livre. Para capa, cabeçalho de capítulo e rodapé em **PDF**, vá direto aos 4 arquivos abaixo.
- [`references/print-pages.md`](references/print-pages.md) — **comece por aqui para qualquer PDF gerado via Chrome headless**: a arquitetura de página (`.gh-page` fixa 210×297mm, `@page { margin: 0 }`) que evita um bug real de paginação do Chrome (margem negativa + quebra de página forçada pinta uma barra fantasma da cor errada na página anterior). Também traz o procedimento **obrigatório** de conferir visualmente todas as páginas do PDF gerado (rasterizar + inspecionar) atrás de dois erros opostos: overflow silencioso (conteúdo cortado sem aviso) e espaço desperdiçado (quebras de página desnecessárias) — a paginação manual não avisa de nenhum dos dois sozinha.
- [`references/print-cover.md`](references/print-cover.md) — capa de PDF (branca, formas oficiais, parceiros pretos), código exato validado com o usuário em 2026-09-17.
- [`references/print-frontmatter.md`](references/print-frontmatter.md) — folha de identificação do projeto + índice, as duas páginas que vêm logo após a capa **só em relatório de entrega de produto** (pergunte antes — ver seção 4 acima). Inclui a lista exata do que perguntar ao usuário para preencher a folha.
- [`references/print-header.md`](references/print-header.md) — cabeçalho de capítulo em PDF (branco, numeral/eyebrow em navy, título em roxo, barra abaixo), código exato validado com o usuário em 2026-09-18.
- [`references/print-footer.md`](references/print-footer.md) — rodapé de PDF (repete em toda página, barra alinhada à margem do conteúdo, não à borda física), código exato validado, com os erros já cometidos documentados (barra até a borda física em vez da margem, logo grande demais, barra colada no texto).
- [`references/print-table.md`](references/print-table.md) — tabela de dados em PDF: legenda numerada + header sólido navy + linhas com zebra sutil, sem cartão/sombra ao redor. Use sempre que o PDF tiver uma tabela de dados — não invente um componente "cartão de tabela" novo.
- [`references/print-watermark.md`](references/print-watermark.md) — marca d'água **opcional** em páginas de conteúdo de PDF (uma forma isolada no canto, roxo a 7 %). Pergunte antes; padrão sem. Nunca em capa, folha de identificação, índice ou encerramento.
- [`references/slides.md`](references/slides.md) — **variante colorida** de apresentação: arquitetura HTML 1920×1080 → PDF, os 6 templates oficiais como fundo (um por tipo de slide, ordem canônica capa → seção/seção-alt → conteúdo → ênfase → encerramento), zonas seguras de texto de cada template, código exato de cada tipo, exportação e conferência visual.
- [`references/slides-sober.md`](references/slides-sober.md) — **variante sóbria** de apresentação (branca, navy + roxo + pêssego, a linguagem do relatório em PDF no canvas 16:9): código exato validado em 2026-09-18 de capa, seção, conteúdo (tópicos, duas colunas, cards, tabela), ênfase (número-chave, citação) e encerramento, rodapé só com número + símbolo, e as armadilhas do WeasyPrint com SVG inline (`currentColor`/`transform` não funcionam).
- [`references/social-posts.md`](references/social-posts.md) — **comece por aqui para post ou carrossel de Instagram/LinkedIn**: as 5 estruturas de quadro 1080×1350 (capa, conteúdo, ênfase, convite, fechamento) com código exato validado, posições das formas, zonas de texto, limites de linhas, mapeamento ícone↔chip e a lista de erros já cometidos.
- [`references/graphic-elements-catalog.md`](references/graphic-elements-catalog.md) — os 8 elementos gráficos (**servidos por CDN** a partir de `GovHub-br/skills-assets`, **ainda nas cores do Gov Hub**; os snippets SVG inline já saem na cor do token): tabela de quando usar cada um, snippets das formas isoladas, formatos e regras de recomposição para Instagram/poster/banner, e como adicionar um elemento novo.
- [`references/logo/`](references/logo/) — logo oficial Lab Livre, o que já existe em SVG: `lab-livre-{black,blue,white}.svg` (assinatura horizontal) e `borboleta-{black,blue,white}.svg` (ícone). `blue` é o azul institucional `#080056`. Faltam roxo, vertical, tipográfica isolada e peach (ver `partners.md`). Tabela de qual arquivo usar onde em `editorial-report.md` seção 1. Em `references/logo/parceiros/` ficam as logos dos parceiros: UnB (sempre, o Lab Livre fica dentro dela), Gov Hub (`govhub-{navy,white,black}.svg`, quando o documento é de projeto Gov Hub), Ipea e os ministérios MGI, MIR, Cidades e Cultura, usadas no rodapé da capa, no encerramento de slides e no fechamento de carrossel — ordem fixa: UnB → Gov Hub (se houver) → Ipea (se houver) → ministério do projeto (se houver). Qual arquivo usar em cada fundo, quais faltam, e a regra do **período de defeso eleitoral** (sufixo `-defeso`) estão em [`references/partners.md`](references/partners.md).
- [`references/icons-catalog.md`](references/icons-catalog.md) — biblioteca de ícones de produto (332 nomes × variantes `default`/`orange`/`purple`), **servida por CDN** a partir do repo `GovHub-br/skills-assets` e **ainda nas cores do Gov Hub** (roxo `#613EFF`, navy `#0A005A`): perto das cores do Lab Livre, mas não iguais; até existirem os ícones do Lab Livre, use-os sabendo disso. O catálogo traz a URL-base jsDelivr, o padrão `<nome>-<variante>.svg`, a lista dos 332 nomes e o comando para baixar tudo local em ambiente sem internet. Para capas/callouts de relatório use a variante `default`. Escolha o ícone **pelo nome** (são descritivos, ex.: `document-check`, `shield-check`, `chart-bar`) — a biblioteca é grande demais pra um mapeamento fixo; há um subconjunto curado só para os callouts do Framework de Briefing em `editorial-report.md` seção 5. Cada variante traz o fundo embutido na paleta atual (`default` pêssego, `purple` navy, `orange` rosa); **nunca** use um ícone sobre fundo diferente do da sua variante — ver regra completa em `editorial-report.md` seção 5.
