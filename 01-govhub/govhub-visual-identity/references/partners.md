# Logos dos parceiros institucionais

Arquivos em `references/logo/parceiros/`. Aparecem no rodapé da capa
(`print-cover.md`), no slide de encerramento (`slides.md`) e no quadro de
fechamento de carrossel (`social-posts.md`), sempre **ao lado** da marca Gov
Hub, nunca no lugar dela.

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

Lab Livre e UnB vieram com nomes próprios, pela cor e não pelo fundo
(`-white`/`-black`/`-blue`, `-light`/`-dark`/`-colourfull`). A tabela abaixo
já traduz cada um para o fundo certo.

## Lab Livre e UnB: sempre juntos, nessa ordem

O Lab Livre é o "dono" dos projetos Gov Hub e é um laboratório **dentro da
UnB**; por isso as duas logos aparecem sempre juntas, Lab Livre primeiro,
UnB logo depois. Nunca uma sem a outra.

## Catálogo

| Parceiro | Fundo claro (`positivo`) | Fundo escuro (`negativo`) | Formato |
|---|---|---|---|
| Lab Livre (logo completa) | `lab-livre-blue.svg` (azul institucional `#080056`, preferir) ou `lab-livre-black.svg` | `lab-livre-white.svg` | SVG 1514×377 |
| Lab Livre (só a borboleta, ícone) | `borboleta-blue.svg` (preferir) ou `borboleta-black.svg` | `borboleta-white.svg` | SVG 256×256 |
| UnB | `unb-colourfull.svg` (azul `#003F7A` + verde `#008137`, preferir) ou `unb-dark.svg` (preto) | `unb-light.svg` | SVG 1174×301 |
| Ipea | `ipea_positivo.png` (1028×200) | **não há** | PNG |
| MGI — Ministério da Gestão e da Inovação em Serviços Públicos | `mgi_positivo-defeso.svg` | `mgi_negativo-defeso.svg` | SVG 380×119 |
| MIR — Ministério da Integração e do Desenvolvimento Regional | `mir_positivo-defeso.svg` | `mir_negativo-defeso.svg` | SVG 325×118 |
| Ministério das Cidades | `cidades_positivo-defeso.svg` | `cidades_negativo-defeso.svg` | SVG 325×118 |
| Ministério da Cultura | `cultura_positivo-defeso.svg` | `cultura_negativo-defeso.svg` | SVG 325×118 |

A **borboleta** é só o ícone do Lab Livre: use-a apenas onde a logo
completa não cabe (chip, favicon, rodapé muito baixo), e mesmo assim com a
UnB ao lado. Em capa, encerramento e fechamento vai a logo completa.

Em fundo claro (pêssego, magenta, branco), use `lab-livre-blue` +
`unb-dark`: a UnB colorida (`unb-colourfull`) foi testada nos posts em
2026-09-17 e reprovada pelo usuário ao lado da paleta Gov Hub; fica só
para quando ele pedir. `lab-livre-black` é para impressão monocromática. O azul do Lab Livre
(`#080056`) é da marca dele, não é o navy do Gov Hub (`#0A005A`); não
recolorir um pelo outro.

**Lacuna conhecida:** Ipea não tem versão para fundo escuro. Se a peça
exigir a combinação que não existe, **pergunte ao usuário** pelo arquivo em vez de recolorir, inverter
ou aplicar filtro CSS na logo de um parceiro.

## Quem entra em cada peça

- **Sempre:** Lab Livre e UnB, nessa ordem, em toda capa de PDF, slide de
  encerramento e fechamento de carrossel (regra já fixada em
  `print-cover.md`). Em fundo escuro: `lab-livre-white.svg` +
  `unb-light.svg`; em fundo claro: `lab-livre-blue.svg` +
  `unb-dark.svg`.
- **Ipea:** só quando o documento é de um projeto/frente com o Ipea. Entra
  depois da UnB.
- **Ministérios:** só o ministério do projeto/frente a que o documento
  pertence (ex.: relatório de diagnóstico do MGI leva a logo do MGI). Entra
  por último, depois dos parceiros acadêmicos. Nunca coloque todos os
  ministérios juntos "por garantia".
- Ordem final: `Lab Livre → UnB → Ipea (se houver) → Ministério (se houver)`.
- Na dúvida sobre qual ministério (ou se algum) entra, pergunte.

Todas com a mesma altura na linha (22 px na capa A4, 60 px no post
1080×1350), `width: auto`, alinhadas pelo centro vertical. As logos dos
ministérios são mais largas que as demais: se a linha não couber, reduza a
altura de todas por igual, não só a do ministério.

## Ciclo eleitoral

As logos dos ministérios mudam com o governo; as do Lab Livre, UnB e Ipea
não.

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
