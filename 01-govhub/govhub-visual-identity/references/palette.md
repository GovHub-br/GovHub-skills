# Paleta GovHub — referência e quando usar cada cor

Valores extraídos diretamente do CSS de <https://gov-hub.io>. Use exatamente
estes hexadecimais. Os nomes de token estão em inglês (ver `tokens.css`).

## Cores primárias da marca

| Token | Hex | Uso |
|---|---|---|
| `--primary-purple` | `#7A34F3` | **Cor-assinatura.** Títulos de destaque, cabeçalhos de tabela, botões primários, links, badges, barras de topo, ícones de destaque. É o roxo que identifica a marca. |
| `--secondary-purple` | `#8B5CF6` | Roxo de apoio. Segunda parada de gradientes, hovers suaves, elementos secundários que ainda precisam de identidade roxa. |
| `--accent-orange` | `#F97316` | **Acento pontual.** Call-to-action, destaque de um número/metric-chave, tags de alerta positivo. Usar com parcimônia (regra 90/10). |
| `--accent-orange-hover` | `#EA580C` | Estado hover do laranja. |
| `--text-white` | `#FFFFFF` | Texto sobre superfícies roxas ou laranjas. |

## Roxos de apoio e estados

| Token | Hex | Uso |
|---|---|---|
| `--purple-400` | `#9249CA` | Roxo médio para gradientes e detalhes. |
| `--purple-600` | `#7C3AAD` | **Hover/foco** de elementos roxos (botão primário, link). |
| `--purple-700` | `#5B21B6` | **Active/pressionado**, e roxo para texto sobre fundo branco quando precisar de contraste extra (ver acessibilidade). |

## Neutros e texto

| Token | Hex | Uso |
|---|---|---|
| `--text-strong` | `#202020` | Títulos e texto forte. |
| `--text-body` | `#2D3748` | Corpo de texto padrão. |
| `--text-muted` | `#666666` | Legendas, texto secundário, metadados. |

## Fundos

| Token | Hex | Uso |
|---|---|---|
| `--bg-white` | `#FFFFFF` | Cards, superfícies elevadas, conteúdo principal. |
| `--bg-light` | `#F7F7F7` | Fundo neutro da página. |
| `--bg-subtle` | `#F8F9FA` | Linhas alternadas de tabela (zebra), seções alternadas. |

## Cores semânticas / estado

| Token | Hex | Uso |
|---|---|---|
| `--color-success` | `#10B981` | Verde de sucesso, status positivo. |
| `--color-highlight` | `#FFD700` | Amarelo de destaque, marcações pontuais. |
| `--color-warm` | `#F19F42` | Laranja suave, destaque secundário mais calmo que `--accent-orange`. |

## Regra de proporção (uso de marca)

- **Roxo (`#7A34F3`) = cor primária/assinatura.** Domina os elementos de identidade.
- **Laranja (`#F97316`) = acento pontual.** ~10% da tela, só em CTA/destaque. **Não abusar.**
- **Fundos claros neutros** (`#F7F7F7`, `#F8F9FA`, branco) para respiro e legibilidade.
- **Inter** como fonte em tudo.

## Roxo exato da logo vs. roxo do site

| Token | Hex | Uso |
|---|---|---|
| `--primary-purple` | `#7A34F3` | Roxo do CSS do site gov-hub.io. Use em produto, UI, dashboards. |
| `--logo-purple` | `#7521F9` | Extraído do arquivo SVG oficial da logo (`fill="#7521F9"` nos paths). Ligeiramente mais escuro/azulado que `--primary-purple`. Use **especificamente** quando a logo aparecer sobre um fundo sólido (ex: capa de relatório) e o fundo precisar bater exatamente com a cor do arquivo da logo — a diferença é sutil mas visível lado a lado. |

## Rampa editorial — relatórios longos com capítulos (livro GovHub)

Extraída de *Gov Hub: um guia prático para integração e qualificação de dados
públicos* (UnB/Ipea/Lab Livre, 2025). O livro usa uma **progressão de matiz**
para diferenciar capítulos visualmente — cada capítulo tem sua cor sólida de
capa — em vez do roxo+laranja único do site. Use esta rampa **somente em
relatórios/frameworks longos e com capítulos** (como o Briefing, o guia de
integração, ou qualquer PDF no estilo "00 Introdução, 01 Artefato, 02
Artefato..."). Para telas de produto/UI, siga sempre roxo+laranja.

| Token | Hex (aprox.) | Uso |
|---|---|---|
| `--editorial-01-purple` | `#5B21B6` | Capa/numeral do capítulo 00 ou 01 (abertura, introdução) |
| `--editorial-02-magenta` | `#9520B6` | Capa/numeral do capítulo 02 |
| `--editorial-03-pink` | `#C520A4` | Capa/numeral do capítulo 03 |
| `--editorial-04-coral` | `#E8776F` | Capa/numeral do capítulo 04 (fechamento/solução) |

**Como aplicar a progressão:**
- Página de capa do documento: gradiente `--primary-purple` → `--purple-700`, com uma
  faixa/onda decorativa em laranja e no rosa "Lab Livre" (`--editorial-04-coral`)
  cruzando o fundo (ver `component-recipes.md`).
- Cada capítulo/seção numerada ganha sua cor da rampa, em ordem, ciclando de
  volta ao roxo se houver mais de 4 capítulos.
- Sobre o fundo colorido da capa de capítulo, sobreponha uma grade sutil
  (`--editorial-grid-line`) e 1–2 círculos/anéis translúcidos
  (`--editorial-ring`) como textura decorativa — nunca ilustrações figurativas.
- O número do capítulo e o título ficam sempre em branco, bold, sobre a cor sólida.
- Dentro do corpo do capítulo (fundo branco), a cor do capítulo pode ser usada
  como acento local: título de seção, ícone do callout, barra lateral —
  mantendo o roxo como cor dominante do restante do documento (títulos gerais,
  tabelas, badges).

Essas cores foram harmonizadas por rotação de matiz a partir de
`--primary-purple`, não amostradas pixel a pixel do PDF. Se for necessário
fidelidade exata (ex: material impresso oficial), confirme os hexadecimais no
Figma da marca antes de publicar.

## Acessibilidade (contraste)

- Texto **branco** (`#FFFFFF`) sobre `--primary-purple` (`#7A34F3`): **OK** (contraste suficiente).
- Texto **branco** sobre `--accent-orange` (`#F97316`): use `font-weight >= 600` para reforçar; prefira texto escuro em áreas grandes de laranja claro.
- Texto **roxo sobre fundo branco**: para textos pequenos, use o roxo mais escuro
  `--purple-700` (`#5B21B6`) em vez de `#7A34F3` para garantir contraste AA.
- Nunca coloque `--text-muted` (`#666666`) sobre fundos coloridos escuros.
