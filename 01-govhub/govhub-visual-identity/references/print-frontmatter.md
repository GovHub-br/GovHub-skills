# Folha de identificação do projeto + Índice — código exato validado

Pressupõe a arquitetura de [`print-pages.md`](print-pages.md) (`.gh-page`
fixa 210×297mm, `@page { margin: 0 }`). Validado com o usuário em agosto de
2026. São duas páginas de **abertura** (front matter), sempre juntas, sempre
logo após a capa e antes do capítulo 01 — capa (página 1) → folha de
identificação (página 2) → índice (página 3) → capítulo 01 (página 4+).

## Quando usar: pergunte primeiro

Nem todo relatório leva essas duas páginas. **Antes de montar as páginas do
documento**, pergunte ao usuário:

> Este documento é um **relatório de entrega de produto** (vinculado
> formalmente a um projeto de pesquisa/contrato, com meta e produto
> identificados) ou um **relatório comum**?

- **Relatório de entrega de produto** → inclua as duas páginas
  (identificação + índice) descritas neste arquivo. É o caso típico de
  relatórios de PD&I, produtos contratuais, entregas formais a um órgão
  financiador.
- **Relatório comum** → não inclua nenhuma das duas. Vá direto da capa
  para o capítulo 01, como em `print-cover.md`.

Se for relatório de entrega, **peça ao usuário as informações da folha de
identificação** antes de escrever a página — não invente nem deixe
placeholder. Peça especificamente:

1. **Instituições/responsáveis**, com a **hierarquia** entre eles: nome
   da instituição/órgão + nome da pessoa responsável, e a quem cada órgão
   está subordinado. Quantos pares forem necessários (no documento
   validado foram 5, em duas árvores: Universidade → Decanato; Ministério
   → Diretoria → Observatório). Pergunte explicitamente "o que está
   dentro do quê", porque a página recua os níveis (ver abaixo).
2. **Identificação do projeto/entrega**: um bloco "rótulo: descrição" por
   linha, também em hierarquia. Sempre começa pelo projeto de pesquisa;
   os demais rótulos variam por contrato (no documento validado: Projeto
   → Meta → Produto → Relatório de pesquisa Nº; pode ser Entregável, Fase,
   Contrato Nº, etc., conforme o usuário informar).
3. **Autores**, agrupados por papel (ex: Coordenação Geral, Redação,
   Revisão) — pergunte os grupos e os nomes de cada um.

## Folha de identificação — o que é

Lista **alinhada à esquerda**, sem caixa alta em bloco nenhum (nem em
"Autores"). Todo item, dos três blocos, segue o mesmo padrão: rótulo em
negrito numa linha, descrição em itálico cinza na linha de baixo.

