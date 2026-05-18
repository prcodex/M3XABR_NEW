---
name: fiscal_analysis
description: |
  Fires for queries about Brazilian government finance: primary result
  (superávit/déficit primário), public debt (dívida bruta/líquida) and
  debt/GDP trajectory, government spending and revenue, fiscal targets,
  arcabouço fiscal compliance, budget framework (LDO/LOA/PLOA), Tesouro
  Nacional emissions and debt management, rating agency commentary on
  Brazil sovereign, and houses' fiscal projections. Also fires when the
  user asks about Fazenda (Haddad) fiscal communication or IFI (Senate's
  independent fiscal monitor).
version: 0.1
type: expertise
applies_to: brazil
trigger_keywords:
  - fiscal
  - primário
  - resultado primário
  - superávit
  - déficit
  - dívida
  - dívida pública
  - dívida bruta
  - dívida líquida
  - dívida/PIB
  - DBGG
  - DLSP
  - arcabouço
  - arcabouço fiscal
  - meta fiscal
  - meta primária
  - LDO
  - LOA
  - PLOA
  - PEC fiscal
  - gastos
  - despesa
  - receita
  - arrecadação
  - Tesouro
  - Tesouro Nacional
  - emissão
  - rolagem
  - rating
  - downgrade
  - upgrade
  - IFI
  - sustentabilidade fiscal
trigger_entities:
  - haddad
  - fazenda
  - tesouro_nacional
  - ifi
  - moodys
  - sp_global
  - fitch
  - itau
  - xp_macro_strategy
  - btg_pactual
  - bradesco_research
  - santander_research
  - goldman_sachs
  - jpmorgan
  - ubs
---

# Análise Fiscal Brasileira

## O que esta expertise cobre

Foco em **finanças do governo brasileiro** — não política monetária
(Selic/Copom), não atividade real (PIB/IPCA). Esta expertise dispara
quando o usuário pergunta sobre:

- **Resultado primário**: superávit ou déficit, governo central vs
  consolidado (com estados e municípios)
- **Dívida pública**: dívida bruta do governo geral (DBGG), dívida
  líquida do setor público (DLSP), trajetória dívida/PIB
- **Gastos do governo**: discricionários vs obrigatórios, por
  ministério, expansão vs contenção
- **Receitas**: arrecadação federal, surpresas vs projeção, composição
- **Arcabouço fiscal**: regras vigentes (PEC 2023), observância,
  cláusulas de escape, expectativa de cumprimento
- **Documentos orçamentários**: LDO, LOA, PLOA, suas projeções
- **Tesouro Nacional**: emissões, rolagem, custo médio, prazo médio,
  perfil da dívida
- **Metas fiscais**: meta primária por ano, trajetória, bandas
- **Rating soberano**: Moody's, S&P, Fitch — outlook + decisões
- **Sustentabilidade**: avaliações institucionais sobre trajetória

Frequentemente carregada junto com `monetary_analysis` — fiscal afeta
monetary via prêmio de risco e expectativas de inflação.

## Fontes primárias

- **Tesouro Nacional** — Resultado primário do governo central (mensal,
  ~25 dias após mês de referência), boletim mensal de dívida pública,
  Plano Anual de Financiamento (PAF). "Segundo o Tesouro Nacional..."
- **Banco Central** — Estatísticas fiscais consolidadas (governo geral,
  mensal), dívida líquida do setor público. "O BCB divulgou..."
- **Ministério da Fazenda** — Comunicados oficiais, falas do Haddad e
  secretários, projeções no Relatório de Receitas e Despesas Primárias
  (bimestral).
- **Câmara/Senado** — Discussões do arcabouço, PECs fiscais, LDO/LOA.
- **IFI (Instituição Fiscal Independente)** — Acompanhamento técnico
  do Senado, projeções independentes, relatórios mensais.
  "Segundo a IFI..." — usar como contraponto institucional.
- **STN/SOF** — Para análise técnica do orçamento.

## Hierarquia de visões institucionais (sobre fiscal BR)

- **Itaú Macro Research** — Cobertura próxima e contínua do fiscal.
  Projeções de primário e dívida em "Macro Visão" mensal +
  atualizações. "Segundo o Itaú..."
- **XP Macro Strategy** — Visões frequentemente mais críticas no fiscal
  vs Itaú. Boa para cenários de pior caso. "A XP avalia..."
- **BTG Pactual** — Foco em implicações para mercado (curva, soberano,
  rating). "O BTG projeta..."
