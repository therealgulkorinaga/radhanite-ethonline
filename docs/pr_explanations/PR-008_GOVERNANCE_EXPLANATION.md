# PR-008 — Saying who did what

**Pull request:** #8
**Authority:** governance amendment
**Author:** Claude Code, under human product owner authorization

---

## 1. Purpose of this PR

To require every pull request to say which parties worked on it and what each
one did — so that the independent reviewer cannot quietly go unmentioned.

## 2. What changed

| File | What it is |
|---|---|
| `docs/AI_BUILD_GOVERNANCE.md` | New section 4.4 — attribution is required, not optional |
| `docs/pr_explanations/PR-008_...md` | This document |

## 3. Why the change was needed

This project's central claim is that three separate parties are involved: a
person who authorizes and approves the work, an AI that writes it, and a second
AI that independently checks it. Anyone reading a pull request should be able to
see which was which.

Every pull request so far has carried a small table saying exactly that — but
only because the product owner asked for it once, six pull requests ago, and the
AI writing them kept doing it out of habit. Nothing anywhere required it.

Habit failed exactly as habits do. Pull request #7 — whose entire purpose was
fixing a stale claim about the reviewer — was rewritten slightly and the
reviewer disappeared from it altogether. The product owner noticed and asked why.

## 4. How this worked before

Nothing required a pull request to say who worked on it. The table appeared
because it was remembered.

## 5. How it works after

Every pull request must name three things: the person who authorized it and
holds the final say, the AI that wrote the code, and the independent reviewer.

Two details are deliberate.

**The reviewer is named even when it has not reviewed anything.** Leaving the
row out looks like there is no reviewer at all, which is a bigger and less
honest claim than an empty row saying "not yet". Absence reads as denial.

**The reviewer's status is a pointer, not a copy.** Rather than restating an
outcome — which then has to be kept in step and eventually is not — the pull
request points at the review record, which is where the truth lives. That
follows the rule added in the previous pull request for the same reason.

The section states plainly why it exists, naming the pull request where the
habit failed.

## 6. What goes into the system

Nothing changed here. This is a rule about what a pull request must say.

## 7. What the system decides

Nothing changed here. No software behaviour is affected.

## 8. What comes out

Nothing changed here.

## 9. How it can fail

- **It is still a rule, not a mechanism.** Nothing checks that a pull request
  names its parties. The same AI that forgot before can forget again; the rule
  only makes the omission a violation rather than an oversight.
- **A table can be present and wrong.** Requiring attribution does not make it
  accurate.
- **More rules cost time.** This is the fourth governance change in two days,
  against a submission deadline, on a project whose product is not yet built.

## 10. Tests run, and their results

**No tests were run.** This pull request changes a rules document and contains no
code.

What was checked instead: that the new section did not renumber any existing
one. That check mattered here more than usual. The natural place for this
section was 4.3, which would have pushed the existing 4.3 down to 4.4 — and
several **verbatim records of past reviews** quote "§4.3" inside them. Those
records may never be edited, so renumbering would have left permanent, uneditable
references pointing at the wrong rule. The section was added as 4.4 instead, and
nothing moved.

The full existing test suite still passes, unaffected: 57 tests.

## 11. Assumptions made

- That an omitted reviewer reads as no reviewer existing, and is therefore worse
  than an explicit "has not reviewed".
- That the rule should record the failure that caused it, so a later reader can
  see it was learned rather than invented.
- That verbatim records are genuinely uneditable, and that section numbering must
  work around them rather than the reverse.

## 12. Known limitations

- Nothing enforces this automatically.
- It has never been applied; its first test is the next pull request.
- It does not fix the pull request where the omission happened. That one is
  merged, and the history records both the omission and the correction.

## 13. Functionality explicitly left out of scope

No code, no automation, no check comparing a pull request against this rule, and
no change to who may approve or merge anything.

## 14. Deferred to future tasks

Continuing TASK-001: the rule for deciding whether to spend more, the strategies,
the simulator, the loop, the run record, and a command to run one task end to
end.

## 15. How to explain this to a judge

Radhanite is written by one AI and checked by a different one, with a person
deciding what gets built and what gets accepted. Every pull request is supposed
to say so plainly, so you can see the separation rather than take it on trust.

That had been happening only because the AI remembered to do it. When one pull
request was rewritten, the reviewer vanished from it — and it happened to be the
pull request about not making stale claims regarding the reviewer.

Now it is required, and the reviewer is named even when it has reviewed nothing,
because leaving the line out looks like claiming no reviewer exists.

The small lesson is the useful one: on a project built by AI, anything that
depends on the AI remembering will eventually not happen. It has to be written
down, and even then it only becomes a violation rather than an accident.

---

**This document explains; it does not govern.** The product definition,
architecture document, task specification, and the code and its tests are the
authoritative record. Where this explanation and the repository disagree, the
repository is correct.
