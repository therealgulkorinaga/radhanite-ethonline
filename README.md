# Radhanite

**An economic control layer for autonomous AI agents.**

Radhanite is being built for ETHOnline 2026.

**TASK-001 is implemented and merged.** It remains the active CLI/runtime path:
the deterministic **two-tier economic kernel** makes an opening attempt and one
optional escalation, with declared costs and declared success probabilities.
The full suite currently passes **769 tests on Python 3.12** on the TASK-015 branch.

The generalized capability-selection kernel in
[TASK-006](tasks/TASK-006_GENERALIZED_CAPABILITY_SELECTION.md) is implemented and
closed. TASK-007 PR A and PR B provide the immutable run-state and
one-execution foundations; the merged final loop adds the provider-neutral
candidate-source and task-state-updater boundaries, terminal classification,
and generic repeated run loop. TASK-008 PR A provides the
descriptor-to-candidate acquisition/catalog boundary. TASK-008 source-specific
candidate generation and external adapters remain unimplemented. TASK-009 adds
only the declared revenue-benchmark state, evidence contract, initializer, and
updater. TASK-010 adds the historical Circle Discovery/Base CLI adapter and the
authorized Arc Testnet path. The primary Arc path uses Circle's official EOA
Developer-Controlled Wallet SDK and x402 batching SDK, with exact pre-selection
pricing, Gateway balance preparation, Arc-only network binding, and TASK-009
evidence handoff. Circle Discovery currently exposes no Arc offer, so the Arc
smoke uses a separately identified demo seller derived from Circle's official
Arc nanopayments example; it is never represented as a Marketplace listing.
The live Arc smoke is blocked in this checkout until credentials, an EOA wallet,
testnet USDC, Gateway balance, and a seller URL are supplied. The distinction
between what runs, what is implemented and merged, and what is authorized to be
built remains deliberate throughout this repository.

---

## What Radhanite is

Today, using an AI agent means writing a prompt and hoping the result is worth
what it cost. Radhanite changes the unit of instruction.

A user gives Radhanite a **business task, a budget, a task value, constraints,
and a measurable success condition** — not a prompt. Radhanite then:

1. selects a capability to acquire,
2. allocates expenditure across the task,
3. evaluates results against the success condition, and
4. decides whether buying more is economically justified.

The last point is the product:

> **Payment infrastructure answers "How can the machine pay?"**
> **Radhanite answers "Should the machine pay, and what is worth buying?"**

Radhanite is not another agent framework, and not a payment rail. It is the
layer above the rail that decides **what is worth buying, when to buy more, and
when to stop paying**.

> Give Radhanite a task, what success is worth, how much it may spend, and the
> constraints it must obey.

Budget and task value are separate inputs and neither is derived from the other.
A budget alone answers "may I afford this?" — only value answers "is it worth
buying?". That distinction is what makes the decision economic rather than a
spending limit.

The full statement of the product is in
[`docs/PREREQ-001_PRODUCT_DEFINITION.md`](docs/PREREQ-001_PRODUCT_DEFINITION.md).

## ETHOnline benchmark

**Autonomous revenue opportunity pursuit** — an agent pursuing a deal it could
win, deciding what evidence and judgement are worth buying on the way.

| | |
|---|---|
| **Opportunity** | A $50,000 crypto-native infrastructure contract |
| **Operating budget** | $250 |
| **Available** | Research, onchain intelligence, specialist analysis, independent review — each priced, each optional |
| **The question** | What should it spend next, if anything, to raise the probability of winning? |

A large opportunity does not justify spending badly. The benchmark is built so
that **poor execution strategy destroys margin even when the opportunity is
large** — and unused budget is retained margin, not a shortfall.

Circle/Arc supplies discovery and payment; The Graph and Hedera are capabilities
the agent may buy. **Radhanite decides what is worth buying.** TASK-010 is the
current authorized Circle boundary; The Graph, Hedera, and the remaining
payment/budget integrations are not authorized. The capability order is not
hard-coded: a run that buys nothing is a correct run. See
[`docs/PREREQ-001_PRODUCT_DEFINITION.md`](docs/PREREQ-001_PRODUCT_DEFINITION.md)
§6.

## Repository status

| Item | Status |
|---|---|
| Governance and planning scaffolding | Present |
| Product code | **Present** — TASK-001’s active runtime plus the TASK-006 kernel, TASK-007 state/execution/final-loop foundations, and TASK-008 PR A acquisition/catalog boundary |
| TASK-006 | **Implemented and closed.** All 22 acceptance criteria met |
| Tests | **769 passing** on Python 3.12 |
| Language | Python 3.12 standard-library core; opt-in Node.js 22 Arc SDK path |
| Capability selection engine | **Implemented and closed** — [TASK-006](tasks/TASK-006_GENERALIZED_CAPABILITY_SELECTION.md) |
| TASK-007 run loop | **Implemented and merged** — state model, executor/result boundary, injected candidate source/updater, terminal classification, immutable history, and repeated orchestration; provider-specific integrations remain incomplete |
| TASK-008 acquisition | **PR A implemented** — normalization/catalog boundary; source-specific generation and adapters remain incomplete |
| TASK-009 benchmark reasoning | **Implemented and merged** — immutable opportunity state, declared evidence transitions, benchmark initializer, and TASK-007 updater; provider adapters remain incomplete |
| TASK-010 Circle adapter | **Implemented and merged in PR #37** — historical Base Discovery/CLI corrections plus the authorized Arc Testnet EOA Developer-Controlled Wallet + x402/Gateway boundary; live Arc payment remains unverified until the explicit smoke is configured |
| Benchmark assembly and remaining adapters | **Specified, not implemented** — TASK-011 … TASK-014 |
| External integrations (Circle Discovery/Gateway and Arc Testnet x402) | **TASK-010 merged; TASK-015 is the authorized Arc execution follow-on; other integrations not authorized** |
| Privy | **Deprioritized** — superseded on the active path ([TASK-003](tasks/TASK-003_PROGRAMMABLE_AUTHORITY_VIA_PRIVY.md)) |

