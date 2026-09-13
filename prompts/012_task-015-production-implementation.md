Implementation agent: Manus.

AUTHORIZE TASK-015 PRODUCTION IMPLEMENTATION — ARC TESTNET EXECUTION PATH.

Repository:
therealgulkorinaga/radhanite-ethonline

Production checkout baseline:

e5fdd4349a294403f27b353280f1722759743b0b

The TASK-015 pre-implementation SDK gate has PASSED.

Human product owner / merge authority: Arko.
Independent reviewer: Codex.

Create a new branch and one new unmerged PR.

Suggested branch:

task-015-circle-arc-execution

AUTHORIZED IMPLEMENTATION PATH

Implement exactly the proven path:

TASK-008 priced Arc capability
→ TASK-006 economic selection
→ TASK-007 selected-only execution
→ Circle Developer-Controlled Wallet EOA
→ BatchEvmScheme with injected Circle signTypedData
→ x402 exact payment
→ Arc Testnet
→ exact committed testnet-USDC + authoritative payment/reference
→ capability result
→ TASK-009 evidence/state update

Do not use GatewayClient.

Do not request or export a private key.

PINNED DEPENDENCIES

Use:

@circle-fin/developer-controlled-wallets@10.8.0

@circle-fin/x402-batching@3.4.0

Do not upgrade these during TASK-015.

WALLET / SIGNER CONTRACT

Required configuration:

CIRCLE_API_KEY

CIRCLE_ENTITY_SECRET

CIRCLE_ARC_WALLET_ID

CIRCLE_ARC_WALLET_ADDRESS

RADHANITE_ARC_RESOURCE

RADHANITE_ARC_PRICE

Use:

CIRCLE_ARC_WALLET_ID

for Circle signing.

Use:

CIRCLE_ARC_WALLET_ADDRESS

as the x402 signer EOA address.

Verify that the wallet resource referenced by walletId corresponds to the configured address before allowing a live payment.

SIGNING PATH

Circle signing must use:

client.signTypedData({ walletId, data, memo })

Inject that signer into:

new BatchEvmScheme({ address, signTypedData })

Payment payload creation must use the proven x402 v2 path:

createPaymentPayload(2, paymentRequirements)

Do not use a raw private key anywhere.

Do not add a generic signer abstraction beyond what TASK-015 needs.

ARC EIP-712 REQUIREMENTS

Validate before signing:

primaryType = TransferWithAuthorization

Domain:

name = GatewayWalletBatched

version = 1

chainId = 5042002

verifyingContract = 0x0077777d7EBA4688BDeF3E311b846F25870A19B9

Validate authorization fields:

from
to
value
validAfter
validBefore
nonce

Any mismatch must fail before calling Circle signing.

NETWORK / ASSET

Use only:

x402 network:

eip155:5042002

Circle blockchain:

ARC-TESTNET

Arc Testnet USDC:

use the exact officially documented address already frozen in TASK-015.

Validate EVM address syntax and compare addresses case-insensitively after validation.

No Base fallback.

No multichain abstraction.

GATEWAY FUNDING MODEL

The purchase runtime assumes a pre-provisioned and pre-funded Gateway balance.

The following remain outside TASK-006 and outside the Radhanite spending ledger:

wallet creation
faucet funding
USDC approval
Gateway deposit

Do not automatically perform these inside the purchase path.

Add a readiness check that reports whether the required setup is missing before economic execution.

If Gateway balance cannot be checked without additional scope, fail with a precise setup blocker instead of trying to fund automatically.

CAPABILITY / CANDIDATE

RADHANITE_ARC_RESOURCE defines the Arc x402 resource.

RADHANITE_ARC_PRICE defines the exact pre-purchase demo quote.

This exact positive price must be normalized through TASK-008 before TASK-006 evaluates it.

Keep seller/network/asset/payment metadata outside Candidate.

TASK-006 must see only its existing allowed fields:

candidate ID
exact cost
expected post-action success probability
ECONOMIC ORDERING

No wallet, Circle SDK, x402 signer, or HTTP payment action may occur before TASK-006 selects the capability.

Required order:

construct exact Arc offer
normalize via TASK-008
evaluate/select via TASK-006
if not selected: no wallet/payment call
if selected: TASK-007 invokes Arc executor

Non-selected offers must never cause signing.

PAYMENT EXECUTION

The Arc executor must:

resolve selected Candidate back to exact retained Arc offer
validate authorization ceiling
validate network
validate asset
validate scheme/version/batching/verifying contract
validate exact amount
create x402 v2 payment payload
sign EIP-712 via Circle signTypedData
submit the paid request
capture service response
capture authoritative payment/Gateway reference
return exact committed cost
ACCOUNTING / AMBIGUITY

