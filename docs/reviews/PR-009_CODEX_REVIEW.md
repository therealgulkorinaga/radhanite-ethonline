# Codex review — PR-009

**Pull request:** [#9](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/9) — the escalation rule (TASK-001)
**Reviewer:** Codex (independent review agent, `AI_BUILD_GOVERNANCE.md` §1.3)
**Reviewed against:** `tasks/TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md`, `docs/PREREQ-001_PRODUCT_DEFINITION.md`, `docs/ARCHITECTURE.md`
**Date issued:** 2026-09-08
**Outcome:** **Approved with corrections** — `CODEX-PR009-01`, `-02`, `-03`, all since corrected. The rule itself was found correct.
**Commit reviewed:** `be267c7`

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

Recorded verbatim, as returned. Not summarized, softened, or filtered.

> Reviewed PR #9 at `be267c7`.
>
> The escalation implementation is correct. Across 26,136 generated input combinations, its result matched TASK-001 §2.5 exactly. The worked example, equality boundaries, zero-improvement case, budget ceiling, independent budget/value roles, recorded quantities, and dual failure reporting all held.
>
> Exactness also held:
>
> - Ambient decimal precision and traps neither changed results nor leaked state.
> - Values within the 200-digit context remained exact.
> - Operations exceeding it raised `Inexact` rather than returning rounded data.
> - Money formatting preserved large, tiny, zero, negative, and sub-cent values.
> - Accepted extreme-precision values can fail loudly beyond 200 digits, but cannot produce an incorrectly rounded decision. This matches the documented exact-or-stop policy.
>
> Rejecting negative escalation costs and negative remaining balances is justified as domain-integrity validation. A negative remaining balance means the hard ceiling has already been breached; treating that corrupted state as an ordinary Stop would conceal the breach.
>
> No external dependency, excluded integration, learned probability, database, speculative future abstraction, or USDC misrepresentation appears. `Probability`, `FailedCondition`, and the shared exactness helper are all used directly by the current authorized rule. All five commits map explicitly to TASK-001.
>
> The complete suite passes: 102 tests on Python 3.12.13. All requested mutations were detected:
>
> - Value `>` changed to `>=`: tie test failed.
> - Budget `>=` changed to `>`: two boundary tests failed.
> - Budget and task value swapped: both separation tests failed.
> - Dual-condition reporting short-circuited: the both-fail test failed.
>
> Three documentation/test-evidence corrections remain.
>
> CODEX-PR009-01
>
> File and line: `docs/pr_explanations/PR-009_TASK-001_EXPLANATION.md:18`
>
> The changed-file/test inventory is inaccurate. The PR changes 11 files, but the table omits `docs/reviews/README.md`. It also says `tests/test_escalation.py` contains 27 checks, whereas test discovery finds 30: 29 test methods and one doctest. The overall 57-to-102 and 45-new-test counts are correct.
>
> This departs from the review prompt’s requirement to verify every file and test count accurately.
>
> CODEX-PR009-02
>
> File and line: `tests/test_escalation.py:192`; `docs/pr_explanations/PR-009_TASK-001_EXPLANATION.md:119`
>
> `test_the_decision_can_be_recomputed_from_what_it_recorded` does not recompute the decision. It only recomputes `incremental_expected_value`; it never independently applies the budget and value conditions or compares the resulting verdict and failed conditions. The explanation consequently overstates what the test proves.
>
> The record contains sufficient information to recompute the decision, so this is a test-evidence and claim defect rather than an implementation defect. It departs from TASK-001 §2.5’s recomputability requirement and §7’s prohibition on claiming behavior tests do not demonstrate.
>
> CODEX-PR009-03
>
> File and line: `docs/pr_explanations/PR-009_TASK-001_EXPLANATION.md:175`; `tests/test_escalation.py:96`
>
> The explanation claims that “one cent either side of the tie decides opposite ways.” The tests cover the exact tie and one cent on the escalating side (`$5.99` cost against `$6.00` value), but no `$6.01` case covers the stopping side. Either add that boundary test or narrow the claim.
>
> This departs from TASK-001 §7’s requirement that documentation claims be demonstrated by tests.
>
> Approved with corrections (CODEX-PR009-01, CODEX-PR009-02, CODEX-PR009-03)

## 3. Outcome

**Approved with corrections.** All three findings were accepted without dispute
and corrected.

This is the first review in the project to find **no defect in the
implementation**. The rule was checked against TASK-001 §2.5 across 26,136
generated input combinations and matched in every one, and all four requested
mutations were detected by the existing tests.

Two questions the prompt raised explicitly were answered against the implementing
agent's own doubt:

- Raising on a negative remaining balance was found **justified** as
  domain-integrity validation, not a recurrence of `CODEX-PR006-04`. A negative
  balance means the ceiling has already been breached, and treating it as an
  ordinary Stop would conceal the breach.
- `Probability`, `FailedCondition` and the shared exactness helper were found to
  be used directly by the authorized rule, not speculative abstraction under
  ARCHITECTURE §6 item 7.

All three findings concerned what the documentation and tests **claimed**, not
what the code did. `-01` was the fifth instance of a hand-maintained count left
behind by a later change.

## 4. Corrections

| Finding | Correction commit | What changed |
|---|---|---|
| `CODEX-PR009-01` | `d710bb2` | File table corrected to eleven, escalation test count to 31. Every count verified against `git diff --name-only` and `unittest discover` before being written. |
| `CODEX-PR009-02` | `5479e41` | The recompute test now re-derives the whole verdict from the record alone — both conditions applied independently — across six cases. Verified by mutation: forcing the rule to always escalate fails 18 tests. |
| `CODEX-PR009-03` | `5479e41` | Added the `$6.01` case, the stopping side of the tie boundary the claim asserted and no test covered. |

```
git log --grep=CODEX-PR009
```

### Verification after correction

```
$ python -m unittest discover
Ran 103 tests in 0.006s
OK
```
