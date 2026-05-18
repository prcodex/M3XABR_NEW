# Architecture

This document covers the 7-actor pipeline in depth, the rationale for each design choice, and what's simplified in `m3xabr-core` vs a full production deployment.

## The pipeline at a glance

A user query passes through seven actors. Two of them (Router and Assembler) are what makes this architecture *expertise-composed* rather than monolithic. The rest are standard RAG plumbing: classify, retrieve, synthesize, evaluate.

```
USER QUERY
   │
   ▼
[Actor 1 — Classifier]       Haiku, extracts query metadata
   │
   ▼
[Actor 1.5 — Router]         Haiku, picks 1-3 expertises  ◄── NEW
   │
   ▼
[Actor 2 — Assembler]        File ops, concatenates expertise files  ◄── NEW
   │
   ├──► [Actor 3 — Agent Hub]    runs in parallel with Actor 4
   │
   └──► [Actor 4 — Retriever]    runs in parallel with Actor 3
   │
   ▼
[Actor 5 — Synthesizer]      Sonnet, produces the response
   │
   ▼
[Actor 7 — Evaluator]        Haiku, scores; auto-regen at 5.0 ≤ score < 7.0
   │
   ▼
RESPONSE + EVALUATION SCORE
```

### Why no Actor 6 (Format Enforcer) or Actor 8 (Delivery)?

In the live production agent that this repo is the stripped-down sibling of, Actor 6 carries Telegram-specific output rules and Actor 8 handles delivery. `m3xabr-core` is **surface-agnostic** — input is text, output is text. Consumers (a Telegram bot, a web UI, an API client) handle their own formatting concerns. This keeps the core pipeline focused on producing a good answer rather than producing a good answer *for a specific channel*.

If you fork this repo and need Telegram-specific rules, add an Actor 6 between Synthesizer and Evaluator, loading a `delivery_rules/telegram_output_rules.md` file via the same pattern as expertise composition.

## Actor 1 — Classifier

**Model:** Haiku
**Input:** raw user query
**Output:** `ClassifierOutput` schema (see `m3xabr_core/schemas.py`)
**Cost:** ~$0.0001 per query

Extracts structured metadata that downstream actors consume:
- `query_type`: info / analysis / comparison / release / forecast / drift / off_scope
- `time_window`: last_24h / last_7d / last_30d / last_90d
- `entities_mentioned`: normalized institution/person names
- `topics`: substantive topics
- `language`: pt-BR / en / mixed

The classifier doesn't pick expertises (that's Actor 1.5's job). It extracts *facts* about the query that everyone downstream needs.

## Actor 1.5 — Expertise Router

**Model:** Haiku
**Input:** query + ClassifierOutput
**Output:** `RoutingDecision` schema — kernel + scope_filter + 1-3 expertises + confidence
**Cost:** ~$0.0001 per query

The architectural centerpiece. Reads the query and classifier output, picks which expertise files to load. The router prompt (`config/router_prompt.md`) contains the description of each expertise; the model does semantic match.

Routing examples:
- "Como está o IPCA de março?" → `economic_releases`
- "O Itaú revisou Selic?" → `monetary_analysis` + `institutional_source_briefing` + `narrative_drift_detection`
- "Como o quadro fiscal afeta o Copom?" → `fiscal_analysis` + `monetary_analysis`
- "Quem está na frente nas pesquisas?" → `electoral_analysis`

**Conservative fallback.** If the router's `confidence` is < 0.7, the Assembler loads additional expertises matching `trigger_keywords` from the classifier output. The failure mode "loaded an irrelevant expertise" is much milder than "missed a relevant one."

**Why a separate Actor 1.5 instead of extending Actor 1?** Separation of concerns. Actor 1 extracts facts. Actor 1.5 makes a routing decision. These compose differently in the future — a different agent with the same Actor 1 might need a domain-specific Actor 1.5, while keeping Actor 1 stable.

## Actor 2 — Expertise Assembler

**Model:** none (pure file ops)
**Input:** `RoutingDecision`
**Output:** assembled system prompt (string)
**Cost:** zero

Reads the expertise files from `expertises/` and concatenates them in dependency order:

```
kernel → scope_filter → expertises (in routing order)
```

Frontmatter is stripped; only body content goes into the prompt. Files are separated by section breaks that the synthesizer can parse if needed.

