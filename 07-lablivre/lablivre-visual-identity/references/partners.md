# Logo do Lab Livre e logos dos parceiros institucionais

A marca principal desta skill é o **Lab Livre**; os parceiros aparecem no
rodapé da capa (`print-cover.md`), no slide de encerramento (`slides.md`)
e no quadro de fechamento de carrossel (`social-posts.md`), sempre **ao
lado** da marca Lab Livre, nunca no lugar dela. Arquivos da marca em
`references/logo/`, dos parceiros em `references/logo/parceiros/`.

## Logo do Lab Livre: o que existe e o que falta

| Arquivo | O que é | Fundo |
|---|---|---|
| `lab-livre-blue.svg` | Assinatura horizontal, azul institucional `#080056` | claro (**padrão** em capa e slide) |
| `lab-livre-black.svg` | Assinatura horizontal, preta | claro, quando a paleta não for viável |
| `lab-livre-white.svg` | Assinatura horizontal, branca | escuro (azul profundo, roxo) |
| `borboleta-blue.svg` | Só o ícone (a folha/borboleta), azul | claro (**padrão** no rodapé de PDF) |
| `borboleta-black.svg` | Só o ícone, preto | claro |
| `borboleta-white.svg` | Só o ícone, branco | escuro |

Todos SVG (1514×377 a assinatura, 256×256 a borboleta), fundo transparente.

**Ainda não existem em SVG** (o usuário vai enviar; quando chegarem,
acrescente aqui e atualize `print-cover.md`, `slides.md` e
`social-posts.md`):

- versão **roxa** `#7023E8`, que o MIV aponta como aplicação preferencial;
  até lá, em fundo claro use `lab-livre-blue`;
- assinatura **vertical**;
- assinatura **tipográfica** isolada (só "Lab Livre"); se precisar, recrie
  o texto em Reddit Sans Black na paleta, sem a borboleta;
- versão **peach** `#FFE7E1` para fundo escuro colorido.

O plugin `anthropic-skills` tem a versão roxa em PNG
(`lablivre-roxo.png`); não a copie para cá, SVG é o formato desta skill.

## Convenção de nome

```
<parceiro>_<positivo|negativo>[-defeso].<svg|png>
```

- `positivo`: texto preto, para **fundo claro** (branco, `--bg-light`,
  pêssego).
- `negativo`: texto branco, para **fundo escuro** (navy, roxo). O símbolo
  colorido (bandeira verde/amarelo/azul nos ministérios) é o mesmo nas duas
  versões; só o texto muda.
- `-defeso`: versão do **período de defeso eleitoral**, com a marca
  genérica do Governo Federal (sem slogan nem identidade do governo em
  exercício). Ver "Ciclo eleitoral" abaixo.

UnB e Gov Hub vieram com nomes próprios, pela cor e não pelo fundo
(`-light`/`-dark`/`-colourfull`, mais `-outlined`/`-fulfilled` e
`-vertical` na UnB; `-navy`/`-white`/`-black` no Gov Hub). A tabela abaixo
já traduz cada um para o fundo certo.

## UnB sempre; Gov Hub quando o documento é de projeto Gov Hub

O Lab Livre é um laboratório **dentro da UnB**: toda peça do Lab Livre leva
a UnB na linha de parceiros, sem exceção. O Gov Hub é um projeto do Lab
Livre: entra como parceiro só em peça sobre o Gov Hub (relatório de
entrega, apresentação do projeto). Na skill do Gov Hub a relação é a
inversa (Gov Hub é a marca, Lab Livre e UnB são parceiros).

## Catálogo

