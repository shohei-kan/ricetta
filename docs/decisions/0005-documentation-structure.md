# 0005 Documentation Structure

## Date

2026-05-05

## Status

Accepted

## Context

Ricetta uses handoff documents so future agents can continue development without re-reading the full project history.

The previous `docs/handoff/latest.md` was starting to accumulate multiple work phases, which made it less useful as a current-state handoff.

## Decision

Ricetta uses the following documentation structure:

```text
docs/handoff/latest.md
docs/handoff/archive/
docs/handoff/archive/index.md
docs/decisions/
```

`docs/handoff/latest.md` contains only the latest current state and the next recommended work.

`docs/handoff/archive/` stores previous handoffs by broad topic, not by every single task.

Archive files use broad topic names such as:

```text
planning-and-docs.md
backend-foundation.md
frontend-implementation.md
release-prep.md
```

Inside each archive file, entries are separated by date and title headings.

`docs/handoff/archive/index.md` is a table of contents for archive files. It lists archive files and their broad purpose, not every detailed entry.

Long-term decisions belong under `docs/decisions/`. Ricetta does not use a root-level `decisions/` directory.

## Reasons

- `latest.md` stays short and useful for the next agent.
- Past context remains searchable without overwhelming the current handoff.
- Durable decisions are separated from short-lived working context.
- Archive files avoid excessive fragmentation.

## Consequences

- Agents must archive or summarize old handoff content before replacing `latest.md`.
- Similar handoff entries should be appended to the existing broad archive file.
- New archive files should be created only when a new broad work area appears.

## Related Docs

- `AGENTS.md`
- `docs/handoff/latest.md`
- `docs/handoff/archive/index.md`
