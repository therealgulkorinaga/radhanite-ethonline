# Codex review — PR-027

**Pull request:** [#27](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/27) — TASK-007, the capability run loop
**Reviewer:** Codex (independent review agent, `AI_BUILD_GOVERNANCE.md` §1.3)
**Reviewed against:** `tasks/TASK-006_GENERALIZED_CAPABILITY_SELECTION.md`, `docs/PREREQ-001_PRODUCT_DEFINITION.md`, `docs/ARCHITECTURE.md`, `docs/AI_BUILD_GOVERNANCE.md`
**Date issued:** 2026-09-11
**Outcome:** **Rejected** — `CODEX-PR027-01` … `-05`; all five corrected

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

**The reviewer's verbatim response was not supplied** to the agent writing this
record. What follows is the five findings **as relayed by the human product
owner** in the correction authorization. Nothing has been invented. §0 is
unaffected: the prompt in §1 was committed before the review ran.

| | Finding | Departs from |
|---|---|---|
| `-01` | The run context carries `current_success_probability` but **not the opaque task/evidence state** that candidate generation, state update and audit reconstruction all require | TASK-007 §3, §5 |
| `-02` | The history is **recursively defined**: an entry contains the complete post-transition run state, which itself contains the history | TASK-007 §3.1; `PREREQ-001` §8 |
| `-03` | Accounting is **inconsistent**. `total_spend + remaining_budget == initial_budget` is asserted while `total_spend` is defined as capability-loop spend only — but TASK-006 §2.2a defines `remaining_budget` as already net of baseline spend | TASK-006 §2.2a |
| `-04` | Acceptance criterion 2 claims **every** "no eligible candidate" outcome is an economic STOP. False — a ceiling stop refuses nothing on economic grounds. Precedence for an already-complete task is also unspecified | TASK-006 §8; TASK-007 §6 |
| `-05` | Criterion 14 **overclaims**: it requires candidates differing only in provider metadata to produce identical complete runs. TASK-006 guarantees identical assessments and selection, not identical execution, evidence or runs | TASK-006 §2.1 |

## 3. Outcome

**Rejected** — `CODEX-PR027-01` through `-05`.

`-02` alone would justify it: a recursively defined structure cannot be
constructed, so the audit model as specified was unbuildable. `-03` and `-04`
are both cases of the specification asserting something that contradicts
TASK-006, and `-05` claimed a guarantee the kernel does not provide.

## 4. Corrections

All five corrected; §§2–9 of the task were rewritten rather than patched, since
the findings interlock across the state model, the history, the accounting, the
terminal states and the criteria.

| Finding | Correction |
|---|---|
| `-01` | `task_state` added — opaque, stored and passed, **never read** by this task or the decision. Its production and interpretation are explicitly a separate future task |
| `-02` | History is now a sequence of immutable transition records holding **snapshots that exclude the history**. Nothing contains itself; the whole `Selection` is still preserved |
| `-03` | `total_spend` means all spend from the initial budget, baseline included. Initialization must satisfy `total_spend = initial_budget - remaining_budget`. No redundant pre-loop field |
| `-04` | Classification derived from refusal reasons, mixed case defined, and **already-complete given explicit precedence** over zero-step policy, reached ceiling and available candidates |
| `-05` | Criterion 20 now asserts identical **assessments and selection** only; §9a states what is not guaranteed |

The product owner also supplied **execution semantics** — §7 — replacing the
four-option question the earlier draft left open. A withdrawn claim is recorded
there: consuming a candidate ID does **not** guarantee termination, since a
source may regenerate an equivalent capability under a fresh ID. Termination on
failure now rests on an explicit terminal state.

Acceptance criteria reconciled to **22**, not appended to.

**Corrections are themselves subject to review** (`AI_BUILD_GOVERNANCE.md`
§7.5). This corrective commit has not been reviewed.
