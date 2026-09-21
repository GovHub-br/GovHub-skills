# govhub-diagramas — Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar a skill `01-govhub/govhub-diagramas` que gera diagramas de arquitetura, mapa de schemas, fluxo de processo (raias) e pipeline de dados em HTML/CSS com a IDV do Gov Hub, renderizados em PNG por Chromium headless, com lineage extraído do `manifest.json` do dbt.

**Architecture:** Templates HTML usam um vocabulário CSS fixo (`references/diagram.css`) e declaram setas em JSON que `references/diagram.js` desenha como SVG overlay posicionado a partir do layout real (sem coordenadas à mão). `scripts/render.mjs` abre o HTML com Playwright, espera fontes, dispara o desenho das setas e captura `.diagram`. `scripts/dbt_lineage.py` transforma o manifest em nós/arestas para o Claude preencher o template.

**Tech Stack:** HTML/CSS, JavaScript (browser), Node.js 18+ (ESM) + Playwright, Python 3 stdlib. Spec: `docs/superpowers/specs/2026-09-21-govhub-diagramas-design.md`.

## Global Constraints

- Paleta: só os hex de `references/colors.md`: `#613EFF`, `#0A005A`, `#5235D9`, `#3F28A6`, `#EF41FF`, `#F9006F`, `#FFE7E1`, `#202020`, `#2D3748`, `#666666`, `#FFFFFF`, `#F7F7F7`, `#F8F9FA`, `#E9DFFF`, `#9CA3AF`. **Proibidos:** `#7A34F3`, `#F97316`, `#5B21B6`, `#8B5CF6`, qualquer fonte Inter.
- Fonte: Reddit Sans via Google Fonts `@import`. Nada de Oswald dentro do diagrama.
- Largura da raiz `.diagram`: 1500 px; altura livre. PNG padrão em `deviceScaleFactor` 2 → 3000 px de largura.
- Templates no repositório referenciam `../references/diagram.css` e `../references/diagram.js` por `<link>`/`<script src>` (DRY). Ao copiar um template para uso, `scripts/inline_assets.mjs` embute os dois (HTML único, portável) — é isso que o spec chama de "CSS inline".
- Textos em português; comentários de código em português, curtos.
- Commits com a linha `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>` no fim.
- `node_modules/` de `scripts/` **não** entra no git.

---

## Mapa de arquivos

| Arquivo | Responsabilidade |
|---|---|
| `01-govhub/govhub-diagramas/SKILL.md` | Gatilhos, famílias, fluxo de trabalho em 6 passos, checklist. |
| `references/colors.md` | Papel no diagrama → token/hex. |
| `references/diagram.css` | Tokens + vocabulário de classes. |
| `references/diagram.js` | Desenha setas do JSON `#arrows` em SVG. |
| `references/grammar-processo.md` | Gramática de raias (portada). |
| `references/grammar-dados.md` | Gramática política→dado e pipeline (portada). |
| `references/grammar-arquitetura.md` | Gramática de blocos/zonas e mapa de schemas (nova). |
| `templates/arquitetura-blocos.html` | Recriação da Fig. 3 do relatório MinC. |
| `templates/mapa-schemas.html` | Recriação da Fig. 8. |
| `templates/fluxo-raias.html` | Exemplo ilustrativo de processo com 3 atores. |
| `templates/pipeline-dados.html` | Exemplo fonte → ingestão → camadas → consumo. |
| `scripts/render.mjs` | HTML → PNG. |
| `scripts/inline_assets.mjs` | Copia template embutindo CSS/JS. |
| `scripts/dbt_lineage.py` + `scripts/test_dbt_lineage.py` + `scripts/fixtures/manifest.min.json` | Lineage do dbt. |
| `scripts/package.json`, `scripts/setup.sh`, `scripts/.gitignore` | Instalação do renderizador. |
| `.claude-plugin/marketplace.json`, `README.md` | Registro da skill. |

---

### Task 1: Motor de render (CSS base, JS de setas, render.mjs, inline_assets.mjs, setup)

**Files:**
- Create: `01-govhub/govhub-diagramas/references/diagram.css`
- Create: `01-govhub/govhub-diagramas/references/diagram.js`
- Create: `01-govhub/govhub-diagramas/scripts/render.mjs`
- Create: `01-govhub/govhub-diagramas/scripts/inline_assets.mjs`
- Create: `01-govhub/govhub-diagramas/scripts/package.json`
- Create: `01-govhub/govhub-diagramas/scripts/setup.sh`
- Create: `01-govhub/govhub-diagramas/scripts/.gitignore`
- Test: HTML de fumaça em `/tmp/claude-1000/*/scratchpad/smoke.html` (não commitado)

**Interfaces:**
- Produces: classes CSS `.diagram .title .subtitle .canvas .zone .zone--dashed .zone--plain .pill .pill--navy .pill--pink .pill--magenta .node .node--out .node--legacy .node--muted .node--pink .node--fill .tag .note .note--lgpd .note--plain .lanes .lane .lane-head .lane-body .dot .dot--end .decision .legend .legend-title .item .sample .sample--data .sample--meta .sample--flow .sample--gov .swatch .swatch--dashed .swatch--out .composition .step .num .sep .layer .layer--1 .layer--2 .layer--3`.
- Produces: contrato de setas — `<script type="application/json" id="arrows">[{"from":"idA","to":"idB","type":"exec|data|meta|flow|gov","label":"...","fromSide":"top|right|bottom|left","toSide":"...","via":<número>,"labelAt":"start|mid|end","dx":0,"dy":0}]</script>` dentro de `.canvas`; `window.drawArrows()` redesenha.
- Produces: `node scripts/render.mjs <in.html> [out.png] [--width 1500] [--scale 2] [--selector ".diagram"]` → exit 0 e PNG; exit 2 sem renderizador.
- Produces: `node scripts/inline_assets.mjs <template.html> <saida.html>`.

- [ ] **Step 1: Criar `references/diagram.css`**

```css
/* govhub-diagramas — CSS base dos diagramas.
   Tokens ESPELHADOS de 01-govhub/govhub-visual-identity/references/tokens.css
   (2026-09-21). Se a IDV mudar, atualize aqui também. */
@import url('https://fonts.googleapis.com/css2?family=Reddit+Sans:wght@400;500;600;700;800&display=swap');

:root {
  --primary-purple: #613EFF;
  --dark-navy: #0A005A;
  --purple-600: #5235D9;
  --purple-700: #3F28A6;
  --accent-magenta: #EF41FF;
  --accent-pink: #F9006F;
  --bg-peach: #FFE7E1;
  --text-strong: #202020;
  --text-body: #2D3748;
  --text-muted: #666666;
  --bg-white: #FFFFFF;
  --bg-light: #F7F7F7;
  --bg-subtle: #F8F9FA;
  --border-soft: #E9DFFF;
  --gray-out: #9CA3AF;                       /* fora do escopo — não é cor de marca */
  --purple-tint-1: rgba(97, 62, 255, .06);   /* fundo de zona */
  --purple-tint-2: rgba(97, 62, 255, .12);   /* nó de saída / camada bruta */
  --purple-tint-3: rgba(97, 62, 255, .30);   /* camada intermediária */
  --font: 'Reddit Sans', 'Open Sans', -apple-system, 'Segoe UI', Roboto, sans-serif;
  --radius-sm: 6px; --radius-md: 10px; --radius-lg: 16px;
}

* { box-sizing: border-box; }
html, body { margin: 0; background: #fff; }
body { font-family: var(--font); color: var(--text-body); -webkit-font-smoothing: antialiased; }

/* raiz: largura fixa, altura livre */
.diagram { position: relative; width: 1500px; background: #fff; padding: 28px 24px 24px; font-size: 14px; line-height: 1.35; }
.title { margin: 0; text-align: center; font-size: 30px; font-weight: 800; color: var(--dark-navy); }
.subtitle { margin: 6px 0 0; text-align: center; font-size: 15px; color: var(--text-muted); }
.canvas { position: relative; margin-top: 28px; }

/* zonas (agrupamentos) */
.zone { position: relative; border: 2px solid var(--primary-purple); border-radius: var(--radius-lg); background: var(--bg-subtle); padding: 44px 22px 22px; }
.zone--dashed { border-style: dashed; }
.zone--plain { background: #fff; }

/* pílula: rótulo sobre a borda, contorno branco cobre a linha */
.pill { position: absolute; top: -16px; left: 20px; padding: 6px 16px; border-radius: 999px; background: var(--primary-purple); color: #fff; font-size: 12px; font-weight: 600; letter-spacing: .04em; text-transform: uppercase; box-shadow: 0 0 0 4px #fff; white-space: nowrap; }
.pill--navy { background: var(--dark-navy); }
.pill--pink { background: var(--accent-pink); }
.pill--magenta { background: var(--accent-magenta); }

/* nós */
.node { position: relative; border: 2px solid var(--primary-purple); border-radius: var(--radius-md); background: #fff; padding: 14px 16px; }
.node h3 { margin: 0; font-size: 16px; font-weight: 700; color: var(--text-strong); }
.node p { margin: 4px 0 0; font-size: 12.5px; color: var(--text-muted); }
.node--out { background: var(--purple-tint-2); }
.node--legacy { border-style: dashed; }
.node--muted { border-color: var(--gray-out); }
.node--muted h3, .node--muted p { color: var(--gray-out); }
.node--pink { border-color: var(--accent-pink); }
.node--fill { background: var(--primary-purple); border-color: var(--primary-purple); }
.node--fill h3, .node--fill p { color: #fff; }
.node .pill { top: -14px; left: 14px; font-size: 11px; padding: 5px 12px; }

/* etiqueta de instrumento/sistema */
.tag { display: inline-block; margin-top: 8px; padding: 3px 10px; border-radius: 999px; background: var(--border-soft); color: var(--purple-700); font-size: 11px; font-weight: 600; }

/* notas e callouts */
.note { border: 1.5px dashed var(--accent-pink); background: var(--bg-peach); border-radius: var(--radius-sm); padding: 8px 12px; font-size: 12px; color: var(--text-body); }
.note strong { color: var(--accent-pink); font-weight: 700; }
.note--lgpd { border-style: solid; }
.note--lgpd::before { content: "LGPD · "; font-weight: 800; color: var(--accent-pink); }
.note--plain { border-color: var(--border-soft); background: var(--bg-subtle); }
.note--plain strong { color: var(--purple-700); }

/* raias (swimlanes): grid de 2 colunas — cabeçalho | corpo */
.lanes { display: grid; grid-template-columns: 150px 1fr; border: 2px solid var(--border-soft); border-radius: var(--radius-lg); overflow: hidden; }
.lane { display: contents; }
.lane-head { padding: 18px 14px; font-weight: 700; color: #fff; background: var(--primary-purple); display: flex; align-items: center; }
.lane:nth-of-type(2) .lane-head { background: var(--purple-700); }
.lane:nth-of-type(3) .lane-head { background: var(--accent-magenta); }
.lane:nth-of-type(4) .lane-head { background: var(--dark-navy); }
.lane-body { position: relative; display: grid; grid-template-columns: repeat(7, 170px); gap: 20px; align-items: center; padding: 26px 20px; border-bottom: 1px solid var(--border-soft); min-height: 130px; }
.lane:last-of-type .lane-body { border-bottom: 0; }
.lane:nth-of-type(even) .lane-body { background: var(--bg-subtle); }
.lane-body .node { padding: 10px 12px; }
.lane-body .node h3 { font-size: 13.5px; }
.lane-body .node p { font-size: 11px; }

/* início / fim / decisão */
.dot { width: 26px; height: 26px; border-radius: 50%; background: var(--primary-purple); justify-self: center; position: relative; }
.dot--end { box-shadow: 0 0 0 3px #fff, 0 0 0 5px var(--primary-purple); }
.dot span { position: absolute; top: 32px; left: 50%; transform: translateX(-50%); font-size: 11px; white-space: nowrap; color: var(--text-muted); }
.decision { width: 160px; height: 100px; display: flex; align-items: center; justify-content: center; text-align: center; font-size: 12px; font-weight: 600; color: var(--dark-navy); background: var(--bg-peach); clip-path: polygon(50% 0, 100% 50%, 50% 100%, 0 50%); padding: 0 24px; justify-self: center; }

/* legenda */
.legend { margin-top: 22px; border: 1.5px solid var(--border-soft); border-radius: var(--radius-md); background: #fff; padding: 14px 22px; display: flex; align-items: center; gap: 32px; font-size: 12px; }
.legend-title { font-weight: 800; color: var(--primary-purple); letter-spacing: .04em; }
.legend .item { display: flex; align-items: center; gap: 10px; }
.legend .item b { display: block; font-size: 12.5px; color: var(--text-strong); }
.legend .item span { color: var(--text-muted); }
.legend .sample { width: 52px; height: 0; border-top: 2px solid var(--dark-navy); position: relative; }
.legend .sample::after { content: ""; position: absolute; right: -2px; top: -5px; border: 4px solid transparent; border-left: 7px solid var(--dark-navy); }
.legend .sample--data { border-top-style: dashed; }
.legend .sample--meta { border-color: var(--primary-purple); border-top-style: dashed; }
.legend .sample--meta::after { border-left-color: var(--primary-purple); }
.legend .sample--flow { border-color: var(--primary-purple); }
.legend .sample--flow::after { border-left-color: var(--primary-purple); }
.legend .sample--gov { border-color: var(--accent-pink); border-top-style: dashed; }
.legend .sample--gov::after { border-left-color: var(--accent-pink); }
.legend .swatch { width: 26px; height: 18px; border: 2px solid var(--primary-purple); border-radius: 5px; background: #fff; flex: none; }
.legend .swatch--dashed { border-style: dashed; }
.legend .swatch--out { background: var(--purple-tint-2); }
.legend .swatch--fill { background: var(--primary-purple); }
.legend .swatch--navy { background: var(--purple-700); border-color: var(--purple-700); }
.legend .swatch--magenta { background: var(--accent-magenta); border-color: var(--accent-magenta); }
.legend .swatch--peach { background: var(--bg-peach); border-color: var(--bg-peach); clip-path: polygon(50% 0, 100% 50%, 50% 100%, 0 50%); }
.legend .swatch--tag { background: var(--border-soft); border-color: var(--border-soft); border-radius: 999px; }
.legend .swatch--muted { border-color: var(--gray-out); }

/* barra de composição numerada */
.composition { margin-top: 14px; border: 1.5px solid var(--border-soft); border-radius: var(--radius-md); background: var(--bg-subtle); padding: 16px 22px; display: flex; align-items: center; gap: 26px; font-size: 12px; }
.composition .step { display: flex; align-items: center; gap: 10px; }
.composition .num { width: 32px; height: 32px; border-radius: 50%; background: var(--primary-purple); color: #fff; font-weight: 800; display: flex; align-items: center; justify-content: center; flex: none; }
.composition .step:nth-of-type(odd) .num { background: var(--dark-navy); }
.composition .step b { display: block; color: var(--text-strong); }
.composition .step span { color: var(--text-muted); }
.composition .sep { width: 28px; height: 0; border-top: 2px solid var(--dark-navy); position: relative; }
.composition .sep::after { content: ""; position: absolute; right: -2px; top: -5px; border: 4px solid transparent; border-left: 7px solid var(--dark-navy); }

/* camadas de dado: saturação crescente do roxo (nunca marrom/amarelo) */
.layer { border: 2px solid var(--primary-purple); border-radius: var(--radius-md); padding: 14px 16px; background: #fff; }
.layer h3 { margin: 0; font-size: 15px; font-weight: 700; color: var(--text-strong); }
.layer p { margin: 4px 0 0; font-size: 12px; color: var(--text-muted); }
.layer--1 { background: var(--purple-tint-2); }
.layer--2 { background: var(--purple-tint-3); }
.layer--3 { background: var(--primary-purple); }
.layer--3 h3, .layer--3 p { color: #fff; }

/* setas — SVG overlay desenhado por diagram.js */
svg.arrows { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; overflow: visible; }
svg.arrows path.a { fill: none; stroke-width: 2; }
svg.arrows .a-exec { stroke: var(--dark-navy); }
svg.arrows .a-data { stroke: var(--dark-navy); stroke-dasharray: 6 5; }
svg.arrows .a-meta { stroke: var(--primary-purple); stroke-dasharray: 6 5; }
svg.arrows .a-flow { stroke: var(--primary-purple); }
svg.arrows .a-gov { stroke: var(--accent-pink); stroke-dasharray: 6 5; }
svg.arrows marker path { fill: var(--dark-navy); }
svg.arrows #m-meta path, svg.arrows #m-flow path { fill: var(--primary-purple); }
svg.arrows #m-gov path { fill: var(--accent-pink); }
svg.arrows text { font-family: var(--font); font-size: 11.5px; font-weight: 600; fill: var(--purple-700); paint-order: stroke; stroke: #fff; stroke-width: 4px; stroke-linejoin: round; }
```

