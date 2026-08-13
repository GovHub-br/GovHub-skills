# Arquitetura de página para PDF — capítulo, página fixa sem margem

Validado na prática (agosto de 2026) num documento de teste de 3 páginas,
revisado e aprovado pelo usuário. Esta é a técnica correta para gerar PDF a
partir de HTML impresso via Chrome headless (`--print-to-pdf` ou
`Page.printToPDF`) sempre que o documento tiver **capa + cabeçalho de
capítulo em faixa colorida full-bleed + rodapé repetido em toda página**.
Não é a técnica do `editorial-report.md` original (que usava margem de
página + margem negativa para sangrar a faixa) — aquela abordagem tem um bug
real do Chrome, documentado abaixo. Use sempre esta versão.

## O problema que esta técnica resolve

A tentação óbvia é: dar um `@page { margin: 14mm }` para toda página (assim
o conteúdo normal já nasce com respiro), e usar `margin: -14mm` na faixa
colorida do cabeçalho para ela "sangrar" e cobrir essa margem, chegando até
a borda física da página. **Isso quebra no Chrome**: quando um elemento tem
margem negativa E está posicionado logo após uma quebra de página forçada
(`break-before`/`break-after: page`, de qualquer lado, elemento ou irmão),
o Chrome pinta um resíduo sólido da cor de fundo desse elemento no fim da
página ANTERIOR — uma barra fantasma, sem relação com o conteúdo real
daquela página. Testado e confirmado: o bug desaparece assim que a margem
negativa é removida, e não some só trocando qual elemento (o da faixa ou
seu irmão anterior) carrega a propriedade de quebra — é a combinação
margem-negativa + quebra-de-página em qualquer arranjo que causa o problema.

## A solução: sem margem de página nenhuma, cada página é uma caixa fixa

Em vez de deixar o navegador paginar automaticamente um documento HTML
fluido, cada página física vira uma `<div>` com tamanho A4 exato
(`210mm × 297mm`), `@page { margin: 0 }` global, e todo o conteúdo interno
(faixa, corpo, rodapé) posicionado com `position: absolute` relativo a essa
`<div>`. Como não existe margem de página nenhuma para sangrar, a faixa
colorida simplesmente **é** a largura da página — não precisa de nenhum
truque de margem negativa, e o bug não tem como acontecer.

```css
@page { size: A4; margin: 0; }

.gh-page {
  width: 210mm; height: 297mm;
  position: relative;
  overflow: hidden;              /* cada página é uma caixa fechada */
  page-break-after: always;
  break-after: page;
}
.gh-page:last-child { page-break-after: auto; break-after: auto; }
```

Cada página do documento é `<div class="gh-page">...</div>` em sequência no
`<body>`. Dentro dela, tudo é posicionado absolutamente:
- a faixa do cabeçalho: `position:absolute; top:0; left:0; right:0;` — veja
  [`print-header.md`](print-header.md);
- o rodapé: `position:absolute; ...; bottom:12mm;` — veja
  [`print-footer.md`](print-footer.md);
- a capa segue a mesma `.gh-page`, com seu próprio conteúdo — veja
  [`print-cover.md`](print-cover.md).

## Geração do PDF

Como todo o layout já é 100% determinístico (nenhuma margem/header/footer
via API), **não precisa** do Chrome DevTools Protocol nem de
`displayHeaderFooter`/`footerTemplate` — um `--print-to-pdf` de linha de
comando simples já basta:

```
chrome --headless=new --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="saida.pdf" "file:///caminho/para/documento.html"
```

## Revisão obrigatória depois de gerar o PDF: overflow silencioso e espaço desperdiçado

Como cada `.gh-page` tem altura fixa e `overflow: hidden`, **conteúdo que não
cabe simplesmente desaparece** — sem erro, sem aviso, sem quebra automática
para a página seguinte. A paginação é 100% manual (o autor decide onde cada
`.gh-page` termina), então os dois erros abaixo são inevitáveis se o PDF não
for conferido visualmente depois de gerado:

1. **Overflow (perda de conteúdo)**: uma estimativa otimista de quanto texto
   cabe numa página corta as últimas linhas/linhas de tabela sem deixar
   rastro. Já aconteceu numa tabela de 3 colunas com células de texto longo:
   a estimativa de altura por linha ficou baixa demais, e as últimas 7 das
   16 linhas sumiram silenciosamente.
