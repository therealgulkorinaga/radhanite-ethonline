# TASK-013 — The revenue-agent benchmark

**Status:** Specified — **NOT AUTHORIZED for implementation**
**Authorization:** None. This document specifies the work; it does not permit it.
**Traces to:** [`PREREQ-001`](../docs/PREREQ-001_PRODUCT_DEFINITION.md) §6
**Depends on:** TASK-007 through TASK-012

---

## 1. Purpose

Assemble the generic engine and the real adapters into the ETHOnline benchmark:
**a crypto-native agent pursuing a high-value contract on a bounded operating
budget.**

```
Opportunity        a $50,000 crypto-native infrastructure contract
Operating budget   $250
Available          research, onchain intelligence, specialist analysis,
                   independent review — each priced
Question           what should it spend next, if anything, to increase the
                   probability of winning?
```

## 2. What the benchmark must prove

**That poor execution strategy destroys margin even when the opportunity is
large.** A $50,000 contract does not justify spending $250 badly, and an agent
that buys everything available has not made a single economic decision.

The demonstration is not that Radhanite wins the deal. It is that **spend
tracked the opportunity** — and that unused budget is retained margin, not
failure.

## 3. Scenarios — the order must differ

At least four, on the **same engine**, differing only in evidence and state:

| Scenario | Shape |
|---|---|
| **Onchain first** | Cheap onchain signal is decisive; buy it, then stop |
| **Research first** | The opportunity is off-chain; research earns its price before anything else |
| **Deep pursuit** | Several capabilities in sequence as the probability climbs |
| **Abandon cheaply** | Early evidence is discouraging; stop having spent almost nothing |

**The capability order is not hard-coded anywhere.** Different evidence produces
a different sequence through identical code — that is the whole claim, and a
benchmark that always produces the same order would falsify it.

**Abandoning cheaply is a success**, per `PREREQ-001` §5.4. A scenario set
without it would be demonstrating enthusiasm rather than economics.

## 4. Out of scope

Any change to the engine to make a scenario work. If a scenario cannot be
expressed, that is a finding about the specification, not a licence to special-case
it.

## 5. Truthfulness

Probabilities and uplifts are **declared benchmark fixtures** — TASK-006 §9.
Nothing here may present them as learned, measured or predicted, and the
benchmark must say which figures are declared wherever it reports one.
