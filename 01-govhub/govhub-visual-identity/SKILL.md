---
name: govhub-visual-identity
description: >-
  Use quando o usuário pedir para aplicar a identidade visual, cores, paleta,
  tema, estilo, marca ou "cara" do Gov Hub em qualquer artefato: relatório
  HTML/PDF, e-book ou framework numerado no estilo do livro Gov Hub, slides,
  post ou carrossel de Instagram/LinkedIn, poster, banner, página web,
  componente, dashboard, e-mail, tema CSS. Dispara com: "identidade visual
  govhub", "tema govhub", "cores/paleta do govhub", "roxo do govhub", "deixar
  com a cara do govhub", "padrão govhub", "slides govhub", "post instagram
  govhub", "elementos gráficos govhub", "marca d'água govhub", "logo govhub".
---

# Gov Hub — Identidade Visual

Aplique a identidade visual **oficial** do Gov Hub, definida no Manual de
Identidade Visual (MIV) da marca, em qualquer artefato. A marca é definida
por:

- **Roxo `#613EFF` como cor primária/assinatura** (destaque principal).
- **Rosa `#F9006F` como acento pontual** (só CTA/destaque — não abusar).
- **Azul-marinho `#0A005A`** para contraste máximo (títulos grandes, fundos escuros).
- **Magenta `#EF41FF`** como acento secundário (gradientes, rampa editorial).
- **Fundos claros** (neutros ou pêssego `#FFE7E1`) e as fontes **Reddit Sans**
  (principal — Open Sans no Canva gratuito) + **Oswald** (apoio, só títulos/
  chamadas de impacto, uppercase + bold).
- **Elementos gráficos de apoio:** círculo, anel/donut, semicírculo, quarto
  de círculo e pílula (retângulo 100% arredondado), nunca ilustrações
  figurativas. Os arquivos oficiais (6 templates de slide + folha de formas
  + padrão) são servidos por CDN e catalogados em
  [`references/graphic-elements-catalog.md`](references/graphic-elements-catalog.md).

> **Nota de versão:** esta é a paleta/tipografia atualizadas do MIV mais
> recente, que **substituem totalmente** o roxo/laranja e a fonte Inter de
> versões anteriores desta skill. Os arquivos de logo em `references/logo/`
> já são a nova exportação (2026-09-16): `logomarca-horizontal-*`,
> `logomarca-vertical-*`, `assinatura-*` (tipográfica) e `icone-none-*`,
> cada um em `default`/`navy`/`peach`/`white`/`black`. Os ícones de produto
> do CDN também já estão na paleta atual.

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
  --primary-purple: #613EFF; /* ROXO — cor-assinatura */
  --dark-navy:      #0A005A; /* contraste máximo, títulos grandes, fundos escuros */
  --accent-magenta: #EF41FF; /* acento secundário */
  --accent-pink:    #F9006F; /* acento pontual (CTA) */
  --bg-peach:       #FFE7E1; /* fundo claro "de marca" */
  --text-white:     #FFFFFF;

  /* Estados derivados do primário */
  --purple-600: #5235D9; /* hover/foco */
  --purple-700: #3F28A6; /* active/pressionado */

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
  --shadow-md: 0 2px 10px rgba(10,0,90,0.10);
  --shadow-lg: 0 4px 20px rgba(10,0,90,0.12);
  --shadow-xl: 0 8px 30px rgba(10,0,90,0.16);

  /* Transição padrão */
  --transition-normal: all 0.3s ease;

  --radius-sm: 6px; --radius-md: 10px; --radius-lg: 16px;
}
```

### Cor primária e como derivar estados

`--primary-purple` (`#613EFF`) é **sempre** a cor primária. Para estados:

- **Hover/foco:** `--purple-600` (`#5235D9`).
- **Active/pressionado:** `--purple-700` (`#3F28A6`).
- **Gradiente da marca:** `linear-gradient(135deg, #613EFF, #0A005A)`.

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

