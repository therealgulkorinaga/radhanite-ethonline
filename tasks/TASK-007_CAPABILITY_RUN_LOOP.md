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
        run state (§3)
             │
             ▼
      is the task already complete?  ──── yes ──► TERMINAL: task complete (§6)
             │ no
             ▼
    ┌──► current candidate set        ← candidate source (§5.1), given task_state
    │        │
    │        ▼
    │   TASK-006 eligibility, per candidate
    │        │
    │        ▼
    │   TASK-006 ranking / selection
    │        │
    │        ├── STOP ──────────────► TERMINAL: economic or safety (§6)
    │        │
    │        ▼ selected capability
    │   execute it — exactly one       ← capability executor (§5.2)
    │        │
    │        ▼
    │   apply the result (§7):
    │     · consume the candidate ID           — always
    │     · commit `committed_cost`            — always, success or failure
    │     · increment the paid-step count      — iff committed_cost > 0
    │        │
    │        ├── failure ────────────► TERMINAL: execution failure (§6)
    │        │
    │        ▼ success
    │   task-state updater             ← §5.3, returns new task_state,
    │        │                            probability and completion
    └────────┘
```

**The already-complete check comes first, before any candidate is considered.**
That ordering is §6.1's precedence rule and it is not an optimisation.

**One iteration attempts at most one capability.** Two would make the step count
meaningless and the safeguards unenforceable.

## 3. Run state

The minimum a run must carry. Immutable per transition: each iteration produces
a **new** state rather than mutating the last.

| Field | Why it is needed | Changes? |
|---|---|---|
| `task_value` | An input to every eligibility test | Fixed |
| `initial_budget` | The original run budget — §3.2 | Fixed |
| `policy` | `RunPolicy` — the step ceiling | Fixed |
| `task_state` | **Opaque.** §3.1 | Yes |
| `current_success_probability` | What each candidate is measured against | Yes |
| `remaining_budget` | Passed to eligibility each iteration | Yes |
| `total_spend` | §3.2 | Yes |
| `consumed_candidate_ids` | §2.5a single-use enforcement | Yes |
| `paid_capability_step_count` | §2.5 C ceiling enforcement — §7.2 | Yes |
| `status` | Running, or which terminal state — §6 | Yes |
| `history` | §3.3 | Append-only |

**Deliberately excluded**, because no specified behaviour needs them: any task
description or constraints text, any provider identity, any per-capability
metadata, and any retry counters — §7 authorizes no retry.

### 3.1 `task_state` is opaque, and TASK-007 does not interpret it

**TASK-007 stores `task_state` and passes it. It never reads inside it.**

Candidate generation needs to know what the task currently looks like. So does
the state updater. So does anyone reconstructing a decision from the record.
Carrying only `current_success_probability` would make all three impossible:
a probability is a *summary* of a state, not the state.

| | |
|---|---|
| **Given to** | the candidate source (§5.1) and the task-state updater (§5.3) |
| **Returned by** | the task-state updater, alongside the new probability and the completion verdict |
| **Interpreted by** | **neither TASK-007 nor TASK-006** |

It must be **provider-neutral**: nothing inside it may reach the economic
decision, which sees only the three candidate fields. `ARCHITECTURE.md` §6
item 7 applies — this task must not acquire a field, branch or helper that
reads it.

> **Producing and interpreting `task_state` is owned by a separate future task
> that does not yet exist**, and is not designed here. See §5.3 and §10.

### 3.2 Budget accounting

`initial_budget` is **the original run budget**, not a capability-only
allowance. There is no hidden sub-budget.

`total_spend` is **all spend committed from that budget up to the current
state**, including anything spent before the loop was entered — a baseline
attempt, for instance. TASK-006 §2.2a already defines `remaining_budget` as net
of everything spent so far, including the baseline, and an accounting model that
counted only loop spend would contradict it.

**At loop entry**, initialization must therefore satisfy:

```
total_spend = initial_budget - remaining_budget
```

and thereafter every committed cost increases `total_spend` and decreases
`remaining_budget` by the same exact `Money` amount, preserving:

```
total_spend + remaining_budget == initial_budget
```

**No separate `spend_before_capability_loop` field.** It would be derivable
from the entry state, it would duplicate a fact already recorded in the first
transition's before-snapshot, and a redundant field is a field that can drift.
Criterion 12 tests the initialization directly instead.

All arithmetic is exact `Money`.

### 3.3 The history is a sequence of transitions, not nested states

One immutable `TransitionRecord` per iteration. **Nothing contains itself,
transitively or otherwise** — a record holds *snapshots*, and a snapshot
excludes `history`.

| Field | Contents |
|---|---|
| `before` | Run-state snapshot, **excluding `history`** |
| `selection` | The **complete** TASK-006 `Selection` |
| `execution` | The execution result or failure record — absent on a STOP iteration |
| `after` | Run-state snapshot, **excluding `history`** |

A snapshot carries every §3 field except `history`: `task_value`,
`initial_budget`, `policy`, `task_state`, `current_success_probability`,
`remaining_budget`, `total_spend`, `consumed_candidate_ids`,
`paid_capability_step_count`, `status`.

The `Selection` is kept **whole** rather than summarized, because TASK-006 §8
already requires every candidate considered with its figures and the reason it
failed. Summarizing here would discard exactly what that section exists to
preserve.

## 4. Invariants

1. **`total_spend + remaining_budget == initial_budget`** after every
   transition, and at initialization — §3.2.
2. **Remaining budget never becomes negative.**
3. **A consumed candidate ID never executes again** — §2.5a.
4. **The same capability type may return under a new candidate ID.** Enforced by
   ID alone; this task acquires no notion of type.
5. **No capability executes unless TASK-006 selected it.**
6. **At most one capability execution is attempted per iteration.**
7. **`paid_capability_step_count` increments exactly once per attempt that
   committed a positive cost**, and never otherwise — §7.2.
8. **`paid_capability_step_count >= max_capability_steps` prevents another
   execution** — TASK-006 §2.5 C, unchanged.
9. **No execution occurs after a terminal state**, of any kind.
10. **TASK-006 stays provider-neutral.** Nothing passed into the decision
    carries provider, network or payment identity — §5.4.
11. **An execution failure never appears as successful completion**, and never
    silently records zero spend when a cost was committed.
12. **`0 <= committed_cost <= candidate.cost`**, and `committed_cost` never
    exceeds `remaining_budget` — §7.1.
13. **Every state transition is reconstructable from the history**, which is
    non-recursive — §3.3.

## 5. External interfaces

Three boundaries, all **provider-neutral**. This task orchestrates them and
defines none of their domain reasoning.

### 5.1 Candidate source

> Given `task_state` and the current run state, return the current candidate set.

Whether the candidates came from declared fixtures, a marketplace, an onchain
index or anything else **is not this task's concern**.
`capability.DECLARED_CANDIDATES` satisfies this today, which is how the loop can
be tested with no integration in existence.

### 5.2 Capability executor

> Given the selected candidate and the current state, attempt that capability
> and return a structured execution result.

The result carries:

| | |
|---|---|
| `succeeded` | Whether the capability delivered |
| `committed_cost` | Exact `Money` actually committed — §7.1 |
| `evidence` | Opaque; meaningful only to §5.3. Absent or partial on failure |

**No payment or provider fields**, unless a later authorized task demonstrates
one is unavoidable.

### 5.3 Task-state updater

> Given the previous `task_state` and an execution result, return the new
> `task_state`, the new `current_success_probability`, and whether the task is
> now complete.

**TASK-007 never derives a probability or a completion verdict itself.** It
calls this boundary and stores what comes back.

> **This boundary's reasoning requires its own future task**, which does not
> exist and is not designed here. Turning opaque evidence into a declared
> probability and a completion verdict is a domain judgement — the same open
> question recorded in
> [TASK-008](TASK-008_ONCHAIN_INFORMATION_VIA_THE_GRAPH.md) §6.3.

### 5.4 What may cross into the decision

Only the three TASK-006 §2.2 candidate fields, plus the run-level inputs in
§2.2a. `task_state`, `evidence`, and anything a provider attached to either
**must not reach an eligibility test or a ranking comparison.**

## 6. Terminal states

Four, kept distinct. Collapsing them would destroy the distinction TASK-006 §8
spent effort creating.

| State | Meaning |
|---|---|
| **`TASK_COMPLETE`** | The success condition was satisfied. **Zero further executions** |
| **`ECONOMIC_STOP`** | Nothing eligible, and at least one candidate was refused on economic grounds |
| **`SAFETY_STOP`** | Nothing eligible, and no candidate was refused on economic grounds — or a run-level safeguard blocked the run outright |
| **`EXECUTION_FAILURE`** | A capability was attempted and did not deliver — §7.3 |

### 6.1 Precedence — already-complete wins

**The already-complete check runs before any candidate is considered**, on entry
and after every successful execution.

Consequently, a run whose task is complete terminates `TASK_COMPLETE` **even
when**:

- `max_capability_steps == 0`; or
- the step ceiling has been reached; or
- eligible candidates are still on offer.

A completed task is not stopped by a ceiling. It is finished.

### 6.2 Classifying a STOP

Classification is **derived from why the candidates were ineligible**, never
assumed.

TASK-006 already computes this: `Selection.stopped_without_economic_judgement`
is true exactly when every refusal was a §2.5 safeguard. **This task must read
that value rather than re-derive it.**

| Situation | Terminal state |
|---|---|
| Every refusal was a safeguard — consumed, ceiling, non-positive cost | `SAFETY_STOP` |
| Any candidate was refused on economic grounds — budget, uplift, value | `ECONOMIC_STOP` |
| Zero candidates offered, below the ceiling | `ECONOMIC_STOP` — nothing was affordable because nothing was on offer |
| Zero candidates offered, at the ceiling | `SAFETY_STOP` |
| `max_capability_steps == 0`, task not complete | `SAFETY_STOP`, immediately |

**Mixed failures are recorded as they happened.** A run where one candidate
failed on budget and another was already consumed is an `ECONOMIC_STOP` — a real
economic verdict was reached on at least one — and the per-candidate reasons
survive intact in the `Selection`. The run-level label never erases them.

## 7. Execution semantics

Supplied by the human product owner following review. **Binding on the
implementation**, and — like everything in this document — not itself an
authorization to build.

### 7.1 The executor commits, and reports what it committed

The selected candidate's declared `cost` is the **maximum the executor is
authorized to commit**. What it actually committed comes back as
`committed_cost`.

```
0 <= committed_cost <= candidate.cost
committed_cost <= remaining_budget
```

**`committed_cost` is what changes the accounting** — not the declared cost.
Failure does **not** imply zero spend: a call that debited and then failed
committed real money, and recording zero would falsify the ledger.

### 7.2 On every execution attempt, success or failure

1. The selected **candidate ID becomes consumed.**
2. **`committed_cost` is recorded** and applied to `total_spend` and
   `remaining_budget`.
3. **If `committed_cost > 0`**, `paid_capability_step_count` increments — a paid
   capability step occurred.
4. **If `committed_cost == 0`**, the attempt is recorded but the paid-step count
   does **not** increment. Nothing was bought.

### 7.3 Failure terminates the run

An execution failure terminates the run as **`EXECUTION_FAILURE`**. There is
**no automatic retry**, and retry behaviour is outside current authorization.

**This is what guarantees termination on the failure path** — explicitly, not by
side effect.

> An earlier revision of this document claimed that consuming the candidate ID
> was itself sufficient to guarantee termination. **It is not.** Nothing stops a
> candidate source regenerating an equivalent capability under a fresh ID, which
> would be eligible on identical terms. Termination on failure rests on §7.3's
> explicit terminal state; ID consumption prevents *re-execution of the same
> offer*, which is a different and narrower guarantee.

Termination on the non-failure paths rests on TASK-006's three safeguards, which
are unchanged.

## 8. Inherited from TASK-006 — criteria 10 and 13

TASK-006 §5a records two acceptance criteria whose end-to-end meaning needs a
run loop. **This task inherits responsibility for demonstrating them**, meaning
unchanged.

| TASK-006 | As stated there | Inherited as |
|---|---|---|
| **Criterion 10** | *Task already successful → STOP, with no candidate evaluated* | §9 criteria 1 and 2 |
| **Criterion 13** | *Total spend can never exceed the budget, on every path including boundary cases where cost exactly equals the remaining budget* | §9 criteria 12–15 |

**TASK-006 is not made complete by this document existing.** It becomes complete
when a TASK-007 implementation demonstrates these — not before.

## 9. Acceptance criteria

Terminal states and precedence:

1. **Already-complete task → zero executions**, terminal `TASK_COMPLETE` —
   inherited criterion 10.
2. **Already-complete takes precedence** over `max_capability_steps == 0`, over
   a reached ceiling, and over available eligible candidates.
3. **Every candidate refused on economic grounds → `ECONOMIC_STOP`.**
4. **Every candidate refused only by safeguards → `SAFETY_STOP`.**
5. **Mixed refusals → `ECONOMIC_STOP`**, with every per-candidate reason
   preserved in the `Selection`.
6. **`max_capability_steps == 0` with an incomplete task → immediate
   `SAFETY_STOP`**, zero executions.
7. **The step ceiling prevents further execution.**

Execution and the loop:

8. **One successful execution → state updates → STOP.**
9. **Several successful executions run in sequence**, one per iteration.
10. **A consumed candidate ID cannot execute again.**
11. **The same capability type may reappear under a new ID** and execute — by ID
    alone, with no notion of type anywhere.

Accounting — inherited criterion 13:

12. **Baseline spend initializes correctly**: entering with
    `remaining_budget < initial_budget` yields
    `total_spend == initial_budget - remaining_budget`.
13. **A committed cost exactly equal to the remaining budget is permitted**
    where the economics selected it.
14. **`committed_cost` never exceeds the candidate's declared cost, nor the
    remaining budget.**
15. **`total_spend + remaining_budget == initial_budget`** holds across every
    transition, and `total_spend` equals the sum of all committed costs plus
    the entry spend.

Failure semantics:

16. **Success with committed spend** updates accounting and increments the
    paid-step count.
17. **Failure with committed spend** records the spend, consumes the ID,
    increments the paid-step count, and terminates `EXECUTION_FAILURE`.
18. **Failure with zero committed spend** consumes the ID, leaves the paid-step
    count unchanged, and terminates `EXECUTION_FAILURE`.
19. **No execution occurs after any terminal state.**

Neutrality and audit:

20. **Provider metadata cannot influence TASK-006.** Candidates whose external
    metadata differs but whose three economic fields are identical produce
    **identical assessments and an identical selection**. This asserts nothing
    about execution results, evidence, subsequent task states, or whole runs —
    §9a.
21. **Candidate ordering cannot change the winner** — permuted offers, identical
    selections.
22. **The history is non-recursive** and reconstructs every decision and
    transition, including the rejected candidates and their reasons.

### 9a. What criterion 20 does not claim

TASK-006's neutrality guarantee is about **the economic kernel**, and stops
there:

| Guaranteed | **Not** guaranteed |
|---|---|
| Identical economic inputs → identical assessments | Identical execution results |
| Identical eligible economics → identical selection | Identical evidence returned |
| Provider metadata never reaches or influences selection | Identical task-state updates |
| | Identical complete runs |

Two capabilities priced the same and claiming the same probability are
indistinguishable **to the decision**. They may then do entirely different
things, return different evidence, and send the run down different paths. That
is expected, and a criterion demanding otherwise would be asserting something
neither TASK-006 nor this task can deliver.

## 10. Out of scope

Not owned by this task, and not authorized by it:

- **producing or interpreting `task_state`** — the reasoning that turns
  previous state plus execution evidence into a new state, a declared
  probability and a completion verdict. **This requires its own future task**,
  which does not exist and is not designed here — §5.3;
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
- Confirm §7's execution semantics are implemented **exactly** — the authorized
  maximum, `committed_cost` driving the accounting, the paid-step count rising
  only on positive spend, and failure terminating the run with no retry.
- Confirm `task_state` is **never read** by this task or by the decision, and
  that no field, branch or helper inspects it — §3.1, §5.4.
- Confirm the history is **non-recursive**: no snapshot contains a history.
- Confirm the already-complete check **precedes** candidate selection on every
  path — §6.1.
- Confirm STOP classification is **read from**
  `Selection.stopped_without_economic_judgement` rather than re-derived — §6.2.
