# PR-035 — TASK-007 final generic capability run loop

**Implementation agent: Manus.**

## Purpose

This pull request implements the minimum provider-neutral TASK-007 orchestration loop authorized by Arko after PR #34 was merged into `main`. It turns the existing TASK-006 decision and TASK-007 PR-B execution transition into a repeatable run without adding provider, payment, network, marketplace, or domain-specific revenue logic.

## Implemented boundary

The new `radhanite/loop.py` module defines `CandidateSource`, `TaskStateUpdater`, `TaskStateUpdate`, and `run_capability_loop(...)`. The loop checks terminal state before asking for candidates, freezes updater state structurally, constructs TASK-006 assessments, calls the existing `select_capability(...)`, invokes `apply_execution(...)` at most once per iteration, and calls the updater only after success. It classifies STOP from the retained TASK-006 selection, gives the step ceiling safety precedence, records one immutable non-recursive transition per iteration, preserves committed-cost accounting, consumes candidate IDs, increments attempts including zero-cost attempts, and terminates failures without retry.

The existing TASK-001 CLI/runtime remains unchanged. Candidate discovery, revenue reasoning, provider-specific adapters, payment, network, persistence, UI, and deployment remain outside this pull request.

## Validation

The new focused suite contains 13 critical loop tests and passes. The full Python 3.12 suite contains 712 passing tests. The six focused mutation checks killed all six deliberate faults: skipped terminal precedence, cost-dependent step increments, continuing after execution failure, ceiling misclassification, updater invocation after failure, and lost committed spend.

The pre-implementation baseline on fresh `main` was 699 passing tests. No external dependency was added.

## Review boundary

Codex review is required before merge. The implementation agent must not merge this pull request.

## CODEX-PR035-01 contract correction

The correction clarifies the ownership boundary for completion. `RunStatus.TASK_COMPLETE`
is the authoritative precomputed completion signal at loop entry. TASK-007 checks
that terminal status before candidate sourcing and returns the original terminal
state unchanged, so it makes zero candidate-source, executor, or updater calls.

TASK-007 does not inspect opaque `task_state` to infer completion. The upstream
task/domain initializer owns the domain-specific determination that a task is
already complete. For the revenue-agent benchmark, that responsibility belongs
to TASK-009 or its initializer; no TASK-009 logic is included here.

The focused tests now also prove that a `RUNNING` state containing opaque
`{"complete": True}` is not interpreted as completion. The TASK-006 criterion-10
closure claim is correspondingly narrowed to the precomputed `TASK_COMPLETE`
entry-state guarantee. No new evaluator, provider integration, revenue logic, or
runtime abstraction was added.
