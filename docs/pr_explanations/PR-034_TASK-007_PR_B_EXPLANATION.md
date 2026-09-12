# PR-034 — TASK-007 PR B: one capability execution transition

**Implementation agent: Manus.**

## 1. Purpose of the PR

This pull request implements the smallest runtime boundary needed to turn one
already-selected TASK-006 capability into one auditable attempt. It does not
implement the repeated capability run loop. This explanation also records the
authorized corrections for CODEX-PR034-01, CODEX-PR034-02, and CODEX-PR034-03.

Arko authorized this work as TASK-007 PR B. The human-only merge gate remains in
force, and Codex remains the independent reviewer.

## 2. What changed

The branch adds an immutable `ExecutionResult` containing three provider-neutral
facts: whether the attempt succeeded, the exact amount actually committed, and
opaque evidence for a later task-state interpreter. It adds a minimal
`CapabilityExecutor` protocol receiving the selected candidate, the current run
state, and the explicit maximum authorized commitment.

The branch also adds `apply_execution(...)`. This function accepts an already
selected capability, calls the injected executor once, validates the result, and
returns a new immutable `RunState` containing one transition record. The
transition consumes the candidate identifier, increments the capability-step
count once, and applies the exact committed amount to the ledger. Before the
executor is called, the generic layer validates the entire retained Selection
graph by exact type and matches the Selection’s recorded decision inputs to the
current RunState.

`TransitionRecord.execution` now accepts either `None` or the exact
`ExecutionResult` type. Arbitrary payloads, run states, snapshots, and
subclasses remain rejected. The package exports the existing public boundary;
no new public data type was introduced by the corrections.

### 2.1 Codex corrections

**CODEX-PR034-01 — transitive exact-type audit safety.** A frozen subclass of
`Candidate` or `Assessment` can carry a mutable subclass-only field. The
correction walks every retained assessment and candidate, including rejected
ones, and rejects every subclass before the Selection can enter a transition
record. Exact ordinary `Candidate`, `Assessment`, and `Selection` values remain
valid.

**CODEX-PR034-02 — current-state authorization.** `apply_execution(...)` now
requires the Selection’s recorded task value, probability, remaining budget,
consumed candidate IDs, capability-step count, and maximum step ceiling to match
the current RunState. It also requires an exact, eligible selected Assessment
that is one of the retained assessments. Any mismatch is rejected before the
executor is called; no selection or ranking is rerun.

**CODEX-PR034-03 — executor commitment and failure contract.** The generic
layer passes `min(candidate.cost, current_state.remaining_budget)` to the
executor before any side effect. A compliant executor must never exceed it and
must return an exact failed `ExecutionResult` with actual committed cost for
every post-attempt/provider failure, including positive-cost failure. A raw
exception means the executor failed before an attempt or financial commitment
began. The generic layer does not fabricate spend from arbitrary exceptions or
silently clamp malformed results.

## 3. Why the change was needed

TASK-007 PR A established immutable state and snapshots but intentionally left
execution as a reserved placeholder. Without this boundary, the generalized
TASK-006 selector could decide but could not record what one selected attempt
actually did or what it cost.

The boundary is needed to preserve the product’s economic accounting. A failed
attempt may still commit a non-zero amount, so failure cannot be represented as
zero spend. A zero-cost attempt still counts as an attempt and must consume its
candidate identifier.

## 4. How the system worked before

Before this branch, TASK-001 remained the active CLI/runtime path. TASK-006
provided the generalized candidate, eligibility, ranking, and policy kernel.
TASK-007 PR A provided immutable run state, snapshots, and the shape of a
transition record, but `TransitionRecord.execution` had to be `None` and no
execution transition existed.

The full repository suite passed 652 tests before this PR. The new focused test
module initially failed during collection with:

```text
ModuleNotFoundError: No module named 'radhanite.capability_execution'
```

That failing state was recorded before the implementation was written, as
required by the authorization.

## 5. How it works after

A caller first supplies a valid TASK-006 `Selection` whose outcome is
`SELECTED`. `apply_execution(...)` verifies that the run is still running, that
the step ceiling has not been reached, and that the candidate identifier has not
already been consumed.

The injected executor receives exactly the selected `Candidate`, the current
`RunState`, and `min(candidate.cost, current_state.remaining_budget)`. It is
called exactly once. Its exact `ExecutionResult` is then validated against that
explicit authorization ceiling.

For a valid attempt, the returned state has one additional consumed identifier,
one additional capability step, and ledger values derived from
`committed_cost`. A successful result preserves the task state, success
probability, and `RUNNING` status. A failed result sets the new status to
`EXECUTION_FAILURE` and is not retried.

## 6. Important inputs, data, or state entering the system

The transition receives an existing `RunState`, an existing TASK-006
`Selection`, and an injected object implementing the executor protocol. The
executor receives no provider, payment, wallet, network, endpoint, or
marketplace parameter. Its third input is only the exact provider-neutral
authorization ceiling.