- [ ] **Step 2: Criar `references/diagram.js`**

```js
/* govhub-diagramas — desenha as setas declaradas em
   <script type="application/json" id="arrows">[...]</script> como SVG sobre .canvas.
   Seta: {"from":"id","to":"id","type":"exec|data|meta|flow|gov","label":"opcional",
          "fromSide":"top|right|bottom|left","toSide":"...", "via": número (x da vertical
          numa rota horizontal, ou y da horizontal numa rota vertical),
          "labelAt":"start|mid|end", "dx":0, "dy":0}
   Posições vêm do layout real (getBoundingClientRect) — nada de coordenadas à mão. */
(function () {
  const NS = 'http://www.w3.org/2000/svg';
  const TYPES = ['exec', 'data', 'meta', 'flow', 'gov'];

  function box(id, root) {
    const el = document.getElementById(id);
    if (!el) throw new Error('seta aponta para id inexistente: ' + id);
    const r = el.getBoundingClientRect(), o = root.getBoundingClientRect();
    const x = r.left - o.left, y = r.top - o.top;
    return { x, y, w: r.width, h: r.height, cx: x + r.width / 2, cy: y + r.height / 2 };
  }
  function anchor(b, side) {
    return { top: [b.cx, b.y], bottom: [b.cx, b.y + b.h], left: [b.x, b.cy], right: [b.x + b.w, b.cy] }[side];
  }
  function autoSides(a, b) {
    const dx = b.cx - a.cx, dy = b.cy - a.cy;
    if (Math.abs(dx) > Math.abs(dy)) return dx > 0 ? ['right', 'left'] : ['left', 'right'];
    return dy > 0 ? ['bottom', 'top'] : ['top', 'bottom'];
  }

  function draw() {
    const root = document.querySelector('.canvas') || document.querySelector('.diagram');
    const def = document.getElementById('arrows');
    if (!root || !def) return;
    root.querySelectorAll('svg.arrows').forEach(s => s.remove());
    const svg = document.createElementNS(NS, 'svg');
    svg.setAttribute('class', 'arrows');
    svg.innerHTML = '<defs>' + TYPES.map(t =>
      '<marker id="m-' + t + '" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto" markerUnits="userSpaceOnUse">' +
      '<path d="M0,0 L9,4.5 L0,9 z"/></marker>').join('') + '</defs>';

    JSON.parse(def.textContent).forEach(a => {
      const A = box(a.from, root), B = box(a.to, root);
      const [sa, sb] = autoSides(A, B);
      const fromSide = a.fromSide || sa, toSide = a.toSide || sb;
      const [x1, y1] = anchor(A, fromSide), [x2, y2] = anchor(B, toSide);
      const horiz = fromSide === 'left' || fromSide === 'right';
      const type = a.type || 'flow';
      let d, label;
      if (Math.abs(horiz ? y1 - y2 : x1 - x2) < 1) {
        d = 'M' + x1 + ',' + y1 + ' L' + x2 + ',' + y2;
        label = [(x1 + x2) / 2, (y1 + y2) / 2];
      } else if (horiz) {
        const mx = a.via != null ? a.via : (x1 + x2) / 2;
        d = 'M' + x1 + ',' + y1 + ' L' + mx + ',' + y1 + ' L' + mx + ',' + y2 + ' L' + x2 + ',' + y2;
        label = { start: [(x1 + mx) / 2, y1], end: [(mx + x2) / 2, y2], mid: [mx, (y1 + y2) / 2] }[a.labelAt || 'mid'];
      } else {
        const my = a.via != null ? a.via : (y1 + y2) / 2;
        d = 'M' + x1 + ',' + y1 + ' L' + x1 + ',' + my + ' L' + x2 + ',' + my + ' L' + x2 + ',' + y2;
        label = { start: [x1, (y1 + my) / 2], end: [x2, (my + y2) / 2], mid: [(x1 + x2) / 2, my] }[a.labelAt || 'mid'];
      }
      const p = document.createElementNS(NS, 'path');
      p.setAttribute('d', d);
      p.setAttribute('class', 'a a-' + type);
      p.setAttribute('marker-end', 'url(#m-' + type + ')');
      svg.appendChild(p);
      if (a.label) {
        const t = document.createElementNS(NS, 'text');
        // rota vertical: texto à direita da linha; horizontal: centrado acima
        const vertical = !horiz && Math.abs(x1 - x2) < 1;
        t.setAttribute('x', label[0] + (a.dx || 0) + (vertical ? 10 : 0));
        t.setAttribute('y', label[1] + (a.dy || 0) + (vertical ? 4 : -6));
        t.setAttribute('text-anchor', vertical ? 'start' : 'middle');
        t.textContent = a.label;
        svg.appendChild(t);
      }
    });
    root.appendChild(svg);
  }

  window.drawArrows = draw;
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(draw);
  else window.addEventListener('load', draw);
})();
```

- [ ] **Step 3: Criar `scripts/package.json`, `scripts/.gitignore`, `scripts/setup.sh`**

`scripts/package.json`:
```json
{
  "name": "govhub-diagramas-scripts",
  "private": true,
  "type": "module",
  "description": "Renderizador HTML -> PNG dos diagramas Gov Hub",
  "dependencies": {
    "playwright": "^1.47.0"
  }
}
```

`scripts/.gitignore`:
```
node_modules/
package-lock.json
```

`scripts/setup.sh`:
```bash
#!/usr/bin/env bash
# Instala o renderizador (Playwright + Chromium). Rode UMA vez por máquina.
# Pode pedir sudo: o Chromium precisa de libs do sistema (libnss3, libgbm, ...).
set -euo pipefail
cd "$(dirname "$0")"
command -v node >/dev/null || { echo "Node.js 18+ é necessário: https://nodejs.org" >&2; exit 1; }
npm install --no-fund --no-audit
npx playwright install --with-deps chromium
echo "OK. Teste: node render.mjs ../templates/arquitetura-blocos.html /tmp/teste.png"
```

Depois: `chmod +x 01-govhub/govhub-diagramas/scripts/setup.sh`.

- [ ] **Step 4: Criar `scripts/render.mjs`**

