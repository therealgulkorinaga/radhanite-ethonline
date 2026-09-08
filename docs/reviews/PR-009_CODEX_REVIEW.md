# Codex review — PR-009

**Pull request:** [#9](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/9) — the escalation rule (TASK-001)
**Reviewer:** Codex (independent review agent, `AI_BUILD_GOVERNANCE.md` §1.3)
**Reviewed against:** `tasks/TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md`, `docs/PREREQ-001_PRODUCT_DEFINITION.md`, `docs/ARCHITECTURE.md`
**Date issued:** 2026-09-08
**Outcome:** _pending — review not yet run_

---

## 1. Prompt issued

Recorded verbatim, before the review was run.

```text
You are the independent review agent for the Radhanite repository, per
docs/AI_BUILD_GOVERNANCE.md §1.3.

Review pull request #9:
https://github.com/therealgulkorinaga/radhanite-ethonline/pull/9

This is the most important pull request in the project. It implements the
escalation rule from TASK-001 §2.5 — the decision the entire product exists to
make. An error here invalidates everything built on top of it.

Review against these authoritative documents ONLY:
  - tasks/TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md
  - docs/PREREQ-001_PRODUCT_DEFINITION.md
  - docs/ARCHITECTURE.md

Do NOT treat docs/pr_explanations/PR-009_TASK-001_EXPLANATION.md as evidence of
correctness (§4.3).

Context from previous reviews, which this PR must not regress:
  - PR #3 was rejected for depending on pytest and hatchling. TASK-001 §1
    requires no external dependencies, with no exemption for tooling.
  - CODEX-PR006-03 established that wrapping Decimal is not sufficient for
    exactness: the ambient context rounds, and a shared mutable Context can have
    its guarantee stripped. This PR moves that machinery into
    radhanite/_exactness.py and adds a second user of it.
  - CODEX-PR006-08: display must not round or raise under a changed ambient
    context. This PR changes how amounts are displayed.
  - CODEX-PR006-04: do not invent product rules the specification does not
    state.

PART A — is the rule correct?

1. Compare radhanite/escalation.py line by line against TASK-001 §2.5. Is
   incremental_expected_value computed exactly as specified? Are both
   conditions exactly as specified, including >= on budget and a strict > on
   value?

2. §2.5 lists properties that must survive implementation. Verify each by
   experiment, not by reading:
   - Marginal, not cumulative: can spend-to-date influence the decision by any
     path?
   - Ties do not escalate.
   - No expected improvement means Stop, with no special case.
   - The budget ceiling is enforced structurally.
   - Budget and task_value never substitute for each other.
   - All quantities are recorded, and a Stop records which condition failed.

3. Try to construct inputs where the implementation and the specification
   disagree. Boundary values, exact ties, zero, one, extreme magnitudes, and
   very high precision are all fair game. This is the question that matters
   most.

PART B — exactness, again

4. radhanite/_exactness.py is new and shared by money and probability. Can the
   guarantee be defeated? Try a lowered ambient precision and ambient traps
   against: probability subtraction, the expected-value multiplication, and the
   comparisons in both conditions.

5. Money display was changed to drop trailing zeros via Decimal.normalize().
   Does this round, lose real precision, or raise under a changed ambient
   context? Check large values, tiny values, zero, and negatives.

PART C — invented rules and scope

6. decide() raises on a negative remaining_budget and a negative
   escalation_cost. Is that justified by the authoritative documents, or is it
   CODEX-PR006-04 recurring — a product rule invented by the implementing
   agent? The PR argues a negative balance means criterion 12's ceiling was
   already breached and is a fault rather than an economic situation. Assess
   that argument.

7. Does anything TASK-001 §3 exclude appear? Any learned, inferred or estimated
   probability? Any dependency? Any abstraction justified only by a future task
   (ARCHITECTURE §6 item 7) — assess the Probability type and FailedCondition
   specifically.

PART D — tests and claims

8. Are the tests real? Mutate the implementation and confirm the relevant tests
   fail. Specifically try: changing > to >= in the value condition, changing >=
   to > in the budget condition, swapping remaining_budget and task_value, and
   short-circuiting so only the first failed condition is recorded.

9. Is any claim in a commit message, docstring, comment or the explanation
   unsupported by the code? Check every count and every stated figure.

FORMAT OF YOUR FINDINGS

Number every finding, per §3.1:

    CODEX-PR009-01
    CODEX-PR009-02
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
