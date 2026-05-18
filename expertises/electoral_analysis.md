---
name: electoral_analysis
description: |
  Fires for queries about Brazilian elections, polling, candidates,
  voting intention, electoral scenarios. Includes presidential races,
  gubernatorial, congressional. Handles Polymarket cross-reference for
  political prediction markets. Active especially around 2026
  presidential cycle.
version: 0.1
type: expertise
applies_to: brazil
trigger_keywords:
  - eleição
  - eleições
  - pesquisa
  - Datafolha
  - Quaest
  - Atlas
  - Ipec
  - intenção de voto
  - primeiro turno
  - segundo turno
  - candidato
  - rejeição
  - cenário eleitoral
  - simulação
trigger_entities:
  - datafolha
  - quaest
  - atlas
  - ipec
  - poder360
  - pesquisas_vlm
  - polymarket
---

# Análise Eleitoral

## Hierarquia de institutos de pesquisa

- **Datafolha** — Maior amostra histórica, série mais longa, benchmark
  metodológico. Pesquisas presenciais.
- **Quaest** — Cadência semanal, frequentemente o dado mais atual.
  Telefone + presencial.
- **Atlas** — Alta frequência, amostras menores, online.
- **Ipec** — Sucessor do IBOPE, frequência menor, presencial.
- **Pesquisas VLM** — Agregador via leitura de gráficos publicados pelos
  institutos. Atualiza diariamente.
- **Poll Scanner** — Outro agregador, cobertura ampla.

## Lente analítica

- **Mostrar evolução temporal**: como os candidatos se moveram?
  Comparar com leitura anterior do MESMO instituto (não com instituto
  diferente — diferenças metodológicas confundem o sinal temporal).
- **Comparar institutos quando disponível**: Datafolha 32% vs Quaest
  30% vs Atlas 31%. Apresentar lado a lado.
- **Notar diferenças metodológicas**: presencial vs telefone vs online,
  tamanho de amostra, margem de erro.
- **Pesquisas são FATO**: reportar números exatos, NUNCA arredondar.
  Datafolha disse 32%, não "cerca de 30%."
- **Margem de erro**: incluir quando relevante para interpretar mudanças.

## Cross-reference Polymarket

- **Só mencionar Polymarket se há dados no contexto.** Se silêncio do
  agente Polymarket, silêncio na resposta.
- **NUNCA sinalizar ausência** ("sem dados do Polymarket disponíveis").
  Silêncio total é a regra.
- **Threshold de 2pp para inclusão narrativa**: só comentar Polymarket
  se houve mudança >2pp (dia ou semana).
- **Formato de contraste**: "Enquanto Datafolha mostra Lula em 32%,
  Polymarket precifica reeleição em 41%."
- **NÃO criar correlações artificiais**. Não explicar "por que Polymarket
  precifica X enquanto pesquisa mostra Y" a menos que haja movimento
  recente >2pp.

## Tipos de query e formato

**Pesquisa única (release recente)**:
- Snapshot do instituto + comparação com leitura anterior do mesmo
- Tabela `<pre>` compacta: Candidato, % atual, % anterior, var.
- Caveat: metodologia, data de campo, amostra

**Comparação cross-instituto**:
- Tabela `<pre>`: Instituto, Data, Top 3 candidatos
- MAX 30 chars de largura
- Bullets abaixo para divergências metodológicas

**Pergunta sobre tendência**:
- Evolução temporal em prosa, ancorada em datas
- Múltiplos institutos como check cruzado
- Polymarket como sinal complementar se >2pp move

## Modos de falha (corrigir)

- **NÃO forçar correlação Polymarket** quando mercado está flat.
- **NÃO arredondar pesquisas** (32%, não "~30%").
- **NÃO embrulhar institutos como "as pesquisas mostram X"** — nomear
  cada um.
- **NÃO sinalizar ausência de Polymarket** — silêncio total quando
  ausente.
- **NÃO comparar institutos diferentes na mesma série temporal** sem
  explicar a diferença metodológica.
- **CUIDADO com cenários eleitorais simulados.** Datafolha "se Lula
  enfrentar Tarcísio no 2º turno" é simulação, não previsão. Reportar
  como simulação metodológica.
- **NUNCA inventar candidatos** que não aparecem no retrieval.
