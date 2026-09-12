# TASK-010 — Circle marketplace and Arc payments adapter

**Status:** Authorized — **implementation on review branch**
**Authorization:** Arko authorized TASK-010 on 2026-09-13 for one thin Circle
Marketplace/Arc payment adapter. This review branch is not merged.
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

## 6. Current implementation boundary

This review branch uses **live Circle Discovery** at
`https://api.circle.com/v2/x402/discovery/resources`. The selected vertical
slice is the live AIsa API CoinGecko Simple Price resource, exposed at an exact
quoted price of `12000` micro-USDC (`0.012` USDC) on Base mainnet with the
`GatewayWalletBatched` scheme. Circle Marketplace Discovery currently did not
establish an Arc Testnet listing for this resource, so the code does not claim
that the live Marketplace path is an Arc Testnet path.

The adapter normalizes Circle descriptors through TASK-008, retains Circle
metadata outside the three-field TASK-006 `Candidate`, and maps the selected
candidate back to its provider descriptor. The executor delegates signing and
settlement to the official `circle services pay` CLI, passes an explicit method,
chain, wallet address, and `--max-amount`, and returns an exact
`ExecutionResult`. The explicit smoke command is
`PYTHONDONTWRITEBYTECODE=1 python3.12 -m radhanite.circle_smoke`; it requires
`CIRCLE_WALLET_ADDRESS`, an installed/authenticated Circle CLI, and explicit
`CIRCLE_SMOKE_ALLOW_MAINNET=1` for the currently selected Base-mainnet offer.
No credentials are committed, and the smoke command is never run by unit tests.

The deterministic suite mocks HTTP and payment calls. A live read-only
Discovery request succeeded during implementation; a payment smoke was not run
because no Circle wallet credentials or CLI were available, and a mainnet
payment is consequential. Arc Testnet Gateway/x402 remains the documented
testnet path when a compatible offer and funded EOA are available; testnet
tokens are not production value.

For the selected exact-payment scheme, a successful response commits the exact
pre-purchase quote. If the official CLI reports that payment was submitted but
the service failed, the same exact quote is recorded as committed; no partial
metered amount is invented. A failure before submission raises a pre-attempt
error and records no spend.

## 7. Open decisions ⚠️ **UNRESOLVED**

Whether discovery is live or a captured snapshot for the benchmark, and what a
partial or metered charge reports as `committed_cost` (TASK-007 §7.1).

**Pricing is no longer open.** TASK-008 §6.2 settles it: Circle Discovery
exposes payment terms before purchase, TASK-008 normalizes the quoted amount
into the candidate cost, and **no payment is made to discover a price**.
Discovery may happen before selection; purchase happens only after it.
