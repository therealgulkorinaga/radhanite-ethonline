# PR-004 — Making review fixes traceable

**Pull request:** #4
**Authority:** governance amendment
**Author:** Claude Code, under human product owner authorization

---

> **A note on numbering.** This pull request is one of the reasons the build plan
> and the pull request numbers no longer line up.
>
> TASK-001 was planned as twelve build steps, originally labelled PR-003 through
> PR-014 on the assumption they would match GitHub's numbering. This governance
> pull request, and the one after it, landed in the middle of that sequence and
> took numbers #4 and #5. From that point the two numberings diverge: the second
> build step is pull request **#6**, not #4.
>
> Files and finding identifiers here are named for the **GitHub pull request
> number**, never for a position in the build plan. GitHub numbers are permanent,
> assigned at creation and shared with the issue counter, so they cannot be
> reassigned. When the plan and the record disagreed, the plan moved.
>
> Governance work interleaving with build work is expected, not an accident, so
> this divergence will widen. Read pull request numbers as pull request numbers.

## 1. Purpose of this PR

To make sure that when a reviewer finds a problem, the fix for that problem can
always be found again later.

## 2. What changed

One new subsection, `§3.1 Referencing a review finding`, was added to
`docs/AI_BUILD_GOVERNANCE.md`. Nothing else in the repository changed.

## 3. Why the change was needed

The rules already said that a fix must reference the review finding it resolves.
They never said *how*. In practice that meant a reviewer would say "this is
wrong", someone would fix it, and six weeks later nobody could match the fix back
to the complaint.

The usual solution is a bug tracker: a separate system holding a list of
problems. That is a lot of machinery for a project this size, and it puts the
record somewhere other than where the work is.

## 4. How this worked before

Fixes were required to reference a finding, but findings had no names. A fix
could only gesture vaguely at what it was fixing.

## 5. How it works after

Every problem a reviewer raises now gets a short label, like `CODEX-PR003-01` —
meaning "the first problem Codex found in pull request 3". Labels are handed out
in the order the review lists them and are never reused.

The fix for that problem carries the same label in its description. That means
the entire life of a problem — what was wrong, what was changed, and why that
settles it — can be pulled up with a single search of the project's history.

The record lives with the work, and nothing else has to be maintained. The
section closes with a deliberately blunt line: a correction that names no
finding is not a correction, it is an unauthorized change.

## 6. What goes into the system

Nothing changed here. This is a rule about how humans and AI agents write
descriptions of their work.

## 7. What the system decides

Nothing changed here. No software behaviour is affected.

## 8. What comes out

Nothing changed here.

## 9. How it can fail

- **The labels could be applied carelessly**, reusing a number or skipping one,
  which would make the trail misleading rather than absent. Nothing enforces
  this automatically; it depends on whoever records the review.
- **A fix could quietly not reference anything.** The rule says such a change is
  unauthorized, but the rule is checked by people, not by tooling.
- **It could create bureaucracy for its own sake.** The convention was kept to
  one label and one line in a description precisely to avoid this.

## 10. Tests run, and their results

**No tests were run.** This pull request changes a rules document and contains
no code.

What was checked instead: that adding the subsection did not renumber any
existing section, since other documents refer to sections by number. Those
numbers were confirmed unchanged.

## 11. Assumptions made

- That the project does not want a separate bug tracker, and that keeping the
  record in the project's own history is preferable.
- That reviews will usually come from Codex, so the label format names the
  reviewer and generalizes if another reviewer is ever added.
- That one label and one reference line is enough, and anything more would be
  process for its own sake.

## 12. Known limitations

- Nothing enforces the convention automatically.
- It has never been used. The first real test will be the first review that
  actually finds something.

## 13. Functionality explicitly left out of scope

No code. No bug tracker, no issue templates, no automation, and no change to
what the three parties are allowed to do.

## 14. Deferred to future tasks

Continuing TASK-001, which is where the convention will first be exercised.

## 15. How to explain this to a judge

When a reviewer finds a problem in this project, that problem gets a short
label, and the fix carries the same label. One search of the project's history
brings up the complaint and its resolution together.

It replaces what would normally need a separate bug-tracking system with a
naming convention, which is the right size for a project like this. The point is
the same either way: you can check that a problem raised was a problem actually
fixed, rather than taking anyone's word for it.

---

**This document explains; it does not govern.** The product definition,
architecture document, task specification, and the code and its tests are the
authoritative record. Where this explanation and the repository disagree, the
repository is correct.
