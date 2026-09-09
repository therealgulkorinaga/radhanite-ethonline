# Codex review — PR-021

**Pull request:** [#21](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/21) — TASK-006: the candidate capability model
**Reviewer:** Codex (independent review agent, `AI_BUILD_GOVERNANCE.md` §1.3)
**Reviewed against:** `tasks/TASK-006_GENERALIZED_CAPABILITY_SELECTION.md`, `docs/PREREQ-001_PRODUCT_DEFINITION.md`, `docs/ARCHITECTURE.md`, `docs/AI_BUILD_GOVERNANCE.md`
**Date issued:** 2026-09-09
**Outcome:** **Approved** — no findings

---

## 0. Governance disclosure — read this first

Two things about this record are not what §7.3 requires, and both are stated
rather than glossed.

> **1. The prompt was committed after the review had already run.** §7.3
> requires it to be committed first, for a stated reason: *"A prompt recorded
> afterwards can be quietly reshaped to fit the answer it received."* That
> protection was not in place for this review.

The prompt in §1 is nonetheless **exact**. It was issued to the reviewer in full
before the review ran and is reproduced here unchanged — but that is a fact
about this particular record, not a substitute for the ordering rule, and it
cannot be verified from the repository alone.

> **2. The reviewer's verbatim response was not supplied** to the agent writing
> this record. The outcome below — Approved, no findings — is **as relayed by
> the human product owner**.

Nothing has been invented to fill that gap. §2 says what is known and marks
exactly what is missing. If the verbatim response is available it should replace
§2, and this second disclosure should be struck.

**This is the third consecutive review with a §7.3 ordering deviation** — PR-017,
PR-020 (unreviewed), and now PR-021. That is a pattern in how this project runs
reviews rather than three separate lapses, and it is recorded here so it is
visible as one.

## 1. Prompt issued

Recorded **after** the review was run, per §0. Exact text as issued:

```text
You are the independent review agent for the Radhanite repository, per
docs/AI_BUILD_GOVERNANCE.md §1.3.

Review pull request #21:
https://github.com/therealgulkorinaga/radhanite-ethonline/pull/21

This is the FIRST implementation step of TASK-006, which the human product owner
authorized in PR #20. It delivers the candidate model only. It must contain no
economic rule.

Review against these authoritative documents ONLY:
  - tasks/TASK-006_GENERALIZED_CAPABILITY_SELECTION.md
  - docs/PREREQ-001_PRODUCT_DEFINITION.md
  - docs/ARCHITECTURE.md
  - docs/AI_BUILD_GOVERNANCE.md

Do NOT treat docs/pr_explanations/PR-021_TASK-006_EXPLANATION.md as evidence of
correctness (§4.3).

PART A — scope

1. TASK-006 §2 is authorized; §3 is not. Confirm nothing in the diff implements
   eligibility, ranking, tie-breaking, consumed-ID tracking, the step ceiling,
   candidate generation, task-state evaluation, or execution.
2. validate_candidates has no caller in this PR. Is delivering it now correct as
   a specified §2.2 behaviour, or is it an abstraction ahead of its use and
   therefore ARCHITECTURE §6 item 7? Give a clear answer either way.
3. Confirm no dependency, credential, or configuration was added.

PART B — provider neutrality (§2.1)

4. Confirm the Candidate carries exactly three fields and that no field, method,
   comment, or test name could let the rule distinguish one supplier from
   another.
5. A test reads the module source for forbidden words. Assess whether that test
   is meaningful or defeatable — for example by a word not on its list, or by
   the concept arriving without the word.

PART C — the positive-cost invariant (§2.5 A)

6. Confirm cost must be strictly positive, and that zero is refused.
7. §2.5 A frames this as a termination safeguard, not an economic rule. Is the
   implementation placed correctly — at construction rather than in a decision —
   and does the error message make the distinction clear enough that a later
   reader would not relax it as an over-strict business rule?
8. Does refusing zero at construction conflict with anything in TASK-001, whose
   Strategy permits a zero escalation cost? TASK-006 §7 records this narrowing;
   verify that account is accurate.

PART D — the boundary checks (§2.2)

9. Duplicate identifiers must be refused, not resolved. Verify, and check the
   refusal cannot be bypassed.
10. Assess the refusal of unordered collections. The stated reason is run-record
    reproducibility rather than selection determinism. Is that reasoning sound,
    and is it consistent with TASK-001's select() refusing unordered catalogues
    for a different reason?
11. Identifiers are compared case-sensitively and padded identifiers are
    refused. Are those the right calls, and are they specified anywhere or
    invented here?
12. Confirm validate_candidates returns a copy the caller cannot mutate.

PART E — what must NOT be validated

13. TASK-006 §2.3 decides whether a candidate is worth buying. Confirm the
    Candidate makes no such judgement — a hopeless or unaffordable candidate
    must be a valid object. This is the mistake CODEX-PR006-04 caught in
    TASK-001.

PART F — tests

14. The PR claims 36 new tests and that five deliberate faults were each caught.
    Verify the tests actually detect what they claim rather than passing
    vacuously. Look specifically for assertions that would pass whatever the
    code does.
15. Verify the exact-money and probability semantics are preserved: no float
    anywhere, and all arithmetic through Money and Probability.
16. Verify the claimed counts independently: 242 existing tests unchanged, 278
    total, on Python 3.12.

FORMAT OF YOUR FINDINGS

Number every finding, per §3.1:

    CODEX-PR021-01
    CODEX-PR021-02
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

**None.** No finding was raised.

**The reviewer's verbatim response is not recorded here**, because it was not
supplied to the agent writing this record — §0. What is known is the outcome, as
relayed by the human product owner: **Approved**.

§7.3 requires findings to be recorded verbatim and never summarized. There are
no findings to summarize, so nothing has been softened or dropped — but the
reasoning behind the approval, and the reviewer's answers to the specific
questions in §1, are absent from this record and should not be assumed. In
particular the record cannot show how the reviewer answered:

- **Part A question 2** — whether `validate_candidates`, which has no caller in
  this pull request, is a correctly-scoped §2.2 behaviour or an abstraction
  ahead of its use under `ARCHITECTURE.md` §6 item 7;
- **Part B question 5** — whether the source-scanning test for provider names is
  meaningful or defeatable;
- **Part D question 11** — whether case-sensitive comparison and the refusal of
  padded identifiers are specified or were invented in implementation.

Those were the three places the implementing agent expected a finding. An
approval answers them, but this record does not carry the answers.

## 3. Outcome

**Approved.** No findings, no corrections required, no unauthorized scope
identified.

Under §7.2 this means the work matches the specification and the product owner
may merge.

## 4. Corrections

**None.** No findings were raised, so there was nothing to correct.
