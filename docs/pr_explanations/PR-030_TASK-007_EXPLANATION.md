# PR-030 — What a run carries, before anything runs

**Pull request:** #30
**Authorized task:** TASK-007 §3, PR A
**Author:** Claude Code, under human product owner authorization

---

## 1. Purpose of this PR

The state a capability run carries — and **nothing that changes it.**

No execution, no loop, no transitions, no terminal classification, no
acquisition call, no task-state reasoning. Those are later steps, and a state
model that quietly did any of them would be the loop wearing a different name.

## 2. What changed

| File | |
|---|---|
| `radhanite/runstate.py` | **New.** The §3 state model |
| `tests/test_runstate.py` | **New.** 46 tests |
| `radhanite/__init__.py` | Exports |
| `tasks/TASK-007_CAPABILITY_RUN_LOOP.md` | §3.4 what PR A delivered; **§3.5 an ambiguity it leaves open** |
| `docs/reviews/PR-030_...`, `docs/pr_explanations/PR-030_...`, `docs/reviews/README.md` | Review prompt, this document, index row |

**No dependency.** The project still has none.

## 3. Why the change was needed

The loop cannot be written until there is something for it to carry forward.
Doing the state first means the accounting, the opacity boundary and the
non-recursion can each be settled and tested on their own, rather than argued
about while execution is being wired.

## 4. How this worked before

Nothing existed. `run.py` is TASK-001's two-tier loop and carries none of this.

## 5. How it works after

### The ledger includes what was spent before the loop started

`initial_budget` is the **original run budget**, not a capability allowance. A
run may enter with less remaining because earlier work spent money, so
`total_spend` is **derived**:

```
total_spend = initial_budget - remaining_budget
```

A caller cannot state a spend that disagrees with the budget it also states —
there is no parameter for it.

**Both ends are bounded**, because the identity alone is not enough.
`remaining_budget > initial_budget` satisfies `spend + remaining == initial`
while producing a **negative** spend, which is not a coherent ledger. Refused,
along with negative amounts on either side.

### `task_state` is opaque, and that settles how it is stored

TASK-007 stores it and passes it, and **never reads inside it**. So it is held
**by reference** — copying or freezing an arbitrary object means inspecting it,
and deep-copying one would break perfectly reasonable states that cannot be
copied.

A test proves the prohibition rather than asserting it: it passes in an object
that raises on `__getattr__`, `__len__`, `__iter__`, `__eq__` and `__hash__`,
then takes a snapshot. Any inspection at all fails the test.

**The consequence is stated, not buried.** A caller who mutates that object
changes what every snapshot appears to have recorded. See §12.

### Snapshots cannot contain history

`RunSnapshot` carries every §3 field **except `history`**. That is the
non-recursion §3.3 requires, and it is what `CODEX-PR027-02` caught in the
specification: an entry containing the whole post-transition state, which
contains the history, cannot be constructed at all.

Three structural tests: the snapshot's field set is asserted exactly, no field
name contains "history" or "transition", and walking every snapshot field finds
nothing that leads back to a `RunState` or a `TransitionRecord`.

### What is modelled but not decided

`RunStatus` carries `RUNNING` and §6's four terminal values, because the state
has to be able to *hold* one. **Choosing which applies is not this step.** A
zero-step policy is valid state here and classifies nothing — §6.1's precedence
and §6.2's classification arrive with the loop.

`TransitionRecord` exists so `history` has a member type. Its `execution` field
is deliberately untyped: the execution result belongs to a later step, and
inventing its shape now would be an abstraction justified only by future work.

## 6. What goes into the system

A task value, an initial and remaining budget, a `RunPolicy`, an opaque task
state, a current success probability, and optionally identifiers already
consumed and a step count already reached.

## 7. What the system decides

**Nothing.** It validates, derives the ledger, normalizes identifiers, and
holds. Tests assert the module exports nothing named for executing, selecting,
acquiring or classifying, and that `RunState` has no transition methods.

## 8. What comes out

A `RunState`, and `.snapshot()` for a transition record to hold later.

## 9. How it can fail

Every failure is a refusal at initialization: money that is not `Money`, a
probability that is not a `Probability`, a policy that is not a `RunPolicy`, a
remaining budget that is negative or exceeds the initial one, a negative or
non-integer step count, `True` as a count, a bare string of consumed
identifiers, or non-string members.

## 10. Tests run and their results

**Before** — written first, run against `main`:

```
ImportError: cannot import name 'runstate' from 'radhanite'
Ran 528 tests — FAILED (errors=1)
```

An import failure proves *absence*. The mutations establish the rest.

**After:**

```
$ python3.12 -m unittest discover -q
Ran 573 tests in 0.14s
OK
```

**527 existing, unchanged, plus 46 new.**

### Deliberate faults, all caught

Bytecode writing disabled throughout.

| Fault introduced | Result |
|---|---|
| `total_spend` zero despite baseline spend | **4 failures** |
| Allow `remaining_budget > initial_budget` | **1 failure** |
| Allow a negative step count | **1 failure** |
| Accept `True` as a step count | **1 failure** |
| Retain the caller's mutable consumed-ID collection | **4 failures** |
| Put `history` inside the snapshot | **4 failures** |
| Omit consumed IDs from the snapshot | **1 failure** |

## 11. Assumptions made

- **Consumed identifiers normalize sorted and de-duplicated**, matching
  `eligibility`. The specification does not state it; consistency with the layer
  that consumes them does.
- **A run may begin part-way through** — with spend already made, identifiers
  already consumed, and steps already taken. §3.2 requires the first; the others
  follow from the same reasoning.

## 12. Known limitations

- **`task_state` mutability is a real gap, and it is the specification's.**
  §3.1 requires opacity, which entails storing by reference, which means a
  caller mutating that object changes what every snapshot appears to have
  recorded. The obligation is documented on the caller. Whether the spec should
  instead *require* immutable task state — and how it would check that without
  inspecting — is recorded as open in TASK-007 §3.5.
- **`TransitionRecord.execution` is untyped**, pending the execution step.
- **Nothing constructs a `TransitionRecord`.** `history` is always empty until
  the loop exists.
- **No terminal classification.** A run at its ceiling reports `RUNNING`,
  because deciding otherwise is §6's job.

## 13. Explicitly out of scope

Execution, the executor interface, execution results, committed-cost
transitions, candidate consumption, step increments, task-state updates,
acquisition and catalogue calls, eligibility, ranking, selection, terminal
classification, retry, run-loop orchestration, and every integration.

**TASK-006 and TASK-008 are unchanged** — verified: every existing module is
byte-identical to `main` apart from `__init__.py`'s exports.

## 14. Deferred to future tasks

The rest of TASK-007, and the §3.5 ambiguity.

## 15. How to explain this to a judge

> Before a run can do anything, it has to know what it is carrying: the budget,
> what has been spent, what it has already bought, how many purchases it has
> made. This is that, and deliberately only that — it cannot buy anything or
> decide anything.
>
> Two details are worth the time. The spend figure includes money spent *before*
> the loop started, because a budget that forgets earlier spending is not a
> budget. And the run carries a blob of task-specific state it is forbidden from
> looking inside — there is a test that hands it an object which screams if
> anything reads it.
>
> The third is a thing we wrote down rather than solved: because we cannot look
> inside that blob, we cannot copy it, so if the caller changes it later our
> audit record silently changes too. That is in the specification as an open
> question, not hidden in a comment.
