# 007 — TASK-009 revenue opportunity state and updater

**Date:** 2026-09-13
**Agent:** Manus
**Authority:** Arko authorization for TASK-009 implementation
**Resulted in:** Revenue-opportunity state, declared evidence transitions, benchmark initializer, TASK-007 updater, tests, and one end-to-end fixture path.

## Prompt

> The prompt as issued is appended below verbatim.

## Notes

The implementation is deliberately limited to declared benchmark fixtures. It does not add provider, payment, network, persistence, UI, CRM, or learned-probability functionality.

Implementation agent: Manus.

AUTHORIZE TASK-009 — REVENUE OPPORTUNITY STATE + UPDATER. HACKATHON CRITICAL PATH.

Human product owner / merge authority: Arko.

Independent reviewer: Codex.

Time is constrained. Optimize for a correct end-to-end hackathon demo, not production generality.

Branch from fresh main after PR #35 is merged.

First verify:

PR #35 is present on main
TASK-007 final generic loop is merged
full test suite passes
TASK-007 exposes the generic TaskStateUpdater / TaskStateUpdate boundary

If not, stop and report.

GOAL

Implement the revenue-opportunity-specific state and updater used by the ETHOnline benchmark.

TASK-009 is the domain layer that answers:

After a capability returns evidence, what changed about this commercial opportunity?

It must convert capability evidence into:

updated opportunity state
updated declared success probability
task-complete verdict

It must not decide which capability to buy.

TASK-006 remains the economic decision maker.

TASK-007 remains the generic orchestration loop.

BENCHMARK

Current ETHOnline benchmark:

An autonomous revenue agent is pursuing a high-value crypto-native commercial opportunity with a bounded operating budget.

Representative demo:

opportunity value: $50,000
operating budget: $250
initial declared success probability: approximately 0.07–0.08
candidate capabilities may later include:
Circle/marketplace research
The Graph onchain intelligence
Hedera independent opportunity review

These values are benchmark fixtures.

Do not build probability prediction or ML.

TASK-009 STATE

Introduce the minimum immutable revenue-opportunity state required by the demo.

It should capture the domain facts needed for repeated capability decisions, for example:

opportunity identifier
prospect / opportunity description
current evidence
unresolved questions
completed capability results / findings where necessary
benchmark completion condition

Keep it minimal.

Do not turn this into a CRM.

Do not add sales pipeline stages, contacts, emails, outreach automation, forecasting, or generic CRM functionality.

The purpose is only to give candidate sources and the updater enough domain state to support the economic loop.

INITIALIZATION

TASK-009 owns the domain-specific initial completion determination that TASK-007 deliberately does not perform.

Provide a benchmark initializer that returns the appropriate initial RunState / state inputs.

It must:

create the immutable revenue opportunity state
set the declared initial success probability
determine whether the opportunity is already complete
if already complete, ensure TASK-007 receives authoritative RunStatus.TASK_COMPLETE
otherwise initialize RUNNING

This closes the boundary clarified by CODEX-PR035-01.

Do not inspect task state inside TASK-007.

PROBABILITY POLICY

For the hackathon, success probabilities are declared benchmark fixtures, not model-generated predictions.

Capability evidence may map deterministically to a new declared probability using scenario fixtures.

Example shape:

Graph result A -> probability 0.08 → 0.14

Hedera review B -> probability 0.14 → 0.17

but actual fixture values must live in TASK-009 / benchmark configuration, not inside TASK-006.

Do NOT:

ask an LLM to invent a probability
infer probability from prose ad hoc
let Graph/Hedera directly modify TASK-006
create learned scoring

Make the fixture nature obvious in code and documentation.

UPDATER

Implement the TASK-007 TaskStateUpdater boundary for revenue opportunities.

Conceptually:

update(previous_opportunity_state, execution_result) -> TaskStateUpdate

It must:

accept exact immutable revenue opportunity state
inspect the successful capability evidence
update the evidence / unresolved-question state
apply the declared benchmark probability transition
determine whether the benchmark task is complete
return TASK-007's generic TaskStateUpdate

Do not perform economic selection here.

Do not read capability price here.

Do not rank providers here.

CAPABILITY EVIDENCE CONTRACT

Define the smallest benchmark-level evidence format needed so later adapters can return results consistently.

It should distinguish capability identity/type from the evidence itself without contaminating TASK-006's Candidate.

Good examples:

capability key / evidence type
facts/findings
source reference if useful
benchmark outcome key used to map the fixture probability transition

Keep provider metadata outside the economic Candidate.

This evidence contract must be usable by:

Circle marketplace capability execution
The Graph
Hedera

without making TASK-009 depend directly on those providers.

DEMO SCENARIO

Implement at least one deterministic benchmark scenario that can eventually support:

Run A

Initial:

value = $50,000
budget = $250
probability = fixture P0

First useful capability result:

evidence updates opportunity
probability becomes P1

Second useful capability result:

evidence updates opportunity
probability becomes P2

Eventually:

task becomes complete OR
remaining capability uplift is economically unjustified and TASK-006 stops.

Do not hard-code provider order.

TASK-006 must still determine which capability is selected based on candidate economics.

IMPORTANT ARCHITECTURE

Preserve:

Circle/Arc

later supplies/discovers/buys capabilities

The Graph

later supplies onchain commercial evidence

Hedera

later supplies independent review evidence

TASK-009

interprets benchmark evidence into opportunity-state changes

TASK-006

decides whether purchasing a candidate is economically worthwhile

TASK-007

orchestrates the repeated run

Do not collapse these responsibilities.

TESTS — TIME-BOXED

Add the critical tests only:

initializer produces RUNNING for an incomplete opportunity
initializer produces TASK_COMPLETE for an already-complete opportunity
initial probability uses declared fixture exactly
successful evidence updates immutable opportunity state
declared probability transition applies exactly
completion evidence returns task_complete=True
non-completion evidence returns false and continues
unknown/malformed evidence is rejected deterministically
mutable evidence/state aliases do not survive
updater does not perform economic selection
updater does not use candidate cost
provider identity is not required by the generic economic layer
at least one TASK-007 end-to-end test runs with this real TASK-009 updater

Avoid exhaustive production hardening.

CRITICAL END-TO-END TEST

Add one integration test using:

TASK-006 selector
TASK-007 full loop
TASK-009 revenue opportunity initializer/updater
fixture candidate source
fixture executor results

The test must demonstrate:

evidence changes the opportunity → declared probability changes → TASK-006 makes the next economic decision using the new probability.

This is the central Radhanite behavior.

The candidate order must not be hard-coded by the updater.

DO NOT IMPLEMENT

Do not implement:

Circle API calls
Arc payments
x402
Graph API calls
Hedera calls
UI
persistence
CRM features
outreach
LLM-generated probability
learned scoring

Those come immediately after this task.

VALIDATE

Run:

PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest discover -q

All existing tests must remain passing.

No external dependency unless absolutely necessary; prefer none for TASK-009.

DELIVER

Open one PR.

Suggested branch:

task-009-revenue-opportunity-state

Do not merge.

Report:

PR
branch
commit
files changed
exact state model
initializer contract
updater contract
benchmark fixture probability transitions
E2E scenario demonstrated
final test count
blockers for Circle/Arc, Graph, or Hedera

End with:

Implementation agent: Manus.

Then stop.