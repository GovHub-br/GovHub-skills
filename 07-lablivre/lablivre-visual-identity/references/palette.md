# Paleta Lab Livre — referência e quando usar cada cor

Valores extraídos diretamente do Manual de Identidade Visual (MIV) oficial
do Lab Livre. Use exatamente estes hexadecimais. Os nomes de token estão em
inglês e são **os mesmos da skill do Gov Hub** (ver `tokens.css`): esta
skill é uma cópia daquela com a paleta trocada, e manter os nomes deixa o
código das referências válido nas duas marcas. Tradução dos nomes usados
nos textos: "navy" = azul profundo, "magenta" = rosa-choque, "rosa"/"pink"
= laranja, "pêssego"/"peach" = rosa claro.

As cinco cores formam uma **rampa do frio para o quente**: azul profundo →
roxo → rosa-choque → laranja, com o rosa claro como fundo de apoio.

## Cores primárias da marca

| Token | Hex | Uso |
|---|---|---|
| `--primary-purple` | `#7023E8` | **Roxo, cor-assinatura.** A mais usada no ícone da folha e em destaques: títulos de destaque, cabeçalhos de tabela em web, botões primários, links, badges, barras de topo. |
| `--dark-navy` | `#080056` | **Azul profundo, cor-base.** Texto escuro, títulos grandes, fundo institucional sério, alto contraste. É também o azul da logo `lab-livre-blue.svg`. |
| `--accent-magenta` | `#E52E70` | **Rosa-choque.** Acento vibrante, transições de gradiente, rampa editorial. |
| `--accent-pink` | `#F46B2F` | **Laranja, acento quente / CTA.** Call-to-action, destaque de número-chave, contraponto ao roxo/azul. Com parcimônia (regra 90/10). |
| `--bg-peach` | `#FFE7E1` | **Rosa claro.** Fundo claro, respiro, base para cards e telas. Nunca como cor de destaque. |
| `--text-white` | `#FFFFFF` | Texto sobre superfícies roxas ou azul profundo. |

## Estados derivados do primário

| Token | Hex | Uso |
|---|---|---|
| `--purple-600` | `#5F1EC5` | **Hover/foco** de elementos roxos (botão primário, link). Aproximado por escurecimento — não vem do MIV, ajuste se o design confirmar um valor exato. |
| `--purple-700` | `#4A17A0` | **Active/pressionado**, e roxo para texto sobre fundo branco quando precisar de contraste extra. |

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

- **Roxo (`#7023E8`) = cor primária/assinatura.** Domina os elementos de identidade.
- **Laranja (`#F46B2F`) = acento quente pontual.** ~10% da tela, só em CTA/destaque. **Não abusar.**
- **Rosa-choque (`#E52E70`)** é acento secundário — mais usado em gradientes e na rampa editorial do que como cor sólida isolada de UI.
- **Azul profundo (`#080056`)** é a cor-base: texto escuro, títulos grandes, fundos escuros.
- **Gradientes** seguem a ordem da rampa, do frio para o quente: `linear-gradient(135deg, #7023E8, #E52E70)` ou `linear-gradient(135deg, #080056, #7023E8, #E52E70, #F46B2F)`.
- **Fundos claros** (`#F7F7F7`, `#F8F9FA`, `#FFE7E1`, branco) para respiro e legibilidade.
- **Reddit Sans** (ou Open Sans no Canva gratuito) para texto corrido e logotipo; **Oswald** só para títulos/chamadas de impacto, sempre uppercase + bold.

## Roxo exato da logo vs. roxo da marca

| Token | Hex | Uso |
|---|---|---|
| `--primary-purple` | `#7023E8` | Roxo oficial do MIV. Use em produto, UI, dashboards, texto. |
| `--logo-purple` | `#7023E8` | Cor preferencial de aplicação da marca segundo o MIV, igual ao primário. Mantido como token separado só por compatibilidade com o código herdado do Gov Hub. Ainda não há SVG da logo em roxo (ver `partners.md`). |

## Rampa editorial — relatórios longos com capítulos (livro Lab Livre)

