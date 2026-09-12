# 008 — TASK-010 Circle marketplace and Arc payment adapter

**Date:** 2026-09-13
**Agent:** Manus
**Authority:** Arko authorization for TASK-010
**Resulted in:** A thin live Circle Discovery and opt-in official CLI x402/Gateway adapter boundary on the review branch.

## Prompt

Implementation agent: Manus.

AUTHORIZE TASK-010 — CIRCLE MARKETPLACE + ARC PAYMENT ADAPTER. HACKATHON CRITICAL PATH.

Human product owner / merge authority: Arko.

Independent reviewer: Codex.

This prompt is the human authorization that TASK-010 currently lacks in the repository.

Branch from fresh main.

Suggested branch:

task-010-circle-arc-adapter

Before editing:

verify PR #36 / TASK-009 is merged into main;
run the full suite;
read:
TASK-008_CAPABILITY_ACQUISITION.md
TASK-010_CIRCLE_MARKETPLACE_ADAPTER.md
TASK-007_CAPABILITY_RUN_LOOP.md
radhanite/acquisition.py
radhanite/capability_execution.py
radhanite/loop.py
radhanite/revenue.py
inspect the current official Circle documentation for Agent Marketplace / service discovery / Arc / x402 / Nanopayments that is actually available today.

Do not rely on remembered or outdated Circle API shapes.

If the repository specification names a Circle surface that is not currently usable, do not fabricate it. Use the closest currently documented Circle mechanism and record the deviation truthfully.

HACKATHON GOAL

Build one thin real integration proving:

Circle tells Radhanite what it can buy and what it costs.
Radhanite decides whether it is worth buying.
Only after selection does the Circle/Arc execution/payment path run.

We do not need a production marketplace framework.

We need one end-to-end path that can be demonstrated reliably.

TWO SEPARATE RESPONSIBILITIES

Keep these distinct.

A. Discovery

Obtain a machine-readable capability/service offer and its price/payment terms.

Convert it through the existing TASK-008 boundary:

external Circle descriptor

→ CapabilityDescriptor

→ three-field TASK-006 Candidate

Do not put Circle/provider/payment fields into Candidate.

B. Execution / payment

Only after TASK-006 selects the candidate:

execute/invoke the chosen service;
perform the real supported Circle/Arc testnet payment flow where available;
return exact ExecutionResult;
report actual committed_cost;
return evidence usable by the TASK-009 boundary.

Selection must happen before payment.

DISCOVERY STRATEGY

Prefer live Circle discovery.

Time-box live marketplace discovery work.

If the current official Circle Marketplace/Discovery API is accessible and practical with available credentials:

use it live;
fetch at least one real capability/service;
read exact quoted price/payment terms before purchase.

If live discovery is unavailable, inaccessible, undocumented, or would consume disproportionate hackathon time:

use a captured Circle discovery response/snapshot taken from a real documented/current response or actual successful discovery;
label it explicitly as captured discovery;
do not call it live discovery in the README/demo.

A captured discovery snapshot is acceptable for discovery only.

We still want the execution/payment path real if Circle/Arc permits it.

Do not fabricate marketplace listings.

PRICE CONTRACT

This is non-negotiable:

exact price must be known before TASK-006 selection.

Discovery/quoting must not itself commit payment.

TASK-008 candidate cost must equal the exact pre-purchase quote used for authorization.

Never:

estimate price;
infer price after execution;
hide metered pricing uncertainty;
let an unknown-price service enter TASK-006.

If a Circle service cannot expose an exact maximum cost before purchase, exclude it from this hackathon candidate path.

SUCCESS-PROBABILITY FIXTURE

Circle does not determine the candidate's expected post-action success probability.

That remains a benchmark-declared Radhanite fixture.

Therefore keep:

Circle = capability metadata + price/payment terms
benchmark configuration = expected post-action success probability

Compose them only at TASK-008 normalization.

Do not claim Circle supplied the probability.

Do not infer it from marketplace metadata.

ADAPTER SHAPE

Build the smallest provider-specific adapter needed to satisfy:

TASK-008 capability acquisition/source boundary
TASK-007 CapabilityExecutor

The adapter may retain provider-specific information internally, such as:

Circle service/listing ID
endpoint/invocation metadata
payment terms
Arc network/payment metadata

None of those fields may enter TASK-006 Candidate.

Maintain a safe mapping from stable candidate ID back to the discovered Circle descriptor required for execution.

ONE REAL CAPABILITY

For TASK-010, integrate one useful capability only.

Prefer an actually available marketplace service relevant to the revenue-agent benchmark, such as:

research/search;
market/company research;
inference/analysis;
another current Circle Marketplace capability that can produce useful commercial evidence.

Do not integrate five services just because they exist.

One reliable real purchase is worth more than a broad brittle adapter.

EXECUTION RESULT

Respect the PR #34 executor contract completely.

Before side effects:

executor receives/derives the explicit maximum_authorized_cost;
payment cannot exceed it.

After an actual attempt:

success/failure must return exact ExecutionResult;
committed_cost must be the actual committed amount;
post-attempt failures must be normalized rather than leaking a raw exception;
raw exception is only allowed before attempt/commitment begins.

