# Posts e carrossel Gov Hub

Posts de feed retrato (`1080×1350`) para Instagram e LinkedIn, na
linguagem sóbria fechada pela equipe de design e comunicação em
2026-09-30 (v22, 58 posts). Os posts coloridos anteriores foram
descontinuados.

## Primeiro passo: parta de um template pronto

Não componha do zero. Os templates estão no CDN, um HTML autocontido por
post (CSS, marcação, logos e ícones embutidos):

```
https://cdn.jsdelivr.net/gh/GovHub-br/skills-assets@main/gov-hub/post-templates-sobrio/<arquivo>.html
```

- Galeria com filtro por fundo e tipo: `.../post-templates-sobrio/index.html`
- Lista completa com nome, tipo, fundo e descrição: `.../post-templates-sobrio/manifest.json`

Fluxo: escolha o **fundo do carrossel**, escolha um template por quadro
na tabela abaixo, baixe os HTMLs, troque só os textos e números de
exemplo (e o ícone de produto, se o card tiver um), mantenha formas,
posições e tamanhos. Ao entregar, diga quais arquivos usou.

## Um fundo por carrossel

Um carrossel usa **um fundo só**: navy, roxo ou claro. A capa
pode inverter (carrossel claro com capa navy, por exemplo). Ordem:
**capa → conteúdo × N → dados ou ênfase → convite**. Um post único usa só
uma capa, uma ênfase ou um quadro de dados.

**Não há template de fechamento.** Quando um carrossel precisar de
fechamento, a equipe de design cria a partir dos modelos existentes: não
componha um por conta própria; avise o usuário e termine no convite.

## Catálogo por tipo e fundo

Número do arquivo por combinação. `—` = não existe nesse fundo (use o
mesmo tipo em outro fundo só na capa, ou escolha outro tipo).

| Tipo | Nome | Navy | Roxo | Claro |
|---|---|---|---|---|
| capa | Chamada gigante | 01 | 04 | — |
| capa | Pílula na chamada | 02 | 06 | — |
| capa | Capa D (chamada + apoio) | 03 | 05 | — |
| conteúdo | Círculo com texto | 10 | 33 | 07 (acento rosa), 24 (acento roxo) |
| conteúdo | Lista estilo app | 12 | 34 | 08 (rosa), 26 (roxo) |
| conteúdo | Card-pasta (dataset) | 09 | — | — |
| conteúdo | Notificações | 11 | 25 | — |
| conteúdo | Lista numerada | 13 | 27 | 18 |
| conteúdo | Marcadores-círculo | 14 | 28 | 19 |
| conteúdo | Cards com ícone | 15 | 30 | 21 |
| conteúdo | Checklist com faixa | — | 29 | 20 |
| conteúdo | Linha do tempo | 16 | 31 | 22 |
| conteúdo | Texto + destaque | 17 | 32 | 23 |
| dados | Barras | 36 | 45 | 40 |
| dados | Números em grade | 37 | 46 | 41 |
| dados | Ranking | 38 | 47 | 42 |
| dados | Antes e depois | 39 | 48 | 43 |
| dados | Número com pílula | — | 49 | 35 (rosa), 44 (roxo) |
| ênfase | Número-chave solo | 50 | 54 | 52 |
| ênfase | Frase em bloco | 51 | 55 | 53 |
| convite | Convite em conversa | — | 58 | 56 |
| convite | Convite B (CTA em bloco) | — | 57 | — |

Nome do arquivo = `NN-<tipo>-<nome>-<fundo>.html` (ver `manifest.json`).
Carrossel navy usa o convite roxo (57 ou 58).

## Linguagem (o que foi aprovado)

**Tipografia:** Reddit Sans em tudo. Chamada com peso 400 misturado a 800
("Seu **órgão** merece **dados** melhores."), caixa alta e baixa,
`letter-spacing: -0.025em`, `line-height: 1.06`. Numerais grandes em 800
com `-0.05em`. Eyebrow pequeno pode ser uppercase com espaçamento largo.
Sem Oswald e sem chamada em caixa alta.

**Cor por fundo** (regra completa e contraste em `palette.md`):

| Fundo | Texto | Formas e objetos | Acento |
|---|---|---|---|
| Navy | Branco; números em branco ou `#F2F1F6` | Formas roxas ou `#F2F1F6`; cards e balões brancos/`#F2F1F6` com texto navy | `#BE006E` só em forma ou detalhe |
| Roxo | Branco | Formas navy ou `#F2F1F6`; cards brancos/`#F2F1F6` | Sem rosa; acento é navy |
| Claro | Títulos navy, corpo `#2D3748` | Roxo e navy nas formas; blocos `#F2F1F6` sobre branco | `#BE006E` em pílula, tag, pontinho, círculo numerado, aspas, seta, CTA |

Nunca texto roxo sobre navy; nunca texto branco sobre claro.

**Composição:** um objeto por quadro (mockup de UI, círculo ou bloco),
margens laterais de 88px, logo pequena (40 a 56px), cards com raio de
28 a 36px e sombra suave. Sem fotos, sem travessão, sem traço decorativo
sob o título.

**Ícones de produto em card:** variante `-sober` do CDN (fundo embutido
`#F2F1F6`, detalhe `#BE006E`), só sobre card claro. Os templates já trazem
os ícones embutidos; para trocar, use
`https://cdn.jsdelivr.net/gh/GovHub-br/skills-assets@main/gov-hub/icons/<nome>-sober.svg`
(ver `icons-catalog.md`).

**Parceiros**, quando entrarem: Lab Livre e depois UnB; brancos sobre
navy e roxo, pretos sobre claro (`partners.md`).

## Texto

- O texto do briefing entra como descrição; a chamada curta é redigida a
  partir dele, não inventada.
- Texto corrido justificado só pelo espaçamento entre palavras
  (`hyphens: none; overflow-wrap: normal`). Se estourar, corte texto, não
  reduza fonte.
- Mantenha o número de linhas do template: a chamada da capa cabe em 2 ou
  3 linhas, títulos de conteúdo em 2, descrições de card em 2.
- Números dos templates são fictícios: troque sempre pelos reais.

## Exportação e conferência

Cada HTML vira um PNG `1080×1350`:

```bash
chrome --headless=new --window-size=1080,1350 --screenshot=01.png 01-capa-capa-chamada-gigante-navy.html
```

Com a Reddit Sans carregada (o HTML importa do Google Fonts; sem rede,
instale a fonte localmente). **Confira visualmente cada quadro** antes de
entregar: nada invadindo borda, rodapé ou outra forma.

## Derivar uma variação nova

Não edite os templates à mão. A galeria de trabalho
`post-templates-sobrio/fonte/fonte-completa-v3-a-v22.html` tem todas as
versões intermediárias e o código que as gera (listas de substituição por
quadro). Uma variação nova vira uma versão nova derivada por código, e só
depois é exportada para a pasta de templates.
