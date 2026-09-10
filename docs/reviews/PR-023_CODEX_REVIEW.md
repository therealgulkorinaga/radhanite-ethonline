# Codex review — PR-023

**Pull request:** [#23](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/23) — TASK-006: ranking and deterministic tie-breaking
**Reviewer:** Codex (independent review agent, `AI_BUILD_GOVERNANCE.md` §1.3)
**Reviewed against:** `tasks/TASK-006_GENERALIZED_CAPABILITY_SELECTION.md`, `docs/PREREQ-001_PRODUCT_DEFINITION.md`, `docs/ARCHITECTURE.md`, `docs/AI_BUILD_GOVERNANCE.md`
**Date issued:** 2026-09-09
**Outcome:** **Rejected** — `CODEX-PR023-01`, `-02`, `-03`; all three corrected

---

## 0. Note on ordering

**This prompt is committed before the review runs**, as §7.3 requires, in the
same commit as the work — as it was for PR-022.

## 1. Prompt issued

Recorded **before** the review was run.

```text
You are the independent review agent for the Radhanite repository, per
docs/AI_BUILD_GOVERNANCE.md §1.3.

Review pull request #23:
https://github.com/therealgulkorinaga/radhanite-ethonline/pull/23

This is the THIRD implementation step of TASK-006, authorized in PR #20. It
delivers ranking and deterministic tie-breaking only: choose one winner from
already-assessed eligible candidates, or STOP. It must not execute, consume,
advance a run, or change the eligibility rule.

Review against these authoritative documents ONLY:
  - tasks/TASK-006_GENERALIZED_CAPABILITY_SELECTION.md
  - docs/PREREQ-001_PRODUCT_DEFINITION.md
  - docs/ARCHITECTURE.md
  - docs/AI_BUILD_GOVERNANCE.md

Do NOT treat docs/pr_explanations/PR-023_TASK-006_EXPLANATION.md as evidence of
correctness (§4.3).

PART A — the ranking, implemented exactly

1. §2.4 states three levels: highest net_expected_value, then lower cost, then
   lexicographically smaller stable candidate ID. Confirm all three are
   implemented, in that order, and that none is skipped or reordered.
2. Confirm only eligible candidates compete, and that an ineligible candidate
   cannot win however large its computed net expected value.
3. Confirm the ranking does not recompute or alter eligibility.
4. §2.4 says the ranking is total and the result is independent of input order.
   Verify that claim holds for ALL cases, including a full tie, and that it
   follows from identifiers being unique rather than from luck.

PART B — the honesty of the test-first claim

5. §0 of the PR explanation discloses that the implementation was written
   BEFORE the test-first authorization arrived, that the ranking was then
   removed to observe genuine failures, and that the author had prior knowledge
   of a working design. Assess whether that disclosure is complete and accurate,
   or whether it understates the departure.
6. §10a records 33 failures across 18 test methods with the ranking removed.
   Verify that independently if you can, and assess whether the tests that
   still PASSED in that state are the right ones to have passed.

PART C — scope

7. Confirm the ranking does NOT: consume the selected candidate ID, increment
   the capability step count, execute anything, update task state, generate
   candidates, or orchestrate a run loop.
8. Confirm no dependency, credential, or configuration was added.
9. §2.1: confirm no provider, network, capability-type, or sponsor preference
   can influence selection. Assess whether the source-scanning test is
   meaningful or defeatable.
10. §2.5's other terminal condition — the success condition already being
    satisfied — must NOT be decided here. Confirm it is not, and that the module
    is not given the means to.

PART D — STOP and the safety distinction

11. Confirm STOP is returned when no candidate is eligible, including for an
    empty offer, and that it is an ordinary return rather than an exception.
12. §8 requires a safety stop to be distinguishable from an economic one.
    Assess whether `stopped_without_economic_judgement` is correct at the
    boundaries: all-safeguard, all-economic, mixed, and empty. Judge
    specifically whether an EMPTY offer should count as a safety stop — this
    implementation says it should not.

PART E — the record

13. §8 requires every candidate considered to be recorded, not only the winner,
    with its figures and why it failed. Confirm rejected candidates keep correct
    figures.
14. Confirm the decision-level inputs survive an empty offer, where there is no
    assessment to read them from.
15. Assess how `Selection.consumed_candidate_ids` is derived — it is taken from
    the first assessment. Is that sound, or should it be normalized
    independently of whether any candidate was offered?

PART F — tests

16. The PR claims 54 new tests and that eight deliberate faults were each
    caught. Verify the tests detect what they claim rather than passing
    vacuously.
17. §10b records that an earlier mutation run gave two FALSE "survived" results
    because of stale compiled bytecode, and that one test was rewritten and one
    vacuous assertion deleted as a result. Assess whether any OTHER test in this
    file has the same weakness — an assertion that would hold whatever the code
    does.
18. Verify exact-decimal semantics: no float anywhere, all arithmetic through
    Money and Probability. Assess the "tie that binary floating point would
    miss" test — does it actually establish that?
19. Verify the claimed counts independently: 346 existing tests unchanged, 400
    total, on Python 3.12.

FORMAT OF YOUR FINDINGS

Number every finding, per §3.1:

    CODEX-PR023-01
    CODEX-PR023-02
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

**The reviewer's verbatim response was not supplied** to the agent writing this
record. What follows is the three findings **as relayed by the human product
owner** in the correction authorization. Nothing has been invented to fill the
gap. §0 is unaffected: the prompt in §1 was committed before the review ran.

The prompt's Part A asked whether the ranking comparison itself was correct. The
product owner relayed that it was validated as correct and must be preserved
unchanged — so all three findings concern the **boundary and the record**, not
the rule.

### `CODEX-PR023-01` — the ranking layer computed its own eligibility

**File:** `radhanite/selection.py` — `select_capability`
**Departs from:** the PR-C boundary; TASK-006 §2.4, §2.7

`select_capability` accepted raw `Candidate` objects and called
`eligibility.assess` internally. Ranking is meant to consume assessments the
eligibility rule has already produced; owning both decisions lets the ranking
layer disagree with the record its caller already holds.

**Required correction:** consume an ordered collection of already-computed
`Assessment` objects; never call `assess`; never recompute eligibility; only
eligible assessments may compete; ineligible ones remain available for STOP and
audit reasoning but may never win; validate candidate-ID uniqueness from the
supplied assessments without re-running eligibility; mutate neither the supplied
assessments nor their candidates; stay free of provider, network, payment and
sponsor concepts.

### `CODEX-PR023-02` — consumed identifiers were lost on an empty offer

**File:** `radhanite/selection.py` — `select_capability`
**Departs from:** TASK-006 §2.7, §8

The consumed set was read off the first assessment. With no assessments there
was nothing to read, so a STOP on an empty offer reported `()` even when the run
had already bought several capabilities. Consumed identifiers are **run state**,
not a property of the current offer.

**Required correction:** normalize them independently of the assessment
collection; preserve them when zero assessments are supplied; never infer them
from the offer; never clear them because the offer is empty; keep the
representation deterministic; detach the stored value from caller mutation.

### `CODEX-PR023-03` — the step ceiling lost precedence to economics

**File:** `radhanite/selection.py` — `Selection.stopped_without_economic_judgement`, `_explain`
**Departs from:** TASK-006 §2.5 C, §8

When the ceiling had been reached **and** candidates also failed economic
conditions, the STOP was classified and described as economic. The run was
already forbidden from taking another capability step before any candidate was
weighed, so no economic verdict ended it.

**Required correction:** a ceiling STOP is non-economic;
`stopped_without_economic_judgement` must say so; the reason must not claim
nothing was worth buying; per-candidate economic failures remain recorded as
assessment facts but must not override the run-level ceiling reason; the
per-candidate eligibility rule itself is unchanged.

## 3. Outcome

**Rejected** — `CODEX-PR023-01`, `-02`, `-03`.

`-01` is a boundary crossing, which under §7.2 is a rejection rather than a
correction: *"the work departs from the specification or crosses an architecture
boundary. It is fixed or removed; it is not merged with a note."*

The ranking comparison in §2.4 was **not** faulted and is preserved byte-for-byte.

## 4. Corrections

| Finding | Correction |
|---|---|
| `CODEX-PR023-01` | `select_capability` now takes `assessments`, never `candidates`. `assess` is neither imported nor called — a test patches it to raise and requires selection to work regardless. `_checked_assessments` reads uniqueness off the supplied assessments. A new integrity check refuses assessments computed against a different task state, which the refactor would otherwise have allowed to pass silently |
| `CODEX-PR023-02` | Consumed identifiers are normalized from the argument, independently of the offer, and survive an empty one |
| `CODEX-PR023-03` | `Selection.ceiling_reached` added; `stopped_without_economic_judgement` returns True whenever the ceiling is reached; `_explain` checks the ceiling **before** anything about the candidates, and says so |

Committed as *"Correct the PR-23 ranking boundary and stop classification"* on
`task-006-selection`.

**Test-first, genuinely this time.** The regression tests were written and run
before any correction existed: **90 failures across 70 test methods**, all
rooted in `select_capability() got an unexpected keyword argument
'assessments'`. Then implemented, then re-run green. Eight mutations, all
caught, with bytecode writing disabled.

**Corrections are themselves subject to review** (`AI_BUILD_GOVERNANCE.md`
§7.5). This corrective commit has not been reviewed.
