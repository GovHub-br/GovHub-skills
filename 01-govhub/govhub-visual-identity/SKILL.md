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
  govhub", "elementos gráficos govhub", "marca d'água govhub", "logo govhub",
  "gerar o PDF desse markdown", "documento/dicionário de dados em PDF",
  "relatório A4 com a capa do govhub", "build_doc".
---

# Gov Hub — Identidade Visual

Aplique a identidade visual do Gov Hub em qualquer artefato. O padrão é o
**modo sóbrio** (2026-09-30), fechado pela equipe de design e comunicação
a partir do MIV:

- **Roxo `#613EFF` como cor primária/assinatura.**
- **Navy `#0A005A`** para títulos, fundos escuros e contraste máximo.
- **Claro `#F2F1F6`** para blocos, cards, pílulas, faixas, zebra e fundo
  claro (substitui o pêssego `#FFE7E1`).
- **Acento `#BE006E`** só em detalhe: pílula, tag, pontinho, numeral, aspas,
  seta, CTA (substitui o rosa `#F9006F`). Magenta `#EF41FF` não é usado.
- **Reddit Sans em tudo** (Open Sans no Canva gratuito). Chamada em peso
  800, ou 400 misturado a 800, em caixa alta e baixa. **Sem Oswald.**
- **Elementos gráficos de apoio:** círculo, anel, semicírculo, quarto de
  círculo e pílula, sempre sólidos e em cor da paleta, nunca ilustração
  figurativa. Catálogo em
  [`references/graphic-elements-catalog.md`](references/graphic-elements-catalog.md).

> A paleta colorida anterior (pêssego, rosa `#F9006F`, magenta, Oswald nas
> chamadas) foi **descontinuada** em 2026-09-30, junto com os posts
> coloridos, os templates de slide coloridos do CDN e os ícones nessas
> cores. Não há modo colorido. Logos em `references/logo/` (exportação de
> 2026-09-16): `logomarca-*`, `assinatura-*`, `icone-none-*` em
> `default`/`navy`/`white`/`black`.

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
@import url('https://fonts.googleapis.com/css2?family=Reddit+Sans:wght@300;400;500;600;700;800;900&display=swap');

:root {
  /* Paleta sóbria (padrão) */
  --primary-purple: #613EFF; /* ROXO — cor-assinatura */
  --dark-navy:      #0A005A; /* títulos, fundos escuros, contraste máximo */
  --bg-soft:        #F2F1F6; /* claro da marca: blocos, cards, pílulas, zebra */
  --accent-rose:    #BE006E; /* acento pontual: detalhe e CTA */
  --text-white:     #FFFFFF;
  --bg-peach:   var(--bg-soft);     /* apelido: era #FFE7E1 */
  --accent-pink: var(--accent-rose); /* apelido: era #F9006F */

  /* Estados derivados do primário */
  --purple-600: #5235D9; /* hover/foco */
  --purple-700: #3F28A6; /* active; roxo de texto pequeno sobre branco */

  /* Neutros / texto */
  --text-strong: #202020;
  --text-body:   #2D3748;
  --text-muted:  #666666;

  /* Fundos (sem cinza além de #F2F1F6) */
  --bg-white:  #FFFFFF;
  --bg-light:  var(--bg-soft);
  --bg-subtle: var(--bg-soft);
  --border-soft: #E9DFFF;

  /* Semânticas */
  --color-success:   #10B981;
  --color-highlight: #FFD700;

  /* Tipografia: Reddit Sans em tudo */
  --font-family-base:    'Reddit Sans', 'Open Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-family-heading: var(--font-family-base); /* compatibilidade: era Oswald */
  --heading-weight: 800; --heading-tracking: -0.025em; --heading-leading: 1.06;

  /* Sombras */
  --shadow-md: 0 2px 10px rgba(10,0,90,0.10);
  --shadow-lg: 0 4px 20px rgba(10,0,90,0.12);
  --shadow-xl: 0 8px 30px rgba(10,0,90,0.16);

  /* Transição padrão */
  --transition-normal: all 0.3s ease;

  --radius-sm: 6px; --radius-md: 10px; --radius-lg: 16px;
}
```

Os nomes `--bg-peach` e `--accent-pink` continuam existindo para não
quebrar receitas antigas, mas agora valem `#F2F1F6` e `#BE006E`.

