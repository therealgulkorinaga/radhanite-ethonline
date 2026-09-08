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

## 1b. Second review prompt

Issued after the eight corrections were pushed, and committed before that second
review was run, per §7.5.

```text
You are the independent review agent for the Radhanite repository, per
docs/AI_BUILD_GOVERNANCE.md §1.3.

This is a SECOND review of pull request #13:
https://github.com/therealgulkorinaga/radhanite-ethonline/pull/13

You reviewed it at commit 2b7331b and REJECTED it with eight findings,
CODEX-PR013-01 through -08, marking six of seventeen acceptance criteria not
met. Your review is recorded verbatim in docs/reviews/PR-013_CODEX_REVIEW.md.

The loop was rebuilt in response. This is not a patched version of what you
rejected: the order of operations changed, selection gained a new
responsibility, and Step and the JSON schema both changed shape.

Review against these authoritative documents ONLY:
  - tasks/TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md
  - docs/PREREQ-001_PRODUCT_DEFINITION.md
  - docs/ARCHITECTURE.md

Do NOT treat the PR explanation or docs/RUN_RECORDS.md as evidence of
correctness (§4.3).

WHAT CHANGED

  -01  The opening attempt is selected and executed without consulting §2.5.
       Its Step carries decision=None.
  -02  A Stop terminates the run. Selection now chooses the next action first —
       the first candidate in declared order that is affordable AND offers a
       higher success probability than has already been achieved — and §2.5
       rules on that single candidate.
  -03  run() refuses non-Sequence strategies itself.
  -04  run() writes the JSON record. record_directory defaults to "runs" and
       accepts None for tests.
  -05  There is always at least one Step. Where a candidate remains, §2.5 is
       applied to the cheapest so a failing condition is recorded.
  -06  Every Step records selection_reason, naming the rule and what was passed
       over.
  -07  Three tests assert failed_conditions directly.
  -08  The omitted sentence is restored to the recorded prompt.

Plus one defect found by the implementing agent, not by you: the stop summary
named whichever leftover candidate was cheapest rather than the one whose
unaffordability ended the run. The summary is now the selection reason.

PART A — is the pipeline order now right?

1. Confirm §2.5 is never consulted before a verdict exists. Is there any path
   where it is?
2. Confirm a Stop always terminates. Try hard to construct a run that receives
   a Stop and continues — both conditions, and both within a strategy and
   across strategies.
3. Selection now skips candidates offering no improvement. Is that legitimately
   selection under §2.2, or has the refusal §2.5 was supposed to make simply
   been moved somewhere it cannot be seen? This is the question I most want
   answered: the loop can now decline to buy something without any economic
   decision being recorded for it.
4. Does the new selection rule leave any candidate unreachable that the
   specification requires be considered?

PART B — the criteria you marked not met

5. Walk criteria 2, 5, 8, 9, 11 and 14 specifically and state whether each is
   now met. Then walk the remaining eleven to confirm none regressed.

PART C — did the rebuild break anything?

6. Determinism: same scenario, same run? Byte-identical JSON?
7. The ceiling: attack it again on the new code paths.
8. run() now writes files. Does it ever overwrite an existing record? Is the
   numbering safe if the directory already contains records, or contains files
   that are not records?
9. Step.decision is now optional. Does anything assume it is present?
10. Does the CLI still avoid double-writing now that run() writes?

PART D — claims and record integrity

11. Verify every count and factual claim in the explanation independently.
12. Confirm the recorded findings are reproduced as received, and that the
    restored prompt sentence is correct.
13. Confirm every cited commit hash exists.

FORMAT

Number any NEW findings continuing the sequence, per §3.1 — identifiers are
never reused, so start at:

    CODEX-PR013-09

If a previous finding is not properly fixed, say so against its ORIGINAL
identifier rather than issuing a new one.

If you find nothing new and all eight fixes hold, say so explicitly.

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

## 2c. Second review — received corrupted

Recorded as received. **This transcript is not usable in full.** From
`CODEX-PR013-10` onward the output degenerates into what appears to be the
reviewer's own internal reasoning, and no concluding outcome was returned. It is
reproduced exactly, including the corruption, rather than tidied or truncated at
a convenient point.

> I reviewed the rebuilt PR #13 at `b110a6c`. Fixes `-01`, `-02`, `-03`, `-07`, and `-08` hold. Fixes `-04`, `-05`, and `-06` remain incomplete, and four new defects were found.
>
> ### Previous findings not fully fixed
>
> CODEX-PR013-04
>
> File: `radhanite/run.py:342`
>
> Default runs now write JSON and the CLI no longer double-writes. However, the public `record_directory=None` option still permits completed runs without a JSON file; all 37 loop tests use that escape hatch. I reproduced a successful completed run with `None` and no file was produced.
>
> The unqualified explanation claim that "Every run writes a file" is therefore still false. TASK-001 §2.6 and criterion 14 provide no testing exemption.
>
> CODEX-PR013-05
>
> File: `radhanite/run.py:371`
>
> The unaffordable-opening path now creates a step, but it still does not create the §2.5 decision, quantities, or failed condition required by the original finding.
>
> With budgets of $0 and $0.01, the sole step has:
>
> - `strategy_name=None`
> - `decision=None`
> - no `failed_conditions`
>
> This only fixes the empty `steps` symptom. The selector still describes this as TASK-001's budget condition, but the run record does not record that condition. The departure from TASK-001 §§2.5–2.6 and criterion 14 remains.
>
> CODEX-PR013-06
>
> Files: `radhanite/run.py:334`, `radhanite/run.py:400`
>
> Selection reasons are correct for the opening attempt and ordinary selected purchases. The terminal fallback is not.
>
> When `_next_action()` says no candidate is worth selecting, the loop applies a separate `_cheapest()` policy and attaches a decision to that rejected candidate. The recorded `selection_reason` lists why every candidate was unusable but never says that the named strategy was subsequently chosen because it was cheapest.
>
> In the default stopped scenario, the final step names Progressive Escalation and records a value-condition Stop even though selection rejected it and the only improving candidate—Exhaustive escalation—was unaffordable. The selection summary is accurate, but the attached economic decision is not the decision that caused the run to end.
>
> The record therefore still does not explain why the strategy named on every step was selected, contrary to TASK-001 §2.6.
>
> ### New findings
>
> CODEX-PR013-09
>
> Files: `radhanite/run.py:482`, `radhanite/run.py:508`
>
> Record numbering is safe for sequential runs but not concurrent runs. `_next_record_number()` scans for the next number and `write_text()` later overwrites that path without exclusive creation.
>
> I synchronized eight runs immediately after their number lookup. All eight completed successfully, all selected `run-001.json`, and only one file remained. Seven completed-run records were silently overwritten.
>
> This departs from TASK-001 §2.6 and criterion 14's requirement for one JSON record per completed run.
>
> CODEX-PR013-10
>
> Files: `radhanite/run.py:122`, `tests/test_run.py:82`, `PR-013_TASK--001 pragmatic retirement question: must balance user desire to spend budget across all strategies? User says candidate skip question. We accept skip but fallback issue.]/private/tmp/radhanite-pr13? No malformed. Need avoid. Let's continue carefully. We need final message correct. I am in analysis before final? Actually composing final not sent yet. Need ensure links valid. Continue final from scratch maybe.
>
> Need name file explanation line213. Link proper. Need no accidental weird. We'll draft full.
>
> CODEX-PR013-10:
> - doc claim decision None opening only false for no strategies/unaffordable? Step1 no attempt. For exhaustion after single strategy, terminal later step None. Test every later weak. `docs RUN_RECORDS line135 first step none` doesn't say only. Explanation line213 says every later. RunRecord doc line155 each step carries. Mention.
> Departs claims and §2.6? A terminal selection-only step can be legitimate, but false doc/test. Test name false. Task run record explanation must be accurate. use TASK §5 deliverable4 and §7 review notes no untested claims? §7 is review notes authoritative task. Good.
> - New finding 11 docs stale.
> - New 12 double read.
>
> Need review record transcript:
> - `Recorded as received`, all complete. restored sentence. no new.
> - counts etc.
>
> Need final outcome.
>
> Let's redo final in full, not too huge. Ensure last line. Use clone links. After user likely records response, no matter temp links.
>
> Potential output must end one outcome. Fine. Let's send. for pull 13

