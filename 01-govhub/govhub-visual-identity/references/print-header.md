# Cabeçalho de capítulo em PDF — código exato validado

Pressupõe a arquitetura de [`print-pages.md`](print-pages.md) (`.gh-page`
fixa 210×297mm, `@page { margin: 0 }`). Validado com o usuário em
2026-09-17 (simulação do Relatório de Diagnóstico com a IDV nova). Só
aparece na **primeira página de cada capítulo**; páginas de continuação
do mesmo capítulo não têm cabeçalho (ver [`print-footer.md`](print-footer.md)
para o rodapé, que aparece em toda página, com ou sem cabeçalho).

> Este cabeçalho **substitui** a faixa colorida full-bleed da versão
> anterior. O usuário a achou "muito forte" e pediu fundo branco, tudo em
> navy e uma barra abaixo, igual à do rodapé. Se encontrar
> `.gh-band { background: var(--section-color) ... color: #fff }` em algum
> documento antigo, é a faixa velha; não a reproduza em documento novo.

## O que é

Cabeçalho **sóbrio, sobre o branco da página**, alinhado às margens do
conteúdo (20mm): numeral grande em navy translúcido + eyebrow (rótulo
pequeno em maiúsculas) em navy + **título em roxo** (`--primary-purple`,
o único roxo da página de texto), e uma **barra de 2px na cor da barra do
rodapé** (`--border-soft`) fechando o bloco por baixo, da margem esquerda
à direita. Sem fundo, sem formas, sem chip de ícone. O roxo no título é
deliberado (testado e aprovado em 2026-09-18): com os `h3` do corpo em
navy, ele marca o topo da página como o nível mais alto da hierarquia.

**Numeração sempre começa em 1** (não em 0): "01", "02", "03"...

## CSS

```css
.gh-band {
  position: absolute; top: 0; left: 20mm; right: 20mm;   /* mesma margem do conteúdo, NÃO left/right:0 */
  padding: 22mm 0 9mm;
  border-bottom: 2px solid var(--border-soft);           /* mesma barra do rodapé (print-footer.md) */
  color: var(--dark-navy);
}
.gh-band__row { display: flex; align-items: center; gap: 8mm; }

.gh-band__num {
  font-size: 56px; font-weight: 800; line-height: 1;
  color: var(--dark-navy); opacity: .45;
  min-width: 34mm;
}
.gh-band__eyebrow {
  text-transform: uppercase; letter-spacing: 2px;
  font-size: 11px; font-weight: 700;
  color: var(--dark-navy); opacity: .7;
  margin-bottom: 7px;
}
.gh-band__title {
  color: var(--primary-purple);  /* explícito: um reset global tipo h2{color:...} no projeto sobrescreve a herança */
  font-size: 22pt; font-weight: 800; line-height: 1.2; margin: 0;
}
```

Se o **título e/ou eyebrow crescerem** (título de duas linhas), o bloco
fica um pouco mais alto e a barra desce junto; `padding` não é altura
fixa. Não force uma altura fixa por causa disso; ajuste o `top` do corpo
(fórmula abaixo).

## HTML

```html
<div class="gh-page" style="--section-color:var(--editorial-00-navy)">
  <div class="gh-band">
    <div class="gh-band__row">
      <div class="gh-band__num">01</div>
      <div>
        <div class="gh-band__eyebrow">Sobre este documento</div>
        <h2 class="gh-band__title">Introdução</h2>
      </div>
    </div>
  </div>
  <div class="gh-page-body">
    <!-- conteúdo do capítulo, ver "Corpo da página" abaixo -->
  </div>
  <!-- rodapé: ver print-footer.md -->
</div>
```

