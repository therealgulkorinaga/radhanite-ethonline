# TASK-010 — Circle marketplace and Arc payments adapter

**Status:** Specified — **NOT AUTHORIZED for implementation**
**Authorization:** None. This document specifies the work; it does not permit it.
**Bounded by:** [`ARCHITECTURE.md`](../docs/ARCHITECTURE.md) §2.1, §3.3, §6
**Satisfies:** [TASK-008](TASK-008_CAPABILITY_ACQUISITION.md) as a source, and [TASK-007](TASK-007_CAPABILITY_RUN_LOOP.md) §5.2 as an executor

---

## 1. Purpose

Two functions, kept distinct:

1. **Discovery** — read Circle's marketplace for machine-readable capability
   descriptors and prices, and hand them to TASK-008.
2. **Execution and payment** — invoke a capability Radhanite selected, and settle
   it over x402 or Nanopayments.

> **Circle tells the agent what it can buy and how to pay. Radhanite decides what
> is worth buying.**

## 2. What is a candidate, and what is not

Marketplace services — **Tavily-backed research**, **BlockRun inference and
analysis**, and whatever else the catalogue carries — are **candidate
capabilities**. They are discovered, priced, and offered to the economic rule
like anything else.

**Nothing here is a mandatory workflow step.** Radhanite may evaluate a Circle
service and reject it; a run that buys none of them is a correct run. A demo
that always calls a sponsor's service is demonstrating wiring, and
`PREREQ-001` §6.3 already forbids presenting it as anything else.

## 3. Provider-specific information lives here

This adapter **necessarily knows** endpoints, pricing units, payment rails and
credentials. That is what an adapter is for.

What it must not do is let any of that cross into TASK-006. The boundary is
TASK-008: descriptors in, three-field candidates out, provider identity retained
on this side.

## 4. Out of scope

Deciding what to buy; holding the budget; interpreting results — that is
TASK-009. Radhanite does not reimplement discovery, settlement, custody or a
payment protocol — `ARCHITECTURE.md` §6 items 1–4.

## 5. Truthfulness constraints

- **Arc testnet value is not production value** — §6 item 10.
- **A marketplace purchase is a purchase from the marketplace.** A Tavily-backed
  request is not Radhanite paying Tavily unless that is factually the seller
  relationship — §6 item 11, `ARCHITECTURE.md` §4b.
- Credentials come from the environment and are never committed.

## 6. Open decisions ⚠️ **UNRESOLVED**

Whether discovery is live or a captured snapshot for the benchmark; how quoted
prices map to an exact `Money` cost known before purchase (TASK-008 §6.2); and
what a partial or metered charge reports as `committed_cost` (TASK-007 §7.1).