## Running the tests

```
python3.12 -m unittest discover -q
```

Python 3.12 specifically — `pyproject.toml` pins `>=3.12,<3.13` and a test
asserts the running version, so the suite fails by design on anything else.
There are no Python package dependencies or build backend; the core suite is run
directly from the source tree. The opt-in Arc smoke additionally requires
`npm install` in the repository root to install the pinned official Circle SDK
packages.

### TASK-010 Circle smoke

The deterministic suite never needs Circle credentials. After installing and
authenticating the official Circle CLI, an explicit smoke may be run with:

```text
PYTHONDONTWRITEBYTECODE=1 python3.12 -m radhanite.circle_smoke
```

It requires `CIRCLE_WALLET_ADDRESS`. The payment chain is derived from the
selected offer's supported network (`eip155:8453` maps to `BASE`); any explicit
override must match exactly. Because the current live selected Marketplace offer
is Base mainnet, the command refuses to pay unless
`CIRCLE_SMOKE_ALLOW_MAINNET=1` is explicitly set. The current sandbox had no
Circle CLI or wallet credentials, so live Discovery was checked separately but
no payment was attempted. Successful and definitely submitted CLI responses
must contain matching structured payment metadata. A possibly submitted
response without an exact amount aborts with an unresolved-commitment error
rather than inventing spend. No secret is committed or printed.

### TASK-010 Arc Testnet smoke

The primary hackathon payment path is an explicit opt-in command. Start the
minimal demo seller derived from Circle's official Arc nanopayments example with
`CIRCLE_ARC_SELLER_ADDRESS` set:

```text
CIRCLE_ARC_SELLER_ADDRESS=0x... node scripts/arc_demo_seller.mjs
```

Then set `RADHANITE_ARC_RESOURCE` and `RADHANITE_ARC_PRICE`, plus the
pre-provisioned `CIRCLE_ARC_WALLET_ID` and matching `CIRCLE_ARC_WALLET_ADDRESS`,
then run:

```text
npm install
PYTHONDONTWRITEBYTECODE=1 python3.12 -m radhanite.arc_smoke
```

The Arc path requires `CIRCLE_API_KEY`, `CIRCLE_ENTITY_SECRET`,
`CIRCLE_ARC_WALLET_ID`, `CIRCLE_ARC_WALLET_ADDRESS`, a pre-provisioned EOA
Developer-Controlled Wallet on `ARC-TESTNET`, testnet USDC from the Circle
Faucet, and a pre-funded Gateway balance. The helper verifies wallet ID/address
correlation and performs only a read-only Gateway balance check; it never
creates, funds, approves, or deposits. The command performs no Base fallback
and reports the exact blocker if any setup is missing. Arc testnet USDC is
testnet value, not production value.

## Repository layout

```
README.md                  This file
docs/                      Product definition, architecture, rules, governance
  PREREQ-001_PRODUCT_DEFINITION.md   What Radhanite is and why
  ARCHITECTURE.md                    System boundaries and ownership
  HACKATHON_RULES.md                 ETHOnline constraints we build under
  AI_BUILD_GOVERNANCE.md             How AI agents are permitted to build here
radhanite/                 The economic kernel and generalized foundations
scripts/                   Explicit opt-in Circle/Arc smoke and demo-seller helpers
tests/                     The test suite — 769 tests
tasks/                     Authorized work, one file per task
  TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md   Implemented and merged
  TASK-006                                  Kernel implemented and closed
  TASK-007                                  Final generic loop implemented and merged; provider-neutral
  TASK-008                                  PR A acquisition/catalog boundary implemented
  TASK-009                                  Revenue opportunity state/updater implemented and merged
  TASK-010                                  Circle Discovery/Gateway and Arc adapter merged
  TASK-002 .. TASK-005, TASK-011 .. TASK-014 Proposed or specified, not authorized
  BACKLOG.md                                Unauthorized future placeholders
prompts/                   Preserved AI prompts that caused repository changes
site/                      The public ETHOnline progress page (§3.2)
```

## How work happens here

Radhanite is built by AI agents under human authorization. The rules are not
advisory:

- A **human product owner** authorizes tasks and performs all merges.
- **Manus** implements only tasks that have been explicitly authorized.
- Every implementation step carries the bold textual attribution
  **Implementation agent: Manus.**
- **Codex** independently reviews implementations against the specification.
- Future scope is never silently implemented. If it is not in an authorized
  task, it does not get built.

See [`docs/AI_BUILD_GOVERNANCE.md`](docs/AI_BUILD_GOVERNANCE.md) for the full
process, and [`prompts/README.md`](prompts/README.md) for how prompts are
preserved.

## Hackathon constraints

This project starts from scratch, uses version control from the first commit,
commits frequently and meaningfully, remains public, and is open source. Details
in [`docs/HACKATHON_RULES.md`](docs/HACKATHON_RULES.md).

## License

MIT. See [`LICENSE`](LICENSE). The project is open source, as required by
ETHOnline.