### Cor primária e como derivar estados

`--primary-purple` (`#613EFF`) é **sempre** a cor primária. Para estados:

- **Hover/foco:** `--purple-600` (`#5235D9`).
- **Active/pressionado:** `--purple-700` (`#3F28A6`).
- **Sem gradiente** no modo sóbrio: formas e fundos são sólidos.

## Como aplicar por alvo

**PDF sóbrio de corpo corrido, a partir de um markdown longo** (relatório
técnico, dicionário de dados, nota): use
[`scripts/build_doc.py`](scripts/README.md) em vez de escrever o CSS na mão.
Ele implementa a receita validada de capa, faixa de capítulo, rodapé e tabela,
e pagina com WeasyPrint, o que dispensa o loop de paginação por medição de
`print-pages.md`.

```bash
python3 scripts/build_doc.py --markdown doc.md --cover-title "Relatório" --project-short MIR
# documento de verdade: copie scripts/exemplo-config.json e passe --config
```

**O script não substitui a skill.** Ele cobre o texto que flui: capítulos,
tabelas, figuras, blocos de destaque. Fica de fora, e continua nas
referências: ícones de produto em callout e card (`editorial-report.md` §5-6),
folha de identificação e índice (`print-frontmatter.md`), marca d'água
(`print-watermark.md`), qualquer composição em grid (cards, callouts lado a
lado, página de visão geral de framework) e todo layout que o markdown não
expressa. Documento no estilo livro ou framework numerado pede essas peças:
leia as referências e monte à mão, ou gere o corpo com o script e acrescente
as páginas especiais depois.

O script também não vale para peça que não é documento A4 (slide, post,
poster, dashboard) nem para arquitetura de página diferente.

**Qualquer outro PDF.** Isso vale pra qualquer gênero de
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
3. Troque a cor de **títulos** (`h1..h3`) para `var(--primary-purple)` ou `var(--dark-navy)`; para chamadas de grande impacto, use a classe `.gh-heading-display` (Reddit Sans 800, caixa alta e baixa, `letter-spacing: -0.025em`).
4. Em **tabelas**, pinte o `thead th` com `background: var(--primary-purple); color: var(--text-white);` e alterne linhas com `var(--bg-subtle)`.
5. Em **badges/tags**, use `background: var(--primary-purple); color: var(--text-white);`.
6. Em **cards**, aplique `box-shadow: var(--shadow-md)` e `border-radius: var(--radius-md)`.
7. Use o acento `#BE006E` (`--accent-rose`) só em 1 CTA ou detalhe por seção, nunca em área grande.

### 2. CSS / tema novo (do zero)

Comece copiando **todo** o `references/tokens.css` (já traz o `@import` da
Reddit Sans e o `body` base). Depois use as receitas de
`references/component-recipes.md`.

### 3. Slides / e-mail / dashboard

- **Slides** ([`references/slides-sober.md`](references/slides-sober.md)):
  HTML 1920×1080 por slide → PDF, com conferência visual de todas as
  páginas. Fundo branco, navy + roxo + `#F2F1F6`, Reddit Sans, cabeçalho
  e tabela iguais aos do relatório em PDF, formas oficiais só na
  capa/seção/encerramento.
