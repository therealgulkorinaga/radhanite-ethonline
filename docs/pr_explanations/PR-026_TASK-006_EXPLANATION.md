# PR-026 — Closing out TASK-006, and finding it cannot close

**Pull request:** #26
**Authorized task:** TASK-006 §5 deliverables 4, 5 and 6
**Author:** Claude Code, under human product owner authorization

---

## 1. Purpose of this PR

To finish the three outstanding pieces of TASK-006:

1. **Declared candidate fixtures** — a small benchmark catalogue
2. **Criterion 14** — executable proof the delivered two-tier scenarios still
   decide identically
3. **Run policy** — something that actually *states* the purchase ceiling

All three are done. **TASK-006 still cannot be marked complete**, and §12
explains why — it is the most important thing in this document.

## 2. What changed

| File | What it is |
|---|---|
| `radhanite/policy.py` | **New.** `RunPolicy` — the ceiling, and nothing else |
| `radhanite/capability.py` | `DECLARED_CANDIDATES` — three fixtures |
| `tests/test_compatibility.py` | **New.** The Criterion 14 proof, 16 tests |
| `tests/test_policy.py` | **New.** 17 tests |
| `tests/test_capability.py` | 11 fixture tests added |
| `radhanite/__init__.py` | Exports, and the status note |
| `tasks/TASK-006_...md` | Deliverables ticked; **new §5a — why it cannot close** |
| `tasks/BACKLOG.md` | `BL-13` marked implemented-not-closed; **`BL-16`** added |
| `docs/reviews/PR-026_CODEX_REVIEW.md` | The review prompt, **committed before the review** |
| `docs/reviews/README.md` | Its row |
| `docs/pr_explanations/PR-026_...md` | This document |

**No dependency.** The project still has none.

## 3. Why the change was needed

TASK-006's economic rule has been working since PR #23. Three of its six
deliverables were outstanding, and one of them — Criterion 14 — was the only
place in the repository where a claim was **asserted but not demonstrated**.
That is the kind of gap that quietly becomes untrue.

## 4. How this worked before

The rule worked, and was exercised only by fixtures written inside the tests.
Nothing supplied the purchase ceiling as policy; every caller passed a number.
And the claim that the old two-tier scenarios still decide identically rested on
an argument about `Money` never being negative — an argument, not a test.

## 5. How it works after

### Test-first, and the tests really were red

Written first, run against the current code, and they failed for exactly the
right reason:

```
ModuleNotFoundError: No module named 'radhanite.policy'
ImportError: cannot import name 'DECLARED_CANDIDATES' from 'radhanite.capability'
Ran 390 tests — FAILED (errors=3)
```

Then implemented. **467 passing.** §10 has the full before/after.

### The fixtures

Three candidates — `quick-check-001`, `standard-review-001`,
`deep-analysis-001` — priced 8¢, 40¢ and $1.50, ordered by ascending cost.

Their figures deliberately mirror the escalations of the three declared
strategies, which is what makes them sufficient for Criterion 14 without
inventing a second set of numbers to reason about. A test asserts the catalogue
stays **at most five entries**: this is a test fixture, not a catalogue, and not
a discovery mechanism.

A test also scans the identifiers for provider, network and payment words. The
fixtures are the easiest place for a sponsor name to arrive.

### The run policy

`RunPolicy` carries one field and refuses everything questionable: **no default**
(a default would make a safety limit optional), zero, negative, non-integers, and
**`True`** — which would otherwise pass as a ceiling of one, since `bool` is a
subclass of `int`.

It is deliberately stricter than the decision primitives, which tolerate a
ceiling of zero. A run permitted to buy nothing has no use for a capability
decision at all.

**It drives nothing.** No loop, no counter, no orchestration. A run reads the
number and passes it to the decision.

### Criterion 14 — the proof

`tests/test_compatibility.py` runs every scenario **twice** — once through
TASK-001's `decide`, once through the TASK-006 path — and asserts both reach the
same decision *and* compute the same incremental expected value.

Covered: all three declared strategies (bought, unaffordable, worthless task);
the specification's own worked example; exactly affordable; one cent short; the
exact tie; a penny above the tie; zero uplift; a worsening capability; zero
budget; a large budget that cannot rescue a worthless capability; a valuable
capability with no budget.

**Result: every scenario agrees.** The compatibility claim in §7 is now
demonstrated rather than argued.

## 6. What goes into the system

Unchanged. `RunPolicy` adds one number a run states about itself.

## 7. What the system decides

Unchanged. Nothing in this PR touches the economic rule, and a test asserts the
delivered kernel reaches identical decisions.

## 8. What comes out

Unchanged, plus a fixture catalogue and a policy object callers can use instead
of typing a number.

## 9. How it can fail

