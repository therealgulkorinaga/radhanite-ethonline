Fix the real Arc smoke blocker only. Do not redesign TASK-015, change TASK-006 economics, alter Gateway deposit behavior, add dependencies, or run a live payment.

Repository: `therealgulkorinaga/radhanite-ethonline`

Apply this to the existing TASK-015 diagnostic work.

## Observed live result

The final recorded Arc Testnet smoke reached Circle’s Developer-Controlled Wallet typed-data signing call and stopped with:

```text
error: there is extra data provided in the message (0 < 4)
with external msg: Failed during the validation for typed data
```

The saved non-secret transcript is local-only at:

```text
.arc-demo-private/smoke-20260913T144221Z.log
```

Gateway balance remained `1` testnet USDC afterward. No payment reference or committed amount exists. The seller was stopped and no further smoke must be run during this fix.

## Required correction

Fix `scripts/arc_x402_pay.mjs` so the JSON passed to Circle’s `signTypedData` API has the exact EIP-712 structure Circle requires.

Inspect the actual `BatchEvmScheme` typed-data parameters and Circle’s current `signTypedData` contract. In particular, verify whether the serialized `types` map must include an explicit `EIP712Domain` definition matching the domain’s actual fields. Do not guess or add unrelated fields.

The signed data must still be exactly constrained to:

- `TransferWithAuthorization`
- Arc Testnet chain ID `5042002`
- `GatewayWalletBatched`, version `1`
- Arc GatewayWallet verifying contract
- exact selected atomic amount
- configured Circle buyer wallet address
- the existing authorization validity/nonce checks

## Failure classification

Correct the misleading lifecycle flag as well.

The current helper sets `circleSigningAttempted = true` before awaiting Circle’s response. That causes a Circle typed-data validation rejection—which proves Circle did not return a signature—to be reported as an unresolved post-sign state.

Required behavior:

- A known, authoritative Circle typed-data validation rejection must emit the complete affirmative `pre_sign` / `not_committed` envelope and preserve the safe error detail.
- Do not broadly downgrade all signing-call failures to pre-sign.
- Timeout, network loss, malformed response, ambiguous provider error, or any failure where a signature might have been returned remain unresolved.
- Do not retry automatically.
- Do not invent zero spend, a payment reference, or committed cost.
- Preserve API-key and entity-secret redaction.

## Tests

Add only focused tests necessary to prove:

1. The exact serialized payload supplied to Circle includes the EIP-712 schema Circle requires.
2. Reverting to the old malformed serialization fails the relevant test.
3. A Circle validation rejection is classified as affirmative pre-sign/no commitment.
4. An ambiguous signing failure remains unresolved.
5. Existing Arc authorization constraints and credential-redaction tests remain effective.

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest discover -q
npm run arc:setup:test
node scripts/arc_x402_contract_test.mjs
```

Do not run a live smoke, payment, Gateway deposit, or faucet action.

Report the commit hash, changed files, test totals, and the exact safe result expected on the next human-authorized smoke.