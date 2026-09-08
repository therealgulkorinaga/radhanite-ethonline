# Codex review — PR-013

**Pull request:** [#13](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/13) — the economic loop, the run record, and the entry point (TASK-001)
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

Review pull request #13:
https://github.com/therealgulkorinaga/radhanite-ethonline/pull/13

This completes TASK-001. It implements §5 deliverables 1, 4 and 5 and §2.6,
addressing acceptance criteria 1, 12 and 14 — and therefore claims the task's
remaining criteria are met. Verify that claim rather than accepting it.

Review against these authoritative documents ONLY:
  - tasks/TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md
  - docs/PREREQ-001_PRODUCT_DEFINITION.md
  - docs/ARCHITECTURE.md

Do NOT treat docs/pr_explanations/PR-013_TASK-001_EXPLANATION.md or
docs/RUN_RECORDS.md as evidence of correctness (§4.3).

PART A — three decisions that are not forced by the specification

The implementing agent made these and flags them as the most likely places it
has invented product policy. CODEX-PR006-04 was exactly that mistake.

1. Every purchase is weighed by §2.5's rule, INCLUDING the first, with
   current_success_probability = 0. §2.5 describes an escalation decision. Is
   applying it to the opening attempt a legitimate reading, or an invented rule?
   Note the consequence: a task whose value cannot justify the cheapest strategy
   buys nothing at all.
2. Moving to a dearer strategy is weighed by the same rule, treating the next
   strategy's initial probability as the "post escalation" probability. Is that
   the same economic question, or a second rule wearing the first one's clothes?
3. A refusal ends a strategy but not the run: the loop continues to the next
   affordable untried strategy. Is continuing correct, or should a refusal stop
   the run? Consider what §2.5's marginal reasoning implies.

PART B — criterion 12, the budget ceiling

4. Attack it. Find any path where spending exceeds the budget, or the remaining
   balance goes negative. Try zero budgets, budgets between strategy prices,
   very large budgets, empty strategy lists, single-strategy lists, and
   strategies priced at zero.
5. _Ledger refuses negative spends and refuses to overspend. Is the ledger
   actually on every spending path, or can a purchase bypass it?
6. The PR-006 review noted a running balance would have to enforce
   non-negativity itself. Confirm this discharges that, and that Money's
   permissiveness cannot leak through.

PART C — criterion 14 and §2.6, the record

7. Can EVERY decision be recomputed from the JSON alone? Take a record, apply
   §2.5's rule yourself to each step's recorded quantities, and confirm the
   verdict and failed conditions match. Look for anything a decision depended on
   that is not recorded.
8. Steps with no attempt record why nothing was bought. Confirm the reason is
   present and accurate for both a budget refusal and a value refusal.
9. Amounts are written as JSON strings rather than numbers. Assess that choice.
10. Is the record stable — does the same scenario produce byte-identical JSON?
    Consider frozenset ordering.

PART D — the whole task

11. Walk all 17 acceptance criteria in TASK-001 §4 and state which are met and
    which are not. The PR claims all 17. Check each independently, especially
    15 (the required test coverage) and 16 (nothing excluded appears).
12. Does anything TASK-001 §3 excludes appear anywhere — including the CLI and
    the docs? Is the entry point a "developer-facing way to run one task", or
    has it become the production UI §3 forbids?
13. Any abstraction justified only by a future task (ARCHITECTURE §6 item 7)?
    Assess Step.bought, RunRecord.succeeded and ScriptedSimulator.remaining.

PART E — carried-forward defect classes

Six classes have recurred in this project. Check each:

14. Overstated immutability claims — every test name and document claim.
15. Invented product rules — see Part A.
16. Tests that cannot detect what they claim. Mutate and confirm failures:
    remove the ledger's overspend check; make the loop stop at the first
    refusal; make the opening attempt unconditional; drop failed_conditions
    from the JSON; make the loop retry a strategy already tried.
17. Stale hand-maintained counts — verify every count independently.
18. Non-verbatim transcription in the review record.
19. Cited commit hashes that do not exist.

FORMAT OF YOUR FINDINGS

Number every finding, per §3.1:

    CODEX-PR013-01
    CODEX-PR013-02
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
