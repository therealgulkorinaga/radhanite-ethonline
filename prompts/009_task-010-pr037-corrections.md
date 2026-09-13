# 009 — TASK-010 PR #37 Codex corrections

**Date:** 2026-09-13
**Agent:** Manus
**Authority:** Arko authorization for CODEX-PR037-01, CODEX-PR037-02, and CODEX-PR037-03
**Resulted in:** Narrow corrections to the existing TASK-010 PR #37 branch only.

## Prompt

> Implementation agent: Manus.
>
> AUTHORIZE NARROW CORRECTIONS TO PR #37 ONLY — CODEX-PR037-01, 02, 03.
>
> Current PR:
>
> #37 — TASK-010: Circle marketplace and Arc payment adapter
>
> Do not start a new PR.
>
> Do not merge.
>
> Do not add Graph, Hedera, UI, persistence, retries, or generic payment abstractions.
>
> Human product owner / merge authority: Arko.
>
> Independent reviewer: Codex.
>
> OBJECTIVE
>
> Fix only:
>
> CODEX-PR037-01 — authoritative CLI JSON parsing / ambiguous post-payment failure accounting
>
> CODEX-PR037-02 — offer network vs CLI chain mismatch
>
> CODEX-PR037-03 — atomic amount + USDC asset validation / exact conversion
>
> Preserve all already-correct TASK-010 behavior.
>
> CODEX-PR037-01 — PARSE OFFICIAL CLI JSON
>
> Current substring matching is not acceptable for payment accounting.
>
> Replace it with parsing of the official Circle CLI JSON envelope.
>
> Required behavior
>
> On CLI success:
>
> parse JSON;
>
> extract the authoritative payment metadata;
>
> validate:
>
> amount
>
> chain/network
>
> scheme
>
> derive committed_cost from the authoritative result, not blindly from the quote if the result exposes the actual amount;
>
> reject any mismatch with the selected/authorized offer.
>
> On non-zero CLI exit:
>
> parse structured JSON if present;
>
> distinguish:
>
> definitively pre-attempt / no commitment
>
> definitively committed/submitted payment with known amount
>
> ambiguous potentially-charged state
>
> The current Circle guidance explicitly includes a failure state equivalent to:
>
> PAYMENT MAY HAVE BEEN SUBMITTED
>
> This must never become CirclePreAttemptError.
>
> Ambiguous commitment
>
> If the CLI indicates payment may have been submitted but the exact committed amount cannot be established:
>
> do not fabricate zero spend;
>
> do not fabricate full quoted spend;
>
> do not describe accounting as exact;
>
> fail closed with a dedicated provider/accounting state that clearly says commitment is unresolved.
>
> Because TASK-007 requires exact committed-cost accounting, do not convert an unknown amount into a normal ExecutionResult.
>
> It is acceptable for this unresolved condition to abort the live smoke path with an explicit:
>
> payment may have been submitted; exact commitment unresolved; inspect Circle payment records
>
> provided the docs are truthful that this state cannot be safely committed into the generic run ledger.
>
> Do not use arbitrary substring matching as the accounting source of truth.
>
> Tests
>
> Add cases for:
>
> successful official JSON envelope with exact payment amount
>
> successful envelope amount mismatch
>
> successful envelope chain mismatch
>
> successful envelope scheme mismatch
>
> definite pre-attempt failure
>
> definite committed/submitted failure with authoritative amount
>
> ambiguous payment may have been submitted failure with unknown exact amount
>
> arbitrary unrelated text containing paymentSubmitted must not fabricate spend
>
> CODEX-PR037-02 — NETWORK / CHAIN MUST MATCH
>
> The payment chain must come from, or be checked against, the selected CircleOffer.
>
> Do not allow:
>
> Base offer + MATIC
>
> Base offer + Arc
>
> Arc offer + default Base
>
> any other silent mismatch
>
> Preferred implementation
>
> Derive the CLI chain from the selected offer network using one explicit mapping.
>
> Example conceptually:
>
> eip155:8453 -> BASE
>
> Add only mappings that are actually supported and documented.
>
> If an override remains available, it must be exact-match validated before runner invocation.
>
> Mainnet safety
>
> Apply the payment confirmation/safety guard to the actual CLI payment chain, not merely the discovery network.
>
> A mismatch must fail before any runner/subprocess invocation.
>
> Tests
>
> Add:
>
> Base offer derives/uses BASE
>
> Base offer + MATIC override rejected before runner
>
> unsupported network rejected before runner
>
> mainnet confirmation guard evaluates actual payment chain
>
> CODEX-PR037-03 — ATOMIC AMOUNT + USDC ASSET VALIDATION
>
> Before creating Money from a Circle/x402 offer:
>
> Amount
>
> Require amount to be:
>
> exact string
>
> non-empty
>
> decimal digits only
>
> positive integer atomic units
>
> Reject:
>
> fractional atomic values such as "1.5"
>
> negative
>
> exponent notation
>
> whitespace
>
> floats/ints supplied as JSON types if the x402 schema expects string
>
> Asset
>
> Validate the accepted asset against the supported USDC asset for the selected network.
>
> For the current Base-mainnet benchmark:
>
> verify against the documented Base USDC contract.
>
> Do not treat arbitrary ERC-20 addresses as USDC.
>
> Exact conversion
>
> Do not use ambient Decimal context in a way that can round.
>
> Convert integer micro-units exactly.
>
> Preferred approach:
>
> parse atomic units as integer
>
> construct decimal representation exactly from integer quotient/remainder, or equivalent context-independent method
>
> 12000 atomic micro-USDC must become exactly:
>
> 0.012
>
> and large values must preserve all 6 decimal places exactly.
>
> Tests
>
> Add:
>
> "12000" -> exact 0.012
>
> "1" -> exact 0.000001
>
> "123456789" -> exact 123.456789 even under deliberately tiny Decimal context precision
>
> "1.5" rejected
>
> wrong asset rejected
>
> zero rejected
>
> malformed amount rejected
>
> PRESERVE
>
> Preserve:
>
> live Circle Discovery
>
> TASK-008 normalization
>
> provider-neutral Candidate
>
> benchmark probability supplied externally
>
> selection before payment
>
> TASK-007 authorization ceiling
>
> TASK-009 evidence handoff
>
> no dependencies if possible
>
> Do not claim Arc is integrated.
>
> Current verified state remains:
>
> Circle Discovery: live
>
> Gateway/x402: adapter implemented
>
> live payment: not yet verified
>
> Arc: not used
>
> DOCUMENTATION
>
> Update PR #37 docs/review/explanation to reflect:
>
> structured CLI JSON is authoritative
>
> ambiguous possibly-charged failures cannot be entered into exact TASK-007 accounting
>
> actual payment chain must match selected offer
>
> supported USDC asset is validated
>
> atomic-unit conversion is exact
>
> Preserve:
>
> Implementation agent: Manus.
>
> VERIFY
>
> Run:
>
> PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest discover -q
>
> Re-run the focused TASK-010 suite.
>
> No live payment is required for this correction if credentials remain unavailable.
>
> REPORT
>
> Push to existing PR #37.
>
> Do not merge.
>
> Report:
>
> new head SHA
>
> files changed
>
> final full-suite count
>
> exact JSON fields used for authoritative payment accounting
>
> exact behavior for ambiguous “may have been submitted” failure
>
> chain/network mapping adopted
>
> supported USDC asset validation adopted
>
> exact atomic-unit conversion method
>
> status of all three findings
>
> End with:
>
> Implementation agent: Manus.
>
> Then stop.

## Notes

The later architectural suggestion to broaden TASK-010 toward developer-controlled wallets and Arc testnet is outside this narrow correction authorization. This branch preserves the verified Base Discovery/CLI boundary and does not claim Arc integration.
