# TASK-007 — The capability run loop

**Status:** Specified — **NOT AUTHORIZED for implementation**
**Authorization:** None. This document specifies the work; it does not permit it.
**Traces to:** [`PREREQ-001`](../docs/PREREQ-001_PRODUCT_DEFINITION.md) §5.2, §5.5
**Bounded by:** [`ARCHITECTURE.md`](../docs/ARCHITECTURE.md) §2.1, §2.2.3, §6
**Replaces backlog entry:** `BL-16`
**Depends on:** TASK-006's kernel — implemented and merged
**Inherits:** TASK-006 §4 criteria 10 and 13 — see §8

---

## 1. Purpose

TASK-006 delivered a decision. **It decides once, and then nothing happens.**

This task turns that kernel into a run: something that asks the decision
repeatedly, acts on each answer, keeps the state the decision needs, and stops.

**It redefines no economics.** The formula, the six eligibility conditions, the
three-level ranking and the three termination safeguards are TASK-006's and are
not reopened here. This task supplies the loop around them and the state they
read.

## 2. The loop

```
        run state (from §3)
             │
             ▼
    ┌──► current candidate set        ← candidate source (§5.1)
    │        │
    │        ▼
    │   TASK-006 eligibility, per candidate
    │        │
    │        ▼
    │   TASK-006 ranking / selection
    │        │
    │        ├── STOP ──────────────► terminal (§6)
    │        │
    │        ▼ selected capability
    │   execute it — exactly one       ← capability executor (§5.2)
    │        │
    │        ▼
    │   apply result to run state:
    │     · commit the spend
    │     · mark the candidate ID consumed
    │     · increment the step count
    │        │
    │        ▼
    │   obtain updated task state      ← task-state updater (§5.3)
    │        │
    └────────┘
```

**One iteration buys at most one capability.** A loop that could buy two in a
pass would make the step count meaningless and the safeguards unenforceable.

## 3. Run state

The minimum a run must carry. Immutable per transition: each iteration produces
a **new** state rather than mutating the last, so the history in §3.1 is a
sequence of facts rather than a reconstruction.

| Field | Why it is needed | Owner |
|---|---|---|
| `task_value` | An input to every eligibility test | Task, fixed |
| `initial_budget` | The ceiling total spend is checked against | Task, fixed |
| `policy` | `RunPolicy` — the step ceiling | Run, fixed |
| `current_success_probability` | What each candidate is measured against | §5.3, changes |
| `remaining_budget` | Passed to eligibility each iteration | This task, changes |
| `total_spend` | Checked against `initial_budget` | This task, changes |
| `consumed_candidate_ids` | §2.5a single-use enforcement | This task, changes |
| `capability_step_count` | §2.5 C ceiling enforcement | This task, changes |
| `status` | Running, or which terminal state — §6 | This task |
| `history` | §3.1 | This task, append-only |

**Deliberately excluded**, because nothing in this task needs them: any task
description or constraints text, any provider identity, any per-capability
metadata, any timing or retry counters (until §7 is decided), and anything
belonging to the domain layers in §5.

`remaining_budget` and `total_spend` are both carried although one is derivable
from the other. The derivation is the invariant — §4 item 1 — and a run record
that stated only one would make it uncheckable after the fact.

### 3.1 The history

An append-only record, one entry per iteration, each carrying:

- the **`Selection`** TASK-006 returned, whole — which already holds every
  candidate considered, its figures, and why each failed;
- the **run state before** the iteration;
- the **execution result**, where a capability was executed;
- the **run state after**.

A `Selection` is kept rather than summarized because TASK-006 §8 already
requires the rejected candidates and their reasons, and summarizing here would
discard what that section exists to preserve.

## 4. Invariants

The specification guarantees all of these, and each gets a test in §9.

1. **Total spend never exceeds the initial budget**, and
   `total_spend + remaining_budget == initial_budget` after every transition.
2. **Remaining budget never becomes negative.**
3. **A consumed candidate ID never executes again** — §2.5a.
4. **The same capability type may return under a new candidate ID**, once the
   state has changed. Enforced by ID alone; this task acquires no notion of
   type, exactly as TASK-006 §2.5a forbids.
