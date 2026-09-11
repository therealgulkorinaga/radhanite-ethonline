# Codex review — PR-027

**Pull request:** [#27](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/27) — TASK-007, the capability run loop
**Reviewer:** Codex (independent review agent, `AI_BUILD_GOVERNANCE.md` §1.3)
**Reviewed against:** `tasks/TASK-006_GENERALIZED_CAPABILITY_SELECTION.md`, `docs/PREREQ-001_PRODUCT_DEFINITION.md`, `docs/ARCHITECTURE.md`, `docs/AI_BUILD_GOVERNANCE.md`
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

Review pull request #27:
https://github.com/therealgulkorinaga/radhanite-ethonline/pull/27

Specification only. It promotes BL-16 to TASK-007, the capability run loop, and
renumbers The Graph from TASK-007 to TASK-008. It contains no code and
authorizes nothing.

Review against these authoritative documents ONLY:
  - tasks/TASK-006_GENERALIZED_CAPABILITY_SELECTION.md
  - docs/PREREQ-001_PRODUCT_DEFINITION.md
  - docs/ARCHITECTURE.md
  - docs/AI_BUILD_GOVERNANCE.md

Do NOT treat docs/pr_explanations/PR-027_TASK-007_EXPLANATION.md as evidence of
correctness (§4.3).

PART A — no economics may have moved

1. TASK-007 must redefine nothing in TASK-006. Confirm no formula, eligibility
   condition, ranking rule, tie-break, threshold or safeguard is restated in a
   way that could diverge, and that TASK-006 itself is unchanged apart from §5a's
   pointer.
2. §4 item 5 says no capability executes unless TASK-006 selected it. Assess
   whether the specified loop actually makes that structurally true, or merely
   asserts it.
3. §2.1 provider neutrality: assess whether the three interfaces in §5 can leak
   provider identity into the decision. Look specifically at §5.2's execution
   result flowing through §5.3 into the next probability.

PART B — the invariants

4. Twelve invariants are listed in §4. Are any unenforceable as specified, or
   in tension with each other?
5. Invariant 7 says the step count increments exactly once per completed paid
   capability step. Is "completed" well enough defined given §7 is unresolved?
6. Invariant 1 requires total_spend + remaining_budget == initial_budget. Is
   carrying both fields justified, or is it redundancy that could drift?
7. Assess whether the loop is provably terminating under the specified
   invariants, and say which safeguard does it in each terminal case.

PART C — the unresolved failure policy

8. §7 presents four options and recommends B. Assess the reasoning, in
   particular the claim that consuming the ID on failure is what guarantees
   termination.
9. Is the recommendation compatible with invariant 11 — a failure never
   appearing as success — under all four options?
10. Does §7 leave enough undecided that implementation genuinely cannot begin,
    or has it decided by implication?

PART D — inherited criteria

11. §8 claims to inherit TASK-006 criteria 10 and 13 with their meaning
    unchanged. Compare the wording in both documents and confirm no drift.
12. Confirm nothing in this PR marks TASK-006 complete, and that TASK-006 §5a
    now says closure follows implementation rather than specification.

PART E — scope, state and the demonstration

13. §3's run state claims to be minimal. Identify any field that is not required
    by a stated behaviour, and any required field that is missing.
14. §10 lists what this task does not own. Cross-check against §2 and §5: does
    anything excluded there in fact appear in the loop?
15. §11 requires the supplier demonstration to be driven by state and decisions,
    not a hard-coded order. Assess whether the specification makes that
    achievable, and whether PREREQ-001 §6.3's "a run that buys nothing is
    correct" survives.

PART F — the renumbering and the record

16. The Graph moved from TASK-007 to TASK-008. Confirm its content is unchanged
    apart from the number, that every reference was updated, and that no dangling
    link remains anywhere in the repository.
17. Confirm the move is recorded where a reader following an old reference would
    find it.
18. Confirm no code, test, dependency or configuration changed, and that 476
    tests still pass.

FORMAT OF YOUR FINDINGS

Number every finding, per §3.1:

    CODEX-PR027-01
    CODEX-PR027-02
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
