# Codex review — PR-024

**Pull request:** [#24](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/24) — the ETHOnline progress page, and §3.2 which permits it
**Reviewer:** Codex (independent review agent, `AI_BUILD_GOVERNANCE.md` §1.3)
**Reviewed against:** `docs/AI_BUILD_GOVERNANCE.md`, `docs/ARCHITECTURE.md`, `docs/PREREQ-001_PRODUCT_DEFINITION.md`, `tasks/`
**Date issued:** 2026-09-11
**Outcome:** _pending — review not yet run_

---

## 0. Note on ordering

**This prompt is committed before the review runs**, as §7.3 requires, in the
same commit as the work — as it was for PR-022 and PR-023.

## 1. Prompt issued

Recorded **before** the review was run.

```text
You are the independent review agent for the Radhanite repository, per
docs/AI_BUILD_GOVERNANCE.md §1.3.

Review pull request #24:
https://github.com/therealgulkorinaga/radhanite-ethonline/pull/24

It does two things: it adds a public ETHOnline progress page at site/index.html,
and it adds §3.2 to the governance — a fifth change-authorization authority for
public communication material, without which the page could not be committed at
all.

Review against these authoritative documents ONLY:
  - docs/AI_BUILD_GOVERNANCE.md
  - docs/ARCHITECTURE.md
  - docs/PREREQ-001_PRODUCT_DEFINITION.md
  - tasks/ (for what is and is not authorized)

Do NOT treat docs/pr_explanations/PR-024_GOVERNANCE_EXPLANATION.md as evidence
of correctness (§4.3).

PART A — the amendment, and whether it is too wide

1. §3 previously admitted four authorities and stated that it covers "all
   committed repository content ... and any other committed artifact". Confirm
   a progress page genuinely fits none of the four, so the gap the amendment
   closes is real rather than manufactured to justify the page.
2. Assess whether §3.2's five conditions are tight enough. Say specifically
   whether you can construct material that satisfies all five and still
   misleads a reader.
3. §3.2 forbids shipping code, dependencies or a build step under this
   authority. Is that prohibition clear enough to be enforced at review, and
   does vercel.json stay inside "the minimum configuration required to serve
   them"?
4. Does the amendment weaken §3 for anything OTHER than communication material?
   Look for wording that a future change could stretch.
5. Confirm the amendment changes no product or architecture decision, and that
   it did not silently renumber or alter §3.1 or any other cited section.

PART B — the page, claim by claim

6. Verify EVERY figure on site/index.html against the repository at the commit
   the page names: 423 tests, 23 pull requests merged, 47 review findings, 0
   external dependencies, 12 modules, "3 of 5 steps" if present. Report any that
   is wrong or unverifiable.
7. The "Implemented" list and the "Not built" list are the page's central
   claim. Check each entry independently. A single item on the wrong side is a
   serious finding.
8. ARCHITECTURE §6 items 8-12 apply in full. Confirm the page does not describe
   simulated values as USDC, does not present declared fixtures as measured or
   learned, does not present testnet value as production value, does not
   misdescribe a payee, and does not claim Radhanite fixed code, changed a
   repository, or ran tests as a task.
9. The page names Hedera, Circle/Arc and Privy. Confirm each is visibly marked
   unauthorized ON THE PAGE, not merely in a document a reader will not open,
   and that no wording implies an integration exists.
10. The review record card shows outcomes including rejections. Verify those
    against docs/reviews/ and confirm none is softened.
11. Assess the provenance line. Does naming a commit and date actually protect a
    reader from a stale page, or is it decoration?

PART C — scope and truthfulness of the PR itself

12. Confirm no .py file, test, or dependency changed, and that the claimed test
    count is accurate.
13. Confirm no task changed authorization status and that TASK-006's remaining
    work is untouched.
14. The explanation admits the page has no tests and that nothing enforces
    freshness automatically. Assess whether that disclosure is complete, or
    whether it understates the risk.

FORMAT OF YOUR FINDINGS

Number every finding, per §3.1:

    CODEX-PR024-01
    CODEX-PR024-02
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
