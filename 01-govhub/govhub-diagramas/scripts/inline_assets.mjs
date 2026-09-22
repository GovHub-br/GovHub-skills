#!/usr/bin/env node
// govhub-diagramas — copia um template embutindo diagram.css e diagram.js (HTML único, portável).
// Uso: node inline_assets.mjs <template.html> <saida.html>
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { resolve, dirname } from 'node:path';

const [src, dst] = process.argv.slice(2);
if (!src || !dst) { console.error('Uso: node inline_assets.mjs <template.html> <saida.html>'); process.exit(1); }
const srcAbs = resolve(src);
let html = readFileSync(srcAbs, 'utf8');
let linkCount = 0, scriptCount = 0;
html = html.replace(/<link\s+rel="stylesheet"\s+href="([^"]+)">/g, (_, href) => {
  linkCount++;
  return '<style>\n' + readFileSync(resolve(dirname(srcAbs), href), 'utf8') + '\n</style>';
});
html = html.replace(/<script\s+src="([^"]+)"><\/script>/g, (_, s) => {
  scriptCount++;
  // um "</script" dentro do JS (string ou comentário) fecharia a tag no HTML; escapa
  const js = readFileSync(resolve(dirname(srcAbs), s), 'utf8').replace(/<\/script/gi, '<\\/script');
  return '<script>\n' + js + '\n</script>';
});
if (linkCount === 0) console.error('AVISO: nenhum <link rel="stylesheet"> encontrado');
if (scriptCount === 0) console.error('AVISO: nenhum <script src> encontrado');
mkdirSync(dirname(resolve(dst)), { recursive: true });
writeFileSync(resolve(dst), html);
console.log('HTML: ' + resolve(dst));
