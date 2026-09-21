# govhub-diagramas — desenho da skill

Data: 2026-09-21 · Status: aprovado em conversa, aguardando plano de implementação

## Problema

As figuras de arquitetura e de modelo físico do 3º Relatório Parcial MinC
(págs. 31 e 41 de `relatorio-com-anexos-versao-final-revisada.pdf`) foram
feitas com a skill `govhub-fluxos` (claude.ai), mas em HTML/CSS capturado por
Chrome headless — não em SVG como a skill manda — e com a paleta
descontinuada (`#7A34F3`, `#5B21B6`, `#F97316`) e fonte Inter. Não existe no
repositório uma skill que (a) saiba a gramática de fluxos, (b) use a IDV
atual e (c) gere o PNG no Claude Code.

## Decisões

| Pergunta | Decisão |
|---|---|
| Ambiente | Claude Code. Skill versionada em `01-govhub/govhub-diagramas`, plugin `govhub-core`. |
| Famílias de diagrama | Arquitetura em blocos (Fig. 3), mapa de schemas/camadas (Fig. 8), fluxo de processo com raias, pipeline de dados. |
| Visual | IDV oficial (`#613EFF`, navy `#0A005A`, Reddit Sans). Sem Inter, sem Tailwind, sem hex descontinuado. |
| Marcas | Só Gov Hub. |
| Entrega | HTML (fonte editável, CSS inline) + PNG (largura base 1500 px, `deviceScaleFactor` 2). |
| Fontes de dados automáticas | Só dbt (`target/manifest.json`). Banco e Airflow ficam fora. |
| Relação com `govhub-fluxos` (claude.ai) | Esta skill absorve a gramática. A versão web pode ser substituída depois por um zip desta, sem `scripts/`. |

## Estrutura

```
01-govhub/govhub-diagramas/
├── SKILL.md
├── references/
│   ├── grammar-processo.md      # raias, decisão, instrumento, subprocesso (portado)
│   ├── grammar-dados.md         # política→dado e pipeline (portado)
│   ├── grammar-arquitetura.md   # blocos/zonas/pílulas/setas tipadas + mapa de schemas (novo)
│   ├── colors.md                # papel → token da IDV atual
│   └── diagram.css              # CSS base; tokens copiados de govhub-visual-identity/references/tokens.css
├── templates/
│   ├── arquitetura-blocos.html  # recriação da Fig. 3 com a IDV atual
│   ├── mapa-schemas.html        # recriação da Fig. 8
│   ├── fluxo-raias.html
│   └── pipeline-dados.html
└── scripts/
    ├── render.mjs               # HTML → PNG (Playwright)
    ├── dbt_lineage.py           # manifest.json → JSON de nós/arestas
    ├── package.json             # dependência: playwright
    └── setup.sh                 # npm install + npx playwright install --with-deps chromium
```

Os tokens são **copiados** para `diagram.css` (com comentário apontando a
origem), não importados por caminho relativo — caminhos entre skills não são
garantidos no plugin instalado. Cada template embute o CSS inline: um HTML
por diagrama, portável.

## Motor de render — `scripts/render.mjs`

```
node render.mjs <entrada.html> [saida.png] [--width 1500] [--scale 2] [--selector "#diagram"]
```

1. Playwright Chromium, viewport `{width, height: 100}`, `deviceScaleFactor: scale`.
2. Espera `networkidle` e `document.fonts.ready`; loga
   `document.fonts.check('700 16px "Reddit Sans"')` para acusar fallback.
3. `locator(selector).screenshot()` — altura vem do conteúdo. Se o seletor
   não existir, `fullPage: true`.
4. Fallback: se `playwright` não carregar, procura Chrome/Chromium no PATH e
   usa `--headless=new --screenshot --window-size=<width>,<altura>`; se
   nada existir, sai com código 2 imprimindo o comando de `setup.sh`.
5. Saída padrão: mesmo nome do HTML com `.png`, ao lado.

`setup.sh` roda uma vez; pode pedir sudo (dependências de sistema do
Chromium). Na máquina de origem faltam hoje `libnss3`, `libgbm` etc.

Fora de escopo: SVG, geração do HTML a partir de YAML/JSON, temas múltiplos.

## Extração de lineage — `scripts/dbt_lineage.py`

```
python3 dbt_lineage.py <target/manifest.json> [--group schema|layer]
```

Só stdlib. Lê `sources`, `nodes` (models, seeds, snapshots) e `depends_on`.
Saída JSON:

```json
{
  "groups": [{"name": "bronze", "nodes": [{"name": "salic_projetos", "kind": "source|model|seed", "materialization": "table", "description": "..."}]}],
  "edges": [["source.salic.projetos", "model.gold.cotas"]]
}
```

