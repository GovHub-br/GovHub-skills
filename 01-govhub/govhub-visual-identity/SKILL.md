---
name: govhub-visual-identity
description: >-
  Especialista em aplicar a identidade visual oficial do GovHub (gov-hub.io) em
  qualquer artefato — relatórios HTML/PDF, páginas web, componentes, slides,
  dashboards, e-mails, temas CSS. Use SEMPRE que o usuário pedir para aplicar,
  usar ou trazer a identidade visual, cores, paleta, tema, estilo, marca ou
  "cara" do GovHub. Dispara com: "roxo do govhub", "tema govhub", "identidade
  visual govhub", "estilo govhub", "cores do govhub", "paleta govhub", "deixar
  com a cara do govhub", "aplicar a marca govhub", "deixar no padrão govhub",
  "estilizar como o govhub", "usar o roxo #7A34F3". Cobre estilização de
  relatório, site, PDF, slide, componente, e-mail e dashboard.
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
- [`references/palette.md`](references/palette.md) — paleta detalhada, quando usar cada cor e regras de contraste.
- [`references/component-recipes.md`](references/component-recipes.md) — receitas prontas: botão, card, navbar, tabela zebrada, badge, capa de relatório, gradiente.
