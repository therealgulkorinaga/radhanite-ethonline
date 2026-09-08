# PR-007 — Recording a review, all at once

**Pull request:** #7
**Authority:** governance amendment
**Author:** Claude Code, under human product owner authorization

---

## 1. Purpose of this PR

To stop the project claiming a piece of work has not been reviewed when it has.

## 2. What changed

| File | What it is |
|---|---|
| `docs/AI_BUILD_GOVERNANCE.md` | New section 7.4 — a review is recorded everywhere at once |
| `docs/reviews/README.md` | A sixth rule, pointing at it |
| `docs/pr_explanations/PR-007_...md` | This document |

## 3. Why the change was needed

Pull request #6 was independently reviewed twice, rejected both times, and ten
separate problems were found and fixed. Throughout all of that, the pull
request's own description continued to say the reviewer *had not yet reviewed
it*.

The proper record was accurate. The description was months of work away from the
truth, and the description is what a reader sees first.

That was the fourth time the same mistake had occurred: something changed in one
place, and a sentence describing it left untouched somewhere else. Twice the
reviewer caught it, once the author did, and this time the product owner did —
by reading the pull request and asking why it said that.

A project whose central claim is *"every change here is honestly recorded"*
cannot afford a false statement about its own review process sitting at the top
of the page.

## 4. How this worked before

Recording a review meant writing the proper record and updating an index. What
the pull request itself said was left to whoever remembered. Four times out of
several, nobody did.

## 5. How it works after

Recording a review is now **one action with three parts**: the record itself,
its row in the index, and every statement about review status in the pull
request. Doing two of the three is not "mostly done" — it produces a repository
that contradicts itself, which is worse than one that was never reviewed,
because a reader cannot tell which sentence to believe.

The section also gives the more durable advice: **stop making the same claim
twice.** A description that summarises a record has to be kept in step with it,
and anything that has to be kept in step eventually falls out of step. Pointing
at the record instead removes the possibility. Where the two disagree anyway,
the record wins.

The rule is written with the failure that produced it named in full, including
which pull request and how many times, so that anyone later can see it was
written from experience rather than invented.

## 6. What goes into the system

Nothing changed here. This is a rule about how work is recorded.

## 7. What the system decides

Nothing changed here. No software behaviour is affected.

## 8. What comes out

Nothing changed here.

## 9. How it can fail

- **It is still a rule, not a mechanism.** Nothing checks automatically that a
  pull request's description matches the review record. A person or an agent
  can still forget, and this rule's own history is four instances of exactly
  that.
- **The advice to point rather than repeat is advice.** A description that
  restates an outcome is still permitted, and still able to go stale.
- **It adds a step to a process that already has many.** Under time pressure,
  process that is not enforced is process that gets skipped.

## 10. Tests run, and their results

**No tests were run.** This pull request changes rules documents and contains no
code.

What was checked instead: that the new section did not renumber any existing
section, since other documents refer to sections by number, and that the links
between the changed files resolve.

## 11. Assumptions made

- That a false claim about process is worse than an absent one, because it
  actively misleads rather than merely omitting.
- That the same information kept in two places will eventually disagree, so the
  better fix is to keep it in one.
- That writing down the specific failure that caused a rule makes the rule more
  likely to be followed than stating it abstractly.

## 12. Known limitations

- Nothing enforces this automatically.
- It has never been applied. Its first real test is the next review.
- It does not fix the four instances already in the history; those are recorded
  where they happened.

## 13. Functionality explicitly left out of scope

No code, and no automation. No check that compares a pull request description
against a review record — that would need tooling and access to the code hosting
service, and neither is authorized. Nothing about who may approve or merge
changes.

## 14. Deferred to future tasks

Continuing TASK-001: the rule for deciding whether to spend more, the
strategies, the simulator, the loop, the run record, and a command to run one
task end to end.

## 15. How to explain this to a judge

This project claims that an independent reviewer checks the AI's work, and that
everything is honestly recorded. Then a pull request that had been reviewed
twice and rejected twice sat there saying it had never been reviewed.

The proper record was right. The summary at the top of the page was wrong, and
that is what anyone reads first.

The fix is that a review is now recorded in all three places at once, or it is
not recorded — and, better, that a summary which has to be kept in step with a
record should be replaced by a pointer to the record, because two copies of the
same fact eventually stop agreeing.

It is worth noticing how this was caught. Not by the AI that made the mistake,
and not by the reviewer, but by the person reading the pull request and asking
why it said that. Which is the whole reason a human holds the merge.

---

**This document explains; it does not govern.** The product definition,
architecture document, task specification, and the code and its tests are the
authoritative record. Where this explanation and the repository disagree, the
repository is correct.
