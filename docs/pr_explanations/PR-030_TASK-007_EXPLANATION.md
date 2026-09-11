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
| `tests/test_runstate.py` | **New.** 102 tests |
| `radhanite/__init__.py` | Exports |
| `tasks/TASK-007_CAPABILITY_RUN_LOOP.md` | §3.1.1 opacity is not aliasing; §3.4 what PR A delivered; **§3.5 a retraction** |
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

### Every construction is validated — `CODEX-PR030-01`

The first revision of this PR put the invariants in `begin_run()` while
exporting a `RunState` anyone could construct directly, bypassing every one of
them. **One safe path and one unsafe path is one unsafe path.**

The invariants now live in `__post_init__`, shared by all three public records
through a single `_normalise` implementation:

| Enforced | |
|---|---|
| Types | `Money` ×4, `RunPolicy`, `Probability`, `RunStatus` |
| Bounds | `0 <= remaining_budget <= initial_budget`, `0 <= total_spend <= initial_budget` |
| Identity | `total_spend + remaining_budget == initial_budget` |
| Step count | `int`, not `bool`, not negative |
| Consumed IDs | sorted, de-duplicated, detached, frozen to a tuple |
| History | detached, frozen to a tuple, every member a `TransitionRecord` |
| Opaque state | frozen — below |

`begin_run()` keeps exactly one job: deriving `total_spend` from the two
budgets, so a caller cannot state a spend that contradicts the budget it also
states. It is the *convenient* entrance, no longer the *safe* one, because
`RunState(...)` is now equally safe.

`RunSnapshot` validates identically — the correction explicitly required that
neither a run **nor a snapshot** expose a live alias, and the snapshot is the
record an auditor actually reads. `TransitionRecord` checks that `before` and
`after` are snapshots and `selection` is a `Selection`: a transition holding a
`RunState` would put a history inside a history, which is the recursion §3.3
exists to prevent.

### `TransitionRecord.execution` is reserved, and must be `None`

The first correction typed `before`, `after` and `selection` and left
`execution: Any = None` accepting anything. That was the last live alias in the
module, and it reopened through a field everything the type checks had just
closed: a mutable payload is a caller-owned object sitting inside an audit
record, and a `RunState` payload puts a history inside a history.

**PR A refuses any non-`None` payload**, immutable ones included. That is not
excessive strictness — it is the absence of a decision. PR A implements no
execution, no caller has a result to pass, and **the authorized execution result
type is introduced in PR B**. Freezing an arbitrary payload instead would be
PR B's schema arriving early under a different name, which `ARCHITECTURE.md` §6
item 7 forbids. The field stays so the shape of a transition is settled.

### `task_state` is opaque, and opacity is not aliasing — `CODEX-PR030-02`

The first revision stored `task_state` **by reference**, and argued §3.1
entailed it: copying or freezing an arbitrary object means inspecting it, and
this task must not inspect. **That argument was wrong on both halves.**

- Freezing reads *shape* — mapping, sequence, set — and never meaning. No key,
  value or field is interpreted, so opacity gives up nothing.
- A live reference lets a caller rewrite what an already-written audit record
  appears to say, and lets them insert a back-reference that makes the record
  recursive after the fact — defeating §3.3 from outside this module.

So opaque state is **frozen structurally on the way in**, matched on **exact
type** throughout:

| Input | Stored as |
|---|---|
| `None`, `bool`, `int`, `float`, `complex`, `str`, `bytes`, `Decimal` | unchanged |
| `Money`, `Probability`, `RunPolicy` | unchanged — this repository's own frozen values |
| `dict`, `mappingproxy` | read-only mapping over a **fresh** dict, members frozen |
| `list`, `tuple` | tuple, members frozen |
| `set`, `frozenset` | frozenset, members frozen |
| a cycle | **`ValueError`** — refused deterministically, never recursed into |
| **anything else, subclasses of the above included** | **`TypeError`** — refused, never aliased |

**Exact type, not `isinstance`.** The first correction used `isinstance`, which
trusts subclasses — and a subclass of an immutable scalar is not immutable:

```python
class Smuggler(int):
    def __init__(self, *_):
        self.baggage = []        # the caller keeps this
```

`Smuggler(1)` satisfies `isinstance(x, int)` and was stored unchanged, list and
all, through a check that looked airtight. The same holds one level up for
`Enum`: a member's `value` can be a list, and every member has an instance
dictionary things can be attached to — so **no `Enum` is blanket-accepted**,
this module's own included. Narrowing that to specific authorized Enum types is
a decision, and not PR A's to make.

Exact matching closes a quieter hole too. A `str` subclass **is** a `Sequence`,
so the `isinstance` rule converted `"abc"` into `("a", "b", "c")` and recorded
that as the caller's state — silent corruption rather than a refusal.

Immutable containers are rebuilt rather than passed through for the same
reason: a `mappingproxy` can wrap a dict the caller still holds, and a `tuple`
or `frozenset` subclass can carry mutable attributes.

