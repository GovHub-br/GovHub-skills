# Receitas de componentes Gov Hub

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
.gh-btn--accent { background: var(--accent-pink); color: var(--text-white); font-weight: 600; }
.gh-btn--accent:hover { background: #D40060; }
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
  <span class="gh-navbar__brand">Gov Hub</span>
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
.gh-table tbody tr:hover { background: rgba(97, 62, 255, 0.06); }
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
.gh-badge--accent  { background: var(--accent-pink); }
.gh-badge--success { background: var(--color-success); }
```

## Capa de relatório

```html
<header class="gh-report-cover">
  <div class="gh-report-cover__kicker">Relatório Gov Hub</div>
  <h1 class="gh-report-cover__title">Título do Relatório</h1>
  <p class="gh-report-cover__subtitle">Subtítulo ou período</p>
  <div class="gh-report-cover__meta">Emitido em 01/07/2026</div>
</header>
```

```css
.gh-report-cover {
  background: linear-gradient(135deg, var(--primary-purple) 0%, var(--dark-navy) 100%);
  color: var(--text-white);
  padding: 80px 48px;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
}
.gh-report-cover__kicker { text-transform: uppercase; letter-spacing: 2px; font-weight: 600; font-size: 0.85rem; opacity: 0.9; }
.gh-report-cover__title { font-size: 2.75rem; font-weight: 800; margin: 12px 0; line-height: 1.1; }
.gh-report-cover__subtitle { font-size: 1.25rem; opacity: 0.95; margin: 0; }
.gh-report-cover__meta { margin-top: 32px; font-size: 0.9rem; opacity: 0.8; }
/* Acento pontual opcional: uma faixa rosa fina */
.gh-report-cover::after { content: ""; display: block; width: 64px; height: 4px; background: var(--accent-pink); margin-top: 24px; border-radius: 999px; }
```

## Padronagem e elementos gráficos (MIV)

O manual define três formas geométricas simples como recursos de apoio da
marca — **círculos, semicírculos e retângulos arredondados** — usados como
fundo, divisor, moldura ou detalhe decorativo. Nunca ilustrações
figurativas, ícones de linha genéricos ou formas livres: só essas três,
soltas ou repetidas em padronagem, sempre na paleta oficial (`--primary-purple`,
`--dark-navy`, `--accent-magenta`, `--accent-pink`, `--bg-peach`, ou brancos/
pretos translúcidos sobre fundo colorido).

Com base nas páginas do MIV enviadas pelo usuário (a legenda do manual diz
"círculos, semicírculos e retângulos arredondados", mas as duas páginas de
exemplo mostram um repertório um pouco mais amplo, derivado dessas três
formas base): **círculo cheio, anel/círculo vazado (donut), semicírculo,
quarto de círculo, e retângulo arredondado no formato pílula** (cantos 100%
arredondados, não só levemente). Nas duas referências, essas formas
aparecem como **blocos sólidos e saturados** competindo entre si na
composição — não só como textura sutil de fundo — então os dois modos de
uso abaixo são válidos, escolha pelo contexto.

### Modo 1 — Composição (capa, post, hero): formas sólidas e grandes

Formas grandes, cor sólida (sem opacidade reduzida), uma cor diferente por
forma, se sobrepondo/saindo da borda do frame — é assim que a página de
exemplo do MIV usa os elementos (círculo roxo ocupando um canto inteiro,
círculo navy grande no centro, anel magenta, pílula rosa). Fundo geralmente
`--bg-peach`.

**Círculo:**
```css
.gh-shape-circle {
  border-radius: 50%;
  background: var(--dark-navy); /* ou qualquer cor da paleta oficial */
}
```

**Anel / círculo vazado (donut) — via `border`, funciona sobre qualquer fundo:**
```css
.gh-shape-ring {
  width: 210px; height: 210px;
  border-radius: 50%;
  border: 52px solid var(--accent-magenta); /* espessura do anel */
  background: transparent;
}
```

**Semicírculo (metade de um círculo, lado reto para baixo):**
```css
.gh-shape-semicircle {
  width: 300px; height: 150px; /* largura = 2x altura, sempre */
  border-radius: 300px 300px 0 0;
  background: var(--accent-pink);
}
/* Virado para outro lado: gire com transform: rotate(90deg/180deg/270deg) */
```

**Quarto de círculo (quarter-pie — o "canto arredondado" que aparece muitas
vezes na padronagem, ex. imagem 2 do MIV): técnica de círculo cortado por
`overflow: hidden` no contêiner pai, com o círculo posicionado num dos
cantos do contêiner. Testado nas 4 orientações — copie a que precisar:**
```css
.gh-shape-quarter {
  width: 120px; height: 120px; /* contêiner = tamanho do quarto de círculo */
  overflow: hidden;
  position: relative;
}
.gh-shape-quarter::before {
  content: "";
  position: absolute;
  width: 240px; height: 240px; /* círculo = 2x o contêiner */
  border-radius: 50%;
  background: var(--primary-purple); /* qualquer cor da paleta */
  top: 0; left: 0;
}
/* Arco no canto inferior-esquerdo (arredondado embaixo/esquerda) */
.gh-shape-quarter--bl { transform: scaleY(-1); }
/* Arco no canto superior-direito (arredondado em cima/direita) */
.gh-shape-quarter--tr { transform: scaleX(-1); }
/* Arco no canto inferior-direito (arredondado embaixo/direita) */
.gh-shape-quarter--br { transform: rotate(180deg); }
```

**Retângulo arredondado / pílula (cantos 100% arredondados, não `--radius-lg`):**
```css
.gh-shape-pill {
  height: 90px; /* altura define o raio */
  border-radius: 999px;
  background: var(--accent-pink);
}
```

### Modo 2 — Textura de fundo: formas pequenas, translúcidas, repetidas

Para fundos que precisam de conteúdo/texto legível em cima (cards, capas
com título), reduza opacidade e/ou desature: `rgba(255,255,255,0.08)` sobre
fundo colorido, ou a cor sólida em opacidade 10–18% sobre fundo claro. Uma
cor por elemento, sem misturar as 5 cores no mesmo fundo.

```css
.gh-deco-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
}
.gh-deco-circle--corner { width: 480px; height: 480px; top: -180px; right: -180px; }
```

**Padronagem em grade (dots), para fundo de card/seção:**
```css
.gh-pattern-dots {
  background-image: radial-gradient(rgba(97, 62, 255, 0.12) 2px, transparent 2px);
  background-size: 28px 28px;
}
```

### Padronagem tipo "wallpaper" (mosaico de formas, ex. imagem 2 do MIV)

Para um fundo decorativo cobrindo toda a área (capa cheia, header grande),
espalhe várias instâncias das formas acima (círculo, anel, semicírculo,
quarto de círculo, pílula) em tamanhos variados, cor sólida alternando
entre as 4 cores de acento sobre fundo `--bg-peach`, encostando ou se
sobrepondo levemente — sem grade rígida, mas também sem espaço vazio
sobrando entre as formas (o efeito é de mosaico denso, não de elementos
soltos). Construa isso como SVG ou um grid CSS com posições levemente
deslocadas manualmente; não existe uma fórmula única, o efeito é de colagem.

Regra geral: elementos gráficos são **recursos de apoio**, seja no modo 1
(protagonismo visual controlado, típico de capa/post) ou modo 2 (textura
discreta atrás de conteúdo) — nunca competem com o título, a logo, ou o
texto principal quando estes estão presentes na mesma peça.

## Gradiente da marca (uso em heros / capas)

```css
.gh-gradient { background: linear-gradient(135deg, var(--primary-purple), var(--dark-navy)); }
/* Variante mais vibrante, para capas de destaque/editorial */
.gh-gradient--vivid { background: linear-gradient(135deg, var(--primary-purple), var(--accent-magenta)); }
```
