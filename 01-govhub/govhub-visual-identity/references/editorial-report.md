# Estilo editorial Gov Hub — relatórios longos e frameworks numerados

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
`--editorial-*` e `--logo-purple`) já está carregado. As **logos** usadas
nos exemplos estão em `references/logo/` desta skill — copie a pasta para o
projeto. Os **ícones** vêm por CDN (ver [`icons-catalog.md`](icons-catalog.md)),
não são arquivos locais.

## 1. Logo — qual arquivo usar onde

`references/logo/` tem a logo em 3 orientações (`horizontal`, `vertical`,
`none` = só o símbolo circular) × 4 cores (`primary` roxo, `light` branco,
`dark`, `colourfull`). Regra prática:

| Contexto | Arquivo | Tamanho de referência |
|---|---|---|
| Capa, fundo colorido/escuro | `horizontal-light.svg` (logotipo completo, branco) | ~64px de altura |
| Rodapé de página, fundo branco | `none-primary.svg` (só o símbolo, roxo) | ~45px de altura |
| Rodapé sobre fundo colorido | `none-light.svg` (símbolo branco) | ~45px de altura |

Os arquivos atuais já vêm com o *viewBox* ajustado rente ao desenho (sem
sobra de espaço em branco nas bordas) — é seguro colocar `height` direto no
CSS sem compensar padding interno. Se um dia a logo for reexportada do
Figma e voltar a ter espaçamento embutido no SVG (aconteceu uma vez: ~9–13%
da largura era espaço vazio), o sintoma é a logo parecer desalinhada/mais
para dentro do que o texto ao lado — nesse caso, ajuste o `viewBox` para o
bounding box real do desenho, não tente compensar só no CSS.

```html
<img src="logo/horizontal-light.svg" alt="Gov Hub" style="height:64px; width:auto;">
```

Não escreva "Gov Hub" como texto ao lado da logo (ex. "· Lab Livre") a menos
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
  página) + marca da Gov Hub.

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

## 5. Ícones de produto Gov Hub (não são os ícones de linha genéricos)

Os ícones oficiais reais do Gov Hub são ilustrações
"duotone" com contorno roxo e uma sombra/silhueta laranja atrás, variante
`default` (pensada para fundo branco). Use estes, não ícones de linha
genéricos desenhados à mão — o efeito de marca é bem mais forte.

> **Atenção — descompasso de paleta pendente:** a paleta oficial da marca
> mudou (ver `palette.md`: roxo agora é `#613EFF`, e o laranja foi
> descontinuado). O repositório externo de ícones (`GovHub-br/skills-assets`)
> ainda não foi regerado com as novas cores — os arquivos que chegam pelo CDN
> continuam desenhados no roxo/laranja antigos. Até a equipe de design
> regerar esse repositório: use a variante `-default.svg` (fundo branco) e
> `-purple.svg` (fundo roxo — o roxo antigo do ícone é próximo o bastante do
> novo `#613EFF` pra não destoar); **evite a variante `-orange.svg`**, já que
> não existe mais um fundo laranja oficial pra ela combinar.

Os SVGs **não ficam nesta skill** — são servidos por CDN a partir do repo
`GovHub-br/skills-assets`. Ver [`icons-catalog.md`](icons-catalog.md) para a
URL-base, o padrão de nome e a lista completa dos 332 nomes. Resumo:

```
https://cdn.jsdelivr.net/gh/GovHub-br/skills-assets@main/icons/<nome>-<variante>.svg
```

São 332 nomes de ícone, cada um em 3 variantes (`default`, `orange`, `purple`).
**Escolha pelo nome**: os nomes são descritivos do conceito (ex.:
`document-check`, `shield-check`, `chart-bar`, `folder-open`,
`user-group`), então procure na lista de `icons-catalog.md` o nome mais
próximo do conteúdo, em vez de depender de uma tabela fixa — a biblioteca é
grande demais pra manter um mapeamento exaustivo atualizado. Abaixo está o
mapeamento curado só para os callouts específicos do Framework de
Briefing (um caso de uso recorrente que já foi validado); pra qualquer
outro conteúdo, busque pelo nome.

**Consistência dentro do mesmo documento**: depois de escolher um ícone
para representar um conceito recorrente (ex.: "arquivo"), use o mesmo
nome em todas as ocorrências desse conceito no documento — não alterne
entre sinônimos próximos (`folder` num capítulo, `folder-open` noutro)
para a mesma ideia.

**Fundo permitido — até a atualização do repositório de ícones.** Os
ícones têm três variantes de arquivo, uma por fundo, desenhadas para a
paleta antiga:

| Fundo | Variante (sufixo na URL) | Status |
|---|---|---|
| Branco / claro | `-default.svg` (duotone roxo+laranja) | OK, usar |
| Roxo Gov Hub (`--primary-purple`, agora `#613EFF`) | `-purple.svg` | OK, usar — tom próximo o bastante do roxo antigo |
| ~~Laranja~~ | `-orange.svg` | **Evitar** — não existe mais fundo laranja oficial; sem substituto até o repo ser regerado |

Para **criar um ícone novo** que ainda não existe na biblioteca, esta skill
não cobre isso — use a skill separada `govhub-icon-creation`, dedicada à
técnica duotone exata (camadas, offset, cores por variante) e ao workflow
de construção no Figma.

Nunca coloque um ícone (nenhuma variante) sobre outra cor — inclusive as
cores da rampa editorial (navy, magenta, rosa, pêssego) ou o `--accent-pink`
(`#F9006F`, cor de CTA). Não existe arquivo desenhado para essas cores, e o
duotone/fundo sólido do ícone destoa visualmente quando forçado sobre uma
cor pra qual ele não foi feito. É por isso que o chip do ícone no
cabeçalho de capítulo (`gh-band__icon`, ver `print-header.md`) é sempre um
quadrado **branco**, mesmo quando a faixa atrás dele é magenta/rosa/coral —
o chip branco garante que o ícone sempre está sobre um dos três fundos
permitidos, não sobre a cor variável da faixa.

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

**Borda do badge (fundo branco):** todo ícone sobre fundo branco (badge de
callout, card, etc.) leva uma borda fina na cor da seção/callout — a mesma
cor e espessura da borda do card ao redor dele (`gh-callout-box`), pra dar
uma moldura consistente ao ícone em vez de deixá-lo solto no fundo branco.

```css
.gh-icon-badge {
  width: 46px; height: 46px;
  border: 1.4px solid var(--callout-color, var(--section-color, var(--primary-purple)));
  border-radius: var(--radius-sm);
  background: var(--bg-white);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.gh-icon-badge img { width: 32px; height: 32px; }
```

## 6. Caixa de callout (outline, não preenchida)

Contorno fino colorido (na cor da seção) e fundo branco, ícone à esquerda,
título em uppercase pequeno, corpo de texto normal.

```html
<div class="gh-callout-box">
  <div class="gh-icon-badge"><img src="https://cdn.jsdelivr.net/gh/GovHub-br/skills-assets@main/icons/paper-default.svg" alt=""></div>
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
  como "produto Gov Hub" (não como "publicação/relatório Gov Hub") → prefira
  roxo+laranja puro (`--primary-purple`, não `--logo-purple`).
