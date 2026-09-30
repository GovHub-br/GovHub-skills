# Paleta Gov Hub — referência e quando usar cada cor

Use exatamente estes hexadecimais. Os nomes de token estão em inglês (ver
`tokens.css`).

> **Modo sóbrio (2026-09-30).** A equipe de design e
> comunicação fechou a linguagem sóbria no pacote de 58 posts (v22) e ela
> passa a valer para **tudo**: post, relatório, slide, dashboard, página.
> Mudanças em relação ao MIV colorido:
> - `#F2F1F6` no lugar do pêssego `#FFE7E1`;
> - `#BE006E` no lugar do rosa `#F9006F`, só em detalhe;
> - magenta `#EF41FF` fora da paleta ativa;
> - Reddit Sans em tudo, sem Oswald e sem caixa alta nas chamadas.
>
> A paleta colorida anterior foi descontinuada, junto com os templates e
> ícones que a usavam: não há modo colorido.

## Cores da marca (modo sóbrio)

| Token | Hex | Uso |
|---|---|---|
| `--primary-purple` | `#613EFF` | **Cor-assinatura.** Títulos de destaque, formas, botões primários, links, badges, fundo de peça. |
| `--dark-navy` | `#0A005A` | Títulos, fundos escuros, cor de seção em PDF (tabela, callout), contraste máximo. |
| `--bg-soft` | `#F2F1F6` | O claro da marca: blocos, cards, pílulas, faixas, zebra de tabela, fundo claro de peça. Apelido antigo: `--bg-peach`. |
| `--accent-rose` | `#BE006E` | **Acento pontual.** Pílula, tag, pontinho, círculo numerado, aspas, seta, CTA. Nunca em área grande. Apelido antigo: `--accent-pink`. |
| `--text-white` | `#FFFFFF` | Texto sobre roxo, navy ou `#BE006E`. |

Fora disso só entram branco, os neutros de texto e as semânticas. Não há
cinza além de `#F2F1F6`: os antigos `#F7F7F7` e `#F8F9FA`
(`--bg-light`, `--bg-subtle`) agora apontam para ele.

## Estados derivados do primário

| Token | Hex | Uso |
|---|---|---|
| `--purple-600` | `#5235D9` | Hover/foco de elementos roxos. Aproximado, não vem do MIV. |
| `--purple-700` | `#3F28A6` | Active/pressionado, e roxo de texto pequeno sobre branco. |

## Neutros e texto

| Token | Hex | Uso |
|---|---|---|
| `--text-strong` | `#202020` | Títulos e texto forte neutros. |
| `--text-body` | `#2D3748` | Corpo de texto padrão, mantido neutro para leitura longa. |
| `--text-muted` | `#666666` | Legendas, metadados. Nunca sobre fundo escuro. |

## Os três fundos e o que vai sobre cada um

Vale para posts, slides, capas e qualquer peça com fundo de cor.

| Fundo | Texto | Formas e objetos | Acento |
|---|---|---|---|
| **Navy** `#0A005A` | Branco; números grandes em branco ou `#F2F1F6` | Formas roxas ou `#F2F1F6`; cards, painéis, notificações e balões brancos ou `#F2F1F6` com texto navy | `#BE006E` só em forma ou detalhe, nunca em texto |
| **Roxo** `#613EFF` | Branco | Formas navy ou `#F2F1F6`; cards brancos ou `#F2F1F6` | Sem `#BE006E` (contraste baixo); o acento é navy |
| **Claro** (branco ou `#F2F1F6`) | Títulos navy, corpo `#2D3748` | Roxo e navy nas formas; blocos `#F2F1F6` sobre branco | `#BE006E` em pílula, tag, pontinho, círculo numerado, aspas, seta, CTA |

## Acessibilidade (contraste)

- Branco sobre roxo, navy ou `#BE006E`: **OK**.
- Navy sobre branco ou `#F2F1F6`: **OK**.
- `#BE006E` sobre claro: cerca de 5:1, **OK** para texto de detalhe e CTA.
- `#BE006E` sobre navy: cerca de 3:1, **só em forma**, nunca em texto.
- **Nunca texto roxo sobre navy** (cerca de 2,6:1).
- **Nunca texto branco sobre fundo claro** (branco ou `#F2F1F6`).
- Roxo em texto pequeno sobre branco: use `--purple-700` (`#3F28A6`).
- Nunca `--text-muted` sobre fundo escuro.

## Regra de proporção

- Roxo e navy dominam; `#F2F1F6` é o respiro.
- `#BE006E` é detalhe, bem menos de 10 % da peça. Em fundo roxo ele não
  entra.
- Um objeto por quadro (post e slide): mockup, círculo ou bloco. Formas
  oficiais sólidas, sem gradiente e sem tom derivado (nada de círculo
  "tonal" com branco translúcido).

## Rampa editorial e PDF

No modo sóbrio a rampa é só **navy → roxo → `#F2F1F6`**:

| Token | Hex | Uso em PDF |
|---|---|---|
| `--editorial-00-navy` | `#0A005A` | Cor de seção (header e legenda de tabela, contorno de callout) em todos os capítulos. |
| `--editorial-01-purple` | `#613EFF` | Título do capítulo (`.gh-band__title`), quarto de círculo da capa, índice. |
| `--editorial-04-soft` | `#F2F1F6` | Fundo de forma e de chip (pílula da capa), zebra. Texto por cima em navy. |

Decisões que continuam valendo (2026-09-17/18): navy em todas as tabelas,
roxo só no título do capítulo, `h3` em navy, capa branca, cabeçalho
branco, rodapé com símbolo navy. A faixa colorida full-bleed por capítulo
(navy → roxo → magenta → rosa → pêssego) é histórico: não reproduza.

## Roxo exato da logo

`--logo-purple` = `#613EFF`, o mesmo do primário (confirmado na exportação
de 2026-09-16). Existe como token separado só por compatibilidade com
`print-cover.md`.

## Elementos gráficos

Círculo cheio, anel, semicírculo, quarto de círculo e pílula, derivados das
formas-base do MIV ("círculos, semicírculos e retângulos arredondados").
Sempre sólidos, em cor da paleta ativa. Ver `graphic-elements-catalog.md`.

## Aplicação da marca (regra do MIV)

Logo navy sobre fundo claro, branca sobre fundo escuro (navy, roxo). Os
arquivos `*-peach` da logo ficam sem uso no modo sóbrio. Nunca distorcer,
girar, contornar, aplicar sombra/efeito ou recolorir fora da paleta.
