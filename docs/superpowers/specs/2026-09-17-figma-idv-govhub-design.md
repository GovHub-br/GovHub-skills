# Organizar a identidade visual Gov Hub no Figma (template modelo-idv)

Arquivo: `figma.com/design/1dMR0VyyTRmAYyPHi2HKsn` (páginas `modelo-idv`,
`idv-gov-hub`, `logo-gov-hub`, `logo-lab-livre`, `icons`).

## Objetivo

Preencher o template "Criação de Identidade Visual v2.0" (página
`modelo-idv`) com o conteúdo real do MIV Gov Hub e criar os tokens
(variáveis + estilos) do arquivo, com os cards do template já ligados às
variáveis. Opção A: preencher **no lugar**, sem reestruturar o template.

## Fonte da verdade

- Paleta MIV: `#0A005A` navy, `#613EFF` roxo, `#EF41FF` magenta, `#F9006F`
  rosa, `#FFE7E1` pêssego, mais preto `#000000` e branco `#FFFFFF`.
- Tipografia: Reddit Sans (principal; Open Sans no Canva gratuito) + Oswald
  (apoio, títulos em caixa alta, Bold). Texto oficial do MIV vai como
  subtítulo da seção Tipografia. No Figma, Reddit Sans vai até
  **ExtraBold** (não há Black): o card do logotipo usa ExtraBold com nota
  "Black no MIV".
- Elementos gráficos e padronagem: texto oficial do MIV vai como subtítulo
  da seção Estilo. Vetores já estão em `idv-gov-hub` (6 templates de slide,
  `elementos-graficos`, `outros-elementos-graficos`).
- Ícones: component set `icon` (`name × background`) na página `icons`.
- Logos: componentes em `logo-gov-hub`; Lab Livre/UnB em `logo-lab-livre`.
- Demais tokens (estados, neutros, sombras, raios): `references/tokens.css`
  da skill `govhub-visual-identity`.

Nada é baixado de CDN: tudo vem de instâncias/clones do próprio arquivo.

## 1. Tokens

Coleção de variáveis `Gov Hub`, um modo (`Default`). Escopos explícitos.

| Grupo | Variáveis | Escopo |
|---|---|---|
| `brand/` | `navy`, `purple`, `magenta`, `pink`, `peach`, `black`, `white` | FRAME_FILL, SHAPE_FILL, TEXT_FILL, STROKE_COLOR |
| `state/` | `purple-600 #5235D9`, `purple-700 #3F28A6` | FRAME_FILL, SHAPE_FILL, TEXT_FILL |
| `text/` | `strong #202020`, `body #2D3748`, `muted #666666` | TEXT_FILL |
| `bg/` | `light #F7F7F7`, `subtle #F8F9FA` | FRAME_FILL |
| `status/` | `success #10B981`, `highlight #FFD700` | FRAME_FILL, SHAPE_FILL, TEXT_FILL |
| `radius/` (float) | `sm 6`, `md 10`, `lg 16` | CORNER_RADIUS |

Estilos de texto (nomes = escala da seção Documentação):

| Estilo | Fonte | Tamanho/entrelinha | Extra |
|---|---|---|---|
| `Gov Hub/H1 Display` | Oswald Bold | 144 / 120 % | caixa alta |
| `Gov Hub/H2` | Reddit Sans ExtraBold | 72 / 120 % | |
| `Gov Hub/H3` | Reddit Sans Bold | 36 / 120 % | |
| `Gov Hub/B1 Lead` | Reddit Sans Medium | 36 / 140 % | tagline/abertura |
| `Gov Hub/B2 Body` | Reddit Sans Regular | 24 / 150 % | texto corrido |
| `Gov Hub/C1 Caption` | Reddit Sans Regular | 16 / 150 % | |

Estilos de efeito: `Gov Hub/Shadow md|lg|xl` (drop shadow navy a 10/12/16 %,
y 2/4/8, blur 10/20/30).

## 2. Seções do template preenchidas

Cada card do template mantém sua estrutura; só o conteúdo muda. Swatches
(`Rectangle`) ficam **ligados à variável** correspondente.