```js
#!/usr/bin/env node
// govhub-diagramas — HTML -> PNG.
// Uso: node render.mjs <entrada.html> [saida.png] [--width 1500] [--scale 2] [--selector ".diagram"]
// Sai com 0 e o caminho do PNG; 1 em erro de uso; 2 sem renderizador disponível.
import { resolve, dirname, basename, extname, join } from 'node:path';
import { existsSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';

const USO = 'Uso: node render.mjs <entrada.html> [saida.png] [--width 1500] [--scale 2] [--selector ".diagram"]';
const opt = { width: 1500, scale: 2, selector: '.diagram' };
const pos = [];
const args = process.argv.slice(2);
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--width') opt.width = Number(args[++i]);
  else if (args[i] === '--scale') opt.scale = Number(args[++i]);
  else if (args[i] === '--selector') opt.selector = args[++i];
  else pos.push(args[i]);
}
if (!pos[0]) { console.error(USO); process.exit(1); }
const input = resolve(pos[0]);
if (!existsSync(input)) { console.error('Arquivo não encontrado: ' + input); process.exit(1); }
const output = resolve(pos[1] || join(dirname(input), basename(input, extname(input)) + '.png'));
const here = dirname(fileURLToPath(import.meta.url));

async function comPlaywright() {
  let pw;
  try { pw = await import('playwright'); } catch { return false; }
  let browser;
  try { browser = await pw.chromium.launch(); }
  catch (e) { console.error('playwright instalado, mas o Chromium não abriu:\n' + e.message.split('\n')[0]); return false; }
  try {
    const page = await browser.newPage({ viewport: { width: opt.width, height: 100 }, deviceScaleFactor: opt.scale });
    await page.goto(pathToFileURL(input).href, { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    const fonteOk = await page.evaluate(() =>
      [...document.fonts].some(f => f.family.replace(/["']/g, '') === 'Reddit Sans' && f.status === 'loaded'));
    console.log(fonteOk ? 'fonte: Reddit Sans carregada' : 'AVISO: Reddit Sans NÃO carregou (sem internet?) — o PNG sai com fonte fallback');
    await page.evaluate(() => { if (window.drawArrows) window.drawArrows(); });
    const el = page.locator(opt.selector).first();
    if (await el.count()) await el.screenshot({ path: output });
    else { console.log('seletor ' + opt.selector + ' não encontrado; capturando a página inteira'); await page.screenshot({ path: output, fullPage: true }); }
  } finally { await browser.close(); }
  return true;
}

function comChrome() {
  const bins = ['google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser', 'chrome'];
  const bin = bins.find(b => spawnSync('sh', ['-c', 'command -v ' + b], { stdio: 'ignore' }).status === 0);
  if (!bin) return false;
  console.log('playwright indisponível; usando ' + bin + ' --screenshot (escala 1x, sem espera de fonte, altura fixa 4000)');
  const r = spawnSync(bin, ['--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars',
    '--window-size=' + opt.width + ',4000', '--screenshot=' + output, pathToFileURL(input).href], { stdio: 'inherit' });
  return r.status === 0;
}

if (await comPlaywright() || comChrome()) {
  console.log('PNG: ' + output);
} else {
  console.error('Nenhum renderizador disponível (playwright ou Chrome/Chromium).\nInstale uma vez com:\n  bash ' + join(here, 'setup.sh'));
  process.exit(2);
}
```

- [ ] **Step 5: Criar `scripts/inline_assets.mjs`**

```js
#!/usr/bin/env node
// govhub-diagramas — copia um template embutindo diagram.css e diagram.js (HTML único, portável).
// Uso: node inline_assets.mjs <template.html> <saida.html>
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { resolve, dirname } from 'node:path';

const [src, dst] = process.argv.slice(2);
if (!src || !dst) { console.error('Uso: node inline_assets.mjs <template.html> <saida.html>'); process.exit(1); }
const srcAbs = resolve(src);
let html = readFileSync(srcAbs, 'utf8');
html = html.replace(/<link\s+rel="stylesheet"\s+href="([^"]+)">/g, (_, href) =>
  '<style>\n' + readFileSync(resolve(dirname(srcAbs), href), 'utf8') + '\n</style>');
html = html.replace(/<script\s+src="([^"]+)"><\/script>/g, (_, s) =>
  '<script>\n' + readFileSync(resolve(dirname(srcAbs), s), 'utf8') + '\n</script>');
mkdirSync(dirname(resolve(dst)), { recursive: true });
writeFileSync(resolve(dst), html);
console.log('HTML: ' + resolve(dst));
```

- [ ] **Step 6: Instalar o renderizador**

Run: `bash 01-govhub/govhub-diagramas/scripts/setup.sh`
Expected: termina com `OK. Teste: ...`. Se `playwright install --with-deps` pedir sudo e o ambiente não permitir, rode `sudo npx playwright install-deps chromium` manualmente e repita.

- [ ] **Step 7: HTML de fumaça e teste do render**

Criar `$SCRATCH/smoke.html` (SCRATCH = diretório scratchpad da sessão), com caminhos absolutos para os assets:

```bash
S=/tmp/claude-1000/-home-joaoegewarth-GovHub-skills/*/scratchpad; S=$(echo $S)
R=$(pwd)/01-govhub/govhub-diagramas/references
cat > "$S/smoke.html" <<EOF
<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>smoke</title>
<link rel="stylesheet" href="$R/diagram.css"></head><body>
<div class="diagram"><h1 class="title">Fumaça</h1>
<div class="canvas" style="display:grid;grid-template-columns:300px 300px;gap:200px">
  <div class="node" id="a"><h3>A</h3><p>origem</p></div>
  <div class="node node--out" id="b"><h3>B</h3><p>destino</p></div>
  <script type="application/json" id="arrows">[{"from":"a","to":"b","type":"flow","label":"a → b"}]</script>
</div></div>
<script src="$R/diagram.js"></script></body></html>
EOF
node 01-govhub/govhub-diagramas/scripts/render.mjs "$S/smoke.html" "$S/smoke.png"
python3 -c "from PIL import Image; im=Image.open('$S/smoke.png'); print(im.size); assert im.size[0]==3000"
```
Expected: `fonte: Reddit Sans carregada`, `PNG: .../smoke.png`, `(3000, N)` sem AssertionError. Abrir `smoke.png` (Read) e conferir: seta roxa sólida de A para B com rótulo "a → b", nós com borda roxa `#613EFF`.

- [ ] **Step 8: Testar inline_assets e o código de saída 2**

```bash
node 01-govhub/govhub-diagramas/scripts/inline_assets.mjs "$S/smoke.html" "$S/smoke-inline.html"
grep -c "<link" "$S/smoke-inline.html"; grep -c "drawArrows" "$S/smoke-inline.html"
node 01-govhub/govhub-diagramas/scripts/render.mjs; echo "exit=$?"
```
Expected: `0` links, `>=1` drawArrows, e `Uso: ...` com `exit=1`.

- [ ] **Step 9: Commit**

```bash
git add 01-govhub/govhub-diagramas/references/diagram.css 01-govhub/govhub-diagramas/references/diagram.js 01-govhub/govhub-diagramas/scripts/
git commit -m "feat(govhub-diagramas): motor de render HTML -> PNG e CSS base

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```
Conferir com `git status` que `node_modules/` não entrou.

---

### Task 2: `dbt_lineage.py` (TDD)

**Files:**
- Create: `01-govhub/govhub-diagramas/scripts/fixtures/manifest.min.json`
- Create: `01-govhub/govhub-diagramas/scripts/test_dbt_lineage.py`
- Create: `01-govhub/govhub-diagramas/scripts/dbt_lineage.py`

**Interfaces:**
- Produces: `load(manifest_path: str, group: str = 'schema') -> dict` com `{"groups": [{"name": str, "nodes": [{"id","name","kind","materialization","description"}]}], "edges": [[from_id, to_id], ...]}`; CLI `python3 dbt_lineage.py <manifest.json> [--group schema|layer]` (exit 0 JSON no stdout; 1 uso; 2 arquivo inexistente).

- [ ] **Step 1: Criar a fixture `scripts/fixtures/manifest.min.json`**

```json
{
  "metadata": {"dbt_schema_version": "https://schemas.getdbt.com/dbt/manifest/v12.json"},
  "sources": {
    "source.minc.salic.projetos": {
      "resource_type": "source", "source_name": "salic", "name": "projetos",
      "schema": "bronze", "path": "models/sources.yml",
      "description": "Réplica diária da tabela de projetos do SALIC"
    }
  },
  "nodes": {
    "model.minc.stg_projetos": {
      "resource_type": "model", "name": "stg_projetos", "schema": "silver",
      "path": "silver/stg_projetos.sql", "original_file_path": "models/silver/stg_projetos.sql",
      "description": "Projetos tipados e deduplicados",
      "config": {"materialized": "view"},
      "depends_on": {"nodes": ["source.minc.salic.projetos"]}
    },
    "model.minc.cotas": {
      "resource_type": "model", "name": "cotas", "schema": "cotas",
      "path": "gold/cotas.sql", "original_file_path": "models/gold/cotas.sql",
      "description": "Cotas por grupo no grão de pagamento",
      "config": {"materialized": "table"},
      "depends_on": {"nodes": ["model.minc.stg_projetos", "seed.minc.deflator"]}
    },
    "seed.minc.deflator": {
      "resource_type": "seed", "name": "deflator", "schema": "bacen",
      "path": "deflator.csv", "original_file_path": "seeds/deflator.csv",
      "description": "Série do deflator (SGS/Bacen)",
      "config": {"materialized": "seed"},
      "depends_on": {"nodes": []}
    },
    "test.minc.not_null_cotas": {
      "resource_type": "test", "name": "not_null_cotas", "schema": "cotas",
      "path": "not_null_cotas.sql", "config": {"materialized": "test"},
      "depends_on": {"nodes": ["model.minc.cotas"]}
    }
  }
}
```

- [ ] **Step 2: Escrever o teste `scripts/test_dbt_lineage.py`**

```python
"""Testes de dbt_lineage.py. Rode: python3 scripts/test_dbt_lineage.py (ou pytest)."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dbt_lineage import load  # noqa: E402

FIX = os.path.join(HERE, "fixtures", "manifest.min.json")


def _names(out):
    return {g["name"]: [n["name"] for n in g["nodes"]] for g in out["groups"]}


def test_group_by_schema():
    assert _names(load(FIX, "schema")) == {
        "bacen": ["deflator"],
        "bronze": ["salic.projetos"],
        "cotas": ["cotas"],
        "silver": ["stg_projetos"],
    }


def test_group_by_layer():
    names = _names(load(FIX, "layer"))
    assert names["fonte"] == ["salic.projetos"]
    assert names["silver"] == ["stg_projetos"]
    assert names["gold"] == ["cotas"]
    assert names["bacen"] == ["deflator"]  # seed sem camada no path cai no schema


def test_edges_sorted_and_tests_ignored():
    out = load(FIX)
    assert out["edges"] == [
        ["model.minc.stg_projetos", "model.minc.cotas"],
        ["seed.minc.deflator", "model.minc.cotas"],
        ["source.minc.salic.projetos", "model.minc.stg_projetos"],
    ]
    kinds = {n["id"]: n["kind"] for g in out["groups"] for n in g["nodes"]}
    assert "test.minc.not_null_cotas" not in kinds
    assert kinds["seed.minc.deflator"] == "seed"
    assert kinds["source.minc.salic.projetos"] == "source"


def test_materialization_and_description():
    nodes = {n["id"]: n for g in load(FIX)["groups"] for n in g["nodes"]}
    assert nodes["model.minc.cotas"]["materialization"] == "table"
    assert nodes["model.minc.stg_projetos"]["materialization"] == "view"
    assert nodes["source.minc.salic.projetos"]["description"].startswith("Réplica")


def test_cli_missing_file_exit_2():
    r = subprocess.run([sys.executable, os.path.join(HERE, "dbt_lineage.py"), "/nao/existe.json"],
                       capture_output=True, text=True)
    assert r.returncode == 2
    assert "dbt parse" in r.stderr


def test_cli_bad_group_exit_1():
    r = subprocess.run([sys.executable, os.path.join(HERE, "dbt_lineage.py"), FIX, "--group", "x"],
                       capture_output=True, text=True)
    assert r.returncode == 1


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
```

- [ ] **Step 3: Rodar e ver falhar**

Run: `python3 01-govhub/govhub-diagramas/scripts/test_dbt_lineage.py`
Expected: `ModuleNotFoundError: No module named 'dbt_lineage'`

- [ ] **Step 4: Escrever `scripts/dbt_lineage.py`**

