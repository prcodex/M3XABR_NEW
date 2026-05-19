# LESSONS — coding & structuring lessons earned in m3xabr-core

**Scope:** patterns and gotchas specific to *building* this repo. Architectural choices that paid off, mistakes worth not repeating, conventions adopted after a real bug taught us why.

**Not scope:** operational lessons from running a deployed M3xA system (those live in the M3xA House MCP at `mind_lessons.md`). This file is *just* about coding and structuring m3xabr-core itself.

**Convention:** newest at the top. Each entry has a date, one-line summary, a brief "what happened" + "what to do" body. Keep terse — the next agent reading this is on a clock.

---

## 2026-05-19 · Mermaid `click` directives only fire on Mermaid blocks, not static SVG embeds

**What happened.** The initial commit rendered both diagrams as `<img src="docs/diagrams/*.svg">` because it lets the SVG carry styling that the Mermaid pipeline would otherwise lose. But GitHub's static-SVG `<img>` doesn't honor per-element click events. Wanting clickable nodes meant switching to inline Mermaid code blocks (which GitHub renders natively *and* respects `click` directives in).

**What to do.** Pick one:
- (a) Static SVG `<img>` = nice typography, can't make nodes clickable.
- (b) Inline Mermaid code block = clickable nodes via `click NodeId "url"`, but typography is GitHub's Mermaid theme (less control).

For m3xabr-core we picked (b). If you regenerate diagrams via `mermaid-cli` for offline use, keep both — the SVG for fallback, the `.mmd` source as the authoritative version with `click` directives mirrored.

---

## 2026-05-19 · Self-knowledge layer is opt-in for every file, enforced by CI

**What happened.** Building BODY.md taught us that ad-hoc documentation conventions ("please remember to update BODY when you change X") don't survive multiple contributors or multiple AI tools editing concurrently. The only mechanism that scales is **CI failure**.

**What to do.** When you introduce a convention that requires hand-maintenance:
1. Make it auto-maintainable where possible (`<!-- AUTOGEN:start:... -->` blocks + a generator script).
2. For the parts that CAN'T be auto-maintained, write a **sync check** (`tools/check_*.py`) that asserts the convention is met, run it in both pre-commit AND CI.
3. Skip the "honor system" entirely. The pre-commit hook can be bypassed (`--no-verify`); CI cannot. Both layers needed.

The autogen + CI pattern adds ~30 minutes per convention but pays back the first time someone forgets to update a doc.

---

## 2026-05-19 · Per-tool pointer files are 5-line stubs, not duplicates

**What happened.** Different AI coding tools each have their own "read this first" convention file: `CLAUDE.md` (Claude Code), `.cursor/rules/*.mdc` (Cursor), `.github/copilot-instructions.md` (GitHub Copilot). The tempting wrong move is to copy the project orientation into all three. That creates 3-way drift.

**What to do.** Make BODY.md (or `AGENTS.md`) the source of truth. Each per-tool file is a 5-line pointer:
```
**Authoritative spec:** [BODY.md](./BODY.md). Read it first.
**Lessons:** [LESSONS.md](./LESSONS.md).
**Stack registry:** [docs/stack/](./docs/stack/).
... 3 hard rules tool-specific syntax cares about ...
```

Three pointers, one source. Editing BODY.md updates every tool. The pointers themselves rarely change — they're closer to constants than documents.

---

## 2026-05-19 · Vendor SDKs live in `backends/` only

**What happened.** The temptation when writing `actors/router.py` is to import `anthropic` directly and call `client.messages.create(...)` inline — it's faster than going through an abstraction. The reason not to is that **every actor with a direct SDK import becomes a swap-blocker** when you want to test with a fake LLM, fork for a different provider, or wrap with telemetry.

**What to do.** All vendor SDK imports stay in `m3xabr_core/backends/{llm,embeddings,vector_db}.py`. Actors take a `backend` parameter (interface), never instantiate clients themselves. Tests inject fakes via the backend interface.

The discipline cost: ~15 LOC of abstraction per backend. The payoff: every test runs without API keys, every actor is provider-agnostic.

---

## 2026-05-19 · Router output schema is the cross-actor contract

**What happened.** Designing the router's return shape (`{"expertises": [...], "confidence": float, "rationale": str}`) felt arbitrary at the time. It became the keystone: assembler depends on the `expertises` list, evaluator uses `confidence`, debugging uses `rationale`. Changing it later would have rippled across 4 files.

**What to do.** Pin cross-actor schemas in `m3xabr_core/schemas.py` early. Treat them like API contracts — version bump if breaking. Add a pytest that validates the shape (we have `test_router.py::test_router_validates_expertise_count` + `test_router_validates_confidence_range`).

---

## 2026-05-19 · pyproject.toml URLs are easy to forget when forking

**What happened.** The initial commit had placeholder URLs `your-username/m3xabr-core` in pyproject.toml's `Homepage`/`Documentation`/`Issues`. Force-pushing to `prcodex/M3XABR_NEW` succeeded but the URLs still pointed at the placeholder. Caught in the kickoff Step 3 review.

**What to do.** When the build process produces a tarball intended for re-homing, leave placeholders explicit (`your-username/REPO`) so they're obvious — not `prcodex/m3xabr-core` (which looks valid but might be wrong). The find/replace in Step 3 of the push kickoff is the right pattern.

---

## How to add a lesson

When you learn something architectural while editing this repo, add it to the top of the list. Format:

```
## YYYY-MM-DD · One-line summary

**What happened.** 2-4 sentences of context.

**What to do.** Bulleted or numbered actionable guidance for the next agent.
```

Keep entries under 200 words. If a lesson grows past that, it's a doc, not a lesson — move the doc to `docs/` and leave a 50-word pointer here.

Lessons age. If a lesson has been superseded (e.g., we adopted a tool that solved the problem), don't delete it — strike-through the title and add a `**Superseded by:** ...` line. History matters; the next agent might wonder why we did things the old way.

Archive once we hit ~30 lessons: move the bottom half to `docs/LESSONS_archive.md`. The top of this file stays scannable.