5. **No capability executes unless TASK-006 selected it.** There is no path from
   a candidate to execution that does not pass through the decision.
6. **At most one capability executes per iteration.**
7. **The step count increments exactly once per completed paid capability step.**
8. **`capability_step_count >= max_capability_steps` prevents another
   execution** — TASK-006 §2.5 C, unchanged.
9. **No execution occurs after a terminal state**, of any kind.
10. **TASK-006 stays provider-neutral.** Nothing this task passes into the
    decision may carry provider, network or payment identity.
11. **An execution failure can never appear as successful completion.** §7.
12. **Every state transition is reconstructable from the run record** —
    `PREREQ-001` §8 criterion 3.

## 5. External interfaces

Three boundaries, all **provider-neutral**. This task orchestrates them and
defines none of their domain reasoning. Each is specified here only as a shape;
what sits behind them is other work, none of it authorized.

### 5.1 Candidate source

> Given the current run and task state, return the current candidate set.

Whether the candidates came from declared fixtures, a marketplace, an onchain
index, or anything else **is not this task's concern and must not become
visible to it**. `capability.DECLARED_CANDIDATES` satisfies this interface
today, which is how the loop can be tested without any integration existing.

### 5.2 Capability executor

> Given the selected candidate and the current state, perform that capability
> and return a structured execution result.

The result carries whether it succeeded and whatever the task-state updater
needs — and **no payment or provider fields** unless a later authorized task
demonstrates one is unavoidable. A field naming a provider here would reach the
decision through §5.3 and defeat §4 item 10.

### 5.3 Task-state updater

> Given the previous task state and an execution result, return the new task
> state — including the new current success probability — and whether the task
> is now complete.

**This is where the domain reasoning lives, and it is emphatically not here.**
How evidence becomes a probability is a judgement this task orchestrates and
does not make. It is the same open question recorded in
[TASK-008](TASK-008_ONCHAIN_INFORMATION_VIA_THE_GRAPH.md) §6.3, and **no
authorized task owns it.**

## 6. Terminal states

Four, kept distinct. Collapsing them into one STOP would destroy the
distinction TASK-006 §8 spent effort creating.

| State | Meaning |
|---|---|
| **Already complete** | The task's success condition was satisfied before any decision. **Zero capabilities execute** |
| **Economic stop** | TASK-006 returned STOP and at least one candidate was refused on economic grounds |
| **Safety stop** | TASK-006 returned STOP and every refusal was a §2.5 safeguard — including the step ceiling, and including an empty offer at the ceiling |
| **Unrecoverable execution failure** | §7 |

The middle two come straight from `Selection.stopped_without_economic_judgement`,
which already draws that line. This task must not re-derive it.

## 7. Execution failure — **UNRESOLVED, requires authorization** ⚠️

**If a selected capability call fails, what happens?**

This is a product decision and it is not taken here. Four things hang on it, and
inventing an answer would embed economics this task has no authority over.

| | Was the money spent? | Is the ID consumed? | Does the step count rise? | Retry? |
|---|---|---|---|---|
| **A — Paid and spent** | Yes | Yes | Yes | No |
| **B — Not paid** | No | Yes | No | No |
| **C — Not paid, retryable** | No | No | No | Yes, bounded |
| **D — Fail the run** | Either | — | — | Run ends |

**Recommended: B — not paid, consumed, no step.**

The reasoning: the run did not receive what it was deciding about, so charging
it would make `total_spend` stop meaning *value acquired*. Consuming the ID
anyway is what guarantees termination — a failing capability that stayed on offer
would be selected again on identical terms forever, which is the same
non-termination §2.5 A exists to prevent. Not incrementing the step count keeps
that counter meaning *capabilities actually bought*.

Against it: a real payment rail may debit before failing, in which case A is
what actually happened and B would record a falsehood. That is why this needs
deciding with the payment integration in view rather than now.

**C is not recommended** without a bound and a distinct terminal state, since
retry is where a run loop quietly becomes non-terminating.

**No provider-specific retry rules are specified, and none may be added.** A
rule that behaved differently for one provider would put provider identity into
the loop.

