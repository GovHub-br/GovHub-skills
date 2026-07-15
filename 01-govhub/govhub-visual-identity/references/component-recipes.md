# Receitas de componentes GovHub

Todas as receitas assumem que os tokens de `tokens.css` já estão no `:root`.
Copie o componente desejado e ajuste o conteúdo. Nomes de classe em inglês.

## Botão primário (roxo)

```html
<button class="gh-btn gh-btn--primary">Ação principal</button>
```

```css
.gh-btn {
  font-family: var(--font-family-base);
  font-weight: 600;
  border: none;
  border-radius: var(--radius-sm);
  padding: 12px 24px;
  cursor: pointer;
  transition: var(--transition-normal);
}
.gh-btn--primary {
  background: var(--primary-purple);
  color: var(--text-white);
  box-shadow: var(--shadow-md);
}
.gh-btn--primary:hover  { background: var(--purple-600); box-shadow: var(--shadow-lg); }
.gh-btn--primary:active { background: var(--purple-700); }

/* Variante de acento — usar só em CTA pontual */
.gh-btn--accent { background: var(--accent-orange); color: var(--text-white); }
.gh-btn--accent:hover { background: var(--accent-orange-hover); }
```

## Card com sombra

```html
<div class="gh-card">
  <h3 class="gh-card__title">Título do card</h3>
  <p>Conteúdo do card.</p>
</div>
```

```css
.gh-card {
  background: var(--bg-white);
  border-radius: var(--radius-md);
  padding: 24px;
  box-shadow: var(--shadow-md);
  transition: var(--transition-normal);
}
.gh-card:hover { box-shadow: var(--shadow-xl); transform: translateY(-2px); }
.gh-card__title { color: var(--primary-purple); font-weight: 700; margin-top: 0; }
```

## Navbar

```html
<nav class="gh-navbar">
  <span class="gh-navbar__brand">GovHub</span>
  <ul class="gh-navbar__links">
    <li><a href="#">Início</a></li>
    <li><a href="#">Dados</a></li>
    <li><a href="#">Sobre</a></li>
  </ul>
</nav>
```

```css
.gh-navbar {
  display: flex; align-items: center; justify-content: space-between;
  background: var(--primary-purple);
  padding: 14px 24px;
  box-shadow: var(--shadow-md);
}
.gh-navbar__brand { color: var(--text-white); font-weight: 800; font-size: 1.25rem; }
.gh-navbar__links { display: flex; gap: 24px; list-style: none; margin: 0; padding: 0; }
.gh-navbar__links a { color: var(--text-white); text-decoration: none; font-weight: 500; transition: var(--transition-normal); }
.gh-navbar__links a:hover { opacity: 0.8; }
```

## Tabela zebrada com header roxo

```css
.gh-table { width: 100%; border-collapse: collapse; background: var(--bg-white); box-shadow: var(--shadow-md); border-radius: var(--radius-md); overflow: hidden; }
.gh-table thead th {
  background: var(--primary-purple);
  color: var(--text-white);
  font-weight: 600;
  text-align: left;
  padding: 12px 16px;
}
.gh-table tbody td { padding: 12px 16px; color: var(--text-body); border-bottom: 1px solid #eee; }
.gh-table tbody tr:nth-child(even) { background: var(--bg-subtle); }
.gh-table tbody tr:hover { background: rgba(122, 52, 243, 0.06); }
```

## Tag / badge

```html
<span class="gh-badge">Novo</span>
<span class="gh-badge gh-badge--accent">Destaque</span>
<span class="gh-badge gh-badge--success">Concluído</span>
```

```css
.gh-badge {
  display: inline-block;
  background: var(--primary-purple);
  color: var(--text-white);
  font-size: 0.75rem; font-weight: 600;
  padding: 4px 10px; border-radius: 999px;
}
.gh-badge--accent  { background: var(--accent-orange); }
.gh-badge--success { background: var(--color-success); }
```

## Capa de relatório

```html
<header class="gh-report-cover">
  <div class="gh-report-cover__kicker">Relatório GovHub</div>
  <h1 class="gh-report-cover__title">Título do Relatório</h1>
  <p class="gh-report-cover__subtitle">Subtítulo ou período</p>
  <div class="gh-report-cover__meta">Emitido em 01/07/2026</div>
</header>
```

```css
.gh-report-cover {
  background: linear-gradient(135deg, var(--primary-purple) 0%, var(--purple-700) 100%);
  color: var(--text-white);
  padding: 80px 48px;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
}
.gh-report-cover__kicker { text-transform: uppercase; letter-spacing: 2px; font-weight: 600; font-size: 0.85rem; opacity: 0.9; }
.gh-report-cover__title { font-size: 2.75rem; font-weight: 800; margin: 12px 0; line-height: 1.1; }
.gh-report-cover__subtitle { font-size: 1.25rem; opacity: 0.95; margin: 0; }
.gh-report-cover__meta { margin-top: 32px; font-size: 0.9rem; opacity: 0.8; }
/* Acento pontual opcional: uma faixa laranja fina */
.gh-report-cover::after { content: ""; display: block; width: 64px; height: 4px; background: var(--accent-orange); margin-top: 24px; border-radius: 999px; }
```

## Gradiente da marca (uso em heros / capas)

```css
.gh-gradient { background: linear-gradient(135deg, var(--primary-purple), var(--secondary-purple)); }
```
