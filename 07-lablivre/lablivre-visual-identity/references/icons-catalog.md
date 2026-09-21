# Catálogo de ícones de produto Lab Livre

Os 332 ícones × 3 variantes existem **na paleta do Lab Livre**, na pasta
`lablivre/icons/` do `skills-assets` (recoloridos a partir dos do Gov Hub
em 2026-09-21: mesma geometria, só os hex trocados pelo mapeamento de
`palette.md`). O repositório tem uma pasta por marca, `lablivre/` e
`gov-hub/`, com a mesma estrutura; não misture os dois conjuntos.

Os ícones **não ficam nesta skill** (seriam ~1000 arquivos, acima do limite
de 200 do claude.ai). Eles vivem no repo público
[`GovHub-br/skills-assets`](https://github.com/GovHub-br/skills-assets) e são
servidos por CDN.

## URL

```
https://cdn.jsdelivr.net/gh/GovHub-br/skills-assets@main/lablivre/icons/<nome>-<variante>.svg
```

- `<nome>` — um dos 332 nomes listados abaixo (descritivos do conceito).
- `<variante>` — cada uma traz o **fundo embutido** no próprio SVG, na
  paleta atual (repo regerado em 2026-09-16, mesma nomenclatura de antes):
  `default` (preenchimento rosa claro `#FFE7E1`, contorno azul profundo,
  sombra laranja), `purple` (preenchimento azul profundo `#080056`,
  contorno rosa claro, sombra laranja) e `orange` (preenchimento rosa
  claro, contorno azul profundo, sombra rosa claro). Os nomes
  `purple`/`orange` são históricos; o que vale é a cor do fundo embutido.
  Para relatório/e-book use quase sempre `default`. Regra completa de qual
  variante sobre qual fundo: `editorial-report.md` seção 5.

  > A CDN (`@main`) guarda cache de ~12 h; logo após uma regeração, baixe
  > pelo `raw.githubusercontent.com` ou fixe o SHA do commit na URL.

Exemplo:

```html
<img src="https://cdn.jsdelivr.net/gh/GovHub-br/skills-assets@main/lablivre/icons/document-check-default.svg" alt="">
```

`@main` acompanha o repo (cache CDN de ~12 h). Para congelar uma versão
exata, troque `@main` por uma tag (`@v1`) ou pelo SHA do commit.

## Sem internet no ambiente de geração do PDF

Baixe a pasta e troque os `src=` para caminho relativo (`icons/<nome>-<variante>.svg`):

```bash
git clone --depth 1 https://github.com/GovHub-br/skills-assets.git
cp -r skills-assets/lablivre/icons ./icons
```

ou, sem git:

```bash
curl -sL https://github.com/GovHub-br/skills-assets/archive/refs/heads/main.tar.gz \
  | tar xz --strip-components=2 skills-assets-main/lablivre/icons
```

## Escolha pelo nome

Os nomes seguem o padrão Heroicons (`document-check`, `chart-bar`,
`magnifying-glass`, `user-group`…) mais alguns próprios do Gov Hub
(`pessoal`, `governance`, `orcamento`, `acesso`, `forum`, `teds`, `ia`).
Procure o nome mais próximo do conceito; para conceitos recorrentes no mesmo
documento, fixe um nome e repita.

## 332 nomes

acesso, archive, archive-box-x-mark, archive-download, arrow-down, arrow-down-circle
arrow-down-left, arrow-down-on-square, arrow-down-on-square-stack, arrow-down-right, arrow-down-tray, arrow-left
arrow-left-circle, arrow-left-end-on-rectangle, arrow-long-down, arrow-long-left, arrow-long-right, arrow-long-up
arrow-path, arrow-path-rounded-square, arrow-right, arrow-right-circle, arrow-right-end-on-rectangle, arrow-top-right-on-square
arrow-trending-down, arrow-trending-up, arrow-turn-down-left, arrow-turn-down-right, arrow-turn-left-down, arrow-turn-left-up
arrow-turn-right-down, arrow-turn-right-up, arrow-turn-up-left, arrow-turn-up-right, arrow-up, arrow-up-circle
arrow-up-left, arrow-up-on-square, arrow-up-on-square-stack, arrow-up-right, arrow-up-tray, arrow-uturn-down
arrow-uturn-left, arrow-uturn-right, arrow-uturn-up, arrows-pointing-in, arrows-pointing-out, arrows-right-left
arrows-up-down, at-symbol, backspace, backward, banknotes, bars-2
bars-3, bars-3-bottom-left, bars-3-bottom-right, bars-3-center-left, bars-4, bars-arrow-down
battery-empty, battery-full, battery-half, beaker, bell, bell-alert
bell-slash, bell-snooze, bold, bolt, bolt-slash, book-open
bookmark, bookmark-slash, bookmark-square, briefcase, bug-ant, building-library
building-office, building-office-2, building-storefront, cake, calculator, calendar
calendar-date-range, calendar-days, camera, chart-bar, chart-bar-square, chart-pie
charts, chat-bubble-bottom-center, chat-bubble-bottom-center-text, chat-bubble-left-ellipsis, chat-bubble-oval-left-ellipsis, chat_round
chat_square, check, check-badge, check-circle, chevron-double-down, chevron-double-left
chevron-double-right, chevron-double-up, chevron-down, chevron-left, chevron-right, chevron-up
chevron-up-down, clipboard, clipboard-document, clipboard-document-check, clipboard-document-list, clock
cloud, cloud-arrow-down, cloud-arrow-up, code, code-bracket, code-bracket-square
cog, cog-6-tooth, cog-8-tooth, contratos, courses, cpu
credit-card, cube, cube-transparent, currency-bangladeshi, currency-dollar, currency-euro
currency-pound, currency-rupee, currency-yen, cursor-arrow-rays, cursor-arrow-ripple, database
deploy, desktop, device-phone-mobile, device-tablet, divide, document
document-arrow-down, document-arrow-up, document-chart-bar, document-check, document-currency-bangladeshi, document-currency-dollar
document-currency-euro, document-currency-pound, document-currency-rupee, document-currency-yen, document-duplicate, document-magnifying-glass
document-minus, document-plus, document-text, document_check, download, ellipsis-horizontal
ellipsis-horizontal-circle, ellipsis-vertical, envelope, envelope-open, equals, exclamation-circle
exclamation-triangle, eye, eye-slash, eye_dropper, face-frown, face-smile
figma, film, filters, finger-print, fire, flag
folder, folder-arrow-down, folder-minus, folder-open, folder-plus, forum
forward, funnel, gif, gift, gift-top, github
globe-alt, globe-americas, globe-asia-australia, globe-europe-africa, governance, h1
h2, h3, hand-raised, hand-thumb-down, hand-thumb-up, hashtag
heart, help, home, home-modern, ia, identification
inbox, inbox-arrow-down, inbox-stack, information-circle, italic, key
language, lifebuoy, light-bulb, link, link-slash, list
list-bullet, lock-closed, login, logout, magnifying-glass, magnifying-glass-circle
magnifying-glass-minus, magnifying-glass-plus, map, map-pin, megaphone, microphone
minus, minus-circle, moon, musical-note, newspaper, no-symbol
notification, numbered-list, open-folder, orcamento, paint_brush, paper
paper-clip, pause, pause-circle, pencil, pencil-square, percent-badge
pessoal, phone, phone-arrow-down-left, phone-arrow-up-right, phone-x-mark, photo
pie_chart, play, play-circle, play-pause, plus, plus-circle
power, presentation-chart-line, printer, puzzle-piece, qr-code, radio
receipt, receipt-refund, rectangle-group, rectangle-stack, rss, scale
scissors, send, server, server-2, settings, share
shield-check, shield-exclamation, shopping-bag, shopping-cart, signal, signal-slash
slash, sliders, sort, sparkles, speaker-wave, speaker-x-mark
square-2-stack, square-3-stack-3d, squares-2x2, squares-plus, star, stop
stop-circle, strikethrough, sun, swatch, table-cells, tag
teds, terminal, ticket, tools, trash, trophy
truck, tv, underline, user-circle, user-group, user-minus
user-plus, users, variable, video-camera, video-camera-slash, view-columns
viewfinder-circle, wallet, wifi, window, workflow, wrench
x-circle, x-mark