No silent clamping.

No fabricated spend.

ARC / MONEY TRUTHFULNESS

If using Arc testnet:

state explicitly:

this is testnet value / testnet USDC, not production money.

Never describe Arc testnet assets as real production-value USDC.

Record:

chain/network used;
transaction/payment identifier if available;
amount;
service/capability purchased.

Keep secrets and credentials in environment variables.

Never commit private keys, API keys, wallet secrets, bearer tokens, or seed material.

EVIDENCE INTO TASK-009

Keep provider execution output and benchmark interpretation conceptually separate.

The Circle adapter may construct the provider-neutral benchmark evidence envelope required by TASK-009, but:

it must not update probability itself;
it must not declare task completion itself;
it must not perform economic selection;
it must not decide whether another capability should be bought.

TASK-009 remains the interpreter.

If a tiny mapping from a known demo capability result into an authorized TASK-009 evidence outcome_key is necessary for the vertical slice, keep it explicit and fixture-driven.

Do not build generic LLM interpretation machinery.

INTEGRATED DEMO TEST

Add at least one end-to-end test/demo path showing:

Circle capability discovered/loaded with exact price.
TASK-008 normalizes it into Candidate.
TASK-006 evaluates it economically.
If eligible, TASK-006 selects it.
TASK-007 calls the Circle executor only after selection.
Circle/Arc execution/payment completes or returns normalized failure.
Exact committed cost is recorded.
Evidence reaches TASK-009.
Opportunity probability/state updates.
TASK-007 reaches the next economic decision.

Mock external Circle network calls in ordinary unit tests.

Separately provide one live smoke/integration command that can be run with credentials.

Tests must never require secrets to run the normal 725+ test suite.

LIVE SMOKE TEST

Provide a deliberately explicit opt-in command such as:

python -m ...circle_smoke

or equivalent existing repo convention.

It should:

require environment credentials;
fail clearly when credentials are missing;
never run automatically in unit tests;
print enough non-secret information to demonstrate:
capability/service
pre-purchase quoted/max price
selected candidate ID
transaction/payment result
committed cost
evidence/result summary

Do not print secrets.

FALLBACK HIERARCHY

If Circle surfaces create blockers, follow this order:

Preferred

live Circle discovery + real Arc/testnet execution/payment

Acceptable

captured real Circle discovery + real Arc/testnet execution/payment

Last-resort hackathon fallback

captured discovery + adapter execution against the real service, with payment component clearly represented as unavailable/not completed

If you reach fallback 3:

STOP and report before pretending TASK-010 is complete.

We need to know immediately because sponsor eligibility may be affected.

DO NOT BUILD

Do not build:

your own marketplace;
your own wallet/custody system;
your own x402 protocol;
a generalized Circle SDK wrapper;
multiple payment rails;
retries;
production persistence;
UI;
Graph integration;
Hedera integration;
new probability logic;
generic agent framework.

TESTS — TIME-BOXED

Critical tests only:

Circle descriptor with exact price normalizes through TASK-008.
provider metadata does not enter Candidate.
discovery itself commits no payment.
unknown/non-exact price cannot become Candidate.
benchmark probability fixture is externally supplied, not Circle-derived.
candidate ID maps back to correct Circle execution descriptor.
non-selected Circle capability is never executed/paid.
selected capability receives correct maximum authorized cost.
execution cannot commit more than authorization.
successful execution records exact committed cost.
paid/attempted failure records actual committed cost.
pre-attempt failure causes no false spend record.
credentials are environment-only.
resulting evidence can be consumed by TASK-009.
one TASK-006/007/008/009 integration path works.

Do not spend hours on exhaustive mutation testing.

DOCUMENTATION

Update TASK-010 status to reflect this human authorization.

Document truthfully:

whether discovery is live or captured;
which Circle capability is used;
which Circle/Arc payment mechanism actually works;
network/testnet status;
exact distinction between quoted cost and committed cost;
environment variables required;
how to run the live smoke test.

Preserve the line:

Circle tells the agent what it can buy and how to pay. Radhanite decides what is worth buying.

Do not claim direct relationships with Tavily/BlockRun unless that is factually how the marketplace transaction works.

VALIDATE

Run:

PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest discover -q

All existing tests must remain passing.

Run the live smoke test separately if credentials/network access permit it.

Record both results separately:

deterministic unit/integration suite
live Circle/Arc smoke result

DELIVER

Open one PR.

Do not merge.

Report:

PR
branch
commit/head
files changed
exact Circle APIs/products used
live vs captured discovery status
capability/service used
quoted candidate cost
actual committed cost
Arc network/payment mechanism
transaction/payment reference if successful
environment variables required
final test count
live smoke result
any blocker that affects Circle sponsor eligibility

End with:

Implementation agent: Manus.

Then stop.

## Notes

Live Discovery was available and returned current Circle Marketplace resources. The live selected capability is an AIsa CoinGecko Simple Price endpoint on Base mainnet with Circle Gateway payment terms. The current live response did not establish an Arc Testnet Marketplace listing for that resource. No wallet credentials or Circle CLI were present, so the payment smoke was not run and no mainnet money was spent.
