# Codex review — PR-015

**Pull request:** [#15](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/15) — give the Circle work its own task, and fix two records
**Reviewer:** Codex (independent review agent, `AI_BUILD_GOVERNANCE.md` §1.3)
**Reviewed against:** `docs/PREREQ-001_PRODUCT_DEFINITION.md`, `docs/ARCHITECTURE.md`, `docs/AI_BUILD_GOVERNANCE.md`
**Date issued:** 2026-09-08
**Outcome:** **Rejected** — the PR-013 record was incomplete and TASK-005 defines no coherent real-spend path. Three P0 findings; `-01` corrected, `-02` and `-03` recorded as unresolved product decisions.
**Commit reviewed:** `497d6bf`

---

## 1. Prompt issued

Recorded before the review was run.

```text
You are the independent review agent for the Radhanite repository, per
docs/AI_BUILD_GOVERNANCE.md §1.3.

Review pull request #15:
https://github.com/therealgulkorinaga/radhanite-ethonline/pull/15

Documentation only. It adds TASK-005 (the budget as real USDC on Arc),
reassigns BL-03 to it, marks TASK-001 as delivered, and records the third
review of PR #13 which had never been written down.

Review against these authoritative documents ONLY:
  - docs/PREREQ-001_PRODUCT_DEFINITION.md
  - docs/ARCHITECTURE.md
  - docs/AI_BUILD_GOVERNANCE.md

Do NOT treat docs/pr_explanations/PR-015_GOVERNANCE_EXPLANATION.md as evidence
of correctness (§4.3).

PART A — the record that was missing

1. §2d of docs/reviews/PR-013_CODEX_REVIEW.md now contains your third review of
   PR #13, transcribed after the fact from the session. Confirm it reproduces
   what you actually returned, including the acceptance-criteria table. Report
   any discrepancy — this is the one place in the repository where a record was
   written from memory of a conversation rather than from a pasted transcript.
2. Does recording it late, after the work was merged, need stating more plainly
   than it is?
3. TASK-001's status line claims 43 findings across 13 review passes, and that
   the final corrections were merged unreviewed. Verify both by counting.

PART B — the split between TASK-003 and TASK-005

4. TASK-003 establishes the wallet and authority; TASK-005 makes the balance real
   USDC. Is that a real separation or an administrative one? Could either be
   built and judged without the other, as TASK-003 §3.2 now claims?
5. Does TASK-005 overlap or conflict with TASK-003 or TASK-004 anywhere?
6. BL-03 previously pointed at TASK-004, which does not mention Arc. Confirm the
   mapping is now coherent across BACKLOG, ARCHITECTURE §4a, and the task files.

PART C — the specification

7. ARCHITECTURE §3.3 now argues Arc is chosen for a property — USDC settlement
   and USDC gas making cost one unit rather than two. Is that argument sound, or
   is it a rationalisation of a sponsor choice? PREREQ-001 §4.2 and §2.2 are the
   test.
8. TASK-005 §4 names three problems: a budget exceeding the balance, a balance
   moving mid-run, and costs finer than USDC's six decimals. Assess each against
   the code on main. Are they accurate, and is the decimal one correctly
   identified as determining whether a run total is what was decided or what was
   paid?
9. Is there a fourth problem none of them names? This is the question I most
   want answered.
10. Does any acceptance criterion require something unverifiable, or permit
    something ARCHITECTURE forbids? Assess criterion 7 specifically — it lifts
    §6 item 8's prohibition for real values while keeping it for simulated ones.

PART D — authorization and record integrity

11. Confirm nothing here authorizes anything, and that TASK-005 is marked NOT
    AUTHORIZED.
12. Confirm no code, dependency, credential or configuration appeared.
13. Verify every count and factual claim in the explanation independently.
14. Confirm PR-013's earlier recorded reviews are unaltered by this change.

FORMAT OF YOUR FINDINGS

Number every finding, per §3.1:

    CODEX-PR015-01
    CODEX-PR015-02
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

Recorded as received.

> Reviewed PR #15 at 497d6bf. I limited this hackathon review to essential blockers.
>
> The documentation-only scope is honest: nine files changed, with no code, dependencies, credentials, or configuration. Python 3.12 discovers and passes all 242 tests. TASK-005 remains explicitly unauthorized.
>
> The Arc rationale is technically sound: Arc officially describes fees as USDC-denominated. That gives costs one unit of account, but does not by itself solve fee budgeting or the Arc/Hedera split. Arc official documentation
>
> The newly recorded third PR-013 review accurately reproduces the response and acceptance table. However, it is not the final review that occurred.
>
> CODEX-PR015-01
> Priority: P0
> Files and lines: docs/reviews/PR-013_CODEX_REVIEW.md:573; tasks/TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md:3-4; docs/pr_explanations/PR-015_GOVERNANCE_EXPLANATION.md:103-110,142-145
>
> The record says no fourth PR-013 pass occurred. That is false. Codex reviewed commit 9fae266 after the recorded third pass, confirmed CODEX-PR013-10 and -13 fixed, and reported -06, -11, and -12 still unresolved. Commits 92681be and fe79183 followed that review and were the corrections ultimately merged unreviewed.
>
> Consequently, there were 14 review passes, not 13. The claimed 43 findings is also unsupported: the TASK-001 review records contain 42 distinct stable finding identifiers:
> - PR-003: 4
> - PR-006: 10
> - PR-009: 3
> - PR-011: 7
> - PR-012: 5
> - PR-013: 13
>
> The omitted fourth transcript must be recorded and the counts corrected. This departs from AI_BUILD_GOVERNANCE.md §§1.3(4) and 7.3.
>
> CODEX-PR015-02
> Priority: P0
> Files and lines: tasks/TASK-005_BUDGET_IN_REAL_USDC_ON_ARC.md:8,44-52,82-93; tasks/TASK-004_AGENTIC_PAYMENTS_VIA_HEDERA_AND_X402.md:7,17-19,41-48,86-93; docs/ARCHITECTURE.md:114-126,148-151; docs/pr_explanations/PR-015_GOVERNANCE_EXPLANATION.md:63-67
>
> TASK-005 requires recorded spend to correspond to USDC actually moved on Arc, but it defines neither a recipient nor a purchase/payment operation. The only task that makes the agent pay for purchases is TASK-004, which instead settles on Hedera and is not a TASK-005 dependency. Bridging or converting the Arc balance is explicitly out of scope.
>
> The same money therefore cannot presently be both the Arc budget and the Hedera purchase payment. TASK-005 cannot independently satisfy criterion 2, and the explanation's claim that both TASK-003 and TASK-005 can be built and judged independently is false—TASK-005 explicitly depends on TASK-003.
>
> TASK-004 also still claims to replace BL-03 and says the architecture lacks outbound payments, contradicting this PR's updated backlog and architecture.
>
> Before implementation, choose a coherent route: spend the Arc balance on Arc, move TASK-004's settlement to the same rail, or explicitly authorize and specify the cross-chain movement. This departs from the ownership boundaries in ARCHITECTURE.md §§3.3–3.4 and leaves PREREQ-001 §4.2's real economic expenditure undefined.
>
> CODEX-PR015-03
> Priority: P0
> Files and lines: tasks/TASK-005_BUDGET_IN_REAL_USDC_ON_ARC.md:25-37,44-46,54-76,88-123; docs/ARCHITECTURE.md:99-103
>
> TASK-005 notes that gas is paid in USDC but never specifies whether gas counts against the task budget, how enough gas is reserved before a purchase, or how estimated and actual fees are reconciled.
>
> That is the missing fourth problem. A run can authorize spending its entire remaining budget and then require an additional USDC fee to execute the transaction. Either the wallet lacks enough money, or total task expenditure exceeds the hard ceiling. Merely using the same currency makes the comparison possible; it does not enforce the ceiling.
>
> TASK-005 needs an explicit decision and acceptance test covering purchase amount plus transaction fee. Without it, criteria 1 and 6 cannot guarantee the absolute ceiling required by PREREQ-001 §4.2 and ARCHITECTURE.md §2.3.
>
> Rejected — the PR-013 review record remains incomplete, and TASK-005 does not yet define a coherent real-spend path or preserve the hard budget ceiling once Arc transaction fees are included.

## 3. Outcome

**Rejected.** All three findings accepted without dispute.

`-01` is corrected. `-02` and `-03` are **product decisions the implementing
agent must not make**, and are recorded as unresolved in TASK-005 §7.5 and §7.6
with TASK-005 marked blocked by both.

`-01` is the more uncomfortable of the three. The fourth review was not lost —
it was **misread**. The implementing agent received it as a prioritisation
instruction from the product owner and recorded it as prose describing how the
findings were worked, rather than as a review transcript. The record then
asserted positively that no fourth pass had occurred.

`-03` is the answer to a question this project's own review prompt had asked:
whether there was a fourth broken assumption the specifications missed. There
was, and it is the one that breaks the ceiling.

## 4. Corrections

| Finding | What changed |
|---|---|
| `CODEX-PR015-01` | The fourth pass recorded as §2e, as received. Counts corrected to 42 findings across 14 passes. The counting method now excludes prompt blocks, which had credited `CODEX-PR009-04` — an identifier that only ever told a reviewer where to start numbering. |
| `CODEX-PR015-02` | TASK-005 §7.5 records the unspendable-balance problem as UNRESOLVED with three routes and none chosen. TASK-004's stale `BL-03` claim and its "architecture lacks outbound payments" claim removed; its §7.1 superseded. The explanation's false independence claim corrected. |
| `CODEX-PR015-03` | TASK-005 §7.6 records the fee problem as UNRESOLVED, naming the acceptance criterion it requires — purchase plus fee — without writing it, since the rule it tests must be decided first. |

**Neither `-02` nor `-03` is resolved.** TASK-005 cannot be implemented until the
product owner settles both, and `-02` may block TASK-004 as well.
