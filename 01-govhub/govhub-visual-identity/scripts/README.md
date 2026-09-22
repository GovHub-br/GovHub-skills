# build_doc.py — markdown longo → PDF A4 na identidade Gov Hub

Use **antes** de escrever CSS de PDF na mão. O script já traz a receita
validada das referências desta skill (`print-cover`, `print-header`,
`print-footer`, `print-table`, `print-pages`), então um documento novo não
exige reler nada disso nem reescrever o CSS.

```bash
# caminho curto
python3 scripts/build_doc.py --markdown doc.md --cover-title "Relatório" --project-short MIR

# documento de verdade, com capa, eyebrows e parceiros
cp scripts/exemplo-config.json meu-doc/documento.json   # edite
python3 scripts/build_doc.py --config meu-doc/documento.json
python3 scripts/build_doc.py --config meu-doc/documento.json --html-only
```

## O que o markdown precisa ter

Um capítulo por `## N. Título` (a numeração vira o numeral da faixa). O resto
é markdown comum: `###`/`####` viram subtítulos, tabelas GFM viram tabelas de
PDF com legenda numerada.

## O que o script faz sozinho

| Entrada no markdown | Saída no PDF |
| --- | --- |
| `## 3. Convênios` | faixa de capítulo: `03` + eyebrow + título roxo |
| tabela GFM | header navy, zebra, `Tabela N: <legenda>` inferida do título anterior |
| `\| # \| Coluna \| Descrição \|` | colunas com largura fixa (idem `# / Campo / Tipo / Descrição`) |
| `![alt](caminho.png)` sozinho num parágrafo | `<figure>` centrada, sem quebrar entre páginas |
| parágrafo iniciado por `**Limitações:**` | callout com contorno navy e badge navy com ícone (também `Atenção:`, `Ressalva:`, `Cuidado ao ler:`) |
| `## Sumário`, `# H1`, `**Versão:**` | removidos (a capa cumpre esse papel) |
| ` — ` no texto corrido | vira `:` ou vírgulas (convenção editorial; desligue com `dash_convention: false`) |

Título seguido de parágrafo/lista vira um bloco indivisível, para não sobrar
título órfão no fim da página.

## Peças que o markdown não expressa: HTML bruto + `extra_css`

Cards lado a lado, grids, qualquer composição da skill que não tenha sintaxe
em markdown: escreva o bloco como **HTML bruto dentro do `.md`** (o pipeline
deixa passar intacto) e ponha a receita de CSS num arquivo apontado por
`extra_css`. O script continua cuidando de página, rodapé e paginação.

```markdown
<div class="gh-cards">
  <div class="gh-card"><div class="gh-card__t">O que é</div><div>Texto.</div></div>
  <div class="gh-card"><div class="gh-card__t">Quando</div><div>Texto.</div></div>
</div>
```

```json
{ "extra_css": "cards.css" }
```

Pegue o CSS da receita em `../references/editorial-report.md` §6, não invente.
Use os tokens (`var(--section-color)`, `var(--bg-white)`) que o script já
define. Flexbox e grid funcionam: testado no WeasyPrint 70.

## Abertura: folha de identificação, índice

O que vem **antes do primeiro `## N.`** e leva `class="gh-front-page"` vira
página de abertura, entre a capa e o capítulo 01, já com o rodapé:

```markdown
<div class="gh-front-page">
  ... folha de identificação, receita em ../references/print-frontmatter.md ...
</div>

## 1. Primeiro capítulo
```

Sem essa classe, o bloco é descartado: título, descrição e badges no topo do
`.md` servem a quem lê o arquivo no GitHub, e a capa cumpre esse papel no PDF.
O build lista no terminal tudo o que ignorou, então a perda nunca é silenciosa.

## O que o script NÃO faz

Continua nas referências da skill, para montar à mão quando o documento pedir:

- marca d'água: `../references/print-watermark.md` (pergunte antes)
- slide, post, poster, dashboard: nada disso é A4

Para e-book ou framework numerado, gere o corpo aqui e acrescente as páginas
especiais depois.

**O callout baixa o ícone da CDN em tempo de build.** Sem rede, o WeasyPrint
avisa e o badge sai vazio (quadrado navy), o resto do PDF fica intacto. Para
build offline, baixe os ícones e aponte `icons_base` para a pasta:

```bash
curl -sL https://github.com/GovHub-br/skills-assets/archive/refs/heads/main.tar.gz \
  | tar xz --strip-components=2 skills-assets-main/gov-hub/icons
```

## Campos do config

Caminhos são relativos ao próprio JSON. Ver `exemplo-config.json`.

- `logo_dir` — `null` usa `references/logo/` da skill. O HTML sai com caminho
  relativo quando os logos estão dentro da pasta de saída, e `file://`
  absoluto quando não. **Para distribuir o HTML**, copie os logos ao lado da
  saída e aponte `logo_dir` para lá.
- `extra_css` — CSS do documento, como caminho de arquivo ou string. Anexado
  depois do CSS do script, então sobrescreve o que precisar.
- `callout_icons` — mapa `"rótulo:" -> nome-do-ícone` para acrescentar rótulos
  ou trocar o ícone de um deles (nomes em `../references/icons-catalog.md`).
  `icons_base` troca a CDN por uma pasta local; `icon_variant` troca a
  variante (`default` sobre o chip navy, `purple` sobre fundo claro).
- `partners` — ordem fixa Lab Livre → UnB → Ipea → ministério
  (ver `references/partners.md`, inclusive a regra do defeso eleitoral).
  Aceita `"arquivo.svg"` ou `{"file": "...", "alt": "Nome"}`; prefira a forma
  com `alt`.

## Depois de gerar

Rasterize o PDF e **olhe todas as páginas**, atrás dos dois erros opostos:
overflow silencioso e espaço desperdiçado. O procedimento está em
[`../references/print-pages.md`](../references/print-pages.md); nenhuma das
duas falhas se anuncia sozinha.

## Dependências

`markdown`, `beautifulsoup4`, `lxml`, `weasyprint`.

```bash
pip install markdown beautifulsoup4 lxml weasyprint
```
