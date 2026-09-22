/* govhub-diagramas — desenha as setas declaradas em
   <script type="application/json" id="arrows">[...] (o elemento de id "arrows") como SVG sobre .canvas.
   Seta: {"from":"id","to":"id","type":"exec|data|meta|flow|gov","label":"opcional",
          "fromSide":"top|right|bottom|left","toSide":"...", "via": número (x da vertical
          numa rota horizontal, ou y da horizontal numa rota vertical — ignorado quando
          fromSide e toSide estão em eixos diferentes: a rota vira um único cotovelo em L
          para chegar perpendicular ao alvo, sem ponto de desvio),
          "labelAt":"start|mid|end" (posição do rótulo ao longo da rota; em linha reta = 25% / 50% / 75%), "dx":0, "dy":0}
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
      const fromVert = fromSide === 'top' || fromSide === 'bottom';
      const toVert = toSide === 'top' || toSide === 'bottom';
      const type = a.type || 'flow';
      let d, label, vertical;
      if (fromVert !== toVert) {            // eixos mistos: um único cotovelo, chega perpendicular ao alvo
        d = fromVert
          ? 'M' + x1 + ',' + y1 + ' L' + x1 + ',' + y2 + ' L' + x2 + ',' + y2
          : 'M' + x1 + ',' + y1 + ' L' + x2 + ',' + y1 + ' L' + x2 + ',' + y2;
        const legA = fromVert ? Math.abs(y2 - y1) : Math.abs(x2 - x1);   // primeira perna
        const legB = fromVert ? Math.abs(x2 - x1) : Math.abs(y2 - y1);   // segunda perna
        // rótulo: 'start' = meio da primeira perna, 'end' = meio da segunda, 'mid' = a perna mais longa
        const onFirst = (a.labelAt || 'mid') === 'start' || ((a.labelAt || 'mid') === 'mid' && legA >= legB);
        label = fromVert
          ? (onFirst ? [x1, (y1 + y2) / 2] : [(x1 + x2) / 2, y2])
          : (onFirst ? [(x1 + x2) / 2, y1] : [x2, (y1 + y2) / 2]);
        vertical = fromVert ? onFirst : !onFirst;
      } else if (Math.abs(horiz ? y1 - y2 : x1 - x2) < 1) {
        d = 'M' + x1 + ',' + y1 + ' L' + x2 + ',' + y2;
        label = {
          start: [x1 + (x2 - x1) * 0.25, y1 + (y2 - y1) * 0.25],
          mid:   [(x1 + x2) / 2, (y1 + y2) / 2],
          end:   [x1 + (x2 - x1) * 0.75, y1 + (y2 - y1) * 0.75],
        }[a.labelAt || 'mid'];
        vertical = !horiz;
      } else if (horiz) {
        const mx = a.via != null ? a.via : (x1 + x2) / 2;
        d = 'M' + x1 + ',' + y1 + ' L' + mx + ',' + y1 + ' L' + mx + ',' + y2 + ' L' + x2 + ',' + y2;
        label = { start: [(x1 + mx) / 2, y1], end: [(mx + x2) / 2, y2], mid: [mx, (y1 + y2) / 2] }[a.labelAt || 'mid'];
        vertical = false;
      } else {
        const my = a.via != null ? a.via : (y1 + y2) / 2;
        d = 'M' + x1 + ',' + y1 + ' L' + x1 + ',' + my + ' L' + x2 + ',' + my + ' L' + x2 + ',' + y2;
        label = { start: [x1, (y1 + my) / 2], end: [x2, (my + y2) / 2], mid: [(x1 + x2) / 2, my] }[a.labelAt || 'mid'];
        vertical = false;
      }
      const p = document.createElementNS(NS, 'path');
      p.setAttribute('d', d);
      p.setAttribute('class', 'a a-' + type);
      p.setAttribute('marker-end', 'url(#m-' + type + ')');
      svg.appendChild(p);
      if (a.label) {
        const t = document.createElementNS(NS, 'text');
        // perna vertical: texto à direita da linha; perna horizontal: centrado acima
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
