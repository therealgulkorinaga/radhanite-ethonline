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
