# PR-036 — TASK-009 revenue opportunity state and updater

**Implementation agent: Manus.**

## Purpose

This pull request implements the authorized TASK-009 benchmark domain layer. It
makes the revenue-opportunity state concrete without moving benchmark reasoning
into TASK-006 or TASK-007.

## What changed

`radhanite/revenue.py` adds an immutable opportunity-state mapping, an immutable
benchmark evidence contract, the benchmark initializer, and
`RevenueOpportunityUpdater`. The initializer owns the domain-specific decision
that an already-complete opportunity must enter TASK-007 as `TASK_COMPLETE`.
Incomplete opportunities enter as `RUNNING`.

The declared benchmark fixture contains a $50,000 opportunity, a $250 operating
budget, and an initial declared success probability of `0.08`. A positive market
signal changes the declared probability from `0.08` to `0.14`. A positive
commercial-fit result changes it from `0.14` to `0.17` and resolves the two
required benchmark questions, producing `PURSUE` and `task_complete=True`.
These are typed fixture transitions, not predictions or learned scores.

The updater accepts only exact immutable benchmark state and successful
`ExecutionResult` values. It does not read candidate price, inspect budget,
select capabilities, rank providers, or make network calls. Provider identity is
not required by the evidence contract.

## End-to-end demonstration

The focused integration test runs the real TASK-006 selector, the merged TASK-007
full loop, the TASK-009 initializer and updater, a fixture candidate source, and
fixture executor results. It demonstrates that the first evidence result changes
the opportunity and declared probability, and that TASK-006 uses the updated
probability in the next economic decision before the second result completes the
task.

## Validation

- Focused TASK-009 suite: **12 tests passing**.
- Full Python 3.12 suite: **725 tests passing**.
- No third-party dependencies were added.
- No provider, payment, network, persistence, UI, CRM, or LLM-generated
  probability work was added.
- The TASK-001 CLI/runtime path remains unchanged.

## Review boundary

Codex review is required before merge. The implementation agent must not merge
this pull request. The human product owner and merge authority is Arko.
