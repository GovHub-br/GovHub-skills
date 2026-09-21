#!/usr/bin/env bash
# Instala o renderizador (Playwright + Chromium). Rode UMA vez por máquina.
# Pode pedir sudo: o Chromium precisa de libs do sistema (libnss3, libgbm, ...).
set -euo pipefail
cd "$(dirname "$0")"
command -v node >/dev/null || { echo "Node.js 18+ é necessário: https://nodejs.org" >&2; exit 1; }
npm install --no-fund --no-audit
npx playwright install --with-deps chromium
echo "OK. Teste: node render.mjs ../templates/arquitetura-blocos.html /tmp/teste.png"
