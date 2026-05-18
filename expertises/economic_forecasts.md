---
name: economic_forecasts
description: |
  Fires for queries about Brazilian economic projections — what
  institutional houses expect for GDP, inflation, activity. Covers
  Focus survey (BCB's weekly survey of ~140 institutions), revisions
  across houses (who moved their forecast up/down, when, why),
  contrast across Itaú/XP/BTG/Bradesco/Santander/Goldman/JPMorgan,
  and forward-looking scenario analysis.
version: 0.1
type: expertise
applies_to: brazil
trigger_keywords:
  - projeção
  - projetam
  - expectativa
  - expectam
  - cenário
  - revisão
  - revisaram
  - revisar
  - Focus
  - boletim Focus
  - house view
  - call
  - mediana
  - consenso
  - estimativa
  - prevê
  - esperam
  - 2025
  - 2026
  - 2027
trigger_entities:
  - itau
  - xp_macro_strategy
  - btg_pactual
  - bradesco_research
  - santander_research
  - goldman_sachs
  - jpmorgan
  - ubs
  - morgan_stanley
  - bank_of_america
  - citi
  - bcb
---

# Projeções e Revisões Econômicas

## O que esta expertise cobre

Foco em **visões prospectivas das casas** sobre a economia brasileira.
Não cobre dados publicados (esses vão para `economic_releases`).
Dispara quando o usuário pergunta sobre:

- Projeção institucional para PIB, IPCA, atividade, em horizontes
  específicos (corrente, próximo ano, 2026, 2027)
- Revisão recente de uma casa (quem revisou, em que direção, por quê)
- Comparação cross-casa: Itaú vs XP vs BTG vs Goldman vs JPMorgan
- Boletim Focus do BCB (mediana de ~140 instituições semanalmente)
- Contraste mediana de mercado vs casas específicas vs cenário oficial
  do governo
- Cenários alternativos (otimista, pessimista, base)

## Hierarquia de fontes prospectivas

**Para projeção institucional brasileira:**

- **Itaú Macro Research** — Maior cobertura macro Brasil. "Macro Visão"
  mensal + atualizações semanais. Projeções publicadas para PIB, IPCA,
  Selic, câmbio, fiscal em horizontes 2-3 anos. "Segundo o Itaú..."
- **XP Macro Strategy** — "Daily" + temáticos semanais. Visões com
  frequente desvio vs Focus mediana. "A XP avalia..."
- **BTG Pactual** — Macro brasileiro com foco em câmbio e atividade.
  "O BTG projeta..."
- **Bradesco DEPEC** — "Boletim Macroeconômico" semanal. Tradicional,
  tipicamente próximo da mediana de Focus.
- **Santander Brasil Macro** — Cobertura com viés commodities e setor
  externo.

**Para projeções internacionais sobre Brasil:**

- **Goldman Sachs Brazil Economic Watch** — Mensal. Frequentemente
  destaca riscos fiscais; visões mais críticas em PIB que casas
  domésticas.
- **JPMorgan Brazil Watch** — Boletim macro. Foco em curva e moedas.
- **UBS Latam Macro** — Visão Brasil dentro do regional.
- **Morgan Stanley**, **Bank of America**, **Citi** — Cobertura
  institucional Brasil dentro de research macro mais amplo.

**Para mediana de mercado:**

- **Pesquisa Focus do BCB** — Publicada toda segunda-feira (~8h BRT)
  com mediana de ~140 instituições para PIB, IPCA, Selic, câmbio,
  conta corrente, primário. Inclui top-5 (mais acuradas historicamente)
  como referência adicional.
- **Reuters Survey**, **Broadcast Survey**, **Bloomberg Survey** —
  Versões privadas com universo institucional menor. Citar quando
  aparecem no feed.

## Convenções

- **Horizonte**: SEMPRE especificar para qual ano a projeção se refere.
  "Itaú projeta PIB de 2,0%" sem ano é ambíguo.
- **Última revisão**: ancorar no tempo. "Em relatório de 12/03, o Itaú
  revisou..." é diferente de "o Itaú projeta..."
- **Comparativos**: contrastar com mediana de Focus quando disponível.
  "Itaú em 2,0% vs Focus em 1,8%" mostra a casa onde está vs consenso.
- **Composição**: para PIB, citar a decomposição quando relevante
  (consumo, investimento, gov, líquidas).
- **Selic terminal** vs **Selic final do ano**: números diferentes.
  Terminal é o ponto mais baixo/alto esperado no ciclo; final é onde
  estará no fim do horizonte temporal.

## Lente analítica

- **Para query sobre projeção institucional**: identificar todas as
  casas com visão no retrieval, organizar em tabela comparativa,
  destacar onde estão vs mediana Focus, mencionar quando última revisão
  ocorreu.
- **Para revisão recente**: descrever movimento (de X para Y, em que
  data), citar justificativa do release, comparar com movimento de
  pares (Itaú revisou — XP também moveu? Bradesco manteve?).
- **Para divergência grande mediana-vs-casa**: tratar como sinal, não
  erro. Goldman frequentemente mais pessimista em PIB que Focus — isso
  é informação, não ruído.
- **Para Focus**: mediana é só parte da história — top-5 e o desvio-
  padrão da pesquisa também informam.

## Formato de output

- **Comparação cross-casa**: tabela `<pre>` com Casa, Indicador (e ano),
  Projeção, Última revisão. Compacta (~30 chars).
- **Revisão narrada**: prosa com data específica, valor antes/depois,
  justificativa publicada, contraste com pares.
- **Focus snapshot**: tabela com mediana atual + 4 semanas atrás +
  variação. Para PIB e IPCA do ano corrente + próximo ano.

## Modos de falha (corrigir)

- **NUNCA fabricar projeção.** Se Itaú não está no retrieval com PIB
  recente, dizer "não tenho a projeção atual do Itaú para PIB no feed."
  NUNCA inferir "o Itaú provavelmente projeta X."
- **NUNCA confundir mediana Focus com casa específica.** Focus é
  mediana de ~140 casas; uma casa específica pode estar em qualquer
  lugar da distribuição.
- **NUNCA tratar uma revisão como "consenso mudou"** sem ver 3-4 casas
  movendo na mesma direção em janela curta.
- **NUNCA citar projeção sem horizonte.** "PIB de 2%" sem dizer o ano
  é ambíguo e potencialmente errado.
- **NUNCA confundir "Itaú revisou" com "Itaú divergiu".** Revisão é
  movimento no tempo (de A para B); divergência é posição vs consenso
  (acima/abaixo de Focus).
- **NUNCA inferir convergência institucional sem evidência.** Duas
  casas em valores próximos é coincidência até prova em contrário.
- **Para cenários** (base/otimista/pessimista): só citar quando a casa
  publicou cenários — não fabricar variantes.
