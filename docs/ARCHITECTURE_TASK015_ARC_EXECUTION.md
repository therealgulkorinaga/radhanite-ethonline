# TASK-015 Architecture Note — Arc Testnet execution boundary

**Status:** Authorized follow-on design and implementation note. **Implementation agent: Manus.**

TASK-015 adds one provider-specific execution edge below the existing Radhanite economic kernel. It does not change TASK-006, TASK-007, TASK-008, or TASK-009 semantics.

## Boundary ownership

| Boundary | Owner | TASK-015 rule |
|---|---|---|
| Exact pre-purchase price | Circle/Arc seller or demo seller | The price is known before candidate selection |
| Candidate normalization | TASK-008 adapter | Circle/Arc metadata remains outside Candidate |
| Economic decision | TASK-006 | Only stable ID, exact cost, and declared probability enter selection |
| Selected-only execution | TASK-007 | The executor receives the selected Candidate and exact authorization ceiling |
| Wallet custody and signing | Circle Developer-Controlled Wallet EOA | Circle SDK/API signs EIP-712; Radhanite holds no key |
| x402 payment protocol and Gateway acceptance | Circle x402 batching SDK/Gateway | Radhanite does not implement x402 or settlement |
| Exact ledger cost | TASK-007 | `committed_cost` is the validated selected USDC amount |
| Evidence interpretation | TASK-009 | The adapter supplies immutable evidence; TASK-009 changes state/probability |

## Selected wallet model

The runtime uses exactly one wallet model: a **Circle Developer-Controlled Wallet EOA**. It does not use Circle Agent Wallet CLI login, raw private keys, `GatewayClient`, or a generic wallet abstraction. The pinned SDK gate proved the supported route: `client.signTypedData({ walletId, data, memo })` is adapted to `{ address, signTypedData }` for `BatchEvmScheme`, while `GatewayClient` is private-key-only. The pinned versions are `@circle-fin/developer-controlled-wallets@10.8.0` and `@circle-fin/x402-batching@3.4.0`.

## Arc contract

The only accepted payment environment is `ARC-TESTNET`, x402 network `eip155:5042002`, EVM chain ID `5042002`, and Arc Testnet USDC interface `0x3600000000000000000000000000000000000000`. Gateway domain `26` and GatewayWallet `0x0077777d7EBA4688BDeF3E311b846F25870A19B9` are used for the GatewayWalletBatched EIP-712 contract. Payment amounts are exact 6-decimal USDC atomic units. The helper rejects Base and every other network.

The seller's x402 v2 response must expose an exact requirement with `scheme=exact`, `extra.name=GatewayWalletBatched`, `extra.version=1`, and the authoritative Gateway verifying contract. The amount must equal the pre-purchase quote, not merely be below the authorization ceiling.

`CIRCLE_ARC_WALLET_ID` must resolve to the same `ARC-TESTNET` EOA whose address is supplied as `CIRCLE_ARC_WALLET_ADDRESS`. The helper checks this correlation before signing. A read-only Gateway balance check must show enough available balance for the exact selected amount. Wallet creation, faucet funding, approval, and Gateway deposit are setup actions and are never initiated by the purchase runtime.

## Reference semantics

The x402 response's successful Gateway transaction/payment reference is retained in evidence. The implementation labels immediate Gateway acceptance separately from later on-chain finality. It does not call an acceptance reference an on-chain final transaction unless a separate authoritative transfer lookup establishes that fact. Payment-response metadata is parsed before service HTTP status, so an accepted payment plus service failure retains exact committed cost and reference.

## Safety posture

All network, asset, amount, scheme, version, batching name, verifying contract, EIP-712 primary type, authorization fields, selected-candidate, wallet correlation, and authorization checks occur before Circle signing or payment. Arc atomic conversion uses the Decimal coefficient/exponent tuple rather than ambient-context multiplication. Only an affirmative `pre_sign` helper envelope permits a pre-attempt error; crashes, timeouts, malformed output, and contradictory metadata raise unresolved commitment. The generic loop does not retry and does not fabricate zero spend. A validated positive demo result is the only path that emits `positive_market_signal`; neutral or negative results remain non-success evidence.

**Implementation agent: Manus.**

## References

[1]: https://developers.circle.com/wallets/dev-controlled-wallets "Circle Developer-Controlled Wallets documentation"
[2]: https://developers.circle.com/gateway "Circle Gateway documentation"
[3]: https://github.com/circlefin/arc-x402-circle-wallets "Circle Arc x402 wallet example"
[4]: https://github.com/akelani-circle/arc-nanopayments "Circle Arc nanopayments example"
[5]: https://github.com/circlefin/arc-commerce "Circle Arc Commerce example"

**Implementation agent: Manus.**
