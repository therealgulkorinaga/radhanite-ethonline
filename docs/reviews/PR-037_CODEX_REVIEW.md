# Codex review — PR-037

**Implementation agent: Manus.**
**Pull request:** #37 — TASK-010: Circle marketplace and Arc payment adapter
**Reviewer:** Codex (independent review agent, AI_BUILD_GOVERNANCE.md §1.3)
**Reviewed against:** TASK-010_CIRCLE_MARKETPLACE_ADAPTER.md, TASK-008_CAPABILITY_ACQUISITION.md, TASK-007_CAPABILITY_RUN_LOOP.md, TASK-009_REVENUE_OPPORTUNITY_STATE.md, ARCHITECTURE.md §2, §3, §4, §6, and the changed source/tests
**Date issued:** 2026-09-13
**Outcome:** corrections applied; pending independent re-review

## 1. Prompt issued

Review PR #37 as an independent adversarial reviewer. Verify the exact Circle Discovery endpoint and response handling, pre-purchase exact-price invariant, TASK-008 descriptor-to-candidate boundary, provider metadata exclusion from Candidate, candidate-to-provider mapping, selection-before-payment ordering, explicit authorization ceiling, exact committed-cost accounting on success and attempted failure, pre-attempt no-spend behavior, evidence handoff to TASK-009, environment-only credentials, live-smoke opt-in behavior, Arc/mainnet/testnet truthfulness, and absence of forbidden wallet/x402/SDK/retry/UI/integration scope. Run the focused and full Python 3.12 suites. Check that documentation does not claim a live payment or Arc Testnet marketplace offer that was not actually verified.

## 2. Findings returned

### CODEX-PR037-01 — authoritative CLI JSON accounting

The first implementation used substring matching and treated a payment-submitted
message as an exact quote commitment. The correction parses the official JSON
envelope, validates authoritative amount/network/chain/scheme/asset metadata,
records a definite submitted amount only when exact, and raises an unresolved
commitment error when the provider says payment may have been submitted without
an exact amount. Unrelated text cannot fabricate spend.

### CODEX-PR037-02 — offer network and CLI chain

The correction adopts the explicit supported mapping `eip155:8453 -> BASE`.
An override must exactly match the selected offer's mapped CLI chain, unsupported
networks are rejected, and the mainnet safety guard evaluates the actual payment
chain before runner invocation.

### CODEX-PR037-03 — atomic amount and USDC asset

The correction requires a positive decimal-digit string for atomic micro-USDC,
validates the documented Base USDC asset, and converts quotient/remainder units
to `Money` without using ambient Decimal precision. `12000` becomes exactly
`0.012`, and large values retain all six decimal places.

## 3. Outcome

Corrections are implemented and validated locally. Independent Codex re-review
is pending. This record remains committed before review in accordance with
AI_BUILD_GOVERNANCE.md §7.3.

## 4. Corrections

The three findings above are the only authorized correction scope. No Arc
integration, Circle wallet model change, Graph, Hedera, UI, persistence, retry,
or generic payment abstraction was added.
