# Codex review — PR-012

**Pull request:** [#12](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/12) — simulated execution and outcome evaluation (TASK-001)
**Reviewer:** Codex (independent review agent, `AI_BUILD_GOVERNANCE.md` §1.3)
**Reviewed against:** `tasks/TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md`, `docs/PREREQ-001_PRODUCT_DEFINITION.md`, `docs/ARCHITECTURE.md`
**Date issued:** 2026-09-08
**Outcome:** **Rejected** — `CODEX-PR012-01` left criterion 4 unimplemented and `-02` left the simulator's determinism unenforced at its public boundary. All three findings corrected.
**Commit reviewed:** `ad55b32`

---

## 1. Prompt issued

Recorded verbatim, before the review was run.

```text
You are the independent review agent for the Radhanite repository, per
docs/AI_BUILD_GOVERNANCE.md §1.3.

Review pull request #12:
https://github.com/therealgulkorinaga/radhanite-ethonline/pull/12

It implements TASK-001 §2.3 (simulated execution) and §2.4 (outcome
evaluation), addressing acceptance criteria 3 and 4.

Review against these authoritative documents ONLY:
  - tasks/TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md
  - docs/PREREQ-001_PRODUCT_DEFINITION.md
  - docs/ARCHITECTURE.md

Do NOT treat docs/pr_explanations/PR-012_TASK-001_EXPLANATION.md as evidence of
correctness (§4.3).

PART A — the rule that matters most

§2.4 says evaluation "does not interpret, soften, or infer partial success that
the condition does not define". Softening partial progress into success would
tell the escalation rule the task was finished and stop the spending on work
that never completed.

1. Confirm PARTIAL_PROGRESS evaluates to NOT MET on every path. Try to find any
   route — direct or through the loop of Outcome members — where it does not.
2. Confirm the record still distinguishes partial progress from outright
   failure, so a run record does not lose which happened.
3. Verdict has exactly two members. Is two correct under §2.4, or does the
   specification anywhere require or permit a third?

PART B — the simulator

4. §2.3 requires the simulator to be deterministic and controllable. Attack
   that. Is there any path by which the same script could produce a different
   run — iteration order, hashing, shared state between instances, module state?
5. Confirm nothing is sampled against a strategy's stated success probability.
   A simulator that rolled dice would make the loop untestable.
6. The simulator is stateful: it consumes its script. Is that consistent with
   §2.3, and can two simulators interfere with each other?
7. Running past the end of a script raises RuntimeError rather than reporting an
   outcome. Is that defensible, or an invented rule (CODEX-PR006-04)?
8. evaluate() takes the success condition, validates it is non-empty, records it
   and names it in the reason — but the verdict is derived from the outcome
   alone. §2.4 says "compare the outcome against the task's measurable success
   condition". Is that a departure? The PR argues the outcome is a controlled
   input in TASK-001 so there is nothing else to compare against, and that real
   checking arrives with real execution. Assess that argument.

PART C — carried-forward defects

Four classes of defect have recurred in this project. Check each against the
new code:

9.  Immutability claims. Attempt and Evaluation are frozen, slotted, and
    refuse __setstate__. Confirm, and confirm no claim overstates what that
    prevents — object.__setattr__ and ctypes remain open by design and
    radhanite/_immutable.py says so.
10. Invented product rules (CODEX-PR006-04). Does anything here reject an input
    the specification does not require rejecting?
11. Tests that cannot detect what they claim (CODEX-PR011-04, -05). Mutate the
    implementation and confirm failures: make PARTIAL_PROGRESS return MET, make
    the simulator ignore the escalated flag, make it return script[0] every
    time, and remove the empty-condition check.
12. Stale hand-maintained counts (six previous instances). Verify every count
    and factual claim in the explanation independently.

PART D — scope

13. Does anything TASK-001 §3 excludes appear? Any dependency, model API,
    learned behaviour, database, or UI? Is the simulator anywhere presented as
    a model of intelligence rather than a fixture?
14. Any abstraction justified only by a future task (ARCHITECTURE §6 item 7)?
    Assess Attempt.success_probability and ScriptedSimulator.remaining
    specifically — are they used, or speculative?

FORMAT OF YOUR FINDINGS

Number every finding, per §3.1:

    CODEX-PR012-01
    CODEX-PR012-02
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

> Reviewed PR #12 at ad55b32. The unmodified suite passes 169 tests on Python 3.12.13.
>
> Three findings.
>
> CODEX-PR012-01
>
> File and line: [radhanite/evaluation.py (line 59)](/Users/arkoganguli/Projects/radhanite-ethonline/radhanite/evaluation.py:59); [radhanite/evaluation.py (line 83)](/Users/arkoganguli/Projects/radhanite-ethonline/radhanite/evaluation.py:83); [tests/test_evaluation.py (line 83)](/Users/arkoganguli/Projects/radhanite-ethonline/tests/test_evaluation.py:83); [docs/pr_explanations/PR-012_TASK-001_EXPLANATION.md (line 121)](/Users/arkoganguli/Projects/radhanite-ethonline/docs/pr_explanations/PR-012_TASK-001_EXPLANATION.md:121)
>
> evaluate() does not compare the outcome against the success condition. It strips and records the condition, but the verdict depends exclusively on the Outcome enum:
>
> evaluate(success_attempt, "tests pass").verdict       == Verdict.MET
> evaluate(success_attempt, "issue #184 closed").verdict == Verdict.MET
> evaluate(success_attempt, "2 + 2 == 5").verdict       == Verdict.MET
>
> The test named test_the_condition_does_not_change_the_verdict explicitly preserves this behavior.
>
> The controlled-input argument does not resolve the departure. Controlling the simulated evidence makes evaluation deterministic; it does not authorize evaluation to ignore the condition. By naming the input Outcome.SUCCESS, the simulator has already supplied the verdict, leaving evaluation as a tautological relabeling step. The specification deliberately separates simulated execution in §2.3 from comparison against the condition in §2.4.
>
> If the current Task.success_condition representation is insufficient for an objective comparison, that is a specification/interface gap to resolve with the product owner. Deferring the actual comparison until real execution leaves TASK-001 §2.4 and acceptance criterion 4 unimplemented. It also departs from PREREQ-001 §5.3.
>
> CODEX-PR012-02
>
> File and line: [radhanite/execution.py (line 91)](/Users/arkoganguli/Projects/radhanite-ethonline/radhanite/execution.py:91); [radhanite/execution.py (line 98)](/Users/arkoganguli/Projects/radhanite-ethonline/radhanite/execution.py:98)
>
> ScriptedSimulator traverses the supplied Sequence twice: once to validate its elements and again to create the stored tuple. It therefore does not necessarily store what it validated.
>
> I supplied a valid Sequence whose first traversal yielded Outcome.SUCCESS and whose second yielded "not-an-outcome". Construction succeeded, and execute() produced an Attempt whose outcome was a string. A second stateful sequence passed validation both times but caused two simulators constructed from the same sequence object to produce SUCCESS and FAILURE respectively.
>
> This also applies to a mutable sequence changed between validation and copying. Snapshotting the sequence once and validating that snapshot would close the validation gap.
>
> The ordinary list and tuple paths are deterministic, source-list mutation after construction does not affect an instance, and two ordinary simulator instances do not interfere. Nevertheless, the accepted public Sequence boundary permits unvalidated and variable scripts, departing from TASK-001 §2.3’s deterministic, controllable simulator requirement.
>
> CODEX-PR012-03
>
> File and line: [docs/pr_explanations/PR-012_TASK-001_EXPLANATION.md (line 110)](/Users/arkoganguli/Projects/radhanite-ethonline/docs/pr_explanations/PR-012_TASK-001_EXPLANATION.md:110); [docs/pr_explanations/PR-012_TASK-001_EXPLANATION.md (line 155)](/Users/arkoganguli/Projects/radhanite-ethonline/docs/pr_explanations/PR-012_TASK-001_EXPLANATION.md:155); [tests/test_execution.py (line 143)](/Users/arkoganguli/Projects/radhanite-ethonline/tests/test_execution.py:143); [tests/test_evaluation.py (line 107)](/Users/arkoganguli/Projects/radhanite-ethonline/tests/test_evaluation.py:107)
>
> The explanation says Attempt and Evaluation records cannot be altered afterwards, including through the previously discovered back door. The tests have similarly absolute names. Both objects remain writable using the deliberately open routes:
>
> object.__setattr__(attempt, "outcome", Outcome.SUCCESS)
> object.__setattr__(evaluation, "verdict", Verdict.MET)
> ctypes.pythonapi.PyObject_GenericSetAttr(...)
>
> The implementation itself is honest: _immutable.py expressly discloses these limits. Ordinary assignment and __dict__ mutation are blocked, and direct __setstate__ calls raise as intended. The defect is the unqualified explanation and test claim, not the bounded immutability implementation.
>
> This departs from TASK-001 §7’s requirement that documentation claim no behavior the tests do not demonstrate.
>
> Additional checks:
>
> - PARTIAL_PROGRESS produces NOT_MET through both its direct test and the complete Outcome loop.
> - Partial progress and failure retain distinct Evaluation.outcome values and reasons.
> - Verdict has exactly MET and NOT_MET. A third verdict is neither required nor justified; partial progress is an outcome, not a softened verdict.
> - Nothing samples or otherwise consults a strategy probability when choosing the scripted outcome.
> - Consuming a script is legitimate run state. Separate ordinary simulators own separate tuple snapshots and positions.
> - Exhausting a script is reasonably treated as test-fixture/caller failure rather than inventing an economic outcome. It is not an unauthorized product rule.
> - The four requested mutations were detected:
>   - partial progress returning MET: four failures;
>   - ignoring escalated: four failures;
>   - always returning script[0]: two failures;
>   - removing empty-condition validation: two failures.
> - Eight files are changed, with eight table rows.
> - Test discovery finds 16 execution tests and 14 evaluation tests: 30 new, increasing the suite from 139 to 169.
> - All other factual counts checked in the explanation are correct.
> - No dependency, model API, learned behavior, database, UI, or other TASK-001 §3 exclusion appears.
> - The simulator is consistently described as a controlled fixture, not intelligence.
> - Attempt.success_probability is used in the attempt record and its rendering and carries the declared stage-specific figure needed for inspectability. ScriptedSimulator.remaining exposes the current state of the controllable fixture and is exercised directly. Neither is an abstraction justified only by an unauthorized future task, so ARCHITECTURE §6 item 7 is not violated.
>
> Rejected — CODEX-PR012-01 departs from TASK-001 §2.4 and acceptance criterion 4, and CODEX-PR012-02 departs from §2.3’s deterministic, controlled simulator requirement.

## 3. Outcome

**Rejected.** All three findings accepted without dispute and corrected.

`CODEX-PR012-01` is the most consequential finding of the project so far. The
implementing agent had argued in the review prompt itself that deriving the
verdict from the outcome alone was defensible because the outcome is a
controlled input. The reviewer rejected that argument on its merits: controlling
the evidence makes evaluation deterministic, it does not license evaluation to
ignore the condition. By naming the input `SUCCESS` the simulator had already
supplied the verdict, and criterion 4 was simply unimplemented.

The reviewer also identified the right resolution — that if the interface could
not support an objective comparison, it was a specification gap for the product
owner. It could: the simulator now reports evidence rather than a verdict, and
the comparison is real without any change to the specification.

## 4. Corrections

| Finding | Correction commit | What changed |
|---|---|---|
| `CODEX-PR012-01` | `a5cbfa5` | The simulator reports an `Observation` — the set of conditions that became true — instead of a `SUCCESS`/`FAILURE` label. Evaluation compares the task's success condition against that set and nothing else. The `Outcome` enum is removed entirely, since a descriptive label beside the evidence would invite the same tautology back. No synonym or approximate matching. |
| `CODEX-PR012-02` | `a5cbfa5` | The script is snapshotted once and the snapshot validated, so what is stored is what was checked. Verified by mutation: restoring validate-then-copy fails the new test. |
| `CODEX-PR012-03` | `1e0bd28` | The absolute immutability claim and the test names are bounded, and point at `radhanite/_immutable.py`, which states what is and is not prevented. |

```
git log --grep=CODEX-PR012
```

### Verification after correction

```
$ python -m unittest discover
Ran 183 tests in 0.015s
OK
```

The finding, retested:

```
achieved {"tests pass"} judged against "tests pass"        -> MET
achieved {"tests pass"} judged against "issue #184 closed" -> NOT MET
achieved {"tests pass"} judged against "2 + 2 == 5"        -> NOT MET
```
