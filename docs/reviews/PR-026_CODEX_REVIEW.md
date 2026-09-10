# Codex review — PR-026

**Pull request:** [#26](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/26) — TASK-006 closure: fixtures, compatibility proof, and run policy
**Reviewer:** Codex (independent review agent, `AI_BUILD_GOVERNANCE.md` §1.3)
**Reviewed against:** `tasks/TASK-006_GENERALIZED_CAPABILITY_SELECTION.md`, `tasks/TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md`, `docs/ARCHITECTURE.md`, `docs/AI_BUILD_GOVERNANCE.md`
**Date issued:** 2026-09-11
**Outcome:** _pending — review not yet run_

---

## 0. Note on ordering

**This prompt is committed before the review runs**, as §7.3 requires, in the
same commit as the work — as it was for PR-022 through PR-025.

## 1. Prompt issued

Recorded **before** the review was run.

```text
You are the independent review agent for the Radhanite repository, per
docs/AI_BUILD_GOVERNANCE.md §1.3.

Review pull request #26:
https://github.com/therealgulkorinaga/radhanite-ethonline/pull/26

It closes out the three outstanding TASK-006 §5 deliverables: declared candidate
fixtures, the Criterion 14 compatibility proof, and max_capability_steps
supplied as explicit run policy. It must implement nothing else.

Review against these authoritative documents ONLY:
  - tasks/TASK-006_GENERALIZED_CAPABILITY_SELECTION.md
  - tasks/TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md
  - docs/ARCHITECTURE.md
  - docs/AI_BUILD_GOVERNANCE.md

Do NOT treat docs/pr_explanations/PR-026_TASK-006_EXPLANATION.md as evidence of
correctness (§4.3).

PART A — Criterion 14, the claim that matters most

1. TASK-006 §7 requires the compatibility claim to be DEMONSTRATED BY TEST and
   says outright that if the demonstration fails the claim is withdrawn rather
   than qualified. Assess tests/test_compatibility.py against that standard.
2. Independently identify the authoritative TASK-001 decision branches — from
   TASK-001 §2.5's "Properties of the rule that must be preserved", from
   tests/test_escalation.py, and from DECLARED_STRATEGIES. Then say whether the
   compatibility module covers ALL of them or has gaps.
3. Verify the harness genuinely runs BOTH models and compares them, rather than
   asserting an expected value it computed once. A test that only checks the new
   model against a hard-coded expectation is not a compatibility proof.
4. Verify it compares the arithmetic (incremental expected value), not only the
   verdict.
5. §7 maps the initial attempt to the baseline and the escalation to one
   candidate. Confirm the harness implements THAT mapping and not a convenient
   variant.
6. The PR claims every scenario agrees. Verify independently. A single
   disagreement is a Rejected outcome, not a finding to correct.

PART B — the one narrowing

7. §7 records that a zero-cost escalation is expressible in TASK-001 and cannot
   be a candidate under §2.5 A. Confirm TheOneNarrowingTests proves all three
   parts, and that no declared strategy is affected.
8. Assess whether scoping Criterion 14 to the declared fixtures is faithful to
   §7, or whether it is a weakened test the instruction forbade.

PART C — the fixtures

9. Confirm DECLARED_CANDIDATES uses the existing Candidate model, has stable
   unique IDs, exact Money and Probability, is immutable, deterministically
   ordered, and carries no provider, network, payment or sponsor identity.
10. Confirm it is not a discovery mechanism and makes no API call.
11. Assess the size. §5 says "sufficient", and the PR asserts a cap of five.
    Is three enough for Criterion 14, and is the cap a real guard?
12. Assess the provider-word scan test: meaningful, or defeatable by a word not
    on its list?

PART D — the run policy

13. Confirm RunPolicy has NO default, rejects zero, negatives, non-integers and
    bool, is immutable, and carries only max_capability_steps.
14. RunPolicy requires >= 1 while eligibility's primitive tolerates 0. Judge
    whether that divergence is coherent or a latent inconsistency.
15. Confirm the policy VALUE actually reaches eligibility and selection, and
    that no default or literal ceiling exists anywhere in radhanite/.
16. The PR says a source-scanning test was REPLACED during implementation
    because it flagged a doctest call site. Assess whether the replacement is
    stronger or whether a real guard was lost.
17. Confirm RunPolicy implements no loop, increments no counter, and orchestrates
    nothing.

PART E — closure honesty

18. The PR states TASK-006 CANNOT be closed: criteria 10 and 13 need a run loop
    that §2.5, §2.7 and §3 place outside the task. Verify that reasoning against
    the specification. Is it correct, or is it an excuse for incomplete work?
19. If it is correct, then TASK-006 §4 asks for two things TASK-006 §2.5/§2.7/§3
    forbid. Confirm that inconsistency is real and that §5a records it
    accurately rather than resolving it unilaterally.
20. Confirm no document claims TASK-006 is complete, and that the status wording
    is accurate and not self-serving.
21. Verify the count: 20 of 22 criteria demonstrated. Check each.

PART F — scope and regressions

22. Confirm NOTHING was implemented from the hard exclusions: run loop,
    task-state generation, baseline probability production, candidate or
    provider discovery, capability execution, consumed-ID or step-count
    mutation, any integration, any dependency.
23. Confirm TASK-001's implementation is unchanged and TASK-006's economic rule,
    eligibility conditions and ranking are unchanged.
24. Verify the claimed counts: 423 existing tests unchanged, 467 total, on
    Python 3.12.
25. The PR reports the pre-implementation red state as import errors and
    explicitly notes that this proves absence rather than assertion strength.
    Assess whether that disclosure is complete, and whether the six mutation
    results adequately establish what the import errors do not.

FORMAT OF YOUR FINDINGS

Number every finding, per §3.1:

    CODEX-PR026-01
    CODEX-PR026-02
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