Whatever is chosen, invariant 11 holds: **a failure never appears as success.**

## 8. Inherited from TASK-006 — criteria 10 and 13

TASK-006 §5a records two acceptance criteria whose end-to-end meaning needs a
run loop. **This task inherits responsibility for demonstrating them**, with
their meaning unchanged.

| TASK-006 | As stated there | Inherited as |
|---|---|---|
| **Criterion 10** | *Task already successful → STOP, with no candidate evaluated* | §9 test 1 |
| **Criterion 13** | *Total spend can never exceed the budget, on every path including boundary cases where cost exactly equals the remaining budget* | §9 tests 10, 11, 12 |

**TASK-006 is not made complete by this document existing.** It becomes
complete when these are demonstrated by a TASK-007 implementation — not before,
and not by writing a specification that promises to.

## 9. Acceptance criteria

1. **Task already complete → zero executions**, and the terminal state is
   *already complete* — inherited criterion 10.
2. **No eligible candidate → economic stop.**
3. **One capability executes, state updates, then STOP.**
4. **Several capabilities execute in sequence**, each a separate iteration.
5. **A consumed candidate ID cannot execute twice.**
6. **The same capability type, under a new candidate ID, may execute later** —
   by ID alone, with no notion of type anywhere.
7. **The step ceiling prevents another execution.**
8. **`max_capability_steps = 0` produces an immediate safety stop**, with zero
   executions.
9. **A positive budget does not override the step ceiling** — criterion 22's
   run-level form.
10. **Spend exactly equal to the remaining budget is allowed**, where the
    economics selected it — inherited criterion 13's boundary.
11. **Spend can never exceed the remaining budget**, on any path.
12. **Total spend equals the sum of committed capability costs**, and
    `total_spend + remaining_budget == initial_budget` throughout.
13. **Candidate ordering cannot change the winner** — permuted offers, identical
    runs.
14. **Provider identity cannot influence selection.** Candidates differing only
    in metadata produce identical runs.
15. **Execution failure follows the authorized §7 policy exactly**, and never
    reads as success.
16. **No execution occurs after a terminal state.**
17. **The full run record reconstructs every decision and transition**, including
    the candidates that were rejected and why.

## 10. Out of scope

Not owned by this task, and not authorized by it:

- how the **baseline or current success probability** is derived;
- how **success or completion** is evaluated;
- how **candidates are discovered or generated**;
- **provider discovery**;
- any **capability-specific logic**;
- **Hedera, Circle/Arc, The Graph, Privy, OpenRouter**;
- **payment-provider internals**;
- **learned probability estimation** — `BL-05`, `BL-06`;
- **sponsor-specific routing** of any kind.

All of these enter through §5's interfaces or not at all.

Also excluded: any change to TASK-006's formula, conditions, ranking or
safeguards.

## 11. The demonstration this has to support

The supplier-onboarding demonstration in `PREREQ-001` §6 must be expressible:

```
baseline  →  a second opinion  →  updated state
          →  research           →  updated state
          →  optionally, analysis
          →  STOP
```

**Driven entirely by changing state and TASK-006 decisions.** Not by a
hard-coded provider order, not by a sequence this task knows about, and not by
any capability being preferred for what it is.

`PREREQ-001` §6.3 already requires that a run which buys nothing, or stops after
one purchase, is equally correct. A loop that always produces the full sequence
would be demonstrating wiring rather than economics, and would falsify the
product's central claim.

## 12. Review notes

- Confirm **no economics moved** into this task: no formula, no condition, no
  ranking, no threshold.
- Confirm **no path reaches execution without a TASK-006 selection**.
- Confirm the step count rises **exactly once** per completed paid step, and
  never on a failure unless §7's authorized policy says so.
- Confirm the loop **terminates** under every §9 scenario, and say which
  safeguard does it in each.
- Confirm **no notion of capability type** exists — consumption is by ID.
- Confirm **no provider name** appears anywhere, including fixtures, comments
  and test names.
- Confirm §7 was **decided by the product owner before implementation**, and
  that the implementation matches what was decided.
