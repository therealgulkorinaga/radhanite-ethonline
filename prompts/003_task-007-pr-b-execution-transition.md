# 003 — TASK-007 PR B execution transition

**Date:** 2026-09-12
**Agent:** Manus
**Authority:** TASK-007 PR B authorization from Arko
**Resulted in:** Provider-neutral execution result, executor boundary, and one immutable execution transition on the review branch.

**Implementation agent: Manus.**

## Prompt

The following is preserved verbatim from the product owner’s authorization attachment.

Implementation agent: Manus.

AUTHORIZE TASK-007 RUNTIME PR B — EXECUTION RESULT + EXECUTOR BOUNDARY + ONE EXECUTION TRANSITION. TEST-FIRST.

Human product owner / final authority: Arko.

Independent reviewer: Codex.

Human-only merge gate remains in force.

Before editing, verify:

branch from fresh main
current main includes PR #33
PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest discover -q passes
current authoritative test count is 652 before this PR
TASK-007 PR A is implemented
TASK-008 PR A is implemented
TASK-007 §5.2, §7 and §9 are the authoritative execution semantics

If any of those are false, STOP and report the discrepancy.

PURPOSE

TASK-007 PR A delivered the immutable run-state and snapshot foundation.

PR B must implement the provider-neutral execution boundary for exactly one selected capability attempt.

This PR must take:

an already-selected TASK-006 Candidate + current RunState + injected executor

and produce:

an immutable execution result + one new RunState transition

It must not implement the full iterative loop yet.

AUTHORITATIVE EXECUTION SEMANTICS

Preserve TASK-007 exactly:

The executor receives one already-selected candidate.
The execution result must contain:
succeeded
exact committed_cost
opaque evidence/result
The candidate's declared cost is the maximum amount execution may commit:

0 <= committed_cost <= candidate.cost

and:

committed_cost <= remaining_budget

Failure does not imply zero spend.

Whatever amount was actually committed must be recorded even if execution failed.

On every execution attempt, success or failure:
selected candidate ID becomes consumed
capability_step_count increments exactly once
committed_cost increases total_spend
committed_cost decreases remaining_budget
A zero-cost execution still:
consumes the candidate ID
increments the step count exactly once
Failed execution sets terminal status:

EXECUTION_FAILURE

and there is no retry.

Successful execution does not itself interpret evidence or update task-state probability/completion.

That belongs to the separately owned task-state updater boundary.

PR B should stop before implementing that updater.

PR B SCOPE

Implement only the minimum required pieces.

1. ExecutionResult

Introduce the provider-neutral immutable execution result type required by TASK-007.

Minimum semantic fields:

succeeded
committed_cost
opaque evidence

Use the exact naming already specified by TASK-007 unless current code conventions require otherwise.

committed_cost must use existing Money.

No float conversion.

No provider/payment/network identity.

evidence must follow the same generic safe opaque-state boundary established in TASK-007 PR A:

no live mutable aliases
no recursive/self-referential state
generic structural freezing only
no domain interpretation

Reuse the existing safe-freeze mechanism if appropriate rather than creating a second inconsistent one.

2. Executor interface

Define the minimum provider-neutral executor boundary:

conceptually:

execute(selected_candidate, current_state) -> ExecutionResult

The exact Python form may be:

Protocol
callable contract
abstract interface

Choose the smallest form consistent with current repository conventions and TASK-007.

Do not add provider-specific parameters.

3. One execution transition

Implement a function that applies exactly one execution attempt to current run state.

It must:

require a valid selected Candidate
require that candidate is not already consumed
require another execution is permitted by the current state/policy
call the injected executor exactly once
validate the returned ExecutionResult
consume candidate ID
increment capability step count exactly once
update exact ledger values from committed_cost
construct immutable before/after snapshots
construct one TransitionRecord containing the ExecutionResult

If execution failed:

after.status = EXECUTION_FAILURE

If execution succeeded:

preserve task_state
preserve current_success_probability
preserve RUNNING status
do NOT call any updater yet

Later work will interpret the evidence and update task state.

IMPORTANT BOUNDARIES

PR B must NOT:

run TASK-006 selection itself
choose between candidates
generate candidates
call TASK-008 acquisition
implement a candidate source
call a task-state updater
interpret evidence
update current success probability after successful execution
decide TASK_COMPLETE
classify ECONOMIC_STOP
classify SAFETY_STOP
implement the full loop
retry failed execution
implement Circle/Arc
implement x402
implement Nanopayments
implement The Graph
implement Hedera
implement provider discovery
implement real payments
TRANSITIONRECORD

PR A currently requires:

TransitionRecord.execution is None

