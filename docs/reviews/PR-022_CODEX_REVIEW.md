# Codex review — PR-022

**Pull request:** [#22](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/22) — TASK-006: per-candidate eligibility
**Reviewer:** Codex (independent review agent, `AI_BUILD_GOVERNANCE.md` §1.3)
**Reviewed against:** `tasks/TASK-006_GENERALIZED_CAPABILITY_SELECTION.md`, `docs/PREREQ-001_PRODUCT_DEFINITION.md`, `docs/ARCHITECTURE.md`, `docs/AI_BUILD_GOVERNANCE.md`
**Date issued:** 2026-09-09
**Outcome:** _pending — review not yet run_

---

## 0. Note on ordering

**This prompt is committed before the review runs**, as `AI_BUILD_GOVERNANCE.md`
§7.3 requires, and in the same commit as the work it reviews.

The three preceding reviews did not manage that. PR-017's prompt was recorded
afterwards; PR-020 was merged unreviewed; PR-021's prompt was also recorded
afterwards. Each carries its own disclosure, and PR-021's record notes the three
together as a pattern rather than three separate lapses.

This is the correction to that pattern. It is recorded here so the change of
practice is visible in the same place the lapses were.

## 1. Prompt issued

Recorded **before** the review was run.

```text
You are the independent review agent for the Radhanite repository, per
docs/AI_BUILD_GOVERNANCE.md §1.3.

Review pull request #22:
https://github.com/therealgulkorinaga/radhanite-ethonline/pull/22

This is the SECOND implementation step of TASK-006, authorized in PR #20. It
delivers per-candidate eligibility only: given the current task state and ONE
candidate, eligible or ineligible, with reasons and the economic figures. It
must select nothing.

Review against these authoritative documents ONLY:
  - tasks/TASK-006_GENERALIZED_CAPABILITY_SELECTION.md
  - docs/PREREQ-001_PRODUCT_DEFINITION.md
  - docs/ARCHITECTURE.md
  - docs/AI_BUILD_GOVERNANCE.md

Do NOT treat docs/pr_explanations/PR-022_TASK-006_EXPLANATION.md as evidence of
correctness (§4.3).

PART A — the rule, implemented exactly

1. TASK-006 §2.3 states six eligibility conditions. Confirm all six are
   implemented, none is dropped as redundant, and none is added.
2. Verify the arithmetic is exactly:
       incremental_expected_value =
           (candidate_success_probability - current_success_probability)
           × task_value
       net_expected_value = incremental_expected_value - candidate_cost
   Check specifically that task_value and remaining_budget are not
   interchangeable: remaining_budget must appear ONLY in the affordability
   condition, task_value ONLY in the value one.
3. The value condition is a strict `>`. Confirm a candidate worth exactly its
   cost is INELIGIBLE. A `>=` here is a defect, not a rounding preference.
4. The affordability condition is `cost <= remaining_budget`. Confirm a
   candidate costing exactly the remaining budget IS affordable.
5. The step condition is `capability_step_count < max_capability_steps`.
   Confirm equality means ineligible.
6. Confirm every failed condition is reported, not only the first.

PART B — scope

7. This step must select nothing. Confirm no ranking, tie-breaking, ordering,
   comparison between candidates, or run-loop behaviour appears.
8. Confirm nothing from TASK-006 §3 appears: candidate generation, task-state
   evaluation, execution, provider discovery, payment.
9. Confirm no dependency, credential, or configuration was added.
10. §2.1: confirm no provider, network, or payment concept can influence the
    result. Assess whether the source-scanning test for forbidden words is
    meaningful or defeatable.

PART C — the two non-economic conditions

11. §2.5 B and C are termination safeguards, not economic judgements, and §8
    requires a run record to keep that distinction. Assess whether the
    implementation actually carries it in a way a later caller cannot lose —
    or whether it is only prose.
12. `max_capability_steps` has no default. Confirm omitting it is an error and
    that no literal ceiling value appears anywhere.
13. Consumed candidates are matched by identifier alone. Confirm no notion of
    capability type, class, or family has appeared — §2.5a, criterion 20.

PART D — condition 1, and whether it should be here at all

14. `candidate_cost > 0` is enforced at construction by `Candidate` (PR #21) and
    is therefore unreachable through ordinary use. This PR checks it again, and
    tests it by bypassing the constructor with object.__setattr__.
    Give a clear judgement: is that defence in depth appropriate to a
    termination safeguard, or is it dead code and a contrived test?
15. If you judge it dead code, say what should replace it — the specification
    does state six conditions.

PART E — condition 3, and whether it earns its place

16. §2.3 keeps the uplift condition although it is redundant while cost is
    positive and task_value is non-negative. The implementation justifies it by
    a negative-task_value case, which is tested. Assess whether that
    justification is sound, and whether `assess` should instead reject a
    negative task_value outright — noting that TASK-001's `decide()` does not
    check it either, and that `Task` already forbids it.

PART F — inputs and faults

17. A negative remaining_budget raises rather than answering. Confirm that
    matches TASK-001's `decide()` and is the right call here.
18. consumed_candidate_ids refuses a bare string, because `in` on a string is a
    substring test. Verify the guard is complete — consider bytes, and any
    other type where membership would silently misbehave.
19. Confirm step counts must be whole numbers and that bool is refused.
20. Confirm the arguments are keyword-only.

PART G — tests

21. The PR claims 56 new tests and that eight deliberate faults were each
    caught. Verify the tests detect what they claim rather than passing
    vacuously. Look specifically for assertions that would hold whatever the
    code does.
22. Verify exact-decimal semantics throughout: no float anywhere, all
    arithmetic through Money and Probability.
23. Verify the claimed counts independently: 278 existing tests unchanged, 334
    total, on Python 3.12.
24. Confirm the economic figures are computed for INELIGIBLE candidates too, as
    §8 requires, and are correct in that case.

FORMAT OF YOUR FINDINGS

Number every finding, per §3.1:

    CODEX-PR022-01
    CODEX-PR022-02
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
