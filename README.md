# m3xabr-core

> A reference implementation of expertise-composition architecture for a Brazilian intelligence agent.

`m3xabr-core` is a query infrastructure that answers Portuguese-language questions about Brazilian politics, economics, and markets by composing small expertise modules at query time, rather than loading a single large system prompt.

It's the stripped-down sibling of a live production agent — the architecture, expertise prompts, and orchestration code, without the deployment specifics. Clone it, point it at your own LanceDB corpus and API keys, and run it as a library, a CLI, or a service.

## What's interesting about it

Most RAG agents load a monolithic system prompt — every rule the system has ever needed, on every query. As the prompt grows, attention gets diluted, token budget gets eaten, and adding a new capability means editing a global file that already covers ten others.

**Expertise composition** flips this. A kernel holds identity and grounding rules. A `scope filter` bounds the corpus. Everything else — fiscal analysis, monetary policy, polling discipline, market conventions, drift detection — lives in **9 separate expertise files**. A cheap Haiku call routes each query to the 1-3 expertises that actually apply.

The result: per-query system prompt of **~2,300-6,000 tokens** depending on routing breadth (1-3 expertises loaded), vs ~6,800 for a static monolithic soul that always loads everything. The architecture is genuinely modular — adding a `commodity_analysis` expertise is one new file plus one line in the router prompt.

## The pipeline

![Pipeline diagram](docs/diagrams/pipeline.svg)

Seven actors process a query in sequence. The two teal boxes (Router and Assembler) are what makes this architecture *expertise-composed* rather than monolithic. Everything else is standard RAG plumbing.

```mermaid
flowchart TD
    Q[User query]
    A1[Actor 1 — classifier<br/>Haiku · query metadata]
    A15[Actor 1.5 — router<br/>Haiku · picks expertises]
    A2[Actor 2 — assembler<br/>File ops · no LLM call]
    A3[Actor 3 — agent hub<br/>Brazil subset]
    A4[Actor 4 — retriever<br/>LanceDB · domain=brazil]
    A5[Actor 5 — synthesizer<br/>Sonnet · pt-BR response]
    A7[Actor 7 — evaluator<br/>Haiku · PT rubric, regen gate]
    R[Response + score]

    Q --> A1 --> A15 --> A2
    A2 --> A3
    A2 --> A4
    A3 --> A5
    A4 --> A5
    A5 --> A7 --> R

    classDef new fill:#ccfbf1,stroke:#14b8a6,stroke-width:1.5px;
    classDef base fill:#f3f4f6,stroke:#9ca3af,stroke-width:1px;
    class A15,A2 new;
    class Q,A1,A3,A4,A5,A7,R base;

    click Q "https://github.com/prcodex/M3XABR_NEW/blob/HEAD/m3xabr_core/cli.py" "Entry point — cli.py" _self
    click A1 "https://github.com/prcodex/M3XABR_NEW/blob/HEAD/m3xabr_core/actors/classifier.py" "Open classifier.py" _self
    click A15 "https://github.com/prcodex/M3XABR_NEW/blob/HEAD/m3xabr_core/actors/router.py" "Open router.py" _self
    click A2 "https://github.com/prcodex/M3XABR_NEW/blob/HEAD/m3xabr_core/actors/assembler.py" "Open assembler.py" _self
    click A3 "https://github.com/prcodex/M3XABR_NEW/blob/HEAD/m3xabr_core/actors/agent_hub.py" "Open agent_hub.py" _self
    click A4 "https://github.com/prcodex/M3XABR_NEW/blob/HEAD/m3xabr_core/actors/retriever.py" "Open retriever.py" _self
    click A5 "https://github.com/prcodex/M3XABR_NEW/blob/HEAD/m3xabr_core/actors/synthesizer.py" "Open synthesizer.py" _self
    click A7 "https://github.com/prcodex/M3XABR_NEW/blob/HEAD/m3xabr_core/actors/evaluator.py" "Open evaluator.py" _self
    click R "https://github.com/prcodex/M3XABR_NEW/blob/HEAD/m3xabr_core/pipeline.py" "Pipeline orchestrator — pipeline.py" _self
```

## The expertise pool

