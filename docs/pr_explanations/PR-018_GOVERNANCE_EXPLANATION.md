# PR-018 — Two merged pull requests were still saying a review was coming

**Pull request:** #18
**Authority:** governance record correction (`AI_BUILD_GOVERNANCE.md` §7.4), authorized by the human product owner
**Author:** Claude Code, under human product owner authorization

---

## 1. Purpose of this PR

To stop two review records from saying something that is no longer true.

Pull requests #14 and #16 were merged. Their review records still said the
review was **pending**. On a merged pull request, "pending" promises a review
that will never arrive.

**No code changed. No product decision was made.** This corrects the
repository's account of its own process.

## 2. What changed

| File | What it is |
|---|---|
| `docs/reviews/PR-016_CODEX_REVIEW.md` | Outcome corrected from "pending" to "Merged without review", with the reason |
| `docs/reviews/PR-014_CODEX_REVIEW.md` | The same correction — it had the identical problem |
| `docs/reviews/README.md` | Both index rows corrected; a new rule so this cannot recur silently |
| `docs/pr_explanations/PR-018_...md` | This document |

Four files. No `.py` file. The test count is unchanged at 242.

## 3. Why the change was needed

Radhanite has a rule about exactly this, and it was written after the same
mistake happened before.

`AI_BUILD_GOVERNANCE.md` §7.4 says a review is *"recorded everywhere at once, or
it is not recorded"* — the record, its index row, and the pull request's own
claims. Its stated reason:

> A review recorded in two of the three places has produced a repository that
> contradicts itself, which is worse than one that had not been reviewed at all
> — a reader cannot tell which statement to believe.

That rule exists because pull request #6 was reviewed twice and rejected twice
while its own description still read *"Codex: has not yet reviewed."*

This is the mirror image. Nothing was reviewed, and nothing claimed it was — but
"pending" is a claim about the **future**, and on a merged pull request that
claim is dead. A reader checking whether PR-016 was reviewed would have been
told to wait for an answer that was never coming.

## 4. How this worked before

Both records read:

```
Outcome: pending — review not yet run
Findings: Pending. Codex has not yet reviewed this pull request.
Outcome: Pending.
Corrections: None yet.
```

And both index rows read simply `pending`.

Every one of those statements was accurate on the day it was written. None of
them was updated when the pull request merged.

## 5. How it works after

Both records now say **Merged without review**, with the date and the fact that
the human product owner merged them — which §1.1 gives them sole authority to
do.

Each record also explains *why the correction was made*, so a future reader sees
the process failure rather than a tidy record that hides it. And each notes a
detail worth keeping: **the review prompt was committed before the review would
have run**, exactly as §7.3 requires. That half of the process held. The review
simply never followed.

"Merged without review" is deliberately **not** presented as one of the three
outcomes in §7.2 — Approved, Approved with corrections, Rejected. It is the
*absence* of a review, and calling it an outcome would make it sound like a
verdict somebody reached.

## 6. What goes into the system

Nothing. This is a documentation correction with no runtime, no inputs, and no
state.

## 7. What the system decides

Nothing. No decision logic exists in these files.

The only judgement made here was a human one, already made: the product owner
chose to merge both pull requests without a review. That was theirs to decide.
This PR records the decision rather than changing it.

## 8. What comes out

A review index in which **no merged pull request is marked pending**, and two
records that say what actually happened to them.

## 9. How it can fail

The failure mode is recurrence: the next pull request merged without a review
leaves another stale `pending` behind, and someone has to notice again.

So the index now carries a rule rather than relying on anyone remembering:

> **A merged pull request is never left "pending."** `pending` means a review is
> still expected. Once a pull request is merged, either a review outcome is
> recorded or the record says **Merged without review**.

That is checkable by looking, which is the most that can be asked of a rule
about prose.

## 10. Tests run and their results

```
$ python3.12 -m unittest discover -q
Ran 242 tests in 0.09s
OK
```

**242 passing, unchanged.** No test could have been affected — this pull request
contains no code. The suite was run to confirm the repository is still green.

## 11. Assumptions made

- **Both merges were deliberate.** The product owner said so directly for #16
  (*"just merging now, no need to review"*), and #16's own merge record confirms
  who merged it. #14's merge is treated the same way.
- **Neither was reviewed off the record.** If a review did run for either and
  was simply never written down, these records are now wrong in a new way and
  should be replaced with the actual findings.

## 12. Known limitations

- **This does not make the pull requests reviewed.** Two merged changes to the
  governance and architecture documents have been examined by nobody but the
  agent that wrote them. That is now visible instead of obscured, which is an
  improvement in honesty and not in review coverage.
- **PR-017's record has its own, separate disclosure.** It was written after its
  review ran, and its findings are as relayed rather than verbatim. That is
  disclosed in `docs/reviews/PR-017_CODEX_REVIEW.md` §0 and is untouched here.

## 13. Explicitly out of scope

- No earlier review record was altered. Only #14 and #16 — the two that were
  untrue — and the shared index.
- No finding, prompt, or verbatim reviewer text was edited anywhere. §7.3
  forbids it, and nothing here needed it.
- `BL-13` is not begun. No task changed authorization status. No code,
  dependency, or configuration was touched.

## 14. Deferred to future tasks

Nothing is deferred. This correction is complete.

Whether pull requests #14 and #16 should now be reviewed retrospectively is a
question for the product owner. It is not deferred work — it is a decision that
has not been asked for.

## 14a. Adjacent-document disclosure

**PR-014 was corrected alongside PR-016, and only PR-016 was asked for.**

`AI_BUILD_GOVERNANCE.md` §2.1 permits the minimum necessary adjacent-document
correction where leaving a document alone would make the repository *"contradict
itself or state something untrue."* PR-014's record carried the identical false
promise, in the same file's index, one row away. Correcting one and leaving the
other would have produced an index where two merged pull requests in the same
state were described differently, and a reader would have found the
inconsistency immediately.

The edit is the same three-line change applied to a second file, introduces no
new product or architecture decision, and is disclosed here as §2.1 requires.

The rule added to `docs/reviews/README.md` is disclosed on the same basis: once
two records use an outcome value the template did not list, the template was
itself inaccurate.

## 15. How to explain this to a judge

> Two of our pull requests were merged without an independent review. Their
> records still said a review was *pending* — which, on something already
> merged, is a promise nobody was going to keep.
>
> We didn't quietly change them to look reviewed. We changed them to say
> **"merged without review"**, with the date and who decided, and we wrote down
> a rule so the next one can't slip through the same way.
>
> That's the whole point of the governance in this repository. It's not there to
> make the project look rigorous — it's there to make the project's own record
> of itself trustworthy, including the parts where the process didn't hold.
