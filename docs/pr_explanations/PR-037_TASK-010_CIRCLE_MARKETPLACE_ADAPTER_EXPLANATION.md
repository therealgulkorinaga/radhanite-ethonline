# PR-037 — TASK-010 Circle marketplace and Arc payment adapter

**Implementation agent: Manus.**

## Purpose

This pull request adds one thin provider-specific Circle boundary to Radhanite. It does not replace the economic kernel, add a marketplace, implement a wallet, or reimplement x402. Circle supplies a machine-readable service offer and its pre-purchase payment terms; TASK-008 converts that descriptor to a provider-neutral candidate; TASK-006 decides whether the candidate is worth buying; TASK-007 invokes the executor only after selection; TASK-009 interprets the returned evidence.

The preserved product line remains: **Circle tells the agent what it can buy and how to pay. Radhanite decides what is worth buying.**

## What is implemented

`radhanite.circle` reads the keyless public Circle Discovery API at `https://api.circle.com/v2/x402/discovery/resources`. It accepts only exact, positive `GatewayWalletBatched` offers on the requested EVM network. It converts integer micro-USDC amounts to exact `Money` values before selection. Provider metadata stays in `CircleCapabilityCatalog` and `CircleOffer`; TASK-006 sees only the existing three-field `Candidate`.

The selected vertical slice is a live AIsa API CoinGecko Simple Price service. The current live response exposed `https://api.aisa.one/apis/v2/coingecko/simple/price`, a GET resource requiring `ids` and `vs_currencies`, with a quoted price of `12000` micro-USDC (`0.012` USDC) on Base mainnet and the `GatewayWalletBatched` payment scheme. This is a marketplace service; the repository does not claim a direct relationship with CoinGecko or AIsa beyond the discovered listing.

`CircleCapabilityExecutor` maps the selected candidate back to the retained provider descriptor and delegates payment to the official Circle CLI. The CLI command receives the explicit HTTP method, wallet address, chain, and `--max-amount` authorization ceiling. A successful exact-payment response returns an exact `ExecutionResult` with the quoted committed cost and a fixture-driven TASK-009 evidence envelope. A failure before payment raises a pre-attempt error without fabricated spend. If the official CLI reports that payment was submitted but the service failed, the exact quoted amount is recorded as committed because the selected scheme is exact rather than metered; no partial amount is invented.

The opt-in live command is:

```text
PYTHONDONTWRITEBYTECODE=1 python3.12 -m radhanite.circle_smoke
```

The command requires an installed and authenticated official Circle CLI and `CIRCLE_WALLET_ADDRESS`. The current selected resource is Base mainnet, so the command refuses to pay unless `CIRCLE_SMOKE_ALLOW_MAINNET=1` is explicitly set. `CIRCLE_CHAIN` defaults to `BASE`, and `CIRCLE_DISCOVERY_NETWORK` defaults to `eip155:8453`. It prints only non-secret discovery, selection, payment, accounting, and evidence summaries.

## Circle/Arc truthfulness

Circle's official documentation describes Arc Testnet Gateway/x402 nanopayments with an EOA, faucet USDC, Gateway deposit, EIP-3009 authorization, and later batched settlement. The live Marketplace response used for this branch did not establish an Arc Testnet listing for the selected service; therefore this PR does not describe the live Marketplace purchase as an Arc Testnet purchase. The adapter accepts a network parameter and is compatible with an Arc offer if Circle Discovery returns one, but the payment smoke was not run here because no Circle CLI or wallet credentials were available. No production money was spent and no credentials are committed.

## Validation

The focused TASK-010 suite contains **13 tests** and mocks HTTP and payment calls. It covers exact-price normalization, provider neutrality, no payment during discovery, unknown/non-Gateway exclusion, candidate-to-descriptor mapping, selection-before-payment, explicit authorization, over-commitment rejection, exact successful accounting, attempted-failure accounting, pre-attempt failure, CLI command construction, and environment-only credential handling.

The authoritative command `PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest discover -q` passes **738 tests** on Python 3.12. The live read-only Circle Discovery check succeeded and returned **18** exact Base-mainnet Gateway offers at the time of implementation. The live payment smoke was **not run**: the sandbox has no Circle CLI or wallet credentials, and a mainnet payment requires explicit user-controlled setup and funding.

## Deliberate non-scope

This PR adds no Circle SDK dependency, no wallet custody, no private-key handling, no payment protocol implementation, no retry behavior, no persistence, no UI, no The Graph or Hedera integration, no probability logic, and no change to the TASK-001 CLI/runtime path. TASK-010 remains a review branch and must not be merged by the implementation agent.
