# TASK-008 — Onchain information as a paid capability, via The Graph

**Status:** Placeholder — **NOT AUTHORIZED**, and not yet specified
**Authorization:** None. This document reserves the work and states its premise; it does not permit implementation.
**Traces to:** [`PREREQ-001`](../docs/PREREQ-001_PRODUCT_DEFINITION.md) §4a
**Bounded by:** [`ARCHITECTURE.md`](../docs/ARCHITECTURE.md) §2.1, §3.5, §6
**Replaces backlog entry:** `BL-15`
**Renumbered:** was TASK-007 when first written (PR #25). Moved to 008 so the run loop could take 007, which is the number the product owner originally proposed for this task
**Supersedes on the active path:** [TASK-003](TASK-003_PROGRAMMABLE_AUTHORITY_VIA_PRIVY.md), deprioritized 2026-09-11

---

## 1. Premise

**The Graph is not part of Radhanite's economic decision engine.** It is one
external capability that Radhanite may choose to buy, when onchain evidence
would change what the task knows.

That distinction is the whole of this task's premise, and getting it wrong is
the way this integration fails.

```
current task state
  → among the candidates on offer, one of them is priced onchain evidence
  → the ordinary economic rule decides
  → buy it, or buy something else, or STOP
```

## 2. The role it plays

A capability backed by The Graph would:

- retrieve **structured onchain data**;
- inspect **wallet, protocol or entity activity** where the task makes that
  relevant;
- return **evidence that changes the current task state** — which is to say, a
  new `current_success_probability` for the next decision.

Radhanite then does what it does with any purchase: decides afterwards whether
that information was worth what it cost, and whether anything further is worth
buying.

**Buying information is a purchase like any other.** It has a price, it may
improve the odds, and it is not exempt from `value > cost` because it happens to
be data rather than judgement.

## 3. What must not happen

> **The Graph must not influence ranking merely because it is The Graph.**

[`TASK-006`](TASK-006_GENERALIZED_CAPABILITY_SELECTION.md) §2.1 keeps provider
and network identity **outside** the selection logic, and this task does not
relax that by a word. A capability backed by a subgraph and one computed locally
must be indistinguishable to the rule: same three fields, same six conditions,
same ranking.

Concretely, none of the following is permitted:

- a field, enum, branch or weighting in the selection path that names a provider;
- a preference, tie-break or bonus that any provider earns by identity;
- a "trusted source" concept, which is provider preference wearing a hat.

If onchain evidence deserves to win, it wins on **price and effect**, through
`net_expected_value`, like everything else. Encoding anything else is a boundary
violation under [`ARCHITECTURE.md`](../docs/ARCHITECTURE.md) §6 items 1–7.

## 4. Where it sits on the path

| | Integration | Role |
|---|---|---|
| 1 | **Hedera / x402** — [TASK-004](TASK-004_AGENTIC_PAYMENTS_VIA_HEDERA_AND_X402.md) | Paid independent judgement |
| 2 | **Circle / Arc** — [TASK-005](TASK-005_BUDGET_IN_REAL_USDC_ON_ARC.md) | Marketplace and payment environment, and research |
| 3 | **The Graph** — this task | Paid onchain information |

Privy is **not** on this path — TASK-003 records why.

## 5. Out of scope, and not authorized

This document is a placeholder. It authorizes nothing, and specifies nothing in
enough detail to be built from.

Explicitly excluded:

- **Any Graph API call**, subgraph, query, endpoint, key or client library.
- **Any change to TASK-006.** The candidate model, the six conditions and the
  ranking are settled and provider-neutral, and stay that way.
- **Candidate discovery** — deciding what is on offer is not this task.
- **The run loop**, and the layer that establishes task state from returned
  evidence.
- **Payment execution** of any kind.
- Every other integration, each of which remains unauthorized on its own terms.

## 6. Decisions still open

None of these is answered here, and all of them must be before implementation.

### 6.1 What is one candidate? ⚠️ **UNRESOLVED**

Is a Graph-backed capability a single candidate, or a family of them — one per
query shape, per entity, per depth of history? The answer determines what a
stable candidate ID even identifies, and `TASK-006` §2.5a makes an offer
single-use by that ID.

### 6.2 Where does the price come from? ⚠️ **UNRESOLVED**

The economic rule requires a cost **before** the purchase, and a strictly
positive one. Query pricing that is only knowable afterwards does not satisfy
`TASK-006` §2.3 as written, and `ARCHITECTURE.md` §4a assumption 1 is the same
problem in its general form.

### 6.3 How does evidence become a probability? ⚠️ **UNRESOLVED**

Returned data has to move `current_success_probability` for the next decision to
mean anything. That translation is a judgement, it belongs to the task-state
layer rather than here, and no authorized task owns that layer yet.

**Until 6.3 has an owner, this task cannot deliver a working loop on its own.**
That is worth stating plainly rather than discovering during a hackathon.
