# AGENTS — entry point for AI coding tools

You are an AI tool (Claude Code, Cursor, GitHub Copilot, Aider, etc.) reading this repo. Start here.

## Read order

1. **[BODY.md](./BODY.md)** — the authoritative infrastructure map. Architecture invariants, actor list, expertise pool, dependency stack, env vars, public API surface. Auto-maintained; trust it.
2. **[LESSONS.md](./LESSONS.md)** — coding / structuring lessons earned while building this repo. Don't repeat the mistakes already documented.
3. **[docs/stack/README.md](./docs/stack/README.md)** — registry of every external tool the repo depends on. One doc per tool, with the rationale + alternatives.
4. **[ARCHITECTURE.md](./ARCHITECTURE.md)** — narrative-style architecture description for humans. Overlaps with BODY.md but tells the *why*.
5. **[README.md](./README.md)** — public-facing project description.

## What this is

A reference library for **expertise-composed LLM agents** over a Brazilian-macro vector corpus. Library, not service. Small (~3K LOC). Pipeline-shaped. See BODY.md.

## What you must not do

- **Don't merge actors.** The 7-actor pipeline is the architectural contract.
- **Don't add vendor SDK imports outside `m3xabr_core/backends/`.** Backends are pluggable; protect that.
- **Don't add a new dependency without registering a `docs/stack/<name>.md` page.** CI will fail.
- **Don't hand-edit content inside `<!-- AUTOGEN:start:... -->`...`<!-- AUTOGEN:end:... -->` markers in BODY.md.** It gets regenerated.
- **Don't break the public API in `m3xabr_core/__init__.py`** without a version bump + CHANGELOG entry.

## What you should do

- **Before committing**, run `python tools/regenerate_body.py` (or rely on the pre-commit hook). Keeps BODY.md in sync with code.
- **When adding a new external tool**, run `python tools/check_stack_in_sync.py --template <toolname>` to scaffold the docs page.
- **When you learn something architectural**, append a row to `LESSONS.md`. Keep it terse; the next agent reading is on a clock.

## Tool-specific notes

- **Claude Code:** also see [`CLAUDE.md`](./CLAUDE.md) (same content; CLAUDE.md is the convention name).
- **Cursor:** rules at [`.cursor/rules/m3xabr.mdc`](./.cursor/rules/m3xabr.mdc).
- **GitHub Copilot Workspace:** [`.github/copilot-instructions.md`](./.github/copilot-instructions.md).

All three pointer files re-export BODY.md as the source of truth. There's one spec; only one place to update.
