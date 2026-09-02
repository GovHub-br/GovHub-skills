---
name: govhub-visual-identity
description: >-
  Especialista em aplicar a identidade visual oficial do Gov Hub (gov-hub.io e
  o livro "Gov Hub: um guia prático") em qualquer artefato — relatórios
  HTML/PDF, e-books, frameworks numerados, páginas web, componentes, slides,
  dashboards, e-mails, temas CSS. Use SEMPRE que o usuário pedir para aplicar,
  usar ou trazer a identidade visual, cores, paleta, tema, estilo, marca ou
  "cara" do Gov Hub. Dispara com: "roxo do govhub", "tema govhub", "identidade
  visual govhub", "estilo govhub", "cores do govhub", "paleta govhub", "deixar
  com a cara do govhub", "aplicar a marca govhub", "deixar no padrão govhub",
  "estilizar como o govhub", "usar o roxo #7A34F3", "relatório/framework no
  estilo do livro do Gov Hub", "e-book com capítulos Gov Hub". Cobre
  estilização de relatório, site, PDF, e-book, framework numerado, slide,
  componente, e-mail e dashboard.
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
  de círculo e pílula (retângulo 100% arredondado) — nunca ilustrações
  figurativas.

> **Nota de versão:** esta é a paleta/tipografia atualizadas do MIV mais
> recente, que **substituem totalmente** o roxo/laranja e a fonte Inter de
> versões anteriores desta skill. Os arquivos de logo em `references/logo/`
> ainda são os antigos — a nova versão da logo (assinaturas horizontal/
> vertical, tipográfica e ícone) será atualizada quando o arquivo chegar.

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
validada pra isso.

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

- **Slides:** capa com o gradiente da marca + Reddit Sans no corpo, Oswald uppercase nos títulos de impacto; roxo nos títulos; rosa num único destaque por slide.
- **E-mail:** cores inline (clientes de e-mail ignoram variáveis CSS) — use os hexadecimais literais: cabeçalho `#613EFF`, texto `#2D3748`, botão CTA `#F9006F`.
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
1. Capa com fundo **sólido** na cor exata da logo (`--logo-purple`,
   *pendente* — placeholder `#613EFF` até a nova exportação chegar),
   logo oficial (`references/logo/`, também pendente de atualização) +
   moldura arredondada fina, sem onda decorativa, sem pílula, sem
   subtítulo — versão limpa.
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
- Elementos gráficos de apoio: círculo, anel/donut, semicírculo, quarto de círculo e pílula — derivados de "círculos, semicírculos e retângulos arredondados" (ver `component-recipes.md`).

## Referências (progressive disclosure)

- [`references/tokens.css`](references/tokens.css) — tokens completos e comentados, prontos para copiar.
- [`references/palette.md`](references/palette.md) — paleta detalhada, quando usar cada cor, regras de contraste e a rampa editorial multicor.
- [`references/component-recipes.md`](references/component-recipes.md) — receitas prontas: botão, card, navbar, tabela zebrada, badge, capa de relatório, gradiente.
- [`references/editorial-report.md`](references/editorial-report.md) — estilo editorial geral (ícones de produto, callouts outline, convenção de escrita sem travessão) para relatórios/e-books longos no estilo do livro Gov Hub. Para capa, cabeçalho de capítulo e rodapé em **PDF**, vá direto aos 4 arquivos abaixo.
- [`references/print-pages.md`](references/print-pages.md) — **comece por aqui para qualquer PDF gerado via Chrome headless**: a arquitetura de página (`.gh-page` fixa 210×297mm, `@page { margin: 0 }`) que evita um bug real de paginação do Chrome (margem negativa + quebra de página forçada pinta uma barra fantasma da cor errada na página anterior). Também traz o procedimento **obrigatório** de conferir visualmente todas as páginas do PDF gerado (rasterizar + inspecionar) atrás de dois erros opostos: overflow silencioso (conteúdo cortado sem aviso) e espaço desperdiçado (quebras de página desnecessárias) — a paginação manual não avisa de nenhum dos dois sozinha.
- [`references/print-cover.md`](references/print-cover.md) — capa de PDF, código exato validado com o usuário.
- [`references/print-frontmatter.md`](references/print-frontmatter.md) — folha de identificação do projeto + índice, as duas páginas que vêm logo após a capa **só em relatório de entrega de produto** (pergunte antes — ver seção 4 acima). Inclui a lista exata do que perguntar ao usuário para preencher a folha.
- [`references/print-header.md`](references/print-header.md) — cabeçalho de capítulo em PDF (faixa full-bleed, numeral/eyebrow/título, chip de ícone opcional), código exato validado com o usuário.
- [`references/print-footer.md`](references/print-footer.md) — rodapé de PDF (repete em toda página, barra alinhada à margem do conteúdo, não à borda física), código exato validado, com os erros já cometidos documentados (barra até a borda física em vez da margem, logo grande demais, barra colada no texto).
- [`references/print-table.md`](references/print-table.md) — tabela de dados em PDF: legenda numerada + header sólido na cor da seção atual + linhas com zebra sutil, sem cartão/sombra ao redor. Use sempre que o PDF tiver uma tabela de dados — não invente um componente "cartão de tabela" novo.
- [`references/logo/`](references/logo/) — logo oficial Gov Hub em 3 orientações (horizontal, vertical, símbolo isolado) × 4 cores (primary, light, dark, colourfull), SVG, pronta para usar. Em `references/logo/parceiros/` ficam as logos institucionais dos parceiros (Lab Livre, UnB), já em versão branca/transparente, usadas no rodapé da capa (ver `print-cover.md`) — ordem fixa: Lab Livre primeiro, UnB depois.
- [`references/icons-catalog.md`](references/icons-catalog.md) — biblioteca completa de ícones de produto Gov Hub (332 nomes × variantes `default`/`orange`/`purple`), **servida por CDN** a partir do repo `GovHub-br/skills-assets` — não são arquivos locais. O catálogo traz a URL-base jsDelivr, o padrão `<nome>-<variante>.svg`, a lista dos 332 nomes e o comando para baixar tudo local em ambiente sem internet. Para capas/callouts de relatório use a variante `default`. Escolha o ícone **pelo nome** (são descritivos, ex.: `document-check`, `shield-check`, `chart-bar`) — a biblioteca é grande demais pra um mapeamento fixo; há um subconjunto curado só para os callouts do Framework de Briefing em `editorial-report.md` seção 5. **Nunca** use os ícones sobre fundo diferente de branco/roxo Gov Hub/laranja Gov Hub — ver regra completa e a borda do badge em `editorial-report.md` seção 5.
