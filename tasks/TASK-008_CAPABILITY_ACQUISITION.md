# TASK-008 — Capability acquisition and candidate generation

**Status:** Specified — **NOT AUTHORIZED for implementation**
**Authorization:** None. This document specifies the work; it does not permit it.
**Traces to:** [`PREREQ-001`](../docs/PREREQ-001_PRODUCT_DEFINITION.md) §4a
**Bounded by:** [`ARCHITECTURE.md`](../docs/ARCHITECTURE.md) §2.1, §6
**Satisfies:** [TASK-007](TASK-007_CAPABILITY_RUN_LOOP.md) §5.1, the candidate-source boundary

---

## 1. Purpose

> Given the current task state and whatever external capability descriptors are
> available, produce **provider-neutral candidates** that TASK-006 can evaluate.

TASK-007 §5.1 names a boundary and deliberately does not fill it. **This is the
thing that fills it.**

## 2. What it does

It **normalizes**. An external source describes a capability in its own terms —
a name, an endpoint, a price in some unit, whatever metadata it chooses. TASK-006
accepts exactly three fields. This task is the translation, and the place where
provider identity stops.

| Comes in | Goes out |
|---|---|
| A capability descriptor from some source | A `Candidate` — stable ID, cost, expected post-action probability |
| Provider, endpoint, invocation metadata | **Retained here**, never passed to the decision |
| The current `task_state` | Used to decide what to offer; never interpreted economically |

## 3. What it may know, and what TASK-006 may not

**TASK-008 may know**: the capability's description, its source or provider, its
price, and whatever invocation metadata executing it will later require.

**TASK-006 remains provider-neutral.** That is not softened by this task
existing. The candidate crossing the boundary carries the three fields of
TASK-006 §2.2 and nothing else, and a capability's source must never be
recoverable from what the decision sees.

This is the asymmetry the architecture depends on: **acquisition knows who is
selling; the decision does not.**

## 4. Expected post-action probabilities

For the current benchmark these remain **declared fixtures**, exactly as
TASK-006 §9 requires. Nothing here estimates, learns or predicts an uplift.

Learning them is `BL-05`/`BL-06` and is unauthorized. A task that quietly began
predicting uplift would be the most consequential unauthorized change this
repository could make, because every downstream figure would inherit it.

## 5. Out of scope

- **Executing** anything — TASK-007 §5.2 and the adapters.
- **Interpreting evidence** or updating probabilities — TASK-009.
- **Any specific source.** Circle is TASK-010, The Graph TASK-011, Hedera
  TASK-012. This task defines the shape they normalize into.
- Learned or predicted uplift — §4.

## 6. Open decisions

### 6.1 Candidate identity across iterations ⚠️ **UNRESOLVED**

TASK-006 §2.5a makes an offer single-use by stable ID, and TASK-007 relies on
that. If the same underlying service is re-offered after the state changes, does
it get a **new** ID?

It must, or it can never be bought twice — but then IDs must be stable *within*
an iteration while differing *across* them, and what makes two offers "the same
service" is a question this task would have to answer without acquiring a notion
of capability type, which TASK-006 §2.5a forbids.

### 6.2 Pricing that is not known in advance ⚠️ **UNRESOLVED**

TASK-006 §2.3 requires a strictly positive cost **before** the purchase. A
source quoting per-token or per-result pricing cannot supply one. Either the
candidate carries a bound the executor may not exceed — which TASK-007 §7.1
already anticipates — or such capabilities cannot be offered at all.
