# PR #38 — TASK-015: Circle Wallet + x402 + Arc Testnet Execution

**Authority:** TASK-015, authorized by Arko on 2026-09-13.
**Branch:** `task-015-circle-arc-execution`.
**Baseline:** merged PR #37 at `4ac9756fcb5a4d18fa137395df77fccb18b0f395`; PR #37 remains closed and merged.
**Implementation agent:** **Manus.**
**Human product owner and merge authority:** Arko.
**Independent reviewer:** Codex; pending record: [`PR-038_CODEX_REVIEW.md`](../reviews/PR-038_CODEX_REVIEW.md).

## 1. Purpose

This pull request adds the narrow Arc Testnet execution slice that was missing after PR #37. It demonstrates the intended boundary: Radhanite receives an exact priced capability, turns it into a provider-neutral candidate, lets TASK-006 decide whether the purchase is worth making, lets TASK-007 execute only the selected candidate, and passes the exact service result and payment evidence to TASK-009.

PR #37's merged Base Discovery and CLI adapter is preserved. Arc is treated as a separate payment environment. The change does not infer Arc behavior from Base and does not add a Base fallback.

## 2. What changed

The Arc adapter now retains the x402 batching metadata required to validate an Arc offer: exact scheme, batching name and version, and Gateway verifying contract. It strictly validates the Arc Testnet network, EVM asset syntax, Arc Testnet USDC asset, exact quoted amount, and Gateway contract before invoking the buyer helper.

The Node buyer helper uses only Circle's **Developer-Controlled Wallet EOA** model. It uses `@circle-fin/developer-controlled-wallets@10.8.0` and `@circle-fin/x402-batching@3.4.0`. The pre-implementation gate proved that the pinned `GatewayClient` cannot accept a Circle signer because it requires a raw private key, so the implementation uses the supported lower-level `BatchEvmScheme({ address, signTypedData })` path. Circle signing uses `client.signTypedData({ walletId, data, memo })`; no private key is requested or exported.

The helper validates that `CIRCLE_ARC_WALLET_ID` resolves to the configured `CIRCLE_ARC_WALLET_ADDRESS` on `ARC-TESTNET` before signing. It performs only a read-only Gateway available-balance check. Wallet creation, faucet funding, approval, and Gateway deposit are setup actions and are not performed in the purchase path.

The helper now emits an explicit phase envelope: `pre_sign` with affirmative `signing_started=false` and `payment_submitted=false` is the only structured state that permits a pre-attempt failure. Completed payments use `phase=complete` and `commitment_status=committed`. Missing, malformed, contradictory, killed, timed-out, or nonzero/no-JSON helper output defaults to `ArcPaymentCommitmentUnresolvedError`; it is never treated as zero spend or retried.

The Arc price-to-atomic conversion uses the Decimal coefficient/exponent tuple directly. It does not multiply, quantize, round, or use float under the ambient Decimal context, and rejects values that are not exactly representable at six USDC decimal places.

After the signed paid request returns, the helper parses and validates `PAYMENT-RESPONSE` before branching on service HTTP status. An accepted payment with a 2xx service response requires the deterministic demo service-result contract and an explicit `positive_market_signal`, `neutral`, or `negative` outcome. An accepted payment with HTTP 500 or 404 returns a failed receipt with the exact committed cost, reference, status, and structured service failure. It is not unresolved. The validated service result is retained in immutable evidence.

The opt-in smoke report now includes the wallet model and safe address, quote, current probability, incremental expected value, TASK-006 decision, execution status, committed testnet-USDC amount, payment reference, service result, and TASK-009 state/probability. Missing setup still blocks before payment.

The documentation records TASK-015, the architecture boundary, the verbatim authorization prompt, and the pending Codex review. Stale status wording that described merged PR #37 as an unmerged review branch was corrected minimally in the current-status documents.

## 3. Why the change was needed

TASK-010 supplied an Arc scaffold and a safe credential-blocking smoke, but it did not yet provide a sufficiently strict, truthful Arc x402 acceptance contract. In particular, it accepted a loosely described helper result, used a nonce as a fallback reference, did not require the seller's x402 v2 batching metadata to match the selected Arc offer, and did not report the economic decision fields required by the authorized smoke.

