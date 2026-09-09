# TASK-005 — The budget denominated in real USDC on Arc

**Status:** Specified — **NOT AUTHORIZED**
**Authorization:** None. This document does not permit implementation.
**Traces to:** [`PREREQ-001`](../docs/PREREQ-001_PRODUCT_DEFINITION.md) §4.2, §2.2
**Bounded by:** [`ARCHITECTURE.md`](../docs/ARCHITECTURE.md) §3.3, §6 item 8
**Replaces backlog entry:** `BL-03`
**Depends on:** TASK-002 and TASK-003 complete and merged
**Blocked by:** §7.5 and §7.6 — two unresolved product decisions

**Predates the product pivot.** Written under the previous product definition
(inference-expenditure allocation). Preserved as a **proposed specification and
historical record** under [`PREREQ-001`](../docs/PREREQ-001_PRODUCT_DEFINITION.md)
§2.3; its technical decisions are unaltered. **Its place in the dependency chain
is not automatically authorized** under the new direction — see
[`BACKLOG.md`](BACKLOG.md) and [`ARCHITECTURE.md`](../docs/ARCHITECTURE.md) §4a.

---

## 1. Purpose

To make the budget **money**.

Today a budget is a decimal number Radhanite keeps in memory and agrees to
respect. `ARCHITECTURE.md §6` item 8 forbids calling it USDC, because it is not:
calling a simulated quantity a currency would misrepresent the system. This task
is what earns the right to drop that prohibition.

After it, `budget = 2.00` means two dollars of USDC that exist, on a chain, in an
account the agent holds — and every figure in a run record refers to money that
was really there.

## 2. Why Arc specifically

**Arc settles in USDC and charges gas in USDC.**

That is not a convenience. Radhanite's entire premise is weighing what a purchase
costs against what an outcome is worth, and a chain that charges fees in a
different token would split every cost in two: the price of the thing, and the
price of paying for the thing, in units that need converting before they can be
compared. "What did this task cost" would stop having a single answer.

On Arc the budget, the spend, and the fee are one unit. `Money` needs no second
currency, the ledger needs no conversion, and a run record's totals are directly
comparable to the task value the user declared.

This is the clearest case in the project of a chain being chosen for a property
rather than for a logo.

## 3. Scope

- The agent's budget is **USDC held on Arc**, in the wallet TASK-003 established.
- A run is funded from that balance and cannot exceed it.
- Spend recorded in a run record corresponds to USDC that actually moved.
- The prohibition in `ARCHITECTURE.md §6` item 8 is lifted **only** for values
  that are genuinely USDC, and remains in force for anything simulated.

Radhanite must **not** implement token accounting, transfers, or settlement
(`ARCHITECTURE.md §3.3`). Circle's chain and the wallet do that. Radhanite
decides how much to spend and records what was spent.

## 4. The problem this task actually has to solve

**A balance is not a budget, and Radhanite has only ever had budgets.**

`Task.budget` is a number the caller supplies. A USDC balance is a fact about the
world that changes without asking: it can be topped up, drawn down by another
run, or spent by something else entirely holding the same wallet.

Three things follow, and none is currently handled:

1. **A budget may exceed the balance.** A task declaring a $2.00 budget against
   $0.40 of USDC is not a task that can be attempted as specified. Is that an
   error, or a run that proceeds against the smaller figure?
2. **The balance can change mid-run.** Radhanite's ledger is computed once at the
   start. If the true balance falls below it, the ceiling that criterion 12
   guarantees is guaranteeing the wrong number.
3. **Decimals must line up exactly.** USDC has six decimal places. `Money` is
   arbitrary-precision and refuses to round. A cost of `$0.0000015` is
   representable in `Money` and **not** in USDC, so something must decide what
   happens — and silently rounding it would be precisely the defect the money
   type exists to prevent.

The third is the one most likely to be discovered late and hurt.

## 5. Out of scope

| Excluded | Note |
|---|---|
| Token accounting, transfers, settlement | Circle's job. `ARCHITECTURE.md §3.3`. |
| The wallet and authority over it | TASK-003. This task denominates the budget; that one establishes who may spend it. |
| Paying over x402 | TASK-004. |
| Holding, converting, bridging, or trading value | Radhanite spends its budget. It is not a treasury, and nothing authorizes it to become one. |
| Any currency other than USDC | One unit. The whole argument for Arc is that there is only one. |

## 6. Acceptance criteria

1. A run's budget is USDC held on Arc, and the run cannot spend more than the
   balance allows.
2. Spend in a run record corresponds to USDC that actually moved, verifiable
   independently on the chain.
