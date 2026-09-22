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
if (!pos[0] || !Number.isFinite(opt.width) || !Number.isFinite(opt.scale)) { console.error(USO); process.exit(1); }
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
  } catch (e) {
    await browser.close();
    console.error('render falhou: ' + e.message);
    process.exit(1);
  }
  await browser.close();
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