PR B is now authorized to change this boundary only enough to accept the exact new ExecutionResult type.

Preserve the PR-A safety principle:

exact type, not broad subclass acceptance
immutable
no arbitrary payload
no mutable alias
no RunState / RunSnapshot / arbitrary custom object accepted as execution

Do not make execution generic.

It should accept:

None for iterations with no execution
exact authorized ExecutionResult for execution transitions

Nothing else.

LEDGER TRANSITION

For old state:

old_total_spend

old_remaining_budget

and execution result:

committed_cost

derive:

new_total_spend = old_total_spend + committed_cost

new_remaining_budget = old_remaining_budget - committed_cost

Preserve:

new_total_spend + new_remaining_budget == initial_budget

and:

0 <= new_total_spend <= initial_budget

0 <= new_remaining_budget <= initial_budget

The transition must reject:

negative committed cost
committed cost > candidate cost
committed cost > remaining budget

No silent clamping.

STEP COUNT + CONSUMPTION

On every actual executor call:

new_capability_step_count = old_capability_step_count + 1

regardless of:

success
failure
positive committed cost
zero committed cost

Candidate ID must be added to consumed IDs exactly once.

Same candidate ID must never execute twice.

A different future candidate ID for the same conceptual capability remains valid; do not invent capability-family semantics.

TEST-FIRST REQUIREMENT

Before implementation:

write focused tests for the authorized PR-B behavior
run them against current main
confirm expected failure
record that failing state in the PR explanation
implement minimum code
run focused tests
run full suite

Required tests at minimum:

ExecutionResult
successful result with positive committed cost
successful result with zero committed cost
failed result with positive committed cost
failed result with zero committed cost
negative committed cost rejected
exact Money preserved
mutable evidence detached/frozen
cyclic evidence rejected
scalar/custom subclass escape hatches rejected according to PR-A exact-type policy
Executor boundary
executor called exactly once
executor receives selected Candidate
executor receives current RunState if required by the chosen interface
arbitrary provider metadata is absent from the generic interface
State transition
candidate consumed on successful execution
candidate consumed on failed execution
step count increments once on successful positive-cost execution
step count increments once on successful zero-cost execution
step count increments once on failed positive-cost execution
step count increments once on failed zero-cost execution
committed cost exactly updates total spend
committed cost exactly updates remaining budget
ledger identity remains true
committed cost equal to remaining budget is allowed
committed cost > candidate cost rejected
committed cost > remaining budget rejected
same candidate ID cannot execute twice
before snapshot reflects exact pre-attempt state
after snapshot reflects exact post-attempt state
successful execution preserves current task_state
successful execution preserves current_success_probability
successful execution leaves status RUNNING
failed execution sets EXECUTION_FAILURE
failed execution does not retry
task-state updater is not called
no selection/ranking occurs in the transition
TransitionRecord
exact ExecutionResult accepted
None remains accepted where appropriate
ExecutionResult subclass rejected
arbitrary mutable execution payload rejected
RunState/RunSnapshot/custom object rejected as execution
MUTATION / FAULT CHECKS

At minimum deliberately verify tests catch:

do not consume candidate on failure
increment step count only when cost > 0
increment step count only on success
charge declared candidate cost instead of actual committed cost
treat failure as zero committed cost
allow committed_cost > candidate.cost
allow committed_cost > remaining_budget
retry executor after failure
mutate old RunState instead of constructing a new one
allow arbitrary TransitionRecord.execution payload

Use:

PYTHONDONTWRITEBYTECODE=1

for mutation runs so stale bytecode cannot contaminate results.

DOCUMENTATION / GOVERNANCE

Update TASK-007 status truthfully to reflect PR B progress, but do not mark TASK-007 complete.

Preserve historical review records.

Create the required:

PR explanation
review record
preserved authorization prompt according to repository governance

Every required implementation progress artifact, commit message, PR body, explanation and handoff/report must visibly include:

Implementation agent: Manus.

This is provenance only and changes no authority.

VERIFY

Run:

PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest discover -q

Confirm:

all 652 pre-existing tests still pass
all new PR-B tests pass
no dependency added
TASK-006 semantics unchanged
TASK-008 semantics unchanged
no provider-specific runtime work added
DELIVER

Branch from fresh main.

Suggested branch:

task-007-execution-transition

Open a new PR.

Do not merge.

Do not start full run-loop orchestration.

Report:

branch
PR number/link
commit hash
files changed
exact public types/functions introduced
failing test state before implementation
final test count
mutation results
confirmation candidate consumption occurs on every attempt
confirmation step count increments on every attempt
confirmation failed execution accounts for committed spend
any material architectural blocker

End the report with:

Implementation agent: Manus.

Then stop.