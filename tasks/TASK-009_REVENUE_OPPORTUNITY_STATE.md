# TASK-009 — Revenue opportunity state and evaluation

**Status:** Specified — **NOT AUTHORIZED for implementation**
**Authorization:** None. This document specifies the work; it does not permit it.
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

## 7. Open decision ⚠️ **UNRESOLVED**

**How does evidence become a probability?** Declared rules keep it honest but
make the benchmark's realism depend on how those rules were chosen. This is the
question recorded as unresolved in TASK-011 §6.3 and TASK-007 §5.3, and it is
now this task's to answer — but it is not answered here.