`--section-color` fica no `.gh-page` (não no `.gh-band`) porque quem a
consome são a tabela e os callouts do corpo, inclusive em página de
continuação sem cabeçalho. **Em PDF ela é sempre `--editorial-00-navy`**,
em todos os capítulos (decisão de 2026-09-18: "sempre navy, sem
intercalar"); a variável continua existindo só para manter os componentes
do corpo desacoplados. Nome exato do token, com sufixo, definido em
`tokens.css`; um `var()` apontando para um nome que não existe não dá
erro visível: cai silenciosamente no fallback (`var(--primary-purple)`) e
a tabela sai roxa sem avisar.

### Chip de ícone (removido)

A faixa antiga tinha um chip branco com ícone de produto à direita. No
cabeçalho branco ele ficaria solto, então saiu. Se o usuário pedir o ícone
de volta, a saída é um chip pêssego (`--bg-peach`, `border-radius: 14px`,
60px, ícone `-default` 42px) com `margin-left: auto` dentro do
`.gh-band__row`; não reintroduza sem pedido.

## Corpo da página (`.gh-page-body`)

```css
.gh-page-body {
  position: absolute; left: 20mm; right: 20mm;
  top: 58mm; bottom: 32mm;    /* top = altura real do cabeçalho + ~12mm de respiro, ver fórmula */
  overflow: hidden;
}
/* página de continuação, sem cabeçalho: só o top muda (respiro normal do topo).
   bottom continua 32mm igual: o rodapé (print-footer.md) fica na mesma
   altura em toda página, tenha ela cabeçalho ou não. */
.gh-page-body.no-band { top: 20mm; }
```

**`58mm` não é uma constante fixa: é `altura_real_do_cabeçalho + ~12mm`
de respiro**, e deu 58mm porque o cabeçalho validado (uma linha de
eyebrow + título) termina em ~46mm, barra incluída. A primeira versão da
IDV nova usava 74mm (~28mm de respiro, herdado da faixa colorida) e o
usuário pediu para "diminuir o espaço entre a barra abaixo do título e o
início do texto"; 12mm foi o valor aprovado.

Quando o corpo pagina por medição (ver "Conteúdo que flui em muitas
páginas" em `print-pages.md`) e você mede a altura real de cada cabeçalho
no navegador, **não use a altura medida como `top` diretamente**: já
aconteceu de um agente fazer isso e o texto nascer colado na barra. A
regra, com cabeçalho de altura variável:

```
top = altura_real_do_cabeçalho_em_mm (até a barra) + 12
```

Os ~12mm valem tanto para cabeçalho curto quanto para título de duas
linhas: é sempre a mesma folga absoluta somada à altura real, não uma
margem fixa de página que ignora o quanto o cabeçalho cresceu.

## Escala tipográfica (PDF impresso)

Validada com o usuário em agosto de 2026. **Use sempre `pt`, nunca `px`**,
em qualquer texto de PDF: `pt` é unidade física fixa (1pt = 1/72
polegada), então o tamanho no papel é previsível; `px` depende da resolução
assumida pelo motor de renderização. Vale para todo o corpo do documento
(título de capítulo já é a exceção documentada abaixo, por ser elemento de
cabeçalho, não corpo corrido).

| Nível | Uso | Tamanho |
|---|---|---|
| Título principal (H1) | `.gh-band__title`, título de capítulo no cabeçalho | 20–24pt (padrão: 22pt) |
| Subtítulo (H2/H3) | `.gh-page-body h3`/`h4`, subtítulo de seção dentro do corpo (ex: "Fontes de dados analisadas"), em `--dark-navy` | 14–18pt (padrão: 16pt) |
| Texto principal (corpo) | `.gh-page-body p`, `li`, texto corrido | 11–12pt (padrão: 11.5pt) |
| Notas de rodapé e legendas | `.gh-footer__text`, `.gh-fig-inline__caption`, `.gh-table-caption`, células de tabela, callouts | 9–10pt |

```css
.gh-page-body h3 { font-size: 16pt; color: var(--dark-navy); margin: 0 0 10px; }  /* navy, não roxo: o roxo roubava atenção do título do capítulo (pedido do usuário, 2026-09-18) */
.gh-page-body p  { font-size: 11.5pt; line-height: 1.5; color: var(--text-body); margin: 0 0 14px; text-align: justify; hyphens: none; }
.gh-page-body li { font-size: 11.5pt; line-height: 1.5; color: var(--text-body); margin-bottom: 4px; }
```

O que **não muda** com essa escala: o numeral grande (`.gh-band__num`,
56px, decorativo) e o eyebrow (`.gh-band__eyebrow`, rótulo pequeno em
maiúsculas); nenhum dos dois é "texto de leitura", então ficam fora da
escala de 4 níveis.

## O que varia por capítulo

- Numeral, eyebrow, título. Só isso.

## O que não varia

Fundo branco, numeral e eyebrow em navy (opacidades .45 e .7), título em
roxo, barra de 2px `--border-soft` alinhada às margens de 20mm, sem
formas, sem chip de ícone, `--section-color` navy.

## Histórico

- **Agosto/2026:** faixa colorida full-bleed na cor do capítulo, texto
  branco, numeral a 72% de branco, chip branco com ícone. Substituída.
- **2026-09-17 (IDV nova):** v1 manteve a faixa com meio-anel decorativo;
  o usuário pediu "mais sóbrio: fundo branco, número, título e subtítulo
  em navy, e uma barra similar à do footer abaixo". v2 aprovada; depois
  respiro do corpo reduzido de 28mm para 12mm.
- **2026-09-18:** `h3` do corpo de roxo para navy ("roubava atenção do
  título da página"); em seguida o título do capítulo testado em roxo e
  aprovado; tabelas fixadas em navy em todos os capítulos.
