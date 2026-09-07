# PR-005 — Keeping the reviews

**Pull request:** #5
**Authority:** governance amendment
**Author:** Claude Code, under human product owner authorization

---

## 1. Purpose of this PR

To keep a permanent record of every independent review — both the question the
reviewer was asked and the answer it gave.

## 2. What changed

A new folder, `docs/reviews/`, containing:

| File | What it is |
|---|---|
| `README.md` | What the folder is for and how records must be written |
| `PR-003_CODEX_REVIEW.md` | The record for pull request 3: the prompt, the findings, the verdict, and the fixes |

One new subsection, `§7.3 Review records`, was added to
`docs/AI_BUILD_GOVERNANCE.md` requiring these records to exist.

## 3. Why the change was needed

The rules say an independent reviewer checks the work before it is merged. Until
now, nothing proved that ever happened. The reviewer's instructions were written
into a temporary file on one laptop, and its answer would have arrived in a chat
window and then vanished.

That is a hole in the central claim this project makes. The whole argument is
that every change can be traced to a decision somebody actually made. A review
nobody can produce afterwards is indistinguishable from a review that never
happened.

## 4. How this worked before

There was no record. The prompt for the first review sat in a temporary
directory that is wiped periodically, and nothing at all was set up to capture
what a reviewer replied.

## 5. How it works after

Every reviewed pull request now gets one file that holds four things: the exact
instructions the reviewer was given, exactly what it reported back, the verdict,
and the list of fixes made in response.

One detail is deliberate and worth pointing out. **The instructions are saved
before the review is run**, not afterwards. A question written down after you
have seen the answer can be quietly reshaped to suit it, and then the record
flatters everyone involved. Saving it first makes that impossible.

Two other rules matter. Findings are recorded word for word — not summarized,
softened, or dropped — and a finding somebody disagreed with is kept along with
the disagreement rather than deleted. And the record is explicitly a transcript,
not a source of truth: a reviewer can be wrong, and keeping what it said is not
the same as agreeing with it.

## 6. What goes into the system

Nothing changed here. This pull request changes how work is recorded, not what
any software does.

## 7. What the system decides

Nothing changed here.

## 8. What comes out

Nothing changed here.

## 9. How it can fail

- **A record could be written after the fact**, defeating the point. Nothing
  enforces the ordering except the requirement being written down and the
  history showing when each file was committed.
- **Findings could be quietly softened** when transcribed by hand. The rule
  forbids it, but a person still does the copying.
- **The folder could fill up with records nobody reads.** That is acceptable.
  The value is in being able to check, not in being read routinely.

## 10. Tests run, and their results

**No tests were run.** This pull request contains no code — only documents and a
new folder.

What was checked instead: that the new subsection did not renumber any existing
section, since other documents refer to sections by number, and that the links
between the new files resolve.

## 11. Assumptions made

- That both halves of a review matter. A finding is hard to judge without seeing
  what the reviewer was asked.
- That records should live in this repository rather than in an external system,
  for the same reason the fixes do.
- That records are named for the pull request they concern, not the pull request
  that commits them. This one is committed here but named for PR-003.

## 12. Known limitations

- The first record is now complete. Its prompt was committed before the review
  ran, and the findings were added afterwards — the commit history shows that
  ordering, which is the only thing that makes the ordering rule checkable.
- Nothing is automated. A person runs the reviewer and pastes the result.
- Ordering is enforced by convention plus the commit history, not by tooling.

## 13. Functionality explicitly left out of scope

No code. No automation, no reviewer integration, no scripts to run reviews or
collect their output, and no change to who may approve or merge anything.

## 14. Deferred to future tasks

Running the actual review of PR-003, and continuing TASK-001.

## 15. How to explain this to a judge

This project claims an independent reviewer checks the AI's work before any of
it is accepted. This pull request makes that claim checkable.

Every review now leaves a file in the repository containing the exact
instructions the reviewer was given, exactly what it found, the verdict, and the
fixes that followed. The instructions are committed before the review runs, so
they cannot be rewritten to match a favourable answer.

The short version: it is the difference between saying the work was reviewed and
being able to show it.

---

**This document explains; it does not govern.** The product definition,
architecture document, task specification, and the code and its tests are the
authoritative record. Where this explanation and the repository disagree, the
repository is correct.
