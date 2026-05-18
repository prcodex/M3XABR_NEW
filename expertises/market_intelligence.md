---
name: market_intelligence
description: |
  Fires for queries about Brazilian markets: BRL, Ibovespa, B3, DI1
  futures curves, câmbio, intraday and end-of-day market analysis,
  sector rotation, price action, technical patterns on BR assets.
version: 0.1
type: expertise
applies_to: brazil
trigger_keywords:
  - BRL
  - real
  - dólar
  - câmbio
  - Ibovespa
  - Bovespa
  - B3
  - DI1
  - futuros
  - juros futuros
  - mercado
  - bolsa
  - cotação
  - USDBRL
trigger_entities:
  - markets_agent
  - polymarket
  - b3
---

# Inteligência de Mercado (Brasil)

## Convenções brasileiras de mercado

- **USD/BRL**: positivo = BRL FORTALECEU vs USD. Negativo = BRL
  ENFRAQUECEU.
- **Horário BRL**: USD/BRL opera na B3 das 9h às 18h (BRT), segunda a
  sexta. Fora desse horário, preço é o ÚLTIMO NEGOCIADO — informar
  "mercado fechado."
- **Juros em mudanças**: pontos-base (1 pb = 0,01%).
- **Juros em nível**: % a.a. (Selic, DI1, IPCA implícito).
- **Benchmark de variação**: diárias/semanais/MTD/YTD computadas vs
  fechamento 18h BRT (não 17h, não 19h — exatamente 18h).
- **Fuso**: BRT (UTC-3) sempre, especificar ao citar preços ou eventos.

## Lente analítica

- **MARKET SNAPSHOT é LIVE e canônico.** Usar sempre sobre qualquer
  preço citado em matérias ou tweets. Matéria de 6 horas atrás com
  preço obsoleto: usar snapshot, não o preço da matéria.
- **Rotação setorial**: BRL vs Ibovespa vs curva de futuros vs
  commodities. Quando o BRL fortalece com Ibovespa caindo, é fluxo
  externo. Quando fortalece com Ibovespa subindo, é convicção
  doméstica.
- **Curva DI1 (futuros de juros B3)**: ler estrutura a termo como
  expectativa monetária. Inversão na curva = mercado precificando
  corte; steepening = precificando aperto.
- **Volume e liquidez**: B3 tem horários de baixa liquidez (almoço,
  pós-fechamento NY). Movimentos nesses horários são menos
  significativos.

## Formato de output

- **Tabela `<pre>` para snapshots**: Ativo, Preço, Variação dia, MTD,
  YTD. MAX 30 chars de largura.
- **Análise narrativa fora da tabela**: o que o movimento significa.
- **Sem tabelas markdown** (`| col | col |`).
- **Citar horário do snapshot**: "Preços às 14h35 BRT."

## Sugestões de gráfico (condicional)

Quando a query é especificamente sobre ação de preço, tendências ou
performance, anexar tag ao final da resposta (após todo o texto):

`<!--CHART:TICKER:RANGE:TYPE-->`

- **TICKER**: símbolo yfinance (USDBRL=X, ^BVSP, GC=F, BTC-USD) ou
  separados por vírgula para comparação.
- **RANGE**: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y
- **TYPE**: candlestick (preço de um ativo), comparison (múltiplos),
  snapshot (barras por categoria)

**Regras**:
- Máximo 1 gráfico por resposta.
- Só sugerir quando query é especificamente sobre price action.
- NÃO sugerir para resumos de notícias, análise política, roundups
  de research.
- A tag é invisível para o usuário — aciona geração server-side.

## Modos de falha (corrigir)

- **NÃO mostrar BRL como LIVE** fora do horário de trading (9-18h BRT).
  Sinalizar "mercado fechado, último preço."
- **NÃO conflar preço LIVE com timestamps de eventos passados.**
  Snapshot é agora; matéria é quando foi publicada.
- **NÃO produzir ASCII art**: sparklines, gráficos de barra em texto,
  caixas decorativas. Usar tabela `<pre>` para dados, tag
  `<!--CHART:...-->` para visualização.
- **NÃO usar tabelas markdown** (`| col |`). Quando o output for para
  Telegram, isso quebra; quando for web, fica feio.
- **NÃO forçar gráfico em respostas narrativas.** Gráfico é para price
  action específico.
- **CUIDADO com causalidade**: "BRL caiu porque X" requer fonte para
  X. Movimentos de mercado têm múltiplas causas.
