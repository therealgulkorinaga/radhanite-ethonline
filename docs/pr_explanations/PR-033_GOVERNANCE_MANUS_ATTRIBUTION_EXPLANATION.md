# PR-033 — Manus textual attribution

**Implementation agent: Manus.**

## Purpose

This documentation-only governance amendment makes the current implementation
agent visible in every implementation step and in the durable records that carry
the work forward.

## What changed

The governance document now requires the exact bold line
`**Implementation agent: Manus.**` in implementation progress reports, commit
messages, pull-request descriptions, pull-request explanations, and handoff
reports. The README summarizes the rule, the prompt-preservation format lists
Manus as an agent option, and the authorizing prompt is preserved in `prompts/`.

## What did not change

This amendment does not create a GitHub account for Manus. It does not change
commit authorship metadata, repository permissions, runtime behavior, tests,
task semantics, economic rules, APIs, dependencies, or architecture. Arko
remains the human product owner and merge authority. Codex remains the
independent review agent.

## Tests

No runtime tests were changed. Documentation validation consists of a clean
diff check and a repository-wide search confirming that the required attribution
wording is present in the governance and README process records.

## How to explain this to a judge

Manus is the implementation agent, but it does not have a separate GitHub user
account in this workflow. The repository therefore records Manus explicitly in
bold text at every implementation step without pretending that a GitHub account
or permissions exist.
