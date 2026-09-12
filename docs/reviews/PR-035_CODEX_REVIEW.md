# Codex review — PR-035

**Implementation agent: Manus.**

**Pull request:** [#35](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/35) — TASK-007 final generic capability run loop
**Reviewer:** Codex (independent review agent, `AI_BUILD_GOVERNANCE.md` §1.3)
**Reviewed against:** `tasks/TASK-007_CAPABILITY_RUN_LOOP.md` §§2–9; `tasks/TASK-006_GENERALIZED_CAPABILITY_SELECTION.md`; `docs/ARCHITECTURE.md`; `docs/AI_BUILD_GOVERNANCE.md`
**Date issued:** 2026-09-12
**Outcome:** correction applied for CODEX-PR035-01; tiny re-review pending

---

## 0. Note on ordering

The review prompt is committed before Codex review runs, as `AI_BUILD_GOVERNANCE.md` §7.3 requires.

## 1. Prompt issued

Recorded before the review was run:

```text
You are Codex, the independent review agent for the Radhanite repository.

Review pull request #35:
https://github.com/therealgulkorinaga/radhanite-ethonline/pull/35

This is the authorized TASK-007 final generic loop. Review only the provider-neutral orchestration boundary:
- terminal/completion precedence;
- candidate-source and task-state-updater interfaces;
- reuse of TASK-006 assessment and selection;
- reuse of TASK-007 PR-B apply_execution;
- one execution attempt per iteration;
- exact accounting, candidate consumption, and attempt counting;
- failure termination without updater or retry;
- STOP classification and complete Selection retention;
- immutable, non-recursive TransitionRecord history;
- critical tests and status/provenance artifacts.

Verify:
1. Already-complete state is checked before candidate sourcing, including zero-step and reached-ceiling cases.
2. Incomplete zero-step and reached-ceiling runs are SAFETY_STOP; below-ceiling economic refusals are ECONOMIC_STOP; safeguard-only refusals are SAFETY_STOP.
3. The loop does not derive TASK-006 economics and invokes select_capability rather than reimplementing ranking or eligibility.
4. Execution can occur at most once per iteration and only through apply_execution.
5. Successful execution invokes the updater exactly once; failed execution never invokes it, never retries, and retains committed cost.
6. Zero-cost attempts increment capability_step_count, consumed IDs cannot execute again, and a new ID for the same conceptual capability can execute.
7. Initial pre-loop spend and exact-budget exhaustion preserve all ledger identities and bounds.
8. Every iteration appends exactly one immutable non-recursive transition, with complete Selection and execution=None on STOP.
9. No provider, payment, network, marketplace, revenue-specific, persistence, UI, deployment, or dependency work was added.
10. Run the focused and full tests, and assess whether the six deliberate mutation checks kill the listed critical faults.

Report stable finding identifiers CODEX-PR035-01, CODEX-PR035-02, and so on. For every finding give the file, line, violated boundary, and correction required. If there are no findings, say so explicitly. Do not merge the pull request.
```

## 2. Findings returned

### CODEX-PR035-01 — completion ownership was overstated

The implementation correctly gives terminal state precedence, but the original
documentation and test naming could be read as generic detection that an opaque
task was already complete. `begin_run()` creates a `RUNNING` state, and TASK-007
does not inspect `task_state` to determine completion. The upstream task/domain
initializer must determine completion and supply `RunStatus.TASK_COMPLETE` when
appropriate. No completion evaluator or TASK-009 logic belongs in TASK-007.

The required correction was documentation- and test-focused: the terminal-entry
test now names and proves the `TASK_COMPLETE` contract, a new regression test
proves that `RUNNING` with opaque `{"complete": True}` is not interpreted, and
TASK-006 criterion-10 wording no longer claims generic completion inference or a
STOP transition that is not written.

## 3. Outcome

CODEX-PR035-01 is addressed on the existing PR #35 branch. A tiny independent
re-review remains required and is limited to the five verification points in the
authorization record. The pull request must remain unmerged until that re-review
returns an outcome and the human merge authority approves the merge.

## 4. Corrections

Applied by **Implementation agent: Manus.** No runtime completion evaluator,
opaque-state inspection, provider integration, or revenue-specific logic was
added. The loop mechanics outside this narrow contract correction were not
reopened.
