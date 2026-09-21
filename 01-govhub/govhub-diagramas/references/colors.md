# Cores dos diagramas — papel → token da IDV

Os tokens vivem em `diagram.css` (espelho de
`govhub-visual-identity/references/tokens.css`). Use **só** estes valores.
O roxo/laranja antigo (`#7A34F3`, `#5B21B6`, `#F97316`) e a paleta Tailwind
(`#8B5CF6`) foram descontinuados — figuras antigas que os usam estão fora da
identidade.

## Tabela papel → token

| Papel no diagrama | Token | Hex | Classe |
|---|---|---|---|
| Zona/ator principal, pílulas, setas de leitura de dados | `--primary-purple` | `#613EFF` | `.zone`, `.pill`, `.a-flow` |
| Título do diagrama; setas de execução e transferência | `--dark-navy` | `#0A005A` | `.title`, `.a-exec`, `.a-data` |
| Segundo ator/estágio; texto roxo sobre fundo claro | `--purple-700` | `#3F28A6` | `.lane:nth-of-type(2)`, `.tag`, rótulos de seta |
| Terceiro ator / camada intermediária | `--accent-magenta` | `#EF41FF` | `.lane:nth-of-type(3)`, `.pill--magenta` |
| Destaque pontual: pendente, governança, alerta LGPD | `--accent-pink` | `#F9006F` | `.pill--pink`, `.node--pink`, `.note`, `.a-gov` |
| Fundo de nota/callout quente e de decisão | `--bg-peach` | `#FFE7E1` | `.note`, `.decision` |
| Fundo de zona | `--bg-subtle` | `#F8F9FA` | `.zone` |
| Nó de saída / camada bruta | `--purple-tint-2` | `rgba(97,62,255,.12)` | `.node--out`, `.layer--1` |
| Camada intermediária | `--purple-tint-3` | `rgba(97,62,255,.30)` | `.layer--2` |
| Camada curada / pronta | `--primary-purple` | `#613EFF` | `.layer--3` |
| Bordas sutis, tracejado de legado, etiquetas | `--border-soft` | `#E9DFFF` | `.legend`, `.tag`, `.note--plain` |
| Fora do escopo | `--gray-out` | `#9CA3AF` | `.node--muted` |
| Texto forte / corpo / secundário | `--text-strong` / `--text-body` / `--text-muted` | `#202020` / `#2D3748` / `#666666` | `h3`, `body`, `p` |

## Regras de distribuição

- **Cada ator ou estágio recebe uma cor fixa** em todos os seus nós. Ordem de
  atribuição, do mais estrutural ao mais operacional: `--primary-purple` →
  `--purple-700` → `--accent-magenta` → `--dark-navy`. Quatro atores é o
  máximo confortável; acima disso, divida o diagrama.
- **Pink é só alerta/destaque** (pendente, governança, LGPD). Nunca como cor
  de ator.
- **Camadas bronze/prata/ouro**: progressão de saturação do roxo
  (`.layer--1` → `.layer--2` → `.layer--3`). Nunca marrom, amarelo ou dourado.
- **Instrumento/sistema** (`.tag`): fundo `--border-soft`, texto `--purple-700`.
- **Observação** (`.note--plain`): fundo neutro, nunca saturado. `.note`
  (peach + pink) só para status/alerta; `.note--lgpd` para dado pessoal.
- **Fora do escopo**: cinza, nunca cor de marca.

## Tipografia

Reddit Sans em tudo. Título 800; nomes de nó 700; descrições 400 em
`--text-muted`; pílulas caixa alta 600 com `letter-spacing`. Sem Oswald.

## Acessibilidade

- Texto branco só sobre roxo, navy, magenta ou pink sólidos.
- Sobre fundos claros (zona, tint, peach), sempre texto escuro.
- Rótulos de seta usam contorno branco (`paint-order: stroke`) para ler sobre
  qualquer fundo.
