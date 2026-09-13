# TASK-015 — Circle Wallet + x402 + Arc Testnet Execution

**Status:** Authorized — implementation on review branch; live smoke remains explicitly opt-in and credential-gated.
**Authorization:** Arko authorized TASK-015 on 2026-09-13 for one new branch and one unmerged pull request. **Implementation agent: Manus.**
**Human merge authority:** Arko. **Independent reviewer:** Codex.
**Depends on:** merged TASK-006, TASK-007, TASK-008, TASK-009, and TASK-010 boundaries.
**Bounded by:** [`PREREQ-001`](../docs/PREREQ-001_PRODUCT_DEFINITION.md), [`ARCHITECTURE.md`](../docs/ARCHITECTURE.md), and [`AI_BUILD_GOVERNANCE.md`](../docs/AI_BUILD_GOVERNANCE.md).

---

## 1. Purpose

TASK-015 demonstrates one truthful, minimal Arc Testnet vertical slice:

```text
exact priced capability
  → TASK-008 provider-neutral Candidate
  → TASK-006 economic decision
  → TASK-007 selected-only execution
  → Circle Developer-Controlled Wallet EOA
  → x402 exact payment through Circle Gateway
  → Arc Testnet service result
  → exact committed testnet-USDC amount and reference
  → TASK-009 immutable evidence/state update
```

Radhanite owns the decision to buy. Circle's wallet and Gateway/x402 systems own signing, custody, payment protocol, and settlement infrastructure.

## 2. Selected wallet model

The only wallet model authorized by this task is the **Circle Developer-Controlled Wallet EOA**. The runtime uses `@circle-fin/developer-controlled-wallets@10.8.0` with `CIRCLE_API_KEY` and `CIRCLE_ENTITY_SECRET`, and uses `CIRCLE_ARC_WALLET_ID` to identify a pre-provisioned wallet. Circle signs the EIP-712 authorization on behalf of the EOA. The runtime does not use Circle Agent Wallet CLI login, email OTP, private keys, GatewayClient, or a generic wallet abstraction.

This model is selected because Circle's current official Arc x402 examples use the Developer-Controlled Wallet with `@circle-fin/x402-batching`, while Circle Agent Wallet is a separate CLI/email-OTP product. Mixing those models would obscure custody and authentication semantics.

Required runtime setup is supplied through the environment only:

| Variable | Meaning |
|---|---|
| `CIRCLE_API_KEY` | Circle Developer-Controlled Wallet API credential |
| `CIRCLE_ENTITY_SECRET` | Circle entity secret used by the SDK |
| `CIRCLE_ARC_WALLET_ID` | Required pre-provisioned Circle wallet resource ID used for signing |
| `CIRCLE_ARC_WALLET_ADDRESS` | Required Arc EOA address; the helper verifies it matches the wallet ID |
| `RADHANITE_ARC_RESOURCE` | Explicit Arc x402 seller URL |
| `RADHANITE_ARC_PRICE` | Exact pre-purchase decimal USDC quote used by the demo catalog |
| `CIRCLE_ARC_SELLER_ADDRESS` | Seller address when running the separate local demo seller |

Secrets are never committed or printed. Wallet creation, faucet funding, approval, and Gateway deposit are setup actions and are not performed inside the purchase path. The Radhanite budget remains an economic permission ceiling; it is not represented as a Circle wallet spending limit.

The pre-implementation SDK gate established the exact supported composition: `client.signTypedData({ walletId, data, memo })` is injected as `{ address, signTypedData }` into `new BatchEvmScheme(...)`, followed by `createPaymentPayload(2, paymentRequirements)`. The pinned `GatewayClient` is intentionally not used because it constructs a viem account from a raw private key.

## 3. Official Arc identifiers and exact units

The implementation encodes only these current official values:

| Concept | Value |
|---|---|
| x402 network | `eip155:5042002` |
| Circle blockchain identifier | `ARC-TESTNET` |
| EVM chain ID | `5042002` |
| Circle Gateway domain | `26` |
| Arc Testnet USDC ERC-20 interface | `0x3600000000000000000000000000000000000000` |
| GatewayWallet/verifying contract | `0x0077777d7EBA4688BDeF3E311b846F25870A19B9` |
| x402 scheme | `exact` |
| x402 batching name | `GatewayWalletBatched` |
| x402 protocol version | `2` |
| payment precision | 6 decimal USDC atomic units |

Arc native gas accounting uses 18 decimals, but this payment slice records the purchased capability's USDC amount in 6-decimal atomic units. Those units must not be conflated.

Before signing or payment, the adapter and buyer helper validate the exact network, strict EVM asset syntax, exact Arc Testnet USDC address, exact positive atomic amount, x402 v2, exact scheme, batching name, batching version, Gateway verifying contract, EIP-712 primary type, and authorization fields. The wallet ID is resolved and checked against the configured EOA address, and Gateway available balance is checked read-only. There is no Base fallback and no automatic funding or deposit.

## 4. Capability provenance and seller identity

The first discovery question is whether Circle Discovery exposes a usable Arc Testnet paid capability. The current captured live Discovery path used by TASK-010 exposes a usable Base Gateway offer but did not establish an Arc Testnet listing for the selected resource. Therefore this task must not represent the Arc seller as a Circle Marketplace listing.