3. The decimal mismatch is handled explicitly per §7.3 — never by silent
   rounding, and demonstrated by a test with a cost finer than USDC can express.
4. A budget larger than the available balance is handled per §7.1, not ignored.
5. A balance that changes mid-run is handled per §7.2, not assumed static.
6. The budget ceiling holds against real balance, not the declared figure alone.
7. Anything still simulated is still **not** described as USDC — `§6` item 8
   remains in force for it.
8. No key appears in the repository, a run record, or a log.
9. The existing suite still runs deterministically without network access.
10. Nothing in §5 appears.
11. Repository tests pass.

Criterion 7 is the one to watch. This task lifts a prohibition for real values,
and the temptation afterwards is to relabel everything as USDC because most of it
now is. Anything simulated stays labelled as simulated.

## 7. Open decisions — product owner input required

1. **A budget exceeding the balance.** Refuse the task, or run against the
   smaller of the two? Refusing is honest; proceeding is more useful. Either is
   defensible and neither is specified.
2. **A balance changing mid-run.** Re-read it before each purchase, or fix it at
   the start and accept that the ceiling may be guaranteeing a stale number?
   Re-reading is correct and costs a call per purchase.
3. **Costs finer than six decimals.** Inference is priced below a millionth of a
   dollar per token. Options: round up at the point of payment and record both
   figures; accumulate exact costs and settle periodically; or refuse to price a
   strategy at a precision USDC cannot pay. **This decision cannot be deferred**
   — it determines whether a run record's total is the sum of what was decided
   or the sum of what was paid, and those will differ.
4. **Which Arc network**, and the verified chain ID, RPC endpoint, explorer and
   faucet. These must come from Circle's own documentation. Values circulated
   secondhand are not good enough to build on and have not been confirmed.

### 7.5 UNRESOLVED — what the Arc balance actually buys

**This task cannot be implemented until this is settled, and it may block
TASK-004 as well.**

This task requires recorded spend to correspond to USDC that moved on Arc. It
defines no recipient and no purchase operation. The only task that has the agent
pay for something is TASK-004 — and that settles on **Hedera**, a different
chain. Bridging and converting are excluded by §5.

So the same money cannot presently be both the budget on Arc and the payment on
Hedera. As specified, criterion 2 is unsatisfiable: there is nothing for the Arc
balance to be spent on.

Three routes, none chosen:

1. **Spend the Arc balance on Arc.** Requires something on Arc worth buying, and
   leaves the Hedera work needing its own funding.
2. **Move TASK-004's settlement to Arc.** Coherent, and it removes Hedera as the
   payment rail — which matters if Hedera is being targeted for its own sake.
3. **Authorize cross-chain movement explicitly.** Currently excluded by §5, and
   would be a substantial addition rather than a clarification.

A fourth possibility is two balances — one per chain — which makes "the budget"
a thing with two locations and needs its own thinking.

**This is a product decision and the implementing agent must not make it.**

### 7.6 UNRESOLVED — transaction fees against the budget

**Identified by review as the fourth broken assumption, which §4 missed.**

§2 argues that USDC-denominated gas gives cost a single unit of account. That is
true and it is not sufficient. Nothing here says:

- whether a transaction fee counts against the **task budget**;
- how enough is reserved for the fee **before** a purchase is authorized;
- how an estimated fee is reconciled against the actual one.

The failure is concrete. A run can authorize spending its entire remaining
budget, and then need a further amount in USDC to execute the transaction at
all. Either the wallet cannot cover it, or the total spent on the task exceeds
the ceiling that TASK-001 criterion 12 and PREREQ-001 §4.2 make absolute.

**Using one currency makes the comparison possible; it does not enforce the
ceiling.** An acceptance criterion covering *purchase amount plus fee* is
required, and the rule it tests has to be decided first.

**This is a product decision and the implementing agent must not make it.**

## 8. Review notes

- Confirm no token accounting, transfer, or settlement logic is reimplemented.
- Confirm the ceiling holds against the real balance and not only the declared
  budget.
- Confirm the decimal mismatch is handled explicitly and never by silent
  rounding — this is the `CODEX-PR006-03` class of defect applied to a chain.
- Confirm nothing simulated is described as USDC anywhere, including in the
  demonstration output and the documentation.
- Confirm chain parameters came from Circle's documentation rather than a
  secondhand source.
- Confirm §7.5 and §7.6 were settled by the product owner before any code, and
  that the implementation follows what was settled rather than a reading of it.
- Confirm the budget ceiling holds against **purchase plus transaction fee**,
  not the purchase alone.