- **E-mail:** cores inline (clientes de e-mail ignoram variáveis CSS): use os hexadecimais literais: cabeçalho `#613EFF`, texto `#2D3748`, botão CTA `#BE006E`, blocos `#F2F1F6`.
- **Dashboard:** roxo e navy nos headers/KPIs principais; verde `#10B981` para positivo; fundos branco e `#F2F1F6`; `#BE006E` só em destaque pontual.

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
1. Capa **branca** (`print-cover.md`, validada em 2026-09-17): logo navy
   no alto à esquerda, título em Reddit Sans 800 navy (caixa alta e
   baixa), três elementos gráficos oficiais sangrando pelas bordas (quarto
   roxo, pílula `#F2F1F6`, anel navy), parceiros pretos (Lab Livre + UnB outlined, 34px) no rodapé.
   Sem moldura, sem gradiente, sem kicker.
2. Cabeçalho de capítulo **sóbrio** (`print-header.md`): sobre o branco da
   página, numeral e eyebrow em navy, **título em roxo**, barra de 2px
   `--border-soft` abaixo, alinhado às margens de 20mm. Sem faixa colorida,
   sem chip de ícone. Corpo começa 12mm abaixo da barra; `h3` em navy.
3. Cor de seção (`--section-color`) **sempre navy**, em todos os capítulos
   (`palette.md`). Ela pinta header e legenda de tabela (`print-table.md`)
   e o contorno dos callouts; `#BE006E` não entra em texto nem tabela de
   PDF, e o roxo fica só no título do capítulo, capa e índice.
4. Rodapé em toda página de conteúdo com símbolo `icone-none-navy.svg`
   (`print-footer.md`); em relatório de entrega, folha de identificação
   com hierarquia por recuo (`print-frontmatter.md`).
5. Callouts usam ícones de produto oficiais (não ícones de linha genéricos)
   em caixa de contorno fino na cor da seção (badge 46px / ícone 32px).
6. Sem travessão (—) no texto corrido — troque por dois-pontos, vírgula ou
   ponto final.

Em PDF o documento inteiro fica em navy + roxo + `#F2F1F6`. Produto, site
e dashboard usam roxo como assinatura e `#BE006E` só como acento pontual.

### 5. Comunicação: Instagram, poster, banner

**Post ou carrossel de feed (1080×1350):** não componha do zero. Parta
dos **58 templates prontos no CDN** (`post-templates-sobrio/` do
`skills-assets`), catalogados por tipo e fundo em
[`references/social-posts.md`](references/social-posts.md):

- Um carrossel usa **um fundo só**: navy, roxo ou claro. A capa pode
  inverter.
- Ordem: **capa → conteúdo × N → dados ou ênfase → convite**. Não há
  template de fechamento: quando for preciso, a equipe de design cria a
  partir dos modelos; não componha um.
- Baixe o HTML de cada quadro, troque só textos, números e ícone, mantenha
  formas e posições, e diga ao usuário quais arquivos usou.
- Reddit Sans com peso 400 misturado a 800, um objeto por quadro (mockup
  de UI, círculo ou bloco), sem fotos, sem travessão, sem traço
  decorativo.

**Poster, banner e outras peças** que não são post de feed: componha com
as formas isoladas e as regras da seção "Comunicação" de
[`references/graphic-elements-catalog.md`](references/graphic-elements-catalog.md),
com fundo sólido navy, roxo ou claro, formas sólidas da paleta, chamada em
Reddit Sans 800 e as regras de cor por fundo de `palette.md`.

## Acessibilidade (obrigatório)

- Texto **branco** sobre roxo, navy ou `#BE006E`: OK.
- Texto **navy** sobre branco ou `#F2F1F6`: OK. **Nunca** texto branco sobre fundo claro.
- **Nunca texto roxo sobre navy** (cerca de 2,6:1).
- `#BE006E` sobre claro (cerca de 5:1) serve para texto de detalhe e CTA; sobre navy (cerca de 3:1) só em forma, nunca em texto; sobre roxo, não use.
- Texto **roxo sobre branco** em tamanho pequeno: use `--purple-700` (`#3F28A6`).

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
  recolorir fora da paleta (gradiente, cor sólida fora de roxo, navy,
  `#F2F1F6`, `#BE006E`, branco e preto). Ver exemplos em `palette.md`.

## Diretrizes de marca

