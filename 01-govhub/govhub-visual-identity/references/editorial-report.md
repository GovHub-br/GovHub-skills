# Estilo editorial GovHub — relatórios longos e frameworks numerados

Fonte: *Gov Hub: um guia prático para integração e qualificação de dados
públicos* (UnB/Ipea/Lab Livre, 2025) — o "livro" oficial do projeto — e um
ciclo de validação real feito com o Framework de Briefing (documento gerado
e refinado em conjunto com o usuário). Use este padrão quando o pedido for um
**relatório, e-book, ou framework em PDF com seções numeradas** (ex:
"framework de briefing", "guia prático", "como fazer X — tutorial +
framework"), inspirado no estilo de documentos como `data-privacy-framework.pdf`.
Para telas de produto, dashboards ou UI, use `component-recipes.md` e a
paleta roxo+laranja normal — não este arquivo.

Todos os componentes abaixo assumem que `tokens.css` (incluindo a rampa
`--editorial-*` e `--logo-purple`) já está carregado. Os assets de logo e
ícones oficiais usados nos exemplos estão em `references/logo/` e
`references/icons/` desta skill — copie-os para o projeto em vez de
recriar ícones do zero.

## 1. Logo — qual arquivo usar onde

`references/logo/` tem a logo em 3 orientações (`horizontal`, `vertical`,
`none` = só o símbolo circular) × 4 cores (`primary` roxo, `light` branco,
`dark`, `colourfull`). Regra prática:

| Contexto | Arquivo | Tamanho de referência |
|---|---|---|
| Capa, fundo colorido/escuro | `orientation=horizontal, colour=light.svg` (logotipo completo, branco) | ~64px de altura |
| Rodapé de página, fundo branco | `orientation=none, colour=primary.svg` (só o símbolo, roxo) | ~45px de altura |
| Rodapé sobre fundo colorido | `orientation=none, colour=light.svg` (símbolo branco) | ~45px de altura |

Os arquivos atuais já vêm com o *viewBox* ajustado rente ao desenho (sem
sobra de espaço em branco nas bordas) — é seguro colocar `height` direto no
CSS sem compensar padding interno. Se um dia a logo for reexportada do
Figma e voltar a ter espaçamento embutido no SVG (aconteceu uma vez: ~9–13%
da largura era espaço vazio), o sintoma é a logo parecer desalinhada/mais
para dentro do que o texto ao lado — nesse caso, ajuste o `viewBox` para o
bounding box real do desenho, não tente compensar só no CSS.

```html
<img src="logo/orientation=horizontal, colour=light.svg" alt="GovHub" style="height:64px; width:auto;">
```

Não escreva "GovHub" como texto ao lado da logo (ex. "· Lab Livre") a menos
que peçam explicitamente — a logo sozinha já é a marca; texto adicional colado
nela tende a ficar poluído.

## 2. Capa, cabeçalho de capítulo e rodapé — ver arquivos dedicados

Estes três componentes têm receita própria, com código exato validado e
pronto pra copiar, em arquivos separados (mudam pouco de um documento para
outro: só título/subtítulo na capa, só numeral/eyebrow/título/cor no
cabeçalho, só o nome do documento no rodapé):

- [`print-pages.md`](print-pages.md) — **leia primeiro**: a arquitetura de
  página (`.gh-page` fixa 210×297mm, `@page { margin: 0 }`) que capa,
  cabeçalho e rodapé pressupõem, e o motivo (um bug real de paginação do
  Chrome) de por que essa é a versão certa e não a de margem
  negativa/sangria que um relatório antigo desta skill usava.
- [`print-cover.md`](print-cover.md) — capa: fundo sólido `--logo-purple`,
  moldura fina, logo no fluxo (não solta num canto), título/subtítulo,
  rodapé pequeno da capa.
- [`print-header.md`](print-header.md) — cabeçalho de capítulo: faixa
  full-bleed com numeral (sempre começando em 01, não 00) + eyebrow +
  título, chip de ícone opcional.
- [`print-footer.md`](print-footer.md) — rodapé: repete em toda página de
  conteúdo, barra fina alinhada à margem do texto (não à borda física da
  página) + marca da GovHub.

**Página de visão geral/framework** (grid com um card por seção) usa a
mesma faixa full-bleed sólida no topo, com o texto "FRAMEWORK" como eyebrow
e o título + subtítulo da faixa — não um card ou banda com margem.

## 4. Escrita: sem travessão (—)

Convenção adotada após feedback direto: não usar travessão (—) no corpo do
texto de relatórios. Troque por dois-pontos, vírgula ou ponto-final,
dependendo do que ficar mais natural na frase:

- Frase explicativa → dois-pontos (`"...custa caro: descobre-se tarde..."`).
- Continuação leve → vírgula (`"...mapeados, antes de qualquer linha..."`).
- Duas ideias completas → ponto final, frase nova.

Hífens dentro de palavras compostas (`ator-chave`, `pré-requisito`)
continuam normais — a regra é só sobre o travessão longo usado como pausa.

## 5. Ícones de produto GovHub (não são os ícones de linha genéricos)

`references/icons/` traz os ícones oficiais reais do GovHub: ilustrações
"duotone" com contorno roxo (`#7A34F3`) e uma sombra/silhueta laranja
(`#F19F42`, igual a `--color-warm`) atrás, variante `background=Default`
(pensada para fundo branco). Use estes, não ícones de linha genéricos
desenhados à mão — o efeito de marca é bem mais forte.

A pasta tem 32 nomes de ícone, cada um também em `background=orange` e
`background=purple` (versões de fundo sólido colorido, para usar sobre
cartões/badges coloridos em vez do duotone). Abaixo está o mapeamento
curado para os callouts do Framework de Briefing — os demais nomes (acesso,
charts, chat_round, chat_square, code, contratos, courses, deploy,
download, eye_dropper, figma, folder, github, ia, link, open-folder,
orcamento, paint_brush, server, teds) seguem o mesmo padrão de uso, escolha
pelo nome mais próximo do conteúdo.

Mapeamento usado no Framework de Briefing (adapte os nomes ao conteúdo real):

| Ícone | Uso sugerido |
|---|---|
| `workflow` | etapas/processo de uma política ou fluxo |
| `document_check` | marco legal, conformidade, aprovação |
| `pessoal` | atores, pessoas, stakeholders |
| `forum` | expectativas, alinhamento, discussão |
| `database` | fontes de dados, sistemas |
| `pie_chart` | objetivos, métricas, perguntas-guia |
| `settings` | hipóteses, ajustes, configuração |
| `governance` | encerramento, governança, síntese |
| `paper` | callout "o que é" |
| `notification` | callout "quando" |
| `tools` | callout "como" / dica prática |

**Tamanho dos ícones pequenos nos callouts:** a primeira tentativa (22px
dentro de um badge de 34px) ficou pequena demais segundo o usuário. Tamanho
validado: badge de 46px com ícone de 32px dentro.

```css
.gh-callout-box .gh-icon-badge { width: 46px; height: 46px; border-width: 1.4px; }
.gh-callout-box .gh-icon-badge img { width: 32px; height: 32px; }
```

## 6. Caixa de callout (outline, não preenchida)

Contorno fino colorido (na cor da seção) e fundo branco, ícone à esquerda,
título em uppercase pequeno, corpo de texto normal.

```html
<div class="gh-callout-box">
  <div class="gh-icon-badge"><img src="icons/name=paper, background=Default.svg" alt=""></div>
  <div>
    <div class="gh-callout-box__title">O que é</div>
    <div class="gh-callout-box__body">Texto explicativo do callout.</div>
  </div>
</div>
```

```css
.gh-callout-box {
  border: 1.4px solid var(--callout-color, var(--section-color, var(--primary-purple)));
  border-radius: var(--radius-md);
  padding: 14px 16px; display: flex; gap: 12px; align-items: flex-start;
  background: var(--bg-white);
}
.gh-callout-box__title { font-size: 8.5pt; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 700; color: var(--text-strong); margin-bottom: 4px; }
.gh-callout-box__body { font-size: 9.2pt; color: var(--text-body); margin: 0; }
```

Três callouts lado a lado (O que é / Quando / Como) usam
`display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px;` no
container pai.

## 7. Quando NÃO usar este estilo

- Dashboards, telas de app, e-mails, slides de reunião → use
  `component-recipes.md` (roxo+laranja, cards sólidos, tabela zebrada).
- Documentos de 1–3 páginas sem seções numeradas → a rampa editorial é
  exagero; um único acento roxo+laranja já resolve.
- Qualquer contexto onde a marca precisa ser reconhecida instantaneamente
  como "produto GovHub" (não como "publicação/relatório GovHub") → prefira
  roxo+laranja puro (`--primary-purple`, não `--logo-purple`).
