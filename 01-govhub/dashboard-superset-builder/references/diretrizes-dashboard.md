# Diretrizes de Design para Dashboards

Resumo curado do guia interno de Markdown do time (Guia para Markdown, 17
capítulos), focado no que a skill `dashboard-superset-builder` usa nas Fases 0 e 2.
Esse guia é um documento interno de trabalho da equipe — não é distribuído junto
com a skill, então não conte com poder abri-lo a partir do repositório; este resumo
é a fonte que a skill de fato usa.

**Aviso de cobertura:** os capítulos mais específicos de dashboard — 13
(Estruturação de Dashboards), 14 (Tabelas), boa parte do 15 (Catálogo de
Componentes) e 4.5 (Cores para Visualização de Dados) — estão, no guia interno
usado como fonte, só com os títulos das subseções, sem conteúdo escrito. Não
invente conteúdo para preencher essas lacunas: quando uma decisão do esboço
dependeria de uma diretriz específica ainda não escrita (ex.: regra exata de cor
por tipo de gráfico), sinalize isso no esboço em vez de decidir sozinho.

## Perfil do usuário

Duas perguntas definem a complexidade permitida na interface:

**Experiência digital:**
- **Iniciante** — precisa de mais orientação visual, fluxos simples, baixa
  densidade, ações e informações importantes bem destacadas.
- **Intermediário** — entende padrões comuns de navegação, lida com mais
  informação, precisa de equilíbrio entre clareza e produtividade.
- **Avançado** — prefere velocidade, tolera densidade visual alta, precisa de
  acesso rápido, dispensa explicações excessivas.
- **Especialista** — busca produtividade máxima, quer dados detalhados, tolera
  interfaces complexas, prefere acesso direto a recursos avançados.

**Conhecimento de negócio:**
- **Leigo** (clientes finais, consumidores) — linguagem simples, explicações
  claras.
- **Técnico** (operadores, analistas) — pode usar terminologia da área.
- **Especialista** (engenheiros, consultores) — informação mais detalhada e
  técnica.
- **Gestor** (coordenadores, gerentes, diretores) — prioriza indicadores, resumos
  e informação que apoie decisão, não necessariamente detalhe operacional.

Exemplo prático: **Iniciante + Leigo** pede menos informação por tela, mais
contexto, navegação simples, baixa densidade. **Avançado + Especialista** se
beneficia de mais informação simultânea, menos texto explicativo, menos etapas.
**Avançado + Gestor** pede poucos detalhes operacionais mas muitos indicadores e
comparativos.

## Hierarquia de informação

Toda informação exibida tem custo visual e cognitivo. Antes de incluir algo,
pergunte: "a ausência desta informação impede o usuário de concluir a tarefa?" —
se não, ela deve ser removida, reduzida ou movida para um local secundário.

Camadas, da mais para a menos destacada:

1. **Primária** (~60% da atenção) — o motivo principal de acessar a tela. Maior
   tamanho, maior contraste, maior peso tipográfico, posição prioritária.
   Exemplos: consumo total, quantidade de alertas ativos, receita do período, KPI
   principal.
2. **Secundária** (~25%) — ajuda a interpretar a informação primária, sem competir
   visualmente com ela. Exemplos: comparativo com período anterior, percentual de
   crescimento, categoria do alerta.
3. **Complementar** (~10%) — aprofundamento, acessível quando necessário, sem
   gerar ruído. Exemplos: observações, histórico detalhado, logs, data da última
   atualização.
4. **Opcional/descartável** (~5%) — só em situações específicas (tooltip, drawer,
   modal, tela de detalhe) ou removível de vez. Exemplos: campos técnicos
   avançados, configurações, ilustrações decorativas, texto institucional.

Regra de ouro: se tudo recebe destaque, nada recebe destaque.

## Densidade visual

- **Alta densidade** — usuários avançados, operações técnicas, monitoramento,
  backoffice.
- **Média densidade** — **padrão para dashboards corporativos**, produtos SaaS,
  gestão.
- **Baixa densidade** — público geral, autoatendimento, mobile.

## Contexto de uso

- **Desktop** — mais informação simultânea, tabelas completas, múltiplos
  gráficos, filtros avançados. Mesmo assim, não adicione informação só porque há
  espaço.
- **Tablet** — botões maiores, menor densidade, interações otimizadas para toque,
  considerar retrato e paisagem.
- **Mobile** — priorizar ações principais, alertas, indicadores críticos;
  evitar tabelas complexas e muitos filtros simultâneos.
- **Ambiente corporativo** — priorizar produtividade, reduzir cliques, favorecer
  atalhos.
- **Ambiente operacional/industrial** — leitura rápida, status facilmente
  identificáveis, mínimo de navegação.
- **Uso diário** vs. **uso ocasional** — usuário frequente tolera mais informação
  e fluxos especializados; usuário ocasional precisa de mais suporte visual e
  terminologia simples.

## Cores

**Institucionais:**
- **Primária** — a cor da ação principal da plataforma (botão principal, links,
  estados ativos, seleções, foco). Deve ter escala tonal (100–900) para hover,
  focus, bordas, backgrounds.
- **Secundária** — apoio visual (categorias, destaques específicos, gráficos),
  nunca competindo com a primária.

**Neutras** — sustentam a maior parte da interface (>80% em sistemas
corporativos): branco/off-white para superfícies, tons claros para bordas e
divisores, tons médios para texto secundário/rebaixado, tons escuros para texto
principal. Evite preto e branco absolutos em textos/grandes blocos.

**Semânticas** — significado reconhecido universalmente, nunca usar como
decoração nem trocar de significado entre telas:
- **Verde** — sucesso, aprovado, concluído, saudável, disponível.
- **Vermelho** — erro, falha, alerta, bloqueio, crítico.
- **Amarelo** — atenção, aviso, monitoramento, pendência.
- **Azul** — informação, navegação, ação, referência.
- **Cinza** — desabilitado/desativado.

Nunca usar cor como único indicador de estado — combine sempre com ícone e/ou
texto (redundância visual), importante para acessibilidade (daltonismo, baixa
visão).

## Tipografia e hierarquia

- Poucos tamanhos e poucos pesos tipográficos = mais consistência.
- H1 é o assunto principal da tela (um só por tela); em dashboards, o "H1" visual
  muitas vezes é o KPI/big number, não um texto — mesmo assim, use estrutura
  semântica correta (H1–H6) para acessibilidade (WCAG/eMAG), não só peso/tamanho.
- Fatores que aumentam destaque visual: cor mais saturada, mais contraste, maior
  tamanho, mais espaço em branco ao redor. Quanto mais desses recursos um
  elemento recebe, mais atenção atrai — use com intenção, não em tudo.
- Em um dado dentro de um dashboard, o valor (big number) é o que recebe o maior
  peso/tamanho — o rótulo/chapéu acima dele fica discreto (ex.: rótulo Regular
  10px, valor Bold 15px+).