2. **Espaço desperdiçado (quebras desnecessárias)**: o erro oposto e igual
   de comum — estimar pouco espaço disponível numa página (com medo do
   erro 1) deixa 200-500px de sobra em branco antes do rodapé, quando dava
   pra ter puxado o parágrafo/bloco seguinte pra cima. Isso aconteceu em
   várias páginas seguidas num relatório de ~30 páginas: capítulos que
   caberiam em 2 páginas ficaram espalhados em 3 porque a estimativa de
   altura de cada bloco de texto era conservadora demais.

**Procedimento obrigatório após gerar o PDF** (não pule esta etapa,
independente de quão confiante a estimativa de paginação pareça):

1. Rasterize **todas** as páginas do PDF gerado em PNG (ex: `pdftoppm -png
   -r 90 arquivo.pdf pagina` do Poppler) — não confie só no HTML fonte.
2. Abra cada imagem e confira, por página:
   - **Overflow**: alguma tabela, lista ou parágrafo termina exatamente na
     borda inferior da área de conteúdo (perto do `bottom` do
     `.gh-page-body`) de um jeito que parece cortado no meio de uma frase,
     linha de tabela ou item de lista? Se sim, é overflow — confira contra
     o HTML fonte quantos itens deveriam existir ali.
   - **Espaço sobrando**: existe uma folga grande e óbvia (bem mais que uma
     margem de respiro normal) entre o fim do conteúdo e a barra do
     rodapé? Se a página seguinte for uma continuação do mesmo capítulo
     (`.gh-page-body.no-band`, sem faixa nova), o início dela provavelmente
     cabe nessa folga.
3. Quando achar espaço sobrando entre duas páginas do mesmo capítulo, mova
   parágrafos/blocos inteiros da página seguinte para o fim da página com
   folga (nunca corte um parágrafo no meio). Prefira mover pouco e sobrar
   uma margem segura (100px+) a preencher exatamente até a borda.
4. Gere o PDF de novo e repita a conferência visual **completa** (todas as
   páginas, não só as que mudaram) — mover conteúdo de uma página pode
   fazer a página seguinte, antes cheia, ficar apertada ou até estourar.
5. Repita até não sobrar nem overflow nem folga grande evidente. Normalmente
   leva 2-3 rodadas num documento longo.

Não existe atalho confiável de calcular isso só de cabeça (contando
caracteres, estimando linhas) — a fonte, o `line-height`, a largura da
coluna e a presença de negrito/itálico mudam a altura real o suficiente
para a estimativa errar por uma margem grande. A rasterização + inspeção
visual é o único jeito confiável de saber com certeza.

## Limitação conhecida (ainda em aberto): conteúdo que flui

Esta técnica pressupõe que o autor sabe de antemão quantas páginas físicas
existem e escreve uma `.gh-page` por página. Isso funciona bem para
frameworks/relatórios curtos com paginação manual (como o Framework de
Briefing, ~10-15 páginas). Para um documento onde o conteúdo é gerado
dinamicamente e pagina sozinho (ex: um dicionário de dados com centenas de
linhas de tabela, onde não dá pra saber de antemão onde cada página
termina), ainda não temos uma receita validada que combine "página fixa sem
margem" com "conteúdo que flui e quebra sozinho". Duas direções possíveis a
explorar quando isso for necessário, nenhuma testada ainda neste projeto:
1. Gerar o PDF em duas passadas: uma primeira renderização mede onde as
   quebras de conteúdo fluido cairiam, e uma segunda monta as `.gh-page`
   manualmente com esses cortes.
2. Usar `Page.printToPDF` (CDP) só para o rodapé repetido (via
   `footerTemplate`) nas páginas de conteúdo fluido, mantendo margem real de
   página (não zero) nelas — aceitando que, nessas páginas específicas, o
   cabeçalho em faixa full-bleed não é usado (só a página de abertura de
   capítulo, que pode continuar sendo uma `.gh-page` fixa isolada).

## Caminho dos assets (logo e ícones)

Copie as pastas `references/logo/` e `references/icons/` desta skill para
**dentro da pasta do projeto onde o HTML do documento vai morar**, como
`logo/` e `icons/` irmãs do arquivo HTML — não recrie os SVGs, não referencie
o caminho original da skill a partir de outro projeto. Os `src=` usados nos
exemplos deste arquivo e de `print-cover.md`/`print-header.md`/`print-footer.md`
(ex: `logo/orientation=horizontal, colour=light.svg`) já assumem essa
cópia local, relativa ao HTML.

## Referências

- [`print-cover.md`](print-cover.md) — código exato da capa.
- [`print-header.md`](print-header.md) — código exato do cabeçalho de capítulo (faixa colorida).
- [`print-footer.md`](print-footer.md) — código exato do rodapé.
