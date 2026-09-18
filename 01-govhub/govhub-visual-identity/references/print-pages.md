# Arquitetura de página para PDF — capítulo, página fixa sem margem

Validado na prática (agosto de 2026) num documento de teste de 3 páginas,
revisado e aprovado pelo usuário. Esta é a técnica correta para gerar PDF a
partir de HTML impresso via Chrome headless (`--print-to-pdf` ou
`Page.printToPDF`) sempre que o documento tiver **capa com formas
sangrando pelas bordas + cabeçalho de capítulo + rodapé repetido em toda
página**. Não é a técnica do `editorial-report.md` original (que usava
margem de página + margem negativa para sangrar a faixa) — aquela abordagem
tem um bug real do Chrome, documentado abaixo. Use sempre esta versão.
Desde 2026-09-17 o cabeçalho de capítulo é branco (não sangra mais), mas a
capa continua sangrando as formas, e a arquitetura é a mesma.

## Regra: a dificuldade de paginar o corpo NÃO é motivo para simplificar capa/cabeçalho

A capa (`print-cover.md`) e o cabeçalho de capítulo (`print-header.md`) são
páginas de conteúdo curto e conhecido de antemão — sempre cabem numa única
`.gh-page` full-bleed, sem exceção nenhuma. A dificuldade real está em
paginar um **corpo** longo que flui por muitas páginas (ver "Conteúdo que
flui em muitas páginas" abaixo) — isso é um problema totalmente
independente e não justifica tocar na capa ou na faixa.

**Já aconteceu**: montando o PDF de um dicionário de dados (28 tabelas,
corpo com dezenas de páginas), o agente leu a limitação de paginação do
corpo e, por analogia/receio de complexidade, decidiu simplificar TAMBÉM a
capa e o cabeçalho — trocou o fundo sólido full-bleed por um cartão roxo
com margem branca ao redor da página, e a faixa de capítulo por um card
arredondado dentro da margem, sem nunca ter tentado a versão full-bleed
para essas duas peças. O resultado não seguia mais o idv, e o usuário só
percebeu depois de já ter recebido o PDF.

**Regra**: capa e faixa de capítulo usam o código exato de `print-cover.md`
e `print-header.md`, sempre — mesmo quando o corpo do documento é longo,
tem conteúdo dinâmico, ou parece complicado demais para paginar com
precisão. Se depois de tentar isso realmente não for possível, pare e
pergunte ao usuário antes de simplificar — não decida sozinho que "mais
simples" é aceitável só porque outra parte do documento é trabalhosa.

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
- o cabeçalho de capítulo: `position:absolute; top:0; left:20mm; right:20mm;` — veja
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

## Conteúdo que flui em muitas páginas: paginação por medição (validado)

Escrever uma `.gh-page` por página à mão só funciona quando o autor sabe de
antemão quantas páginas físicas existem — bom para frameworks/relatórios
curtos (ex: o Framework de Briefing, ~10-15 páginas). Para um documento
onde o conteúdo é gerado dinamicamente e não dá pra saber de antemão onde
cada página termina (ex: um dicionário de dados com dezenas de tabelas e
diagramas de tamanho variável), pagine por **medição real de altura**, não
por estimativa manual. Validado em produção (agosto de 2026, relatório de
21 páginas com diagramas mermaid de altura variável, capa e faixas de
capítulo full-bleed em todas as páginas, sem overflow nem folga grande):

1. Quebre o conteúdo do corpo em **blocos atômicos** (uma tabela, um
   diagrama, uma nota — nunca algo que não possa ser cortado no meio) mais
   um **cabeçalho** (`.gh-band`, ver `print-header.md`) por capítulo.
2. Num navegador headless (Puppeteer/Playwright), depois que qualquer
   conteúdo assíncrono (ex: diagramas mermaid) já tiver renderizado, crie um
   container escondido `position:absolute; width:170mm` (a largura útil do
   corpo — 210mm menos as margens de 20mm de cada lado de `print-header.md`)
   e, para cada bloco, jogue o HTML dele lá dentro e leia `scrollHeight`.
   Meça o cabeçalho de cada capítulo do mesmo jeito, a `170mm` (ele é
   alinhado às margens, como o corpo).
3. Empacote os blocos em páginas com um algoritmo guloso: a primeira página
   de um capítulo tem orçamento vertical `297mm − (altura_do_cabeçalho + 12mm) − 32mm`
   (12mm de respiro após a barra, 32mm reservados pro rodapé); páginas de
   continuação (sem cabeçalho) têm
   `297mm − 20mm − 32mm`. Assim que um bloco não cabe no orçamento restante,
   feche a página atual e abra uma nova sem cabeçalho. Subtraia uma margem de
   segurança do orçamento pra absorver diferenças de arredondamento entre a
   medição e a renderização final — **use pelo menos ~20mm, não ~4mm**: em
   produção, blocos empilhados como siblings reais (margem entre um bloco e
   o próximo) mediram consistentemente alguns mm mais altos no PDF final do
   que a soma das alturas medidas isoladamente, mesmo com o container de
   medição em `position:absolute` (que já cria BFC) — a causa exata não foi
   isolada, mas o sintoma é sempre no mesmo sentido (final mais alto que a
   medição, nunca o contrário), então uma margem de segurança generosa é a
   mitigação certa: overflow (conteúdo cortado) é o erro pior que espaço
   sobrando, então errar para o lado de "mais folga" é a escolha segura.
4. Blocos minúsculos (< ~40mm — legendas, cadeia de hierarquia, um `<h3>` de
   seção) ficam órfãos com facilidade no fim de uma página, separados do
   conteúdo que os segue. Antes de empacotar, funda cada bloco minúsculo com
   o **próximo** bloco da lista (concatene o HTML, some as alturas).
5. Gere o HTML final já com os blocos posicionados por página (uma
   `.gh-page` por página calculada) e imprima normalmente. Como cada bloco
   foi medido na mesma largura/fonte/CSS em que será renderizado no final, a
   medição bate com o resultado real — mas confira mesmo assim (ver
   "Revisão obrigatória" acima; ela continua obrigatória mesmo com
   paginação por medição).
6. **Numere as páginas e o índice no mesmo passo.** O gerador é quem sabe
   quantas páginas físicas existem, então é ele que preenche o
   `.gh-footer__page` de cada rodapé (`print-footer.md`) e a coluna `.page`
   do índice (`print-frontmatter.md`), nunca um número digitado à mão:

   ```js
   // pages: array de {html, chapter?} na ordem final; a capa é pages[0]
   pages.forEach((pg, i) => { pg.number = i + 1; });          // capa = 1
   const tocEntries = chapters.map(ch => ({
     num: ch.num, label: ch.title,
     page: pages.find(pg => pg.chapter === ch.num).number,    // 1ª página do capítulo
   }));
   const footer = (pg) => pg.isCover ? '' : `
     <div class="gh-footer-bar"></div>
     <div class="gh-footer">
       <span class="gh-footer__text"><span class="gh-footer__page">${pg.number}</span>${docShort} &middot; ${projectShort} &middot; Gov Hub &middot; Lab Livre - UnB</span>
       <img class="gh-footer__logo" alt="" src="logo/icone-none-navy.svg">
     </div>`;
   ```

   Ordem de montagem: capa, front matter (se houver), capítulos. O índice
   é o único bloco que depende do resultado da paginação, então gere o HTML
   dele **depois** de empacotar os capítulos; a página do índice em si tem
   posição fixa (3, logo após a folha de identificação), e o front matter
   ocupa sempre 2 páginas, então não altera a contagem dos capítulos de
   forma imprevisível. Se o documento não tem front matter, o capítulo 01
   começa na página 2.

**Pegadinha: bloco/faixa com `<img>` (ícone) mede menor do que o real se
você não esperar a imagem carregar.** Ao jogar o HTML de um bloco dentro
do container escondido de medição, `holder.scrollHeight` é lido de forma
síncrona logo depois de `holder.innerHTML = html` — mas uma `<img>` (chip
de ícone na faixa, ícone dos callouts) ainda não tem altura intrínseca
nesse instante, porque o carregamento do arquivo (mesmo local, `file://`)
não é síncrono com a atribuição do HTML. O resultado: a faixa/bloco é
medido mais baixo do que vai ficar de verdade assim que a imagem terminar
de carregar no HTML final — e esse déficit não aparece na medição, só no
PDF já gerado, como uma linha de tabela cortada no fim de uma página que
"deveria" ter cabido. Já aconteceu: um capítulo com chip de ícone na faixa
mediu ~alguns pixels a menos que o real, e a última linha da tabela
seguinte saiu cortada pelo `overflow:hidden` do `.gh-page-body`. Antes de
ler `scrollHeight`, espere toda `<img>` dentro do container de medição
terminar de carregar:

```js
const waitImages = (holder) => Promise.all(
  Array.from(holder.querySelectorAll('img')).map((img) =>
    img.complete ? Promise.resolve() : new Promise((res) => { img.onload = res; img.onerror = res; })
  )
);
// depois de holder.innerHTML = html, antes de ler holder.scrollHeight:
await waitImages(holder);
```

Diagramas mermaid que não cabem numa página inteira sozinhos (ex: um ER
diagram com muitas entidades em layout vertical) não têm solução de
paginação — a correção é no diagrama, não na página: use `direction LR`
para cadeias hierárquicas longas (transforma uma cadeia alta e estreita numa
faixa larga e baixa, que cabe do lado da faixa de capítulo em vez de
estourar a página sozinha) — só funciona a partir do **mermaid v11**; a v10
ignora a diretiva e pior, a interpreta como um node literal chamado
"direction"/"LR" no diagrama. Diagramas com grafo complexo (várias tabelas
centrais, não uma cadeia linear) devem ser quebrados em 2-3 diagramas
menores por sub-relação em vez de um único diagrama gigante.

## Caminho dos assets (logo e ícones)

**Logos:** copie a pasta `references/logo/` desta skill para **dentro da
pasta do projeto onde o HTML do documento vai morar**, como `logo/` irmã do
arquivo HTML — não recrie os SVGs. Os `src=` de logo nos exemplos deste
arquivo e de `print-cover.md`/`print-header.md`/`print-footer.md`
(ex: `logo/logomarca-horizontal-white.svg`) já assumem essa cópia local, relativa ao HTML.

**Ícones:** não são copiados — os `src=` nos exemplos apontam direto para a
CDN (`https://cdn.jsdelivr.net/gh/GovHub-br/skills-assets@main/icons/...`).
Ver [`icons-catalog.md`](icons-catalog.md) para a lista de nomes e, se o
ambiente de geração do PDF não tiver internet, o comando para baixar a pasta
`icons/` local e trocar os `src=` para caminho relativo.

## Referências

- [`print-cover.md`](print-cover.md) — código exato da capa.
- [`print-header.md`](print-header.md) — código exato do cabeçalho de capítulo (branco, navy, barra abaixo).
- [`print-footer.md`](print-footer.md) — código exato do rodapé.
- [`print-table.md`](print-table.md) — código exato de tabela de dados (legenda + header sólido na cor da seção, sem cartão ao redor).
- [`print-frontmatter.md`](print-frontmatter.md) — folha de identificação + índice, só em relatório de entrega de produto (pergunte antes).
