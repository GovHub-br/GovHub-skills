# Paleta GovHub — referência e quando usar cada cor

Valores extraídos diretamente do CSS de <https://gov-hub.io>. Use exatamente
estes hexadecimais. Os nomes de token estão em inglês (ver `tokens.css`).

## Cores primárias da marca

| Token | Hex | Uso |
|---|---|---|
| `--primary-purple` | `#7A34F3` | **Cor-assinatura.** Títulos de destaque, cabeçalhos de tabela, botões primários, links, badges, barras de topo, ícones de destaque. É o roxo que identifica a marca. |
| `--secondary-purple` | `#8B5CF6` | Roxo de apoio. Segunda parada de gradientes, hovers suaves, elementos secundários que ainda precisam de identidade roxa. |
| `--accent-orange` | `#F97316` | **Acento pontual.** Call-to-action, destaque de um número/metric-chave, tags de alerta positivo. Usar com parcimônia (regra 90/10). |
| `--accent-orange-hover` | `#EA580C` | Estado hover do laranja. |
| `--text-white` | `#FFFFFF` | Texto sobre superfícies roxas ou laranjas. |

## Roxos de apoio e estados

| Token | Hex | Uso |
|---|---|---|
| `--purple-400` | `#9249CA` | Roxo médio para gradientes e detalhes. |
| `--purple-600` | `#7C3AAD` | **Hover/foco** de elementos roxos (botão primário, link). |
| `--purple-700` | `#5B21B6` | **Active/pressionado**, e roxo para texto sobre fundo branco quando precisar de contraste extra (ver acessibilidade). |

## Neutros e texto

| Token | Hex | Uso |
|---|---|---|
| `--text-strong` | `#202020` | Títulos e texto forte. |
| `--text-body` | `#2D3748` | Corpo de texto padrão. |
| `--text-muted` | `#666666` | Legendas, texto secundário, metadados. |

## Fundos

| Token | Hex | Uso |
|---|---|---|
| `--bg-white` | `#FFFFFF` | Cards, superfícies elevadas, conteúdo principal. |
| `--bg-light` | `#F7F7F7` | Fundo neutro da página. |
| `--bg-subtle` | `#F8F9FA` | Linhas alternadas de tabela (zebra), seções alternadas. |

## Cores semânticas / estado

| Token | Hex | Uso |
|---|---|---|
| `--color-success` | `#10B981` | Verde de sucesso, status positivo. |
| `--color-highlight` | `#FFD700` | Amarelo de destaque, marcações pontuais. |
| `--color-warm` | `#F19F42` | Laranja suave, destaque secundário mais calmo que `--accent-orange`. |

## Regra de proporção (uso de marca)

- **Roxo (`#7A34F3`) = cor primária/assinatura.** Domina os elementos de identidade.
- **Laranja (`#F97316`) = acento pontual.** ~10% da tela, só em CTA/destaque. **Não abusar.**
- **Fundos claros neutros** (`#F7F7F7`, `#F8F9FA`, branco) para respiro e legibilidade.
- **Inter** como fonte em tudo.

## Acessibilidade (contraste)

- Texto **branco** (`#FFFFFF`) sobre `--primary-purple` (`#7A34F3`): **OK** (contraste suficiente).
- Texto **branco** sobre `--accent-orange` (`#F97316`): use `font-weight >= 600` para reforçar; prefira texto escuro em áreas grandes de laranja claro.
- Texto **roxo sobre fundo branco**: para textos pequenos, use o roxo mais escuro
  `--purple-700` (`#5B21B6`) em vez de `#7A34F3` para garantir contraste AA.
- Nunca coloque `--text-muted` (`#666666`) sobre fundos coloridos escuros.
