# Skill `lablivre-visual-identity`: cópia da skill do Gov Hub para a marca Lab Livre

Data: 2026-09-18. Decidido em conversa com João Egewarth.

## Objetivo

Ter uma skill de identidade visual do Lab Livre com a mesma profundidade da
`govhub-visual-identity` (PDF, slides, posts, web, tokens), em vez da skill
resumida do plugin `anthropic-skills` (que traz só MIV + 6 PNGs). Copia a
estrutura inteira e troca a marca; assets do CDN ficam pendentes.

## Decisões

1. **Escopo: tudo, adaptando as cores.** Os 16 arquivos de `references/` e
   o `SKILL.md` são copiados. Slides, posts, ícones e elementos gráficos
   continuam apontando para os SVGs do Gov Hub no CDN, com aviso no topo de
   cada catálogo e o caminho previsto para os assets do Lab Livre
   (`skills-assets@main/lablivre/<icons|graphic-elements|post-templates>/`).
2. **Cores: mapeamento posicional** da rampa do MIV Gov Hub para a do MIV
   Lab Livre, mantendo os **nomes** dos tokens:

   | Token | Gov Hub | Lab Livre | Nome no MIV Lab Livre |
   |---|---|---|---|
   | `--dark-navy` | `#0A005A` | `#080056` | azul profundo |
   | `--primary-purple` | `#613EFF` | `#7023E8` | roxo (assinatura) |
   | `--accent-magenta` | `#EF41FF` | `#E52E70` | rosa-choque |
   | `--accent-pink` | `#F9006F` | `#F46B2F` | laranja |
   | `--bg-peach` | `#FFE7E1` | `#FFE7E1` | rosa claro |

   Derivados recalculados a partir do novo roxo e do novo azul:
   `--purple-600/700`, `--logo-purple`, `--border-soft`, sombras
   (`rgba(8,0,86,…)`), rampa `--editorial-00…04`.
3. **Local e distribuição:** `07-lablivre/lablivre-visual-identity/`, novo
   plugin `govhub-lablivre` (sem `version`), entrada no `marketplace.json`,
   skill incluída na coleção `govhub-skills` (52 skills). Symlink
   `~/.claude/skills/lablivre-visual-identity` para o repo.
4. **Logos agora:** os 6 SVGs já existentes (`lab-livre-{black,blue,white}`,
   `borboleta-{black,blue,white}`) viram a logo principal em
   `references/logo/`. Parceiros: UnB (outlined, sempre), Gov Hub
   (`logomarca-horizontal-navy/white`, quando o documento é de projeto Gov
   Hub), Ipea e ministérios (iguais ao Gov Hub, ciclo eleitoral igual).
   Faltam e ficam catalogados como pendentes: roxo `#7023E8`, vertical,
   tipográfica isolada, versões peach. Até chegarem, fundo claro usa
   `lab-livre-blue` (ou `black`), fundo escuro `lab-livre-white`.
5. **Regras de marca** vêm do MIV Lab Livre (via skill do plugin):
   assinaturas horizontal / tipográfica / ícone com reduções mínimas 3 cm /
   2 cm / 0,5 cm; área de não interferência "x" = altura do ícone; usos
   indevidos; Reddit Sans (Black no logotipo) + Oswald Bold uppercase; Open
   Sans como substituta.
6. **Validação:** tudo que na skill do Gov Hub diz "validado com o usuário"
   passa a "herdado da skill do Gov Hub, ainda não validado em peça do Lab
   Livre". As regras de PDF aprovadas em 2026-09-17/18 (capa branca,
   cabeçalho sóbrio, tabela em azul profundo, título de capítulo em roxo,
   hierarquia da folha de identificação, paginação) valem igual.
7. **Texto:** "Gov Hub" → "Lab Livre" onde é a marca; onde é o projeto
   (rodapé `· Gov Hub · Lab Livre - UnB`, folha de identificação, exemplos
   de conteúdo) o rodapé vira `· Lab Livre · UnB` e o Gov Hub passa a ser
   um dos projetos citados como exemplo.

## Fora do escopo

- Gerar assets do Lab Livre no CDN (ícones, templates de slide, posts).
- Figma do Lab Livre.
- Remover a skill `lablivre-visual-identity` do plugin `anthropic-skills`
  (decisão do usuário, fora do repo).

## Implementação

Script de cópia + substituições em lote (hex, nomes, caminhos), seguido de
revisão manual arquivo a arquivo. Verificação: `grep` por hex do Gov Hub e
por "Gov Hub" nos arquivos copiados; `scripts/atualizar-manifestos.py` para
os manifestos; `claude plugin marketplace update govhub` para confirmar que
o plugin novo aparece.
