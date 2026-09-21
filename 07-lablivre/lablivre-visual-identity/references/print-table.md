# Tabela de dados em PDF — código exato validado

Pressupõe a arquitetura de [`print-pages.md`](print-pages.md) (`.gh-page`
fixa 210×297mm, `@page { margin: 0 }`). Herdado da skill do Gov Hub
(extraído do `Relatório de Diagnóstico e Entregáveis - GovHub.pdf`, um
documento real validado lá); ainda não validado em peça do Lab Livre.
Tabela em azul profundo `#080056` (o "navy" do texto).

## O que é

Tabela **sem cartão ao redor**: nada de borda arredondada, sombra, ou caixa
de cabeçalho separada como em `component-recipes.md` (`.gh-table`, que é
para HTML/web, não para PDF impresso). No PDF, a tabela é só a tabela:
uma legenda em negrito acima, header sólido navy, linhas finas embaixo de
cada linha, zebra sutil.

**Numeração de legenda é sequencial no documento inteiro** (Tabela 1,
Tabela 2, Tabela 3...), não reinicia por capítulo. Conte a partir da
primeira tabela do documento, na ordem em que aparecem.

## CSS

```css
.gh-table-caption {
  font-size: 10.5pt; font-weight: 700;
  color: var(--section-color, var(--primary-purple));
  margin: 0 0 6pt;
}
.gh-print-table {
  width: 100%; border-collapse: collapse;
}
.gh-print-table thead th {
  background: var(--section-color, var(--primary-purple));
  color: #fff;
  font-weight: 600; font-size: 9.5pt;
  text-align: left;
  padding: 9pt 12pt;
}
.gh-print-table tbody td {
  padding: 8pt 12pt;
  font-size: 9.5pt; color: var(--text-body);
  border-bottom: 1px solid var(--border-soft);
  vertical-align: top;
}
.gh-print-table tbody tr:last-child td { border-bottom: none; }
.gh-print-table tbody tr:nth-child(even) td { background: var(--bg-subtle); }
```

O header é **sempre navy** (`--editorial-00-navy`, via `--section-color`
definida no `.gh-page`, ver `print-header.md`), em todos os capítulos.
Histórico da decisão (simulação do Relatório de Diagnóstico com a IDV
nova): em 2026-09-17 o usuário tirou magenta e rosa das tabelas e aprovou
navy e roxo alternando por capítulo; em 2026-09-18 pediu "a cor da tabela
sempre em navy, sem intercalar entre os capítulos". Legenda e contorno dos
callouts herdam a mesma cor. O roxo no PDF fica reservado ao título do
capítulo, à capa e ao índice.

A variável `--section-color` continua sendo o mecanismo (a tabela não
declara navy fixo) para que um documento que precise de outra cor de seção
mude num lugar só; mas o padrão, sem pedido em contrário, é navy em tudo.

## HTML

```html
<p class="gh-table-caption">Tabela 6: Quantidade de registros da extração da API do Compras.gov.br</p>
<table class="gh-print-table">
  <thead>
    <tr><th>Tabela</th><th>Registros</th><th>Domínio</th></tr>
  </thead>
  <tbody>
    <tr><td>caracteristicas_material</td><td>1.904.256</td><td>Catálogo de Materiais</td></tr>
    <!-- uma linha por registro -->
  </tbody>
</table>
```

## O que não varia

Sem borda ao redor da tabela inteira, sem `border-radius`, sem
`box-shadow` — a única cor que a tabela carrega é o header (sólido, cor da
seção) e a zebra sutil (`--bg-subtle`) nas linhas pares. A legenda sempre
vem **antes** da tabela, nunca dentro de uma barra de cabeçalho separada.

## Quando a tabela precisa de metadados extras (chave primária, join, etc.)

O documento de referência é narrativo (sem PK/FK) — se o seu conteúdo
precisar desse tipo de indicador (ex: dicionário de dados/schema com
chaves primárias e estrangeiras), mantenha a legenda e as cores do header
exatamente como acima, e adicione só o indicador necessário dentro da
célula (ex: um badge pequeno depois do nome da coluna), sem reintroduzir
cartão, sombra ou cabeçalho de tabela em caixa separada — o padrão "sem
cartão, header sólido, zebra fina" é o que precisa ficar consistente entre
documentos, não o conjunto exato de colunas.

## Referências

- [`print-pages.md`](print-pages.md) — arquitetura de página que esta tabela pressupõe.
- [`print-header.md`](print-header.md) — de onde vem `--section-color`.
- [`palette.md`](palette.md) — o que sobrou da rampa editorial em PDF.