`--group schema` agrupa pelo schema físico (mapa de schemas); `--group layer`
agrupa pela camada inferida do path do modelo (`models/bronze/...`) ou do
prefixo do schema (pipeline). Se o manifest não existir, a skill orienta a
rodar `dbt parse`. O JSON é insumo para o Claude diagramar com julgamento —
não gera layout automaticamente.

## Tema — `colors.md` / `diagram.css`

| Papel | Token | Hex |
|---|---|---|
| Zona/ator principal, pílulas, setas de dados | `--primary-purple` | `#613EFF` |
| Título do diagrama, texto forte de marca | `--dark-navy` | `#0A005A` |
| Segundo ator/estágio | `--purple-700` | `#3F28A6` |
| Terceiro ator / camada intermediária | `--accent-magenta` | `#EF41FF` |
| Destaque pontual: pendente, governança, alerta LGPD | `--accent-pink` | `#F9006F` |
| Fundo de nota/callout quente | `--bg-peach` | `#FFE7E1` |
| Fundo de zona e de nó de saída | `--bg-subtle` / `rgba(97,62,255,.06)` | |
| Bordas sutis, tracejado de legado | `--border-soft` | `#E9DFFF` |
| Fora do escopo | cinza neutro | `#9CA3AF` |
| Texto | `--text-strong` / `--text-body` / `--text-muted` | `#202020` / `#2D3748` / `#666666` |

Camadas bronze/prata/ouro: opacidade crescente do roxo (`.12 → .3 → sólido`).
Nunca marrom/amarelo.

Vocabulário CSS fixo (os templates só usam estas classes):
`.diagram` (raiz, `width:1500px`) · `.title` `.subtitle` · `.zone` `.zone--dashed` ·
`.pill` (rótulo sobre a borda, contorno branco via `box-shadow`) ·
`.node` `.node--out` `.node--legacy` `.node--muted` · `.lane` · `.decision` ·
`.note` `.note--lgpd` · `.legend` · `.composition` ·
`.arrows` (svg overlay absoluto) com `<marker>` por tipo `exec`, `data`, `meta`, `gov`.

Tipografia: Reddit Sans via `@import` Google Fonts. Títulos e nomes de nó
700; descrições 400 em `--text-muted`; pílulas caixa alta 600 com
`letter-spacing`. Sem Oswald dentro do diagrama.

## Fluxo de trabalho no `SKILL.md`

Gatilhos: "desenha esse fluxo", "diagrama de arquitetura", "fluxograma",
"mapeia o processo", "raias por ator", "diagrama dos schemas", "fluxo
bronze/prata/ouro", "figura para o relatório", "como os dados chegam no…".
Diferencia de `mermaid-diagram-specialist` (Mermaid genérico, sem IDV) e de
`govhub-visual-identity` (tema, não gramática).

1. **Extrair a lógica da fonte.** Tabela fonte → método: manifest dbt →
   `dbt_lineage.py`; processo institucional → documento/ata lido pelo Claude,
   listado em texto (atores, etapas, decisões, sistemas, observações). Lacuna
   → perguntar, nunca inventar.
2. **Escolher a família** (tabela família → template + reference).
3. **Copiar o template** para o diretório de saída (padrão `./diagramas/`),
   renomear, editar conteúdo.
4. **Renderizar** com `render.mjs`; se falhar por setup, rodar `setup.sh`.
5. **Conferir o PNG** lendo a imagem: texto cortado, seta desalinhada, fonte
   fallback. Corrigir e re-renderizar.
6. **Entregar** HTML + PNG + legenda em texto para o usuário colar como
   "Figura N".

Checklist de qualidade: legenda sempre; largura 1500, altura livre; só cores
de `colors.md`; dado pessoal com `.note--lgpd`; máximo ~12 nós por diagrama,
acima disso dividir com nó de subprocesso.

## Verificação da skill

- Renderizar os 4 templates: PNG existe, largura 3000 px (scale 2).
- Log do render acusa `Reddit Sans` carregada.
- `grep -i "7a34f3\|f97316\|8b5cf6\|5b21b6\|inter" templates/ references/diagram.css` vazio
  (exceto ocorrências em comentários explicando o descontinuado).
- `dbt_lineage.py` contra um manifest de exemplo (fixture mínima em
  `scripts/fixtures/manifest.min.json`) produz grupos e arestas esperados.
- `arquitetura-blocos.html` e `mapa-schemas.html` reproduzem o conteúdo das
  Figs. 3 e 8 do relatório, com a IDV atual — comparação visual lado a lado.

## Pós-implementação

- Atualizar `.claude-plugin/marketplace.json` (govhub-core passa a 4 skills;
  contagem total) e `README.md`.
- Espelhar a mudança de paleta na `govhub-fluxos` do claude.ai quando for
  substituída pelo zip desta skill.