| Parceiro | Fundo claro (`positivo`) | Fundo escuro (`negativo`) | Formato |
|---|---|---|---|
| UnB horizontal, **outlined** (padrão) | `unb-dark-outlined.svg` | `unb-light-outlined.svg` | SVG 1172×303 |
| UnB horizontal, fulfilled (símbolo cheio) | `unb-dark-fulfilled.svg` | `unb-light-fulfilled.svg` | SVG 1174×301 |
| UnB vertical, outlined | `unb-dark-vertical-outlined.svg` | `unb-light-vertical-outlined.svg` | SVG 605×559 |
| UnB colorida (azul `#133E79` + verde `#008940`) | `unb-colourfull-fulfilled.svg` (horizontal) / `unb-colourfull-vertical.svg` | não há | SVG |
| Gov Hub (logomarca horizontal) | `govhub-black.svg` (preferir, mesma cor da UnB) ou `govhub-navy.svg` | `govhub-white.svg` | SVG 1104×257 |
| Ipea | `ipea_positivo.png` (1028×200) | **não há** | PNG |
| MGI — Ministério da Gestão e da Inovação em Serviços Públicos | `mgi_positivo-defeso.svg` | `mgi_negativo-defeso.svg` | SVG 380×119 |
| MIR — Ministério da Integração e do Desenvolvimento Regional | `mir_positivo-defeso.svg` | `mir_negativo-defeso.svg` | SVG 325×118 |
| Ministério das Cidades | `cidades_positivo-defeso.svg` | `cidades_negativo-defeso.svg` | SVG 325×118 |
| Ministério da Cultura | `cultura_positivo-defeso.svg` | `cultura_negativo-defeso.svg` | SVG 325×118 |

**UnB sempre na versão `outlined`** (símbolo em contorno): a `fulfilled`
(símbolo cheio) foi reprovada na skill do Gov Hub (2026-09-17) por ficar
pesada ao lado da Lab Livre; fica para quando o usuário pedir. Os
parceiros vão **na mesma cor entre si**, preta em fundo claro
(`unb-dark-outlined` + `govhub-black`), branca em fundo escuro
(`unb-light-outlined` + `govhub-white`). A marca Lab Livre, que fica em
outro lugar da peça (topo da capa, rodapé), vai em `blue` no claro e
`white` no escuro. A UnB colorida (`unb-colourfull-*`) foi reprovada nos
posts do Gov Hub ao lado da paleta; só a pedido. As versões `vertical` são
para espaços altos e estreitos (coluna lateral, selo), nunca na linha de
parceiros. O navy do Gov Hub (`#0A005A`) e o azul profundo do Lab Livre
(`#080056`) são quase iguais, mas cada logo fica na cor da própria marca;
não recolorir uma pela outra.

**Lacuna conhecida:** Ipea não tem versão para fundo escuro. Se a peça
exigir a combinação que não existe, **pergunte ao usuário** pelo arquivo em
vez de recolorir, inverter ou aplicar filtro CSS na logo de um parceiro.

## Quem entra em cada peça

- **Sempre:** UnB, em toda capa de PDF, slide de encerramento e fechamento
  de carrossel (regra fixada em `print-cover.md`). Em fundo escuro
  `unb-light-outlined.svg`; em fundo claro `unb-dark-outlined.svg`.
- **Gov Hub:** quando a peça é de projeto Gov Hub. Entra depois da UnB.
- **Ipea:** só quando o documento é de um projeto/frente com o Ipea. Entra
  depois do Gov Hub.
- **Ministérios:** só o ministério do projeto/frente a que o documento
  pertence (ex.: relatório de diagnóstico do MGI leva a logo do MGI). Entra
  por último. Nunca coloque todos os ministérios juntos "por garantia".
- Ordem final: `UnB → Gov Hub (se houver) → Ipea (se houver) → Ministério (se houver)`.
- Na dúvida sobre qual parceiro entra, pergunte.

Todas com a mesma altura na linha (34 px na capa A4, 60 px no post
1080×1350), `width: auto`, alinhadas pelo centro vertical. As logos dos
ministérios são mais largas que as demais: se a linha não couber, reduza a
altura de todas por igual, não só a do ministério.

## Ciclo eleitoral

As logos dos ministérios mudam com o governo; as do Lab Livre, UnB, Gov Hub
e Ipea não.

1. **Período de defeso eleitoral** (hoje: eleições de 2026): use só os
   arquivos `-defeso`. É o estado atual da pasta.
2. **Novo governo definido** (a partir da posse, com a nova marca do
   Governo Federal publicada): o usuário adiciona
   `<ministerio>_positivo.svg` e `<ministerio>_negativo.svg` **sem sufixo**.
   A partir daí esses são os atuais; os `-defeso` ficam na pasta, mas não
   são usados. Ministérios podem ser criados, fundidos ou renomeados: o
   catálogo acima precisa ser revisado nesse momento, não só os arquivos.
3. **Próximo defeso** (eleições seguintes): voltam a valer os `-defeso`.

Regra prática para escolher: se existe `<ministerio>_<versão>.svg` sem
sufixo, use-o; se não existe, use o `-defeso`. Se houver dúvida sobre em
qual período estamos, pergunte ao usuário antes de gerar a peça.