- **Roxo (`#613EFF`) = assinatura** e **navy (`#0A005A`)** dominam. **`#BE006E` = acento** de detalhe e CTA, bem menos de 10 % da peça, nunca em área grande nem sobre roxo.
- **`#F2F1F6`** é o claro da marca (blocos, cards, zebra, fundo claro). Sem pêssego, sem magenta, sem cinza além dele.
- **Reddit Sans em tudo**; chamada em 800 (ou 400 misturado a 800), caixa alta e baixa. Sem Oswald.
- Verde/amarelo apenas como status semântico, nunca como cor de marca.
- Elementos gráficos de apoio: círculo, anel/donut, semicírculo, quarto de círculo e pílula, derivados de "círculos, semicírculos e retângulos arredondados" (ver `component-recipes.md`). Arquivos oficiais e snippets em `graphic-elements-catalog.md`; em documento, só como marca d'água opcional (`print-watermark.md`).

## Referências (progressive disclosure)

- [`scripts/build_doc.py`](scripts/README.md) — **comece por aqui para um markdown longo que vira PDF**: script pronto (Python + WeasyPrint) que monta capa, faixa de capítulo, rodapé e tabelas numeradas a partir de um `.md` com um capítulo por `## N. Título`, configurado por um JSON pequeno. Também trata imagem solta como `<figure>`, `**Limitações:**` como bloco de destaque, e evita título órfão no fim da página. Validado no Dicionário de Dados do MIR (129 páginas, 91 tabelas, 7 figuras).
- [`references/tokens.css`](references/tokens.css) — tokens completos e comentados, prontos para copiar, com os apelidos de compatibilidade (`--bg-peach` → `#F2F1F6`, `--accent-pink` → `#BE006E`).
- [`references/partners.md`](references/partners.md) — logos dos parceiros institucionais: catálogo por fundo claro/escuro, quem entra em cada peça e em que ordem, e o ciclo eleitoral (arquivos `-defeso` valem no defeso; sem sufixo, no governo em exercício).
- [`references/palette.md`](references/palette.md) — paleta sóbria detalhada: quando usar cada cor, **o que vai sobre cada um dos três fundos** (navy, roxo, claro), contraste, rampa editorial de PDF (tabelas navy, título de capítulo roxo).
- [`references/component-recipes.md`](references/component-recipes.md) — receitas prontas: botão, card, navbar, tabela zebrada, badge, capa de relatório, gradiente.
- [`references/editorial-report.md`](references/editorial-report.md) — estilo editorial geral (ícones de produto, callouts outline, convenção de escrita sem travessão) para relatórios/e-books longos no estilo do livro Gov Hub. Para capa, cabeçalho de capítulo e rodapé em **PDF**, vá direto aos 4 arquivos abaixo.
- [`references/print-pages.md`](references/print-pages.md) — **comece por aqui para qualquer PDF gerado via Chrome headless**: a arquitetura de página (`.gh-page` fixa 210×297mm, `@page { margin: 0 }`) que evita um bug real de paginação do Chrome (margem negativa + quebra de página forçada pinta uma barra fantasma da cor errada na página anterior). Também traz o procedimento **obrigatório** de conferir visualmente todas as páginas do PDF gerado (rasterizar + inspecionar) atrás de dois erros opostos: overflow silencioso (conteúdo cortado sem aviso) e espaço desperdiçado (quebras de página desnecessárias) — a paginação manual não avisa de nenhum dos dois sozinha.
- [`references/print-cover.md`](references/print-cover.md) — capa de PDF (branca, formas oficiais, parceiros pretos), código exato validado com o usuário em 2026-09-17.
- [`references/print-frontmatter.md`](references/print-frontmatter.md) — folha de identificação do projeto + índice, as duas páginas que vêm logo após a capa **só em relatório de entrega de produto** (pergunte antes — ver seção 4 acima). Inclui a lista exata do que perguntar ao usuário para preencher a folha.
- [`references/print-header.md`](references/print-header.md) — cabeçalho de capítulo em PDF (branco, numeral/eyebrow em navy, título em roxo, barra abaixo), código exato validado com o usuário em 2026-09-18.
- [`references/print-footer.md`](references/print-footer.md) — rodapé de PDF (repete em toda página, barra alinhada à margem do conteúdo, não à borda física), código exato validado, com os erros já cometidos documentados (barra até a borda física em vez da margem, logo grande demais, barra colada no texto).
- [`references/print-table.md`](references/print-table.md) — tabela de dados em PDF: legenda numerada + header sólido navy + linhas com zebra sutil, sem cartão/sombra ao redor. Use sempre que o PDF tiver uma tabela de dados — não invente um componente "cartão de tabela" novo.
- [`references/print-watermark.md`](references/print-watermark.md) — marca d'água **opcional** em páginas de conteúdo de PDF (uma forma isolada no canto, roxo a 7 %). Pergunte antes; padrão sem. Nunca em capa, folha de identificação, índice ou encerramento.
- [`references/slides-sober.md`](references/slides-sober.md) — apresentação (branca, navy + roxo + `#F2F1F6`, Reddit Sans, a linguagem do relatório em PDF no canvas 16:9): código exato de capa, seção, conteúdo (tópicos, duas colunas, cards, tabela), ênfase (número-chave, citação) e encerramento, rodapé só com número + símbolo, e as armadilhas do WeasyPrint com SVG inline (`currentColor`/`transform` não funcionam).
- [`references/social-posts.md`](references/social-posts.md) — **comece por aqui para post ou carrossel de Instagram/LinkedIn**: os 58 templates prontos no CDN catalogados por tipo × fundo (navy, roxo, claro), a regra de um fundo por carrossel, cor por fundo, tipografia, texto, exportação e como derivar variação nova.
- [`references/graphic-elements-catalog.md`](references/graphic-elements-catalog.md) — as formas de apoio da marca (círculo, anel, semicírculo, quarto de círculo, pílula e derivadas) como snippets SVG inline, regras de composição para stories, poster e banner, e formatos canônicos. Não há templates de fundo prontos.
- [`references/logo/`](references/logo/) — logo oficial Gov Hub (nova exportação do MIV): `logomarca-horizontal-*`, `logomarca-vertical-*`, `assinatura-horizontal-*`/`assinatura-vertical-*` (só o nome) e `icone-none-*` (só o ícone), cada uma em `default`/`navy`/`white`/`black`, SVG (navy ou default sobre claro, white sobre navy/roxo). Tabela de qual arquivo usar onde em `editorial-report.md` seção 1. Em `references/logo/parceiros/` ficam as logos institucionais dos parceiros (Lab Livre e UnB, que andam sempre juntas e nessa ordem porque o Lab Livre é o dono dos projetos e fica dentro da UnB; Ipea; e os ministérios MGI, MIR, Cidades e Cultura), usadas no rodapé da capa, no encerramento de slides e no fechamento de carrossel — ordem fixa: Lab Livre → UnB → Ipea (se houver) → ministério do projeto (se houver). Qual arquivo usar em cada fundo (`positivo`/`negativo`), quais faltam, e a regra do **período de defeso eleitoral** (sufixo `-defeso`) estão em [`references/partners.md`](references/partners.md).
- [`references/icons-catalog.md`](references/icons-catalog.md) — biblioteca de ícones de produto Gov Hub (332 nomes, variante única `-sober`: preenchimento `#F2F1F6`, contorno navy, sombra `#BE006E`), **servida por CDN** a partir do repo `GovHub-br/skills-assets`. Traz a URL-base jsDelivr, o padrão `<nome>-sober.svg`, a lista dos 332 nomes e o comando para baixar tudo local em ambiente sem internet. Escolha o ícone **pelo nome** (ex.: `document-check`, `shield-check`, `chart-bar`); há um subconjunto curado para os callouts do Framework de Briefing em `editorial-report.md` seção 5.
