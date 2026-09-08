# Codex review — PR-006

**Pull request:** [#6](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/6) — exact money and the five task inputs (TASK-001)
**Reviewer:** Codex (independent review agent, `AI_BUILD_GOVERNANCE.md` §1.3)
**Reviewed against:** `tasks/TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md`, `docs/PREREQ-001_PRODUCT_DEFINITION.md`, `docs/ARCHITECTURE.md`
**Date issued:** 2026-09-07
**Outcome:** **Rejected** — `CODEX-PR006-01` violated ARCHITECTURE.md §6 item 7; `-02` through `-05` departed from TASK-001 and PREREQ-001 input and economic-boundary requirements. All seven findings corrected.
**Commit reviewed:** `d3c13d7`

---

## 1. Prompt issued

Recorded verbatim, before the review was run.

```text
You are the independent review agent for the Radhanite repository, per
docs/AI_BUILD_GOVERNANCE.md §1.3.

Review pull request #6:
https://github.com/therealgulkorinaga/radhanite-ethonline/pull/6

Review the implementation against these authoritative documents ONLY:
  - tasks/TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md
  - docs/PREREQ-001_PRODUCT_DEFINITION.md
  - docs/ARCHITECTURE.md

Do NOT treat docs/pr_explanations/PR-006_TASK-001_EXPLANATION.md as evidence
that the implementation is correct. Per §4.3 the explanation is not
authoritative. A confident, well-written explanation of behaviour the code does
not exhibit is a defect to catch, not a reason to approve.

Context: PR #3 was rejected for depending on pytest and hatchling, because
TASK-001 §1 requires no external dependencies with no exemption for tooling.
Check that this PR has not reintroduced any dependency.

Answer these specifically:

1. Does the PR do what it claims, and ONLY that?

2. Does it contain anything TASK-001 §3 excludes? That list is: OpenRouter,
   real model APIs, Privy, Arc/USDC, Hedera, x402, production UI, machine
   learning, contextual bandits, reinforcement learning, any database, and
   learned or inferred probabilities. Check imports, configuration and declared
   dependencies, not only source files.

3. Does it violate any boundary in ARCHITECTURE.md §6? Item 7 matters most here:
   is any abstraction present whose only justification is a future unauthorized
   task? Assess Task.headroom_ratio specifically — is it speculative scope, or
   acceptable as an inspection-only convenience?

4. PREREQ-001 §4.3 requires budget and task_value to remain separate, with
   neither derived from the other. Is that actually enforced by the code, or
   only claimed? Could any code path collapse them?

5. Money claims to be exact and to refuse floats. Test this. Try constructing
   from a float, from a bool, and from a numpy-style or other numeric type if
   available. Try arithmetic that would drift in floating point. Report anything
   that gets through.

6. Money permits negative amounts, justified by TASK-001 §2.5's requirement that
   the no-improvement case fall out of the arithmetic. Is that justification
   sound, or does permitting negatives create a risk elsewhere — for instance,
   could a negative budget or a negative remaining balance now pass unnoticed?

7. Are the tests real, or do any pass regardless of the state of the code?
   Verify by breaking the implementation and confirming the relevant test fails.

8. Is there any claim in a commit message, docstring, or code comment that the
   code does not support? Check the package docstring in radhanite/__init__.py
   especially: PR #3 was faulted for describing unimplemented behaviour in the
   present tense, and the claim of what is and is not implemented must be true.

9. Does every commit map to an authorized task, prerequisite, governance
   amendment, or documented review correction, per §3?

FORMAT OF YOUR FINDINGS

Number every finding, in this exact form, per §3.1:

    CODEX-PR006-01
    CODEX-PR006-02
    ...

For each: the identifier, the file and line, what is wrong, and which
specification or boundary it departs from. Number them in the order you list
them and do not reuse a number.

If you find nothing, say so explicitly and raise no findings.

CONCLUDE

End with exactly ONE outcome, per §7.2:
  - Approved
  - Approved with corrections  (list the finding identifiers to be fixed)
  - Rejected  (state which specification or boundary was departed from)
```

## 1b. Second review prompt

Issued after the seven corrections were pushed, and committed before that second
review was run.

```text
You are the independent review agent for the Radhanite repository, per
docs/AI_BUILD_GOVERNANCE.md §1.3.

This is a SECOND review of pull request #6:
https://github.com/therealgulkorinaga/radhanite-ethonline/pull/6

You reviewed it previously at commit d3c13d7 and rejected it with seven
findings, CODEX-PR006-01 through CODEX-PR006-07. Seven correction commits have
since been pushed. Your record of the first review, including your findings
verbatim, is in docs/reviews/PR-006_CODEX_REVIEW.md.

Review against these authoritative documents ONLY:
  - tasks/TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md
  - docs/PREREQ-001_PRODUCT_DEFINITION.md
  - docs/ARCHITECTURE.md

Do NOT treat the PR explanation as evidence of correctness (§4.3).

PART A — do the fixes hold?

For each of CODEX-PR006-01 through -07, verify the fix actually resolves the
finding. Reproduce where you can rather than reading the diff:

  -01  Is headroom_ratio gone, with nothing equivalent reintroduced?
  -02  Are Infinity, -Infinity and NaN refused, as Money and inside a Task?
  -03  Is arithmetic now exact? Retry your own example. Try changing the
       ambient decimal context and confirm results are unaffected. Confirm an
       operation that genuinely cannot be represented raises rather than
       rounding.
  -04  Are zero budget and zero task value now accepted, and negatives still
       refused?
  -05  Is constraints required? Confirm omitting it raises, and confirm the
       replacement test fails if the default is restored.
  -06  Does the justification now preserve the equality case?
  -07  Is the corrected comment accurate?

PART B — did any correction introduce a NEW defect?

This is the part that matters most. On PR #3 a correction introduced a fresh
defect that only the second review caught. Look specifically at:

  - The new decimal context (prec=200, Inexact/InvalidOperation/DivisionByZero/
    Overflow trapped). Does trapping change behaviour anywhere unintended? Can
    a legitimate amount of money now raise? Is comparison, equality, hashing,
    or string formatting affected? Does the context leak or fail to apply?
  - Accepting zero. Does any code path now divide by, or otherwise mishandle,
    a zero budget or zero task value?
  - Money.is_negative alongside is_positive. Is zero handled consistently by
    both, and is either used anywhere it should not be?
  - Making constraints required. Did that break any construction site?

PART C — claims

Re-check every count and claim in
docs/pr_explanations/PR-006_TASK-001_EXPLANATION.md against reality: file
counts, test counts, and behavioural claims. Stale counts after a correction
were finding CODEX-PR003-04 on the previous pull request; check the same class
of error has not recurred.

Also confirm the review record in docs/reviews/PR-006_CODEX_REVIEW.md reproduces
your first-round findings verbatim, without softening or omission.

FORMAT

Number any NEW findings continuing the existing sequence, per §3.1 — identifiers
are never reused, so start at:

    CODEX-PR006-08

For each: identifier, file and line, what is wrong, and which specification or
boundary it departs from.

If a previous finding is not properly fixed, say so against its ORIGINAL
identifier rather than issuing a new one.

If you find nothing new and all seven fixes hold, say so explicitly.

CONCLUDE

End with exactly ONE outcome, per §7.2:
  - Approved
  - Approved with corrections  (list the finding identifiers)
  - Rejected  (state which specification or boundary was departed from)
```

## 2. Findings returned

Recorded verbatim, as returned. Not summarized, softened, or filtered.

> Reviewed PR #6 at `d3c13d7`. The baseline suite passes: 40 tests on Python 3.12.13.
>
> 1. The PR is limited to money, task inputs, tests, and required review documentation, but it does not fully support all its claims.
> 2. No prohibited integration, database, learning component, or third-party dependency appears. Imports are standard-library-only.
> 3. `headroom_ratio` should be removed. It is unused, unauthorized by the economic rule, and exists only as a speculative convenience.
> 4. `budget` and `task_value` are genuinely separate immutable fields. No implementation path derives or substitutes one for the other.
> 5. Direct float, bool, `numpy.float64`, `numpy.int64`, and `Fraction` inputs were rejected. Ordinary decimal drift examples pass, but non-finite and high-precision cases expose defects below. `Money(Decimal(0.1))` is accepted because the float has already been converted before reaching `Money`.
> 6. Signed `Money` is defensible: worsening probabilities require a negative intermediate expected value. Negative initial budgets and task values are rejected. No remaining-balance type exists yet, so future run-state code must enforce non-negative balances at that boundary.
> 7. Most tests are real: mutations to float/bool rejection, addition, budget validation, and budget/value separation caused relevant failures. One test does not test what its name claims.
> 8. The package docstring correctly distinguishes implemented from intended behavior, subject to the false “exact” claim below. Other inaccurate comments remain.
> 9. All four commits explicitly map to TASK-001.
>
> `CODEX-PR006-01`
>
> File and line: `radhanite/task.py:25-34,75-83`; `tests/test_task.py:49-62`
>
> `headroom_ratio` is a public, tested derived metric with no consumer and no role in TASK-001. The authorized escalation rule deliberately uses budget and task value separately and marginally; it never uses their total-value ratio. “Inspection-only convenience” is not a specified need, and PREREQ-001 §8 requires inspection of actual economic decisions, not unrelated derived metrics. This violates ARCHITECTURE.md §6 item 7.
>
> `CODEX-PR006-02`
>
> File and line: `radhanite/money.py:52-64`; `radhanite/task.py:46-60`
>
> `Money` accepts non-finite decimal values. `Money("Infinity")`, `Money("-Infinity")`, and `Money("NaN")` all construct successfully. More seriously, a `Task` accepts positive infinity as either its budget or task value. An infinite budget is not the finite hard ceiling required by PREREQ-001 §§2.1 and 4.2. NaN then fails unpredictably during comparison or display rather than being rejected at construction.
>
> `CODEX-PR006-03`
>
> File and line: `radhanite/money.py:3-10,68-87`; `radhanite/__init__.py:8`
>
> The claim that `Money` arithmetic is always exact is false for accepted values. Operations use the active `decimal` context and can silently round. Under the default 28-digit context:
>
> ```text
> 1.234567890123456789012345678
> + 0.0000000000000000000000000009
> = 1.234567890123456789012345679
> ```
>
> The exact result ends in `6789`. Reducing the active context precision also rounds ordinary additions and multiplications. This can eventually move an expected-value calculation across TASK-001 §2.5's strict comparison boundary. Arithmetic must either preserve accepted inputs exactly or refuse inexact operations loudly.
>
> `CODEX-PR006-04`
>
> File and line: `radhanite/task.py:48-60`; `tests/test_task.py:70-86`
>
> The code rejects zero budgets and zero task values before the economic loop runs. Neither authoritative document requires those inputs to be positive. A zero budget should naturally fail the budget condition, and a zero task value should naturally fail the value condition; TASK-001 §2.5 assigns those decisions to the escalation-or-stop rule. Rejecting them as invalid silently introduces a new product rule and prevents the specified Stop outcome from being reached. Negative initial values may reasonably be rejected, but zero must not be conflated with negative without human authorization.
>
> `CODEX-PR006-05`
>
> File and line: `radhanite/task.py:36-40`; `tests/test_task.py:17-27,39-40`; `docs/pr_explanations/PR-006_TASK-001_EXPLANATION.md:76-78`
>
> The PR claims that a task missing any of its five inputs is refused, but `constraints` has a default and can be omitted. The test named `test_constraints_are_optional` does not test omission: its helper always supplies `constraints`, and the test explicitly supplies `constraints=()`. Removing the field's default did not make this test fail. This leaves TASK-001 §2.1 and PREREQ-001 §4's five-input contract unenforced while claiming otherwise.
>
> `CODEX-PR006-06`
>
> File and line: `radhanite/money.py:44-47`; `tests/test_money.py:68-72`; `docs/pr_explanations/PR-006_TASK-001_EXPLANATION.md:63-68`
>
> The negative-money justification says no improvement always produces a negative expected value. Equal current and post-escalation probabilities produce zero. TASK-001 §2.5 explicitly says “zero or negative.” Signed intermediate amounts remain justified for a worsening probability, but the claim must preserve the equality case.
>
> `CODEX-PR006-07`
>
> File and line: `tests/test_task.py:54-56`
>
> The comment claims that when task value is below budget, “the escalation rule will simply refuse to spend.” That is false. The rule compares incremental expected value with incremental cost; total task value being below total budget does not prevent an inexpensive, high-improvement escalation. This contradicts TASK-001 §2.5's marginal rule and its requirement that budget and value serve separate conditions.
>
> Rejected — `CODEX-PR006-01` violates ARCHITECTURE.md §6 item 7, and `CODEX-PR006-02` through `CODEX-PR006-05` depart from TASK-001 and PREREQ-001 input and economic-boundary requirements.

## 3. Outcome

**Rejected.** All seven findings were accepted without dispute and corrected.
None was disputed.

Three are worth singling out, because they were defects the implementing agent
could not have found by re-reading its own work:

- **`-03`** established that wrapping `Decimal` does not make arithmetic exact.
  The ambient decimal context defaults to 28 significant digits and any code in
  the process can change it. The reviewer produced a concrete sum that rounded.
- **`-02`** found that `Decimal("Infinity")` is a valid `Decimal`, so an
  infinite budget was accepted — which is not the finite hard ceiling
  PREREQ-001 §4.2 requires.
- **`-04`** caught the implementing agent inventing a product rule. Rejecting a
  zero budget seemed obviously correct and is authorized nowhere; worse, it made
  the specified Stop outcome unreachable for exactly the tasks that should
  produce it.

`-06` and `-07` were false claims in comments — the class of defect the PR-003
review had already flagged once.

## 4. Corrections

| Finding | Correction commit | What changed |
|---|---|---|
| `CODEX-PR006-01` | `1c49e2d` | `headroom_ratio` removed with its tests. The tests it occupied now assert what those cases were actually about. |
| `CODEX-PR006-02` | `9ad738e` | Non-finite amounts refused at construction. |
| `CODEX-PR006-03` | `9ad738e` | Arithmetic moved into `Money`'s own decimal context with a far larger precision and `Inexact` trapped, so an operation that would round raises instead. Amounts are exact or the program stops. |
| `CODEX-PR006-04` | `d9a68e6` | Zero budget and zero task value accepted; only negatives refused. `Money.is_negative` added so the check says what it means. |
| `CODEX-PR006-05` | `ae0610a` | `constraints` default removed, so all five inputs are required. Test replaced with one that constructs a `Task` without it and requires a `TypeError`; verified by mutation. |
| `CODEX-PR006-06` | `0dc2d42` | Justification now preserves the equality case ("zero or negative"), with a test for zero. |
| `CODEX-PR006-07` | `03dbc61` | Comment corrected: the rule is marginal, so totals do not constrain each other. |

```
git log --grep=CODEX-PR006
```

### Verification after correction

```
$ python -m unittest discover
....................................................
Ran 52 tests in 0.005s
OK
```

The reviewer's rounding example is now exact:

```
1.234567890123456789012345678 + 0.0000000000000000000000000009
= 1.2345678901234567890123456789
```

Non-finite values refused; ambient precision changes cannot alter a result; and
restoring the `constraints` default makes the replacement test fail.

### Carried forward

The review noted that no remaining-balance type exists yet, and that future
run-state code must enforce a non-negative balance at that boundary, since
`Money` deliberately permits negatives and will not catch it. Recorded in the
PR-006 explanation's known limitations and to be honoured when the loop is built.