### Id Visual / Cor (`2:4796`)
- Subtítulo: "Paleta oficial do MIV: roxo como assinatura, rosa como acento
  pontual, navy para contraste, magenta como acento secundário, pêssego
  como fundo claro de marca."
- **Qual é**: 7 cards (clonar os 3 existentes): navy, roxo, magenta, rosa,
  pêssego, preto, branco (o branco recebe stroke `#E5E5E5` para aparecer).
  Título = nome + hex; bullets = papel de cada cor (do `palette.md`).
- **Qual não é**: 3 cards: verde/amarelo como cor de marca (só status);
  laranja e roxo da versão anterior da marca; texto branco sobre pêssego ou
  magenta (contraste). Swatches nas cores erradas correspondentes.

### Id Visual / Tipografia (`2:4834`)
- Subtítulo = texto oficial do MIV sobre tipografia (3 parágrafos).
- Coluna 1 Reddit Sans: ExtraBold caixa alta ("logotipo, Black no MIV"),
  Medium ("tagline"), Regular ("texto corrido"), Bold ("destaques").
- Coluna 2 Oswald: Bold caixa alta ("títulos e chamadas de impacto"),
  SemiBold, Medium, Regular (marcados como "uso não recomendado pelo MIV").
- Coluna 3 Open Sans (substituta no Canva gratuito): Bold, SemiBold,
  Regular, Light.
- Cada card: título na própria fonte/peso; "Texto de exemplo." vira
  descrição de uso.

### Id Visual / Documentação (`2:4878`)
- **Cor**: 7 cards em 2 linhas (clonar linha): nome, hex, swatch ligado à
  variável.
- **Tipografia**: os 6 textos da escala recebem os estilos `Gov Hub/*`
  acima, texto "H1 Oswald Bold 144" etc.
- **Conceito do símbolo**: intocado (conceitual).
- **Grade de construção**: só a linha "Logo" (3 quadros) recebe instâncias
  de `icone/Default`, `logomarca vertical/Default`, `logomarca
  horizontal/Default`, ajustadas ao quadro. Os 3 quadros de grade ficam
  intocados (a grade oficial só existe no MIV).

### Id Visual / Iconografia (`2:4994`)
- Subtítulo: regra "cada ícone só sobre o fundo da própria variante".
- 3 linhas × 6 = uma linha por `background` (default, purple, orange) e
  seis nomes representativos: `document_check`, `governance`, `database`,
  `charts`, `pie_chart`, `workflow`. Instância escalada a 192 px; label =
  `name / background`.

### Id Visual / Estilo (`2:5056`)
- Subtítulo = texto oficial do MIV sobre padronagens e elementos gráficos.
- **Ilustração** (8 slots): as 8 formas oficiais desenhadas como vetores
  nativos (círculo, anel, semicírculo, quarto de círculo, pílula,
  semi-pílula, meio-anel, quarto de anel), preenchimento ligado às
  variáveis `brand/*` alternando roxo/navy/magenta/rosa; label = nome da
  forma.
- **Fotografia**: intocada.
- **Gráfico**: linha 1 (4 slots 336²) = `capa`, `capa-capitulo`,
  `capa-capitulo-alternativa`, `pagina-comum`; slot largo (1632×336) =
  `outros-elementos-graficos` como faixa (escala à largura, recorte na
  altura); linha 3 (3 slots 480×672) = `pagina-comum-com-enfase`,
  `encerramento`, `elementos-graficos`; linha 4 fica intocada. Vetores
  clonados de `idv-gov-hub` (via export SVG → `createNodeFromSvg` se o
  clone entre páginas falhar). Label = nome do template.

## 3. Fora do escopo

Propósito, Personalidade, Logo/Conceito, Logo/Rascunho, Intro, Final,
Fotografia, grades de construção, Conceito do símbolo. Não se cria página
nova nem se publica biblioteca.

## 4. Execução e verificação

Um `use_figma` por passo (≤ 10 operações), sempre retornando IDs. Fontes
carregadas antes de qualquer edição de texto. Após cada seção:
`get_screenshot` da seção para checar texto cortado, escala e cores. Ao
final: `get_variable_defs` para confirmar as bindings e uma varredura das
seções preenchidas por "Conceito." / "Fonte" / "Ícone" / "Gráfico" restantes.
