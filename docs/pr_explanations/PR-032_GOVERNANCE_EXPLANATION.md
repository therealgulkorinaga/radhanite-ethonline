# PR-032 — Governance and current-status alignment

**Authority:** Human product owner authorization for the Claude Code → Manus handover alignment, issued 2026-09-11.

**Human product owner:** Arko (`therealgulkorinaga`), sole merge authority.

**Implementation agent:** Manus, author of this documentation-only change.

**Review agent:** Codex, independent reviewer; review status is recorded in the repository review record when review occurs.

## 1. Purpose of the PR

This pull request aligns the repository’s current governance and implementation-status documentation with the merged state on `main` and with the authorized change of primary implementation agent from Claude Code to Manus.

## 2. What changed

`docs/AI_BUILD_GOVERNANCE.md` now names Manus as the current primary implementation agent and preserves Claude Code as a historical reference for earlier work. `README.md`, `tasks/BACKLOG.md`, and `docs/ARCHITECTURE.md` now describe TASK-001 as the active runtime, TASK-006 as an implemented but not closed kernel, TASK-007 PR A as an implemented run-state foundation, and TASK-008 PR A as an implemented acquisition/catalog boundary.

The documentation also records the authoritative current test count of 652 tests passing on Python 3.12. The remaining TASK-007 runtime work and TASK-008 source-specific generation work remain explicitly incomplete.

## 3. Why the change was needed

The previous status text described an earlier repository state. It reported 242 tests, described TASK-006 as unimplemented, and described all work beyond TASK-006 as unauthorized or merely specified. Those claims were no longer true after the merged TASK-006, TASK-007 PR A, TASK-008 PR A, and builder-handover changes.

The governance document also still assigned the current implementation role to Claude Code, although the handover made Manus the current implementation agent. Leaving these statements unchanged would make the repository contradict its own authoritative code and task files.

## 4. How the relevant system worked before

The codebase already had a working TASK-001 command-line runtime. The generalized TASK-006 selection kernel, TASK-007 PR-A state model, and TASK-008 PR-A acquisition boundary were present in code, but several summary documents still described only the older TASK-001 state.

The governance process already required narrow authorization, independent review, and human-only merge authority. This PR does not alter that process.

## 5. How it works after

The documentation now distinguishes three states accurately. TASK-001 remains the active runtime. TASK-006 is implemented but not closed. TASK-007 PR A and TASK-008 PR A are implemented within their limited boundaries, while their remaining runtime, generation, adapter, benchmark, and integration work is not complete and is not authorized by this PR.

Manus is the current primary implementation agent. Arko remains the human product owner and sole merge authority. Codex remains the independent reviewer. GitHub remains the public implementation and audit trail.

## 6. Important inputs, data, or state entering the system

This change uses the current `main` branch at commit `2e20126ff1ee9c5438d532d2f2fc5f1b437b756f`, the authoritative task files, the source modules already merged for TASK-006 through TASK-008 PR A, and the result of the repository’s full test command.

No runtime input, task state, capability data, economic figure, API, dependency, credential, or external integration was changed.

## 7. Decisions made by the system

This PR makes no product or runtime decision. It records decisions already made by the product owner and already represented in the task files and source code: the current builder is Manus, TASK-001 remains the active runtime, and the TASK-006, TASK-007 PR-A, and TASK-008 PR-A implementation boundaries are distinct from the work that remains.

## 8. Outputs or state changes

The output is corrected repository documentation. The source tree, tests, task semantics, economic rules, APIs, dependencies, and implementation architecture remain unchanged.

## 9. Failure modes

The main failure mode addressed by this PR was documentation drift: a reader could incorrectly conclude that only TASK-001 existed, that the suite contained 242 tests, or that TASK-006 through TASK-008 PR A were absent or unauthorized.

This PR does not alter runtime failure handling. In particular, it does not implement TASK-007 PR B, execution transitions, terminal classification, the run loop, provider adapters, payment, or network behavior.

## 10. Tests run and results

The authoritative command was run from the repository root:

```text
PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest discover -q
```

Result:

```text
Ran 652 tests in 0.190s
OK
```

## 11. Assumptions made

The current implementation truth was taken from the checked-out `main` branch and from the authoritative task specifications. The next pull request number was treated as PR #32 for the required explanation filename, following the repository’s public pull-request sequence.

No undocumented product rule was introduced.

## 12. Known limitations

The documentation remains a status summary, not a replacement for the authoritative task files or source code. TASK-007 PR A does not constitute a working capability runtime. TASK-008 PR A does not constitute provider discovery, candidate generation, execution, or payment. No live external integration exists.

## 13. Functionality explicitly left out of scope

This PR does not change any runtime source file or test file. It does not modify TASK-006 semantics, TASK-007 semantics, TASK-008 semantics, product economics, APIs, dependencies, implementation architecture, historical review records, or historical PR explanations.

## 14. Anything deferred to future tasks

TASK-007 PR B and later runtime work remain deferred. Candidate generation from task state, benchmark state reasoning, provider-specific adapters, real payments, network integrations, and the demonstration surface remain separate future work subject to their own authorization.

## 15. How to explain this to a judge

Radhanite’s documentation now tells the same story as its code. The original two-tier runtime still runs. The generalized economic selector has been built and tested, and the repository has the immutable run-state and acquisition boundaries needed around it. The repeated run loop and real integrations have not been claimed prematurely. The project also records that Manus now builds under the same human authorization, independent review, and human-only merge controls that governed the earlier Claude Code work.

## References

[1]: ../AI_BUILD_GOVERNANCE.md "AI Build Governance"
[2]: ../ARCHITECTURE.md "Architecture"
[3]: ../../tasks/TASK-006_GENERALIZED_CAPABILITY_SELECTION.md "TASK-006 — Generalized capability selection"
[4]: ../../tasks/TASK-007_CAPABILITY_RUN_LOOP.md "TASK-007 — The capability run loop"
[5]: ../../tasks/TASK-008_CAPABILITY_ACQUISITION.md "TASK-008 — Capability acquisition and candidate generation"