Refusal is still decided from the object's **type**, so the test proving nothing
inspects the state holds — an object raising on `__getattr__`, `__len__`,
`__iter__`, `__eq__` and `__hash__` is refused without any of those being
called. No float is introduced and nothing is serialized: freezing rebuilds
containers and passes values through untouched, so `Decimal` stays `Decimal`.

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
identifiers, non-string members, a ledger that does not add up, a status that
is not a `RunStatus`, a history member that is not a `TransitionRecord`, a
cyclic opaque state, or an opaque state that cannot be frozen.

**Every one of these is refused on direct construction too**, not only through
`begin_run()`.

## 10. Tests run and their results

**Before the module existed** — written first, run against `main`:

```
ImportError: cannot import name 'runstate' from 'radhanite'
Ran 528 tests — FAILED (errors=1)
```

An import failure proves *absence*. The mutations establish the rest.

**Before the first corrections** — 29 regression tests written first and run
against the rejected implementation:

```
$ PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest tests.test_runstate -q
Ran 75 tests in 0.009s
FAILED (failures=25)
```

**Before the final corrections** — 27 further regression tests, run against the
first-correction implementation:

```
$ PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest tests.test_runstate -q
Ran 102 tests in 0.014s
FAILED (failures=14)
```

Seven in `ExecutionPlaceholderTests`, six in `ExactTypeFreezeTests`, and one in
`TransitiveImmutabilityAuditTests` — the one that ties the structural walk to
the constructor. Nothing outside the new classes regressed in either round,
which is what shows the corrections are additive rather than a redesign.

**After:**

```
$ python3.12 -m unittest discover -q
Ran 629 tests in 0.15s
OK
```

**527 existing, unchanged, plus 102 new.**

### Deliberate faults, all caught

Bytecode writing disabled throughout, `__pycache__` cleared between runs.

The seven the correction authorization required, plus two covering the records
the correction extended to:

| Fault introduced | Failures |
|---|---|
| Bypass constructor invariant validation entirely | **26** |
| Retain the caller's mutable consumed-ID input | **5** |
| Retain the caller's mutable history input | **1** |
| Retain `task_state` by reference | **12** |
| Allow recursive/cyclic opaque state | **1** |
| Allow a `total_spend` inconsistent with the budgets | **2** |
| Allow an invalid `RunStatus` | **1** |
| Bypass `RunSnapshot` validation | **2** |
| Let a transition hold a `RunState` where a snapshot belongs | **1** |
| Allow a non-`None` mutable `execution` payload | **7** |
| Allow a `RunState` as `execution` | **2** |
| Revert exact-type atom matching to `isinstance` | **5** |
| Accept arbitrary `Enum` members | **3** |
| Accept a scalar subclass carrying a mutable payload | **4** |

**14/14 killed**, all nine earlier faults re-run against the final code. Two of
them took a second pass to earn:

- *Allow inconsistent total spend* **survived** the first run. The unbalanced
  ledger cases already present were caught by the `total_spend <=
  initial_budget` bound, so the identity check itself was untested. A case where
  both bounds hold and only the identity fails — $250 budget, $100 remaining,
  $50 spent — now covers it.
- *Let a transition hold a run* **survived** because the test that was meant to
  catch it passed a non-`Selection` object, so it was raising for the wrong
  reason. A real `Selection` is constructed now, leaving the field under test as
  the only thing wrong.

The earlier faults from the first revision were re-run and still fail: baseline
spend zeroed (**4**), `remaining_budget > initial_budget` allowed (**1**),
negative step count (**1**), `True` as a step count (**1**), `history` inside
the snapshot (**4**), consumed IDs omitted from the snapshot (**1**).

## 11. Assumptions made

- **Consumed identifiers normalize sorted and de-duplicated**, matching
  `eligibility`. The specification does not state it; consistency with the layer
  that consumes them does.
- **A run may begin part-way through** — with spend already made, identifiers
  already consumed, and steps already taken. §3.2 requires the first; the others
  follow from the same reasoning.

## 12. Known limitations

- **`task_state` now has a narrower contract than "anything at all".** Only
  exactly immutable values and ordinary containers of them are accepted; an
  arbitrary mutable object, and any subclass of an accepted type, is refused.
  That is a real constraint on callers, and it lands on a producer that does not
  exist yet — the task-state updater (§5.3, §10) must be designed to return
  immutable state. Recorded in TASK-007 §3.1.1 so it is a known constraint
  rather than a surprise.
- **No `Enum` may appear in `task_state`**, including this module's own
  `RunStatus`. Blanket-accepting `Enum` is unsafe and narrowing it to specific
  authorized types is a decision PR A should not make alone. If a later task
  needs one, it can authorize that exact type.
- **Freezing rebuilds containers on every snapshot.** A snapshot holds a frozen
  equivalent of the run's state, equal to it but not the same object. Auditors
  compare by value, so this costs nothing but is worth knowing.
- **`TransitionRecord.execution` must be `None`.** It is a reserved
  placeholder; the authorized execution result type arrives with PR B. Nothing
  in PR A can populate it, so nothing in PR A is blocked by this.
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

The rest of TASK-007. **The §3.5 "ambiguity" is not deferred — it is
retracted**: it was a wrong conclusion, not an open product question, and
`CODEX-PR030-02` resolved it against the reasoning this PR originally recorded.

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