Preserve PR #37 safety semantics:

If payment was definitely not attempted:

pre-attempt error / zero spend is valid.

If payment may have been signed/submitted but exact commitment cannot be established:

raise an unresolved-commitment error.

Do not:

record zero spend
invent committed cost
retry automatically

A successful execution must have:

exact selected amount
successful service response
authoritative payment or Gateway reference

Do not describe Gateway acceptance/reference as onchain finality unless actual onchain confirmation is separately available.

TASK-009 HANDOFF

Successful Arc execution should create the existing immutable evidence structure.

Preserve:

make_evidence(...)

The Arc adapter must NOT:

change success probability
mark task complete
choose the next candidate

TASK-009 interprets the evidence.

The subsequent TASK-006 decision must observe the updated TASK-009 state/probability.

LIVE SMOKE

Add one explicit opt-in command:

PYTHONDONTWRITEBYTECODE=1 python3.12 -m radhanite.arc_smoke

Running this command is explicit human authorization for one Arc Testnet purchase up to the exact displayed selected quote.

Before asking for signing, print:

wallet model
wallet address
Arc network
capability/resource
exact testnet-USDC quote
current success probability
expected post-action probability
incremental expected value
maximum authorized spend
TASK-006 selection result

Then execute only if selected.

After execution print:

payment/Gateway reference
exact committed testnet-USDC
service-result summary
TASK-009 updated state/probability

Never print:

API key
entity secret
raw signing material
private key
BLOCKER BEHAVIOR

If live execution cannot proceed, report the exact blocker.

Examples:

missing CIRCLE_API_KEY
missing CIRCLE_ENTITY_SECRET
missing wallet ID/address
wallet ID/address mismatch
Arc wallet not provisioned
insufficient testnet USDC
Gateway deposit missing
missing seller resource

Do not silently use Base.

Do not provision or fund automatically inside the purchase run.

TESTS

Preserve all existing repository tests.

Add critical TASK-015 coverage for:

Circle signer invoked with exact wallet ID
x402 signer exposes matching wallet address
wallet ID/address mismatch rejected before signing
valid Arc x402 requirement accepted
Base network rejected
wrong chain ID rejected
wrong USDC asset rejected
wrong GatewayWalletBatched domain rejected
wrong EIP-712 version rejected
wrong verifying contract rejected
exact six-decimal amount preserved
non-selected candidate never signs
selected candidate signs only after TASK-006
authoritative successful result records exact committed cost/reference
ambiguous post-signing state fails unresolved
no automatic retry after ambiguity
service result becomes TASK-009 evidence
TASK-009 update reaches the next TASK-006 decision

Mock external Circle and seller calls in normal tests.

PACKAGE / RUNTIME BOUNDARY

Keep the Node/Circle/x402 bridge as narrow as possible.

Python remains responsible for:

economic selection
TASK-007 run state
exact ledger accounting
TASK-009 evidence/state

Node helper is responsible only for:

Circle Developer-Controlled Wallet signing
BatchEvmScheme/x402 payload handling
paid HTTP request
returning structured authoritative execution metadata

The Node helper must return structured JSON to Python.

No business/economic decision logic in Node.

DOCUMENTATION

Update TASK-015 and architecture docs with the proven gate findings:

GatewayClient intentionally not used because it requires privateKey
Developer-Controlled Wallet signing uses walletId
x402 scheme uses matching EOA address
BatchEvmScheme is the supported lower-level composition path
Gateway deposit is prerequisite setup
no private key export

Preserve:

Implementation agent: Manus.

in all required implementation progress, commit, PR explanation and handoff artifacts.

GIT / PR

Create a branch from:

e5fdd4349a294403f27b353280f1722759743b0b

Suggested:

task-015-circle-arc-execution

Create one new PR.

Do not merge.

REPORT

Report back:

branch
PR number
head SHA
files changed
pinned package versions
exact Python ↔ Node boundary
exact Circle signing API used
exact BatchEvmScheme integration
Arc requirement validation implemented
final test count
live smoke status
wallet readiness status
Gateway readiness status
quoted testnet-USDC
committed amount/reference if smoke succeeds
exact human setup blocker if smoke cannot run

End with:

Implementation agent: Manus.

Then stop.

One extra note: do not let Manus turn “Gateway deposit required” into a side quest. If the implementation is complete and the only blocker is funding/deposit setup, that’s a good stopping point. We can handle the wallet/Gateway setup manually, run the live smoke, Codex the actual execution boundary, then merge.