The Arc smoke uses a separately identified real x402 seller from the official Circle/Arc example path. The repository includes the smallest local seller needed for deterministic demonstration infrastructure, derived from Circle's official x402 batching sample. It is labelled as demo infrastructure, not Circle Discovery provenance. If a human supplies an official external seller URL, that URL and its actual payee are reported as the seller; upstream technology is not inferred to be the payee.

## 5. Economic and execution contract

The Arc offer enters TASK-008 with an exact positive `Money` quote known before selection. TASK-008 retains seller, network, asset, and payment metadata outside the three-field Candidate. TASK-006 sees only the Candidate's stable ID, exact cost, and declared post-action success probability. Provider, wallet, network, and asset identity cannot influence ranking.

TASK-007 receives the selected Candidate and passes the exact authorization ceiling to the executor. The executor resolves the selected Candidate back to the exact retained Arc offer. It refuses mismatched network, asset, quote, or authorization before invoking Circle or signing. Only the selected candidate may invoke the wallet/payment client; non-selected offers are never paid.

A successful payment result must contain the exact selected atomic amount, the successful service response, and an authoritative payment or transaction reference. The reference is retained as evidence. A Gateway acceptance/reference is not described as later on-chain finality unless separate transfer evidence proves that finality.

The adapter creates immutable `make_evidence(...)` only. It does not select candidates, change declared probability, mark the benchmark complete, or choose the next action. TASK-009 interprets the evidence, and the next TASK-006 decision receives the updater's resulting probability and state.

## 6. Failure and ambiguity semantics

The following rules are mandatory:

1. A wrong network, malformed asset, wrong asset, unsupported x402 requirement, wrong amount, or mismatched quote fails before signing.
2. A payment attempt that returns an authoritative successful Gateway response records the exact selected cost and reference.
3. A service response after a signed payment that lacks authoritative settlement/reference metadata is **unresolved**, not zero spend.
4. Any helper result explicitly marked `commitment_status: unresolved` becomes an unresolved-commitment error. It is never converted into a normal `ExecutionResult` and is never retried.
5. A pre-attempt setup failure may abort without a spend record only when no x402 payment request has been signed/submitted.
6. No automatic retry engine exists in TASK-015.

## 7. Tests and smoke

Ordinary Python and Node contract tests mock external wallet, HTTP, seller, and subprocess behavior. They cover valid Arc requirements, wrong network/Base masquerade, strict asset validation, exact six-decimal amounts, selected-only invocation, exact committed cost/reference, unresolved commitment fail-closed behavior, evidence handoff, and a subsequent TASK-006 decision after the TASK-009 probability update.

The only live payment command is explicit opt-in:

```text
npm install
PYTHONDONTWRITEBYTECODE=1 python3.12 -m radhanite.arc_smoke
```

Before signing it reports wallet model/address, Arc network, resource, exact quote, current and expected post-action probability, incremental expected value, maximum authorization, and TASK-006 selection. After execution it reports the Gateway reference, exact committed testnet-USDC, service-result summary, and TASK-009 state/probability. Missing credentials, wallet mismatch, wallet funding, Gateway balance, or seller URL produces an actionable blocker report and performs no payment. Arc Testnet USDC is testnet value, not production value.

## 8. Out of scope

TASK-015 does not add a generic wallet interface, multichain routing, payment-policy engine, retry engine, production credential storage, UI, The Graph, Hedera, or a new economic rule. It does not rewrite the merged Base Discovery/CLI adapter. It does not claim that a live payment succeeded unless the explicit smoke actually returns a validated result.

## 9. Acceptance criteria

1. One exact Arc price becomes one TASK-008 candidate.
2. TASK-006 makes the purchase decision before any wallet or payment call.
3. Only the selected candidate reaches TASK-007 execution and the Circle client.
4. Wrong network, Base network, malformed asset, wrong asset, wrong x402 scheme, wrong x402 version, wrong batching name/version, and wrong verifying contract are rejected before signing.
5. Exact six-decimal atomic amount is preserved through selection, authorization, receipt, and ledger accounting.
6. Successful Arc execution retains the service result and payment/transaction reference.
7. Ambiguous post-attempt commitment fails closed, records no invented zero spend, and cannot retry.
8. Evidence reaches TASK-009, whose declared probability/state update is visible to the next TASK-006 decision.
9. Normal tests use mocks and never trigger payment automatically.
10. The explicit smoke reports a precise human setup blocker when live execution cannot run.

**Implementation agent: Manus.**

## References

[1]: https://developers.circle.com/wallets/dev-controlled-wallets "Circle Developer-Controlled Wallets documentation"
[2]: https://developers.circle.com/gateway "Circle Gateway documentation"
[3]: https://github.com/circlefin/arc-x402-circle-wallets "Circle Arc x402 Developer-Controlled Wallet example"
[4]: https://github.com/akelani-circle/arc-nanopayments "Circle Arc nanopayments example"
[5]: https://github.com/circlefin/arc-commerce "Circle Arc Commerce example"
[6]: https://faucet.circle.com "Circle Faucet for testnet USDC"
[7]: https://x402.org "x402 protocol documentation"

**Implementation agent: Manus.**
