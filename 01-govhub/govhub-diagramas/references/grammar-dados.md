# Fluxo de dados / arquitetura de informação

Use esta gramática quando o fluxo representa **como uma política gera dado**,
não como um processo é executado por atores. O eixo organizador aqui é o
estágio do ciclo de vida do dado, não quem faz o quê. Cobre dois casos comuns
no GovHub:

1. **Fluxo da política ao dado**: política → instrumento → sistema, a cadeia
   técnica completa por trás do modelo dos três elos usado em comunicação
   (a versão simplificada para divulgação é um segundo diagrama, feito depois
   deste), mas aqui com todo o detalhe técnico que o público externo não
   precisa ver.
2. **Arquitetura de pipeline de dados**: como um dado bruto de uma fonte vira
   informação confiável para consumo, passando por ingestão, camadas de
   qualidade e, no fim, um painel, relatório ou API (o tipo de fluxo que
   documenta o Airflow do GovHub-MCid, o cruzamento entre SFTP e dump de
   dados brutos, ou a construção de uma base "gold" como as usadas nos
   relatórios de conjuntura habitacional).

## Layout: estágios, não raias

Organize o diagrama da esquerda para a direita (ou de cima para baixo, se o
número de estágios for grande) seguindo o ciclo de vida do dado. Não crie
raias por ator aqui, a menos que o pedido combine as duas famílias (nesse
caso, prefira dois diagramas separados e ligados por uma referência de
subprocesso, como orientado no SKILL.md principal).

## Taxonomia de nós — fluxo da política ao dado

| Nó | Forma | Quando usar |
|---|---|---|
| **Política** | Retângulo largo, cor mais escura da rampa | O programa, plano ou objetivo definido no planejamento (PPA, LOA, programa específico do órgão). |
| **Instrumento** | Retângulo com cor intermediária da rampa, ligado à política por seta | O mecanismo jurídico/administrativo que executa a política (TED, convênio, termo de fomento, emenda parlamentar). Etiquete com o nome real do instrumento, nunca genérico. |
| **Sistema/Dado** | Forma de cilindro (banco de dados) ou retângulo com barra superior, cor mais clara/saturada da rampa | O sistema estruturante onde o registro fica (SIAFI, SIOP, TransfereGov, PNCP, Tesouro Gerencial). |
| **Decisão de qualidade** | Losango | Ponto em que o dado é validado, conciliado ou passa por uma regra de negócio antes de seguir (ex.: "bate com o valor do plano de ação?"). |
| **Observação/nota legal** | Caixa leve ligada por linha fina | Base normativa daquele instrumento ou sistema, ou uma ressalva técnica (ex.: "nem toda NE de TED contém a palavra TED na descrição, por isso o cruzamento usa múltiplos critérios"). |

## Taxonomia de nós — arquitetura de pipeline

| Nó | Forma | Quando usar |
|---|---|---|
| **Fonte de dados** | Cilindro ou retângulo com ícone de banco de dados | Sistema de origem externo ou planilha manual (SFTP de um parceiro, export de um sistema legado, planilha do Excel enviada por e-mail). |
| **Ingestão/ETL** | Retângulo de processo com um ícone de engrenagem ou seta circular | Uma etapa de coleta, transformação ou orquestração (uma DAG do Airflow, um script de tratamento). Nomeie a ferramenta real quando souber (Airflow, dbt, script Python). |
| **Camada de dado** | Blocos empilhados ou lado a lado, em progressão de saturação da mesma cor (mais claro = mais bruto, mais saturado = mais tratado) | Represente os estágios de qualidade do dado (bruto/staging/curado, ou bronze/prata/ouro, conforme a nomenclatura real do projeto — confira nos nomes dos arquivos e na documentação técnica antes de escolher o termo). |
| **Validação/qualidade** | Losango | Regra de qualidade que barra ou libera a passagem do dado para a próxima camada. |
| **Consumo/saída** | Retângulo com borda dupla ou ícone de gráfico/painel | O destino final: painel, relatório de conjuntura, API, planilha de entrega. |
| **Observação** | Igual à do fluxo de processo | Detalhe técnico, frequência de atualização, ou ressalva de qualidade dos dados. |

## Camadas de dado: nomenclatura correta

Antes de rotular uma camada como "bronze", "prata" ou "ouro" (nomenclatura de
arquitetura medalhão) ou como "bruto", "tratado", "curado", confirme qual
convenção o projeto realmente usa (aparece nos nomes dos arquivos entregues,
ex.: `gold_financiamentos_imobiliarios`, ou na documentação técnica do
pipeline). Não troque a nomenclatura real do projeto por um termo genérico de
livro-texto. Se o público do diagrama for leigo, adicione uma observação
explicando em uma frase o que aquela camada significa na prática (ex.: "gold =
dado já pronto para entrar direto num relatório ou painel").

## Sinalização de dado pessoal (LGPD)

Sempre que uma fonte, uma camada ou uma saída do fluxo contiver dado pessoal
(CPF, nome de bolsista, dado de beneficiário), adicione uma nota de observação
destacada (pode usar a cor de alerta da rampa, ver `colors.md`) marcando
o ponto exato de anonimização ou de tratamento LGPD. Isso não é opcional: o
próprio projeto já trata esse cuidado como prática padrão (bases marcadas como
"ANONIMIZADA_LGPD"), e o diagrama deve deixar isso visível para quem for
auditar o fluxo depois.

## Nível de detalhe: técnico primeiro, simplificação depois

Este fluxo deve ser **completo e correto**, mesmo que fique denso. Se o pedido
for para um material de divulgação externa, construa este fluxo técnico
primeiro (ele garante que nada da lógica real se perdeu) e depois faça um
segundo diagrama simplificado (três elos: política → instrumento → dado),
nunca tente fazer as duas coisas dentro do mesmo diagrama.

## Checklist antes de finalizar

- Cada seta representa uma transformação ou transferência real do dado, não
  uma suposição.
- O nome de cada sistema, instrumento e camada é o nome real usado no projeto,
  não um termo genérico.
- Pontos de validação/qualidade citados na fonte aparecem como decisão, não
  foram simplificados para uma seta direta.
- Dado pessoal está sinalizado, se existir no fluxo.
- Se o fluxo cruza dados de mais de uma fonte (como o cruzamento SFTP × dump
  de dados brutos), o ponto de cruzamento está explícito como uma etapa
  própria, não implícito na seta.

## Como cada nó vira HTML (template `pipeline-dados.html`)

| Nó | Marcação |
|---|---|
| Estágio do ciclo de vida | `<section class="zone"><span class="pill">Fontes</span>…</section>` — um por coluna, esquerda → direita |
| Fonte de dados | `<div class="node" id="..."><h3>SALIC</h3><p>Postgres · réplica</p><span class="tag">SFTP</span></div>` |
| Ingestão/ETL | `<div class="node node--fill" id="..."><h3>Airflow</h3><p>DAG …</p></div>` |
| Camada de dado | `<div class="layer layer--1|--2|--3" id="..."><h3>bronze</h3><p>…</p></div>` |
| Validação/qualidade | `<div class="decision" id="...">testes dbt passaram?</div>` |
| Consumo/saída | `<div class="node node--out" id="..."><h3>Superset</h3></div>` |
| Observação técnica | `<div class="note note--plain">…</div>` |
| Dado pessoal | `<div class="note note--lgpd">CPF anonimizado na silver</div>` |
| Setas | JSON em `#arrows`; `data` para transferência, `exec` para orquestração, `flow` para leitura |
| Lineage automático | `python3 scripts/dbt_lineage.py target/manifest.json --group layer` |
