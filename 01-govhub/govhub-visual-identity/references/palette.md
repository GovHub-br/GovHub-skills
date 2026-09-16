# Paleta Gov Hub — referência e quando usar cada cor

Valores extraídos diretamente do Manual de Identidade Visual (MIV) oficial
da marca. Use exatamente estes hexadecimais. Os nomes de token estão em
inglês (ver `tokens.css`).

> **Atualização de paleta:** esta versão substitui totalmente o roxo/laranja
> antigo (`#7A34F3` / `#F97316`), que não fazem mais parte da identidade.
> Qualquer artefato antigo que ainda use esses hex está desatualizado.

## Cores primárias da marca

| Token | Hex | Uso |
|---|---|---|
| `--primary-purple` | `#613EFF` | **Cor-assinatura.** Dominante da identidade — títulos de destaque, cabeçalhos de tabela, botões primários, links, badges, barras de topo, ícones de destaque. Ocupa o papel que o roxo antigo tinha. |
| `--dark-navy` | `#0A005A` | Azul-marinho quase preto. Texto de marca em títulos grandes, fundos escuros de alto contraste, estados "pressed" fortes. |
| `--accent-magenta` | `#EF41FF` | Acento secundário. Segunda parada de gradientes, detalhes, rampa editorial. |
| `--accent-pink` | `#F9006F` | **Acento pontual / CTA.** Ocupa o papel que o laranja tinha: call-to-action, destaque de número-chave. Usar com parcimônia (regra 90/10). |
| `--bg-peach` | `#FFE7E1` | Fundo claro "de marca" — alternativa tingida aos neutros cinza, para seções que precisam de um respiro mais quente que branco puro. |
| `--text-white` | `#FFFFFF` | Texto sobre superfícies roxas, navy ou pink. |

## Estados derivados do primário

| Token | Hex | Uso |
|---|---|---|
| `--purple-600` | `#5235D9` | **Hover/foco** de elementos roxos (botão primário, link). Aproximado por escurecimento — não vem do MIV, ajuste se o design confirmar um valor exato. |
| `--purple-700` | `#3F28A6` | **Active/pressionado**, e roxo para texto sobre fundo branco quando precisar de contraste extra. |

## Neutros e texto

| Token | Hex | Uso |
|---|---|---|
| `--text-strong` | `#202020` | Títulos e texto forte **neutros** (não "de marca"). |
| `--text-body` | `#2D3748` | Corpo de texto padrão — mantido neutro de propósito, ver nota de legibilidade abaixo. |
| `--text-muted` | `#666666` | Legendas, texto secundário, metadados. |

> **Por que o corpo de texto continua neutro:** o MIV não define uma cor de
> texto corrido tingida de marca, e usar `--dark-navy` ou `--primary-purple`
> em blocos longos de texto prejudica a leitura. `--dark-navy` fica reservado
> para títulos, destaques e momentos de marca — não para parágrafos inteiros.

## Fundos

| Token | Hex | Uso |
|---|---|---|
| `--bg-white` | `#FFFFFF` | Cards, superfícies elevadas, conteúdo principal. |
| `--bg-light` | `#F7F7F7` | Fundo neutro da página, uso geral. |
| `--bg-subtle` | `#F8F9FA` | Linhas alternadas de tabela (zebra), seções alternadas. |
| `--bg-peach` | `#FFE7E1` | Fundo neutro "de marca", ver acima. |

## Cores semânticas / estado

| Token | Hex | Uso |
|---|---|---|
| `--color-success` | `#10B981` | Verde de sucesso, status positivo. |
| `--color-highlight` | `#FFD700` | Amarelo de destaque, marcações pontuais. |

Não existe mais um "laranja suave" de estado (`--color-warm` foi removido
junto com o laranja de acento) — use `--accent-pink` com opacidade reduzida
se precisar de uma versão mais suave do acento pontual.

## Regra de proporção (uso de marca)

- **Roxo (`#613EFF`) = cor primária/assinatura.** Domina os elementos de identidade.
- **Rosa (`#F9006F`) = acento pontual.** ~10% da tela, só em CTA/destaque. **Não abusar.**
- **Magenta (`#EF41FF`)** é acento secundário — mais usado em gradientes e na rampa editorial do que como cor sólida isolada de UI.
- **Navy (`#0A005A`)** é para contraste máximo: títulos grandes, fundos escuros.
- **Fundos claros** (`#F7F7F7`, `#F8F9FA`, `#FFE7E1`, branco) para respiro e legibilidade.
- **Reddit Sans** (ou Open Sans no Canva gratuito) para texto corrido e logotipo; **Oswald** só para títulos/chamadas de impacto, sempre uppercase + bold.

## Roxo exato da logo vs. roxo da marca

| Token | Hex | Uso |
|---|---|---|
| `--primary-purple` | `#613EFF` | Roxo oficial do MIV. Use em produto, UI, dashboards, texto. |
| `--logo-purple` | `#613EFF` | Confirmado na nova exportação da logo (2026-09-16): `logomarca-*-default.svg` usa `fill="#613EFF"`, o mesmo do primário. Mantido como token separado só por compatibilidade com `print-cover.md`. |

