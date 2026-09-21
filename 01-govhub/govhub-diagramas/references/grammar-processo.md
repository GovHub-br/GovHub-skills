# Fluxo de processo (raias por ator)

Use esta gramática quando o fluxo representa um **rito ou processo de
trabalho** com mais de um ator: um processo de compras e contratações, um rito
de concessão de bolsa, um processo de habilitação, um fluxo de aprovação
interna. É a mesma lógica do fluxo de compras públicas do MGI usado como
referência para esta skill: raias por ator, início/fim marcados, decisões
explícitas, instrumentos e sistemas etiquetados, observações amarradas às
etapas certas, e uma cadeia de referência legal ao final.

## Layout: raias (swimlanes)

- Uma raia por ator responsável (ex.: Fornecedor, Órgão, Comitê, Sistema). Dê
  um título curto e visível para cada raia.
- Organize as raias na ordem em que o processo normalmente as visita primeiro
  (quem inicia o processo fica na raia mais acima ou mais à esquerda).
- Um mesmo ator pode aparecer em mais de um bloco de raia se o processo volta
  a ele depois de outra etapa (como no exemplo do MGI, em que "Fornecedor"
  aparece no início do registro cadastral e depois de novo na execução
  contratual). Isso é normal e não precisa ser evitado, mas deixe claro pela
  proximidade visual e pela cor que é o mesmo ator.
- Etapas fluem majoritariamente da esquerda para a direita dentro da raia, com
  setas descendo ou subindo entre raias quando o processo muda de
  responsável.

## Taxonomia de nós

| Nó | Forma | Quando usar |
|---|---|---|
| **Início (por ator)** | Círculo preenchido, com rótulo "Início" e o nome do ator | Marca onde aquele ator entra no processo. Cor específica do ator (ver `colors.md`). |
| **Fim (por ator)** | Círculo preenchido com uma etiqueta de status ao lado (ex.: "Concluído", "Aprovado") | Marca onde aquele ator sai do processo com sucesso. Sempre que possível, mostre o resultado do fim (aprovado, homologado, pago). |
| **Etapa/processo** | Retângulo de cantos arredondados, preenchimento sólido na cor do ator responsável, texto branco em negrito, curto | A ação concreta de uma etapa. Rótulo em verbo + objeto (ex.: "Elaborar o Termo de Referência"), nunca um jargão sozinho sem explicação. |
| **Decisão** | Losango | Todo ponto em que o processo se ramifica de verdade (ex.: "Existe ARP compatível com a demanda?"). Rotule cada seta de saída com a condição (Sim/Não, ou o valor que define o caminho). |
| **Instrumento/Sistema** | Etiqueta pequena (pílula ou retângulo fino), preenchimento claro, anexada abaixo ou ao lado da etapa que o usa | Nome do sistema ou documento oficial envolvido naquela etapa (ex.: "PNCP", "SICAF", "TR digital PNCP", "Extrato PCP"). Nunca invente o nome do sistema; use exatamente o que está na fonte. |
| **Observação** | Caixa leve, sem preenchimento forte, ligada à etapa por uma linha fina ou pontilhada, ícone opcional de "i" | Contexto, prazo, base normativa ou regra de exceção que não cabe dentro do rótulo da etapa (ex.: "Regulamentado pela Instrução Normativa SEGES nº 81/2022"). |
| **Referência a subprocesso** | Forma com borda tracejada (retângulo de cantos bem arredondados ou hexágono), com um pequeno ícone de link | Indica que aquele ponto do processo continua em outro diagrama detalhado, para não sobrecarregar o fluxo principal (ex.: "Definição dos itens de compra/contratação", detalhado num diagrama à parte). |
| **Etapa fora do escopo** | Mesmo formato de etapa, mas em cinza neutro | Uma etapa que existe no processo real mas não é o foco do mapeamento atual (ex.: um sistema legado que só é citado, não detalhado). |
| **Caminhos alternativos de um mesmo processo** | Cor diferente por caminho (ex.: "contratação direta" vs "licitação"), mantendo a mesma forma de etapa | Quando uma decisão cedo no processo cria dois caminhos estruturalmente diferentes até convergirem de novo. Use a legenda para explicar a diferença de cor. |

## Cadeia de referência legal/normativa (rodapé)

Quando o processo tiver uma base jurídica relevante (leis, decretos, comitês
gestores, estratégias, planos de ação), monte uma cadeia horizontal separada
na parte de baixo do diagrama, com uma caixa por norma/instância, conectadas
por setas simples, e uma legenda curta abaixo de cada caixa explicando o que
ela é em uma frase (ex.: "Comitê Gestor da Rede Nacional de Contratações
Públicas: responsável pela gestão do PNCP, composto por representantes da
União, estados, DF e municípios"). Essa cadeia fica visualmente separada do
fluxo operacional acima, geralmente com uma cor mais escura e neutra, porque
ela é o "pano de fundo legal", não uma etapa que alguém executa.

## Legenda obrigatória

Monte sempre uma legenda no canto superior esquerdo (ou como painel dedicado
antes do fluxo) cobrindo, no mínimo:
- Início e fim, por ator (uma linha por ator na legenda).
- Etapa realizada por cada ator (a cor de preenchimento de cada um).
- Elemento de decisão.
- Referência a subprocesso.
- Instrumento/Sistema (mostre o formato da etiqueta).
- Observação (mostre o formato da nota).
- Etapas fora do escopo.
- Caminhos alternativos, se o diagrama tiver mais de um.

## Checklist antes de finalizar

- Toda etapa tem um ator responsável claro (a cor da caixa não deixa dúvida).
- Toda decisão tem as duas (ou mais) saídas rotuladas.
- Todo sistema ou documento citado no texto de origem aparece como etiqueta de
  instrumento, não escondido dentro do rótulo da etapa.
- Toda observação da fonte original (prazo, norma, exceção) está representada
  como nota, não perdida.
- A legenda existe e cobre todos os tipos de nó usados.
- Nenhuma etapa foi inventada; nenhuma etapa da fonte foi esquecida.

## Como cada nó vira HTML (template `fluxo-raias.html`)

| Nó | Marcação |
|---|---|
| Raia | `<div class="lane"><div class="lane-head">Ator</div><div class="lane-body">…</div></div>` dentro de `<div class="lanes">` |
| Início / Fim | `<div class="dot" id="..."><span>Início</span></div>` / `<div class="dot dot--end" id="..."><span>Aprovado</span></div>` |
| Etapa | `<div class="node node--fill" id="..."><h3>Verbo + objeto</h3></div>` (cor do ator vem da raia: use `node--fill` na raia 1, `style="background:var(--purple-700);border-color:var(--purple-700)"` na 2, `var(--accent-magenta)` na 3) |
| Decisão | `<div class="decision" id="...">Pergunta?</div>`; as saídas são duas setas com `label` "Sim"/"Não" |
| Instrumento/Sistema | `<span class="tag">PNCP</span>` dentro do nó |
| Observação | `<div class="note note--plain"><strong>Prazo:</strong> 10 dias úteis</div>` |
| Subprocesso | `<div class="node node--legacy" id="..."><h3>Nome</h3><p>ver diagrama X</p></div>` |
| Fora do escopo | `<div class="node node--muted">…</div>` |
| Posição na raia | `style="grid-column: N"` (7 colunas de 170 px por padrão) |
| Setas | JSON em `#arrows`, `type: "flow"`; entre raias use `fromSide`/`toSide` explícitos |