```mermaid
flowchart TB
    subgraph always["Always loaded · ~600 tokens"]
        K[Kernel<br/>~400 tokens]
        SF[Scope filter — Brazil<br/>~200 tokens]
    end

    subgraph macro["Macro lens — four expertises"]
        MON[Monetary<br/>Selic · Copom · BCB<br/>~600 tokens]
        FIS[Fiscal<br/>Primário · dívida · Tesouro<br/>~900 tokens]
        ECR[Eco releases<br/>PIB · IPCA · calendar<br/>~850 tokens]
        ECF[Eco forecasts<br/>Focus · house views<br/>~900 tokens]
    end

    subgraph other["Other expertises"]
        ELE[Electoral<br/>~700 tokens]
        POL[Political<br/>~800 tokens]
        MKT[Markets<br/>~500 tokens]
        SRC[Source briefing<br/>~600 tokens]
        DRI[Drift detection<br/>~500 tokens]
    end

    classDef purple fill:#ede9fe,stroke:#8b5cf6;
    classDef teal fill:#ccfbf1,stroke:#14b8a6;
    class K,SF purple;
    class MON,FIS,ECR,ECF,ELE,POL,MKT,SRC,DRI teal;

    click K "https://github.com/prcodex/M3XABR_NEW/blob/HEAD/expertises/m3xabr_kernel.md" "Open kernel" _self
    click SF "https://github.com/prcodex/M3XABR_NEW/blob/HEAD/expertises/scope_filter_brazil.md" "Open scope filter — Brazil" _self
    click MON "https://github.com/prcodex/M3XABR_NEW/blob/HEAD/expertises/monetary_analysis.md" "Open monetary_analysis.md" _self
    click FIS "https://github.com/prcodex/M3XABR_NEW/blob/HEAD/expertises/fiscal_analysis.md" "Open fiscal_analysis.md" _self
    click ECR "https://github.com/prcodex/M3XABR_NEW/blob/HEAD/expertises/economic_releases.md" "Open economic_releases.md" _self
    click ECF "https://github.com/prcodex/M3XABR_NEW/blob/HEAD/expertises/economic_forecasts.md" "Open economic_forecasts.md" _self
    click ELE "https://github.com/prcodex/M3XABR_NEW/blob/HEAD/expertises/electoral_analysis.md" "Open electoral_analysis.md" _self
    click POL "https://github.com/prcodex/M3XABR_NEW/blob/HEAD/expertises/political_analysis.md" "Open political_analysis.md" _self
    click MKT "https://github.com/prcodex/M3XABR_NEW/blob/HEAD/expertises/market_intelligence.md" "Open market_intelligence.md" _self
    click SRC "https://github.com/prcodex/M3XABR_NEW/blob/HEAD/expertises/institutional_source_briefing.md" "Open institutional_source_briefing.md" _self
    click DRI "https://github.com/prcodex/M3XABR_NEW/blob/HEAD/expertises/narrative_drift_detection.md" "Open narrative_drift_detection.md" _self
```

11 markdown files total. The router picks 1-3 conditional expertises per query, alongside the always-loaded kernel + scope filter. The Brazilian macro split (monetary / fiscal / economic releases / economic forecasts) reflects the actual analytical decomposition of the domain — Selic is monetary; primary deficit and debt are fiscal; IPCA-as-release is economic; house projections are forecasts.

## Quickstart

### Install

```bash
git clone https://github.com/prcodex/M3XABR_NEW.git
cd M3XABR_NEW
pip install -e ".[markets,dev]"
```

### Set API keys

```bash
export ANTHROPIC_API_KEY=sk-ant-...
export VOYAGE_API_KEY=pa-...
```

### Index a corpus

The pipeline expects a LanceDB table named `unified_feed` with columns `id`, `text`, `source`, `published_at`, `domain`, `content_vector`, `has_vector`. See [docs/SCHEMA.md](docs/SCHEMA.md) for the full schema. For a smoke test, the `examples/sample_corpus/` directory contains 8 stub documents you can ingest.

### Run a query

```bash
m3xabr query "Como está o IPCA?" --lancedb ./lancedb_data
m3xabr query "O Itaú revisou a projeção de Selic?" --debug
m3xabr expertises  # list available expertises
```

### Use as a library

```python
from m3xabr_core import Pipeline

pipeline = Pipeline(lancedb_path="./lancedb_data")
result = pipeline.run("O que o Goldman pensa sobre BRL?")

print(result.response)
print(f"Score: {result.score:.1f}/10.0")
print(f"Loaded: {result.routing_decision.expertises}")
print(f"System tokens: {result.estimated_system_tokens}")
```

## Repository layout

