# Contributing

Thanks for your interest in `m3xabr-core`. A few notes on how to extend it usefully.

## Adding a new expertise

The most common contribution. Add a new file at `expertises/<your_name>.md`:

1. **Frontmatter** (required):
   - `name`: snake_case identifier matching the filename
   - `description`: 1-3 sentences. **The router reads this** — be specific about what fires this expertise.
   - `version`: semver
   - `type`: `expertise`
   - `applies_to`: `brazil`
   - `trigger_keywords`: pt-BR words the classifier might extract
   - `trigger_entities`: institutions/people the classifier might extract

2. **Body** — markdown sections covering:
   - What this expertise covers (and what it doesn't)
   - Source hierarchy
   - Conventions specific to this domain
   - Analytical lens
   - Output format preferences
   - Failure modes (corrections)

3. **Update** `config/router_prompt.md`:
   - Add a paragraph under "Expertise descriptions" with the new expertise's role
   - Add 1-2 routing examples

4. **Test** the routing with `tests/test_router.py` — hand-label queries that should route to your expertise, verify with a real LLM via integration tests.

No code changes needed for new expertises. The assembler reads from `expertises/` at startup.

## Modifying an existing expertise

1. Bump the `version` in frontmatter
2. Edit the body
3. Run `pytest tests/test_assembler.py` to verify token counts haven't ballooned
4. Add a row to a CHANGELOG entry (informally, in the commit message) describing what changed

## Adding a custom data agent

In `m3xabr_core/actors/agent_hub.py`:

```python
class MyAgent:
    name = "MY_DATA"
    
    def fire(self, classifier_output):
        if "my_trigger_topic" not in classifier_output.topics:
            return None
        # ... your data fetch ...
        return AgentBlock(name=self.name, content="...", timestamp=...)
```

Register it: `hub.register(MyAgent())` or pass to `AgentHub(agents=[..., MyAgent()])`.

The agent must:
- Have a `name: str` class attribute
- Implement `fire(classifier_output) -> AgentBlock | None`
- Return `None` cleanly if not applicable (don't raise)
- Be resilient to network failures (catch internally)

## Adding a new dependency

Every external package the repo depends on must have a registered doc under `docs/stack/`. CI fails the build if you add to `pyproject.toml` without doing this.

1. Add the package to `[project.dependencies]` (or the appropriate extras group) in `pyproject.toml`.
2. Scaffold the doc — copy the most complete existing one as a template:
   ```bash
   cp docs/stack/anthropic.md docs/stack/<new-name>.md
   $EDITOR docs/stack/<new-name>.md
   ```
   Fill in: what it does, where it's used in m3xabr-core, why we picked it, alternatives considered, how to swap it out, links.
3. Verify the check passes:
   ```bash
   python tools/check_stack_in_sync.py
   ```
4. Regenerate `BODY.md` so the stack table reflects the new row:
   ```bash
   python tools/regenerate_body.py
   ```
5. Stage and commit `pyproject.toml`, the new `docs/stack/<new-name>.md`, and the updated `BODY.md` together.

See `docs/stack/README.md` for the doc template and the rationale.

## Swapping backends

Implement the protocol in `m3xabr_core/backends/`:

```python
class MyLLMBackend:
    def complete(self, *, model, system, user, max_tokens=4096, temperature=0.0):
        return "your provider's response"
```

Then `Pipeline(llm=MyLLMBackend(), ...)`.

Same shape for `EmbeddingBackend` and `VectorDBBackend`. See protocols in the respective `.py` files.

## Code style

- Python 3.11+
- Type hints required for all public functions
- `ruff check m3xabr_core/ tests/` before committing
- `mypy m3xabr_core/` before committing
- Tests: `pytest tests/`

## What this repo is not

- **Not a place for a different domain's content.** German energy markets, US tech, Greek politics — fork the repo and replace `expertises/`. Don't add `expertises/greek_politics.md` here. The architecture generalizes; the Brazilian content is the demo.
- **Not a place for production deployment code.** Telegram bots, FastAPI services, scheduled ingestion — those go in your fork. The core stays library-shaped.
- **Not a place for a full ingestion pipeline.** Bring your own corpus.

## Pull requests welcome for

- New expertise files (Brazilian domain only)
- Improvements to existing expertise content (failure modes captured from real responses)
- Backend implementations (Qdrant, Weaviate, pgvector, etc.)
- Test coverage improvements
- Documentation improvements
- Mermaid diagram improvements

Open an issue first if the change is structural (touches the actor protocol or pipeline orchestration).
