# 005 — TASK-007 final loop

**Date:** 2026-09-12
**Agent:** Manus
**Authority:** Arko authorization for TASK-007 final loop
**Resulted in:** The provider-neutral TASK-007 orchestration loop, focused tests, and review artifacts were added on the implementation branch.

## Prompt

Implementation agent: Manus.

AUTHORIZE TASK-007 FINAL LOOP — HACKATHON CRITICAL PATH.

Time remaining is limited. Optimize for a correct, demonstrable end-to-end runtime, not production-hardening.

Human product owner / merge authority: Arko.

Independent reviewer: Codex.

Branch from fresh main after PR #34 is merged.

First verify:

PR #34 is present on main
full suite passes
TASK-007 PR A and PR B are present

If not, stop and report.

GOAL

Complete the minimum generic TASK-007 orchestration loop required for the hackathon.

The loop must:

receive current RunState;
check whether the task is already complete;
obtain current candidates from an injected candidate-source boundary;
call the existing TASK-006 selector;
if TASK-006 selects a candidate, invoke the already-implemented PR-B execution transition;
if execution fails, terminate EXECUTION_FAILURE;
if execution succeeds, call an injected task-state updater;
update:
task_state
current_success_probability
completion status;
repeat;
terminate correctly as:
TASK_COMPLETE
ECONOMIC_STOP
SAFETY_STOP
EXECUTION_FAILURE

Do not redesign TASK-006 economics.

Do not implement provider-specific logic.

REQUIRED PRECEDENCE

Preserve TASK-007 exactly:

Already-complete check happens first.

If task is already complete:

zero candidate evaluation;
zero execution;
terminal TASK_COMPLETE.

This takes precedence over:

zero max steps;
reached step ceiling;
available candidates.
CANDIDATE SOURCE

Introduce/use the smallest provider-neutral candidate-source boundary:

conceptually:

get_candidates(task_state, run_state) -> candidate collection

Do not interpret provider identity.

Existing declared/fixture candidates may satisfy this for tests.

Do not implement Circle, Graph, Hedera, or marketplace discovery in this task.

TASK-STATE UPDATER

Introduce the smallest provider-neutral updater boundary:

conceptually:

update(previous_task_state, execution_result) -> updated task state + new success probability + completion verdict

TASK-007 must not derive these itself.

The updater owns the domain interpretation.

Keep this interface generic enough that TASK-009 can implement the revenue-opportunity logic next.

Do not implement revenue-specific reasoning in TASK-007.

STOP CLASSIFICATION

Use existing TASK-006 Selection output.

Do not recompute candidate economics.

Required behavior:

reached step ceiling → SAFETY_STOP, always
max_capability_steps == 0 with incomplete task → SAFETY_STOP
below ceiling, any economic refusal causing STOP → ECONOMIC_STOP
below ceiling, safeguard-only refusal → SAFETY_STOP
below ceiling, zero candidates → ECONOMIC_STOP

Preserve all per-candidate refusal reasons in the retained Selection.

HISTORY

Every iteration must append exactly one immutable TransitionRecord.

For an execution iteration:

complete Selection retained
exact ExecutionResult retained
before/after snapshots retained

For a STOP iteration:

complete Selection retained
execution=None
before/after snapshots retained

No recursive history.

LOOP SAFETY

Enforce:

at most one capability attempt per iteration
every actual attempt increments the step count once
consumed IDs cannot execute again
no execution after terminal state
failure terminates immediately
no automatic retry
total spend can never exceed initial budget

Do not weaken PR #34's executor contract.

TEST-FIRST, BUT TIME-BOXED

Write the critical behavioral tests first.

Required tests:

already-complete task → TASK_COMPLETE, zero candidate calls, zero execution
successful execution → updater → task complete
multiple successful iterations
economic STOP
safety STOP at ceiling
zero-step policy → immediate safety stop
execution failure → EXECUTION_FAILURE
failed execution with non-zero committed cost remains accounted
zero-cost execution increments step count
consumed candidate cannot execute again
same conceptual capability with new ID may execute
total spend never exceeds budget
exact-budget exhaustion works
pre-loop spend remains preserved
complete Selection retained in history
STOP iteration retains Selection and execution=None
updater not called on failed execution
TASK-006 economics are not reimplemented in the loop

Keep mutation testing focused on the critical invariants only:

skip already-complete precedence
increment only on positive cost
continue after execution failure
misclassify ceiling as economic stop
call updater after failure
lose committed spend

Do not spend time building an exhaustive mutation matrix.

HACKATHON SCOPE RULE

Stop if the code satisfies the specified loop and tests.

Do not add:

generalized plugin systems
retry frameworks
provider adapters
payment abstractions beyond existing executor contract
new persistence
telemetry systems
UI
production deployment features

Those are separate tasks.

KNOWN DEFERRED HARDENING

Record, but do not fix now:

A deliberately hand-constructed same-context Selection can theoretically name a different eligible candidate than TASK-006's ranked winner. The supported runtime path uses select_capability() and is unaffected. Post-hackathon constructor hardening.

Do not let this delay the loop.

VALIDATE

Run:

PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest discover -q

All existing tests must remain passing.

No external dependency.

DELIVER

Open one PR for the final TASK-007 orchestration loop.

Do not merge.

Report:

PR
branch
commit
files changed
new public interfaces
failing tests before implementation
final test count
focused mutation results
confirmation all four terminal states work
confirmation multiple iterations work
confirmation TASK-006 economics were reused, not reimplemented

End with:

Implementation agent: Manus.

Then stop.