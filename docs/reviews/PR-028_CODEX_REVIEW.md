# Codex review — PR-028

**Pull request:** [#28](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/28) — the revenue-agent benchmark refactor
**Reviewer:** Codex (independent review agent, `AI_BUILD_GOVERNANCE.md` §1.3)
**Reviewed against:** `docs/PREREQ-001_PRODUCT_DEFINITION.md`, `docs/ARCHITECTURE.md`, `docs/AI_BUILD_GOVERNANCE.md`, `tasks/`
**Date issued:** 2026-09-11
**Outcome:** **Approved with corrections** — two material contradictions, both corrected

---

## 0. Note on ordering

**This prompt is committed before the review runs**, as §7.3 requires, in the
same commit as the work.

## 1. Prompt issued

Recorded **before** the review was run.

```text
You are the independent review agent for the Radhanite repository, per
docs/AI_BUILD_GOVERNANCE.md §1.3.

Review pull request #28:
https://github.com/therealgulkorinaga/radhanite-ethonline/pull/28

Documentation only. The benchmark changed from supplier onboarding to autonomous
revenue opportunity pursuit. Six new task specifications were added, The Graph
was renumbered from TASK-008 to TASK-011, and the engine was NOT redesigned. It
authorizes no implementation.

Review against these authoritative documents ONLY:
  - docs/PREREQ-001_PRODUCT_DEFINITION.md
  - docs/ARCHITECTURE.md
  - docs/AI_BUILD_GOVERNANCE.md
  - tasks/

Do NOT treat docs/pr_explanations/PR-028_GOVERNANCE_EXPLANATION.md as evidence
of correctness (§4.3).

PART A — the central claim: the engine did not move

1. The PR claims TASK-006's economics and TASK-007's runtime semantics are
   untouched. Verify by diff. Anything beyond the two reframed sentences is a
   finding.
2. Confirm radhanite/ and tests/ are identical to main.
3. Assess whether the claim is actually TRUE in substance, not just in diff:
   does any new task push benchmark-specific concepts back into TASK-006 or
   TASK-007 by implication?

PART B — provider neutrality across the new boundary

4. TASK-008 may know provider, price and invocation metadata; TASK-006 may not.
   Assess whether that asymmetry is specified tightly enough to be enforceable,
   or whether provider identity could reach the decision through the candidate.
5. TASK-011 says The Graph returns evidence and does not decide probability or
   eligibility. Confirm nothing in TASK-009, TASK-011 or TASK-007 lets evidence
   reach the economic rule directly.
6. TASK-010 documents Circle services as candidates, not workflow steps. Confirm
   no document implies a sponsor service must be called, and that PREREQ-001
   §6.3's "a run that buys nothing is correct" survives intact.

PART C — the benchmark pivot and historical truth

7. Confirm supplier onboarding is preserved as a PREVIOUS framing rather than
   erased, and that PREREQ-001 §6.3a is accurate about what it was.
8. Confirm no immutable review record and no historical PR explanation was
   edited.
9. PREREQ-001 now carries three framings: software engineering, supplier
   onboarding, revenue pursuit. Assess whether §6.6 makes the status of each
   unambiguous, or whether the document has become confusing.
10. Verify the completion contract in §6.5 is still coherent for the NEW
    benchmark, or say plainly if it is not — it was written for supplier
    verdicts.

PART D — the new task specifications

11. Six new tasks. Assess whether each has a real boundary or whether any is
    filler. Say specifically which could not be built from as written.
12. TASK-009 claims to be the ONLY place benchmark reasoning may live. Verify
    nothing in TASK-008, 010, 011, 012 or 013 also reasons about the
    opportunity.
13. TASK-008 §6.1 and §6.2 and TASK-009 §7 record unresolved decisions. Assess
    whether they are genuinely unresolved or whether the specification has
    decided them by implication.
14. TASK-008 §6.2 and TASK-006 §2.3 may be in conflict: the rule requires a
    strictly positive cost known before purchase, and marketplace pricing may
    not supply one. Judge whether this is a real blocker for TASK-010.

PART E — truthfulness

15. Confirm no document claims learned or predicted probabilities. TASK-008 §4
    and TASK-009 §5 both assert they remain declared fixtures — verify nothing
    elsewhere contradicts that.
16. Confirm testnet value is not presented as production value, and that no
    document claims Radhanite itself performs discovery or payment where that
    belongs to an adapter.
17. site/index.html is committed under §3.2, which requires staleness corrected
    in the same PR. Confirm it no longer advertises supplier diligence and that
    every integration is still marked not authorized ON the page.

PART F — numbering and consistency

18. The Graph moved TASK-008 -> TASK-011. Confirm content unchanged apart from
    the number, all references updated, no dangling links anywhere.
19. Confirm the task sequence is stated consistently in ARCHITECTURE, BACKLOG
    and README, with no document still presenting the old three-integration
    priority order.
20. Confirm no task changed authorization status and that all six new tasks
    arrive unauthorized.
21. Verify 476 tests pass and no dependency was added.

FORMAT OF YOUR FINDINGS

Number every finding, per §3.1:

    CODEX-PR028-01
    CODEX-PR028-02
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

**The reviewer's verbatim response was not supplied** to the agent writing this
record. What follows is **as relayed by the human product owner**. §0 is
unaffected: the prompt in §1 was committed before the review ran.

Both findings correspond to items the prompt itself asked about — §1 items 10
and 14 — and both were contradictions the PR's own report had already flagged as
unresolvable without changing specification behaviour. The review confirmed they
were material and authorized the change.

| | Finding | Departs from |
|---|---|---|
| **A** | `PREREQ-001` §6.5, part of the **current** benchmark definition, still used the supplier completion contract — `APPROVE`/`ESCALATE`/`REJECT` over supplier evidence categories | `PREREQ-001` §4.5, §6 |
| **B** | TASK-008 §6.2 suggested marketplace pricing might not be known before purchase, conflicting with TASK-006 §2.3's requirement for a known positive cost | TASK-006 §2.3 |

## 3. Outcome

**Approved with corrections.** The benchmark pivot itself, the six new task
specifications, the TASK-008 boundary and the claim that the engine did not move
were not faulted.

## 4. Corrections

| Finding | Correction |
|---|---|
| **A** | Current contract is now `PURSUE` / `ABANDON` / `ESCALATE` with nine machine-checkable clauses. The supplier contract is preserved as historical. The contract is explicitly *not* the economic rule |
| **B** | **TASK-006 was not weakened.** A capability may enter the candidate set only when its exact cost is known before purchase. Discovery and purchase are separated: a quote costs nothing and precedes selection; payment follows it. Circle Discovery satisfies this. A source that cannot quote is **not eligible** until a future authorized task introduces a quote or bounded-price mechanism |

**Corrections are themselves subject to review** (`AI_BUILD_GOVERNANCE.md`
§7.5). This corrective commit has not been reviewed.
