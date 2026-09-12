# 004 — TASK-007 PR B Codex corrections

**Date:** 2026-09-12
**Agent:** Manus
**Authority:** Arko authorization for corrections to existing PR #34 only
**Implementation agent:** **Manus.**

The complete authorization prompt follows verbatim.

Implementation agent: Manus.

AUTHORIZE CORRECTIONS TO PR #34 ONLY — CODEX-PR034-01, 02, 03.

PR:

#34 — TASK-007 PR B: one capability execution transition

Current branch:

task-007-execution-transition

Do not start a new PR.

Do not merge.

Do not begin TASK-007 full-loop work.

Human product owner / final authority: Arko.

Independent reviewer: Codex.

OBJECTIVE

Fix only the three material Codex findings:

CODEX-PR034-01 — transitive immutability through Selection/Assessment/Candidate subclasses
CODEX-PR034-02 — stale/forged Selection accepted against a different current RunState
CODEX-PR034-03 — executor-side-effect / exception path can bypass recording

Preserve all already-correct PR-B semantics.

CODEX-PR034-01 — TRANSITIVE EXACT-TYPE AUDIT SAFETY

Codex demonstrated that exact top-level Selection validation is insufficient because public selection/assessment APIs can still contain subclasses of:

Assessment
Candidate

carrying mutable fields.

Those subclasses can then be retained inside:

history[-1].selection

and mutated after the transition was written.

Required correction

Before retaining a Selection in TransitionRecord, validate the entire retained selection graph by exact type.

At minimum inspect:

Selection
every Assessment in the selection
every nested Candidate
selected assessment/candidate
rejected assessments/candidates
any retained collection/member that can carry subclass-added state

Use exact type:

type(x) is T

not:

isinstance(x, T)

Do not inspect subclasses and attempt to decide whether they are safe.

Reject subclasses.

The complete Selection must remain retained because TASK-006 requires the full decision record.

Important

Do not solve this only for the selected assessment.

A rejected candidate is also part of retained audit history and therefore must be safe.

Tests first

Add adversarial public-pipeline tests using frozen dataclass subclasses with mutable list fields for:

selected Candidate
rejected Candidate
selected Assessment
rejected Assessment

Demonstrate against the rejected implementation that:

they can currently enter through the public selection pipeline;
they can currently be retained in transition history;
mutating their subclass-only field changes recorded history.

Then correct the implementation and prove all are rejected before retention.

Exact normal Candidate/Assessment/Selection values must remain valid.

CODEX-PR034-02 — SELECTION MUST MATCH CURRENT RUN STATE

apply_execution() must not treat any structurally valid Selection as authorization.

It must prove that the Selection was generated for the current decision state.

Before invoking the executor, verify that the Selection's recorded decision inputs exactly match the current RunState values used by TASK-006.

Verify against the actual Selection/assessment model in the repository rather than inventing fields.

The required decision context includes:

task value
current success probability
remaining budget
consumed candidate IDs
capability step count
max capability steps / policy ceiling

Any other TASK-006 run-level input captured by the Selection must also match.

Required behavior

If a Selection was produced under:

a different success probability;
a different remaining budget;
a different task value;
different consumed IDs;
a different step count;
a different ceiling/policy;

then apply_execution() must reject it before the executor is called.

Do not re-run TASK-006 inside apply_execution().

Do not re-rank candidates.

Do not independently recompute the economics.

This is an authorization-context match, not a second decision engine.

Selected assessment integrity

Also verify that the selected assessment is structurally consistent with the Selection:

exact authorized Assessment type
exact Candidate type
selected outcome genuinely corresponds to that assessment/candidate
no forged/malformed selected object can bypass TASK-006's public invariants

Prefer reusing existing Selection invariants where they are authoritative, but add the current-state match that is currently missing.

Tests first

Add at minimum:

Selection created at probability 0.20 rejected against state at 0.90.
Selection created with $2.00 remaining rejected against state with $0.50 remaining.
task-value mismatch rejected.
consumed-ID mismatch rejected.
step-count mismatch rejected.
max-step/policy mismatch rejected.
exact matching current state accepted.
executor call count remains zero on every mismatch.

Preserve exact Money/Probability semantics.

CODEX-PR034-03 — EXECUTOR CONTRACT / ATTEMPT RECORDING

This is the most important correction.

TASK-007 §7 requires every actual execution attempt to be auditable:

candidate consumed
step count incremented
actual committed cost recorded
failure terminates as EXECUTION_FAILURE

The current code cannot satisfy that if a real-side-effect executor:

raises after committing money;
returns malformed data after committing money;
reports a commitment above its authorization.
Required contract

Make the executor boundary explicit:

A compliant CapabilityExecutor MUST:
know its maximum authorized commitment before performing any external side effect;
never commit more than:

min(candidate.cost, current_state.remaining_budget)

