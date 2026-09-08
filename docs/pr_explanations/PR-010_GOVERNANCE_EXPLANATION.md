# PR-010 — Checking the repairs, not just the damage

**Pull request:** #10
**Authority:** governance amendment
**Author:** Claude Code, under human product owner authorization

---

## 1. Purpose of this PR

To require that when problems found in a review are fixed, **the fixes are
checked too** — rather than taken on the word of whoever wrote them.

## 2. What changed

| File | What it is |
|---|---|
| `docs/AI_BUILD_GOVERNANCE.md` | New section 7.5 — corrections are reviewed too |
| `docs/reviews/PR-009_CODEX_REVIEW.md` | A note recording that pull request 9 was merged before its corrections were checked |
| `docs/pr_explanations/PR-010_...md` | This document |

## 3. Why the change was needed

An independent reviewer examines the work as it stood when it looked at it. The
fixes are written afterwards — by the same AI whose work the reviewer had just
faulted, and seen by nobody else.

Twice already this project has re-checked the fixes and found something:

- On one pull request, a fix quietly broke something else in the very document
  it was editing.
- On another, a fix that had been reported as complete turned out to have closed
  only some of the ways the problem could occur, and re-checking found three
  more problems on top.

Both times the AI reported the problems as resolved, in good faith, and was
wrong. That is the ordinary condition of anyone marking their own work.

The practice had been happening informally, then stopped happening, because
nothing wrote it down — the same way attribution stopped happening one pull
request after it was asked for. This is the third time a habit has quietly
lapsed. Habits are not process.

## 4. How this worked before

A reviewer would find problems, the AI would fix them and report them fixed, and
whether anyone checked the fixes depended on somebody remembering.

## 5. How it works after

Fixes get looked at, the same as the original work.

The obvious objection is that this never ends: checking fixes produces more
fixes, which need checking. So the rule states its own floor. The cycle stops
when a check comes back with nothing to report — or when the person in charge
decides to accept it and move on, which they may do at any time and for any
reason, because the final say is theirs and this rule does not qualify that.

What the rule does insist on is that when work is accepted with its fixes
unchecked, **the record says so**, naming exactly which changes went in
unexamined. Not to disapprove of the decision, but so that nobody later has to
guess.

The rule also carves out the trivial case: a typo correction does not restart
anything. Where it is unclear which kind of fix something is, it counts as the
kind that gets checked.

## 6. What goes into the system

Nothing changed here. This is a rule about how work is checked.

## 7. What the system decides

Nothing changed here. No software behaviour is affected.

## 8. What comes out

Nothing changed here.

## 9. How it can fail

- **It is a rule, not a mechanism.** Nothing enforces it. Its own origin is a
  practice that lapsed because nobody wrote it down, and writing it down only
  converts forgetting into a violation.
- **It costs time, and time is short.** Every round of checking is another
  round trip against a deadline. That pressure is exactly when this rule will be
  skipped, and the rule anticipates that by making skipping legitimate and
  recorded rather than quiet.
- **It cannot make the reviewer right.** A second look finds what it finds.

## 10. Tests run, and their results

**No tests were run.** This pull request changes documents and contains no code.

What was checked instead: that the new section did not renumber any existing
one, since verbatim review records quote section numbers and may never be
edited. The existing suite is untouched and still passes: 103 tests.

## 11. Assumptions made

- That an AI marking its own repairs as complete is not evidence they are
  complete, however sincerely meant.
- That a rule which can never terminate is not a rule, so the stopping condition
  belongs in it.
- That the person in charge may always decide to move on, and that the honest
  thing is to record that rather than to forbid it.

## 12. Known limitations

- Nothing enforces this automatically.
- It arrives one pull request too late: the pull request that prompted it was
  merged with its own fixes unchecked, and that is recorded in the review record
  rather than tidied away.
- It has never been applied.

## 13. Functionality explicitly left out of scope

No code, no automation, no check that a second review happened, and no change to
who may approve or merge anything.

## 14. Deferred to future tasks

Continuing the first authorized task: the strategies, choosing between them, the
simulator, evaluating outcomes, the loop, the run record, and a command that
runs one task end to end.

## 15. How to explain this to a judge

An independent AI reviews this project's code and finds problems. The AI that
wrote the code then fixes them and says they are fixed.

The obvious question is: who checks that? Twice we checked, and twice the fixes
were wrong — once a fix broke something new, once it had only partly worked and
three further problems came out. Both times the fixes had been reported as done,
honestly, and were not.

So fixes are now reviewed the same as the original work. The cycle ends when a
review comes back clean, or when the person in charge decides to ship — which
they may always do, and which then gets written down, naming exactly what went
in unchecked.

That last part is the honest bit. The rule does not pretend the deadline does
not exist. It makes moving on a decision somebody made, on the record, rather
than something that quietly happened.

---

**This document explains; it does not govern.** The product definition,
architecture document, task specification, and the code and its tests are the
authoritative record. Where this explanation and the repository disagree, the
repository is correct.
