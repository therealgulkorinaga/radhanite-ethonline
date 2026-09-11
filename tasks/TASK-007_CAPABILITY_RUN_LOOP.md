# TASK-007 — The capability run loop

**Status:** Authorized — **PR A implemented.** The §3 state model exists; the loop, execution and classification do not
**Authorization:** PR A authorized by the human product owner, 2026-09-11
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
    │     · increment capability_step_count    — always, one per attempt
    │     · commit `committed_cost`            — always, success or failure
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
| `capability_step_count` | **Executed attempts**, not dollars — §7.2 | Yes |
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

#### 3.1.1 Opacity is not aliasing

**Opaque means TASK-007 does not interpret the state. It does not mean TASK-007
may retain a mutable reference to it.** An earlier revision of this section
concluded otherwise — that storing by reference *followed* from opacity, because
copying or freezing would require inspection. `CODEX-PR030-02` rejected that,
and it was wrong on both counts:

- **It does not follow.** Freezing a structure reads its *shape* — is this a
  mapping, a sequence, a set — and never its meaning. No key, value or field is
  interpreted, so nothing about opacity is given up.
- **The consequence is unacceptable.** With a live reference, a caller mutating
  their own object rewrites what an already-written audit record appears to say,
  and can insert a back-reference into it that makes it recursive after the
  fact — defeating §3.3 without touching this module.

So `task_state` is **frozen structurally on the way in**: containers become
immutable equivalents, already-immutable values pass through, cycles are
refused, and **an object that cannot be frozen is refused rather than stored**.
Refusal is decided from the object's type alone, so even a value that raises on
every read is refused without being read.

The obligation this places on callers is explicit: **supply immutable values, or
containers of immutable values.** That is a narrower contract than "anything at
all", and a deliberate one — auditability is the point of §3, and a record that
can change after it is written is not a record.

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

#### 3.2.1 The ledger is bounded at both ends

`Money` can represent negative amounts, so the identity in §3.2 is not
sufficient on its own: `remaining_budget > initial_budget` would satisfy it
while producing a **negative** `total_spend`, which is not a coherent ledger.

**At loop entry, and after every transition:**

```
0 <= remaining_budget <= initial_budget
0 <= total_spend      <= initial_budget
total_spend + remaining_budget == initial_budget
```

A state violating any of these is **invalid and must be refused**, not
processed. Specifically, all five of these are rejected:

| Rejected state | Why |
|---|---|
| `remaining_budget < 0` | The ceiling has already been breached |
| `remaining_budget > initial_budget` | A run cannot hold more than it was given |
| `total_spend < 0` | Spend cannot be negative |
| `total_spend > initial_budget` | `PREREQ-001` §4.2's hard ceiling, breached |
| `total_spend + remaining_budget != initial_budget` | The ledger does not balance |

**After an execution committing `committed_cost`:**

```
new_total_spend      = old_total_spend      + committed_cost
new_remaining_budget = old_remaining_budget - committed_cost
new_total_spend + new_remaining_budget == initial_budget
```

§7.1 already bounds `committed_cost` by `remaining_budget`, which is what keeps
the lower bound on the remaining budget from being crossed.

**Pre-loop spend is preserved, not assumed away.** `initial_budget` is the
original task budget; `remaining_budget` may already be lower on entry because
earlier work spent money. TASK-007 initializes `total_spend` from the
difference rather than assuming zero — which is why the upper bound is stated
separately from the identity.

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
`capability_step_count`, `status`.

The `Selection` is kept **whole** rather than summarized, because TASK-006 §8
already requires every candidate considered with its figures and the reason it
failed. Summarizing here would discard exactly what that section exists to
preserve.

### 3.4 What PR A delivered

`radhanite/runstate.py`, and nothing else.

| | |
|---|---|
| `RunStatus` | `RUNNING` plus §6's four terminal values. **Holding one; deciding which is not this step's job** |
| `RunSnapshot` | Every §3 field **except `history`** — §3.3 |
| `TransitionRecord` | `before`, `selection`, `after`, `execution`. Defined so `history` has a member type; **no transition is produced** |
| `RunState` | The §3 fields, `.max_capability_steps` read from the policy, and `.snapshot()` |
| `begin_run(...)` | Derives `total_spend` from the budgets. A convenience, **not the only validated path** |

**Every construction is validated.** The invariants live in `__post_init__` on
all three records, so `RunState(...)`, `RunSnapshot(...)` and
`TransitionRecord(...)` enforce the same rules `begin_run` does. An earlier
revision put them only in `begin_run` while exporting a directly constructible
`RunState`; `CODEX-PR030-01` rejected that, on the grounds that one safe path
and one unsafe path is one unsafe path.

**`task_state` is frozen, not aliased** — §3.1.1.

**Not built**: execution, the executor interface, execution results,
committed-cost transitions, candidate consumption, step increments, task-state
updates, acquisition calls, eligibility, ranking, selection, terminal
classification, retry, and the loop itself.