- **Slides:** siga [`references/slides.md`](references/slides.md) ao pé da
  letra. **Todo slide usa um dos 6 templates oficiais** do CDN como fundo
  (`capa`, `capa-capitulo`, `capa-capitulo-alternativa`, `pagina-comum`,
  `pagina-comum-com-enfase`, `encerramento`); o nome diz o papel. Sem
  gradiente, sem fundo inventado. HTML 1920×1080 por slide → PDF, com
  conferência visual de todas as páginas.
- **E-mail:** cores inline (clientes de e-mail ignoram variáveis CSS): use os hexadecimais literais: cabeçalho `#613EFF`, texto `#2D3748`, botão CTA `#F9006F`.
- **Dashboard:** roxo nos headers/KPIs principais; verde `#10B981` para positivo; fundos `#F7F7F7`/`#F8F9FA`/`#FFE7E1`.

### 4. Relatório longo / e-book / framework numerado (estilo do livro Gov Hub)

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
     Gov Hub nas páginas de conteúdo ("Quer marca d'água com os elementos
     gráficos do Gov Hub nas páginas de conteúdo? (padrão: não)"). Só
     aplique com "sim" explícito; código, opacidade e restrições em
     [`references/print-watermark.md`](references/print-watermark.md).
1. Capa com fundo **sólido** na cor exata da logo (`--logo-purple`,
   `#613EFF`, confirmado na nova exportação), logo oficial
   (`references/logo/logomarca-horizontal-white.svg`) + moldura arredondada
   fina, sem onda decorativa, sem pílula, sem subtítulo — versão limpa.
2. Cada seção ganha uma cor sólida da **rampa editorial** (navy → roxo →
   magenta → rosa → pêssego, ver `palette.md`) numa **faixa full-bleed que
   começa no topo da página e vai de ponta a ponta**, não uma faixa
   inserida com margem.
3. Numeral grande do padrão "numeral + eyebrow + título" fica em branco a
   ~75% de opacidade sobre a faixa colorida (não a técnica antiga de
   "cor-sobre-cor com opacidade baixa", que só funciona em fundo branco).
4. Ícone grande por seção usa os **ícones de produto oficiais**
   (ver `icons-catalog.md` e `editorial-report.md` seção 5) dentro de um
   chip branco, para ter contraste garantido contra qualquer cor da rampa.
5. Callouts usam os mesmos ícones de produto (não ícones de linha genéricos)
   em caixa de contorno fino — tamanho generoso (badge 46px / ícone 32px).
6. Sem travessão (—) no texto corrido — troque por dois-pontos, vírgula ou
   ponto final.

Essa rampa multicor é exclusiva para este tipo de documento. Produto, site e
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

## Acessibilidade (obrigatório)

- Texto **branco sobre `#613EFF`**: OK.
- Texto **roxo sobre branco**: para textos pequenos, use `--purple-700` (`#3F28A6`) para garantir contraste AA.
- Rosa (`--accent-pink`) em áreas grandes: prefira texto escuro; se usar texto branco, `font-weight >= 600`.
- Magenta (`--accent-magenta`) e pêssego (`--bg-peach`) são claros/vibrantes demais para texto branco pequeno em cima — use `--dark-navy` nesses casos (ver `palette.md`).

## Redução mínima e área de não-interferência (MIV)

- **Redução máxima:** o manual define três limites de tamanho mínimo para a
  marca continuar legível — **2,5 cm**, **1,5 cm** e **0,5 cm** — cada um
  correspondente a uma assinatura diferente (horizontal, vertical/
  tipográfica, ícone isolado). A correspondência exata assinatura↔limite
  será confirmada quando os novos arquivos de logo chegarem; até lá, não
  reduza a logo abaixo de 2,5 cm de largura em aplicações horizontais por
  segurança.
- **Área de não-interferência:** o espaço mínimo ao redor da marca é
  definido como **"x"**, a altura da letra do ícone da marca. Nenhum outro
  elemento (texto, imagem, borda) pode invadir esse perímetro.

## Aplicação da marca e usos indevidos (MIV)

- Sempre que possível, use a marca dentro da paleta oficial. Se não for
  viável: **branco** sobre fundo escuro, **preto** sobre fundo claro.
- **Nunca:** distorcer/esticar a proporção da logo, girar fora do eixo,
  adicionar contorno/stroke não previsto, aplicar sombra/efeito 3D/glow, ou
  recolorir fora da paleta oficial (gradiente não documentado, cor sólida
  fora das 5 listadas). Ver exemplos em `palette.md`.

## Diretrizes de marca

- **Roxo (`#613EFF`) = assinatura** (domina a identidade). **Rosa (`#F9006F`) = acento** (~10%, só CTA/destaque; **não abusar**). Magenta e navy são acentos secundários.
- **Fundos claros** (neutros ou pêssego `#FFE7E1`) para respiro. **Reddit Sans** no corpo/logotipo; **Oswald** só em títulos/chamadas de impacto (uppercase + bold).
- Verde/amarelo apenas como status semântico, nunca como cor de marca.
- Elementos gráficos de apoio: círculo, anel/donut, semicírculo, quarto de círculo e pílula, derivados de "círculos, semicírculos e retângulos arredondados" (ver `component-recipes.md`). Arquivos oficiais e snippets em `graphic-elements-catalog.md`; em documento, só como marca d'água opcional (`print-watermark.md`).

## Referências (progressive disclosure)

- [`references/tokens.css`](references/tokens.css) — tokens completos e comentados, prontos para copiar.
- [`references/partners.md`](references/partners.md) — logos dos parceiros institucionais: catálogo por fundo claro/escuro, quem entra em cada peça e em que ordem, e o ciclo eleitoral (arquivos `-defeso` valem no defeso; sem sufixo, no governo em exercício).
- [`references/palette.md`](references/palette.md) — paleta detalhada, quando usar cada cor, regras de contraste e a rampa editorial multicor.
- [`references/component-recipes.md`](references/component-recipes.md) — receitas prontas: botão, card, navbar, tabela zebrada, badge, capa de relatório, gradiente.
- [`references/editorial-report.md`](references/editorial-report.md) — estilo editorial geral (ícones de produto, callouts outline, convenção de escrita sem travessão) para relatórios/e-books longos no estilo do livro Gov Hub. Para capa, cabeçalho de capítulo e rodapé em **PDF**, vá direto aos 4 arquivos abaixo.
- [`references/print-pages.md`](references/print-pages.md) — **comece por aqui para qualquer PDF gerado via Chrome headless**: a arquitetura de página (`.gh-page` fixa 210×297mm, `@page { margin: 0 }`) que evita um bug real de paginação do Chrome (margem negativa + quebra de página forçada pinta uma barra fantasma da cor errada na página anterior). Também traz o procedimento **obrigatório** de conferir visualmente todas as páginas do PDF gerado (rasterizar + inspecionar) atrás de dois erros opostos: overflow silencioso (conteúdo cortado sem aviso) e espaço desperdiçado (quebras de página desnecessárias) — a paginação manual não avisa de nenhum dos dois sozinha.
- [`references/print-cover.md`](references/print-cover.md) — capa de PDF, código exato validado com o usuário.
- [`references/print-frontmatter.md`](references/print-frontmatter.md) — folha de identificação do projeto + índice, as duas páginas que vêm logo após a capa **só em relatório de entrega de produto** (pergunte antes — ver seção 4 acima). Inclui a lista exata do que perguntar ao usuário para preencher a folha.
- [`references/print-header.md`](references/print-header.md) — cabeçalho de capítulo em PDF (faixa full-bleed, numeral/eyebrow/título, chip de ícone opcional), código exato validado com o usuário.
- [`references/print-footer.md`](references/print-footer.md) — rodapé de PDF (repete em toda página, barra alinhada à margem do conteúdo, não à borda física), código exato validado, com os erros já cometidos documentados (barra até a borda física em vez da margem, logo grande demais, barra colada no texto).
- [`references/print-table.md`](references/print-table.md) — tabela de dados em PDF: legenda numerada + header sólido na cor da seção atual + linhas com zebra sutil, sem cartão/sombra ao redor. Use sempre que o PDF tiver uma tabela de dados — não invente um componente "cartão de tabela" novo.
- [`references/print-watermark.md`](references/print-watermark.md) — marca d'água **opcional** em páginas de conteúdo de PDF (uma forma isolada no canto, roxo a 7 %). Pergunte antes; padrão sem. Nunca em capa, folha de identificação, índice ou encerramento.
- [`references/slides.md`](references/slides.md) — **comece por aqui para qualquer apresentação**: arquitetura HTML 1920×1080 → PDF, os 6 templates oficiais como fundo (um por tipo de slide, ordem canônica capa → seção/seção-alt → conteúdo → ênfase → encerramento), zonas seguras de texto de cada template, código exato de cada tipo, exportação e conferência visual.
- [`references/social-posts.md`](references/social-posts.md) — **comece por aqui para post ou carrossel de Instagram/LinkedIn**: as 5 estruturas de quadro 1080×1350 (capa, conteúdo, ênfase, convite, fechamento) com código exato validado, posições das formas, zonas de texto, limites de linhas, mapeamento ícone↔chip e a lista de erros já cometidos.
- [`references/graphic-elements-catalog.md`](references/graphic-elements-catalog.md) — os 8 elementos gráficos oficiais (**servidos por CDN** a partir de `GovHub-br/skills-assets`, não são arquivos locais): tabela de quando usar cada um, snippets SVG das formas isoladas, formatos e regras de recomposição para Instagram/poster/banner, e como adicionar um elemento novo.
- [`references/logo/`](references/logo/) — logo oficial Gov Hub (nova exportação do MIV): `logomarca-horizontal-*`, `logomarca-vertical-*`, `assinatura-horizontal-*`/`assinatura-vertical-*` (só o nome) e `icone-none-*` (só o ícone), cada uma em `default`/`navy`/`peach`/`white`/`black`, SVG. Tabela de qual arquivo usar onde em `editorial-report.md` seção 1. Em `references/logo/parceiros/` ficam as logos institucionais dos parceiros (Lab Livre e UnB, que andam sempre juntas e nessa ordem porque o Lab Livre é o dono dos projetos e fica dentro da UnB; Ipea; e os ministérios MGI, MIR, Cidades e Cultura), usadas no rodapé da capa, no encerramento de slides e no fechamento de carrossel — ordem fixa: Lab Livre → UnB → Ipea (se houver) → ministério do projeto (se houver). Qual arquivo usar em cada fundo (`positivo`/`negativo`), quais faltam, e a regra do **período de defeso eleitoral** (sufixo `-defeso`) estão em [`references/partners.md`](references/partners.md).
- [`references/icons-catalog.md`](references/icons-catalog.md) — biblioteca completa de ícones de produto Gov Hub (332 nomes × variantes `default`/`orange`/`purple`, regeradas na paleta atual em 2026-09-16), **servida por CDN** a partir do repo `GovHub-br/skills-assets` — não são arquivos locais. O catálogo traz a URL-base jsDelivr, o padrão `<nome>-<variante>.svg`, a lista dos 332 nomes e o comando para baixar tudo local em ambiente sem internet. Para capas/callouts de relatório use a variante `default`. Escolha o ícone **pelo nome** (são descritivos, ex.: `document-check`, `shield-check`, `chart-bar`) — a biblioteca é grande demais pra um mapeamento fixo; há um subconjunto curado só para os callouts do Framework de Briefing em `editorial-report.md` seção 5. Cada variante traz o fundo embutido na paleta atual (`default` pêssego, `purple` navy, `orange` rosa); **nunca** use um ícone sobre fundo diferente do da sua variante — ver regra completa em `editorial-report.md` seção 5.
