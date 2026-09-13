mplementation agent: Manus.

AUTHORIZE NARROW CORRECTIONS TO PR #38 ONLY — CODEX-PR038-01 through CODEX-PR038-04.

Repository:
therealgulkorinaga/radhanite-ethonline

PR:
#38 — TASK-015: Circle Wallet + x402 + Arc Testnet Execution

Current reviewed head:
1dd3297b56a54acc3015c6c12af0d534f15386db

Do not create a new PR.

Do not merge.

Do not perform a live Arc payment yet.

Human product owner / merge authority: Arko.
Independent reviewer: Codex.

Fix only the four material findings below.

CODEX-PR038-01 — EXACT USDC ATOMIC CONVERSION

Current conversion is Decimal-context sensitive.

With hostile precision, e.g.:

Decimal context precision = 3

Money("123.456789")

must still convert to:

123456789

atomic units.

Required correction

Implement context-independent conversion using the Decimal value's exact coefficient/exponent representation or another exact integer/string decomposition.

Do not:

multiply under ambient Decimal context;
quantize using ambient context;
round;
use float.

Preserve exact six-decimal semantics.

Reject values that cannot be represented exactly at six USDC decimal places.

Tests

Add hostile-context tests:

123.456789 -> 123456789
0.000001 -> 1
0.012 -> 12000
low Decimal precision does not affect output
more than six fractional digits rejected if not exactly representable
CODEX-PR038-02 — HELPER CRASH AFTER SIGNING MUST FAIL UNRESOLVED

A nonzero helper exit with missing/malformed/non-JSON output cannot be assumed pre-attempt, because the helper process may have died after Circle signing/submission.

Required correction

Change the Python/Node failure contract so that only structured affirmative evidence that signing never began may produce a pre-attempt error.

Define an explicit structured helper state such as:

phase: "pre_sign"

or equivalent.

Python may classify zero-spend pre-attempt failure only if the helper returns a structured, valid envelope proving no signing/payment attempt occurred.

For:

process killed
timeout
nonzero exit with no JSON
malformed JSON
contradictory envelope
helper crash after startup with no trustworthy phase

default to:

ArcPaymentCommitmentUnresolvedError

not ordinary ArcPaymentError.

Do not retry.

Tests

Add:

killed-after-signing process -> unresolved
nonzero/no-JSON -> unresolved
malformed JSON -> unresolved
structured pre-sign validation failure -> pre-attempt/no spend
structured pre-sign credential failure -> pre-attempt/no spend
CODEX-PR038-03 — VALIDATE SERVICE RESULT BEFORE POSITIVE TASK-009 EVIDENCE

Current success handling is too permissive and can transform arbitrary service output into:

outcome_key="positive_market_signal"

That is not acceptable.

Required correction

Define one narrow, deterministic service-result contract for this demo.

The successful helper result must be internally consistent and must include:

commitment_status consistent with success
exact authorized amount_atomic
wallet/signer identity matching configured Arc wallet
authoritative payment/reference
service result matching the expected demo contract

Reject contradictory metadata.

In particular:

success + commitment_status: unresolved must fail
amount mismatch must fail
wallet/address mismatch must fail
missing authoritative payment reference must fail/unresolve as appropriate
Evidence

Retain the validated service result in immutable TASK-009 evidence.

Do not reduce the evidence to a generic “service received” fact while discarding the actual purchased result.

Outcome mapping

Do not hard-code positive_market_signal merely because HTTP/payment succeeded.

Emit positive_market_signal only when the validated service-result contract explicitly supports that outcome.

If the service call succeeds but the result is negative/neutral/non-supporting, map it to the appropriate existing TASK-009 behavior or preserve it as evidence without falsely advancing probability.

Do not invent a new probabilistic model.

Tests

Add:

success + unresolved commitment rejected
wrong amount rejected
wrong wallet rejected
malformed service result rejected
negative/neutral valid service result does not emit positive outcome
positive valid service result emits positive_market_signal
validated result is retained in immutable evidence
CODEX-PR038-04 — PARSE PAYMENT RESPONSE BEFORE SERVICE STATUS

The helper currently branches on non-2xx service status before extracting authoritative payment metadata.

This loses exact commitment information when:

payment succeeds

but

service execution fails.

Required correction

After the signed paid request returns:

parse PAYMENT-RESPONSE / authoritative payment metadata first;
validate payment/reference/amount if present;
only then branch on service HTTP status.

Required outcomes:

Payment accepted + service 2xx

Return successful receipt with exact committed cost/reference and validated result.

Payment accepted + service non-2xx

Return a failed execution receipt/result with:

exact committed cost
authoritative payment/reference
service failure status/details

Do not classify as unresolved.

Payment commitment unknown

Return unresolved commitment.

Definite pre-sign/pre-submit failure

Pre-attempt/no-spend remains valid.

Settlement amount

If the authoritative payment response exposes an amount:

compare it to the exact authorized atomic amount.

Any mismatch is material and must not be silently accepted.

Tests

Add:

payment accepted + service 500 -> failed execution with exact committed cost
payment accepted + service 404 -> failed execution with exact committed cost
payment response amount mismatch -> reject
no authoritative payment metadata after signed submission -> unresolved
success path still records exact cost/reference
PRESERVE

Do not regress:

pinned Circle SDK versions
Developer-Controlled Wallet path
BatchEvmScheme
no private key
TASK-006 selection before signing
non-selected candidate never pays
Arc-only network validation
exact Arc USDC validation
Gateway balance vs wallet balance distinction
no nonce fallback
no automatic retry
TASK-009 owns probability/state update
VERIFY

Run:

PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest discover -q

Re-run:

focused Arc tests
focused Arc + Circle tests
Node contract test against pinned installed SDKs

Do not run live payment.

REPORT

Push corrections to existing PR #38.

Do not merge.

Report:

new head SHA
files changed
final Python test count
focused test counts
Node contract result
exact atomic conversion method
exact helper failure-phase contract
exact service-result contract
exact behavior for payment-accepted/service-failed responses
explicit status of:
CODEX-PR038-01
CODEX-PR038-02
CODEX-PR038-03
CODEX-PR038-04

End with:

Implementation agent: Manus.

Then stop.