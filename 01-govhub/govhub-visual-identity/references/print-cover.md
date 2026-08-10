# Capa de PDF — código exato validado

Pressupõe a arquitetura de [`print-pages.md`](print-pages.md) (`.gh-page`
fixa 210×297mm, `@page { margin: 0 }`). Validado com o usuário em agosto de
2026 — o que muda de um documento para outro é só o **título**, o
**subtítulo** e o **kicker**; o resto (fundo, moldura, logo, rodapé da capa)
é fixo, copie sem alterar.

## O que é

Fundo **sólido** `--logo-purple` (`#7521F9`), sem gradiente, sem onda
decorativa. Moldura arredondada fina inset 10mm. Logo GovHub branca **no
fluxo normal**, alinhada à esquerda junto com o resto do texto (não
posicionada solta no canto) — acima do kicker. Título e subtítulo em
branco. Rodapé pequeno no canto inferior esquerdo, mesma tipografia
(maiúsculas + letter-spacing) do kicker.

## CSS

```css
.gh-cover { background: var(--logo-purple); color: #fff; }

.gh-cover__border {
  position: absolute; inset: 10mm;
  border: 2.5px solid rgba(255,255,255,0.55);  /* fina e discreta, não branco sólido */
  border-radius: 24px;
  pointer-events: none;
}

.gh-cover__logo {
  display: block;
  height: 40px; width: auto;
  margin-bottom: 52px;                          /* respiro antes do kicker */
}

.gh-cover__content {
  position: absolute; left: 20mm; right: 20mm; top: 50%;
  transform: translateY(-30%);                  /* bloco de texto um pouco acima do centro vertical */
}

.gh-cover__kicker {
  text-transform: uppercase; letter-spacing: 2.2px;
  font-size: 10.5px; font-weight: 700; opacity: .85;
  margin-bottom: 16px;
}

.gh-cover__title {
  font-size: 38px; font-weight: 800; line-height: 1.12;
  margin: 0 0 18px; max-width: 15ch;
}

.gh-cover__subtitle {
  font-size: 14px; line-height: 1.55; max-width: 60ch; opacity: .92;
}

.gh-cover__footer {
  position: absolute; left: 20mm; bottom: 16mm;
  text-transform: uppercase; letter-spacing: 1.8px;  /* mesma tipografia do kicker */
  font-size: 10px; font-weight: 700; opacity: .85;
}
```

## HTML

```html
<div class="gh-page gh-cover">
  <div class="gh-cover__border"></div>
  <div class="gh-cover__content">
    <img class="gh-cover__logo" alt="GovHub" src="logo/orientation=horizontal, colour=light.svg">
    <div class="gh-cover__kicker">Metodologia GovHub · Governança de Dados</div>
    <h1 class="gh-cover__title">Título do documento em uma ou duas linhas</h1>
    <p class="gh-cover__subtitle">Subtítulo de uma frase explicando o documento.</p>
  </div>
  <div class="gh-cover__footer">GovHub &middot; Lab Livre &middot; Metodologia de projetos</div>
</div>
```

## O que varia por documento

- **Kicker**: contexto/metodologia (ex: "Metodologia GovHub · Governança de Dados").
- **Título** (`.gh-cover__title`): nome do documento. `max-width: 15ch` já
  força quebra de linha em títulos longos — teste com 2-3 linhas antes de
  aumentar a largura.
- **Subtítulo**: uma frase, `max-width: 60ch`.
- O texto do `.gh-cover__footer` ("GovHub · Lab Livre · Metodologia de
  projetos") é fixo da marca — normalmente **não muda** entre documentos.

## O que não varia (não mexa sem motivo)

Cor de fundo, espessura/opacidade da moldura, tamanho e posição da logo,
tipografia do rodapé da capa — já testados e aprovados.
