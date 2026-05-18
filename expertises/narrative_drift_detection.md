---
name: narrative_drift_detection
description: |
  Fires for queries comparing a source's position over time, asking
  how forecasts changed, tracking consensus shifts, identifying when
  an analyst or institution revised their view. Examples: "how did
  Itaú change its Selic projection", "Goldman's BRL view evolution",
  "did Polymarket consensus shift on Lula in the last month."
version: 0.1
type: expertise
applies_to: brazil
trigger_keywords:
  - mudou
  - mudança
  - shift
  - drift
  - evolução
  - revisou
  - revisão
  - antes
  - depois
  - há semanas
  - há meses
  - tem mudado
  - comparação
  - vs
  - contra
  - como estava
trigger_entities: []
---

# Detecção de Drift Narrativo

## O que esta expertise faz

Quando o usuário pergunta como a visão de uma fonte mudou no tempo,
**esta é a expertise que dispara**.

Especificamente: comparar posições entre janelas de tempo:
- "Visão do Itaú sobre Selic em março vs maio"
- "Como o Goldman evoluiu sua call de BRL"
- "Consenso do Polymarket sobre reeleição mudou no último mês?"
- "Datafolha estabilizou ou está em movimento?"
- "Itaú vs XP: como divergiram nas últimas semanas?"

## Lente analítica

- **Ancorar cada posição no tempo**: "Em março, o Itaú projetava Selic
  terminal em 9,75%. Em maio, projetou 10,25%."
- **Identificar o ponto de inflexão**: o que disparou a mudança?
  Surpresa inflacionária, evento político, comunicação do BCB, dado
  fiscal?
- **Limitar a comparação**: se o retrieval não carrega posições
  históricas, dizer. NUNCA fabricar uma posição "antes" para criar
  uma história de "mudança."
- **Distinguir drift vs ajuste pontual**: uma mudança única pode ser
  reação a dado; drift é padrão sustentado de revisões na mesma
  direção.
- **Contraste com o que NÃO mudou**: drift significativo é mais
  informativo quando contextualizado pelo que se manteve estável.

## Formato de output

- **Bullets ancorados no tempo**, não narrativa contínua.
- **Cada posição citada com data**.
- **Ponto de inflexão explícito** quando recuperável do retrieval.
- **Contra-balanço**: o que NÃO mudou, quando relevante.

Exemplo de estrutura:

```
**Itaú — Selic terminal**
- Mar 5: 9,75% (relatório macro mensal)
- Abr 10: 10,00% (revisão pós-IPCA)
- Mai 7: 10,25% (após sinalização do Copom em ata)

**Inflexão**: o IPCA de março (+0,67% m/m) surpreendeu para cima e
deslocou as expectativas. XP fez movimento similar; Bradesco se
manteve em 10,00%.
```

## Combinação com outras expertises

Esta expertise raramente dispara sozinha. Combina com:

- `monetary_analysis` — para drift em calls de Selic
- `fiscal_analysis` — para drift em projeções fiscais
- `economic_forecasts` — para drift em projeções de PIB/IPCA
- `electoral_analysis` — para drift em pesquisas eleitorais
- `institutional_source_briefing` — para drift na visão de uma casa
  específica

Quando dispara, frequentemente carrega 1-2 outras expertises do
domínio em questão.

## Modos de falha (corrigir)

- **NÃO fabricar drift a partir de uma única observação.** Drift
  requer pelo menos duas posições datadas em tempos diferentes.
- **Se apenas uma posição está recuperável**, enquadrar como "visão
  atual" em vez de "mudança de X para Y."
- **NÃO conflar drift no relatório de um analista com mudança no
  consenso institucional.** Um analista do JPMorgan revisar não é o
  mesmo que o house view do JPMorgan mudar.
- **NÃO inventar datas** para encaixar uma narrativa de drift. Se as
  datas não estão claras no retrieval, dizer.
- **CUIDADO com mudanças no ciclo natural**: projeções de Selic
  terminal naturalmente convergem conforme o ciclo monetário avança.
  Isso não é "drift" — é a curva forward sendo realizada. Distinguir.
- **NUNCA comparar mediana de pesquisas diferentes ao longo do tempo
  sem ajustar pela metodologia.** Datafolha de jan vs Quaest de mar
  não é série temporal — é comparação de institutos.
- **CUIDADO com base effects**: comparações YoY no IPCA podem mostrar
  "drift" que é apenas reflexo de base baixa/alta no ano anterior.
