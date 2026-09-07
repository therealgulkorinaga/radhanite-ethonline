# Codex review — PR-006

**Pull request:** [#6](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/6) — exact money and the five task inputs (TASK-001)
**Reviewer:** Codex (independent review agent, `AI_BUILD_GOVERNANCE.md` §1.3)
**Reviewed against:** `tasks/TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md`, `docs/PREREQ-001_PRODUCT_DEFINITION.md`, `docs/ARCHITECTURE.md`
**Date issued:** 2026-09-07
**Outcome:** _pending — review not yet run_

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

## 2. Findings returned

_Pending. Codex has not yet reviewed this pull request._

Findings will be recorded here verbatim, numbered `CODEX-PR006-01` onward per
`§3.1`.

## 3. Outcome

_Pending._

## 4. Corrections

_None yet._
