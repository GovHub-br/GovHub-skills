# Cabeçalho de capítulo em PDF — código exato validado

Pressupõe a arquitetura de [`print-pages.md`](print-pages.md) (`.gh-page`
fixa 210×297mm, `@page { margin: 0 }`). Validado com o usuário em agosto de
2026. Só aparece na **primeira página de cada capítulo** — páginas de
continuação do mesmo capítulo não têm essa faixa (ver
[`print-footer.md`](print-footer.md) para o rodapé, que aparece em toda
página, com ou sem cabeçalho).

## O que é

Faixa colorida sólida **full-bleed**: cobre 100% da largura e começa
exatamente no topo físico da página, sem nenhuma margem branca ao redor
(isso sai de graça aqui porque a página inteira já não tem margem — ver
`print-pages.md` para o porquê de NÃO tentar isso com margem negativa).
Dentro: numeral grande translúcido + eyebrow (rótulo pequeno em
maiúsculas) + título, e opcionalmente um chip branco com ícone de produto
GovHub à direita.

**Numeração sempre começa em 1** (não em 0) — "01", "02", "03"...

## CSS

```css
.gh-band {
  position: absolute; top: 0; left: 0; right: 0;
  background: var(--section-color, var(--primary-purple));  /* cor do capítulo, ver rampa editorial em palette.md */
  color: #fff;
  padding: 17mm 20mm 14mm;
}
.gh-band__row { display: flex; align-items: center; gap: 8mm; }

.gh-band__num {
  font-size: 56px; font-weight: 800; line-height: 1;
  color: rgba(255,255,255,0.72);
  min-width: 34mm;
}
.gh-band__eyebrow {
  text-transform: uppercase; letter-spacing: 2px;
  font-size: 11px; font-weight: 700; opacity: .85;
  margin-bottom: 7px;
}
.gh-band__title { font-size: 27px; font-weight: 800; line-height: 1.2; margin: 0; }

/* chip do ícone — opcional, mas inclua no exemplo/template para não esquecer como fica */
.gh-band__icon {
  margin-left: auto; flex-shrink: 0;
  width: 60px; height: 60px;
  background: #fff; border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 3px 12px rgba(0,0,0,0.2);
}
.gh-band__icon img, .gh-band__icon svg { width: 42px; height: 42px; }
```

Se o **título e/ou eyebrow crescerem** (título de capítulo mais longo, por
exemplo), é esperado que a faixa fique um pouco mais alta — `padding` não é
fixo em altura, ela cresce com o conteúdo. Não force uma altura fixa na
faixa por causa disso.

## HTML

```html
<div class="gh-page">
  <div class="gh-band" style="--section-color:var(--editorial-01-purple)">
    <div class="gh-band__row">
      <div class="gh-band__num">01</div>
      <div>
        <div class="gh-band__eyebrow">Sobre este documento</div>
        <h2 class="gh-band__title">Introdução</h2>
      </div>
      <!-- ícone opcional: remova o bloco inteiro se o capítulo não tiver um.
           Use <img>, não SVG inline colado — mesmo padrão dos callouts em
           editorial-report.md seção 6, mais simples de manter consistente. -->
      <div class="gh-band__icon">
        <img src="icons/name=workflow, background=Default.svg" alt="">
      </div>
    </div>
  </div>
  <div class="gh-page-body">
    <!-- conteúdo do capítulo, ver "Corpo da página" abaixo -->
  </div>
  <!-- rodapé: ver print-footer.md -->
</div>
```

**Nome exato do token de cor**: é `--editorial-01-purple`,
`--editorial-02-magenta`, `--editorial-03-pink`, `--editorial-04-coral` (com
o sufixo da cor, definidos em `tokens.css`) — não `--editorial-01` sem
sufixo. Um `var()` apontando para um nome que não existe não dá erro
visível: ele silenciosamente cai no fallback (`var(--primary-purple)` aqui),
e a faixa fica na cor errada sem avisar nada. Confira o nome exato em
`tokens.css` antes de usar.

## Corpo da página (`.gh-page-body`)

```css
.gh-page-body {
  position: absolute; left: 20mm; right: 20mm;
  top: 74mm; bottom: 32mm;    /* top reserva espaço pra faixa; ajuste se a faixa crescer muito */
  overflow: hidden;
}
/* página de continuação, sem faixa: só o top muda (respiro normal do topo).
   bottom continua 32mm igual — o rodapé (print-footer.md) fica na mesma
   altura em toda página, tenha ela faixa ou não. */
.gh-page-body.no-band { top: 20mm; }
```

Tipografia do corpo (não especificada em nenhum outro arquivo — use esta
base e ajuste por documento):

```css
.gh-page-body h3 { font-size: 15px; color: var(--logo-purple); margin: 0 0 10px; }
.gh-page-body p  { font-size: 12.5px; line-height: 1.6; color: var(--text-body); margin: 0 0 14px; }
```

## O que varia por capítulo

- `--section-color`: cor da faixa, rotaciona pela rampa editorial (ver
  `palette.md` — `--editorial-01-purple` → `02-magenta` → `03-pink` →
  `04-coral`, repetindo o ciclo do 5º capítulo em diante).
- Numeral, eyebrow, título.
- Ícone (opcional): escolha por nome mais próximo do conteúdo, ver
  `editorial-report.md` seção 5 para o mapeamento curado de ícones.

## O que não varia

Estrutura da faixa (padding, tamanhos de fonte, chip do ícone),
posicionamento full-bleed, opacidade do numeral (0.72).