`committed_cost` uses the existing exact `Money` type. Evidence is frozen with
the same structural mechanism used for opaque `task_state`: containers are
rebuilt into immutable equivalents, cycles are rejected, and unsupported or
subclass-based escape hatches are refused.

## 7. Decisions made by the system

The new code makes only transition and validation decisions required by TASK-007
§5.2 and §7. It does not decide which candidate is best. It does not generate or
acquire candidates. It does not interpret evidence or decide whether a task is
complete. Selection context matching is an authorization check, not a second
decision engine.

The transition accepts a committed amount only when all three economic bounds
hold:

```text
0 <= committed_cost <= candidate.cost
committed_cost <= remaining_budget
```

The authorization ceiling is `min(candidate.cost, remaining_budget)`, and the
actual committed amount drives the ledger.

## 8. Outputs or state changes

The function returns a new immutable `RunState`. The input state is unchanged.
The new state contains one `TransitionRecord` with exact before and after
snapshots, the complete original `Selection`, and the exact `ExecutionResult`.

On every actual executor call, regardless of success or cost, the candidate ID
is consumed and `capability_step_count` increases by exactly one. The ledger
identity remains true:

```text
total_spend + remaining_budget == initial_budget
```

## 9. Failure modes

The transition refuses terminal states, reached step ceilings, STOP selections,
consumed candidate IDs, invalid result types, negative committed cost, committed
cost above the candidate cost, and committed cost above the remaining budget.
It performs no silent clamping.

A compliant failed execution is recorded with its actual committed cost,
consumes the candidate, increments the step count, sets `EXECUTION_FAILURE`, and
receives no retry. An invalid result is an executor contract violation and is
rejected without fabricated accounting. A raw exception is permitted only for a
pre-attempt failure; the generic layer cannot infer what arbitrary code committed
after beginning an attempt.

## 10. Tests run and results

The focused PR B correction suite contains 47 tests and passes:

```text
PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest tests.test_capability_execution -q
Ran 47 tests in 0.010s
OK
```

The full suite passes:

```text
PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest discover -q
Ran 699 tests in 0.247s
OK
```

Nineteen deliberate mutation checks were run against the focused suite. The
tests killed all nineteen mutants: the eight original PR-B accounting/result
faults, retained Candidate and Assessment subclasses, skipped rejected-graph
validation, each of the six current-state context checks, executor invocation
before stale-selection rejection, omitted authorization enforcement, malformed
result conversion, and pre-attempt exception conversion.

The implementation adds no dependency. TASK-006 and TASK-008 semantics remain
unchanged, and no provider-specific runtime work was added.

## 11. Assumptions made

The executor boundary is represented as a standard-library `Protocol`, because
TASK-007 permits a protocol, callable contract, or abstract interface and the
protocol is the smallest explicit interface consistent with the repository.

The transition function accepts a complete `Selection` rather than invoking
selection itself. This keeps selection and execution separate and preserves the
full decision record required by TASK-006.

## 12. Known limitations

The generalized kernel still does not drive the active CLI/runtime. This PR
performs one explicitly selected execution only. It does not provide a candidate
source, task-state updater, completion evaluator, terminal STOP classification,
or iterative orchestration.

The executor itself is injected. No real inference, payment, network, wallet,
provider discovery, or external integration exists.

## 13. Functionality explicitly left out of scope

This PR does not implement TASK-006 selection, candidate ranking, candidate
generation, TASK-008 acquisition calls, evidence interpretation, task-state or
probability updates, `TASK_COMPLETE`, `ECONOMIC_STOP`, `SAFETY_STOP`, retry,
the full loop, Circle/Arc, x402, Nanopayments, The Graph, Hedera, provider
discovery, or real payments.

## 14. Anything deferred to future tasks

The remaining TASK-007 work is the task-state updater boundary, terminal
classification, and the repeated run loop. TASK-008 still needs source-specific
candidate generation and provider adapters. Benchmark reasoning and external
integrations remain separate authorized-task decisions.

## 15. How to explain this to a judge

Radhanite now has the narrow execution boundary needed after its generalized
economic selector: one selected capability can be attempted, its actual spend
can be recorded exactly, and the result can be audited without mutating prior
state. The implementation deliberately stops there. It does not pretend that a
single transition is already an autonomous run loop, and it does not claim real
provider or payment integrations.

## References

[1]: ../AI_BUILD_GOVERNANCE.md "AI Build Governance"
[2]: ../ARCHITECTURE.md "Radhanite architecture boundaries"
[3]: ../../tasks/TASK-006_GENERALIZED_CAPABILITY_SELECTION.md "TASK-006 — Generalized capability selection"
[4]: ../../tasks/TASK-007_CAPABILITY_RUN_LOOP.md "TASK-007 — The capability run loop"
[5]: ../../tasks/TASK-008_CAPABILITY_ACQUISITION.md "TASK-008 — Capability acquisition and candidate generation"
