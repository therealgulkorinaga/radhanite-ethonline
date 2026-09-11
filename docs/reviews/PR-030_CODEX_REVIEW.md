# Codex review — PR-030

**Pull request:** [#30](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/30) — TASK-007 PR A: run state and immutable snapshots
**Reviewer:** Codex (independent review agent, `AI_BUILD_GOVERNANCE.md` §1.3)
**Reviewed against:** `tasks/TASK-007_CAPABILITY_RUN_LOOP.md`, `tasks/TASK-006_GENERALIZED_CAPABILITY_SELECTION.md`, `docs/ARCHITECTURE.md`, `docs/AI_BUILD_GOVERNANCE.md`
**Date issued:** 2026-09-11
**Outcome:** **Rejected** — 2 findings, both corrected (`CODEX-PR030-01`, `CODEX-PR030-02`)

---

## 0. Note on ordering

**This prompt is committed before the review runs**, as §7.3 requires, in the
same commit as the work.

## 1. Prompt issued

Recorded **before** the review was run.

```text
You are the independent review agent for the Radhanite repository, per
docs/AI_BUILD_GOVERNANCE.md §1.3.

Review pull request #30:
https://github.com/therealgulkorinaga/radhanite-ethonline/pull/30

This is TASK-007 PR A: the §3 run-state model only. No execution, no loop, no
transitions, no terminal classification, no acquisition call, no task-state
reasoning.

Review against these authoritative documents ONLY:
  - tasks/TASK-007_CAPABILITY_RUN_LOOP.md
  - tasks/TASK-006_GENERALIZED_CAPABILITY_SELECTION.md
  - docs/ARCHITECTURE.md
  - docs/AI_BUILD_GOVERNANCE.md

Do NOT treat docs/pr_explanations/PR-030_TASK-007_EXPLANATION.md as evidence of
correctness (§4.3).

PART A — the state model against §3

1. §3's table lists eleven fields. Confirm RunState has exactly those, no more
   and no fewer, and that none is provider-specific.
2. Confirm RunSnapshot carries every §3 field EXCEPT history — §3.3.
3. Confirm max_capability_steps is read from the policy rather than duplicated
   as its own field, and judge whether that is right.
4. Assess whether anything modelled here belongs to a later PR: an execution
   result, a committed cost, a retry counter, a terminal decision.

PART B — non-recursion

5. §3.3 requires that nothing contains itself transitively. Verify a snapshot
   cannot reach a history, a RunState, or another snapshot.
6. The PR claims three structural tests prove this. Assess whether they would
   actually catch a future field that reintroduced recursion, or whether they
   are name-based and defeatable.
7. TransitionRecord exists but nothing constructs one. Is defining it now
   correct, or is it an abstraction ahead of its use (ARCHITECTURE §6 item 7)?

PART C — accounting

8. Verify total_spend is DERIVED and cannot be supplied.
9. Verify §3.2.1's bounds are enforced at initialization: 0 <= remaining_budget
   <= initial_budget, 0 <= total_spend <= initial_budget, and the identity.
10. Confirm baseline/pre-loop spend initialises correctly and is not assumed
    away, per §3.2.
11. Confirm exact Money throughout, no float anywhere.

PART D — the opaque task state, and the ambiguity claimed

12. §3.1 says TASK-007 stores and passes task_state and never reads inside it.
    Confirm nothing in this PR inspects it — no attribute access, no len, no
    iteration, no equality, no hashing, no copying.
13. The implementation stores it BY REFERENCE and argues that §3.1 entails this,
    since copying or freezing requires inspection. Judge whether that reasoning
    is sound or whether the implementation has decided something the spec left
    open.
14. TASK-007 §3.5 now records an ambiguity: the spec does not say what happens
    when a caller mutates task_state after a snapshot. Assess whether recording
    it was correct, or whether the implementation should have stopped instead.
15. Assess the "Explodes" test that proves nothing inspects task_state. Is it
    comprehensive, or are there inspection routes it does not cover?

PART E — validation

16. Confirm bool is refused for the step count, negative counts refused,
    non-integers refused.
17. Confirm consumed identifiers are sorted, de-duplicated, detached from
    caller-owned input, and refuse a bare string and non-string members.
18. §3 does not state the normalization rule for consumed identifiers. The
    implementation matched eligibility's. Judge whether that is consistency or
    an invented rule.
19. Confirm RunStatus holds §6's terminal values WITHOUT classifying: a run at
    its ceiling, or with a zero-step policy, must still report RUNNING.

PART F — scope and regressions

20. Confirm nothing executes, selects, acquires, classifies, advances a counter,
    consumes a candidate, or updates task state. Check for transition methods on
    RunState.
21. Confirm TASK-006 and TASK-008 behaviour is unchanged and that every existing
    module is byte-identical to main apart from __init__.py's exports.
22. Confirm no dependency was added.
23. Verify the claimed counts: 527 existing tests unchanged, 573 total, on
    Python 3.12, and that the seven mutation results are reproducible.

FORMAT OF YOUR FINDINGS

Number every finding, per §3.1:

    CODEX-PR030-01
    CODEX-PR030-02
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

> **Disclosure — these findings are recorded as relayed by the human product
> owner in the correction authorization, not transcribed verbatim from Codex's
> response.** The identifiers, the defects and the required remedies are
> Codex's; the wording below is the product owner's restatement of them. No
> verbatim Codex text was available to this record.

### `CODEX-PR030-01` — one safe construction path and one unsafe one

`radhanite/runstate.py`. `RunState` is publicly exported and directly
constructible, but the invariants live only in `begin_run()`. Direct
construction therefore bypasses:

- the accounting bounds,
- the ledger identity `total_spend + remaining_budget == initial_budget`,
- step-count validation,
- consumed-ID immutability,
- history immutability,
- valid-status constraints.

**Required:** every valid public construction path enforces the same
invariants, through the same implementation.

> "Do not keep one safe `begin_run()` path and one unsafe direct-construction
> path."

**Departs from:** TASK-007 §4 invariants 1, 2, 7, 13 — which are stated as
properties of the *state*, not of one factory function.

### `CODEX-PR030-02` — opaque `task_state` retained as a mutable alias

`radhanite/runstate.py`. Storing `task_state` by reference violates
auditability: mutating the original object changes previously created states and
snapshots, and a caller can insert a back-reference into it and make the audit
structure recursively self-containing.

> "Opacity means TASK-007 must not interpret domain/business meaning. It does
> not mean TASK-007 may retain mutable aliases."

**This refutes the reasoning PR-030 recorded in TASK-007 §3.5**, which treated
storage-by-reference as entailed by opacity and the rest as an open product
question. It was neither entailed nor open.

**Required:** one enforced, generic immutable boundary for `task_state`, such
that neither a `RunState` nor a `RunSnapshot` exposes a live mutable alias, a
previously created record stays historically stable, a caller cannot create a
recursive back-reference into an existing record, and TASK-007 still interprets
no domain meaning.

**Departs from:** TASK-007 §3.3 and §4 invariant 13 — a non-recursive history
from which every transition is reconstructable.

### Additional requirement — snapshot non-recursion tests

The existing structural tests relied on field names and immediate field types.
A recursive structural walk was required, proving no `RunState`, `RunSnapshot`,
`TransitionRecord` or self-reference is reachable from stored state — and it had
to **fail** against the by-reference implementation.

## 3. Outcome

**Rejected.**

Departed from TASK-007 §3.3, §4 invariant 13, and the §4 invariants generally,
which constrain the state rather than one construction function.

## 4. Corrections

Authorized by the human product owner, scope limited strictly to the two
findings. Implemented on the same branch and pushed to the same pull request;
**§7.5 — the corrections are themselves subject to review.**

Corrected in **three rounds**. Each round closed the findings at the level they
were raised; the product owner then identified that they remained open one level
further down, and authorized the next. The pattern is worth naming: each round
fixed a *rule*, and the round after found the rule being applied through a check
that trusted subclasses.

### Round 1 — `ce17ec3`

| Finding | Resolution |
|---|---|
| `CODEX-PR030-01` | Invariants moved into `__post_init__` on `RunState`, `RunSnapshot` and `TransitionRecord`, through one shared `_normalise` implementation. `begin_run()` retains only the derivation of `total_spend` and delegates everything else |
| `CODEX-PR030-02` | `task_state` is frozen structurally at construction: immutable values pass through, mappings/sequences/sets become immutable equivalents, cycles are refused with `ValueError`, and anything unfreezable is refused with `TypeError` rather than aliased |

### Round 2 — the same two findings, one level down

| Finding | What round 1 left open | Resolution |
|---|---|---|
| `CODEX-PR030-01` | `TransitionRecord.execution` still accepted **anything**, reopening through a field what the type checks had just closed: a mutable payload is a caller-owned object inside an audit record, and a `RunState` payload puts a history inside a history | **`execution` must be `None` in PR A.** A reserved placeholder; the authorized execution result type arrives with PR B. Refusing outright is smaller and less speculative than inventing a schema to freeze |
| `CODEX-PR030-02` | Atoms were matched with `isinstance`, which trusts subclasses — `class Smuggler(int)` carrying a list passed the check and was stored by reference, list and all. `Enum` was blanket-accepted, and a member's `value` can be mutable. A `str` subclass is a `Sequence`, so `"abc"` was silently recorded as `("a", "b", "c")` | **Exact-type matching throughout.** Only exact `None`/`bool`/`int`/`float`/`complex`/`str`/`bytes`/`Decimal`/`Money`/`Probability`/`RunPolicy` pass through; `dict`/`mappingproxy`, `list`/`tuple`, `set`/`frozenset` are rebuilt immutable; **no `Enum` is accepted**; everything else, subclasses included, is refused |

### Round 3 — `CODEX-PR030-01`, one level further down

Round 2 applied exact-type matching to opaque `task_state` and left the audit
records themselves on `isinstance`. A frozen record's subclass is not immutable:

```python
@dataclass(frozen=True)
class _TransitionWithBaggage(TransitionRecord):
    baggage: list = field(default_factory=list)   # frozen reference, live list
```

Accepted as a history member, that list is caller-owned mutable state inside an
audit record. Separately, `isinstance(x, str)` accepted a `str` subclass as a
consumed candidate identifier, and a `str` subclass is a perfectly good place to
keep one.

| Resolution | |
|---|---|
| Matched exactly | `Money`, `Probability`, `RunPolicy`, `RunStatus`, `RunSnapshot`, `TransitionRecord`, `Selection`, `str` identifiers, `int` step counts — through one shared `_exactly()` helper |
| Left as `isinstance` | **the input containers only** — a `history` sequence or `consumed_candidate_ids` collection is read once and rebuilt as a tuple, never retained, so a subclass of it changes nothing |
| Subclasses | **refused, not inspected.** Deciding which are safe would mean walking their fields at construction, and would still be wrong the moment one grew a field |

Matching `int` exactly subsumes the old `bool` special case: `True` is an `int`
by inheritance, so it is now excluded by the general rule rather than a clause
of its own.

Also corrected: TASK-007 §3.5's claimed ambiguity is **retracted** and replaced
with §3.1.1, "Opacity is not aliasing". The one question that genuinely remains
open is narrower — the task that will *produce* `task_state` does not exist yet
and must produce immutable state.

**Verification:** 79 regression tests written first across the three rounds —
failing 25/75 against the rejected implementation, 14/102 against round 1, and
9/125 against round 2. **652 tests pass after.** 18 deliberate faults introduced
one at a time, **all 18 caught**. Two survived a first pass and are recorded,
with the test weaknesses they exposed, in
`docs/pr_explanations/PR-030_TASK-007_EXPLANATION.md` §10.