**Per-query token math.** A typical query loads:
- Kernel (~900 tokens)
- Scope filter (~600 tokens)
- 1-3 expertises (~800-1,600 tokens each, depending on density)

Total measured (v0): **~2,300-6,000 tokens** of system prompt, vs ~6,800 for a monolithic soul covering everything. The variance comes from routing breadth — single-expertise queries are leaner than 3-expertise bridges. The win is greatest on focused queries (single domain) and smallest on cross-cutting queries. Even cross-cutting queries stay under monolithic, because the synthesizer never sees the irrelevant 4-5 expertises that monolithic would have loaded.

**Why an actor and not inline in the pipeline?** Testability. The assembler is the most-tested component (see `tests/test_assembler.py`) — token counts, frontmatter stripping, conservative fallback all need unit tests. Isolating it makes those tests trivial.

## Actor 3 — Agent Hub

**Model:** depends on agent (live data agents are stateless)
**Input:** `ClassifierOutput`
**Output:** `AgentContext` (list of labeled blocks)
**Cost:** varies by agent

Fires data agents in parallel. v0 ships with:

- **MarketsAgent** — live snapshot via yfinance (Ibovespa, USDBRL, S&P, DXY, oil, gold). Free, no API key. Always fires for Brazil queries — markets are background context.
- **PolymarketAgent** (stub) — fires only for electoral topics. Implement against Polymarket's Gamma API.
- **CalendarAgent** (stub) — for "what comes out this week" queries.
- **BoostAgent** (stub) — for entity-specific content boosting.

Failed agents return `None` and don't break the pipeline. Synthesizer can handle missing agent context — it's enrichment, not core data.

Extend by subclassing `DataAgent` and passing to `AgentHub(agents=[...])`.

## Actor 4 — Retriever

**Model:** embedding model (Voyage by default)
**Input:** query + `ClassifierOutput`
**Output:** list of `RetrievedDoc`
**Cost:** ~$0.00002 per query (Voyage embedding)

Embeds the query, searches the vector DB with domain filter, rescores by freshness.

**v0 scoring (in code):**

```
score = vector_weight × cosine_similarity + freshness_weight × exp(-age_days × decay_rate)
```

Defaults: `vector_weight=0.7`, `freshness_weight=0.3`, `decay_rate=0.05` (~14-day half-life).

**Production scoring (documented, not implemented in core):**

A real production deployment of this architecture uses a more sophisticated formula:

```
score = w_vector  × cosine_similarity
      + w_fresh   × exp(-age_days × decay_rate)
      + w_entity  × entity_boost(doc, classifier_output.entities_mentioned)
      + w_source  × source_tier(doc.source)
      + w_mg      × (macro_score if domain=macro else geo_score)
```

Where:
- `entity_boost` weights up docs from sources the user named ("what does Itaú think" → boost Itaú-sourced docs)
- `source_tier` reflects domain-expert ranking of source reliability (institutional research > major media > aggregators > social)
- `m/g scores` are pre-computed per-doc relevance scores for macroeconomic vs geopolitical framings, useful when one domain owns a query the other might bleed into

Implementing these in `m3xabr-core` is a matter of subclassing `Retriever` and overriding `_rescore`. They're omitted from core to keep the v0 readable.

**Top-K by query type:**

| query_type | top_k |
|---|---|
| info | 30 |
| analysis | 60 |
| comparison | 80 |
| release | 40 |
| forecast | 50 |
| drift | 80 |
| off_scope | 10 |

Different query shapes need different retrieval breadth. Comparison and drift queries need more docs to build the time-series view; pure info queries do well with fewer.

## Actor 5 — Synthesizer

**Model:** Sonnet
**Input:** `SynthesizerInput` (system prompt + dynamic context)
**Output:** response text
**Cost:** ~$0.01-0.04 per query depending on retrieval size

The big call. Receives the assembled system prompt from Actor 2 and a user-turn payload composed of:

1. `DATA WINDOW: last_7d` marker
2. Agent context (MARKET SNAPSHOT, etc.)
3. Retrieved docs (with source + date attribution)
4. Health caveats (if applicable — e.g., "polymarket data unavailable")
5. Session history (if multi-turn — last 10 turns)
6. The user query itself
7. Optional improvement hint from a regen pass

The synthesizer's system prompt is **dynamically composed** for each query. The savings vs monolithic comes from here — Sonnet sees only the rules relevant to the query type at hand.