The fixtures are the exposed surface. A catalogue that grows, acquires a fourth
field, or picks up a provider name stops being a benchmark and starts being a
product decision nobody made. Three tests guard exactly that.

## 10. Tests run and their results

**Before** — the three new modules, run against the code as it stood:

| Module | Result |
|---|---|
| `tests/test_policy` | `ModuleNotFoundError: No module named 'radhanite.policy'` |
| `tests/test_compatibility` | same — it imports `RunPolicy` |
| `tests/test_capability` | `ImportError: cannot import name 'DECLARED_CANDIDATES'` |
| Full suite | `Ran 390 tests — FAILED (errors=3)` |

**Honest note on what that red state proves.** These are import failures, not
assertion failures — the code simply did not exist. That is a genuine red state
and it is the strongest one available for a fixture-and-object addition, but it
demonstrates *absence*, not that each assertion discriminates. The mutation
checks below are what establish the latter.

**After:**

```
$ python3.12 -m unittest discover -q
Ran 467 tests in 0.13s
OK
```

**423 existing, unchanged, plus 44 new.**

One test was rewritten during implementation. A scan for a hard-coded ceiling
flagged `max_capability_steps=4` inside a **doctest** — a call site, which is
exactly what a caller should do. Loosening the scan would have been the easy
fix; instead it was replaced with a behavioural check that the parameter has no
default in `assess`, `select_capability` and `RunPolicy`, plus a scan for a
module-level constant. That measures the thing the rule is actually about.

### Deliberate faults, all caught

Bytecode writing disabled throughout, after the stale-`__pycache__` problem
recorded in PR-023.

| Fault introduced | Result |
|---|---|
| Compatibility path uses `>=` instead of strict `>` | **3 failures** |
| Compatibility path uses budget where task value belongs | **45 failures** |
| Two declared fixtures share an identifier | **1 failure** |
| A default `max_capability_steps = 4` appears | **2 failures** |
| `RunPolicy` accepts zero steps | **1 failure** |
| `RunPolicy` accepts `True` as one step | **1 failure** |

## 11. Assumptions made

- **Criterion 14 is scoped to the fixtures that exist**, as §7 already states.
- **The mapping in §7 is the right one**: the initial attempt is the baseline,
  the escalation is one candidate.

## 12. Known limitations — **TASK-006 cannot be closed**

All six deliverables are met and **20 of 22 acceptance criteria are
demonstrated**. Two cannot be, and the reason is not an implementation gap.

**Criterion 10** — *task already successful → STOP, with no candidate
evaluated.* §2.5 of the same task says this condition is *"**not** decided
here… this module is never told the answer."* Nothing in TASK-006 can observe
that a task has succeeded.

**Criterion 13** — *total spend can never exceed the budget, on every path.* The
selector never spends. Per-decision affordability **is** enforced and tested,
including where cost exactly equals the remaining budget — but a *total* across
purchases needs something that accumulates, and §2.7 gives that to the run loop.

**Both belong to the run loop, and no authorized task owns the run loop.** §2.7
hands it four steps of the iterative cycle and stops; nothing picks them up.

So TASK-006's own §4 asks for two things its own §2.5, §2.7 and §3 forbid it
from doing. **That is an inconsistency in the specification**, recorded in a new
§5a rather than resolved by satisfying the criteria in the wrong layer or by
quietly marking the task done.

### The one narrowing, still true

A **zero-cost** escalation is expressible in TASK-001 and cannot be a candidate
under TASK-006 §2.5 A. `TheOneNarrowingTests` proves all three parts: TASK-001
accepts it and escalates, the generalized model refuses it at construction, and
**no declared strategy is affected** — all three have positive escalation costs.
Recorded, not hidden.

## 13. Explicitly out of scope

No run loop, task-state generation, baseline probability production, candidate
discovery, provider discovery, capability execution, consumed-ID mutation,
step-count mutation, or integration of any kind. No dependency. TASK-001's
implementation and TASK-006's economic rule are untouched.

## 14. Deferred to future tasks

**`BL-16` — the run loop.** Newly added, unauthorized, and now the thing
standing between a working economic kernel and a working system.

## 15. How to explain this to a judge

> We finished the last three pieces of the decision engine — the benchmark
> figures, the run's purchase limit, and a proof that the older simpler engine
> still reaches exactly the same decisions. That proof runs every historical
> scenario through both engines and requires them to agree.
>
> Then we tried to mark the task complete, and couldn't.
>
> Two of its own acceptance criteria need something the same task explicitly
> forbids itself from doing: noticing the job is already finished, and adding up
> spending across several purchases. Both need a loop, and no approved piece of
> work owns that loop yet.
>
> So the task stays open, with a section explaining exactly why. The alternative
> was to tick two boxes we hadn't earned.
