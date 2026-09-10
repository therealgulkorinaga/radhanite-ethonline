# Codex review — PR-025

**Pull request:** [#25](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/25) — The Graph replaces Privy on the active integration path
**Reviewer:** Codex (independent review agent, `AI_BUILD_GOVERNANCE.md` §1.3)
**Reviewed against:** `docs/ARCHITECTURE.md`, `docs/AI_BUILD_GOVERNANCE.md`, `docs/PREREQ-001_PRODUCT_DEFINITION.md`, `tasks/`
**Date issued:** 2026-09-11
**Outcome:** _pending — review not yet run_

---

## 0. Note on ordering

**This prompt is committed before the review runs**, as §7.3 requires, in the
same commit as the work — as it was for PR-022, PR-023 and PR-024.

## 1. Prompt issued

Recorded **before** the review was run.

```text
You are the independent review agent for the Radhanite repository, per
docs/AI_BUILD_GOVERNANCE.md §1.3.

Review pull request #25:
https://github.com/therealgulkorinaga/radhanite-ethonline/pull/25

Documentation and roadmap only. The human product owner deprioritized Privy and
put The Graph on the active integration path in its place. It authorizes no
implementation and must not change TASK-006.

Review against these authoritative documents ONLY:
  - docs/ARCHITECTURE.md
  - docs/AI_BUILD_GOVERNANCE.md
  - docs/PREREQ-001_PRODUCT_DEFINITION.md
  - tasks/

Do NOT treat docs/pr_explanations/PR-025_GOVERNANCE_EXPLANATION.md as evidence
of correctness (§4.3).

PART A — TASK-006 must be untouched

1. Confirm tasks/TASK-006_GENERALIZED_CAPABILITY_SELECTION.md is byte-identical
   to main, and that nothing under radhanite/ or tests/ changed.
2. §2.1 keeps provider and network identity outside selection. Confirm nothing
   in this PR weakens that, and that TASK-007's restatement of the prohibition
   is at least as strong as §2.1 rather than a softened paraphrase.
3. TASK-007 forbids a "trusted source" concept. Assess whether that closes the
   realistic loophole, or whether an information provider could still earn
   preference some other way the document does not name.

PART B — the deprioritization, and whether history survived

4. TASK-003's status is now DEPRIORITIZED / SUPERSEDED FOR CURRENT ETHONLINE
   BUILD. Confirm the specification BELOW that notice is unaltered — diff it and
   say so explicitly.
5. Confirm the three recorded reasons are stated, and assess whether the record
   reads as a priority decision rather than as a claim the original reasoning
   was wrong.
6. ARCHITECTURE §3.2 keeps Privy's argument about self-enforced spending limits
   being circular. Is keeping it correct, or does it now mislead a reader into
   thinking the work is planned?
7. Confirm no immutable review record or historical PR explanation was edited.

PART C — the new task

8. TASK-007 is a placeholder and is NOT AUTHORIZED. Confirm nothing in it, or in
   any document this PR touches, could be read as permission to build.
9. Assess the three unresolved decisions in §6. In particular §6.2: the economic
   rule requires a strictly positive price known BEFORE the purchase. Is a Graph
   capability satisfiable under TASK-006 §2.3 as written, or does this
   integration require a specification change nobody has proposed?
10. §6.3 says no authorized task owns the layer that turns evidence into a
    changed success probability. Verify that is true across tasks/, and say
    whether the roadmap is coherent without it.
11. The task number is TASK-007. The product owner proposed TASK-008. Confirm
    007 was genuinely free and that using it leaves no gap or collision.

PART D — consistency across the repository

12. Find EVERY remaining mention of Privy. For each, say whether it is correctly
    left as history, or whether it now states something untrue about the current
    plan.
13. Confirm the priority order — Hedera, then Circle/Arc, then The Graph — is
    stated consistently in ARCHITECTURE, BACKLOG, README and site/index.html,
    with no document still implying Privy is active.
14. site/index.html is committed under §3.2, which requires staleness to be
    corrected in the same pull request. Confirm the page no longer advertises
    Privy, that The Graph is marked not authorized ON the page, and that its
    provenance line is accurate.
15. Confirm no task other than TASK-007 changed authorization status, and that
    TASK-007 arrives unauthorized.

FORMAT OF YOUR FINDINGS

Number every finding, per §3.1:

    CODEX-PR025-01
    CODEX-PR025-02
    ...

For each: identifier, file and line, what is wrong, and which specification or
boundary it departs from.

If you find nothing, say so explicitly and raise no findings.

CONCLUDE

End with exactly ONE outcome, per §7.2:
  - Approved
  - Approved with corrections  (list the finding identifiers)
  - Rejected  (state which specification or boundary was departed from)
```

## 2. Findings returned

_Pending. Codex has not yet reviewed this pull request._

## 3. Outcome

_Pending._

## 4. Corrections

_None yet._