### 3.5 Retracted: the `task_state` storage question was not ambiguous

This section previously recorded an "ambiguity §3.1 leaves open": that §3.1
settled opacity but not what happens when a caller mutates the state
afterwards, leaving the choice between aliasing and immutability an open
product question.

**That was not an ambiguity; it was a wrong conclusion.** Aliasing was never
entailed by opacity, and the requirement that resolves it — §4 invariant 13,
every transition reconstructable from a non-recursive history — was already
written down. `CODEX-PR030-02` identified this. The resolution is §3.1.1, and
no product decision was needed to reach it.

One question genuinely remains open, and it is narrower: **§3.1.1 constrains
what a `task_state` may be, and the task that will produce `task_state` does
not exist yet** (§5.3, §10). That task must produce immutable state. Recorded
here so it is a known constraint on a future design rather than a surprise.

## 4. Invariants

1. **`total_spend + remaining_budget == initial_budget`** after every
   transition, and at initialization — §3.2.
2. **`0 <= remaining_budget <= initial_budget`** and
   **`0 <= total_spend <= initial_budget`**, always — §3.2.1.
3. **A consumed candidate ID never executes again** — §2.5a.
4. **The same capability type may return under a new candidate ID.** Enforced by
   ID alone; this task acquires no notion of type.
5. **No capability executes unless TASK-006 selected it.**
6. **At most one capability execution is attempted per iteration.**
7. **`capability_step_count` increments exactly once per execution attempt**,
   whatever it cost and whether it succeeded — §7.2. A decision that executes
   nothing never increments it.
8. **`capability_step_count >= max_capability_steps` prevents another
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
> [TASK-011](TASK-011_ONCHAIN_INTELLIGENCE_VIA_THE_GRAPH.md) §6.3.

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
| **`ECONOMIC_STOP`** | Nothing eligible, **below the ceiling**, and at least one candidate was refused on economic grounds |
| **`SAFETY_STOP`** | The ceiling was reached — whatever else was true — or, below it, no candidate was refused on economic grounds |
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

**The ceiling outranks everything.** TASK-006 §2.5 C already makes
`capability_step_count >= max_capability_steps` a run-level safeguard, and
`stopped_without_economic_judgement` already returns true whenever the ceiling
is reached — *whatever else was true of the candidates*. This task must not
reinterpret that.

| Situation | Terminal state |
|---|---|
| **`capability_step_count >= max_capability_steps`** | **`SAFETY_STOP`, always** — regardless of any economic failures also present |
| `max_capability_steps == 0`, task not complete | `SAFETY_STOP`, immediately |
| Below the ceiling, every refusal was a safeguard — consumed, non-positive cost | `SAFETY_STOP` |
| Below the ceiling, any candidate refused on economic grounds | `ECONOMIC_STOP` |
| Below the ceiling, zero candidates offered | `ECONOMIC_STOP` — nothing was affordable because nothing was on offer |

**Worked through, because this is where the earlier revision was wrong:**

| At the ceiling, the offer contains… | Terminal state |
|---|---|
| An economically attractive candidate | `SAFETY_STOP` |
| An economically poor candidate | `SAFETY_STOP` |
| Both economic and safeguard failures, mixed | `SAFETY_STOP` |
| Nothing at all | `SAFETY_STOP` |

An earlier revision classified the mixed case as `ECONOMIC_STOP` on the grounds
that a real economic verdict had been reached on at least one candidate. **That
was wrong.** The run was already forbidden from buying anything before those
candidates were weighed, so no economic verdict ended it. Mixed classification
applies only **below** the ceiling.

**Every per-candidate reason survives regardless.** The `Selection` records why
each candidate failed — budget, uplift, value, consumed, ceiling — and the
run-level label never erases or overwrites them. Classification answers *why the
run ended*; the assessments answer *what was true of each candidate*, and the two
are different questions.

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
2. **`capability_step_count` increments by exactly one.** An attempt occurred.
3. **`committed_cost` is recorded** and applied to `total_spend` and
   `remaining_budget`.

**The counter measures executed attempts, not dollars**, and that is what makes
the ceiling a real termination safeguard.

An earlier revision incremented only when `committed_cost > 0`. **That made the
ceiling defeatable**: a candidate source producing fresh IDs whose executions
committed nothing could loop forever without the count ever moving. A provider
may legitimately execute and charge zero, so the safeguard cannot be made to
depend on money changing hands.

Three concepts, deliberately independent:

| Concept | Measured by | Bounded by |
|---|---|---|
| **Spend** | `committed_cost` → `total_spend` | `initial_budget` |
| **Offer reuse** | consumed candidate IDs | one execution each |
| **Execution count** | `capability_step_count` | `max_capability_steps` |

