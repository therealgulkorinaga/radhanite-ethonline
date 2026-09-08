# Codex review — PR-012

**Pull request:** [#12](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/12) — simulated execution and outcome evaluation (TASK-001)
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

_Pending. Codex has not yet reviewed this pull request._

## 3. Outcome

_Pending._

## 4. Corrections

_None yet._
