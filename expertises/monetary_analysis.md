---
name: monetary_analysis
description: |
  Fires for queries about Brazilian monetary policy: Selic decisions and
  trajectory, Copom communiqués and atas, BCB communication, policy
  rate calls, basis-point changes, BCB reaction function. Also covers
  IPCA as input to monetary policy (vs IPCA-as-release which belongs
  to economic_releases). Houses' Selic calls (Itaú terminal, XP path,
  BTG, Bradesco). DI1 curve reading for monetary expectations.
version: 0.1
type: expertise
applies_to: brazil
trigger_keywords:
  - Selic
  - Copom
  - BCB
  - Banco Central
  - juros
  - juros futuros
  - DI1
  - terminal
  - corte
  - alta
  - manutenção
  - ata
  - comunicado
  - Galípolo
  - aperto
  - afrouxamento
  - ciclo monetário
  - reação
  - hawkish
  - dovish
  - basis points
  - pontos-base
  - pb
trigger_entities:
  - bcb
  - copom
  - galipolo
  - itau
  - xp_macro_strategy
  - btg_pactual
  - bradesco_research
  - santander_research
  - goldman_sachs
  - jpmorgan
  - ubs
---

# Análise Monetária

## O que esta expertise cobre

Foco em **política monetária brasileira** — não fiscal (governo gasta/
arrecada), não atividade (dados publicados). Esta expertise dispara
quando o usuário pergunta sobre:

- Decisão de Selic (corte, alta, manutenção, magnitude)
- Comunicado e ata do Copom — interpretação, sinais
- Trajetória de Selic prospectiva — terminal do ciclo, ritmo
- Função de reação do BCB — quais inputs sensibilizam decisões
- Comunicação do BCB e da diretoria (Galípolo e demais)
- Curva DI1 — estrutura a termo como expectativa monetária
- Calls de Selic das casas (Itaú terminal, XP path, BTG)
- IPCA **como input para a reação monetária** (não o release em si —
  isso é `economic_releases`)

## Fontes primárias

- **BCB** — Comunicado do Copom (logo após reunião), ata (terça-feira
  da semana seguinte), Relatório de Inflação (trimestral), boletim
  Focus (semanal — para Selic mediana de mercado).
- **Diretoria do BCB** — Falas públicas, especialmente do presidente
  (Galípolo). Tratar cada fala com peso institucional.

## Hierarquia de visões institucionais (sobre Selic)

- **Itaú Macro Research** — Call de Selic terminal publicado, atualizado
  conforme dados. "A equipe macro do Itaú projeta Selic terminal em..."
- **XP Macro Strategy** — Visões frequentemente mais hawkish ou dovish
  vs Focus mediana. "A XP avalia..."
- **BTG Pactual** — Foco em implicações para câmbio e curva.
  "O BTG projeta..."
- **Bradesco DEPEC** — Tradicional, alinhado com mediana de mercado.
- **Santander Brasil Macro** — Cobertura macro com visão monetária.

Para visões internacionais sobre Selic BR:
- **Goldman Sachs Brazil Macro** — Frequentemente cita riscos fiscais
  como input do call.
- **JPMorgan Brazil Watch** — Visões publicadas em boletim macro.

## Convenções

- **Selic em mudanças**: pontos-base (1 pb = 0,01%).
- **Selic em nível**: % a.a. ("Selic em 10,75% a.a.").
- **Selic terminal**: o ponto mais baixo/alto esperado no ciclo
  monetário corrente. Diferente de "Selic no fim de [ano]" que é
  cross-section temporal.
- **Aperto monetário** = alta de Selic; **afrouxamento** = corte.
  **Manutenção** é decisão própria, não ausência de decisão.
- **Hawkish/dovish** — usar quando descrever tom de comunicação,
  não para descrever a decisão em si.

## Lente analítica

- **Para próxima decisão**: o que o BCB sinalizou na última comunicação?
  Como o mercado precifica via Focus e curva DI1? Onde estão as casas?
- **Para decisão recém-tomada**: magnitude vs expectativa, sinalização
  no comunicado (mudanças vs comunicado anterior), implicações para
  próxima reunião.
- **Para ata** (saída ~1 semana após reunião): elementos novos vs
  comunicado, ênfase em fiscal/atividade/inflação, sinais para próxima
  reunião.
- **Para projeção de casa**: quando foi a última revisão, justificativa,
  contraste com Focus e com pares.
- **Curva DI1**: ler estrutura a termo. Inversão = mercado precificando
  corte; steepening = precificando aperto. Mudanças na curva entre
  releases são sinal.

## Função de reação do BCB

A reação monetária responde a:
1. **Inflação** (IPCA, expectativas Focus, IPCA-15) — primário
2. **Fiscal** (deteriorização pressiona Selic via prêmio de risco) —
   secundário mas significativo (carregar `fiscal_analysis` nessas
   queries)
3. **Atividade** (hiato do produto) — terciário, mas explicitado em
   comunicados
4. **Câmbio** — input apenas via pass-through inflacionário

Quando o usuário pergunta sobre Selic, frequentemente a resposta certa
exige carregar `economic_releases` (para o IPCA recente) e/ou
`fiscal_analysis` (para o quadro fiscal influenciando o BCB).

## Formato de output

- **Para decisão Copom**: snapshot em `<pre>` com Selic antes/depois,
  vs expectativa, vs reunião anterior. Depois 2-3 parágrafos com
  interpretação do comunicado e implicações.
- **Para call de casa**: tabela `<pre>` comparativa com Casa, Selic
  terminal projetada, data da última revisão.
- **Para curva DI1**: descrição da estrutura (vencimento, taxa
  implícita, comparação com nível atual de Selic).

## Modos de falha (corrigir)

- **NUNCA inferir direção do Copom sem fonte explícita.** Se a matéria
  diz "Copom mantém Selic em 12,75%", reportar isso. NÃO extrapolar
  "sinalizando próximo corte" sem que a fonte tenha dito.
- **NUNCA confundir Selic-meta com Selic-Over.** Selic-meta é a meta
  do Copom; Selic-Over é a taxa diária do mercado interbancário.
  Próximas mas distintas.
- **NUNCA confundir Focus mediana com posição do BCB.** Focus é o que
  ~140 instituições projetam; o BCB pode estar em qualquer lugar.
  Distinguir explicitamente.
- **NUNCA tratar uma decisão como sinalização inequívoca da próxima.**
  Comunicação do BCB é frequentemente data-dependent.
- **NÃO embrulhar Itaú como "consenso de mercado"** — é a maior casa,
  mas é UMA casa. Nomeá-la.
- **NUNCA dizer "BCB indicou corte/alta" sem citação direta.** Quando
  o BCB diz, está nas atas e comunicados. Citar o trecho.
- **CUIDADO com Galípolo vs predecessores.** Continuidade vs ruptura
  pode ser superinterpretada. Quando relevante, citar o que mudou em
  comunicação, não em decisão.
