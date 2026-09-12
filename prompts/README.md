# Preserved Prompts

This directory preserves the AI prompts that caused substantive changes to this
repository.

Radhanite is built primarily by AI agents. Preserving the instructions that
produced the work makes the project's provenance auditable: a reader can see not
just what the repository contains, but what was actually asked for — and can
check whether what was built matches what was requested.

This requirement comes from
[`AI_BUILD_GOVERNANCE.md`](../docs/AI_BUILD_GOVERNANCE.md) §5.

---

## What gets preserved

**Preserve** a prompt when it:

- authorized or specified a task,
- produced or substantially changed product code,
- changed the product definition, architecture, or governance,
- resulted in a review correction being applied,
- changed the direction of the project.

**Do not preserve**:

- trivial or mechanical requests ("fix this typo", "rerun the tests"),
- conversational back-and-forth that produced no repository change,
- anything containing secrets, credentials, or private data — this repository
  is public.

The goal is signal, not a transcript. A directory of everything is as useless as
a directory of nothing.

## Naming convention

```
prompts/NNN_short-description.md
```

`NNN` is a zero-padded sequence number in the order prompts were issued, so the
directory reads chronologically.

Example: `prompts/001_repository-governance-scaffolding.md`

## File format

Each preserved prompt is one file:

```markdown
# NNN — Short description

**Date:** YYYY-MM-DD
**Agent:** Manus | Claude Code | Codex | other
**Authority:** TASK-XXX, PREREQ-XXX, "governance amendment", or "review correction"
**Resulted in:** one line on what changed in the repository

## Prompt

> The prompt as issued, verbatim.

## Notes

Anything a later reader needs to interpret this: assumptions the agent made,
scope explicitly withheld, or corrections that followed.
```

The prompt is recorded **verbatim**. It is not cleaned up, summarized, or
improved after the fact — an edited prompt cannot serve as a record of what was
actually asked.

## Relationship to commits

A preserved prompt records the *instruction*. A commit records the *change*.
Both are required, and neither replaces the other: commit messages must still
explain changes in plain English and reference their authorizing task,
prerequisite, governance amendment, or review correction, per
`AI_BUILD_GOVERNANCE.md` §3.
