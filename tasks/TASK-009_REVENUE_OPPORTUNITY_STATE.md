# TASK-009 — Revenue opportunity state and evaluation

**Status:** Authorized — **implementation in review**
**Authorization:** Arko authorized TASK-009 implementation on 2026-09-12.
**Traces to:** [`PREREQ-001`](../docs/PREREQ-001_PRODUCT_DEFINITION.md) §6
**Bounded by:** [`ARCHITECTURE.md`](../docs/ARCHITECTURE.md) §2.1, §6
**Satisfies:** [TASK-007](TASK-007_CAPABILITY_RUN_LOOP.md) §5.3, the task-state updater boundary

---

## 1. Purpose

**This is where the benchmark's reasoning lives, and it is the only place it may
live.**

TASK-007 §5.3 names a boundary and says outright that the domain judgement
behind it belongs to a separate task. This is that task: given the previous
opportunity state and an execution result, produce the new state, the new
declared success probability, and whether the opportunity is resolved.

## 2. Why it is separate

The engine must not know it is pursuing revenue. TASK-006 decides what is worth
buying for *any* task; TASK-007 runs *any* loop. Putting opportunity reasoning
into either would make the product a sales tool with an economic layer attached,
rather than an economic layer with a sales benchmark on top.

**Everything specific to the benchmark stops here.**

## 3. The state it carries

TASK-007 holds this as opaque `task_state` and never reads inside it. Its shape
is this task's business:

| Field | |
|---|---|
| Opportunity identity | Which account or prospect is being pursued |
| Potential contract value | The revenue at stake — distinct from `task_value` as an input |
| Current evidence | What has been learned, and from which capability |
| Unresolved questions | What is still unknown and might be worth buying an answer to |
| Current success probability | The declared figure the economic rule measures against |
| Completion state | Whether the opportunity is resolved, and how |

## 4. What it decides, and what it must not

**It decides**: how evidence changes what is known, what the resulting success
probability is, and whether the opportunity is resolved.

**It must not**: decide whether a capability was worth its price, rank
candidates, hold a budget, or know what anything cost. Those are TASK-006's and
TASK-007's, and an updater that consulted price would be making an economic
judgement in the one place nobody is reviewing for it.

## 5. Probabilities remain declared

For the current benchmark, the probability this task returns is a **declared
benchmark figure**, not a measurement or a prediction — TASK-006 §9,
`ARCHITECTURE.md` §6 item 12.

It will be tempting to describe this task as "estimating" a probability from
evidence. **It does not.** It applies declared rules to produce a declared
figure, and any document saying otherwise is wrong.

## 6. Out of scope

Discovering or executing capabilities; anything about budget, price or
selection; and every provider — Circle, The Graph and Hedera reach this task as
*results*, through TASK-007, never directly.

## 7. Resolved benchmark fixture decision

The implementation uses two declared, deterministic transitions for the
hackathon fixture:

| Evidence outcome key | Required prior probability | New declared probability | Resolved question |
|---|---:|---:|---|
| `positive_market_signal` | `0.08` | `0.14` | `market_signal` |
| `positive_commercial_fit` | `0.14` | `0.17` | `commercial_fit` |

The probabilities are fixture constants. They are not estimates, predictions,
learned scores, or language-model outputs. The updater rejects an outcome key at
an incompatible prior probability, so transitions cannot be applied out of
sequence.

## 8. Implemented boundary

`radhanite/revenue.py` supplies the minimum benchmark domain layer:

- `RevenueOpportunityState` is an immutable mapping containing the opportunity
  identity, description, potential contract value, immutable evidence tuple,
  unresolved questions, declared probability, completion condition, and terminal
  benchmark outcome.
- `BenchmarkEvidence` is an immutable mapping containing a capability key,
  evidence type, immutable facts, optional opaque source reference, and one
  declared outcome key. It contains no provider requirement and never reaches
  TASK-006.
- `initialize_benchmark_run(...)` creates a TASK-007 `RunState`. An incomplete
  opportunity receives `RUNNING`; an explicitly already-complete opportunity
  receives authoritative `TASK_COMPLETE` before the generic loop is called.
- `RevenueOpportunityUpdater.update(...)` accepts only exact immutable benchmark
  state and a successful `ExecutionResult`. It returns TASK-007's exact
  `TaskStateUpdate` with the next immutable state, declared probability, and
  completion verdict. It does not read candidate price or select capabilities.

The implementation includes one deterministic end-to-end fixture path: a market
signal changes `0.08` to `0.14`, and a commercial-fit result changes `0.14` to
`0.17` and resolves the benchmark's two required questions. TASK-006 still makes
both capability decisions from the updated probability and candidate economics;
the updater does not encode candidate order.
