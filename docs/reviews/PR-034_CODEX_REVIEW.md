# Codex review — PR-034

**Implementation agent: Manus.**

**Pull request:** [#34](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/34) — TASK-007 PR B: one capability execution transition
**Reviewer:** Codex (independent review agent, `AI_BUILD_GOVERNANCE.md` §1.3)
**Reviewed against:** `tasks/TASK-007_CAPABILITY_RUN_LOOP.md` §§3, 5.2, 7, and 9; `tasks/TASK-006_GENERALIZED_CAPABILITY_SELECTION.md`; `tasks/TASK-008_CAPABILITY_ACQUISITION.md`; `docs/ARCHITECTURE.md`; `docs/AI_BUILD_GOVERNANCE.md`
**Date issued:** 2026-09-12
**Outcome:** Merged without review — the correction branch merged before the required independent re-review

---

## 0. Note on ordering

The review prompt is committed before Codex review runs, as `AI_BUILD_GOVERNANCE.md`
§7.3 requires.

## 1. Prompt issued

Recorded before the review was run:

```text
You are Codex, the independent review agent for the Radhanite repository.

Review pull request #34:
https://github.com/therealgulkorinaga/radhanite-ethonline/pull/34

This is TASK-007 PR B. It is authorized to implement only:
- the immutable provider-neutral ExecutionResult;
- the minimum provider-neutral executor boundary;
- exactly one execution transition for an already-selected Candidate;
- the exact ExecutionResult boundary in TransitionRecord;
- focused tests and the required status/provenance artifacts.

Review against the authoritative task specification and repository code, not the
PR explanation:
- tasks/TASK-007_CAPABILITY_RUN_LOOP.md §§3, 5.2, 7, and 9
- tasks/TASK-006_GENERALIZED_CAPABILITY_SELECTION.md
- tasks/TASK-008_CAPABILITY_ACQUISITION.md
- docs/ARCHITECTURE.md
- docs/AI_BUILD_GOVERNANCE.md

Verify the following:

1. ExecutionResult has exactly the provider-neutral semantic fields succeeded,
   committed_cost, and opaque evidence; succeeded and committed_cost use the
   exact-type safety policy; committed_cost is exact Money; evidence is detached,
   structurally frozen, cycle-safe, and not interpreted.
2. The executor receives only the selected Candidate and current RunState, and
   is called exactly once.
3. The transition requires a selected, unconsumed Candidate and a RUNNING state
   below the step ceiling. It does not select, rank, acquire, generate, update
   task state, classify stops, retry, or run a loop.
4. On every actual attempt, successful or failed and positive-cost or zero-cost,
   the candidate ID is consumed, the step count increases once, and committed_cost
   drives total_spend and remaining_budget.
5. The transition rejects negative cost, cost above candidate.cost, and cost above
   remaining_budget without clamping. It preserves the ledger identity and bounds.
6. Failure sets EXECUTION_FAILURE and is never retried. Success preserves task
   state, current success probability, and RUNNING status. No updater is called.
7. Before and after snapshots are immutable and non-recursive, and the history
   contains exactly one TransitionRecord with the exact ExecutionResult.
8. TransitionRecord accepts only None or the exact ExecutionResult type. Reject
   subclasses, arbitrary payloads, RunState, RunSnapshot, and custom objects.
9. Confirm TASK-006 and TASK-008 semantics are unchanged, no provider/payment/
   network identity was added, and no dependency was added.
10. Run the focused and full test suites under PYTHONDONTWRITEBYTECODE=1 and
    assess whether the deliberate mutation checks actually kill the listed
    execution faults.

Report findings using stable identifiers CODEX-PR034-01, CODEX-PR034-02, and so
on. For every finding give the file, line, violated boundary, and correction
required. If there are no findings, say so explicitly. Do not merge the pull
request.
```

## 2. Findings returned

Codex returned three material findings. Arko authorized corrections to this
existing PR only; no new PR was authorized and no merge was performed.

### CODEX-PR034-01 — transitive immutability through the retained Selection

**Finding:** `apply_execution(...)` checked only the top-level `Selection` and
the selected `Assessment` with insufficient transitive exact-type protection.
The public selection pipeline could admit frozen subclasses of `Candidate` or
`Assessment` carrying mutable list fields. A rejected assessment or candidate
is retained in the complete decision record and was therefore an audit escape
hatch as well.

**Correction:** `capability_execution.py` now validates the complete retained
Selection graph before executor invocation. It requires exact `Selection`,
`Assessment`, `Candidate`, economic-value, probability, identifier, step,
policy, and refusal-condition types, rejecting subclasses throughout selected
and rejected members. Normal exact repository values remain accepted.

### CODEX-PR034-02 — stale or forged Selection accepted against another RunState

**Finding:** A structurally valid Selection created for one decision context
could be passed to `apply_execution(...)` with a different current RunState.

**Correction:** The transition now matches the Selection’s recorded task value,
current success probability, remaining budget, consumed candidate IDs,
capability-step count, and maximum capability-step ceiling against the current
RunState before invoking the executor. It also requires the exact selected
Assessment to be retained in the Selection and to be eligible. No selection or
ranking is rerun.

### CODEX-PR034-03 — executor side effects and exception-path recording

**Finding:** The original executor boundary did not make the authorized
commitment ceiling explicit and could not distinguish a pre-attempt raw
exception from a post-attempt failure that had committed money.

**Correction:** The existing `CapabilityExecutor` interface now receives
`maximum_authorized_cost = min(candidate.cost, current_state.remaining_budget)`
before any side effect. A compliant executor must return an exact failed
`ExecutionResult` containing actual committed cost for every post-attempt
failure, including non-zero cost. A raw exception is permitted only before an
attempt or financial commitment begins. Malformed results are contract
violations: the generic layer does not clamp or invent accounting.

## 3. Correction verification

The focused correction suite contains 47 tests and passes. The full repository
suite contains 699 passing tests under Python 3.12. Nineteen deliberate mutation
checks killed all nineteen mutants, including the original eight PR-B faults,
both retained-graph subclass faults, skipped rejected-member validation, all
six state-context omissions, executor-before-stale-rejection, authorization
omission, malformed-result conversion, and pre-attempt exception conversion.

No dependency, provider, payment, wallet, network, retry, selection, ranking,
acquisition, task-state updater, terminal classification, or full-loop work was
added. No new public data type was introduced; the existing provider-neutral
executor interface gained its explicit authorization-ceiling argument.

## 4. Outcome

Corrections for CODEX-PR034-01, CODEX-PR034-02, and CODEX-PR034-03 were complete
on PR #34. PR #34 subsequently merged before the required independent Codex
re-review. This record therefore does not claim Codex approval; it records the
honest outcome **Merged without review**.
