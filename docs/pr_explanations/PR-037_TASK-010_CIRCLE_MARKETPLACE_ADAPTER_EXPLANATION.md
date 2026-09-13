# PR-037 — TASK-010 Circle marketplace and Arc payment adapter

**Implementation agent: Manus.**

## Purpose

This pull request adds one thin provider-specific Circle boundary to Radhanite. It does not replace the economic kernel, add a marketplace, implement a wallet, or reimplement x402. Circle supplies a machine-readable service offer and its pre-purchase payment terms; TASK-008 converts that descriptor to a provider-neutral candidate; TASK-006 decides whether the candidate is worth buying; TASK-007 invokes the executor only after selection; TASK-009 interprets the returned evidence.

The preserved product line remains: **Circle tells the agent what it can buy and how to pay. Radhanite decides what is worth buying.**

## What is implemented

`radhanite.circle` reads the keyless public Circle Discovery API at `https://api.circle.com/v2/x402/discovery/resources`. It accepts only exact, positive `GatewayWalletBatched` offers on the requested EVM network. It converts integer micro-USDC amounts to exact `Money` values before selection. Provider metadata stays in `CircleCapabilityCatalog` and `CircleOffer`; TASK-006 sees only the existing three-field `Candidate`.

The selected vertical slice is a live AIsa API CoinGecko Simple Price service. The current live response exposed `https://api.aisa.one/apis/v2/coingecko/simple/price`, a GET resource requiring `ids` and `vs_currencies`, with a quoted price of `12000` micro-USDC (`0.012` USDC) on Base mainnet and the `GatewayWalletBatched` payment scheme. This is a marketplace service; the repository does not claim a direct relationship with CoinGecko or AIsa beyond the discovered listing.

`CircleCapabilityExecutor` maps the selected candidate back to the retained provider descriptor and delegates payment to the official Circle CLI. The CLI command receives the explicit HTTP method, wallet address, chain, and `--max-amount` authorization ceiling. The structured JSON payment envelope is authoritative: successful and definitely submitted responses must expose matching amount, network, CLI chain, scheme, and supported USDC asset metadata. The current mapping is `eip155:8453 -> BASE`; a mismatched override is rejected before the runner is invoked. A successful exact-payment response returns an exact `ExecutionResult` with the validated atomic amount and a fixture-driven TASK-009 evidence envelope. A failure before payment raises a pre-attempt error without fabricated spend. If the official CLI reports that payment was submitted and provides a matching exact amount, that amount is recorded as committed. If payment may have been submitted but the exact amount is unknown, the adapter raises a dedicated unresolved-commitment error and does not create a normal TASK-007 `ExecutionResult`.

The opt-in live command is:

```text
PYTHONDONTWRITEBYTECODE=1 python3.12 -m radhanite.circle_smoke
```

The command requires an installed and authenticated official Circle CLI and `CIRCLE_WALLET_ADDRESS`. The current selected resource is Base mainnet, so the command refuses to pay unless `CIRCLE_SMOKE_ALLOW_MAINNET=1` is explicitly set. `CIRCLE_CHAIN` defaults to `BASE`, and `CIRCLE_DISCOVERY_NETWORK` defaults to `eip155:8453`. It prints only non-secret discovery, selection, payment, accounting, and evidence summaries.

## Circle/Arc truthfulness

Circle's official documentation describes Arc Testnet Gateway/x402 nanopayments with an EOA, faucet USDC, Gateway deposit, EIP-3009 authorization, and later batched settlement. The live Marketplace response used for this branch did not establish an Arc Testnet listing for the selected service; therefore this PR does not describe the live Marketplace purchase as an Arc Testnet purchase. The adapter accepts a network parameter and is compatible with an Arc offer if Circle Discovery returns one, but the payment smoke was not run here because no Circle CLI or wallet credentials were available. No production money was spent and no credentials are committed.

## Validation

The focused TASK-010 suite contains **26 tests** and mocks HTTP and payment calls. It covers exact-price normalization, provider neutrality, no payment during discovery, unknown/non-Gateway exclusion, candidate-to-descriptor mapping, selection-before-payment, explicit authorization, over-commitment rejection, exact successful accounting, attempted-failure accounting, structured JSON metadata validation, definite pre-attempt and submitted failures, unresolved commitment handling, chain/network mapping, mainnet safety, exact atomic conversion under a tiny Decimal context, supported USDC validation, CLI command construction, and environment-only credential handling.

The authoritative command at the original Base-only implementation passed **751 tests** on Python 3.12. The live read-only Circle Discovery check succeeded and returned **18** exact Base-mainnet Gateway offers at the time of implementation. The live payment smoke was **not run**: the sandbox has no Circle CLI or wallet credentials, and a mainnet payment requires explicit user-controlled setup and funding.

## Deliberate non-scope

This PR adds no Circle SDK dependency, no wallet custody, no private-key handling, no payment protocol implementation, no retry behavior, no persistence, no UI, no The Graph or Hedera integration, no probability logic, and no change to the TASK-001 CLI/runtime path. Arc is not used by the verified live offer. TASK-010 remains a review branch and must not be merged by the implementation agent.


## Arc phase extension

**Implementation agent: Manus.** This same PR now contains the separately authorized Arc Testnet phase. The chosen wallet model is Circle's official **Developer-Controlled Wallet EOA**, because Circle's official Arc nanopayments buyer example uses that SDK directly for wallet creation, typed-data signing, contract execution, and transaction polling. The x402 payment uses Circle's official `@circle-fin/x402-batching` SDK.

Circle Discovery was checked for an Arc-compatible paid resource and did not establish one for the selected live Marketplace resource. Accordingly, the Arc smoke uses a separately identified minimal demo seller derived from Circle's official Arc nanopayments example. The seller is not represented as a Circle Marketplace listing, and Base is not used as a fallback.

The Arc path is bound to `ARC-TESTNET` / `eip155:5042002` and the official Arc Testnet USDC asset configured in the adapter. Before signing, Radhanite knows the exact quoted price and TASK-006 selects the candidate. The helper then checks Gateway balance, performs Circle's official USDC approval and Gateway deposit when needed, obtains the seller's `402` requirements, signs the selected `GatewayWalletBatched` requirement, retries with the x402 payment header, and retains the settlement or authorization reference and exact amount. The result is converted into the existing immutable TASK-009 evidence envelope; the Circle adapter does not update probability, select the next capability, or mark the task complete.

The branch adds six critical Arc tests covering Arc network acceptance, Base rejection, wallet/network binding, wrong-network rejection before signing, exact amount and asset preservation, non-selected payment exclusion, selected-after-TASK-006 ordering, exact committed-cost and reference retention, and TASK-009 evidence handoff. The full Python 3.12 suite passes **764 tests**. Node syntax and official SDK imports also pass.

The live Arc smoke is **blocked, not falsely reported as successful**, because this checkout has no supplied Circle API key, entity secret, funded Arc EOA, Gateway balance, or seller URL. The explicit command reports those exact prerequisites and never prints secrets, attempts Base fallback, or performs a payment without them.