```python
#!/usr/bin/env python3
"""govhub-diagramas — extrai nós e arestas de um target/manifest.json do dbt.

Uso: python3 dbt_lineage.py <manifest.json> [--group schema|layer]

  --group schema  agrupa pelo schema físico (mapa de schemas)       [padrão]
  --group layer   agrupa pela camada inferida do path do modelo
                  (models/bronze/..., silver, gold, staging, marts...);
                  sources viram "fonte"; sem camada no path, usa o schema.

Saída (stdout, JSON):
  {"groups": [{"name": "...", "nodes": [{"id", "name", "kind", "materialization", "description"}]}],
   "edges": [[from_id, to_id], ...]}

Só stdlib. O JSON é insumo para diagramar — não gera layout.
"""
import json
import re
import sys

LAYER_RE = re.compile(
    r"(?:^|/)(bronze|silver|gold|staging|stg|intermediate|int|marts?|raw|prata|ouro|bruto)(?:/|_|$)",
    re.IGNORECASE,
)
KINDS = {"model", "seed", "snapshot"}


def _layer_of(item):
    if item["kind"] == "source":
        return "fonte"  # source é sempre o estágio "Fontes", mesmo que more no schema bronze
    path = item.get("original_file_path") or item.get("path") or ""
    m = LAYER_RE.search(path) or LAYER_RE.search(item.get("schema") or "")
    if m:
        return m.group(1).lower()
    return item.get("schema") or "outros"


def _items(manifest):
    items = {}
    for uid, s in manifest.get("sources", {}).items():
        items[uid] = {
            "id": uid, "name": f"{s['source_name']}.{s['name']}", "kind": "source",
            "materialization": "source", "description": s.get("description", ""),
            "schema": s.get("schema", ""), "path": s.get("path", ""),
            "original_file_path": s.get("original_file_path", ""),
        }
    for uid, n in manifest.get("nodes", {}).items():
        if n["resource_type"] not in KINDS:
            continue
        items[uid] = {
            "id": uid, "name": n["name"], "kind": n["resource_type"],
            "materialization": n.get("config", {}).get("materialized", "view"),
            "description": n.get("description", ""), "schema": n.get("schema", ""),
            "path": n.get("path", ""), "original_file_path": n.get("original_file_path", ""),
        }
    return items


def load(manifest_path, group="schema"):
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)
    items = _items(manifest)
    groups = {}
    for it in items.values():
        key = (it["schema"] or "sem-schema") if group == "schema" else _layer_of(it)
        groups.setdefault(key, []).append(
            {k: it[k] for k in ("id", "name", "kind", "materialization", "description")})
    edges = []
    for uid, n in manifest.get("nodes", {}).items():
        if uid not in items:
            continue
        for dep in n.get("depends_on", {}).get("nodes", []):
            if dep in items:
                edges.append([dep, uid])
    return {
        "groups": [{"name": k, "nodes": sorted(v, key=lambda x: x["name"])} for k, v in sorted(groups.items())],
        "edges": sorted(edges),
    }


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 1
    group = "schema"
    if "--group" in argv:
        i = argv.index("--group")
        group = argv[i + 1] if i + 1 < len(argv) else ""
    if group not in ("schema", "layer"):
        print("--group deve ser schema ou layer", file=sys.stderr)
        return 1
    try:
        out = load(argv[1], group)
    except FileNotFoundError:
        print(f"{argv[1]} não existe. Gere com: dbt parse (ou dbt compile) no projeto dbt.", file=sys.stderr)
        return 2
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 5: Rodar e ver passar**

Run: `python3 01-govhub/govhub-diagramas/scripts/test_dbt_lineage.py`
Expected: seis linhas `ok test_...`, sem traceback.

- [ ] **Step 6: Commit**

```bash
git add 01-govhub/govhub-diagramas/scripts/dbt_lineage.py 01-govhub/govhub-diagramas/scripts/test_dbt_lineage.py 01-govhub/govhub-diagramas/scripts/fixtures/manifest.min.json
git commit -m "feat(govhub-diagramas): dbt_lineage.py extrai nós e arestas do manifest

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 3: References — `colors.md`, gramáticas portadas e `grammar-arquitetura.md`

**Files:**
- Create: `01-govhub/govhub-diagramas/references/colors.md`
- Create: `01-govhub/govhub-diagramas/references/grammar-processo.md` (a partir da `govhub-fluxos`)
- Create: `01-govhub/govhub-diagramas/references/grammar-dados.md` (a partir da `govhub-fluxos`)
- Create: `01-govhub/govhub-diagramas/references/grammar-arquitetura.md`

Origem para portar: `FLX=$(ls -d ~/.claude/skills/synced/*/govhub-fluxos)`.

- [ ] **Step 1: Criar `references/colors.md`**

```markdown
# Cores dos diagramas — papel → token da IDV

Os tokens vivem em `diagram.css` (espelho de
`govhub-visual-identity/references/tokens.css`). Use **só** estes valores.
O roxo/laranja antigo (`#7A34F3`, `#5B21B6`, `#F97316`) e a paleta Tailwind
(`#8B5CF6`) foram descontinuados — figuras antigas que os usam estão fora da
identidade.

## Tabela papel → token

| Papel no diagrama | Token | Hex | Classe |
|---|---|---|---|
| Zona/ator principal, pílulas, setas de leitura de dados | `--primary-purple` | `#613EFF` | `.zone`, `.pill`, `.a-flow` |
| Título do diagrama; setas de execução e transferência | `--dark-navy` | `#0A005A` | `.title`, `.a-exec`, `.a-data` |
| Segundo ator/estágio; texto roxo sobre fundo claro | `--purple-700` | `#3F28A6` | `.lane:nth-of-type(2)`, `.tag`, rótulos de seta |
| Terceiro ator / camada intermediária | `--accent-magenta` | `#EF41FF` | `.lane:nth-of-type(3)`, `.pill--magenta` |
| Destaque pontual: pendente, governança, alerta LGPD | `--accent-pink` | `#F9006F` | `.pill--pink`, `.node--pink`, `.note`, `.a-gov` |
| Fundo de nota/callout quente e de decisão | `--bg-peach` | `#FFE7E1` | `.note`, `.decision` |
| Fundo de zona | `--bg-subtle` | `#F8F9FA` | `.zone` |
| Nó de saída / camada bruta | `--purple-tint-2` | `rgba(97,62,255,.12)` | `.node--out`, `.layer--1` |
| Camada intermediária | `--purple-tint-3` | `rgba(97,62,255,.30)` | `.layer--2` |
| Camada curada / pronta | `--primary-purple` | `#613EFF` | `.layer--3` |
| Bordas sutis, tracejado de legado, etiquetas | `--border-soft` | `#E9DFFF` | `.legend`, `.tag`, `.note--plain` |
| Fora do escopo | `--gray-out` | `#9CA3AF` | `.node--muted` |
| Texto forte / corpo / secundário | `--text-strong` / `--text-body` / `--text-muted` | `#202020` / `#2D3748` / `#666666` | `h3`, `body`, `p` |

## Regras de distribuição

- **Cada ator ou estágio recebe uma cor fixa** em todos os seus nós. Ordem de
  atribuição, do mais estrutural ao mais operacional: `--primary-purple` →
  `--purple-700` → `--accent-magenta` → `--dark-navy`. Quatro atores é o
  máximo confortável; acima disso, divida o diagrama.
- **Pink é só alerta/destaque** (pendente, governança, LGPD). Nunca como cor
  de ator.
- **Camadas bronze/prata/ouro**: progressão de saturação do roxo
  (`.layer--1` → `.layer--2` → `.layer--3`). Nunca marrom, amarelo ou dourado.
- **Instrumento/sistema** (`.tag`): fundo `--border-soft`, texto `--purple-700`.
- **Observação** (`.note--plain`): fundo neutro, nunca saturado. `.note`
  (peach + pink) só para status/alerta; `.note--lgpd` para dado pessoal.
- **Fora do escopo**: cinza, nunca cor de marca.

## Tipografia

Reddit Sans em tudo. Título 800; nomes de nó 700; descrições 400 em
`--text-muted`; pílulas caixa alta 600 com `letter-spacing`. Sem Oswald.

## Acessibilidade

- Texto branco só sobre roxo, navy, magenta ou pink sólidos.
- Sobre fundos claros (zona, tint, peach), sempre texto escuro.
- Rótulos de seta usam contorno branco (`paint-order: stroke`) para ler sobre
  qualquer fundo.
