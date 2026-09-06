# PR Explanations

This directory holds a plain-English explanation document for every pull request
in this repository.

These files are **intentionally committed to GitHub**. They are part of the
project's public record, not scratch notes.

Required by
[`AI_BUILD_GOVERNANCE.md`](../AI_BUILD_GOVERNANCE.md) §4.

---

## Why this exists

Radhanite is built largely by AI agents, which can produce a lot of change
quickly. Without a deliberate explanation, the only people who can understand a
change are those willing to read the diff.

These documents let the **human product owner, reviewers, hackathon judges, and
future contributors** understand what a change does and why — **without reading
source code**.

## Rules

1. **Every pull request must have one.** A PR without an explanation file is
   incomplete and must not be merged.
2. **Write it for a non-technical reader.** Use technical terms only where
   genuinely necessary, and explain each one immediately in ordinary English.
3. **It is not a source of truth.** The product definition, architecture
   documents, task specifications, code, and tests are authoritative. This
   document only explains them.
4. **Codex reviews the code, not this file.** An independent reviewer must
   verify the implementation against the authoritative materials and must never
   treat this explanation as evidence that the implementation is correct.
5. **Be honest.** Failing tests, stubs, and load-bearing assumptions are stated
   outright. A readable document that omits a limitation is worse than no
   document.

## Naming convention

```
docs/pr_explanations/PR-<NNN>_TASK-<NNN>_EXPLANATION.md
```

Example:

```
docs/pr_explanations/PR-001_TASK-001_EXPLANATION.md
```

The PR number, the authorized task the PR implements, and the `_EXPLANATION`
suffix. For a pull request that resolves a review correction rather than a task,
substitute the review reference in the middle position.

## Required structure

Every explanation must cover all fifteen items below, in this order.

```markdown
# PR-<NNN> — <short title>

**Pull request:** #<NNN>
**Authorized task:** TASK-<NNN>
**Author:** <implementing agent>

## 1. Purpose of this PR
## 2. What changed
## 3. Why the change was needed
## 4. How this worked before
## 5. How it works after
## 6. What goes into the system
     Important inputs, data, and state entering the system.
## 7. What the system decides
## 8. What comes out
     Outputs and state changes.
## 9. How it can fail
     Failure modes.
## 10. Tests run and their results
## 11. Assumptions made
## 12. Known limitations
## 13. Explicitly out of scope
## 14. Deferred to future tasks
## 15. How to explain this to a judge
```

Section 15 is a short summary a reader could say out loud to someone
encountering Radhanite for the first time. It is not a marketing section — it
still has to be true.

## Index

No pull requests have been opened yet. This section will list them as they land.
