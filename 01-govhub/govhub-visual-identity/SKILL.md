---
name: govhub-visual-identity
description: >-
  Especialista em aplicar a identidade visual oficial do GovHub (gov-hub.io e
  o livro "Gov Hub: um guia prático") em qualquer artefato — relatórios
  HTML/PDF, e-books, frameworks numerados, páginas web, componentes, slides,
  dashboards, e-mails, temas CSS. Use SEMPRE que o usuário pedir para aplicar,
  usar ou trazer a identidade visual, cores, paleta, tema, estilo, marca ou
  "cara" do GovHub. Dispara com: "roxo do govhub", "tema govhub", "identidade
  visual govhub", "estilo govhub", "cores do govhub", "paleta govhub", "deixar
  com a cara do govhub", "aplicar a marca govhub", "deixar no padrão govhub",
  "estilizar como o govhub", "usar o roxo #7A34F3", "relatório/framework no
  estilo do livro do GovHub", "e-book com capítulos GovHub". Cobre
  estilização de relatório, site, PDF, e-book, framework numerado, slide,
  componente, e-mail e dashboard.
---

# GovHub — Identidade Visual

Aplique a identidade visual **oficial** do GovHub (extraída do CSS de
<https://gov-hub.io>) em qualquer artefato. A marca é definida por:

- **Roxo `#7A34F3` como cor primária/assinatura** (destaque principal).
- **Laranja `#F97316` como acento pontual** (só CTA/destaque — não abusar).
- **Fundos claros neutros** e a fonte **Inter**.

## Design Tokens (fonte da verdade)

Injete este bloco no `:root` do artefato (dentro de `<style>` no `<head>`, ou no
topo do CSS). O arquivo completo e comentado está em
[`references/tokens.css`](references/tokens.css) — copie de lá quando quiser tudo.

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
  /* Cores primárias da marca */
  --primary-purple:   #7A34F3; /* ROXO PRINCIPAL — cor-assinatura */
  --secondary-purple: #8B5CF6;
  --accent-orange:    #F97316; /* acento pontual (CTA) */
  --accent-orange-hover: #EA580C;
  --text-white:       #FFFFFF;

  /* Roxos de apoio / estados */
  --purple-400: #9249CA;
  --purple-600: #7C3AAD; /* hover/foco do primário */
  --purple-700: #5B21B6; /* active/pressionado (mais escuro) */

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
  --color-warm:      #F19F42;

  /* Tipografia */
  --font-family-base: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;

  /* Sombras */
  --shadow-md: 0 2px 10px rgba(0,0,0,0.1);
  --shadow-lg: 0 4px 20px rgba(0,0,0,0.1);
  --shadow-xl: 0 8px 30px rgba(0,0,0,0.15);

  /* Transição padrão */
  --transition-normal: all 0.3s ease;

  --radius-sm: 6px; --radius-md: 10px; --radius-lg: 16px;
}
```

### Cor primária e como derivar estados

`--primary-purple` (`#7A34F3`) é **sempre** a cor primária. Para estados:

- **Hover/foco:** `--purple-600` (`#7C3AAD`).
- **Active/pressionado:** `--purple-700` (`#5B21B6`).
- **Gradiente da marca:** `linear-gradient(135deg, #7A34F3, #8B5CF6)`.

## Como aplicar por alvo

### 1. HTML / relatório já existente

1. Adicione o bloco `:root` (acima) dentro de um `<style>` no `<head>`.
2. Aplique a fonte: `body { font-family: var(--font-family-base); color: var(--text-body); background: var(--bg-light); }`.
3. Troque a cor de **títulos** (`h1..h3`) para `var(--primary-purple)`.
4. Em **tabelas**, pinte o `thead th` com `background: var(--primary-purple); color: var(--text-white);` e alterne linhas com `var(--bg-subtle)`.
5. Em **badges/tags**, use `background: var(--primary-purple); color: var(--text-white);`.
6. Em **cards**, aplique `box-shadow: var(--shadow-md)` e `border-radius: var(--radius-md)`.
7. Use o **laranja** só em 1 CTA ou número-chave por seção.

### 2. CSS / tema novo (do zero)

Comece copiando **todo** o `references/tokens.css` (já traz o `@import` da Inter e
o `body` base). Depois use as receitas de `references/component-recipes.md`.

### 3. Slides / e-mail / dashboard

- **Slides:** capa com o gradiente da marca + Inter; roxo nos títulos; laranja num único destaque por slide.
- **E-mail:** cores inline (clientes de e-mail ignoram variáveis CSS) — use os hexadecimais literais: cabeçalho `#7A34F3`, texto `#2D3748`, botão CTA `#F97316`.
- **Dashboard:** roxo nos headers/KPIs principais; verde `#10B981` para positivo; fundos `#F7F7F7`/`#F8F9FA`.

### 4. Relatório longo / e-book / framework numerado (estilo do livro GovHub)