```

- [ ] **Step 2: Portar `grammar-processo.md`**

```bash
FLX=$(ls -d ~/.claude/skills/synced/*/govhub-fluxos)
D=01-govhub/govhub-diagramas/references
cp "$FLX/references/fluxo-processo.md" "$D/grammar-processo.md"
sed -i 's/`cores-fluxos.md`/`colors.md`/g' "$D/grammar-processo.md"
```

Depois **acrescentar ao final** do arquivo:

```markdown

## Como cada nó vira HTML (template `fluxo-raias.html`)

| Nó | Marcação |
|---|---|
| Raia | `<div class="lane"><div class="lane-head">Ator</div><div class="lane-body">…</div></div>` dentro de `<div class="lanes">` |
| Início / Fim | `<div class="dot" id="..."><span>Início</span></div>` / `<div class="dot dot--end" id="..."><span>Aprovado</span></div>` |
| Etapa | `<div class="node node--fill" id="..."><h3>Verbo + objeto</h3></div>` (cor do ator vem da raia: use `node--fill` na raia 1, `style="background:var(--purple-700);border-color:var(--purple-700)"` na 2, `var(--accent-magenta)` na 3) |
| Decisão | `<div class="decision" id="...">Pergunta?</div>`; as saídas são duas setas com `label` "Sim"/"Não" |
| Instrumento/Sistema | `<span class="tag">PNCP</span>` dentro do nó |
| Observação | `<div class="note note--plain"><strong>Prazo:</strong> 10 dias úteis</div>` |
| Subprocesso | `<div class="node node--legacy" id="..."><h3>Nome</h3><p>ver diagrama X</p></div>` |
| Fora do escopo | `<div class="node node--muted">…</div>` |
| Posição na raia | `style="grid-column: N"` (7 colunas de 170 px por padrão) |
| Setas | JSON em `#arrows`, `type: "flow"`; entre raias use `fromSide`/`toSide` explícitos |
```

- [ ] **Step 3: Portar `grammar-dados.md`**

```bash
cp "$FLX/references/fluxo-dados.md" "$D/grammar-dados.md"
sed -i 's/`cores-fluxos.md`/`colors.md`/g' "$D/grammar-dados.md"
```

Editar à mão as duas menções a `govhub-mapeamento-politica-dado`:
- Na seção inicial (item 1 "Fluxo da política ao dado"): trocar `(ver \`govhub-mapeamento-politica-dado\`)` por `(a versão simplificada para divulgação é um segundo diagrama, feito depois deste)`.
- Na seção "Nível de detalhe": trocar a frase `depois aplique a simplificação de três elos de \`govhub-mapeamento-politica-dado\` separadamente` por `depois faça um segundo diagrama simplificado (três elos: política → instrumento → dado)`.

Conferir: `grep -c "mapeamento-politica" "$D/grammar-dados.md"` → `0`.

Acrescentar ao final:

```markdown

## Como cada nó vira HTML (template `pipeline-dados.html`)

| Nó | Marcação |
|---|---|
| Estágio do ciclo de vida | `<section class="zone"><span class="pill">Fontes</span>…</section>` — um por coluna, esquerda → direita |
| Fonte de dados | `<div class="node" id="..."><h3>SALIC</h3><p>Postgres · réplica</p><span class="tag">SFTP</span></div>` |
| Ingestão/ETL | `<div class="node node--fill" id="..."><h3>Airflow</h3><p>DAG …</p></div>` |
| Camada de dado | `<div class="layer layer--1|--2|--3" id="..."><h3>bronze</h3><p>…</p></div>` |
| Validação/qualidade | `<div class="decision" id="...">testes dbt passaram?</div>` |
| Consumo/saída | `<div class="node node--out" id="..."><h3>Superset</h3></div>` |
| Observação técnica | `<div class="note note--plain">…</div>` |
| Dado pessoal | `<div class="note note--lgpd">CPF anonimizado na silver</div>` |
| Setas | JSON em `#arrows`; `data` para transferência, `exec` para orquestração, `flow` para leitura |
| Lineage automático | `python3 scripts/dbt_lineage.py target/manifest.json --group layer` |
```

- [ ] **Step 4: Criar `references/grammar-arquitetura.md`**

```markdown
# Arquitetura em blocos e mapa de schemas

Duas famílias que não têm "fluxo" no sentido de sequência: mostram **o que
existe e como se conecta**. Exemplos de referência: Figura 3 (arquitetura do
Data Lakehouse) e Figura 8 (schemas do banco) do 3º Relatório Parcial MinC.

## A. Arquitetura em blocos (template `arquitetura-blocos.html`)

Quando usar: componentes de infraestrutura/software agrupados por função,
com setas tipadas entre eles (execução, dados, metadados, governança).

### Gramática

| Elemento | Marcação | Regra |
|---|---|---|
| Zona | `<section class="zone">` com `<span class="pill">NOME</span>` | Agrupa componentes por função (ex.: "Orquestração e armazenamento"). `zone--dashed` para o que ainda não existe ou é lógico. Máximo 3 zonas. |
| Componente | `<div class="node" id="x">` com `<span class="pill">N. PAPEL</span>`, `<h3>Nome real</h3>`, `<p>o que é</p>` e uma descrição do que faz | Numere as pílulas na ordem de leitura. Nome real do software (Airflow, MinIO, Trino), nunca genérico. |
| Sub-bloco | `.node` dentro de `.node` (ex.: formato de tabela dentro do armazenamento) | Só um nível de aninhamento. |
| Status | `<span class="note"><strong>implantado</strong></span>` ou `<strong>previsto</strong> — pendente` | Sempre que o diagrama misturar o que existe e o que é proposto, marque cada um. |
| Seta | `#arrows` com `type` em `exec` (orquestra), `data` (transfere dados), `meta` (consulta metadados), `flow` (leitura/resultado), `gov` (governança) | Toda seta tem um tipo e o tipo aparece na legenda. Rótulo curto na seta quando a relação não for óbvia. |
| Legenda | `<div class="legend">` com um `.item` por tipo de seta usado | Obrigatória. |
| Composição | `<div class="composition">` — barra numerada dos componentes | Opcional; resume "do que é feito" em uma linha. |

### Layout

- Duas colunas (`display:grid`) com a zona de origem à esquerda e a de
  consumo à direita; o dado "anda" da esquerda para a direita.
- Dentro da zona, empilhe os componentes na ordem em que o dado passa por
  eles (`.stack` com `gap` ≥ 52px, para as setas e rótulos caberem).
- Um componente transversal (governança) fica numa coluna lateral, com
  setas `gov` para o que ele controla.

## B. Mapa de schemas / camadas (template `mapa-schemas.html`)

Quando usar: inventário de schemas (ou datasets, buckets, tópicos) de um
mesmo banco, organizado por **papel** (ingestão, legado, saída), com as
convenções ao lado.

### Gramática

| Elemento | Marcação | Regra |
|---|---|---|
| Container | Uma `.zone` com pílula "PostgreSQL · banco X" | O que está dentro pertence ao mesmo banco/instância. |
| Coluna por papel | `<div class="col"><h2>PAPEL</h2>…</div>` | Ingestão ativa · cargas pontuais/legado · saída da transformação. Não organize por camada técnica se o banco é organizado por domínio (regra "schema por domínio"). |
| Schema | `.node` (ingestão ativa), `.node.node--legacy` (pontual/legado), `.node.node--out` (saída) com `<h3>nome_físico</h3><p>conteúdo · frequência</p>` | Nome físico exato, minúsculo. Uma linha de conteúdo e uma de cadência. |
| Convenções | `<div class="conv"><h2>Convenções</h2><dl>…</dl></div>` | Cada convenção = `dt` (nome) + `dd` (uma frase). Só as que valem para o banco inteiro. |
| Seta | Uma única seta `flow` "a transformação consome os schemas de pouso" da coluna de ingestão para a de saída, com `via` na calha entre colunas | Não desenhe uma seta por schema — o detalhe fino vem do lineage do dbt num diagrama de pipeline. |
| Legenda | Três `.swatch`: borda sólida, tracejada, preenchida | Obrigatória. |

### Fonte dos dados

`python3 scripts/dbt_lineage.py target/manifest.json --group schema` devolve
os schemas com seus modelos e a descrição de cada um; use as descrições para
a linha de conteúdo, e o `materialization`/frequência da DAG para a cadência.
Schemas sem produtor no dbt (legado) entram na coluna do meio.

## Checklist (as duas famílias)

- Nome real de cada componente/schema, sem genérico.
- Toda seta tem tipo e o tipo está na legenda.
- Estado (implantado / previsto) marcado quando houver mistura.
- Máximo ~12 nós; acima disso, dois diagramas.
```

- [ ] **Step 5: Verificar e commitar**

```bash
grep -il "7a34f3\|f97316\|5b21b6\|8b5cf6\|cairosvg\|visualize\|project_knowledge" 01-govhub/govhub-diagramas/references/*.md
```
Expected: só `colors.md` (que cita os hex como descontinuados). Os dois `grammar-*.md` portados não devem citar `cairosvg`/`visualize` — se citarem, remover a frase.

```bash
git add 01-govhub/govhub-diagramas/references/
git commit -m "docs(govhub-diagramas): cores da IDV e gramáticas de processo, dados e arquitetura

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 4: Template `arquitetura-blocos.html` (recriação da Figura 3)

**Files:**
- Create: `01-govhub/govhub-diagramas/templates/arquitetura-blocos.html`

**Interfaces:**
- Consumes: classes de `diagram.css`, contrato de `#arrows`, `render.mjs`.

- [ ] **Step 1: Escrever o template**

```html
<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Arquitetura Física Proposta — Data Lakehouse</title>
<link rel="stylesheet" href="../references/diagram.css">
<style>
  /* layout específico deste diagrama */
  .cols { display: grid; grid-template-columns: 560px 1fr; gap: 96px; align-items: start; }
  .stack { display: grid; gap: 64px; }
  .node .row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; align-items: center; }
  .node .name { text-align: center; }
  .node .name h3 { font-size: 20px; }
  .node .desc { font-size: 13px; color: var(--text-muted); text-align: center; }
  .sub { margin-top: 18px; border: 2px solid var(--primary-purple); border-radius: var(--radius-md); background: var(--bg-subtle); padding: 16px 22px; text-align: center; }
  .sub h4 { margin: 0 0 12px; font-size: 13px; letter-spacing: .06em; color: var(--purple-700); }
  .sub .row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .sub .row .node { padding: 12px; }
  .sub .foot { margin-top: 10px; font-size: 12px; color: var(--text-muted); }
  .right { display: grid; grid-template-columns: 1fr 270px; gap: 30px; align-items: start; }
  .right .stack { gap: 52px; }
  .split { display: grid; grid-template-columns: 1fr 1fr; }
  .split > div { padding: 6px 12px; text-align: center; }
  .split > div + div { border-left: 1px solid var(--border-soft); }
  .status { display: inline-block; margin-top: 10px; padding: 6px 14px; border: 1.5px dashed var(--accent-pink); background: var(--bg-peach); border-radius: var(--radius-sm); font-size: 12px; color: var(--text-body); }
  .status b { color: var(--accent-pink); }
  .ranger .name { text-align: center; }
  .ranger ul { margin: 12px 0 0; padding: 12px 0 0 14px; font-size: 12.5px; color: var(--text-body); border-top: 1px solid var(--border-soft); }
  .ranger li { margin: 6px 0; }
  .badge { position: absolute; padding: 6px 10px; border: 1.5px solid var(--primary-purple); border-radius: var(--radius-sm); background: #fff; font-size: 11.5px; font-weight: 600; color: var(--purple-700); text-align: center; }
</style>
</head>
<body>
<div class="diagram">
  <h1 class="title">Arquitetura Física Proposta — Data Lakehouse</h1>
  <p class="subtitle">Estado-alvo: a composição inteira na infraestrutura do Ministério da Cultura</p>

  <div class="canvas">
    <div class="cols">
      <!-- ESQUERDA: orquestração e armazenamento -->
      <section class="zone">
        <span class="pill">Orquestração e armazenamento</span>
        <div class="stack">
          <div class="node" id="airflow">
            <span class="pill">1. Orquestração</span>
            <div class="row">
              <div class="name"><h3>Apache Airflow</h3><p>orquestrador de pipelines</p></div>
              <div class="desc">orquestração e agendamento dos pipelines de dados</div>
            </div>
          </div>
          <div class="node" id="lakehouse">
            <span class="pill">2. Data Lakehouse · Armazenamento</span>
            <div class="row">
              <div class="name"><h3>MinIO</h3><p>object storage</p></div>
              <div class="desc">armazenamento em formato aberto e colunar</div>
            </div>
            <div class="sub">
              <h4>FORMATO DE TABELA ABERTA</h4>
              <div class="row">
                <div class="node"><h3>Apache Iceberg</h3><p>formato de tabela</p></div>
                <div class="node"><h3>Parquet</h3><p>arquivo colunar</p></div>
              </div>
              <div class="foot">dados armazenados em Parquet sob Iceberg</div>
            </div>
          </div>
        </div>
      </section>

      <!-- DIREITA: catálogo, consulta e consumo -->
      <section class="zone zone--dashed">
        <span class="pill">Catálogo, consulta e consumo</span>
        <div class="right">
          <div class="stack">
            <div class="node" id="catalog">
              <span class="pill">3. Catálogo de dados · Metadados</span>
              <div class="row">
                <div class="name"><h3>PostgreSQL</h3><p>(catalog)</p></div>
                <div class="desc">esquemas, tabelas, partições, estatísticas e permissões (Iceberg)</div>
              </div>
            </div>
            <div class="node" id="trino">
              <span class="pill">4. Motor de busca</span>
              <div class="row">
                <div class="name"><h3>Trino</h3><p>(query engine)</p></div>
                <div class="desc">engine única de consulta distribuída que lê os dados do MinIO usando os metadados do catálogo<br><span class="status"><b>implantado no ambiente</b></span></div>
              </div>
            </div>
          </div>
          <div class="node node--pink ranger" id="ranger">
            <span class="pill pill--pink">5. Governança e acesso</span>
            <div class="name"><h3>Apache Ranger</h3><p>governança e controle de acesso</p></div>
            <ul>
              <li>Controle de acesso baseado em políticas</li>
              <li>Auditoria de acesso</li>
              <li>Segurança de dados em todo o ecossistema</li>
            </ul>
            <div style="text-align:center"><span class="status"><b>previsto na proposta</b><br>implantação pendente</span></div>
          </div>
        </div>
        <div class="node" id="consumo" style="margin-top:52px">
          <span class="pill">6. Consumo</span>
          <div class="split">
            <div><h3>Usuários e equipes</h3><p>analistas, cientistas de dados, gestores, sistemas e aplicações</p></div>
            <div><h3>Agentes de IA · GraphRAG</h3><p>geração de SQL a partir de perguntas em linguagem natural (ver Meta 04)</p></div>
          </div>
        </div>
      </section>
    </div>
    <!-- etiqueta sobre a seta de dados entre as zonas; ajuste left/top após o render -->
    <div class="badge" id="badge-parquet" style="left:572px;top:400px">dados brutos<br>em Parquet</div>

    <script type="application/json" id="arrows">
    [
      {"from":"airflow","to":"lakehouse","type":"exec","label":"executa e orquestra os pipelines","fromSide":"bottom","toSide":"top"},
      {"from":"lakehouse","to":"trino","type":"data","fromSide":"right","toSide":"left"},
      {"from":"catalog","to":"trino","type":"meta","label":"leitura de metadados e estatísticas","fromSide":"bottom","toSide":"top"},
      {"from":"trino","to":"consumo","type":"flow","label":"leitura de dados","fromSide":"bottom","toSide":"top"},
      {"from":"ranger","to":"catalog","type":"gov","fromSide":"left","toSide":"right"},
      {"from":"ranger","to":"trino","type":"gov","fromSide":"left","toSide":"right"}
    ]
    </script>
  </div>

  <div class="legend">
    <span class="legend-title">LEGENDA</span>
    <div class="item"><span class="sample"></span><div><b>Orquestração / execução</b><span>Airflow aciona os pipelines</span></div></div>
    <div class="item"><span class="sample sample--data"></span><div><b>Transferência de dados</b><span>armazenamento em Parquet</span></div></div>
    <div class="item"><span class="sample sample--meta"></span><div><b>Consulta de metadados</b><span>esquemas e partições</span></div></div>
    <div class="item"><span class="sample sample--flow"></span><div><b>Leitura de dados</b><span>resultado das consultas</span></div></div>
    <div class="item"><span class="sample sample--gov"></span><div><b>Governança / acesso</b><span>políticas e auditoria</span></div></div>
  </div>

  <div class="composition">
    <div><span class="legend-title">COMPOSIÇÃO</span><br><span style="color:var(--text-muted)">do Lakehouse</span></div>
    <div class="step"><span class="num">1</span><div><b>Object storage</b><span>MinIO</span></div></div><span class="sep"></span>
    <div class="step"><span class="num">2</span><div><b>Catálogo</b><span>PostgreSQL</span></div></div><span class="sep"></span>
    <div class="step"><span class="num">3</span><div><b>Motor de consulta</b><span>Trino</span></div></div><span class="sep"></span>
    <div class="step"><span class="num">4</span><div><b>Formato de tabela aberta</b><span>Parquet sob Iceberg</span></div></div><span class="sep"></span>
    <div class="step"><span class="num">5</span><div><b>Governança</b><span>Apache Ranger</span></div></div>
  </div>
</div>
<script src="../references/diagram.js"></script>
</body>
</html>
```

- [ ] **Step 2: Renderizar e conferir visualmente**

```bash
node 01-govhub/govhub-diagramas/scripts/render.mjs 01-govhub/govhub-diagramas/templates/arquitetura-blocos.html "$S/arq.png"
python3 -c "from PIL import Image; im=Image.open('$S/arq.png'); print(im.size); assert im.size[0]==3000"
```
Abrir `$S/arq.png` (Read) e conferir, item a item:
1. Seis setas visíveis, cada uma com a cor/tracejado do tipo (exec navy sólida; data navy tracejada; meta roxa tracejada; flow roxa sólida; gov pink tracejada).
2. Nenhuma seta atravessa um nó. Se a seta `lakehouse→trino` cruzar o badge ou um nó, ajuste `via` (x da vertical, em px relativos a `.canvas`) na seta e `left/top` do `#badge-parquet` até o badge ficar sobre o trecho horizontal da seta.
3. Rótulos legíveis, não sobrepostos a bordas. Ajuste `dx`/`dy` (px) por seta.
4. Pílulas cobrindo a borda com contorno branco; nenhuma pílula cortada.
5. Texto sem quebra estranha em "Agentes de IA · GraphRAG".
Repita render → conferência até os 5 itens passarem. Comparar lado a lado com a Fig. 3 original (extraída em `$S/fig_p31.png` na conversa; se não existir, `python3 -c "import pymupdf;d=pymupdf.open('/mnt/d/Downloads/relatorio-com-anexos-versao-final-revisada.pdf');pymupdf.Pixmap(d,1857).save('$S/fig_p31.png')"`): mesmo conteúdo, mesma disposição, cores novas.

- [ ] **Step 3: Commit**

```bash
git add 01-govhub/govhub-diagramas/templates/arquitetura-blocos.html
git commit -m "feat(govhub-diagramas): template de arquitetura em blocos (Fig. 3 MinC com IDV atual)

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 5: Template `mapa-schemas.html` (recriação da Figura 8)

**Files:**
- Create: `01-govhub/govhub-diagramas/templates/mapa-schemas.html`

- [ ] **Step 1: Escrever o template**

```html
<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Modelo Físico — Os Schemas do Banco</title>
<link rel="stylesheet" href="../references/diagram.css">
<style>
  .grid { display: grid; grid-template-columns: 300px 300px 300px 1fr; gap: 40px; align-items: start; }
  .col h2, .conv h2 { margin: 0 0 14px; font-size: 13px; letter-spacing: .12em; text-transform: uppercase; color: var(--primary-purple); }
  .col .node { margin-bottom: 16px; }
  .col .node h3 { font-size: 15px; }
  .col .node p { font-size: 11.5px; line-height: 1.4; }
  .conv { border: 1.5px solid var(--border-soft); border-radius: var(--radius-md); background: #fff; padding: 20px 22px; margin-top: 32px; }
  .conv dl { margin: 0; font-size: 11.5px; }
  .conv dt { font-weight: 700; color: var(--text-strong); margin-top: 8px; }
  .conv dd { margin: 2px 0 0 10px; color: var(--text-muted); }
  .legend--bare { justify-content: center; border: 0; background: transparent; }
</style>
</head>
<body>
<div class="diagram">
  <h1 class="title">Modelo Físico — Os Schemas do Banco</h1>
  <p class="subtitle">Um único PostgreSQL, organizado em schemas por papel</p>

  <div class="canvas">
    <section class="zone">
      <span class="pill">PostgreSQL · banco minc</span>
      <div class="grid">
        <div class="col">
          <h2>Ingestão · Airflow</h2>
          <div class="node" id="bronze"><h3>bronze</h3><p>réplica do SALIC · 5 bancos<br>recarga completa diária · colunas em texto</p></div>
          <div class="node"><h3>control</h3><p>log de ingestão do SALIC</p></div>
          <div class="node"><h3>transferegov</h3><p>pouso das APIs + territorialização<br>atualização por chave natural</p></div>
          <div class="node"><h3>relatorio_gestao</h3><p>planilhas de gestão parseadas</p></div>
          <div class="node"><h3>bbagil</h3><p>extrato · subtransações · controle</p></div>
          <div class="node" id="bacen"><h3>bacen</h3><p>séries do SGS · deflator</p></div>
          <div class="node"><h3>ibge_sidra</h3><p>agregados do SIDRA · MUNIC · semanal</p></div>
        </div>
        <div class="col">
          <h2>Cargas pontuais e legado</h2>
          <div class="node node--legacy"><h3>ancine</h3><p>planilha da agência</p></div>
          <div class="node node--legacy"><h3>bsc · bb_agil</h3><p>schemas legados, sem produtor</p></div>
        </div>
        <div class="col">
          <h2>Saída da transformação</h2>
          <div class="node node--out" id="cotas"><h3>cotas</h3><p>bronze, silver e gold do domínio<br>grão de pagamento · cotas por grupo</p></div>
          <div class="node node--out"><h3>agentes</h3><p>perfis, dado mestre e primeiro acesso</p></div>
          <div class="node node--out"><h3>metadata</h3><p>inventário autogerado dos modelos</p></div>
          <div class="node node--out"><h3>minc</h3><p>eixo de tempo da camada semântica</p></div>
        </div>
        <div class="conv">
          <h2>Convenções</h2>
          <dl>
            <dt>· Schema por domínio</dt><dd>o nome físico vem do domínio, não da camada</dd>
            <dt>· Tipagem no pouso</dt><dd>toda coluna nasce em texto; a conversão é do dbt</dd>
            <dt>· Sem chave estrangeira</dt><dd>a integridade é verificada por teste, não por restrição</dd>
            <dt>· Índice único</dt><dd>nas tabelas por atualização incremental, garante idempotência</dd>
            <dt>· Nomes minúsculos</dt><dd>no SALIC, o padrão banco__tabela preserva a origem</dd>
          </dl>
        </div>
      </div>
    </section>

    <script type="application/json" id="arrows">
    [
      {"from":"bacen","to":"cotas","type":"flow","label":"a transformação consome os schemas de pouso","fromSide":"right","toSide":"left","via":684,"labelAt":"start","dx":60}
    ]
    </script>
  </div>

  <div class="legend legend--bare">
    <div class="item"><span class="swatch"></span><span>ingestão ativa</span></div>
    <div class="item"><span class="swatch swatch--dashed"></span><span>carga pontual ou legado</span></div>
    <div class="item"><span class="swatch swatch--out"></span><span>saída da transformação</span></div>
  </div>
</div>
<script src="../references/diagram.js"></script>
</body>
</html>
```

- [ ] **Step 2: Renderizar e conferir**

```bash
node 01-govhub/govhub-diagramas/scripts/render.mjs 01-govhub/govhub-diagramas/templates/mapa-schemas.html "$S/schemas.png"
```
Abrir o PNG e conferir: (1) a seta sai do lado direito de `bacen`, sobe pela calha entre a 2ª e a 3ª coluna (não cruza `ancine`/`bsc`) e entra em `cotas` — se cruzar, ajustar `via` (x em px relativo a `.canvas`; a calha fica entre `24+300+40+300 = 664` e `704`); (2) rótulo acima do trecho horizontal; (3) `ancine`/`bsc` tracejados, coluna de saída com tint roxo; (4) painel de convenções alinhado ao topo das colunas. Comparar com a Fig. 8 (`$S/fig_p41.png`, xref 1972 do PDF).

- [ ] **Step 3: Commit**

```bash
git add 01-govhub/govhub-diagramas/templates/mapa-schemas.html
git commit -m "feat(govhub-diagramas): template de mapa de schemas (Fig. 8 MinC com IDV atual)

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 6: Template `fluxo-raias.html`

**Files:**
- Create: `01-govhub/govhub-diagramas/templates/fluxo-raias.html`

Conteúdo **ilustrativo** (não é um processo real do Gov Hub; o Claude substitui tudo). Três atores, uma decisão, um instrumento, uma observação, um subprocesso.

- [ ] **Step 1: Escrever o template**

```html
<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Fluxo de processo — exemplo ilustrativo</title>
<link rel="stylesheet" href="../references/diagram.css">
<style>
  /* cor de etapa por raia (a mesma da cabeça da raia) */
  .lane:nth-of-type(2) .node--fill { background: var(--purple-700); border-color: var(--purple-700); }
  .lane:nth-of-type(3) .node--fill { background: var(--accent-magenta); border-color: var(--accent-magenta); }
  .lane:nth-of-type(2) .dot { background: var(--purple-700); }
  .lane:nth-of-type(3) .dot { background: var(--accent-magenta); }
  .lane:nth-of-type(2) .dot--end { box-shadow: 0 0 0 3px #fff, 0 0 0 5px var(--purple-700); }
  .lane:nth-of-type(3) .dot--end { box-shadow: 0 0 0 3px #fff, 0 0 0 5px var(--accent-magenta); }
  .lane-body .note { font-size: 11px; }
</style>
</head>
<body>
<div class="diagram">
  <h1 class="title">Concessão de bolsa — fluxo de processo</h1>
  <p class="subtitle">Exemplo ilustrativo: substitua atores, etapas e sistemas pelos da fonte real</p>

  <div class="canvas">
    <div class="lanes">
      <div class="lane">
        <div class="lane-head">Bolsista</div>
        <div class="lane-body">
          <div class="dot" id="ini-bolsista" style="grid-column:1"><span>Início</span></div>
          <div class="node node--fill" id="solicitar" style="grid-column:2"><h3>Preencher solicitação</h3><span class="tag">Formulário SEI</span></div>
          <div class="node node--fill" id="complementar" style="grid-column:4"><h3>Complementar documentos</h3></div>
          <div class="dot dot--end" id="fim-bolsista" style="grid-column:7"><span>Bolsa paga</span></div>
        </div>
      </div>
      <div class="lane">
        <div class="lane-head">Coordenação</div>
        <div class="lane-body">
          <div class="node node--fill" id="analisar" style="grid-column:3"><h3>Analisar documentação</h3></div>
          <div class="decision" id="completa" style="grid-column:4">Documentação completa?</div>
          <div class="node node--fill" id="aprovar" style="grid-column:5"><h3>Aprovar concessão</h3><span class="tag">Portaria de bolsas</span></div>
          <div class="note note--plain" style="grid-column:6"><strong>Prazo:</strong> 10 dias úteis após o recebimento</div>
        </div>
      </div>
      <div class="lane">
        <div class="lane-head">Sistema de bolsas</div>
        <div class="lane-body">
          <div class="node node--fill" id="registrar" style="grid-column:5"><h3>Registrar bolsista</h3><span class="tag">Sistema de bolsas</span></div>
          <div class="node node--legacy" id="pagamento" style="grid-column:6"><h3>Gerar pagamento</h3><p>ver fluxo financeiro</p></div>
        </div>
      </div>
    </div>

    <script type="application/json" id="arrows">
    [
      {"from":"ini-bolsista","to":"solicitar","type":"flow"},
      {"from":"solicitar","to":"analisar","type":"flow","fromSide":"bottom","toSide":"left"},
      {"from":"analisar","to":"completa","type":"flow"},
      {"from":"completa","to":"complementar","type":"flow","label":"Não","fromSide":"top","toSide":"bottom"},
      {"from":"complementar","to":"analisar","type":"flow","fromSide":"left","toSide":"top","via":150},
      {"from":"completa","to":"aprovar","type":"flow","label":"Sim"},
      {"from":"aprovar","to":"registrar","type":"flow","fromSide":"bottom","toSide":"top"},
      {"from":"registrar","to":"pagamento","type":"flow"},
      {"from":"pagamento","to":"fim-bolsista","type":"flow","fromSide":"right","toSide":"bottom"}
    ]
    </script>
  </div>

  <div class="legend">
    <span class="legend-title">LEGENDA</span>
    <div class="item"><span class="swatch swatch--fill"></span><span>etapa do Bolsista</span></div>
    <div class="item"><span class="swatch swatch--navy"></span><span>etapa da Coordenação</span></div>
    <div class="item"><span class="swatch swatch--magenta"></span><span>etapa do Sistema</span></div>
    <div class="item"><span class="swatch swatch--peach"></span><span>decisão</span></div>
    <div class="item"><span class="swatch swatch--tag"></span><span>instrumento / sistema</span></div>
    <div class="item"><span class="swatch swatch--dashed"></span><span>subprocesso (outro diagrama)</span></div>
    <div class="item"><span class="swatch" style="border-color:var(--border-soft);background:var(--bg-subtle)"></span><span>observação</span></div>
  </div>
</div>
<script src="../references/diagram.js"></script>
</body>
</html>
```

- [ ] **Step 2: Renderizar e conferir**

```bash
node 01-govhub/govhub-diagramas/scripts/render.mjs 01-govhub/govhub-diagramas/templates/fluxo-raias.html "$S/raias.png"
```
Conferir: (1) três raias com cabeças roxo / roxo-escuro / magenta e etapas na mesma cor; (2) losango legível com "Sim" para a direita e "Não" subindo para "Complementar documentos"; (3) a seta de retorno `complementar→analisar` não cruza a etapa "Preencher solicitação" — se cruzar, ajustar `via` (y relativo a `.canvas`) para passar acima da raia; (4) nenhum texto branco ilegível; (5) o `.tag` cabe dentro do nó. Ajustar `grid-column` e `via` até passar.

- [ ] **Step 3: Commit**

```bash
git add 01-govhub/govhub-diagramas/templates/fluxo-raias.html
git commit -m "feat(govhub-diagramas): template de fluxo de processo com raias

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 7: Template `pipeline-dados.html`

**Files:**
- Create: `01-govhub/govhub-diagramas/templates/pipeline-dados.html`

- [ ] **Step 1: Escrever o template**

```html
<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Pipeline de dados — fonte ao consumo</title>
<link rel="stylesheet" href="../references/diagram.css">
<style>
  .stages { display: grid; grid-template-columns: 300px 260px 1fr 300px; gap: 56px; align-items: start; }
  .zone .stack { display: grid; gap: 22px; }
  .layers { display: grid; gap: 18px; }
  .zone--plain { background: #fff; }
</style>
</head>
<body>
<div class="diagram">
  <h1 class="title">Pipeline de dados — da fonte ao consumo</h1>
  <p class="subtitle">Exemplo ilustrativo: substitua fontes, DAGs, camadas e saídas pelos do projeto</p>

  <div class="canvas">
    <div class="stages">
      <section class="zone">
        <span class="pill">Fontes</span>
        <div class="stack">
          <div class="node" id="salic"><h3>SALIC</h3><p>Postgres · réplica completa diária</p><span class="tag">acesso direto</span></div>
          <div class="node" id="transferegov"><h3>TransfereGov</h3><p>API · atualização por chave natural</p><span class="tag">API REST</span></div>
          <div class="node" id="planilhas"><h3>Planilhas de gestão</h3><p>xlsx enviadas por e-mail</p><span class="tag">carga pontual</span></div>
        </div>
      </section>

      <section class="zone">
        <span class="pill">Ingestão</span>
        <div class="stack">
          <div class="node node--fill" id="airflow"><h3>Apache Airflow</h3><p>uma DAG por fonte · pouso em texto</p></div>
          <div class="note note--plain"><strong>Cadência:</strong> diária (SALIC), semanal (IBGE), sob demanda (planilhas)</div>
        </div>
      </section>

      <section class="zone zone--plain">
        <span class="pill">Transformação · dbt</span>
        <div class="layers">
          <div class="layer layer--1" id="bronze"><h3>bronze</h3><p>cópia fiel da fonte, colunas em texto</p></div>
          <div class="layer layer--2" id="silver"><h3>silver</h3><p>tipagem, deduplicação, chaves naturais</p></div>
          <div class="decision" id="testes" style="justify-self:center">testes dbt passaram?</div>
          <div class="layer layer--3" id="gold"><h3>gold</h3><p>grão de análise · métricas do domínio</p></div>
          <div class="note note--lgpd">CPF de proponentes anonimizado na silver; a gold não carrega dado pessoal</div>
        </div>
      </section>

      <section class="zone">
        <span class="pill">Consumo</span>
        <div class="stack">
          <div class="node node--out" id="superset"><h3>Superset</h3><p>painéis institucionais</p></div>
          <div class="node node--out" id="relatorios"><h3>Relatórios</h3><p>PDF · notas técnicas</p></div>
          <div class="node node--out" id="agentes"><h3>Agentes de IA</h3><p>SQL a partir de linguagem natural</p></div>
        </div>
      </section>
    </div>

    <script type="application/json" id="arrows">
    [
      {"from":"salic","to":"airflow","type":"data","fromSide":"right","toSide":"left"},
      {"from":"transferegov","to":"airflow","type":"data","fromSide":"right","toSide":"left"},
      {"from":"planilhas","to":"airflow","type":"data","fromSide":"right","toSide":"left"},
      {"from":"airflow","to":"bronze","type":"exec","label":"carrega","fromSide":"right","toSide":"left"},
      {"from":"bronze","to":"silver","type":"flow","fromSide":"bottom","toSide":"top"},
      {"from":"silver","to":"testes","type":"flow","fromSide":"bottom","toSide":"top"},
      {"from":"testes","to":"gold","type":"flow","label":"sim","fromSide":"bottom","toSide":"top"},
      {"from":"gold","to":"superset","type":"flow","fromSide":"right","toSide":"left"},
      {"from":"gold","to":"relatorios","type":"flow","fromSide":"right","toSide":"left"},
      {"from":"gold","to":"agentes","type":"flow","fromSide":"right","toSide":"left"}
    ]
    </script>
  </div>

  <div class="legend">
    <span class="legend-title">LEGENDA</span>
    <div class="item"><span class="sample sample--data"></span><div><b>Transferência de dados</b><span>fonte → pouso</span></div></div>
    <div class="item"><span class="sample"></span><div><b>Orquestração</b><span>Airflow executa a carga</span></div></div>
    <div class="item"><span class="sample sample--flow"></span><div><b>Leitura / transformação</b><span>dbt e consumo</span></div></div>
    <div class="item"><span class="swatch swatch--out"></span><span class="swatch" style="background:var(--purple-tint-3)"></span><span class="swatch swatch--fill"></span><span>camadas: bruta → tratada → curada</span></div>
    <div class="item"><span class="swatch swatch--peach"></span><span>validação de qualidade</span></div>
    <div class="item"><span class="swatch" style="border-color:var(--accent-pink);background:var(--bg-peach)"></span><span>ponto de tratamento LGPD</span></div>
  </div>
</div>
<script src="../references/diagram.js"></script>
</body>
</html>
```

- [ ] **Step 2: Renderizar e conferir**

```bash
node 01-govhub/govhub-diagramas/scripts/render.mjs 01-govhub/govhub-diagramas/templates/pipeline-dados.html "$S/pipeline.png"
```
Conferir: (1) três setas tracejadas convergindo no Airflow sem cruzar os nós vizinhos; (2) progressão bronze (tint claro) → silver (tint médio) → gold (roxo sólido, texto branco); (3) nota LGPD com prefixo "LGPD ·" em pink; (4) três setas saindo da gold para o consumo; (5) legenda com todos os tipos usados. Ajustar `gap`/`via` se algo cruzar.

- [ ] **Step 3: Commit**

```bash
git add 01-govhub/govhub-diagramas/templates/pipeline-dados.html
git commit -m "feat(govhub-diagramas): template de pipeline de dados

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 8: `SKILL.md`

**Files:**
- Create: `01-govhub/govhub-diagramas/SKILL.md`

- [ ] **Step 1: Escrever o SKILL.md**

```markdown
---
name: govhub-diagramas
description: >-
  Constrói diagramas técnicos do Gov Hub em HTML/CSS com a identidade visual
  oficial e gera o PNG pronto para relatório, slide ou docx: arquitetura em
  blocos (componentes, zonas, setas tipadas), mapa de schemas/camadas de um
  banco, fluxo de processo institucional com raias por ator (decisões,
  instrumentos, subprocessos) e pipeline de dados (fonte → ingestão →
  bronze/prata/ouro → consumo, com marcação LGPD). Lê o lineage do dbt
  (manifest.json) quando existir. Use sempre que pedirem para desenhar,
  mapear ou diagramar um processo, uma arquitetura, os schemas de um banco
  ou um fluxo de dados, mesmo sem a palavra "fluxograma". Dispara com:
  "desenha esse fluxo", "diagrama de arquitetura", "fluxograma", "mapeia
  esse processo", "raias por ator", "diagrama dos schemas", "fluxo
  bronze/prata/ouro", "figura para o relatório", "como os dados chegam no",
  "arquitetura do lakehouse". Não é para Mermaid em Markdown (use
  mermaid-diagram-specialist) nem só para aplicar tema (govhub-visual-identity).
---

# Diagramas técnicos — Gov Hub

Você é o(a) arquiteto(a) de processos e de dados do Gov Hub: pega uma lógica
(um rito administrativo, uma arquitetura, um pipeline, os schemas de um
banco) e transforma num diagrama que qualquer pessoa técnica consegue
auditar — nada inventado, nada omitido, com a cara do Gov Hub. O resultado
é um HTML editável e um PNG nítido, no padrão das figuras dos relatórios
parciais (ex.: Figuras 3 e 8 do 3º Relatório Parcial MinC).

## As quatro famílias

| Família | Quando usar | Eixo organizador | Template | Gramática |
|---|---|---|---|---|
| **Arquitetura em blocos** | Componentes de infra/software agrupados por função, com setas tipadas (execução, dados, metadados, governança). | Função do componente | `templates/arquitetura-blocos.html` | `references/grammar-arquitetura.md` (A) |
| **Mapa de schemas / camadas** | Inventário de schemas (datasets, buckets) de um banco, por papel: ingestão, legado, saída. | Papel do schema | `templates/mapa-schemas.html` | `references/grammar-arquitetura.md` (B) |
| **Fluxo de processo** | Rito com mais de um ator, decisões, instrumentos, aprovações. | Ator (uma raia por ator) | `templates/fluxo-raias.html` | `references/grammar-processo.md` |
| **Pipeline de dados** | Como o dado sai da fonte e vira informação: ingestão, camadas, validação, consumo. Também política → instrumento → sistema. | Estágio do ciclo de vida do dado | `templates/pipeline-dados.html` | `references/grammar-dados.md` |

Um caso pode precisar de duas famílias (o processo que alimenta um sistema
que entra num pipeline). Faça dois diagramas ligados por um nó de
subprocesso, nunca um só sobrecarregado.

## Princípios

1. **A fonte manda, você não inventa.** Antes de desenhar, liste em texto:
   atores/estágios, etapas em ordem, decisões e suas saídas, sistemas e
   instrumentos, observações e base legal. Fonte = documento, ata, código,
   DAG, `manifest.json`. Se faltar informação para fechar uma etapa,
   pergunte. Não preencha lacuna com passo "provável".
2. **Legibilidade acima de completude.** Máximo ~12 nós por diagrama. Acima
   disso, divida com nó de subprocesso. Rótulos curtos (verbo + objeto);
   detalhe técnico vai para `.tag` e `.note`, não para dentro da caixa.
3. **Sempre com legenda.** Todo tipo de nó e de seta usado aparece na
   `.legend`.
4. **IDV atual, sem exceção.** Só os tokens de `references/colors.md`.
   Reddit Sans. Nada de `#7A34F3`/`#F97316` (paleta antiga) nem Inter/Tailwind
   (figuras antigas do relatório MinC usam isso e estão fora da identidade).
5. **Dado pessoal aparece no diagrama.** CPF, nome de bolsista, dado de
   beneficiário: marque o ponto de anonimização com `.note--lgpd`.
6. **Nome real de tudo.** Sistema, schema, DAG, camada: o nome que o projeto
   usa (confira no código/documentação), nunca um genérico.

## Como construir — passo a passo

1. **Extrair a lógica da fonte.**

   | Fonte | Como extrair |
   |---|---|
   | Projeto dbt (`target/manifest.json`) | `python3 scripts/dbt_lineage.py target/manifest.json --group schema` (mapa de schemas) ou `--group layer` (pipeline). Sem manifest: `dbt parse`. |
   | DAGs do Airflow, código | Ler os arquivos; listar fontes, tabelas de pouso, cadência. |
   | Documento, ata, transcrição, PDF | Ler tudo; cada caixa, seta, sistema e observação da fonte entra na lista. |
   | Descrição do usuário | Listar e confirmar o que ficou ambíguo antes de desenhar. |

   Escreva a lista (atores/estágios, etapas, decisões, sistemas, observações)
   e mostre ao usuário se houver qualquer dúvida.

2. **Escolher a família** pela tabela acima e ler a gramática correspondente
   (obrigatório — ela diz como cada nó vira HTML).

3. **Copiar o template embutindo os assets** para o diretório de saída
   (padrão `./diagramas/`, ou o que o usuário pedir):
   ```bash
   node <skill>/scripts/inline_assets.mjs <skill>/templates/<familia>.html ./diagramas/figura-N-<nome>.html
   ```
   Editar o HTML: título, subtítulo, nós (com `id` únicos), `.tag`, `.note`,
   legenda, e o JSON de setas em `#arrows` (`from`/`to` = ids; `type` = `exec`,
   `data`, `meta`, `flow`, `gov`; `label`; `fromSide`/`toSide`; `via` para
   desviar de um nó). Layout em CSS no `<style>` do próprio arquivo, usando
   só as classes de `references/diagram.css`.

4. **Renderizar:**
   ```bash
   node <skill>/scripts/render.mjs ./diagramas/figura-N-<nome>.html
   ```
   Gera o `.png` ao lado (largura 3000 px, escala 2). Se sair código 2 ou o
   Chromium não abrir, rode `bash <skill>/scripts/setup.sh` (uma vez; pode
   pedir sudo) e repita. Se o log disser que a Reddit Sans não carregou,
   verifique a internet — o PNG saiu com fonte errada.

5. **Conferir o PNG lendo a imagem.** Procure: texto cortado ou quebrado
   em lugar ruim, seta atravessando nó, rótulo em cima de borda, pílula
   cortada, fonte fallback, cor fora da tabela. Corrija o HTML (`via`,
   `dx`/`dy`, `gap`, `grid-column`) e renderize de novo. Só entregue quando
   passar. Diagramas técnicos raramente saem certos na primeira.

6. **Entregar** o HTML, o PNG e a legenda em texto (a mesma da imagem), no
   formato "Figura N. ..." para o usuário colar no relatório. Diga o que foi
   assumido, se algo foi.

## Checklist antes de entregar

- [ ] Nenhuma etapa/componente inventado; nenhum da fonte esquecido.
- [ ] Legenda cobre todos os tipos de nó e de seta usados.
- [ ] Toda seta tem `type`; toda decisão tem as saídas rotuladas.
- [ ] Nome real de cada sistema/schema/camada.
- [ ] Só cores de `references/colors.md`; Reddit Sans carregada no log.
- [ ] Dado pessoal marcado com `.note--lgpd`, se existir.
- [ ] ≤ ~12 nós, ou dividido em dois diagramas.
- [ ] PNG conferido visualmente após o último ajuste.

## O que não fazer

- Não desenhar sem listar a lógica antes.
- Não usar Mermaid, SVG à mão, cairosvg ou coordenadas fixas de seta — as
  setas vêm do JSON `#arrows` e são posicionadas pelo layout.
- Não usar cores fora de `colors.md` nem fonte diferente de Reddit Sans.
- Não entregar PNG sem ter olhado para ele.
- Não publicar o diagrama técnico como peça de divulgação: para isso, faça um
  segundo diagrama simplificado.

## Arquivos

- `references/colors.md` — papel → token. `references/diagram.css` — classes.
  `references/diagram.js` — setas.
- `references/grammar-arquitetura.md`, `grammar-processo.md`, `grammar-dados.md`.
- `templates/*.html` — quatro pontos de partida, um por família.
- `scripts/render.mjs`, `scripts/inline_assets.mjs`, `scripts/dbt_lineage.py`,
  `scripts/setup.sh`.
```

- [ ] **Step 2: Validar o frontmatter e o tamanho da description**

```bash
python3 - <<'EOF'
import re,sys
s=open('01-govhub/govhub-diagramas/SKILL.md',encoding='utf-8').read()
fm=re.match(r'---\n(.*?)\n---',s,re.S).group(1)
desc=re.search(r'description: >-\n((?:  .*\n?)+)',fm).group(1)
desc=' '.join(l.strip() for l in desc.splitlines())
print(len(desc)); assert len(desc)<=1024, "description > 1024 chars (limite do claude.ai)"
assert 'name: govhub-diagramas' in fm
EOF
```
Expected: número ≤ 1024, sem AssertionError. Se passar de 1024, encurtar a lista de gatilhos.

- [ ] **Step 3: Teste de ponta a ponta do fluxo da skill**

```bash
K=01-govhub/govhub-diagramas
node $K/scripts/inline_assets.mjs $K/templates/mapa-schemas.html "$S/diagramas/figura-8-schemas.html"
node $K/scripts/render.mjs "$S/diagramas/figura-8-schemas.html"
ls -la "$S/diagramas/"
```
Expected: `figura-8-schemas.html` sem `<link`, e `figura-8-schemas.png` ao lado, idêntico ao render do template.

- [ ] **Step 4: Commit**

```bash
git add 01-govhub/govhub-diagramas/SKILL.md
git commit -m "feat(govhub-diagramas): SKILL.md com famílias, fluxo de trabalho e checklist

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 9: Registro no marketplace e README + verificação final

**Files:**
- Modify: `.claude-plugin/marketplace.json` (plugins `govhub-skills` e `govhub-core`)
- Modify: `README.md:54-55` (tabela de plugins), `README.md:105-107` (exemplos de acionamento), `README.md:144-146` (tabela da categoria 01)

- [ ] **Step 1: marketplace.json**

Trocar:
- `"Coleção completa — todas as 52 skills de uma vez.` → `"Coleção completa — todas as 53 skills de uma vez.`
- `identidade visual oficial e relatório de prestação de contas a partir do git. (3 skills)"` → `identidade visual oficial, diagramas técnicos (arquitetura, schemas, raias, pipeline) e relatório de prestação de contas a partir do git. (4 skills)"`

Conferir: `python3 -c "import json;json.load(open('.claude-plugin/marketplace.json'))"` sem erro.

- [ ] **Step 2: README.md**

Linha 54: `| \`govhub-skills\` | **Tudo** — as 52 skills de todas as categorias | 52 |` → `... as 53 skills ... | 53 |`.
Linha 55: `— pipelines, identidade visual, prestação de contas | 3 |` → `— pipelines, identidade visual, diagramas técnicos, prestação de contas | 4 |`.

Após a linha `- *"gera o relatório de prestação de contas do último ano"* → dispara a \`accountability-report\`.` inserir:
```markdown
- *"desenha a arquitetura do lakehouse pra figura do relatório"* → dispara a `govhub-diagramas`.
```

Após a linha da tabela de `govhub-visual-identity` (linha 145) inserir:
```markdown
| [`govhub-diagramas`](01-govhub/govhub-diagramas/) | Diagramas técnicos com a IDV: arquitetura em blocos, mapa de schemas, fluxo de processo com raias e pipeline de dados. HTML editável + PNG via Chromium; lê o lineage do dbt. |
```

Conferir que não sobrou "52": `grep -n "52" README.md .claude-plugin/marketplace.json` → vazio (ou só ocorrências não relacionadas à contagem).

- [ ] **Step 3: Verificação final da skill (spec → "Verificação da skill")**

```bash
K=01-govhub/govhub-diagramas
for t in arquitetura-blocos mapa-schemas fluxo-raias pipeline-dados; do
  node $K/scripts/render.mjs $K/templates/$t.html "$S/final-$t.png" | grep -E "fonte|PNG"
  python3 -c "from PIL import Image; im=Image.open('$S/final-$t.png'); assert im.size[0]==3000, im.size; print('$t', im.size)"
done
grep -rniE "7a34f3|f97316|8b5cf6|5b21b6|font-family:[^;]*inter" $K/templates $K/references/diagram.css $K/references/diagram.js && echo "HEX/FONTE PROIBIDO ENCONTRADO" || echo "paleta ok"
python3 $K/scripts/test_dbt_lineage.py
```
Expected: 4× `fonte: Reddit Sans carregada`, 4× tamanho `(3000, N)`, `paleta ok`, 6× `ok test_`.

- [ ] **Step 4: Commit e status**

```bash
git add .claude-plugin/marketplace.json README.md
git commit -m "docs: registra govhub-diagramas no marketplace e no README

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
git status --short   # vazio
git log --oneline -10
```

---

## Notas para quem executa

- `$S` = diretório scratchpad da sessão (`/tmp/claude-1000/-home-joaoegewarth-GovHub-skills/<id>/scratchpad`). PNGs de teste ficam lá, nunca no repo.
- O renderizador exige internet para a Reddit Sans (Google Fonts). Sem internet, o log avisa e o PNG sai com fallback — não entregue esse PNG.
- Ajustes visuais (`via`, `dx`, `dy`, `gap`, `grid-column`, `left/top` do badge) são esperados nas Tasks 4–7; o critério de pronto é a lista de conferência de cada task, não "ficou parecido".
- Depois de tudo: espelhar a paleta nova na `govhub-fluxos` do claude.ai quando ela for substituída pelo zip desta skill (sem `scripts/`) — fora deste plano.
