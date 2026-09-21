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