```
m3xabr-core/
├── README.md                    # this file
├── LICENSE                      # MIT
├── ARCHITECTURE.md              # the 7-actor pipeline in depth
├── pyproject.toml
├── config/
│   ├── classifier_prompt.md     # Actor 1 prompt
│   ├── router_prompt.md         # Actor 1.5 prompt
│   ├── evaluator_prompt.md      # Actor 7 prompt (Portuguese rubric)
│   └── retrieval_scoring.yaml   # Actor 4 weights + model config
├── expertises/                  # the 11 files
│   ├── m3xabr_kernel.md
│   ├── scope_filter_brazil.md
│   ├── monetary_analysis.md
│   ├── fiscal_analysis.md
│   ├── economic_releases.md
│   ├── economic_forecasts.md
│   ├── electoral_analysis.md
│   ├── political_analysis.md
│   ├── market_intelligence.md
│   ├── institutional_source_briefing.md
│   └── narrative_drift_detection.md
├── m3xabr_core/                 # the Python package
│   ├── pipeline.py              # orchestrator
│   ├── cli.py                   # CLI entrypoint
│   ├── schemas.py               # Pydantic actor contracts
│   ├── actors/                  # 7 actor implementations
│   └── backends/                # pluggable LLM / embedding / vector DB
├── docs/
│   ├── ROUTING_DECISIONS.md     # how the router disambiguates
│   └── diagrams/                # SVG + Mermaid source
├── tests/                       # routing + assembly + pipeline tests
└── examples/                    # sample queries + stub corpus
```

## Customization

**Swap the embedding provider.** Default is Voyage (multilingual, strong on Portuguese). Set `M3XABR_EMBEDDER=openai` and provide `OPENAI_API_KEY` to use OpenAI instead, or implement `EmbeddingBackend` for your provider of choice.

**Swap the vector DB.** Default is LanceDB. Implement `VectorDBBackend` (see `m3xabr_core/backends/vector_db.py`) for Qdrant, Weaviate, pgvector, Pinecone, anything with vector + metadata filter support.

**Add a custom expertise.** Drop a new `expertises/your_expertise.md` file with YAML frontmatter following the SKILL.md schema. Update `config/router_prompt.md` to include the description. No code changes needed — the assembler reads from the directory at startup.

**Add a custom data agent.** Subclass `DataAgent` in `m3xabr_core/actors/agent_hub.py` and pass to `AgentHub(agents=[...])`. The v0 ships with a working markets agent (yfinance) and stubs for polymarket, calendar, and boost.

**Tune the router's routing.** Edit the expertise `description` fields and the routing examples in `config/router_prompt.md`. The router is one Haiku call reading these — descriptions are the lever.

## How the router decides

See [docs/ROUTING_DECISIONS.md](docs/ROUTING_DECISIONS.md) for the disambiguation logic between adjacent expertises (e.g., monetary vs fiscal vs economic releases — what fires on "Itaú's view on Selic given fiscal pressure?").

## What this isn't

- **Not a framework.** It's a reference implementation. The Brazilian domain is hard-coded; the *architecture* is what generalizes. To build an expertise-composed agent for another domain (German energy markets, Greek politics, US tech), fork this and replace the `expertises/` directory.
- **Not a complete RAG system.** No ingestion pipeline. You bring your own corpus and indexer. The repo ships with a tiny stub corpus in `examples/sample_corpus/` for smoke tests only.
- **Not production-ready as deployed.** The retrieval scoring is simplified (vector + freshness only). The full M3xA production scoring (entity boost + source tier + M/G scores) is documented in `ARCHITECTURE.md` and implementable by extending the `Retriever` class.

## Architecture rationale

Long version in [ARCHITECTURE.md](ARCHITECTURE.md). Short version:

| | Monolithic soul | Expertise composition |
|---|---|---|
| Per-query system prompt | ~6,800 tokens (static) | ~2,300-6,000 tokens (dynamic by routing) |
| Adding a capability | Edit one growing file | Add one file |
| Routing | None | One Haiku call |
| Failure modes carried | Globally (every query) | By expertise (only when that expertise fires) |
| Attention dilution | High | Low |

The architectural bet: a router-driven dynamic composition is a strict improvement on a static system prompt for any agent with more than one analytical mode. Validate by A/B against monolithic on the same corpus; the evaluator (Actor 7) scores both and the comparison is empirical.

## Self-knowledge layer

Everything above describes how the **agent** works. This section describes how the **repo** stays coherent — a body-of-knowledge layer that lets coding tools (Claude Code, Cursor, GitHub Copilot, Aider) edit safely without first paging in 3K lines.

The intuition: a small, accurate, auto-maintained map beats a sprawling, eventually-stale wiki. When BODY.md drifts from the code, CI fails the build.

### The loop

```mermaid
flowchart LR
    DEV[Developer / AI coding tool<br/>edits a file]
    HOOK[Pre-commit hook<br/>regenerate_body.py]
    BODY[BODY.md<br/>updated AUTOGEN sections]
    CI[CI · body_in_sync<br/>+ stack_in_sync]
    PR[PR merges]
    TOOL[Next coding agent reads<br/>BODY.md as ground truth]

    DEV --> HOOK --> BODY --> CI --> PR --> TOOL
    TOOL -. starts a new edit .-> DEV

    classDef teal fill:#ccfbf1,stroke:#14b8a6,stroke-width:1.5px;
    classDef purple fill:#ede9fe,stroke:#8b5cf6;
    class HOOK,CI teal;
    class BODY,TOOL purple;

    click HOOK "https://github.com/prcodex/M3XABR_NEW/blob/HEAD/tools/regenerate_body.py" "regenerate_body.py" _self
    click BODY "https://github.com/prcodex/M3XABR_NEW/blob/HEAD/BODY.md" "BODY.md" _self
    click CI "https://github.com/prcodex/M3XABR_NEW/blob/HEAD/.github/workflows/body_in_sync.yml" "body_in_sync workflow" _self
```

