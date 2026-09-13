# PR #42 — TASK-015: correct Arc Circle typed-data signing validation

**Implementation agent: Manus.**

## Root cause

The pinned `@circle-fin/x402-batching` `BatchEvmScheme` constructs an EIP-712 domain with exactly four fields: `name`, `version`, `chainId`, and `verifyingContract`. Its `authorizationTypes` map contains only `TransferWithAuthorization`. The current Circle Developer-Controlled Wallet `signTypedData` contract rejected the serialized request with:

```text
there is extra data provided in the message (0 < 4)
with external msg: Failed during the validation for typed data
```

## Correction

`typedDataJson()` now adds exactly this `EIP712Domain` schema to the serialized `types` map:

```json
[
  { "name": "name", "type": "string" },
  { "name": "version", "type": "string" },
  { "name": "chainId", "type": "uint256" },
  { "name": "verifyingContract", "type": "address" }
]
```

The existing `TransferWithAuthorization` fields and all Arc constraints remain unchanged: Arc EVM chain ID `5042002`, `GatewayWalletBatched` version `1`, GatewayWallet verifying contract, exact selected atomic amount, configured wallet address, validity bounds, and nonce.

## Lifecycle correction

Only the authoritative Circle typed-data validation rejection matching both known messages is classified as affirmative `pre_sign` / `not_committed`. It preserves the safe error detail.

Timeouts, network failures, malformed responses, invalid signatures, ambiguous provider errors, and any situation where a signature might have been returned remain `post_submit` / `unresolved`. No retry, zero spend, payment reference, or committed amount is fabricated.

## Scope

- No live payment or smoke was run.
- No Gateway deposit behavior changed.
- No dependencies added.
- No TASK-006 economics changed.
- No frontend changed.

## Verification

- Full Python suite: **784 passing**
- `npm run arc:setup:test`: passed; mocked only
- `node scripts/arc_x402_contract_test.mjs`: passed; mocked only
- Node syntax check: passed
- No Circle API call, seller request, facilitator request, Gateway deposit, faucet action, or live payment was performed.

**Implementation agent: Manus.**
