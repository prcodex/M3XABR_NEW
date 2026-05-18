# Routing Decisions

How Actor 1.5 (the Expertise Router) disambiguates between expertises with overlapping domains. This is the practical reference for understanding why a given query loads what it loads.

## The four-way macro split

The hardest disambiguation is among the four macro expertises. They share institutional voices (Itaú, XP, BTG, Goldman, JPMorgan) but split by *what they cover*:

| | Primary content | Time orientation |
|---|---|---|
| `monetary_analysis` | Interest rate policy | Forward-looking (next Copom) + reactive (just-decided) |
| `fiscal_analysis` | Government finance | Both — released data + forward trajectory |
| `economic_releases` | Just-published indicators | Backward (what happened) + calendar (what's coming) |
| `economic_forecasts` | Institutional projections | Forward (what's expected) |

The rule: **read the substance of the query, not the speaker.** Galípolo (BCB president) commenting on fiscal is fiscal content delivered through a monetary voice. `monetary_analysis` fires because BCB voice is one of its sources; `fiscal_analysis` fires because the substance is fiscal. Both load.

### Decision matrix

| Query | Routes to | Reasoning |
|---|---|---|
| "O que o Itaú projeta para Selic?" | `monetary_analysis` | Selic projection, monetary domain |
| "O Itaú revisou Selic?" | `monetary_analysis` + `narrative_drift_detection` + `institutional_source_briefing` | Revision = drift; institution-named = source briefing |
| "Como está o resultado primário?" | `fiscal_analysis` | Pure fiscal query |
| "A dívida pública está sob controle?" | `fiscal_analysis` | Sustainability question |
| "Quanto cresceu o PIB no 1T?" | `economic_releases` | Released data |
| "IPCA de março subiu o quê?" | `economic_releases` | IPCA-as-release |
| "O que o BCB faz dado o IPCA atual?" | `monetary_analysis` + `economic_releases` | IPCA-as-monetary-input + the release itself |
| "O Copom vai cortar?" | `monetary_analysis` | Forward monetary call |
| "O que o JPMorgan acha do fiscal?" | `fiscal_analysis` + `institutional_source_briefing` | Fiscal + institution-named |
| "Por que o BCB pode hesitar em cortar?" | `monetary_analysis` (BCB reasoning) + `fiscal_analysis` (if user mentions fiscal as reason) | Bridge query |
| "Como o Brasil está crescendo vs expectativas?" | `economic_releases` + `economic_forecasts` | Released vs projected |
| "Galípolo falou sobre fiscal hoje" | `monetary_analysis` (BCB voice) + `fiscal_analysis` (substance) | Voice-vs-substance split |
| "Itaú vs XP em PIB 2026?" | `economic_forecasts` + `institutional_source_briefing` | Cross-house projection |
| "Selic given fiscal" | `monetary_analysis` + `fiscal_analysis` | Explicit bridge |
| "Como o Goldman mudou BRL?" | `market_intelligence` + `narrative_drift_detection` + `institutional_source_briefing` | FX drift from named institution |

## Routing principles

**Pick 1-3 expertises.** Never zero — the conservative fallback loads more when uncertain, not none. Never more than 3 — beyond that, system prompt approaches monolithic.

**Tie-break = load both.** When in doubt between two adjacent expertises, the router loads both. The extra ~600-900 tokens is cheap; the cost of missing a relevant expertise is higher than the cost of including an irrelevant one.

**Drift always pairs.** `narrative_drift_detection` virtually never fires alone — it pairs with the topical expertise. "How did X change" is a comparison shape applied to some substantive domain.

**Source briefing pairs when named.** `institutional_source_briefing` fires whenever the user names an institution. Pairs with whatever topical expertise the institution is being asked about.

**Off-scope still routes.** The router doesn't refuse to route an off-scope query — it picks expertises that *would* apply if the query were in scope. The kernel + scope filter handle the decline. This keeps the routing logic uniform.

## The conservative fallback

When `routing.confidence < 0.7`, the Assembler (Actor 2) loads additional expertises matching the classifier's `entities_mentioned` or `topics` against each expertise's `trigger_keywords` and `trigger_entities`.

Capped at 3 additional expertises beyond the router's pick, to prevent the system prompt from ballooning past monolithic.

Example: query "como Galípolo vê a economia" — router might be uncertain (could be `monetary_analysis` because Galípolo, could be `economic_releases` because "economia"). With confidence 0.6, the fallback also pulls in any expertise where Galípolo appears in `trigger_entities` — both `monetary_analysis` and `fiscal_analysis` qualify. Three expertises load.

## Routing accuracy as a signal

Every routing decision is logged in `PipelineResult.routing_decision`. For ongoing quality monitoring:

1. Sample 50 queries/week (random across the week)
2. For each, the auditor reviews query + retrieved docs + router decision
3. Mark: ✅ correct, ⚠️ partial (missing relevant or loaded irrelevant), ❌ wrong
4. Target: ≥80% ✅, ≤5% ❌

If routing accuracy drops below threshold, **edit expertise descriptions** in `expertises/*.md` and `config/router_prompt.md`. Don't restructure the router — the model is fine; the lever is what it reads.

## Adding a new expertise

To extend the routing:

1. Create `expertises/your_new_expertise.md` with proper frontmatter:
   - `name`: kebab_case identifier
   - `description`: 1-3 sentences describing what fires this expertise (the router reads this)
   - `trigger_keywords`: pt-BR words the classifier might extract
   - `trigger_entities`: institutions/people relevant to this domain
2. Add a paragraph to `config/router_prompt.md` under "Expertise descriptions" with the new expertise's role.
3. Add 1-2 routing examples involving the new expertise to the prompt.
4. Optionally: add unit tests in `tests/test_router.py` covering hand-labeled queries that should route to the new expertise.

No code changes needed. The assembler reads from `expertises/` at startup.
