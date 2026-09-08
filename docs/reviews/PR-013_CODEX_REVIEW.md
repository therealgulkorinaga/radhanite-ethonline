# Codex review — PR-013

**Pull request:** [#13](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/13) — the economic loop, the run record, and the entry point (TASK-001)
**Reviewer:** Codex (independent review agent, `AI_BUILD_GOVERNANCE.md` §1.3)
**Reviewed against:** `tasks/TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md`, `docs/PREREQ-001_PRODUCT_DEFINITION.md`, `docs/ARCHITECTURE.md`
**Date issued:** 2026-09-08
**Outcome:** **Rejected** — §§2.2, 2.5 and 2.6 and criteria 2, 5, 8, 9, 11 and 14 departed from. Eight findings, all corrected.
**Commit reviewed:** `2b7331b`

---

## 1. Prompt issued

Recorded before the review was run.

**On what was issued.** The prompt below is the formal body. The message that
delivered it to the reviewer also carried a closing sentence written in the
session, after the prompt block:

> Part D question 11 is the one that matters most — I'm claiming all 17 criteria
> are met, and that claim deserves an independent walk rather than my word.

That sentence reached the reviewer as part of the pasted text and was missing
from this record, which claimed the prompt was recorded verbatim. It is restored
here. The lesson is that "the prompt" is whatever was actually sent, not only
the part inside the code block.

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

Recorded as received. Not summarized, softened, or filtered. The fidelity note in
`PR-012_CODEX_REVIEW.md` applies: a review reaches this record by being copied
out of the review tool by a person, and some formatting does not survive that
hop.

> I reviewed PR #13 at `2b7331b` and reproduced the important paths and mutations. The suite passes 216 tests on Python 3.12.13, but TASK-001 is not complete.
>
> ### Findings
>
> CODEX-PR013-01
>
> File: [radhanite/run.py:275](/Users/arkoganguli/Projects/radhanite-ethonline/radhanite/run.py:275)
>
> The loop applies §2.5 before the opening attempt, using a synthetic probability of zero and recording the result as `ESCALATE`. This is invented policy. TASK-001's authorized pipeline places simulated execution and evaluation before the escalation/stop decision, and §2.5 says the decision is made "from the verdict, the spend so far, and the remaining budget." No verdict exists here.
>
> Consequently, a low-value task can be denied its first affordable selected attempt by a rule authorized only for additional expenditure. This departs from TASK-001 §§2, 2.5 and acceptance criterion 5.
>
> CODEX-PR013-02
>
> File: [radhanite/run.py:294](/Users/arkoganguli/Projects/radhanite-ethonline/radhanite/run.py:294)
>
> A `STOP` decision does not stop the run. It removes the strategy and continues searching.
>
> I reproduced both forms:
>
> - After a value-condition `STOP`, the declared demonstration continues to Exhaustive Attempt and can succeed.
> - With custom strategies, an unaffordable $10 escalation records `STOP` for the budget condition, after which the loop buys another strategy and reports success.
>
> TASK-001 §2.5 defines Stop as "Terminate and report the task incomplete" and says "Otherwise, stop." PREREQ-001 §5.4 says the same. "Moving to a dearer strategy" can legitimately constitute escalation to more capable intelligence, but the loop must select that as the next action before applying §2.5; it cannot issue `STOP` for one candidate and then reinterpret that verdict as "skip."
>
> This departs from TASK-001 §2.5 and acceptance criteria 5, 8, 9 and 11.
>
> CODEX-PR013-03
>
> File: [radhanite/run.py:262](/Users/arkoganguli/Projects/radhanite-ethonline/radhanite/run.py:262)
>
> `run()` converts `strategies` to a list before calling `select()`. This bypasses `select()`'s guard against unordered collections.
>
> I passed `set(DECLARED_STRATEGIES)` and repeated the identical run under hash seeds 1–10. The first selected strategy varied among Direct Attempt, Progressive Escalation and Exhaustive Attempt.
>
> This departs from TASK-001 §2.2 and acceptance criterion 2.
>
> CODEX-PR013-04
>
> Files: [radhanite/run.py:246](/Users/arkoganguli/Projects/radhanite-ethonline/radhanite/run.py:246), [PR-013_TASK-001_EXPLANATION.md:126](/Users/arkoganguli/Projects/radhanite-ethonline/docs/pr_explanations/PR-013_TASK-001_EXPLANATION.md:126)
>
> A completed call to `run()` returns an in-memory `RunRecord` but writes no JSON file. Only callers that separately invoke `RunRecord.write()`—such as the CLI—produce one.
>
> I completed a successful run in an empty temporary directory and found no JSON file. The explanation's claim that "Every run writes a file" is therefore false.
>
> TASK-001 §2.6 requires the in-memory record to be written as a JSON file per completed run, and acceptance criterion 14 says every run produces a JSON run record.
>
> CODEX-PR013-05
>
> Files: [radhanite/run.py:266](/Users/arkoganguli/Projects/radhanite-ethonline/radhanite/run.py:266), [docs/RUN_RECORDS.md:182](/Users/arkoganguli/Projects/radhanite-ethonline/docs/RUN_RECORDS.md:182)
>
> When no strategy is affordable, the run stops without creating a step or a decision. For budgets of $0 and $0.01, the JSON representation has `"steps": []`; there are no §2.5 quantities and no `failed_conditions`.
>
> This also disproves the guide's unqualified instruction that the last step's `failed_conditions` explains why a run stopped.
>
> The selector itself describes this path as the §2.5 budget condition, so bypassing the decision record departs from TASK-001 §§2.5–2.6 and acceptance criteria 9 and 14.
>
> CODEX-PR013-06
>
> File: [radhanite/run.py:205](/Users/arkoganguli/Projects/radhanite-ethonline/radhanite/run.py:205)
>
> The JSON records which strategy was used and why its purchase passed the economic rule, but not why that strategy was selected. It does not record catalogue order, the "first affordable strategy" rule, or the alternatives skipped.
>
> A reader can recompute the purchase verdict but cannot audit the strategy-selection decision from the record. This departs from TASK-001 §2.6, which explicitly requires "the strategy chosen and why."
>
> CODEX-PR013-07
>
> File: [tests/test_run.py:241](/Users/arkoganguli/Projects/radhanite-ethonline/tests/test_run.py:241)
>
> Removing `failed_conditions` entirely from the JSON left all 33 new loop and CLI tests passing. The "carries everything" test checks only the six numerical quantities, while the recomputation test checks only the verdict.
>
> The implementation currently emits correct failed conditions on recorded decisions, but the tests cannot detect removal of a field expressly required by TASK-001 §2.5 and acceptance criterion 14.
>
> CODEX-PR013-08
>
> Files: [PR-013_CODEX_REVIEW.md:13](/Users/arkoganguli/Projects/radhanite-ethonline/docs/reviews/PR-013_CODEX_REVIEW.md:13), [issued prompt:105](/Users/arkoganguli/.codex/attachments/19548048-48a4-4029-b932-ca86fe3ddbb3/pasted-text.txt:105)
>
> The review record claims the prompt was recorded verbatim, but it omits the issued closing paragraph beginning "Part D question 11 is the one that matters most…". The substantive formal body otherwise matches after disregarding paste indentation and trailing whitespace.
>
> This fails the requested literal-verbatim transcription check.
>
> ### Other verification
>
> - The ledger is the only spending path. Negative spending and overspending are refused.
> - Removing the ledger's second overspend check did not fail tests because `decide()` and selection independently prevent the current loop from reaching it. The specified ceiling still held, so I did not issue a separate finding for that redundant mutation.
> - Zero-cost strategies, zero budgets, intermediate budgets, empty catalogues, single-strategy catalogues and budgets through `1E+50` did not overspend.
> - At approximately `1E+199`, the existing 200-digit exactness context raises `Inexact` rather than rounding. That is the previously documented exactness refusal, not an overspend, and TASK-001 specifies no unbounded numeric range.
> - JSON decisions that do exist recompute correctly, including their current failed-condition tuples.
> - Value and budget refusal reasons are accurate for steps that exist.
> - JSON amounts as strings are appropriate and preserve exactness.
> - Repeated runs produced byte-identical JSON; achieved frozensets are sorted.
> - `Step.bought`, `RunRecord.succeeded`, and `ScriptedSimulator.remaining` serve current implementation or inspection needs. None is speculative future abstraction.
> - No external dependency or TASK-001 §3 exclusion appears. The CLI remains developer-facing rather than a production UI.
> - The diff contains 11 files. Discovery finds 27 new tests in `test_run.py`, 6 in `test_cli.py`, 33 new total, and 216 overall.
> - All four commits map explicitly to TASK-001, and their hashes exist.
> - The first-refusal and unconditional-opening mutations caused relevant tests to fail. Removing strategy removal caused the suite to hang in a retry loop, rather than passing silently.
>
> ### Acceptance criteria
>
> | Criterion | Result |
> |---|---|
> | 1 | Met |
> | 2 | Not met — unordered catalogues bypass the determinism guard |
> | 3 | Met |
> | 4 | Met |
> | 5 | Not met — §2.5 is applied before a verdict and its Stop result is ignored |
> | 6 | Met |
> | 7 | Met |
> | 8 | Not met — a value-condition Stop need not terminate |
> | 9 | Not met — a budget-condition Stop need not terminate |
> | 10 | Met |
> | 11 | Not met end to end — no-improvement produces Stop, but the loop continues |
> | 12 | Met on the exercised spending paths |
> | 13 | Met |
> | 14 | Not met — persistence and audit-record omissions |
> | 15 | Met at the stated minimum, although one required record field lacks mutation protection |
> | 16 | Met |
> | 17 | Met — 216 tests pass |
>
> Rejected — TASK-001 §§2.2, 2.5 and 2.6 and acceptance criteria 2, 5, 8, 9, 11 and 14 are departed from.

## 3. Outcome

**Rejected.** All eight findings accepted without dispute and corrected.

This was the most serious rejection of the project. Two of the three decisions
the implementing agent had flagged as possibly invented policy **were** invented
policy, and both were wrong in the same direction: they treated §2.5's rule as
something to consult freely rather than as a stage of a pipeline with a fixed
position and a terminal verdict.

- **`-01`** — the rule was applied before the opening attempt, against a
  synthetic probability of zero. §2 places execution and evaluation before the
  decision, and §2.5 decides *from a verdict*. There was none.
- **`-02`** — a Stop did not stop. It was treated as "skip this candidate",
  which turned the rule's only refusal into a suggestion, and let a run that had
  been told to stop go on to succeed.

The reviewer also supplied the resolution for `-02`: select the next action
first, then rule on that one. Passing over a candidate that offers nothing new
is selection, not economics, and a Stop can then always be terminal.

`-03` through `-07` were a determinism guard bypassed by a type conversion, a
record that was never written, a stop path that recorded nothing, a record
missing the selection rationale §2.6 requires by name, and a test suite that
could not detect the removal of a required field.

## 4. Corrections

| Finding | What changed |
|---|---|
| `CODEX-PR013-01` | The opening attempt is selected and executed without consulting §2.5, and its step carries no decision. A $0.05 task now gets its $0.02 opening attempt and is refused further spending. |
| `CODEX-PR013-02` | A Stop terminates the run. Selection picks the next action — first in declared order that is affordable and improves on what has been achieved — and §2.5 rules on that one candidate. |
| `CODEX-PR013-03` | `run()` refuses non-sequences itself rather than converting and slipping past `select()`'s guard. |
| `CODEX-PR013-04` | `run()` writes the JSON record. The destination is configurable; `None` is for tests that should not touch the filesystem. The CLI no longer writes separately. |
| `CODEX-PR013-05` | There is always a step. Where a candidate remains, §2.5 is applied to the cheapest so the failing condition is recorded; where none remains, the step records why nothing was attempted. The guide's unqualified claim is corrected. |
| `CODEX-PR013-06` | Every step records the selection rule that chose it and names what was passed over. |
| `CODEX-PR013-07` | Three tests assert `failed_conditions` directly. Verified by mutation: removing the field now fails four tests. |
| `CODEX-PR013-08` | The sentence issued after the prompt block is restored to the record. |

One further defect was found while checking the `-05` fix and is not from the
review: the stop summary named whichever leftover candidate was cheapest rather
than the one whose unaffordability ended the run. The summary is now the
selection reason, which names every remaining candidate and why each was
unusable.