- **Bradesco DEPEC** — Visão tradicional, projeções DEPEC publicadas
  semanalmente.
- **Santander Brasil Macro** — Tipicamente alinhado com mediana de
  mercado.

Para visões internacionais sobre o fiscal brasileiro:
- **Goldman Sachs Brazil Macro** — Frequentemente cita riscos fiscais
  como condicionante de calls de Selic e BRL.
- **JPMorgan Brazil Watch** — Boletim macro com seção fiscal.
- **UBS Latam Macro** — Visão Brasil dentro da cobertura regional.
- **Morgan Stanley**, **Bank of America**, **Citi** — Cobertura
  institucional Brasil dentro de research macro mais amplo.

## Convenções de dados fiscais

- **Resultado primário**: % do PIB (anual) ou R$ bilhões (mensal/
  acumulado). Especificar.
- **Dívida bruta (DBGG)**: % do PIB. Critério do BCB (inclui títulos
  na carteira do BCB, exclui parte detida pelo Tesouro). FMI usa
  critério ligeiramente diferente — sempre explicitar.
- **Dívida líquida (DLSP)**: % do PIB, exclui ativos. Tipicamente bem
  abaixo da DBGG.
- **Arcabouço fiscal (PEC 2023)**: regra de gasto = crescimento real
  da receita líquida × (0,7 a 1,0), banda de 0,6%–2,5% ao ano em termos
  reais. Trava de superávit + 0,25% da meta para liberar 100% do
  limite.
- **Meta fiscal**: meta de resultado primário em % do PIB. Banda de
  tolerância (±0,25 pp). Atenção à diferença entre meta do governo
  central vs consolidado.
- **Espaço fiscal**: diferença entre teto de gasto e gasto projetado.
  Espaço positivo = governo pode expandir; negativo = corte necessário.

## Lente analítica

- **Para número fiscal recém-publicado**: começar com o número,
  contextualizar vs meta, vs consenso, vs mesmo período do ano
  anterior. Depois implicações para cumprimento da meta + trajetória
  da dívida.
- **Para projeção institucional**: ancorar no tempo (revisão de
  quando?), comparar com Focus mediana, comparar com IFI (tipicamente
  mais cético que mediana), comparar com cenário oficial do governo.
- **Para discussão de arcabouço**: o governo está cumprindo? Quais
  cláusulas de escape estão acionadas? Probabilidade de flexibilização
  vs revisão?
- **Para rating**: outlook atual de cada agência, decisões recentes,
  triggers para downgrade/upgrade. Trajetória da dívida e cumprimento
  do arcabouço são inputs principais.
- **Tensão fiscal-monetary**: quando o BCB sinaliza preocupação fiscal
  nas atas, isso pressiona Selic. Carregar `monetary_analysis` em
  paralelo nessas queries.

## Formato de output

- **Snapshot fiscal**: tabela `<pre>` com Indicador, Valor atual, Meta,
  Variação. Linhas: Primário, Dívida bruta, Dívida líquida, Gasto vs
  teto.
- **Visões institucionais**: tabela `<pre>` comparando casas (Casa,
  Resultado primário ano corrente, Dívida/PIB final do ano).
- **Análise narrativa**: prosa com 2-3 parágrafos, citações específicas,
  contraponto IFI quando relevante.

## Modos de falha (corrigir)

- **NUNCA confundir resultado primário (governo central, antes de
  juros) com resultado nominal (todo setor público, depois de juros).**
  Histórias diferentes.
- **NUNCA citar dívida sem especificar bruta vs líquida.** DBGG e DLSP
  diferem em ~25 pp do PIB.
- **NUNCA tratar o arcabouço fiscal como o antigo teto de gastos.**
  Lógicas distintas — arcabouço é regra de gasto vs receita, não
  congelamento real.
- **NUNCA inferir trajetória de dívida sem horizonte explícito.**
  Dívida sustentável depende de prazo (curto vs médio prazo).
- **NUNCA inferir que "rating estável" significa "fiscal está bem".**
  Outlook é forward-looking; nível é backward-looking.
- **NUNCA fabricar projeções fiscais de uma casa** que não está no
  retrieval.
- **CUIDADO com aritmética**: nominal vs real, % do PIB vs R$ bi,
  anual vs mensal. Sempre especificar.
- **NÃO confundir Fazenda (Haddad) com BCB (Galípolo).** Fazenda é
  executor fiscal; BCB é autoridade monetária. Mesmo quando Galípolo
  comenta fiscal, sua visão é diagnóstica, não executiva.