The official current Circle path makes the Developer-Controlled Wallet EOA the shortest supported model for this slice. Circle's Arc examples pair that wallet model with Gateway/x402 batching. Circle Agent Wallet is a separate CLI/email-OTP product and is not mixed into this runtime.

## 4. How the system worked before

Before TASK-015, the Python package could create a separate Arc demo offer and delegate payment to a Node helper. The normal loop already selected before executing and TASK-009 already owned evidence interpretation. However, the helper did not require all authoritative Arc x402 fields, and if the seller omitted a `PAYMENT-RESPONSE` reference it could fall back to the authorization nonce. That fallback was not an authoritative settlement reference and was unsafe for the requested demonstration.

The previous smoke reported only a small subset of the economic and payment facts. It correctly stopped when credentials or the seller URL were absent, but it could not show all required decision and reference fields after a successful run.

## 5. How it works now

The selected capability is constructed with an exact positive decimal USDC quote. TASK-008 retains the seller URL and payment metadata outside the Candidate. TASK-006 sees only the stable candidate ID, exact `Money` cost, and declared post-action probability. It cannot see provider, wallet, network, or asset identity.

TASK-007 supplies the executor with the selected candidate and the exact maximum authorized cost. The Arc executor resolves that ID to the retained offer and refuses any mismatch before starting the helper. The helper checks the seller's initial 402 response, selects one exact Arc requirement, signs through the Circle EOA, retries with `PAYMENT-SIGNATURE`, and requires a successful `PAYMENT-RESPONSE` containing a transaction/payment reference.

The successful response is normalized into an exact `CirclePaymentReceipt` with the selected amount and immutable evidence. TASK-007 applies the committed cost to its existing ledger. TASK-009 reads the evidence and returns the next declared probability and state. A later TASK-006 decision therefore sees the updated probability through the existing provider-neutral loop.

## 6. Important inputs and state

| Input or state | Meaning |
|---|---|
| `eip155:5042002` | Arc Testnet x402 network |
| `ARC-TESTNET` | Circle Developer-Controlled Wallet blockchain identifier |
| `5042002` | Arc EVM chain ID |
| `0x3600000000000000000000000000000000000000` | Arc Testnet USDC ERC-20 interface |
| `0x0077777d7EBA4688BDeF3E311b846F25870A19B9` | GatewayWallet and EIP-712 verifying contract |
| `26` | Circle Gateway domain |
| `exact` + `GatewayWalletBatched` | x402 payment scheme and batching metadata |
| six-decimal atomic units | Exact USDC payment accounting |
| `CIRCLE_API_KEY`, `CIRCLE_ENTITY_SECRET` | Circle SDK credentials, environment-only |
| `CIRCLE_ARC_WALLET_ID` | Required pre-provisioned Circle wallet ID used for signing |
| `CIRCLE_ARC_WALLET_ADDRESS` | Required matching Arc EOA signer address |
| `RADHANITE_ARC_RESOURCE` | Explicit x402 seller URL |
| `RADHANITE_ARC_PRICE` | Exact pre-purchase decimal quote |

The Radhanite budget is an economic permission ceiling. The Circle Gateway balance is a separate wallet/payment fact. Neither replaces the other.

## 7. Decisions and outputs

The system makes two independent decisions. TASK-006 decides whether the exact quoted capability is economically worth buying. Circle's x402/Gateway system decides whether the signed payment can be accepted and settled. Radhanite does not rank by wallet or provider identity.

A successful output contains the validated service result, exact committed testnet-USDC amount, and Gateway payment/transaction reference. Evidence also records that the reference means Gateway acceptance and does not assert later on-chain finality without separate transfer evidence. Neutral or negative service results are retained as non-success evidence and do not emit `positive_market_signal`.

## 8. Failure modes

A malformed or wrong Arc asset, Base network, wrong network, wrong scheme, wrong batching metadata, wrong Gateway contract, wrong quote, or wrong authorization is rejected before signing or payment. A seller that does not expose exactly one matching x402 v2 requirement is rejected.

A setup or validation failure before signing is reported as a pre-attempt blocker only through the affirmative `phase=pre_sign` envelope. If the helper crashes, times out, is killed, emits no JSON, emits malformed JSON, or returns contradictory metadata after startup, the adapter raises `ArcPaymentCommitmentUnresolvedError`. The generic run does not record invented zero spend and does not retry.

## 9. Tests and verification

