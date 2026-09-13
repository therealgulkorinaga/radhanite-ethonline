# 011 — TASK-015 Circle Wallet + x402 + Arc Testnet Execution

**Date:** 2026-09-13
**Agent:** Manus
**Authority:** TASK-015 authorization from the human product owner
**Resulted in:** New TASK-015 specification, Arc execution hardening, focused tests, smoke reporting, and one unmerged PR.

## Prompt

> Implementation agent: Manus.
>
> AUTHORIZE NEW FOLLOW-ON TASK — ARC TESTNET EXECUTION PATH.
>
> Repository:
> therealgulkorinaga/radhanite-ethonline
>
> PR #37 is already merged and must remain closed.
>
> Create a new task and new branch/PR for the Arc implementation.
>
> Suggested task name:
>
> TASK-015 — Circle Wallet + x402 + Arc Testnet Execution
>
> Human product owner / final merge authority: Arko.
>
> Independent reviewer: Codex.
>
> CONTEXT
>
> Existing merged Circle work already provides:
>
> live Circle Discovery
> TASK-008 normalization
> provider-neutral Candidate generation
> TASK-006 economic selection
> TASK-007 execution boundary
> exact Circle payment accounting invariants
> chain/network binding
> USDC asset validation
> unresolved-payment commitment handling
>
> That merged implementation is currently verified on the Base-mainnet Circle Discovery / Gateway path.
>
> The missing hackathon requirement is a real Arc testnet execution path.
>
> Do not rewrite or regress the existing Base adapter.
>
> OBJECTIVE
>
> Implement one minimal, real vertical slice:
>
> priced capability
>
> → TASK-008 Candidate
>
> → TASK-006 decides whether it is worth buying
>
> → TASK-007 executes only the selected capability
>
> → Circle-controlled wallet
>
> → x402 payment
>
> → Arc testnet settlement
>
> → exact committed testnet-USDC amount
>
> → payment/transaction reference
>
> → capability result
>
> → TASK-009 evidence/state update
>
> The purpose is to demonstrate:
>
> Radhanite decides whether an autonomous agent should spend, and Circle + x402 + Arc execute the selected purchase.
>
> FIRST STEP — VERIFY OFFICIAL CURRENT ARC PATH
>
> Before implementation, inspect the current official Circle/Arc sources and determine the shortest supported route for:
>
> wallet creation/control
> x402 authorization
> Arc testnet settlement
> testnet USDC
> transaction/payment verification
>
> Specifically evaluate:
>
> Circle Agent Wallet
> Circle Developer-Controlled Wallet
>
> Prefer whichever has the clearest current official Arc-testnet x402 support.
>
> If Circle's official Arc/x402 example uses a Developer-Controlled Wallet, prefer that rather than forcing the existing Circle CLI Agent Wallet adapter onto Arc.
>
> Do not infer Arc behavior from the Base implementation.
>
> Record the official references used in the PR explanation.
>
> WALLET MODEL
>
> Select exactly one wallet model for this task.
>
> Document:
>
> wallet model chosen
> why it was chosen
> Circle SDK/API/CLI used
> Arc network identifier
> required environment variables
> how signing/authorization occurs
>
> Do not mix Agent Wallet and Developer-Controlled Wallet concepts in runtime code unless the official flow actually requires both.
>
> ARC NETWORK / USDC
>
> Determine from official sources:
>
> Arc testnet network identifier
> Circle blockchain identifier
> Arc testnet USDC asset/address or token identifier
> x402 payment requirement format
> token decimal precision
>
> Encode only officially supported values.
>
> Validate:
>
> network
> asset
> amount
>
> before any signing/payment action.
>
> No Base fallback.
>
> CAPABILITY SOURCE
>
> First check whether Circle Discovery currently exposes a usable Arc-testnet-compatible paid capability.
>
> If yes
>
> Use:
>
> Circle Discovery
>
> → Arc-priced offer
>
> → TASK-008
>
> → TASK-006
>
> → Arc x402 execution.
>
> If no
>
> Do not fake Discovery provenance.
>
> Use one real Arc-testnet x402 service from an official Circle/Arc example.
>
> If necessary, create the smallest possible Radhanite demo seller based directly on Circle's official Arc x402 example.
>
> Clearly document:
>
> Circle Discovery is a separate marketplace/discovery surface
> the Arc service used for payment execution came from the official/demo Arc path
> ECONOMIC INVARIANTS
>
> Do not modify TASK-006 semantics.
>
> Required:
>
> exact cost known before selection
> cost > 0
> candidate is selected using existing economic rules
> non-selected capabilities are never paid
> wallet/payment provider identity cannot influence ranking
> TASK-006 remains provider-neutral
>
> Radhanite's budget is:
>
> economic permission to spend
>
> not:
>
> a wallet spending limit
>
> Keep those concepts separate.
>
> PAYMENT INVARIANTS
>
> Preserve the payment-accounting safety learned from PR #37:
>
> exact selected offer ↔ exact payment network
> exact selected offer ↔ exact asset
> exact authorized maximum
> exact committed amount where known
> potentially submitted but unknown commitment must fail as unresolved
> never silently record ambiguous payment as zero spend
> no retries after ambiguous commitment
>
> Do not weaken these for the Arc path.
>
> EXECUTION ADAPTER
>
> Implement the narrowest Arc-specific payment client/executor needed behind TASK-007.
>
> It must:
>
> receive the already-selected capability
> validate Arc network/payment requirements
> authorize/sign using the selected Circle wallet model
> execute the x402 payment
> obtain the service response
> obtain authoritative payment/settlement metadata
> return exact committed testnet cost
> retain payment/transaction reference
>
> Keep provider-specific metadata outside Candidate.
>
> Do not turn this into a generalized multichain wallet framework.
>
> TASK-009 EVIDENCE
>
> Map the successful purchased service result into the existing evidence contract.
>
> The Circle/Arc adapter must NOT:
>
> directly change success probability
> mark the revenue task complete
> select the next candidate
>
> TASK-009 interprets the result.
>
> TASK-006 performs the next economic decision.
>
> LIVE ARC SMOKE
>
> Add one explicit opt-in live smoke command.
>
> The target smoke run must show:
>
> wallet type
> wallet address
> Arc testnet network
> capability being considered
> exact quoted testnet-USDC cost
> current success probability
> incremental expected value
> TASK-006 decision
> x402 payment execution
> Arc settlement reference / transaction hash / payment ID
> exact committed testnet-USDC
> capability result
> TASK-009 state/probability after evidence
>
> No payment should happen automatically during ordinary tests.
>
> Never print secrets.
>
> HUMAN SETUP / CREDENTIAL BLOCKER
>
> If live Arc execution requires human setup, stop at the exact blocker and report it precisely.
>
> Possible requirements may include:
>
> Circle API key
> entity secret
> wallet set
> Arc-testnet wallet creation
> faucet/testnet USDC funding
> environment variables
>
> Report:
>
> exact official setup action
> variable name
> wallet address if safe
> required testnet funding amount
> whether implementation/tests are otherwise complete
>
> Do not fall back to Base because credentials are missing.
>
> TESTS
>
> Preserve all existing tests.
>
> Add only critical Arc coverage:
>
> valid Arc testnet payment requirement accepted
> unsupported/wrong network rejected before signing
> Base cannot masquerade as Arc
> Arc testnet USDC asset validated
> malformed/wrong asset rejected
> exact amount preserved
> non-selected candidate never invokes wallet
> selected candidate invokes payment only after TASK-006
> successful Arc payment returns exact committed cost
> transaction/payment reference retained
> ambiguous payment commitment fails closed
> service result becomes TASK-009 evidence
> TASK-009 update is visible to the next TASK-006 decision
>
> Mock external calls in ordinary tests.
>
> DOCUMENTATION
>
> Add:
>
> task specification
> architecture note
> implementation prompt artifact
> PR explanation
> Codex review placeholder
>
> Documentation must clearly distinguish:
>
> Circle Discovery
> chosen Circle wallet model
> x402
> Arc testnet
> Base support already merged
>
> No claim of live Arc execution unless the live smoke succeeds.
>
> Arc USDC must be called testnet USDC.
>
> OUT OF SCOPE
>
> Do not add:
>
> The Graph
> Hedera
> UI
> generic wallet abstraction
> generic multichain routing
> retry engine
> production credential storage
> wallet-policy engine
> batching unless required by the actual official Arc path
> GIT / PR
>
> Create a new branch from current main.
>
> Suggested branch:
>
> task-015-circle-arc-execution
>
> Create one new PR.
>
> Do not merge.
>
> Preserve required textual provenance:
>
> Implementation agent: Manus.
>
> in:
>
> implementation progress report
> commit messages
> PR description
> PR explanation
> handoff report
> REPORT BACK
>
> Report:
>
> task number/name
> branch
> PR number
> head SHA
> wallet model selected
> official Circle/Arc reference used
> Arc network identifier
> Arc testnet USDC identifier
> whether Arc capability came from Circle Discovery
> service/seller used
> quoted testnet price
> test count
> live smoke status
> actual committed amount if successful
> transaction/payment reference if successful
> exact human blocker if live smoke cannot run
>
> End with:
>
> Implementation agent: Manus.
>
> Then stop.

## Notes

The official-path inspection selected the Circle Developer-Controlled Wallet EOA and `@circle-fin/x402-batching` route. Existing TASK-010 scaffolding was retained and hardened rather than duplicated. The live smoke was not run automatically; its status is reported only after explicit setup and opt-in execution.

**Implementation agent: Manus.**