Progressão oficial de matiz do MIV: **azul-marinho → roxo → magenta → rosa →
pêssego claro.** Estes valores são os hexadecimais exatos do manual. Use
esta rampa **somente em relatórios/frameworks longos e com capítulos**
(como o Briefing, o guia de integração, ou qualquer PDF no estilo "01
Introdução, 02 Metodologia..."). Para telas de produto/UI, siga sempre o
roxo como cor única de assinatura.

| Token | Hex (oficial) | Uso |
|---|---|---|
| `--editorial-00-navy` | `#080056` | Cor de seção (tabela, callout) em PDF, em todos os capítulos |
| `--editorial-01-purple` | `#7023E8` | Em PDF: título do capítulo (`.gh-band__title`); não é mais cor de seção |
| `--editorial-02-magenta` | `#E52E70` | **Fora de texto e tabela em PDF** (ver abaixo). Só em elemento gráfico, slide ou post. |
| `--editorial-03-pink` | `#F46B2F` | **Fora de texto e tabela em PDF.** Só em elemento gráfico, slide ou post. |
| `--editorial-04-peach` | `#FFE7E1` | Fundo de forma/chip em PDF (pílula da capa, ver `print-cover.md`). Cor clara: qualquer texto por cima vai em `--dark-navy`. |

### Em PDF: navy nas tabelas, roxo só no título (decisões de 2026-09-17/18)

Na simulação do Relatório de Diagnóstico com a IDV nova, o usuário pediu
para **remover magenta e rosa dos textos e tabelas**; testou navy e roxo
alternando por capítulo e, no dia seguinte, fixou **navy em todas as
tabelas** ("sem intercalar entre os capítulos"). A partir daí, em
documento PDF:

- `--section-color` = `--editorial-00-navy` em todo capítulo. Ela pinta
  header e legenda de tabela e o contorno de callout (`print-table.md`,
  `editorial-report.md` seção 6).
- Hierarquia de títulos: **título do capítulo em roxo** (`.gh-band__title`,
  o único roxo da página de texto; testado e aprovado em 2026-09-18),
  numeral e eyebrow em navy, `h3` de seção em navy (eram roxos; "roubavam
  atenção do título da própria página"). Título do índice em `--logo-purple`.
- Capa branca, cabeçalho branco, rodapé com símbolo navy: o documento
  inteiro fica em navy + roxo + pêssego, com o roxo em poucos pontos
  (título de capítulo, quarto de círculo da capa, índice).
- Magenta e rosa continuam válidos nos **elementos gráficos** de slides e
  posts (`slides.md`, `social-posts.md`) e no CTA de produto
  (`--accent-pink`); só saíram do PDF impresso.

**Como aplicar a progressão (histórico, versão anterior a 2026-09-17):**
a faixa colorida full-bleed por capítulo, com a rampa completa navy →
roxo → magenta → rosa → pêssego, numeral branco a 72% e chip branco com
ícone, foi o padrão de agosto de 2026 e está substituída pelo cabeçalho
sóbrio. Não a reproduza em documento novo; se um documento antigo com a
faixa precisar de manutenção, mantenha-o consistente consigo mesmo.

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

- Texto **branco** (`#FFFFFF`) sobre `--primary-purple` (`#7023E8`): **OK**.
- Texto **branco** sobre `--dark-navy` (`#080056`): **OK**, contraste alto.
- Texto **branco sobre `--accent-pink`** (laranja `#F46B2F`): contraste
  ~3,0:1, **reprovado em texto pequeno**. Só em texto grande e bold (≥ 18pt
  ou ≥ 14pt bold); em botão/chip pequeno use `--dark-navy` sobre o laranja.
  É mais restritivo que o rosa do Gov Hub.
- Texto **branco sobre `--accent-magenta`** (rosa-choque `#E52E70`):
  contraste ~4,3:1, um pouco abaixo de AA para texto pequeno; prefira
  `--dark-navy` sobre ele, ou reserve o rosa-choque para áreas grandes/
  decorativas sem texto em cima.
- Texto **branco sobre `--bg-peach`** (`#FFE7E1`): **nunca** — é uma cor quase
  branca. Use sempre `--dark-navy` ou `--text-strong` sobre peach.
- Texto **roxo sobre fundo branco**: para textos pequenos, use o roxo mais
  escuro `--purple-700` (`#4A17A0`) em vez de `#7023E8` para garantir
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