The focused Arc suite passes **21 tests**, and the focused Arc + Circle suite passes **54 tests** after the Codex corrections. The full Python 3.12 suite passes **779 tests**. The Node contract test covers the exact wallet ID, signer address, payment-response amount/wallet validation, and service-result contract.

```text
PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest discover -q
```

Python compilation and Node `--check` syntax validation pass for the changed runtime and helper files. The pinned SDK package declarations were inspected from the npm registry. The repository's `node_modules` directory was not required for syntax validation.

The explicit smoke was run without credentials or a seller URL. It returned a safe blocker report requiring `CIRCLE_API_KEY`, `CIRCLE_ENTITY_SECRET`, `CIRCLE_ARC_WALLET_ID`, `CIRCLE_ARC_WALLET_ADDRESS`, `RADHANITE_ARC_RESOURCE`, `RADHANITE_ARC_PRICE`, an Arc Testnet EOA, Circle Faucet testnet USDC, and Gateway balance. It exited before payment. **No live Arc payment, committed amount, or settlement reference has been observed in this checkout.**

## 10. Assumptions

The selected seller supplies the current Circle x402 v2 GatewayWalletBatched requirement shape. A seller URL may be a separately identified official/demo Arc service because current Circle Discovery did not establish an Arc listing for the selected resource. No Circle Marketplace provenance is claimed for that seller.

The helper's returned transaction/payment reference is treated as Gateway acceptance metadata. Later on-chain finality requires separate authoritative transfer evidence and is intentionally not invented by this task.

## 11. Known limitations

The live smoke remains credential, wallet-funding, Gateway-balance, and seller-URL gated. This PR does not claim a live settlement. The local demo seller is hackathon test infrastructure, not a Circle Discovery listing. The Arc helper currently supports the explicit GET smoke path and does not generalize request bodies or multichain routing.

## 12. Explicitly out of scope

This PR does not change TASK-006 economics, add a generic wallet abstraction, add a retry engine, add a wallet policy engine, store production credentials, build a UI, add The Graph or Hedera, or modify the merged Base adapter. It does not implement on-chain settlement infrastructure or claim testnet USDC is production value.

## 13. Deferred work

A successful live smoke requires human setup and explicit opt-in. A future task may add authoritative post-acceptance transfer verification if the product owner wants that distinction demonstrated on-chain. No such work is silently included here.

## 14. Codex correction status

| Finding | Status |
|---|---|
| `CODEX-PR038-01` — context-independent exact atomic conversion | Resolved with coefficient/exponent decomposition and hostile Decimal-context tests |
| `CODEX-PR038-02` — helper crash and explicit failure phase | Resolved with affirmative `pre_sign` envelope and unresolved-by-default failures |
| `CODEX-PR038-03` — service-result validation and evidence retention | Resolved with deterministic demo contract, outcome mapping, and full service-result evidence |
| `CODEX-PR038-04` — payment response before service status | Resolved with payment/reference validation before 2xx/4xx/5xx branching |

Independent Codex review remains pending; this correction commit does not merge the PR.

## 15. How to explain this to a judge

Radhanite does not blindly spend because a wallet exists. It first receives an exact Arc Testnet price, puts only the economic fields into the generalized selector, and pays only if TASK-006 says the purchase is worth it. Circle's Developer-Controlled Wallet EOA signs the selected x402 payment, Gateway returns the service result and acceptance reference, and TASK-007 records the exact testnet-USDC amount. TASK-009 then turns the result into evidence for the next economic decision. The repository tests that safety path with mocks; the live smoke is deliberately opt-in and honestly reports setup blockers rather than pretending a payment occurred.

**Implementation agent: Manus.**

## References

[1]: https://developers.circle.com/wallets/dev-controlled-wallets "Circle Developer-Controlled Wallets documentation"
[2]: https://developers.circle.com/gateway "Circle Gateway documentation"
[3]: https://github.com/circlefin/arc-x402-circle-wallets "Circle Arc x402 wallet example"
[4]: https://github.com/akelani-circle/arc-nanopayments "Circle Arc nanopayments example"
[5]: https://github.com/circlefin/arc-commerce "Circle Arc Commerce example"
[6]: https://faucet.circle.com "Circle Faucet for testnet USDC"
[7]: https://x402.org "x402 protocol documentation"

**Implementation agent: Manus.**
