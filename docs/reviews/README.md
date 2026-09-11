# Review Records

This directory holds the permanent record of every independent review carried
out on this repository — the prompt the reviewer was given, and the findings it
returned, mapped to the pull request being reviewed.

These files are **intentionally committed**. A review that lives in a chat
window or a temporary file is not a record.

Required by [`AI_BUILD_GOVERNANCE.md`](../AI_BUILD_GOVERNANCE.md) §7.3.

---

## Why this exists

`§1.3` gives Codex the role of independent reviewer, and `§7.2` says a review
concludes with one of three outcomes. Neither is verifiable if the review itself
leaves no trace.

Keeping both halves — the question asked and the answer given — makes three
things checkable by anyone, including a judge:

1. **That a review actually happened** before the work was merged.
2. **What the reviewer was asked**, so a leading or narrow prompt is visible
   rather than hidden.
3. **What it found**, so the fixes can be matched back to the findings.

The prompt is committed **before** the review is run. That ordering matters: a
prompt recorded afterwards can be quietly reshaped to fit the answer it got.

## Naming convention

```
docs/reviews/PR-<NNN>_CODEX_REVIEW.md
```

One file per pull request reviewed, named for the pull request it concerns — not
for the pull request that commits it. A review record for PR-003 is
`PR-003_CODEX_REVIEW.md` even if it is committed later.

**A merged pull request with no record still gets a row**, marked *(none)* and
**Merged without review**. Without one, an unreviewed merge is invisible in this
table and reads as a pull request that never existed — which is a stronger and
less honest claim than an empty row. This is the same reasoning as
`AI_BUILD_GOVERNANCE.md` §4.4's requirement to name the review agent even when
it has not reviewed.

If a reviewer other than Codex is ever used, substitute its name.

## Required structure

```markdown
# Codex review — PR-<NNN>

**Pull request:** #<NNN> — <title>
**Reviewer:** Codex (independent review agent, §1.3)
**Reviewed against:** <the authoritative documents>
**Date issued:** YYYY-MM-DD
**Outcome:** Approved | Approved with corrections | Rejected | Merged without review | pending

## 1. Prompt issued
## 2. Findings returned
## 3. Outcome
## 4. Corrections
```

## Rules

1. **The prompt is recorded verbatim**, exactly as issued. It is not tidied up
   afterwards.
2. **The findings are recorded verbatim.** They are not summarized, softened, or
   filtered. A finding that was disputed is recorded along with the reasoning
   that disputed it — never deleted.
3. **Findings are numbered** per `§3.1`, as `CODEX-PR<NNN>-<NN>`, so the commits
   that fix them can reference them.
4. **Section 4 lists the correction commits** that resolve each finding, so the
   trail runs from complaint to fix without leaving the repository.
5. **A merged pull request is never left "pending."** `pending` means a review
   is still expected. Once a pull request is merged, either a review outcome is
   recorded or the record says **Merged without review** — which is not one of
   §7.2's three substantive outcomes, but the honest absence of them. Leaving
   `pending` on a merged pull request implies a review that will never arrive.
5. **A review record is a transcript, not a source of truth.** The product
   definition, architecture document, task specification, code and tests remain
   authoritative. A reviewer can be wrong, and the record preserves what it said
   rather than endorsing it.
6. **Recording a review updates this directory, the index below, and the pull
   request itself — in one step** (`AI_BUILD_GOVERNANCE.md` §7.4). A review
   recorded in some places but not others leaves the repository contradicting
   itself. Where a pull request and a record disagree, the record is correct.

## Index

| Pull request | Record | Outcome |
|---|---|---|
| [#3](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/3) | [PR-003](PR-003_CODEX_REVIEW.md) | Rejected → **Approved with corrections** → 4 findings, all corrected |
| [#6](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/6) | [PR-006](PR-006_CODEX_REVIEW.md) | Rejected → Rejected again → 10 findings, all corrected |
| [#9](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/9) | [PR-009](PR-009_CODEX_REVIEW.md) | **Approved with corrections** → 3 findings, all corrected; rule itself found correct |
| [#11](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/11) | [PR-011](PR-011_CODEX_REVIEW.md) | Rejected → Rejected again → 11 findings, all corrected |
| [#12](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/12) | [PR-012](PR-012_CODEX_REVIEW.md) | Rejected → **Approved with corrections** → 5 findings, all corrected; evaluation rebuilt |
| [#13](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/13) | [PR-013](PR-013_CODEX_REVIEW.md) | Rejected twice plus one corrupted pass → 13 findings, all corrected; loop rebuilt twice. Final corrections merged **unreviewed** |
| [#14](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/14) | [PR-014](PR-014_CODEX_REVIEW.md) | **Merged without review** — prompt committed, review never run |
| [#15](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/15) | [PR-015](PR-015_CODEX_REVIEW.md) | **Rejected** → 3 P0 findings; `-01` corrected, `-02`/`-03` unresolved product decisions |
| [#16](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/16) | [PR-016](PR-016_CODEX_REVIEW.md) | **Merged without review** — prompt committed, review never run |
| [#17](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/17) | [PR-017](PR-017_CODEX_REVIEW.md) | **Approved with corrections** → 2 High, 1 Medium. Prompt and findings recorded verbatim, but **retrospectively** — the prompt was not committed before the review (§7.3 deviation, disclosed in the record). All 3 corrected |
| [#18](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/18) | *(none)* | **Merged without review** — governance record correction |
| [#19](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/19) | *(none)* | **Merged without review** — TASK-006 specification |
| [#20](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/20) | *(none)* | **Merged without review** — TASK-006 authorization |
| [#21](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/21) | [PR-021](PR-021_CODEX_REVIEW.md) | **Approved** → no findings. Prompt recorded **retrospectively** (§7.3 deviation) and the verbatim response was not supplied — both disclosed in the record |
| [#22](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/22) | [PR-022](PR-022_CODEX_REVIEW.md) | **Approved with corrections** → 2 findings, both auditability, both corrected. **Prompt committed before the review** (§7.3 satisfied); verbatim response not supplied |
| [#23](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/23) | [PR-023](PR-023_CODEX_REVIEW.md) | **Rejected** → 3 findings, boundary and record, all corrected. **Prompt committed before the review** (§7.3); verbatim response not supplied. Corrections written test-first |
| [#24](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/24) | [PR-024](PR-024_CODEX_REVIEW.md) | pending — **prompt committed before the review**, in the same commit as the work |
| [#25](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/25) | [PR-025](PR-025_CODEX_REVIEW.md) | pending — **prompt committed before the review**, in the same commit as the work |
| [#26](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/26) | [PR-026](PR-026_CODEX_REVIEW.md) | **Rejected** → 7 findings, all corrected. Included a **fabricated quotation** attributed to TASK-006 §2.5, and a regression guard the reviewer defeated in one line. **Prompt committed before the review** (§7.3); verbatim response not supplied |
| [#27](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/27) | [PR-027](PR-027_CODEX_REVIEW.md) | **Rejected twice** → 5 findings, then 3 more on re-review, all corrected. Included a **recursively defined** history and a **defeatable** step ceiling. **Prompt committed before the review** (§7.3); verbatim responses not supplied |
| [#28](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/28) | [PR-028](PR-028_CODEX_REVIEW.md) | **Approved with corrections** → 2 material contradictions, both corrected: the current completion contract was still the supplier one, and pre-purchase pricing conflicted with TASK-006 §2.3. **Prompt committed before the review** (§7.3) |