## Rampa editorial — relatórios longos com capítulos (livro Gov Hub)

Progressão oficial de matiz do MIV: **azul-marinho → roxo → magenta → rosa →
pêssego claro.** Substitui a rampa "harmonizada"/aproximada da versão
anterior desta skill — estes valores agora são os hexadecimais exatos do
manual, não uma aproximação. Use esta rampa **somente em relatórios/
frameworks longos e com capítulos** (como o Briefing, o guia de integração,
ou qualquer PDF no estilo "00 Introdução, 01 Artefato, 02 Artefato..."). Para
telas de produto/UI, siga sempre o roxo como cor única de assinatura.

| Token | Hex (oficial) | Uso |
|---|---|---|
| `--editorial-00-navy` | `#0A005A` | Capa/numeral do capítulo 00 (abertura, introdução) |
| `--editorial-01-purple` | `#613EFF` | Capa/numeral do capítulo 01 |
| `--editorial-02-magenta` | `#EF41FF` | Capa/numeral do capítulo 02 |
| `--editorial-03-pink` | `#F9006F` | Capa/numeral do capítulo 03 |
| `--editorial-04-peach` | `#FFE7E1` | Capa/numeral do capítulo 04 (fechamento) — **atenção:** é uma cor clara, então o numeral/título ficam em `--dark-navy`, não em branco (ver acessibilidade). |

**Como aplicar a progressão:**
- Página de capa do documento: fundo sólido `--dark-navy` ou gradiente
  `--primary-purple` → `--dark-navy`, com um elemento gráfico (círculos/
  semicírculos, ver `component-recipes.md`) em `--accent-magenta` ou
  `--accent-pink` cruzando o fundo.
- Cada capítulo/seção numerada ganha sua cor da rampa, em ordem, ciclando de
  volta ao navy se houver mais de 5 capítulos.
- Sobre o fundo colorido da capa de capítulo, sobreponha uma grade sutil
  (`--editorial-grid-line`) e 1–2 círculos/semicírculos translúcidos
  (`--editorial-ring`) como textura decorativa — nunca ilustrações
  figurativas (ver "Padronagem e elementos gráficos" em `component-recipes.md`).
- O número do capítulo e o título ficam em branco, bold, sobre fundo escuro
  (navy, roxo, magenta, pink) — e em `--dark-navy` sobre o capítulo peach
  (`#FFE7E1`), que é claro demais para texto branco.
- Dentro do corpo do capítulo (fundo branco), a cor do capítulo pode ser
  usada como acento local: título de seção, ícone do callout, barra lateral
  — mantendo o roxo como cor dominante do restante do documento (títulos
  gerais, tabelas, badges).

## Elementos gráficos e padronagem

Ver seção dedicada em `component-recipes.md`. O MIV descreve os elementos
de apoio como "círculos, semicírculos e retângulos arredondados", e as
páginas de exemplo do manual mostram esse repertório na prática: **círculo
cheio, anel/círculo vazado (donut), semicírculo, quarto de círculo
(quarter-pie) e retângulo em formato pílula** — todas variações derivadas
das 3 formas-base. Podem aparecer como blocos sólidos grandes competindo na
composição (capa, post) ou como textura pequena/translúcida atrás de
conteúdo — nunca como ilustração figurativa.

## Acessibilidade (contraste)

- Texto **branco** (`#FFFFFF`) sobre `--primary-purple` (`#613EFF`): **OK**.
- Texto **branco** sobre `--dark-navy` (`#0A005A`): **OK**, contraste alto.
- Texto **branco** sobre `--accent-pink` (`#F9006F`): use `font-weight >= 600`
  para reforçar.
- Texto **branco sobre `--accent-magenta`** (`#EF41FF`): **evite** em texto
  pequeno — o magenta é claro demais para garantir contraste AA com branco;
  prefira `--dark-navy` como texto sobre magenta, ou reserve o magenta para
  áreas grandes/decorativas sem texto em cima.
- Texto **branco sobre `--bg-peach`** (`#FFE7E1`): **nunca** — é uma cor quase
  branca. Use sempre `--dark-navy` ou `--text-strong` sobre peach.
- Texto **roxo sobre fundo branco**: para textos pequenos, use o roxo mais
  escuro `--purple-700` (`#3F28A6`) em vez de `#613EFF` para garantir
  contraste AA.
- Nunca coloque `--text-muted` (`#666666`) sobre fundos coloridos escuros.

## Aplicação da marca (regra do MIV)

Sempre que possível, use a marca dentro da paleta oficial acima, preservando
contraste e proporções originais. Quando isso não for viável:
- Fundo escuro → logo/elementos em **branco**.
- Fundo claro → logo/elementos em **preto** (ou `--dark-navy`).

## Usos indevidos (do MIV — vale para a logo, mas a lógica se estende a
qualquer elemento de marca)

Nunca: distorcer/esticar proporções, girar o elemento fora do eixo,
adicionar contorno/stroke não previsto, aplicar sombra/efeito 3D/glow, ou
recolorir fora da paleta oficial (ex: gradiente não documentado, cor
sólida diferente das listadas acima).