**The transcript ends there.** No outcome was returned.

### What was acted on, and what was not

Four findings were stated clearly enough to act on, and were corrected:
`CODEX-PR013-04`, `-05`, `-06` and `-09`.

Three were not. `-10`, `-11` and `-12` appear only inside the corrupted section.
The fragments suggest `-10` concerns a documentation or test claim that
`decision` is `None` for the opening attempt *only* — which a terminal
selection-only step also makes false — and that `-11` and `-12` concern stale
documentation and a double read. **None of that is recorded as a finding**,
because inferring findings from corrupted output and writing them down as though
they had been made would be worse than leaving them open.

`CODEX-PR013-10`, `-11` and `-12` are therefore **open and unaddressed**, and the
outcome of this review is **unrecorded**, because none was returned. A clean
re-run has been requested.

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
| `CODEX-PR013-04` | `run()` writes the JSON record. The CLI no longer writes separately. *(The `None` option described here was later removed entirely — see the second-pass corrections.)* |
| `CODEX-PR013-05` | There is always a step. *(The "cheapest candidate" rule described here was later replaced — see the second- and third-pass corrections.)* |
| `CODEX-PR013-06` | Every step records the selection rule that chose it and names what was passed over. |
| `CODEX-PR013-07` | Three tests assert `failed_conditions` directly. Verified by mutation: removing the field now fails four tests. |
| `CODEX-PR013-08` | The sentence issued after the prompt block is restored to the record. |

One further defect was found while checking the `-05` fix and is not from the
review: the stop summary named whichever leftover candidate was cheapest rather
than the one whose unaffordability ended the run. The summary is now the
selection reason, which names every remaining candidate and why each was
unusable.

