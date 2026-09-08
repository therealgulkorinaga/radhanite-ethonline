# Codex review — PR-011

**Pull request:** [#11](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/11) — strategy fixtures and deterministic selection (TASK-001)
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

Review pull request #11:
https://github.com/therealgulkorinaga/radhanite-ethonline/pull/11

It implements TASK-001 §2.2 — strategy fixtures and deterministic selection —
and addresses acceptance criteria 2 and 13.

Review against these authoritative documents ONLY:
  - tasks/TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md
  - docs/PREREQ-001_PRODUCT_DEFINITION.md
  - docs/ARCHITECTURE.md

Do NOT treat docs/pr_explanations/PR-011_TASK-001_EXPLANATION.md as evidence of
correctness (§4.3).

PART A — determinism and declared constants

1. Criterion 2 requires identical inputs to produce an identical selection.
   Attack that. Is there ANY path by which selection could vary — dict or set
   iteration order, hashing, module import order, mutable default, global
   state, or the ambient decimal context? The tests assert determinism; try to
   break it rather than trusting them.

2. Criterion 13 requires costs and probabilities to be static declared
   constants, never estimated, learned, inferred, or updated from run history.
   Confirm nothing computes them. Confirm DECLARED_STRATEGIES cannot be mutated
   from outside — try, including via the Strategy objects it contains.

PART B — the selection rule itself

3. The rule is "first strategy in declared order whose initial_cost the
   remaining budget can cover", making catalogue order the policy. TASK-001
   §2.2 requires rules that are fixed and inspectable but does not specify
   which rule. Is order-as-policy a legitimate reading, or has the implementing
   agent invented product policy the specification did not authorize? This is
   the question I most want answered.

4. select() does not take the Task, though §2.2 says "given the task and the
   state of the run so far". The PR argues an accepted-and-ignored parameter
   would be speculative scope under ARCHITECTURE §6 item 7. Assess that
   argument — is omitting it a departure from §2.2?

5. select() returns None when nothing is affordable, and raises on a negative
   budget. Are both defensible, or is either an invented rule (CODEX-PR006-04)?

PART C — scope and boundaries

6. Does anything TASK-001 §3 excludes appear? Any dependency, learned
   probability, database, UI, or ML? Check imports and configuration.

7. Strategy permits an escalation that does not improve, or worsens, the chance
   of success. The PR argues §2.5 must answer that with Stop and forbidding it
   would make that outcome unreachable. Is that correct?

8. Money gained __format__ in this PR, which is not obviously part of §2.2. Is
   that justified scope, or should it have been separate? Does it round, raise,
   or lose precision under a changed ambient decimal context — CODEX-PR006-08
   was exactly this class of defect.

PART D — tests and claims

9. Are the tests real? Mutate and confirm failures: reverse the catalogue
   order, change >= to > in the affordability check, change a declared
   probability, make select() return the last match instead of the first, and
   make DECLARED_STRATEGIES a list.

10. Verify every count and factual claim in the explanation independently —
    file count, per-file and total test counts, and the twelve declared
    figures. Stale hand-maintained counts have been findings five times in this
    project (CODEX-PR003-04, CODEX-PR006-09, CODEX-PR009-01 among them).

FORMAT OF YOUR FINDINGS

Number every finding, per §3.1:

    CODEX-PR011-01
    CODEX-PR011-02
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
