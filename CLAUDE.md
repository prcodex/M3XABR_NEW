# CLAUDE.md — Claude Code orientation

You are Claude Code working in the `m3xabr-core` repo.

**Authoritative spec:** [BODY.md](./BODY.md). Read it first. Everything below is a pointer.

**Lessons earned:** [LESSONS.md](./LESSONS.md). Don't repeat documented mistakes.

**External tools:** [docs/stack/README.md](./docs/stack/README.md). Every dependency has a registered doc; CI fails if a new one isn't registered.

**Convention entry point (cross-tool):** [AGENTS.md](./AGENTS.md). Same content, tool-agnostic.

## Hard constraints (also in BODY.md)

- 7-actor pipeline is the architectural contract. Don't merge or reorder actors.
- Vendor SDK imports stay in `m3xabr_core/backends/`. Don't leak `anthropic.Anthropic()` or `voyageai.Client()` calls into actor files.
- AUTOGEN blocks in BODY.md are off-limits to hand-edits. Run `python tools/regenerate_body.py` to refresh.
- New dependency → `pyproject.toml` + `docs/stack/<name>.md`. Both, every time. CI checks.

## Before committing

```bash
python tools/regenerate_body.py        # updates BODY.md AUTOGEN blocks
python tools/check_stack_in_sync.py    # verifies every dep has a doc
pytest tests/                          # 16+ tests; should all pass
```

The pre-commit hook runs these for you, but `--no-verify` bypasses it. CI runs them too, so the bypass just delays the failure.
