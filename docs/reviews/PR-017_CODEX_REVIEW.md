# Codex review — PR-017

**Pull request:** [#17](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/17) — redefine Radhanite from inference allocation to dynamic capability acquisition
**Reviewer:** Codex (independent review agent, `AI_BUILD_GOVERNANCE.md` §1.3)
**Reviewed against:** the PR diff at `74c46e0` against `main`
**Date issued:** 2026-09-09
**Outcome:** **Approved with corrections** — `CODEX-PR017-01`, `-02`, `-03`

---

## 0. Governance disclosure — read this first

> **The PR-017 review prompt was recorded after the review had already run. This
> does not satisfy the normal pre-review prompt-ordering requirement in
> `AI_BUILD_GOVERNANCE.md` §7.3. The record is being committed retrospectively
> for audit completeness, not to claim procedural compliance.**

§7.3 requires the prompt to be committed **before** the review is run, for a
stated reason: *"A prompt recorded afterwards can be quietly reshaped to fit the
answer it received."* That protection was not in place for this review. Nothing
in this record should be read as evidence that it was.

The prompt in §1 and the response in §2 are the **exact** text issued and
returned, supplied by the human product owner and recorded here unaltered. An
earlier revision of this file recorded them as unavailable and paraphrased the
findings; that limitation no longer applies and the note describing it has been
removed. The ordering violation above is a separate matter and stands.

## 1. Prompt issued

Recorded **after** the review was run, per §0. Exact text as issued:

```text
Independently review PR-17, the documentation-only Radhanite product pivot.

This review is specifically about whether the repository now truthfully and consistently transitions from the already-delivered two-tier inference-oriented kernel toward dynamic capability acquisition without rewriting history or accidentally authorizing implementation.

Do not implement corrections.

Review the actual PR diff against main.

Check the following:

Product definition

1. Radhanite is now clearly defined as the economic control layer deciding which priced external capability, if any, is worth acquiring for a task.
2. task_value and budget remain distinct.
3. “Budget is permission to spend, not a target to spend” is consistent with the rest of the product definition.
4. The repository does not reposition Radhanite as a marketplace, model router, wallet, cross-chain payment product, or x402 router.

Historical integrity

5. TASK-001 remains the historical specification for the implemented two-tier system and has not been rewritten to pretend it implemented dynamic capabilities.
6. Immutable review records and historical PR explanations remain untouched.
7. Existing TASK-002 through TASK-005 remain clearly unimplemented/not automatically authorized and their substantive historical decisions were not silently rewritten.

Implementation boundary

8. The repo clearly distinguishes:
   - current implemented two-tier architecture
   - future generalized capability-selection architecture
9. BL-13 remains the explicit separate migration required before integrations can depend on generalized capability selection.
10. No runtime implementation was introduced.

ETHOnline demonstration

11. Supplier onboarding/due diligence is framed as the primary ETHOnline demonstration, not as a claim that Radhanite is now a supplier-compliance product.
12. Hedera Second Opinion and Circle research/analysis are described as external capabilities beneath Radhanite.
13. The illustrative Hedera → Circle flow is not represented as a mandatory hard-coded sponsor sequence.
14. Earlier stopping paths remain valid.

Payment/network truthfulness

15. Hedera and Arc/Circle are described as independent execution/payment environments.
16. No bridge or unified wallet is implied.
17. Arc Testnet USDC is not misrepresented as production-value USDC.
18. The Circle/Tavily relationship is not overstated as direct Tavily settlement unless explicitly supported.

Probability truthfulness

19. Success probabilities/uplifts are still described as declared benchmark fixtures rather than learned runtime estimates.

Repository consistency

20. README stale claims were correctly fixed.
21. The authoritative Python 3.12 test command is documented appropriately.
22. There are no new contradictions between PREREQ-001, ARCHITECTURE, BACKLOG, README, and TASK-002–005.
23. The committed PR explanation accurately describes the actual diff.

Pay particular attention to the reported BL-11 issue:

- determine whether the distinction between “supplier diligence as frozen demo direction” and “BL-11 implementation remains unauthorized” is coherent under the repository's governance;
- do not treat the mere existence of the demo direction as implementation unless the docs actually authorize runtime work.

Return exactly one outcome:

Approved
Approved with corrections
Rejected

For every finding provide:

- severity
- file
- exact issue
- required correction

Do not broaden scope and do not suggest BL-13 implementation as part of this PR.
```

## 2. Findings returned

Verbatim, exactly as returned. Not summarized, softened, or filtered.

```text
Reviewed PR #17 at `74c46e0` against `main`. No corrections were implemented.

The core pivot is coherent: current two-tier code and future capability selection are clearly separated; TASK-001 and historical records are untouched; TASK-002–005 remain unauthorized; BL-13 remains a separate migration; and no runtime or dependency changes appear.

Three essential documentation corrections remain.

CODEX-PR017-01

- Severity: High
- File: `docs/PREREQ-001_PRODUCT_DEFINITION.md:324-334,403-406`
- Exact issue: The supplier-diligence example labels “a defensible APPROVE / ESCALATE / REJECT” as its success condition. “Defensible” requires judgment and is not objective or machine-checkable, directly contradicting §4.5 and the document’s statement that the new vertical must meet the same standard as “tests pass.” As written, the primary demonstration is not yet demonstrably a Radhanite task.
- Required correction: Define an objective, machine-checkable success condition for the demonstration, or explicitly mark that condition unresolved and required before implementation. Keep the supplier verdict as the target output, not the success condition.

CODEX-PR017-02

- Severity: High
- File: `docs/PREREQ-001_PRODUCT_DEFINITION.md:54-91`; `tasks/BACKLOG.md:118-125`
- Exact issue: The BL-11 distinction is conceptually valid, but the authoritative product definition still says both “In V1 — autonomous software engineering” and “Only the V1 use case in §6 is being built.” Section 6 is now supplier diligence and repeatedly says it is not implemented or authorized. The latter sentence therefore falsely implies that BL-11 work is being built, while the former leaves two different current V1 verticals without explaining their relationship.
- Required correction: Label the software-engineering V1 material as the historical/current TASK-001 framing, and replace “the V1 use case in §6 is being built” with wording that makes supplier diligence a frozen demonstration direction whose implementation remains unauthorized under BL-11.

CODEX-PR017-03

- Severity: Medium
- File: Missing `docs/reviews/PR-017_CODEX_REVIEW.md`
- Exact issue: This review prompt was not committed before review. `AI_BUILD_GOVERNANCE.md` §7.3 requires each review’s prompt to be committed first. The PR has the required explanation, but no PR-017 review record or index entry.
- Required correction: Record this prompt and response, update the review index, and disclose that the prompt was recorded after the review rather than claiming the required ordering occurred.

Everything else requested checks out:

- `task_value` and budget remain separate; budget is consistently a ceiling, not a spending target.
- Radhanite is explicitly not a marketplace, router, wallet, payment protocol, or cross-chain product.
- TASK-001 and all earlier reviews/explanations are untouched.
- TASK-002–005 received only seven-line historical-status notices; their substantive specifications were not rewritten.
- BL-13 is explicit and unauthorized.
- The sponsor sequence is illustrative; all earlier stopping paths remain valid.
- Hedera and Arc/Circle are independent, with no bridge or unified balance implied.
- Testnet USDC and the Circle/Tavily seller relationship are described conservatively.
- Probabilities remain declared benchmark fixtures.
- The nine-file explanation inventory is accurate.
- Python 3.12 passes all 242 tests; the suite fails as documented on Python 3.13 and 3.14.
- No `.py`, test, dependency, credential, or configuration file changed.

**Approved with corrections**
```

## 3. Outcome

**Approved with corrections.** Three findings — two High, one Medium. No finding
disputed.

The pivot itself was not challenged. The separation of implemented architecture
from migration direction, the preservation of `TASK-001` unrewritten, the
handling of TASK-002–005, and the new boundary violations were all accepted as
recorded, and the reviewer confirmed the BL-11 distinction is *"conceptually
valid."*

## 4. Corrections

| Finding | Correction | Where |
|---|---|---|
| `CODEX-PR017-01` | Output separated from success condition; a six-clause deterministic completion contract added, checked by field and state rather than by judgement. Confidence explicitly restated as a declared fixture | `PREREQ-001` §6, **new §6.5**; `README.md` |
| `CODEX-PR017-02` | §2.1's "only the V1 use case in §6 is being built" replaced; **new §6.6** tabulates both framings with the status of each; `BL-11` note rewritten to state it is neither retired nor completed and remains unauthorized | `PREREQ-001` §2.1, **§6.6**; `BACKLOG.md`; `README.md` |
| `CODEX-PR017-03` | This record, its index row, and the disclosure in §0 | `docs/reviews/PR-017_CODEX_REVIEW.md`; `docs/reviews/README.md` |

Committed as *"Correct PR-17 demo success criteria and governance record"*
(`e20c401`) on `docs-product-pivot-skill-acquisition`.

### `CODEX-PR017-02` was corrected in two commits

The finding's required correction had **two** parts, and they landed
separately. Recorded here because the record briefly showed the finding as
closed when only half of it was.

1. *"replace 'the V1 use case in §6 is being built'"* — done in `e20c401`.
   §2.1's closing sentence now points at §6.6, which states that supplier
   diligence is frozen direction, not implemented, and not authorized under
   `BL-11`.
2. *"Label the software-engineering V1 material as the historical/current
   TASK-001 framing"* — done in `Clarify TASK-001 historical V1 framing`. §2.1
   now opens **"Historical/current TASK-001 V1 framing — autonomous software
   engineering:"**. The substance beneath the heading is unchanged.

The second part was missed by the corrective commit, which was scoped to the
findings as they were then understood, and could not be fixed while completing
this record because that authorization forbade touching the product definition.
It was authorized separately and is now closed.

**Corrections are themselves subject to review** (`AI_BUILD_GOVERNANCE.md`
§7.5). Neither the corrective commit nor this record has been reviewed.