**Temperature 0.3.** Low enough for reproducible analysis, high enough for natural prose. Not 0.0 — fully deterministic outputs read robotic for narrative responses.

## Actor 7 — Evaluator

**Model:** Haiku
**Input:** query + synthesized response
**Output:** `EvaluationResult` (score + rubric + improvement_hint + regen_recommended)
**Cost:** ~$0.0002 per query

Scores the response against a Portuguese rubric (`config/evaluator_prompt.md`):

- **grounding** (claims supported by retrieval)
- **citation** (institution + outlet + date)
- **clarity** (pt-BR analytical tone)
- **completeness** (essential elements covered)
- **no_fabrication** (no invented data/identities/projections) — *weighted double*
- **format_compliance** (pt-BR, no markdown tables, no ASCII art)

Overall score = weighted average. If `no_fabrication < 5.0`, score is capped at 4.0 — fabrication is the worst failure mode.

**Regen gate:**

- `score ≥ 7.0` → deliver
- `5.0 ≤ score < 7.0` → regen with `improvement_hint`; adopt regen only if score improves
- `score < 5.0` → deliver anyway, log loudly for soul correction

The regen path is one extra Sonnet call. Cost is real (~$0.01-0.04 again) but the quality improvement justifies it when the eval flagged a fixable issue.

## What this architecture is good at

**Token efficiency.** Per-query system prompt is 55-80% smaller than monolithic. Freed tokens go to retrieval, which is where the value is.

**Adding capabilities.** Drop a new `expertises/your_domain.md` file, add its description to `router_prompt.md`. Done. No code change. No risk of breaking other expertises.

**Pruning corrections.** Each expertise carries the failure-mode corrections relevant to its domain. When a query fires only `political_analysis`, the BRL-hours-as-live correction (which lives in `market_intelligence`) doesn't compete for attention.

**Routing accuracy as a measurable signal.** Every query's routing decision is logged. Periodic hand-audit on 50-100 queries flags wrong choices.

## What this architecture is bad at

**Adversarial queries that bridge many domains.** A query asking about fiscal, monetary, electoral, *and* market implications loads 4 expertises (~2,500-3,400 tokens combined). Per-query cost approaches monolithic. Mitigation: the router picks "top 3" by relevance; some signal is lost on truly cross-cutting queries.

**Cold-start.** A new domain that hasn't accumulated failure modes yet looks generic. Monolithic soul carries the wisdom of all past corrections; expertise composition starts each expertise with explicit drafting effort.

**Routing as a single point of failure.** If Actor 1.5 routes wrong 20% of the time, the agent's behavior degrades worse than monolithic — because the wrong expertise is *confidently* wrong, where a generalist would be vaguely right. Mitigation: conservative fallback, asymmetric scoring, routing audit.

## Comparison with the source production agent

The live production agent (M3xABR) that this repo is the open-source stripped-down sibling of differs in:

| | M3xABR (production) | m3xabr-core (this repo) |
|---|---|---|
| Soul | Monolithic `soul_brazil.md` (~6,800 tokens) | Expertise composition (~1,300-2,900 tokens) |
| Bot identity | Hard-coded `@M3xabr_bot` | `domain` query parameter |
| Surface | Telegram-specific | Surface-agnostic |
| Actor 6 | Telegram format enforcer | Removed |
| Actor 8 | Delivery via Telegram API | Removed |
| Retrieval scoring | Multi-factor (5 components) | Simplified (2 components, full formula documented) |
| Agent hub | Markets + Polymarket + Calendar + Boost | Markets real (yfinance); rest stubbed |
| Domain | Production with millions of docs | Designed for any LanceDB corpus you bring |

The migration path from production (monolithic) to expertise composition: A/B the two on the same corpus, evaluate with Actor 7, decide whether expertise composition is a strict improvement on response quality + token efficiency + extensibility. The architecture is built to be reversible — both code paths can coexist behind a feature flag.

## A note on Anthropic's Skills standard

Each expertise file is structured as a [SKILL.md](https://docs.claude.com/skills) — YAML frontmatter (`name`, `description`, `version`, `trigger_keywords`, `trigger_entities`) plus body. The Skills standard was designed for tool selection; we apply the same shape to prompt selection. The `description` field is what the router reads when deciding what loads. The discipline transfers: descriptions are the lever; frontmatter manages versions; the body is what concatenates.

If you maintain a fork, treat each expertise as you'd treat a tool definition — version it, write a tight description, list its triggers honestly.
