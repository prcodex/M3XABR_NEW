---
name: economic_releases
description: |
  Fires for queries about Brazilian economic data releases — just-
  published numbers, this week's calendar, market reaction to releases.
  Includes GDP (PIB), IPCA and IPCA-15 inflation prints, IBC-Br monthly
  activity proxy, industrial production (PIM-PF), retail (PMC), services
  (PMS), employment (PNAD, Caged), confidence surveys (ICC, ICEI, ICI,
  ICS), PMI, capacity utilization. Also handles the release calendar —
  what's coming, when, with consensus expectations.
version: 0.1
type: expertise
applies_to: brazil
trigger_keywords:
  - saiu
  - divulgação
  - release
  - publicado
  - calendário
  - calendário econômico
  - esta semana
  - hoje
  - amanhã
  - PIB
  - IPCA
  - IPCA-15
  - IBC-Br
  - PIM
  - PIM-PF
  - PMC
  - PMS
  - PNAD
  - Caged
  - ICC
  - ICEI
  - ICI
  - ICS
  - PMI
  - desemprego
  - emprego formal
  - produção industrial
  - varejo
  - serviços
  - confiança
  - capacidade
  - utilização
trigger_entities:
  - ibge
  - fgv
  - bcb
  - caged
  - anfavea
  - mdic
---

# Releases Econômicos Brasileiros

## O que esta expertise cobre

Foco em **dados publicados e calendário de divulgação**. Não cobre
projeções — essas vão para `economic_forecasts`. Dispara quando o
usuário pergunta sobre:

- Indicador recém-divulgado (PIB do trimestre, IPCA do mês, IBC-Br,
  PIM, PMC, PMS, PNAD, Caged, etc.)
- O que sai esta semana / hoje / amanhã no calendário econômico
- Reação de mercado a uma divulgação
- Comparação do dado vs consenso / vs período anterior / vs ano anterior
- Composição do indicador (ex: quais componentes do IPCA puxaram)

Frequentemente carregada com `economic_forecasts` — "IPCA saiu, casas
vão revisar?" carrega ambas.

## Fontes primárias

- **IBGE** — Calendário público com 6 meses de antecedência. Releases
  diários com horário definido (geralmente 9h BRT).
  - PIB: trimestral, ~60 dias após trimestre
  - IPCA: mensal, ~10 dias após mês de referência
  - IPCA-15: prévia, ~5 dias antes do final do mês de referência
  - PIM-PF: mensal, ~1 mês após mês de referência
  - PMC, PMS: mensal, ~45-50 dias após mês de referência
  - PNAD Contínua: mensal, ~45 dias após trimestre móvel
- **FGV/Ibre** — Sondagens (ICI Indústria, ICS Serviços, ICOM Comércio,
  ICST Construção), ICC (Consumidor), IGP-M, IGP-DI. Calendário próprio.
- **BCB** — IBC-Br (atividade mensal, ~45 dias após mês), Relatório
  Trimestral de Inflação. Notas estatísticas mensais.
- **Caged (Ministério do Trabalho)** — Saldo de emprego formal mensal,
  ~30 dias após mês de referência.
- **MDIC** — Balança comercial, diária e mensal.
- **ANFAVEA** — Produção e vendas de veículos, primeira semana do mês
  seguinte. Proxy precoce de atividade.
- **S&P Global / Markit** — PMI manufaturas + serviços, primeiro dia
  útil do mês seguinte.

## Convenções de leitura

- **PIB**:
  - T/T-1 com ajuste sazonal (manchete principal)
  - 4T acumulado (visão anual)
  - YTD (acumulado no ano)
  - Sempre especificar qual está sendo citada
  - Decomposição lado da oferta (agro/indústria/serviços) e lado da
    demanda (consumo/investimento/gov/externo)
- **IPCA**:
  - m/m (variação no mês)
  - acumulado 12 meses (foco principal — é o que o BCB persegue)
  - acumulado no ano
  - Sempre os três quando disponíveis
  - Decomposição por grupos (alimentação, moradia, transporte,
    saúde, etc.) e por núcleos (medianas, médias aparadas)
- **IPCA-15**: prévia, sai antes do mês de referência terminar. Tratar
  como sinal antecipado, não substituto do IPCA cheio.
- **IBC-Br**: proxy mensal do PIB com m/m sazonalmente ajustado +
  acumulado 12 meses. Útil para "como atividade foi em [mês]" antes
  do PIB sair.
- **PIM-PF**: produção industrial, m/m sazonalmente ajustado (manchete),
  acumulado 12 meses, ano contra ano. Decomposição por categoria
  econômica (bens de capital, intermediários, consumo).
- **PMC**: varejo, ampliado vs restrito. Ampliado inclui veículos e
  materiais de construção; restrito é mais conservador. Manchete
  geralmente é o ampliado.
- **PMS**: serviços, total e desagregado por atividade.
- **PNAD Contínua**: trimestre móvel, divulgada mensalmente. Desemprego
  é a manchete; rendimento médio e ocupação são igualmente
  informativos.
- **Caged**: saldo do mês (admitidos − desligados). Comparar com
  consenso de mercado e mesmo mês do ano anterior.

## Lente analítica

Para um dado recém-divulgado, a ordem:

1. **O número** (com unidade e período de referência)
2. **Vs consenso de mercado** (Focus, Reuters, Broadcast, Bloomberg)
3. **Vs release anterior** (mesma série, período anterior)
4. **Vs mesmo período do ano anterior** (onde faz sentido sazonalmente)
5. **Decomposição** se relevante (componentes que puxaram)
6. **Reação de mercado** se já houve

Para calendário: cronológico com horário BRT, indicador, consenso
esperado, peso para mercado.

**Surpresa direcional**: classificar "veio acima/abaixo/em linha" com
magnitude em desvios-padrão da expectativa quando possível.

## Formato de output

- **Snapshot de release**: tabela `<pre>` com Indicador, Período,
  Valor, Consenso, Anterior, Surpresa. Depois 2-3 parágrafos curtos
  com interpretação.
- **Calendário**: lista cronológica formato
  "DIA HH:MM BRT — Indicador (consenso: X)".

## Modos de falha (corrigir)

- **NUNCA arredondar números de release.** IPCA 0,67% é 0,67%, não
  "cerca de 0,7%". Dados são FATOS.
- **NUNCA confundir IPCA-15 com IPCA cheio.** Sempre explicitar qual.
- **NUNCA citar "PIB" sem qualificar**: T/T sazonalmente ajustado,
  4T acumulado, ou YTD são números distintos.
- **NUNCA confundir produção industrial com PIB industrial** (séries
  distintas, PIM-PF é mensal, PIB industrial é trimestral via PIB).
- **NUNCA citar reação de mercado a um release sem hora.** Ibovespa
  pode estar negativo por outro motivo; pareie a reação à hora do
  release.
- **NUNCA confundir Caged com PNAD.** Caged é emprego formal (CLT);
  PNAD é universo trabalhista total (formal + informal). Histórias
  diferentes.
- **NUNCA inferir tendência de um único release.** Um IPCA acima do
  consenso não é "inflação acelerou" — é um release. Múltiplos
  releases formam tendência.
- **CUIDADO com ajuste sazonal vs sem ajuste.** Sempre especificar.
- **NÃO citar PIB sem decomposição quando relevante** — números
  agregados escondem histórias setoriais.
