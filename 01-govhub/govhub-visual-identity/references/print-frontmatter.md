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

1. **Instituições/responsáveis**, na ordem hierárquica em que devem
   aparecer (de cima para baixo): nome da instituição/órgão + nome da
   pessoa responsável. Quantos pares forem necessários (no documento
   validado foram 5: universidade, decanato, ministério, diretoria,
   observatório/programa).
2. **Identificação do projeto/entrega**: um bloco "rótulo — descrição" por
   linha. Sempre inclui o nome do projeto de pesquisa; os demais rótulos
   variam por contrato (no documento validado: Meta, Produto, Relatório de
   pesquisa Nº — mas pode ser Entregável, Fase, Contrato Nº, etc., conforme
   o que o usuário informar).
3. **Autores**, agrupados por papel (ex: Coordenação Geral, Redação,
   Revisão) — pergunte os grupos e os nomes de cada um.

## Folha de identificação — o que é

Lista **uniforme, alinhada à esquerda**, sem caixa alta em nenhum bloco de
conteúdo (só o rótulo "AUTORES" leva versalete/maiúsculas, como um
cabeçalho de seção da página — não o título do projeto). Todo item segue o
mesmo padrão visual: rótulo em negrito numa linha, descrição em itálico
cinza na linha de baixo. **Não dê destaque tipográfico maior ao nome do
projeto do que às instituições** — é a mesma hierarquia visual, só mais um
item da lista. Essa foi uma correção pedida pelo usuário depois de uma
primeira versão que colocava o título do projeto em roxo, caixa alta e
fonte grande, destoando do resto.

Três blocos, separados por um divisor fino (não é uma faixa colorida, é só
uma linha curta): instituições → divisor → identificação do
projeto/entrega → divisor → autores.

### CSS

```css
.gh-id-page { position: absolute; left: 25mm; right: 25mm; top: 26mm; bottom: 22mm; display: flex; flex-direction: column; justify-content: center; }
.gh-id-org-block { text-align: left; margin-bottom: 12px; }
.gh-id-org { font-size: 10.5pt; font-weight: 700; color: var(--text-strong); margin: 0; line-height: 1.35; }
.gh-id-person { font-size: 9.5pt; color: var(--text-muted); font-style: italic; margin: 2px 0 0; line-height: 1.4; }
.gh-id-divider { width: 64px; height: 2px; background: var(--primary-purple); opacity: .35; margin: 18px 0; }
.gh-id-authors-title { text-align: left; text-transform: uppercase; letter-spacing: 2px; font-size: 9.5pt; font-weight: 800; color: var(--text-strong); margin: 4px 0 12px; }
.gh-id-authors-role { text-align: left; font-size: 9pt; font-weight: 700; text-transform: uppercase; letter-spacing: .5px; color: var(--primary-purple); margin: 0 0 4px; }
.gh-id-authors-names { text-align: left; font-size: 10pt; color: var(--text-body); line-height: 1.5; margin: 0 0 10px; }
```

### HTML

```html
<div class="gh-page">
  <div class="gh-id-page">
    <div>
      <!-- um .gh-id-org-block por instituição/responsável, quantos forem necessários -->
      <div class="gh-id-org-block">
        <p class="gh-id-org">Nome da instituição/órgão</p>
        <p class="gh-id-person">Nome da pessoa responsável</p>
      </div>
      <!-- repita para cada instituição -->
    </div>

    <div class="gh-id-divider"></div>

    <div>
      <!-- primeiro item é sempre o projeto; os demais variam por contrato -->
      <div class="gh-id-org-block">
        <p class="gh-id-org">Projeto de Pesquisa</p>
        <p class="gh-id-person">Título completo do projeto</p>
      </div>
      <div class="gh-id-org-block">
        <p class="gh-id-org">Meta 01</p>
        <p class="gh-id-person">Descrição da meta.</p>
      </div>
      <!-- repita para Produto, Relatório de pesquisa Nº, ou o que o usuário informar -->
    </div>

    <div class="gh-id-divider"></div>

    <div>
      <div class="gh-id-authors-title">Autores</div>
      <!-- um par role+names por grupo -->
      <div class="gh-id-authors-role">Coordenação Geral</div>
      <p class="gh-id-authors-names">Nome 1 &middot; Nome 2</p>
      <div class="gh-id-authors-role">Redação</div>
      <p class="gh-id-authors-names">Nome 1 &middot; Nome 2 &middot; Nome 3</p>
    </div>
  </div>
  <div class="gh-footer-bar"></div>
  <div class="gh-footer">
    <span class="gh-footer__text">Nome curto do documento &middot; Nome curto do projeto/frente &middot; Gov Hub &middot; Lab Livre - UnB</span>
    <img class="gh-footer__logo" alt="" src="logo/orientation=none, colour=primary.svg">
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
    <span class="gh-footer__text">Nome curto do documento &middot; Nome curto do projeto/frente &middot; Gov Hub &middot; Lab Livre - UnB</span>
    <img class="gh-footer__logo" alt="" src="logo/orientation=none, colour=primary.svg">
  </div>
</div>
```

### Números de página são manuais — recalcule sempre

Como a paginação inteira é manual (ver `print-pages.md`), os números na
coluna `.page` do índice são texto fixo digitado por você, não algo que o
navegador calcula sozinho. **Toda vez que uma página for inserida, removida
ou movida em qualquer lugar do documento** (inclusive as duas páginas de
abertura descritas aqui, que empurram tudo em +2), os números do índice
ficam desatualizados e precisam ser recontados um por um. Para contar
certo: abra o HTML fonte, conte sequencialmente cada `<div class="gh-page">`
a partir da capa (capa = página 1), e anote em que página física cada
`.gh-band` de capítulo cai. Depois confira renderizando o PDF e olhando a
página real (mesmo processo de revisão do `print-pages.md`) — não confie só
na contagem manual, confirme visualmente.

## Referências

- [`print-pages.md`](print-pages.md) — arquitetura de página que estas duas páginas pressupõem, e o procedimento de revisão visual obrigatório (aplica-se aqui também).
- [`print-cover.md`](print-cover.md) — capa, que vem imediatamente antes destas duas páginas.
- [`print-footer.md`](print-footer.md) — rodapé usado em ambas.
