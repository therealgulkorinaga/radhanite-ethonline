# TASK-012 — Hedera independent review capability

**Status:** Specified — **NOT AUTHORIZED for implementation**
**Authorization:** None. This document specifies the work; it does not permit it.
**Bounded by:** [`ARCHITECTURE.md`](../docs/ARCHITECTURE.md) §2.1, §3.4, §6
**Satisfies:** [TASK-007](TASK-007_CAPABILITY_RUN_LOOP.md) §5.2 as an executor, for one capability

---

## 1. Purpose

Expose **one** paid capability — an independent second opinion — execute it when
Radhanite selects it, and return a structured result to
[TASK-009](TASK-009_REVENUE_OPPORTUNITY_STATE.md).

**One capability. Not a marketplace.** Discovery across many services is
TASK-010's; this is a single specialist the agent may choose to consult.

## 2. Independent Opportunity Review

| In | Out |
|---|---|
| Current opportunity state | Support for, or challenge to, the current assessment |
| Evidence gathered so far | Material signal that is missing |
| Unresolved questions | A recommended next investigation |
| Current strategy | A structured second opinion |

The service may be **x402-gated on Hedera**. Radhanite decides whether buying
that opinion is economically justified — a second opinion has a price and a
declared effect on the odds, and it competes with everything else on offer.

**Being a second opinion earns it no preference.** It wins on net expected value
or it does not win.

## 3. Boundaries

The result goes to TASK-009, which decides what it means. **It never reaches the
economic decision directly** — a review that could adjust its own eligibility
would be marking its own homework.

Radhanite implements no payment protocol and no metering rail. x402 is the
protocol; Hedera is the rail — `ARCHITECTURE.md` §3.4.

## 4. Out of scope

A second marketplace; capability discovery; interpreting the opinion;
any influence on selection.

## 5. Truthfulness constraints

Hedera x402 tooling is **testnet**, and testnet value is a test fixture that
happens to be on-chain — §6 item 10. Hedera and Arc/Circle are **independent
environments**; no bridge is built or needed, and one task budget sits above both
— `ARCHITECTURE.md` §4b.

## 6. Open decision ⚠️ **UNRESOLVED**

What the service actually costs, and whether that price is known before the
call — TASK-006 §2.3 requires it to be.
