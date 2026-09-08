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

## 1b. Second review prompt

Issued after the three corrections were pushed, and committed before that second
review was run, per §7.5.

```text
You are the independent review agent for the Radhanite repository, per
docs/AI_BUILD_GOVERNANCE.md §1.3.

This is a SECOND review of pull request #12:
https://github.com/therealgulkorinaga/radhanite-ethonline/pull/12

You reviewed it at commit ad55b32 and REJECTED it with three findings,
CODEX-PR012-01 through -03. Three correction commits have since been pushed:
65e36d0, a32e241 and 3f824a0. Your first review is recorded verbatim in
docs/reviews/PR-012_CODEX_REVIEW.md.

Review against these authoritative documents ONLY:
  - tasks/TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md
  - docs/PREREQ-001_PRODUCT_DEFINITION.md
  - docs/ARCHITECTURE.md

Do NOT treat the PR explanation as evidence of correctness (§4.3).

WHAT CHANGED, AND WHY IT NEEDS HARD LOOKING AT

CODEX-PR012-01 was not fixed by patching evaluate(). The execution stage was
rebuilt: the Outcome enum is gone, and the simulator now reports an Observation
carrying `satisfied` — the set of conditions that became true — plus a `note`
for human readers. evaluate() decides MET if and only if the task's success
condition is a member of that set.

This is a substantial redesign made in response to a single finding, under
deadline pressure, by the agent whose previous design you rejected. Treat it
accordingly.

PART A — is the comparison now real?

1. Confirm the same attempt is judged differently against different conditions.
   Try to find any input where the verdict does not depend on the condition.
2. Confirm nothing but `satisfied` reaches the verdict — not the note, not the
   strategy, not its stated probability, not the cost, not the escalated flag.
3. Membership is exact after stripping. Is exact matching correct under §2.4,
   or has the implementing agent now invented a matching rule the specification
   does not state? Consider case, punctuation, and the fact that a task's
   success condition and a scripted observation are written by the same person.
4. Does the redesign leave criterion 4 genuinely implemented, or has the
   tautology simply moved — is scripting `satisfied={"tests pass"}` for a task
   whose condition is "tests pass" the same trick in a new place? This is the
   question I most want answered.

PART B — did the rebuild break or lose anything?

5. §2.3 requires success, failure AND partial progress each producible on
   demand. With Outcome gone, is partial progress still a first-class,
   exercisable case, or has it become an accident of set membership?
6. Is the distinction between partial progress and outright failure still
   preserved in the record, as §2.4 requires?
7. Determinism: re-attack it. Same script, same run? Two simulators
   independent? Does Observation's frozenset introduce any iteration-order
   dependence in the reason string or anywhere else?
8. CODEX-PR012-02: the script is now snapshotted once and the snapshot
   validated. Retry your stateful-Sequence attack and any variant. Can anything
   unvalidated still be stored?
9. Does anything now accept an input the specification does not require
   rejecting, or reject one it does not require rejecting (CODEX-PR006-04)?
   Assess Observation's rejection of blank conditions and its required note.

PART C — claims

10. CODEX-PR012-03: confirm the immutability claims in the explanation and the
    test names are now bounded and accurate, and that radhanite/_immutable.py
    still describes reality.
11. Verify every count and factual claim in the explanation independently,
    including the commit hashes cited in the review record — one round of those
    was written wrong and corrected before pushing.
12. Confirm your first-round findings are reproduced literally verbatim,
    punctuation and link formatting included. Non-verbatim transcription was
    CODEX-PR006-10 and recurred as CODEX-PR011-07.

PART D — mutations

13. Confirm these fail: make membership a substring test; make evaluate() return
    MET when `satisfied` is non-empty; make the simulator reuse one Observation
    for every attempt; make Observation.satisfied a plain set rather than
    frozenset.

FORMAT

Number any NEW findings continuing the sequence, per §3.1 — identifiers are
never reused, so start at:

    CODEX-PR012-04

If a previous finding is not properly fixed, say so against its ORIGINAL
identifier rather than issuing a new one.

If you find nothing new and all three fixes hold, say so explicitly.

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

## 2c. Second review findings

Recorded verbatim, as returned. **This transcript is incomplete**: the reviewer's
output was truncated mid-finding and is reproduced exactly as received, including
the point at which it breaks off. Nothing has been inferred or filled in.

> Reviewed PR #12 at `2c3de07`. The redesigned execution/evaluation model is substantively sound, and the unmodified suite passes 183 tests on Python 3.12.13.
>
> `CODEX-PR012-01` is fixed. The same attempt is `MET` for `"tests pass"` and `NOT_MET` for `"issue #184 closed"` or `"2 + 2 == 5"`. Changing strategy name, cost, probability, escalation status, or note does not affect the verdict; changing `satisfied` does.
>
> The tautology has not merely moved. A deterministic simulator necessarily scripts evidence. It now supplies facts that became true rather than a verdict, and evaluation applies a separate, counterfactual comparison: the identical observation can pass one condition and fail another. That genuinely implements TASK-001 §2.4 and criterion 4.
>
> Exact matching after trimming is the correct conservative rule. Case, punctuation, and wording remain significant, which avoids inventing synonym, fuzzy, or semantic interpretation that §2.4 does not authorize. Because the task and scenario fixtures are controlled together, exact agreement is practical. Trimming surrounding whitespace is normalization, not interpretation.
>
> `CODEX-PR012-02` is fixed. The sequence is snapshotted exactly once and that snapshot is validated. The original changing-sequence attack now stores the single value it read; late invalid elements raise, and mutating the source collection afterwards cannot affect the simulator.
>
> `CODEX-PR012-03` is not fully fixed.
>
> CODEX-PR012-03
>
> File and line: [docs/pr_explan Yen?] No. Need write exact no typo. Continue.

**The transcript ends there.** The finding's file references, description and the
review's concluding outcome were never received.

### What was done in the absence of the finding text

The defect class was known — an unqualified immutability claim — so the
implementing agent searched for surviving instances rather than guessing at the
finding. Two were found, both in the file whose path the truncated reference had
begun to name:

- Section 8 of the explanation still read "Neither can be altered afterwards",
  unqualified.
- The same section claimed "the test names now say so too", which was false:
  only the two test files this pull request touched had been renamed. Three
  older tests still made absolute claims while asserting only that ordinary
  assignment raises.

Both are corrected in `f0a2b1e`. **Whether these are what the finding names is
unknown.** If it identifies something else, `CODEX-PR012-03` remains outstanding,
and the outcome of this second review is unrecorded because it was never
received.

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
| `CODEX-PR012-01` | `65e36d0` | The simulator reports an `Observation` — the set of conditions that became true — instead of a `SUCCESS`/`FAILURE` label. Evaluation compares the task's success condition against that set and nothing else. The `Outcome` enum is removed entirely, since a descriptive label beside the evidence would invite the same tautology back. No synonym or approximate matching. |
| `CODEX-PR012-02` | `65e36d0` | The script is snapshotted once and the snapshot validated, so what is stored is what was checked. Verified by mutation: restoring validate-then-copy fails the new test. |
| `CODEX-PR012-03` | `a32e241` | The absolute immutability claim and the test names are bounded, and point at `radhanite/_immutable.py`, which states what is and is not prevented. |

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