The loop is self-closing: every change to actors, expertises, dependencies, tests, or the public API forces a BODY.md regeneration; CI re-runs the same check; the resulting BODY.md is what the next coding agent reads before its first edit.

### The four pieces

| File | What it is | Who maintains it |
|---|---|---|
| [`BODY.md`](./BODY.md) | Live infrastructure map — actor list, expertise inventory, dependency table, env vars, test inventory, public API surface, file tree. The body of the system. | Auto (sections between `<!-- AUTOGEN -->` markers) + hand-written invariants at the top |
| [`AGENTS.md`](./AGENTS.md) | Cross-tool entry point — the file any AI coding tool reads first to find BODY.md, LESSONS.md, docs/stack/ | Hand-written |
| [`LESSONS.md`](./LESSONS.md) | Append-only log of coding lessons learned (the *why* behind structural choices: vendor SDK isolation, router schema contract, Mermaid-over-SVG for clickability, etc.) | Hand-written, by humans or coding agents after a fix |
| [`docs/stack/*.md`](./docs/stack/) | One doc per external dependency — what it does, why we picked it, alternatives, how to swap it out. CI fails if a `pyproject.toml` dep is missing its doc. | Hand-written; existence enforced |

### Per-tool entry points

The same self-knowledge is surfaced to each coding tool through the file *it* looks for:

- [`AGENTS.md`](./AGENTS.md) — the open convention (Aider, Cline, generic agents)
- [`CLAUDE.md`](./CLAUDE.md) — Claude Code
- [`.cursor/rules/m3xabr.mdc`](./.cursor/rules/m3xabr.mdc) — Cursor 0.46+
- [`.github/copilot-instructions.md`](./.github/copilot-instructions.md) — GitHub Copilot Workspace

All four are thin pointers that say the same thing: **read BODY.md first, then LESSONS.md, then docs/stack/.** This is intentional — one source of truth, four well-known doorways.

### Enforcement, three layers deep

1. **Pre-commit hook** (`.pre-commit-config.yaml`) — regenerates BODY.md and runs the stack check on every commit. Local fast feedback.
2. **CI workflows** (`.github/workflows/body_in_sync.yml`, `stack_in_sync.yml`) — re-run on push/PR. Catches `--no-verify` bypass and web-editor commits.
3. **pytest mirrors** (`tests/test_body_in_sync.py`, `tests/test_stack_in_sync.py`) — fail the local test suite if either drifts. Catches it before the developer pushes.

The redundancy is deliberate: pre-commit is fast but bypassable, CI is unbypassable but slow, pytest catches it during normal `pytest tests/` runs. Belt + suspenders + airbag.

### Self-healing — what's next

BODY.md is the **spec layer** that future self-healing logic builds on. The roadmap (see the table in `BODY.md` itself):

- ✅ **Spec** — BODY.md declares what "working" looks like.
- 🟡 **Drift detector** — `tests/test_body_in_sync.py` catches doc-vs-code drift at CI time. A future `validate_runtime.py` will check live config against the spec at pipeline boot.
- 🔮 **Auto-heal actor** — Future Actor 8 that detects missing expertise files, malformed router output, or env-var gaps and fails with repair instructions rather than cryptic stack traces.

### Coding lessons

[`LESSONS.md`](./LESSONS.md) is the project's memory for *structural* mistakes — patterns we've burned hours on, captured so the next agent (human or AI) doesn't repeat them. Examples already in:

- *Mermaid `click` directives only fire on inline code blocks, not `<img>` SVG embeds* — the lesson behind the clickable diagrams above.
- *Vendor SDKs live inside `backends/` only* — preserves the swap surface.
- *Router output schema is a contract, not a suggestion* — downstream actors hard-depend on `{expertises, confidence, rationale}`.

Add a new lesson when you fix something whose root cause was a structural choice you wouldn't have known to look for. Skip it for ordinary bugs.

## License

MIT. See [LICENSE](LICENSE).

## Acknowledgements

Architecture inspired by [Anthropic's Skills standard](https://docs.claude.com/skills) — each expertise file is a SKILL.md with frontmatter the router reads to decide what loads. The standard was designed for tool selection; this is the same shape applied to prompt selection.