convert provider/internal execution failures into an exact ExecutionResult;
return the actual committed cost, including non-zero cost on failure;
never propagate an exception after an external commitment or execution attempt has begun;
return:

ExecutionResult(succeeded=False, committed_cost=<actual>, evidence=<opaque failure evidence>)

for a provider/internal failure after an attempt.

Raw exceptions

Define the boundary clearly enough that a raw exception means:

the executor failed before any execution attempt or financial commitment occurred.

If you choose to catch such an exception in apply_execution(), do not falsely record an execution attempt unless the contract says an attempt occurred.

More importantly, a conforming executor must normalize every post-attempt outcome into ExecutionResult.

Do not pretend apply_execution() can infer actual spend from an arbitrary exception. It cannot.

Pre-authorization

Make the authorized ceiling explicit to the executor before side effects.

The current Candidate and RunState contain enough information mathematically, but the contract should not leave the authorization implicit.

Prefer the smallest provider-neutral solution consistent with the repository.

If introducing a tiny immutable execution authorization/request object makes the pre-commit ceiling explicit and removes ambiguity, that is authorized only if necessary to close this finding.

It must remain provider-neutral.

Do not add payment/provider/network fields.

The executor must never be authorized for more than:

min(candidate.cost, remaining_budget)

Invalid returned result

A malformed result from a compliant executor must not occur after a side effect.

Treat malformed type/bounds as an executor contract violation.

Document clearly that such a violation means the executor broke the no-side-effect-before-valid-result contract and therefore cannot safely be reconciled by the generic layer.

Do not silently clamp.

Do not fabricate committed cost.

Tests first

Add tests that distinguish:

provider failure represented as ExecutionResult(succeeded=False, committed_cost=positive) → recorded correctly.
provider failure at zero cost → recorded correctly.
successful positive-cost attempt → recorded correctly.
executor receives explicit authorized maximum before acting.
compliant executor never exceeds that maximum.
raw pre-attempt exception does not get misrepresented as a paid attempt.
simulated post-attempt/provider failure is normalized into ExecutionResult and therefore recorded.
malformed result remains a contract violation and does not get silently converted into invented accounting.

The tests should make clear which behavior is:

a valid execution failure;
a pre-attempt executor failure;
an executor contract violation.

Do not add retry behavior.

PRESERVE CURRENT PR-B SEMANTICS

For every valid actual execution attempt:

candidate ID consumed exactly once
capability_step_count incremented exactly once
actual committed_cost applied exactly once
before/after snapshots recorded
full Selection retained

Successful execution:

status stays RUNNING
task_state unchanged
current_success_probability unchanged

Failed execution:

status becomes EXECUTION_FAILURE
committed spend still recorded
no retry
DO NOT IMPLEMENT

Do not add:

TASK-006 selection/ranking
re-selection
candidate acquisition
task-state updater
probability updates
TASK_COMPLETE
ECONOMIC_STOP
SAFETY_STOP
full run loop
retry
Circle/Arc
x402/Nanopayments
The Graph
Hedera
provider-specific code
real payment code
TEST / MUTATION REQUIREMENTS

Run focused failing tests against the current rejected implementation before correction.

Add mutation/fault checks that catch at minimum:

accept Candidate subclass in retained Selection
accept Assessment subclass in retained Selection
validate only selected assessment, not rejected assessments
omit probability context match
omit remaining-budget context match
omit consumed-ID context match
omit step-count context match
omit policy/ceiling context match
call executor before stale-selection rejection
permit executor commitment above authorization
allow post-attempt raw exception to bypass ExecutionResult normalization

Re-run existing PR-B mutation checks as well.

Use:

PYTHONDONTWRITEBYTECODE=1

DOCUMENTATION

Update:

TASK-007
PR #34 explanation
Codex review record
any architecture/status text affected by the correction

Correct the existing false statement that every executor call is automatically recorded.

Replace it with the precise contract:

every compliant execution attempt is represented by an exact ExecutionResult and therefore recorded; a raw exception is permitted only before an execution attempt/commitment begins.

Do not imply that arbitrary third-party code can be made auditable after it commits money and then loses the committed amount.

Preserve:

Implementation agent: Manus.

in every required progress/report/commit/PR artifact.

VERIFY

Run:

PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest discover -q

Confirm:

all 652 pre-PR-B tests remain passing
all previous PR-B tests remain passing or are intentionally strengthened
all new regression tests pass
no dependency added
no provider-specific implementation added
REPORT

Push corrections to existing PR #34.

Do not merge.

Report:

new head SHA
files changed
failing regression test count before fix
final full-suite count
mutation results
exact fix for CODEX-PR034-01
exact fix for CODEX-PR034-02
exact executor contract adopted for CODEX-PR034-03
whether any new public type/interface was introduced
explicit status of all three Codex findings

End with:

Implementation agent: Manus.

Then stop.