---
name: govhub-post-especial
description: >-
  Use quando alguém pedir para montar, gerar, diagramar ou corrigir uma
  publicação do site gov-hub.io com layout próprio em HTML (a "página
  especial" do painel /admin/, o Sveltia CMS): relato de evento, datathon,
  oficina, lançamento, resultado de pesquisa com números em destaque, cards,
  galeria de fotos. Também quando um post desses foi ao ar com imagem
  quebrada, bloco branco vazio, fundo branco sobre cinza, código aparecendo
  como texto ou o estilo bagunçando o site. Dispara com: "post especial",
  "página especial", "HTML do post", "post do evento para o site",
  "publicação com layout", "colar no Sveltia", "post do gov-hub.io".
---

# Página especial do gov-hub.io

O site (MkDocs) já desenha o cabeçalho, o título, a data e o rodapé do post. O
HTML que você gera é **só o miolo**: a pessoa cola no campo Texto do painel, com
a opção **Página especial (largura total)** marcada, e ele ocupa a página toda,
em fundo branco, logo abaixo do título.

Quem pede costuma ser da comunicação, sem conhecer programação: explique os
passos do painel em palavras simples e entregue o HTML pronto, validado.

## Antes de gerar

Peça, e não invente:

1. **O texto** do post (ou o material de onde tirar).
2. **As fotos já enviadas pelo painel e os nomes que elas ganharam.** O painel
   converte tudo em `.webp`, põe o nome em minúsculas sem acento e acrescenta
   `-1` quando o nome já existe (`VEC_09521.JPG` → `vec-09521-1.webp`). Se as
   fotos ainda não subiram, oriente: no post, no campo **Fotos da página
   especial**, selecionar ou arrastar todas de uma vez, salvar e copiar a lista
   que o campo mostra (`images/oficina-mir-01.webp` vira
   `/blog/images/oficina-mir-01.webp` no HTML). Não suba pelo botão de imagem do
   editor de texto: a foto entra no corpo do post, que o HTML substitui. Peça
   nomes descritivos antes do envio (`oficina-mir-01.jpg`), que ficam fáceis de
   achar depois.
3. **O que aparece em cada foto**, para o texto alternativo (`alt`), que leitores de
   tela leem em voz alta. Se você consegue ver as fotos anexadas, descreva-as você
   mesmo. Se não, peça uma frase por foto; sem ela, use o nome do evento com o
   número da foto e avise a pessoa de que as descrições ficaram genéricas.

## Contrato da saída

O arquivo é exatamente isto, nesta ordem:

```html
<style>
.ghx{container-type:inline-size; /* tokens e reset */}
.ghx .ghx-topo{...}
/* toda regra começa por .ghx, inclusive dentro de @media e @container */
</style>
<div class="ghx">
  <!-- seções: ghx-topo, ghx-numeros, ghx-sec, ghx-galeria... -->
  <img src="/blog/images/oficina-mir-01.webp" alt="o que se vê na foto">
</div>
```

- **Classes e ids com o prefixo `ghx-`.** O site e o Bootstrap já usam `hero`,
  `band`, `wrap`, `lead`, `row`, `card`, `container`, e aplicam o estilo deles
  em quem usar esses nomes.
- **Imagens com caminho começando por `/blog/images/`**, o nome exato do painel e
  `alt` descrevendo a foto. Link que abre a foto grande: o mesmo caminho no
  `href`, com `target="_blank" rel="noopener"`.
- **Sem** `<html>`, `<head>`, `<body>`, `<script>`, `<link>`, cabeçalho, rodapé ou
  logo do Gov Hub (o site já tem).
- **Medidas relativas à largura do post** (`cqw`, com `container-type` no
  `.ghx`), não à da tela (`vw`).
- **Sem `@import` de fonte:** a Reddit Sans já vem do site.

## Visual

Parta de [references/exemplo-datathon.html](references/exemplo-datathon.html),
um post real que funciona no site, já com a identidade visual do Gov Hub. Ele
traz os blocos que costumam servir:

| Bloco | Classes no exemplo |
|---|---|
| Abertura: etiqueta, frase, pílulas, foto grande | `ghx-hero`, `ghx-eyebrow`, `ghx-lead`, `ghx-pill`, `ghx-hero-photo` |
| Faixa azul de números | `ghx-stats`, `ghx-stat` |
| Texto ao lado de foto | `ghx-sec`, `ghx-two`, `ghx-prose`, `ghx-photo` |
| Etapas numeradas em cards | `ghx-steps`, `ghx-step` |
| Grade de cards com etiqueta | `ghx-eixos`, `ghx-eixo` |
| Faixa azul de destaque | `ghx-bandeira`, `ghx-flag` |
| Galeria de fotos | `ghx-gallery` (`ghx-s2`, `ghx-s3`, `ghx-s4` = largura na grade) |
| Fechamento | `ghx-rede`, `ghx-gh` |

Ajuste as grades ao conteúdo: `ghx-steps` e `ghx-eixos` vêm com 2 colunas no
exemplo; com 3 ou 4 itens, use o mesmo número de colunas (e 1 coluna no celular,
como nas regras `@container` do exemplo).

Regras de cor que o exemplo já segue (para cores e formas novas, use a skill
`govhub-visual-identity`):

- **A primeira seção tem fundo cinza-claro `#F2F1F6`**: o cabeçalho do título,
  logo acima, é branco. Pílulas e cartões sobre o cinza ficam brancos.
- Depois, as seções alternam branco, cinza-claro e azul-marinho `#0A005A`.
- Texto sobre o azul é branco (legenda inclusive), nunca cinza ou roxo.

## Validar e entregar

1. Rode o validador, com a lista de fotos do painel salva em `fotos.txt`:

   ```bash
   python3 scripts/validar_post.py post.html --fotos fotos.txt
   ```

   Só entregue com ✅. Sem como rodar Python, confira à mão cada item do
   contrato acima.
2. Entregue o HTML num bloco de código (ou arquivo) e os passos do painel:
   1. Abrir o post, preencher título, data, tipo, resumo e imagem do card.
   2. Marcar **Página especial (largura total)**.
   3. No campo Texto, trocar o editor para o **modo markdown** e colar o HTML
      inteiro. No modo visual, o editor estraga o código sem avisar.
   4. Salvar, pré-visualizar e conferir fotos e layout; depois Pronto e Publicar.
   5. Abrir a página publicada no celular e no computador.

## Erros que já aconteceram

| Sintoma no site | Causa | Correção |
|---|---|---|
| Fotos quebradas | `src="images/..."` ou nome diferente do painel | `/blog/images/` + nome exato da lista |
| Página dentro da página, logo quebrada | HTML com `<html>`, cabeçalho, rodapé | Só o miolo |
| Bloco branco vazio no topo | Classe `hero`/`band` recebe o padding do site | Prefixo `ghx-` |
| Cartão branco sobre fundo cinza | Página especial não marcada | Marcar a opção no painel |
| Foto aparece como texto `![...](...)` | Imagem inserida pelo botão do editor no meio do HTML | Toda foto como `<img>` |
| `\_blank`, `\*` no código | Colado no modo visual | Colar no modo markdown |
| Legenda ilegível | Texto cinza sobre a faixa azul | Branco sobre azul |
