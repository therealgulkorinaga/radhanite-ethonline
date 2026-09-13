# 010 — TASK-010 Arc wallet and x402 phase

**Date:** 2026-09-13
**Agent:** Manus
**Authority:** Arko authorization on existing PR #37
**Resulted in:** Arc Testnet EOA Developer-Controlled Wallet, Gateway deposit, x402 payment helper, demo seller, smoke command, and critical boundary tests.

## Prompt

Implementation agent: Manus.

AUTHORIZE TASK-010 ARC PHASE — CIRCLE WALLET + X402 + ARC TESTNET.

Continue on existing PR:

#37 — TASK-010

Current reviewed head:
cc3a07ee3a43485c5364083ecd355ed8d374b10c

Do not merge.

Human product owner / merge authority: Arko.

Independent reviewer: Codex.

STATUS TO PRESERVE

The existing Circle/Base discovery/payment adapter corrections are now reviewed and approved.

Preserve:

structured payment accounting
unresolved-commitment handling
exact atomic amount conversion
USDC asset validation
chain/network binding
live read-only Circle Discovery
TASK-006/TASK-007/TASK-008/TASK-009 boundaries

Do not regress these.

NEW AUTHORIZED GOAL

Implement the primary hackathon payment path on Arc testnet.

Target flow:

Circle Marketplace / capability source
→ exact priced offer
→ TASK-008 Candidate
→ TASK-006 economic selection
→ TASK-007 execution
→ Circle-controlled wallet
→ x402 payment
→ Arc testnet settlement
→ ExecutionResult
→ TASK-009 evidence/state update

Base mainnet is not the primary demo execution path.

FIRST: CHOOSE THE OFFICIAL CIRCLE WALLET PATH

Inspect current official Circle material and determine which path is actually supported for Arc testnet:

Circle Agent Wallet
Circle Developer-Controlled Wallet

Prefer the shortest official route to a real Arc x402 payment.

If Circle’s official Arc+x402 example uses a Developer-Controlled Wallet and that path is more direct, use it.

Do not force the current CLI Agent Wallet implementation onto Arc if that is not the official supported path.

Record:

chosen wallet model
why
official reference used
required credentials
required setup
ARC NETWORK CONTRACT

Determine from official Circle/Arc sources:

Arc testnet network identifier
Circle wallet blockchain identifier
Arc testnet USDC asset
x402 payment requirement shape
how settlement is verified

Do not invent these values.

Encode only the actual supported Arc testnet path.

DISCOVERY / SERVICE SOURCE

Check whether Circle Discovery currently exposes a usable Arc-testnet paid service.

If yes

Use:

Circle Discovery
→ exact Arc offer
→ Radhanite selection
→ Arc x402 payment.

If no

Do not fall back to Base.

Use one truthful Arc-testnet x402 service from an official Circle example/reference.

If necessary, use a minimal demo seller derived directly from Circle’s official Arc x402 example.

Document clearly:

Circle Discovery was used for capability-marketplace evidence
Arc payment used a separate official/demo Arc x402 seller

Do not pretend the seller came from Circle Marketplace if it did not.

CIRCLE WALLET

The wallet must be programmatically usable by the agent.

If using Developer-Controlled Wallets:

use Circle’s official SDK/API flow
credentials from environment only
no entity secret/API key committed
no long-lived secret printed

If using Agent Wallet:

use the official supported Arc-compatible flow
no assumptions from the Base CLI path
Radhanite vs WALLET CONTROLS

Preserve the product distinction:

Radhanite budget
= economic decision rule.

Circle wallet controls
= execution/custody safety layer.

The wallet must not decide what is economically worthwhile.

TASK-006 remains authoritative on whether the purchase happens.

X402 EXECUTION

The selected capability should execute only after TASK-006 selection.

Required:

exact price known pre-selection
exact authorization ceiling
no payment for non-selected capability
x402 request signed/authorized through Circle wallet
Arc testnet settlement
exact committed testnet-USDC amount captured
payment/transaction reference retained
TASK-009 HANDOFF

Convert the successful capability result into the existing TASK-009 evidence envelope.

Do not:

update probability inside Circle adapter
mark task complete inside Circle adapter
select next capability inside Circle adapter

TASK-009 interprets evidence.

TASK-006 decides what to buy next.

LIVE ARC SMOKE — REQUIRED

Add an explicit opt-in live smoke command.

It should demonstrate:

Arc wallet identified/created
wallet has sufficient Arc testnet USDC
exact capability price known before selection
TASK-006 selects capability
Circle wallet executes x402 payment
payment settles on Arc testnet
payment/transaction reference printed
actual committed testnet-USDC printed
capability result returned
TASK-009 updates state/probability

Never print secrets.

HUMAN BLOCKER PROTOCOL

If a human action is required, stop at that exact blocker and report:

exact missing credential/setup
official setup step
environment variable name
wallet address if safe to disclose
whether faucet/testnet funding is required
exact amount needed
whether code/tests are otherwise ready

Do not silently route around the blocker.

Do not fall back to Base.

TESTS

Keep all 758 current tests green.

Add only critical Arc tests:

Arc testnet network/payment requirement accepted
Base path cannot masquerade as Arc
wallet network matches selected Arc offer
wrong network rejected before signing
Arc testnet USDC asset validated
exact amount preserved
non-selected capability never paid
selected capability paid only after TASK-006
successful Arc payment records exact committed cost
transaction/payment reference retained
TASK-009 consumes Arc execution evidence
next TASK-006 decision sees updated probability

Mock live APIs in ordinary unit tests.

DOCUMENTATION

Final TASK-010 docs must clearly distinguish:

Circle Marketplace / Discovery
wallet model actually used
x402
Arc testnet
Base historical discovery path
Gateway/Nanopayments only if actually used

No claim of live Arc payment unless smoke succeeds.

Arc testnet USDC must be described as testnet value.

DO NOT BUILD

Do not add:

Graph
Hedera
UI
generalized multichain wallet abstraction
retry framework
wallet policy engine
production credential persistence
REPORT

Push to existing PR #37.

Do not merge.

Report:

new head SHA
Circle wallet model selected
official reference used
Arc network identifier
Arc testnet USDC asset
Circle Discovery Arc-compatibility status
Arc service/seller used
quoted price
actual committed amount
transaction/payment reference
test count
live smoke result
exact human action required if blocked

End with:

Implementation agent: Manus.

Then stop.