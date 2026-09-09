# TASK-004 — Agentic payments via x402, settled on Hedera

**Status:** Specified — **NOT AUTHORIZED**
**Authorization:** None. This document does not permit implementation.
**Traces to:** [`PREREQ-001`](../docs/PREREQ-001_PRODUCT_DEFINITION.md) §2.1
**Bounded by:** [`ARCHITECTURE.md`](../docs/ARCHITECTURE.md) §3.3, §3.4
**Replaces backlog entry:** `BL-04`. (`BL-03` belongs to [TASK-005](TASK-005_BUDGET_IN_REAL_USDC_ON_ARC.md).)
**Depends on:** TASK-003 complete and merged

**Predates the product pivot.** Written under the previous product definition
(inference-expenditure allocation). Preserved as a **proposed specification and
historical record** under [`PREREQ-001`](../docs/PREREQ-001_PRODUCT_DEFINITION.md)
§2.3; its technical decisions are unaltered. **Its place in the dependency chain
is not automatically authorized** under the new direction — see
[`BACKLOG.md`](BACKLOG.md) and [`ARCHITECTURE.md`](../docs/ARCHITECTURE.md) §4a.

---

## 1. Purpose

Let the agent **pay for what it buys, itself**, without a human in the
transaction.

TASK-002 makes the spend real but conventional: an account is billed the ordinary
way. This task makes the agent the payer — it settles its own purchases over
x402, on Hedera, from the wallet TASK-003 gave it.

That is the point Radhanite exists for. An agent that can pay for things needs
something deciding whether each purchase is worth making, and Radhanite is that
thing. Until the agent actually pays, the decision layer is reasoning about
somebody else's money.

## 2. Direction

This task is the **outbound** direction: money going out, Radhanite paying for
what it consumes. `ARCHITECTURE.md §3.4` describes both directions since PR #14;
the inbound one — Radhanite consumable as a paid service — is `BL-04b` and is a
separate feature.

## 3. Scope

- The agent pays for a purchase over **x402**, from its own wallet.
- Payment is settled on **Hedera**.
- The amount paid is the amount the economic rule authorized.
- The run record shows what was paid, to whom, and the settlement reference.

Radhanite must **not** implement a payment protocol, a metering rail, or a
settlement layer (`ARCHITECTURE.md §3.4`). x402 is the protocol; Hedera is the
rail. Radhanite decides *whether* to pay and *how much*.

## 4. The problem this task actually has to solve

**A payment can fail. A decision cannot currently fail.**

TASK-001's loop goes: the ledger permits → the purchase happens → an outcome is
observed. There is no path where the money does not move. Real payments decline,
time out, settle late, or settle for a different amount.

That splits one concept into three the loop does not distinguish:

- **decided to spend** — §2.5 returned Escalate;
- **paid** — settlement succeeded;
- **received what was paid for** — the purchase actually happened.

A failure between any two is a state the loop has never had to represent. A
payment that settles after the run ends is worse: the record says one thing and
the ledger says another.

Nothing here is decided. See §7.

## 5. Out of scope

| Excluded | Note |
|---|---|
| Implementing x402 itself | It is a protocol. Use it. |
| Implementing settlement | Hedera's job. `ARCHITECTURE.md §3.4`. |
| Radhanite as a paid service — the inbound direction | Genuinely separate. If wanted, it is another task. |
| Multi-task or portfolio budgeting | `BL-09`. |
| Speculative trading, holding, or converting value | Radhanite pays for what it buys. It is not a treasury. |

That last row is worth stating: an agent with a wallet and an economic rule is
one short step from something that decides to hold or convert value, and nothing
authorizes that.

## 6. Acceptance criteria

1. The agent pays for a purchase over x402, from its own wallet, with no human
   in the transaction.
2. Payment settles on Hedera and the record carries a verifiable reference.
3. The amount paid equals the amount §2.5 authorized, and any difference is
   detected and recorded rather than absorbed.
4. A failed, declined or timed-out payment is an outcome the loop handles, with
   a defined relationship between *decided*, *paid* and *received*.
5. The budget ceiling holds against what was actually paid.
6. No key appears in the repository, a run record, or a log.
7. The existing suite still runs deterministically without network access.
8. A run record lets a reader confirm, independently, that the money moved as
   recorded.
9. Nothing in §5 appears.
10. Repository tests pass.

Criterion 8 is the one a judge will care about: an economic control layer whose
payments cannot be verified is back to asking for trust.

## 7. Open decisions — product owner input required

1. **Which rail the agent pays on.** ✅ *Superseded — see TASK-005 §7.5, which
   holds the unresolved question of how money on Arc pays for a service on
   Hedera. This task cannot be specified further until that is settled.*
2. **The relationship between decided, paid and received**, and what the loop
   does when they disagree. §4.
3. **What is actually being paid for.** Paying OpenRouter over x402 requires
   OpenRouter to accept x402. If it does not, the demonstrable version is the
   agent paying a machine-payable endpoint that stands in for a service — which
   is honest only if the record says so.
4. **Whether a settled payment can be reversed or refunded**, and what a run
   record says if it is.

Decision 3 is the one most likely to embarrass the project. If the agent is
paying a mock endpoint, that must be stated everywhere the payment is described,
in exactly the way `ARCHITECTURE.md §6` item 8 already requires for simulated
USD.

## 8. Review notes

- Confirm `ARCHITECTURE.md` describes the outbound direction before any code.
- Confirm no payment protocol or settlement logic is reimplemented.
- Confirm the ceiling holds against actual settled amounts.
- Confirm a failed payment is handled rather than assumed away.
- Confirm no key reaches the repository, a record, or a log.
- Confirm nothing presents a mock endpoint or simulated settlement as real. This
  is the `§6` item 8 rule applied to payments.