**Only an execution attempt increments the counter.** A decision that ends in
STOP — of any kind, at any point — executes nothing and increments nothing.

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
| **Criterion 13** | *Total spend can never exceed the budget, on every path including boundary cases where cost exactly equals the remaining budget* | §9 criteria 15–23 |

**TASK-006 is not made complete by this document existing.** It becomes complete
when a TASK-007 implementation demonstrates these — not before.

## 9. Acceptance criteria

Terminal states and precedence:

1. **Already-complete task → zero executions**, terminal `TASK_COMPLETE` —
   inherited criterion 10.
2. **Already-complete takes precedence** over `max_capability_steps == 0`, over
   a reached ceiling, and over available eligible candidates.
3. **Below the ceiling**, every candidate refused on economic grounds →
   `ECONOMIC_STOP`.
4. **Below the ceiling**, every candidate refused only by safeguards →
   `SAFETY_STOP`.
5. **Below the ceiling**, mixed refusals → `ECONOMIC_STOP`, with every
   per-candidate reason preserved in the `Selection`.
6. **At the ceiling → `SAFETY_STOP`, always.** Demonstrated with four offers:
   an economically attractive candidate, an economically poor one, a mixed set
   of economic and safeguard failures, and an empty offer. All four classify
   `SAFETY_STOP`, and in every case the per-candidate reasons survive intact.
7. **`max_capability_steps == 0` with an incomplete task → immediate
   `SAFETY_STOP`**, zero executions.
8. **The step ceiling prevents further execution.**

Execution and the loop:

9. **One successful execution → state updates → STOP.**
10. **Several successful executions run in sequence**, one per iteration.
11. **A consumed candidate ID cannot execute again.**
12. **The same capability type may reappear under a new ID** and execute — by ID
    alone, with no notion of type anywhere.

The capability-step count — the termination safeguard:

13. **Every execution attempt increments `capability_step_count` exactly once**,
    irrespective of `committed_cost`, success or failure. Demonstrated across
    all four combinations: success at positive cost, success at zero cost,
    failure at positive cost, failure at zero cost.
14. **A decision that executes nothing never increments it** — any STOP, of any
    kind, at any point.

Accounting — inherited criterion 13:

15. **Entry with no pre-loop spend**: `remaining_budget == initial_budget`
    yields `total_spend == 0`.
16. **Entry with valid pre-loop spend**: `remaining_budget < initial_budget`
    yields `total_spend == initial_budget - remaining_budget`.
17. **Entry with `remaining_budget == 0`** is valid, and yields
    `total_spend == initial_budget`.
18. **Entry with `remaining_budget > initial_budget` is refused**, along with
    every other state in §3.2.1's rejection table.
19. **A committed cost exactly equal to the remaining budget is permitted**
    where the economics selected it, and leaves `remaining_budget == 0`.
20. **`committed_cost` never exceeds the candidate's declared cost, nor the
    remaining budget.**
21. **Exact accounting after a successful execution**, and **after a failed
    execution that committed a cost** — both apply the same arithmetic.
22. **A zero-cost execution leaves spend unchanged** and **still increments the
    capability-step count**.
23. **`total_spend + remaining_budget == initial_budget`**, with
    `0 <= total_spend <= initial_budget` and
    `0 <= remaining_budget <= initial_budget`, across every transition.

Failure semantics:

24. **Failure terminates `EXECUTION_FAILURE`**, having consumed the ID,
    incremented the capability-step count, and recorded whatever was committed —
    with no retry.
25. **No execution occurs after any terminal state.**

Neutrality and audit:

26. **Provider metadata cannot influence TASK-006.** Candidates whose external
    metadata differs but whose three economic fields are identical produce
    **identical assessments and an identical selection**. This asserts nothing
    about execution results, evidence, subsequent task states, or whole runs —
    §9a.
27. **Candidate ordering cannot change the winner** — permuted offers, identical
    selections.
28. **The history is non-recursive** and reconstructs every decision and
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

The revenue-pursuit benchmark in `PREREQ-001` §6 must be expressible:

```
baseline  →  onchain intelligence  →  updated state
          →  research               →  updated state
          →  optionally, an independent review
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
  maximum, `committed_cost` driving the accounting, the capability-step count
  rising **once per attempt regardless of cost**, and failure terminating the
  run with no retry.
- Confirm the **ceiling outranks every economic reason** in terminal
  classification, and that `stopped_without_economic_judgement` is read rather
  than reinterpreted — §6.2.
- Confirm the ledger bounds in §3.2.1 are enforced at entry and after every
  transition, and that an out-of-range state is **refused**, not processed.
- Confirm `task_state` is **never read** by this task or by the decision, and
  that no field, branch or helper inspects it — §3.1, §5.4.
- Confirm the history is **non-recursive**: no snapshot contains a history.
- Confirm the already-complete check **precedes** candidate selection on every
  path — §6.1.
- Confirm STOP classification is **read from**
  `Selection.stopped_without_economic_judgement` rather than re-derived — §6.2.