Quando o pedido for um **documento longo com seções numeradas** (ex:
"framework de briefing", "guia prático", "tutorial + framework", um e-book
institucional) — não um dashboard nem uma página de produto — siga o estilo
editorial documentado em
[`references/editorial-report.md`](references/editorial-report.md), validado
na prática com o Framework de Briefing:

1. Capa com fundo **sólido** na cor exata da logo (`--logo-purple`,
   `#7521F9`), logo oficial (`references/logo/`) + moldura arredondada fina,
   sem onda decorativa, sem pílula, sem subtítulo — versão limpa.
2. Cada seção ganha uma cor sólida da **rampa editorial** (roxo → magenta →
   rosa → coral, ver `palette.md`) numa **faixa full-bleed que começa no
   topo da página e vai de ponta a ponta**, não uma faixa inserida com
   margem.
3. Numeral grande do padrão "numeral + eyebrow + título" fica em branco a
   ~75% de opacidade sobre a faixa colorida (não a técnica antiga de
   "cor-sobre-cor com opacidade baixa", que só funciona em fundo branco).
4. Ícone grande por seção usa os **ícones de produto oficiais**
   (`references/icons/`, ver `editorial-report.md` seção 5) dentro de um
   chip branco, para ter contraste garantido contra qualquer cor da rampa.
5. Callouts usam os mesmos ícones de produto (não ícones de linha genéricos)
   em caixa de contorno fino — tamanho generoso (badge 46px / ícone 32px).
6. Sem travessão (—) no texto corrido — troque por dois-pontos, vírgula ou
   ponto final.

Essa rampa multicor é exclusiva para este tipo de documento. Produto, site e
dashboard continuam só com roxo+laranja (`--primary-purple` + `--accent-orange`).

## Acessibilidade (obrigatório)

- Texto **branco sobre `#7A34F3`**: OK.
- Texto **roxo sobre branco**: para textos pequenos, use `--purple-700` (`#5B21B6`) para garantir contraste AA.
- Laranja em áreas grandes: prefira texto escuro; se usar texto branco, `font-weight >= 600`.

## Diretrizes de marca

- **Roxo = assinatura** (domina a identidade). **Laranja = acento** (~10%, só CTA/destaque; **não abusar**).
- **Fundos claros neutros** para respiro. **Inter** em tudo.
- Verde/amarelo apenas como status semântico, nunca como cor de marca.

## Referências (progressive disclosure)

- [`references/tokens.css`](references/tokens.css) — tokens completos e comentados, prontos para copiar.
- [`references/palette.md`](references/palette.md) — paleta detalhada, quando usar cada cor, regras de contraste e a rampa editorial multicor.
- [`references/component-recipes.md`](references/component-recipes.md) — receitas prontas: botão, card, navbar, tabela zebrada, badge, capa de relatório, gradiente.
- [`references/editorial-report.md`](references/editorial-report.md) — estilo editorial geral (ícones de produto, callouts outline, convenção de escrita sem travessão) para relatórios/e-books longos no estilo do livro GovHub. Para capa, cabeçalho de capítulo e rodapé em **PDF**, vá direto aos 4 arquivos abaixo.
- [`references/print-pages.md`](references/print-pages.md) — **comece por aqui para qualquer PDF gerado via Chrome headless**: a arquitetura de página (`.gh-page` fixa 210×297mm, `@page { margin: 0 }`) que evita um bug real de paginação do Chrome (margem negativa + quebra de página forçada pinta uma barra fantasma da cor errada na página anterior).
- [`references/print-cover.md`](references/print-cover.md) — capa de PDF, código exato validado com o usuário.
- [`references/print-header.md`](references/print-header.md) — cabeçalho de capítulo em PDF (faixa full-bleed, numeral/eyebrow/título, chip de ícone opcional), código exato validado com o usuário.
- [`references/print-footer.md`](references/print-footer.md) — rodapé de PDF (repete em toda página, barra alinhada à margem do conteúdo, não à borda física), código exato validado, com os erros já cometidos documentados (barra até a borda física em vez da margem, logo grande demais, barra colada no texto).
- [`references/logo/`](references/logo/) — logo oficial GovHub em 3 orientações (horizontal, vertical, símbolo isolado) × 4 cores (primary, light, dark, colourfull), SVG, pronta para usar.
- [`references/icons/`](references/icons/) — biblioteca completa de ícones de produto GovHub, 32 nomes × variante `Default` (duotone roxo+laranja, para fundo branco), `orange` e `purple` (fundo sólido colorido), todos em SVG. Para capas/callouts de relatório use a variante `Default` e o subconjunto curado em `editorial-report.md` seção 5 (workflow, document_check, pessoal, forum, database, pie_chart, settings, governance, paper, notification, tools) — os demais nomes (acesso, charts, chat_round, chat_square, code, contratos, courses, deploy, download, eye_dropper, figma, folder, github, ia, link, open-folder, orcamento, paint_brush, server, teds) ficam disponíveis para outros usos.
