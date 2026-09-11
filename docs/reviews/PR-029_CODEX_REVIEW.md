# Codex review — PR-029

**Pull request:** [#29](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/29) — TASK-008 PR A: capability acquisition and candidate normalization
**Reviewer:** Codex (independent review agent, `AI_BUILD_GOVERNANCE.md` §1.3)
**Reviewed against:** `tasks/TASK-008_CAPABILITY_ACQUISITION.md`, `tasks/TASK-006_GENERALIZED_CAPABILITY_SELECTION.md`, `docs/ARCHITECTURE.md`, `docs/AI_BUILD_GOVERNANCE.md`
**Date issued:** 2026-09-11
**Outcome:** _pending — review not yet run_

---

## 0. Note on ordering

**This prompt is committed before the review runs**, as §7.3 requires, in the
same commit as the work.

## 1. Prompt issued

Recorded **before** the review was run.

```text
You are the independent review agent for the Radhanite repository, per
docs/AI_BUILD_GOVERNANCE.md §1.3.

Review pull request #29:
https://github.com/therealgulkorinaga/radhanite-ethonline/pull/29

This is TASK-008 PR A: the generic boundary that turns externally available
capabilities into TASK-006 candidates. It must normalize and nothing else — no
selection, execution, payment, task-state update, or provider adapter.

Review against these authoritative documents ONLY:
  - tasks/TASK-008_CAPABILITY_ACQUISITION.md
  - tasks/TASK-006_GENERALIZED_CAPABILITY_SELECTION.md
  - docs/ARCHITECTURE.md
  - docs/AI_BUILD_GOVERNANCE.md

Do NOT treat docs/pr_explanations/PR-029_TASK-008_EXPLANATION.md as evidence of
correctness (§4.3).

PART A — Candidate must not be contaminated

1. Confirm radhanite/capability.py is byte-identical to main and that Candidate
   still has exactly three fields.
2. Confirm no provider, network, marketplace, URL, payment rail, invocation
   metadata, sponsor or capability-type concept reaches Candidate — by field, by
   identifier construction, or by any other route.
3. CapabilityDescriptor carries name and source_reference. Assess whether either
   could leak into a Candidate through the identity rule or anywhere else.
4. The module has a whole-word scan for provider terms. Assess whether it is
   meaningful or defeatable — for example by a term not on its list, or by the
   concept arriving without the word.

PART B — the known-price invariant

5. TASK-008 §6.2 and TASK-006 §2.3 require an exact cost known before purchase,
   strictly positive. Confirm there is genuinely NO representation for an
   unknown, estimated or placeholder price.
6. Confirm nothing in this PR pays, calls out, or otherwise spends to discover a
   price.
7. Assess whether a caller could smuggle an unpriced capability through —
   Money("0.01") as a stand-in, for instance. If so, is that this layer's
   problem or the adapter's?

PART C — identity

8. The identity rule is: candidate_id = descriptor_id, unchanged. Assess whether
   that satisfies TASK-008's requirements — stable across repeated
   normalization, unique within an offer, and able to reappear later as a new
   instance with a new ID.
9. Confirm no provider-family or capability-class consumption semantics were
   introduced. TASK-006 consumption must remain candidate-ID based.
10. TASK-008 §6.1 remains unresolved — what makes two offers "the same
    capability" across iterations. Confirm the implementation defers to the
    source rather than deciding it, and say whether that deferral is sound.

PART D — the lookup

11. Confirm the descriptor is recoverable from a selected candidate ID, that the
    mapping is owned by this layer rather than embedded in Candidate, and that
    an unknown ID fails deterministically.
12. Assess CapabilityCatalog for mutability: can anything a caller holds change
    what the catalogue says after construction?

PART E — it must do nothing else

13. Confirm no selection, ranking, eligibility, execution, payment, task-state
    update, run-loop behaviour, provider adapter, or network call.
14. Confirm no dependency was added.
15. Confirm TASK-006 and TASK-007 behaviour is unchanged, and that Money,
    Probability, Assessment and Selection are untouched.

PART F — tests

16. The PR claims 38 new tests and that seven deliberate faults were each
    caught. Verify the tests detect what they claim rather than passing
    vacuously.
17. §10 records that ONE mutation initially survived because a test was weak —
    it checked caller-list mutation, which passes whatever the code does. Assess
    whether any OTHER test in this file has the same shape.
18. The PR also records correcting a provider scan that flagged "arc" inside
    "research". Assess whether the corrected scan is stronger or whether a real
    guard was lost.
19. Verify exact-decimal semantics: no float anywhere, all money and probability
    through Money and Probability.
20. Verify the claimed counts: 476 existing tests unchanged, 514 total, on
    Python 3.12.

FORMAT OF YOUR FINDINGS

Number every finding, per §3.1:

    CODEX-PR029-01
    CODEX-PR029-02
    ...

For each: identifier, file and line, what is wrong, and which specification or
boundary it departs from.

If you find nothing, say so explicitly and raise no findings.

CONCLUDE

End with exactly ONE outcome, per §7.2:
  - Approved
  - Approved with corrections  (list the finding identifiers)
  - Rejected  (state which specification or boundary was departed from)
```

## 2. Findings returned

_Pending. Codex has not yet reviewed this pull request._

## 3. Outcome

_Pending._

## 4. Corrections

_None yet._