**A hierarquia institucional é mostrada por recuo e tamanho** (pedido do
usuário em 2026-09-17: "deixa de forma mais clara, por hierarquia
tipográfica ou por indentação, a separação das coisas"). Cada
`.gh-id-org-block` recebe uma classe de nível:

- `lvl-0`: órgão-raiz (Universidade, Ministério; Projeto de Pesquisa).
  Rótulo 11,5pt navy, com respiro extra acima para separar uma árvore da
  outra.
- `lvl-1`, `lvl-2`, `lvl-3`: subordinados, rótulo 10pt semibold, sem
  nenhuma marca gráfica (a primeira versão tinha um filete de 1,5px à
  esquerda; o usuário pediu para tirar em 2026-09-18). O nível 1 **não
  recua**: entre ele e o nível 0 a diferença de tamanho e cor já basta.
  Os níveis 2 e 3 recuam 8mm e 16mm. O mesmo
  esquema vale para o bloco do projeto: Projeto (0) → Meta (1) → Produto
  (2) → Relatório Nº (3); e para os autores: "Autores" (0, sem descrição)
  → cada papel (1), com os nomes na linha de descrição em itálico. Não
  existe estilo próprio para autores (as classes `.gh-id-authors-*` de
  agosto de 2026, com rótulo uppercase espaçado e papéis em roxo caixa
  alta, foram removidas em 2026-09-18 a pedido do usuário: "está bem
  diferente do institucional, coloca no mesmo padrão").

O nível 0 é o único com destaque; **não dê ao nome do projeto tratamento
maior que o das instituições** (título em roxo, caixa alta, fonte grande
foi reprovado em agosto de 2026): ele é só mais uma raiz, com o mesmo
estilo da Universidade e do Ministério.

Três blocos, separados por um divisor fino (não é uma faixa colorida, é só
uma linha curta): instituições → divisor → identificação do
projeto/entrega → divisor → autores.

### CSS

```css
.gh-id-page { position: absolute; left: 25mm; right: 25mm; top: 26mm; bottom: 22mm; display: flex; flex-direction: column; justify-content: center; }
.gh-id-org-block { text-align: left; margin-bottom: 12px; }
/* hierarquia institucional: nível 0 = órgão-raiz; nível 1 só pela tipografia; níveis 2 e 3 recuam 8mm cada */
.gh-id-org-block.lvl-0 { margin-top: 14px; }
.gh-id-org-block.lvl-0:first-child { margin-top: 0; }
.gh-id-org-block.lvl-0 .gh-id-org { font-size: 11.5pt; color: var(--dark-navy); }
.gh-id-org-block.lvl-1, .gh-id-org-block.lvl-2, .gh-id-org-block.lvl-3 { margin-bottom: 8px; }
.gh-id-org-block.lvl-1 { margin-left: 0; }     /* sem recuo: a tipografia já separa do nível 0 */
.gh-id-org-block.lvl-2 { margin-left: 8mm; }
.gh-id-org-block.lvl-3 { margin-left: 16mm; }
.gh-id-org-block.lvl-1 .gh-id-org, .gh-id-org-block.lvl-2 .gh-id-org, .gh-id-org-block.lvl-3 .gh-id-org { font-size: 10pt; font-weight: 600; }
.gh-id-org { font-size: 10.5pt; font-weight: 700; color: var(--text-strong); margin: 0; line-height: 1.35; }
.gh-id-person { font-size: 9.5pt; color: var(--text-muted); font-style: italic; margin: 2px 0 0; line-height: 1.4; }
.gh-id-divider { width: 64px; height: 2px; background: var(--primary-purple); opacity: .35; margin: 18px 0; }
```

### HTML

```html
<div class="gh-page">
  <div class="gh-id-page">
    <div>
      <!-- um .gh-id-org-block por instituição/responsável; lvl-N = profundidade na árvore -->
      <div class="gh-id-org-block lvl-0">
        <p class="gh-id-org">Universidade de Brasília</p>
        <p class="gh-id-person">Nome da pessoa responsável</p>
      </div>
      <div class="gh-id-org-block lvl-1">
        <p class="gh-id-org">Decanato de Pesquisa e Inovação</p>
        <p class="gh-id-person">Nome da pessoa responsável</p>
      </div>
      <div class="gh-id-org-block lvl-0">
        <p class="gh-id-org">Ministério da Gestão e da Inovação em Serviços Públicos</p>
        <p class="gh-id-person">Nome da pessoa responsável</p>
      </div>
      <div class="gh-id-org-block lvl-1">
        <p class="gh-id-org">Diretoria de Estratégias para Compras Sustentáveis (DECS)</p>
        <p class="gh-id-person">Nome da pessoa responsável</p>
      </div>
      <div class="gh-id-org-block lvl-2">
        <p class="gh-id-org">Observatório de Contratações Públicas</p>
        <p class="gh-id-person">Nome da pessoa responsável</p>
      </div>
    </div>

    <div class="gh-id-divider"></div>

    <div>
      <!-- primeiro item é sempre o projeto (lvl-0); os demais descem um nível por vez -->
      <div class="gh-id-org-block lvl-0">
        <p class="gh-id-org">Projeto de Pesquisa</p>
        <p class="gh-id-person">Título completo do projeto</p>
      </div>
      <div class="gh-id-org-block lvl-1">
        <p class="gh-id-org">Meta 01</p>
        <p class="gh-id-person">Descrição da meta.</p>
      </div>
      <div class="gh-id-org-block lvl-2">
        <p class="gh-id-org">Produto 2</p>
        <p class="gh-id-person">Descrição do produto.</p>
      </div>
      <div class="gh-id-org-block lvl-3">
        <p class="gh-id-org">Relatório de pesquisa 01</p>
        <p class="gh-id-person">Descrição do relatório.</p>
      </div>
    </div>

    <div class="gh-id-divider"></div>

    <div>
      <div class="gh-id-org-block lvl-0"><p class="gh-id-org">Autores</p></div>
      <!-- um bloco lvl-1 por papel; os nomes vão na linha de descrição -->
      <div class="gh-id-org-block lvl-1">
        <p class="gh-id-org">Coordenação Geral</p>
        <p class="gh-id-person">Nome 1 &middot; Nome 2</p>
      </div>
      <div class="gh-id-org-block lvl-1">
        <p class="gh-id-org">Redação</p>
        <p class="gh-id-person">Nome 1 &middot; Nome 2 &middot; Nome 3</p>
      </div>
    </div>
  </div>
  <div class="gh-footer-bar"></div>
  <div class="gh-footer">
    <span class="gh-footer__text"><span class="gh-footer__page">2</span>Nome curto do documento &middot; Nome curto do projeto/frente &middot; Gov Hub &middot; Lab Livre - UnB</span>
    <img class="gh-footer__logo" alt="" src="logo/icone-none-navy.svg">
  </div>
</div>
```

Rodapé igual ao de qualquer página de conteúdo (ver `print-footer.md`) — só
a capa não leva esse rodapé.

## Índice — o que é

Lista numerada dos capítulos (não das duas páginas de abertura — a folha de
identificação e o próprio índice não se autolistam), com linha pontilhada
guia até o número da página, no estilo clássico de sumário.

### CSS

```css
.gh-toc-page { position: absolute; left: 20mm; right: 20mm; top: 30mm; bottom: 32mm; }
.gh-toc-title { font-size: 22pt; font-weight: 800; color: var(--logo-purple); margin: 0 0 30px; }
.gh-toc-list { list-style: none; margin: 0; padding: 0; }
.gh-toc-list li { display: flex; align-items: flex-end; gap: 8px; padding: 13px 0; border-bottom: 1px solid var(--border-soft); font-size: 11.5pt; }
.gh-toc-list .num { font-weight: 800; color: var(--primary-purple); min-width: 26px; }
.gh-toc-list .label { color: var(--text-strong); font-weight: 600; }
.gh-toc-list .leader { flex: 1; border-bottom: 1px dotted var(--border-soft); margin-bottom: 5px; }
.gh-toc-list .page { color: var(--text-muted); font-weight: 700; min-width: 20px; text-align: right; }
```

### HTML

```html
<div class="gh-page">
  <div class="gh-toc-page">
    <h2 class="gh-toc-title">Índice</h2>
    <ul class="gh-toc-list">
      <li><span class="num">01</span><span class="label">Título do capítulo</span><span class="leader"></span><span class="page">4</span></li>
      <!-- um <li> por capítulo, numeração sempre começando em 01 -->
    </ul>
  </div>
  <div class="gh-footer-bar"></div>
  <div class="gh-footer">
    <span class="gh-footer__text"><span class="gh-footer__page">3</span>Nome curto do documento &middot; Nome curto do projeto/frente &middot; Gov Hub &middot; Lab Livre - UnB</span>
    <img class="gh-footer__logo" alt="" src="logo/icone-none-navy.svg">
  </div>
</div>
```

### Números de página são manuais — recalcule sempre

Como a paginação inteira é manual (ver `print-pages.md`), os números na
coluna `.page` do índice são texto fixo digitado por você, não algo que o
navegador calcula sozinho. **Toda vez que uma página for inserida, removida
ou movida em qualquer lugar do documento** (inclusive as duas páginas de
abertura descritas aqui, que empurram tudo em +2), os números do índice
ficam desatualizados e precisam ser recontados um por um, **junto com o
número impresso no rodapé de cada página** (`.gh-footer__page`, ver
`print-footer.md`). Para contar
certo: abra o HTML fonte, conte sequencialmente cada `<div class="gh-page">`
a partir da capa (capa = página 1), e anote em que página física cada
`.gh-band` (cabeçalho de capítulo) cai. Depois confira renderizando o PDF e olhando a
página real (mesmo processo de revisão do `print-pages.md`) — não confie só
na contagem manual, confirme visualmente.

## Referências

- [`print-pages.md`](print-pages.md) — arquitetura de página que estas duas páginas pressupõem, e o procedimento de revisão visual obrigatório (aplica-se aqui também).
- [`print-cover.md`](print-cover.md) — capa, que vem imediatamente antes destas duas páginas.
- [`print-footer.md`](print-footer.md) — rodapé usado em ambas.
