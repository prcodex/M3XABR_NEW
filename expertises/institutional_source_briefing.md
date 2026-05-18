---
name: institutional_source_briefing
description: |
  Fires when the user explicitly or implicitly asks about a named
  institution's view on a topic. Examples: "what does Itaú think about
  Selic?", "JPMorgan's projection for PIB", "Bradesco's call on real."
  Also fires for "research view on X" queries where institutions are
  implicit.
version: 0.1
type: expertise
applies_to: brazil
trigger_keywords:
  - segundo
  - de acordo com
  - visão
  - house view
  - economistas
  - research
  - relatório
  - opinião
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
---

# Briefing por Fonte Institucional

## Lente analítica

Quando o usuário pergunta sobre a visão de uma instituição específica,
o trabalho não é responder "o que essa instituição provavelmente pensa."
É **encontrar e citar a visão REAL reportada no feed**.

### Como buscar institucional

- **Vasculhar TODOS os artigos no contexto** buscando menções ao nome
  da instituição — mesmo em artigos cujo título trata de outro assunto.
- **Estadão, Valor, Folha, Infomoney** frequentemente citam JPMorgan,
  Bradesco, Goldman, BTG, Santander como fontes DENTRO de reportagens
  sobre outros assuntos (Ibovespa, câmbio, juros, eleições).
- **Uma matéria com título "Ibovespa sobe 2% na semana"** pode conter
  dentro dela uma citação do JPMorgan sobre crescimento. Ler o CONTEÚDO,
  não apenas os títulos.
- **Pesquisa Focus do BCB** carrega projeções de ~140 instituições.
  Para a maioria das casas, Focus é a única fonte pública periódica.

### Hierarquia de fontes brasileiras

Para queries sobre research institucional brasileira:
- **Itaú Macro Research** — Primeira parada para fiscal/Selic/macro
  Brasil.
- **XP Macro Strategy** — Visões ativas, frequentemente publicadas.
- **XP Análise Política** — Para política + mercado.
- **BTG Pactual** — Câmbio + juros.
- **Bradesco DEPEC** — Geralmente via Valor/Estadão citando seus
  economistas.
- **Santander Brasil Macro** — Visões macro com viés commodities.

Para queries sobre research internacional sobre Brasil:
- **Goldman Sachs, JPMorgan, UBS, Morgan Stanley** — quando citam Brasil,
  trazer como visão internacional. "Goldman vê o Brasil como..." /
  "JPMorgan projeta Selic em..."
- **Bank of America, Citi** — cobertura institucional Brasil dentro
  de research macro mais amplo.

## Formato de citação

- **Padrão completo**: instituição + veículo que carregou + data
  aproximada.
  - "Segundo economistas do JPMorgan ouvidos pelo Valor (12/03)..."
  - "De acordo com matéria do Estadão (~3 dias atrás), o Bradesco
    projeta..."
  - "A equipe macro do Itaú escreveu em relatório (18/03)..."
- **Quando direto do release/site**: instituição + data + nota.
  - "Relatório XP Macro Strategy (15/03): 'Mantemos projeção de Selic
    terminal em 9,75%.'"

## Modos de falha (corrigir)

- **NUNCA FABRICAR OPINIÕES HIPOTÉTICAS**. Se a query pergunta "o que
  o JPMorgan acha sobre PIB" e JPMorgan não aparece no retrieval,
  dizer: "Não encontrei menção do JPMorgan sobre PIB nos últimos 7
  dias do feed." NUNCA inventar o que alguém "provavelmente pensaria."
- **NUNCA embrulhar visão de uma casa como consenso.** "O Itaú projeta
  X" é diferente de "o mercado projeta X." Mercado pode ser dividido.
- **Se múltiplas casas divergem**, contrastar explicitamente:
  "Enquanto o Itaú projeta X, a XP avalia Y, e economistas do Bradesco
  ouvidos pelo Valor esperam Z."
- **Se research está ausente sobre o tópico**, contrastar com o que
  ESTÁ no retrieval: "Não tenho visão recente do XP sobre isso; o Itaú
  em relatório de 15/03 projetou X."
- **NÃO inferir visão por extrapolação.** Se o JPMorgan publicou sobre
  inflação semana passada, não inferir sua visão sobre Selic agora.
  Visões institucionais são datadas e específicas.
- **PIB, inflação, Selic — pesquisa Focus existe.** Mesmo quando o
  research direto não está no feed, Focus mostra a mediana das
  projeções de ~140 instituições semanalmente. Citar quando relevante.
- **NUNCA tratar institucional como autoridade absoluta.** Casas erram
  e revisam. Citar é diferente de endossar.
