# Codex review — PR-017

**Pull request:** [#17](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/17) — redefine Radhanite from inference allocation to dynamic capability acquisition
**Reviewer:** Codex (independent review agent, `AI_BUILD_GOVERNANCE.md` §1.3)
**Date issued:** 2026-09-09
**Outcome:** **Approved with corrections** — `CODEX-PR017-01`, `-02`, `-03`

---

## 0. Governance disclosure — read this first

> **The PR-017 review prompt was recorded after the review had already run. This
> does not satisfy the normal pre-review prompt-ordering requirement in
> `AI_BUILD_GOVERNANCE.md` §7.3. The record is being committed retrospectively
> for audit completeness, not to claim procedural compliance.**

§7.3 requires the prompt to be committed **before** the review is run, for a
stated reason: *"A prompt recorded afterwards can be quietly reshaped to fit the
answer it received."* That protection was not in place for this review. Nothing
in this record should be read as evidence that it was.

**A second, separate limitation.** The implementing agent did not receive the
reviewer's verbatim prompt or verbatim response. What is recorded in §1 and §2
below is the review **as relayed by the human product owner** in the correction
authorization. §7.3 requires findings *"never summarized, softened, or
deleted"*, and a relayed account cannot be certified against that standard.

Neither gap has been papered over, and no text has been invented to fill either.
Where verbatim material is absent, this record says so rather than supplying a
plausible substitute. If the verbatim prompt and response are available, they
should replace §1 and §2 and this paragraph should be struck.

## 1. Prompt issued

**Not available verbatim.** Not committed before the review, per §0.

The review was run by the human product owner against PR #17 as an independent
Codex review, in the role defined by `AI_BUILD_GOVERNANCE.md` §1.3, and against
the authoritative documents named in §4.3 — `PREREQ-001`, `ARCHITECTURE.md`,
`AI_BUILD_GOVERNANCE.md` and `TASK-001`. The exact wording is not in the
implementing agent's possession and is deliberately **not** reconstructed here.

## 2. Findings returned

**As relayed by the human product owner, not verbatim.** Per §0.

### `CODEX-PR017-01` — the demonstration's success condition is not machine-checkable

**File:** `docs/PREREQ-001_PRODUCT_DEFINITION.md` §6
**Departs from:** `PREREQ-001` §4.5

The supplier-diligence demonstration declared its success condition as *"a
defensible `APPROVE` / `ESCALATE` / `REJECT`."*

Defensibility is a human judgement. §4.5 requires a success condition that is
*"objective, machine-checkable"* and *"evaluable without human judgment"*, and
states that a task whose success cannot be measured **is not a Radhanite task**.
The demonstration therefore contradicted the input contract the same document
sets.

The recommendation is the **output**. It was being used as the success
condition, and those are different things.

### `CODEX-PR017-02` — two V1 framings, with contradictory status

**Files:** `docs/PREREQ-001_PRODUCT_DEFINITION.md` §2.1, §6, §6.4; `tasks/BACKLOG.md`
**Departs from:** internal consistency; `BACKLOG.md` rule 1

The document carried two use cases without stating the status of each:

- the software-engineering V1 that `TASK-001` was built under, and
- the newly frozen supplier-diligence demonstration.

§2.1 still read *"Only the V1 use case in §6 is being built"* — and §6 was now
the supplier demonstration. Read literally, that sentence asserted that supplier
diligence **was being built**, which is false and would also imply `BL-11` had
been authorized.

### `CODEX-PR017-03` — no review record exists for PR-017

**File:** `docs/reviews/` — absent
**Departs from:** `AI_BUILD_GOVERNANCE.md` §7.3, §7.4

PR #17 was opened with no `docs/reviews/PR-017_CODEX_REVIEW.md` and no row in
`docs/reviews/README.md`. §7.3 requires every review to be recorded — prompt and
findings both — and §7.4 requires the record, the index row, and the pull
request's own claims to land as **one action**.

The implementing agent's stated reason at the time was that committing a prompt
for a review that might never run would repeat the stale-`pending` problem then
outstanding on PR-016. That reasoning does not survive a review actually having
happened: once it ran, the absence of a record is a §7.3 failure regardless of
what motivated it.

## 3. Outcome

**Approved with corrections.** Three findings, all P0, all in scope for a single
corrective commit on the PR-017 branch. No finding disputed.

The pivot itself was not challenged: the separation of implemented architecture
from migration direction, the preservation of `TASK-001` unrewritten, and the
new boundary violations were accepted as recorded.

## 4. Corrections

| Finding | Correction | Where |
|---|---|---|
| `CODEX-PR017-01` | Output separated from success condition; a six-clause deterministic completion contract added, checked by field and state rather than by judgement. Confidence explicitly restated as a declared fixture | `PREREQ-001` §6, **new §6.5**; `README.md` |
| `CODEX-PR017-02` | §2.1's "only the V1 use case in §6 is being built" replaced; **new §6.6** tabulates both framings with the status of each; `BL-11` note rewritten to state it is neither retired nor completed and remains unauthorized | `PREREQ-001` §2.1, **§6.6**; `BACKLOG.md`; `README.md` |
| `CODEX-PR017-03` | This record, its index row, and the disclosure in §0 | `docs/reviews/PR-017_CODEX_REVIEW.md`; `docs/reviews/README.md` |

Committed as *"Correct PR-17 demo success criteria and governance record"* on
`docs-product-pivot-skill-acquisition`.

**Corrections are themselves subject to review** (`AI_BUILD_GOVERNANCE.md`
§7.5). This corrective commit has not been reviewed.
