# Codex review — PR-030

**Pull request:** [#30](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/30) — TASK-007 PR A: run state and immutable snapshots
**Reviewer:** Codex (independent review agent, `AI_BUILD_GOVERNANCE.md` §1.3)
**Reviewed against:** `tasks/TASK-007_CAPABILITY_RUN_LOOP.md`, `tasks/TASK-006_GENERALIZED_CAPABILITY_SELECTION.md`, `docs/ARCHITECTURE.md`, `docs/AI_BUILD_GOVERNANCE.md`
**Date issued:** 2026-09-11
**Outcome:** _pending — review not yet run_

---

## 0. Note on ordering

**This prompt is committed before the review runs**, as §7.3 requires, in the
same commit as the work.

## 1. Prompt issued

Recorded **before** the review was run.

```text
You are the independent review agent for the Radhanite repository, per
docs/AI_BUILD_GOVERNANCE.md §1.3.

Review pull request #30:
https://github.com/therealgulkorinaga/radhanite-ethonline/pull/30

This is TASK-007 PR A: the §3 run-state model only. No execution, no loop, no
transitions, no terminal classification, no acquisition call, no task-state
reasoning.

Review against these authoritative documents ONLY:
  - tasks/TASK-007_CAPABILITY_RUN_LOOP.md
  - tasks/TASK-006_GENERALIZED_CAPABILITY_SELECTION.md
  - docs/ARCHITECTURE.md
  - docs/AI_BUILD_GOVERNANCE.md

Do NOT treat docs/pr_explanations/PR-030_TASK-007_EXPLANATION.md as evidence of
correctness (§4.3).

PART A — the state model against §3

1. §3's table lists eleven fields. Confirm RunState has exactly those, no more
   and no fewer, and that none is provider-specific.
2. Confirm RunSnapshot carries every §3 field EXCEPT history — §3.3.
3. Confirm max_capability_steps is read from the policy rather than duplicated
   as its own field, and judge whether that is right.
4. Assess whether anything modelled here belongs to a later PR: an execution
   result, a committed cost, a retry counter, a terminal decision.

PART B — non-recursion

5. §3.3 requires that nothing contains itself transitively. Verify a snapshot
   cannot reach a history, a RunState, or another snapshot.
6. The PR claims three structural tests prove this. Assess whether they would
   actually catch a future field that reintroduced recursion, or whether they
   are name-based and defeatable.
7. TransitionRecord exists but nothing constructs one. Is defining it now
   correct, or is it an abstraction ahead of its use (ARCHITECTURE §6 item 7)?

PART C — accounting

8. Verify total_spend is DERIVED and cannot be supplied.
9. Verify §3.2.1's bounds are enforced at initialization: 0 <= remaining_budget
   <= initial_budget, 0 <= total_spend <= initial_budget, and the identity.
10. Confirm baseline/pre-loop spend initialises correctly and is not assumed
    away, per §3.2.
11. Confirm exact Money throughout, no float anywhere.

PART D — the opaque task state, and the ambiguity claimed

12. §3.1 says TASK-007 stores and passes task_state and never reads inside it.
    Confirm nothing in this PR inspects it — no attribute access, no len, no
    iteration, no equality, no hashing, no copying.
13. The implementation stores it BY REFERENCE and argues that §3.1 entails this,
    since copying or freezing requires inspection. Judge whether that reasoning
    is sound or whether the implementation has decided something the spec left
    open.
14. TASK-007 §3.5 now records an ambiguity: the spec does not say what happens
    when a caller mutates task_state after a snapshot. Assess whether recording
    it was correct, or whether the implementation should have stopped instead.
15. Assess the "Explodes" test that proves nothing inspects task_state. Is it
    comprehensive, or are there inspection routes it does not cover?

PART E — validation

16. Confirm bool is refused for the step count, negative counts refused,
    non-integers refused.
17. Confirm consumed identifiers are sorted, de-duplicated, detached from
    caller-owned input, and refuse a bare string and non-string members.
18. §3 does not state the normalization rule for consumed identifiers. The
    implementation matched eligibility's. Judge whether that is consistency or
    an invented rule.
19. Confirm RunStatus holds §6's terminal values WITHOUT classifying: a run at
    its ceiling, or with a zero-step policy, must still report RUNNING.

PART F — scope and regressions

20. Confirm nothing executes, selects, acquires, classifies, advances a counter,
    consumes a candidate, or updates task state. Check for transition methods on
    RunState.
21. Confirm TASK-006 and TASK-008 behaviour is unchanged and that every existing
    module is byte-identical to main apart from __init__.py's exports.
22. Confirm no dependency was added.
23. Verify the claimed counts: 527 existing tests unchanged, 573 total, on
    Python 3.12, and that the seven mutation results are reproducible.

FORMAT OF YOUR FINDINGS

Number every finding, per §3.1:

    CODEX-PR030-01
    CODEX-PR030-02
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
