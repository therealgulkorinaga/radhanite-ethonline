# PR-016 — Writing down the rules before the integrations start

**Pull request:** #16
**Authority:** governance amendment, authorized by the human product owner
**Author:** Claude Code, under human product owner authorization

---

## 1. Purpose of this PR

To write down four decisions that until now existed only in a conversation, and
to settle the open questions in the first integration's specification.

**Nothing is built by this pull request, and nothing is authorized to be built.**

## 2. What changed

| File | What it is |
|---|---|
| `docs/AI_BUILD_GOVERNANCE.md` | When outside software may be used, and by whose decision |
| `docs/ARCHITECTURE.md` | A new forbidden claim; why the work is ordered as it is; the strategy model is fixed |
| `tasks/BACKLOG.md` | Two future ideas, neither approved |
| `tasks/TASK-002_..._OPENROUTER.md` | Its six open questions, answered |
| `docs/pr_explanations/PR-016_...md` | This document |
| `docs/reviews/PR-016_CODEX_REVIEW.md` | The review prompt, committed before the review |
| `docs/reviews/README.md` | Its row added to the index |

Seven files. No code. The test count is unchanged at 242.

## 3. Why the change was needed

A long design conversation produced decisions that were never recorded anywhere.

That has already gone wrong three times in this project. Three practices lived
only in conversation — crediting the reviewer on each piece of work, keeping the
stated review status truthful, and checking the fixes as well as the original
work — and all three quietly stopped happening. Each came back later as a
problem the product owner had to catch personally.

The four decisions here matter considerably more than any of those.

## 4. How this worked before

The first task forbade using any outside software, and it was enforced strictly —
an early piece of work was rejected for adding a test runner. Nothing said
whether that rule applied to everything that followed.

Nothing forbade claiming the system had fixed code when it had not.

Nothing said the current model of a "strategy" was fixed, so nothing prevented an
integration from quietly redefining it.

And the first integration's specification still had six unanswered questions.

## 5. How it works after

### When outside software may be used

The first task's ban on outside software applied to the first task. It does not
bind the project forever — the integrations cannot be built without some.

A later task may bring one in, subject to four conditions **together**: it is
necessary for that specific integration, it is named in that task's own
specification rather than chosen while writing the code, it is the smallest thing
that works, and it is disclosed plainly in the pull request.

The rule says outright what it is not: **general permission to add things that
seem useful.** If something is needed and the specification does not mention it,
the specification is wrong and the product owner fixes it. The AI does not settle
the question by installing it.

### A new forbidden claim

The system may not say it fixed code, changed a repository, or passed tests, when
no repository was touched and no tests were run.

This matters because of what comes next. The first integration makes the *money*
real — actual inference, actually paid for. It does not make the *work* real: no
code is edited and no test suite runs. A language model producing a confident,
plausible-looking answer is **not** the same as the job having been done, and the
gap between those two is precisely where an honest project becomes a dishonest
one.

So the honest sentence is: *"Radhanite ran real inference and then evaluated a
declared scenario."* Not: *"Radhanite fixed the bug and the tests passed."*

The rule binds every document, record and demonstration — not just the code —
because the temptation to blur it lives in prose, not in software. It sits
alongside the existing rule that forbids calling imaginary dollars by a real
currency's name. Same principle, applied to outcomes instead of money.

### The shape of a "strategy" is fixed

Today a strategy is one attempt plus one optional dearer retry. The demonstration
we had discussed wanted three kinds: a single expensive attempt, a cheap-then-
expensive attempt, and several cheap attempts judged by an expensive one.

Only the middle one fits. A single attempt has no retry; parallel attempts are
several things at once, which the current shape cannot say.

The decision is to **leave the shape alone** and not pretend. Squeezing a
single-attempt or parallel workflow into a shape built for attempt-then-retry
would make the recorded prices and probabilities describe something that did not
happen. Changing the shape properly changes what "spending more" *means*, and
therefore changes the money rule itself — so it gets its own piece of work rather
than being smuggled in alongside an integration.

### Why the work is in this order

Recorded, along with an alternative that was **considered and rejected**:
starting with the payment machinery — a headless process moving real money —
before any of the decision-making.

It would have produced something verifiable on a public ledger sooner. It was
rejected because it merges two things that are deliberately separate — *who is
permitted to spend* and *what the money actually is* — and because it contradicts
the order everything else depends on.

Recording a rejected option and why is worth more to whoever reads this later
than presenting the chosen order as though it were the only one.

### The first integration's questions, answered

| Question | Answer |
|---|---|
| What if it costs more than expected? | Set a hard maximum before calling. If the provider cannot promise to stay under it, do not make the call. |
| Where do cost estimates come from? | Published prices and declared assumptions. **Never** from watching what past calls cost. |
| Which model does what? | Fixed, named models for each tier. No automatic routing, and the provider's own router is not the decision-maker. |
| Do the assumed success rates get updated? | No. Real results are recorded; the assumptions stay as written. They will visibly disagree, and that is expected. |
| What may be claimed about success? | Only that inference ran and a declared scenario was evaluated. |
| What outside software is allowed? | Whatever is needed to call the provider. Nothing else. |

## 6. What goes into the system

Nothing. These are documents.

## 7. What the system decides

Nothing. No behaviour changes.

## 8. What comes out

Nothing.

## 9. How it can fail

- **These are rules, not mechanisms.** Nothing enforces them automatically. The
  forbidden claim in particular is a rule about prose, which no test can check.
- **The answers could be wrong.** They were given for a hackathon under time
  pressure. The cost-estimate answer in particular assumes published prices are
  reliable enough to reserve against, which has not been tested.
- **Fixing the strategy shape has a cost.** The demonstration originally
  envisaged cannot be built as described until a separate piece of work changes
  it, and that work is not approved.
- **Writing a rule down does not make it followed.** It converts forgetting into
  a violation, which is worth something, and is not the same as prevention.

## 10. Tests run, and their results

**No tests were run**, and none changed. This pull request contains no code. The
existing suite is unaffected at 242 tests, and no file under the source
directories was touched — confirmed by inspecting the changed-file list.

## 11. Assumptions made

- That a decision reached in conversation and not written down will be lost.
  This project has three examples.
- That permission to use outside software is best granted one piece of work at a
  time, because the alternative is a judgement call made while writing code.
- That it is better to leave a model unchanged and lose a demonstration than to
  approximate something and report figures describing work that did not happen.

## 12. Known limitations

- Nothing here is enforced by anything but reading.
- Nothing is built, and nothing is authorized to be built.
- The first integration is now fully specified and still requires a separate,
  explicit authorization before any of it is written.

## 13. Functionality explicitly left out of scope

All implementation. No code, no outside software, no credentials, no
configuration. Approving a piece of work is not the same as approving its
specification, and this pull request does only the latter.

## 14. Deferred to future tasks

The four integrations themselves; changing the shape of a strategy; running real
code against a real repository; and standing up a paid endpoint for the system to
buy from, which would be test scaffolding rather than part of the product.

## 15. How to explain this to a judge

Before writing any of the integrations, we wrote down the rules they have to
follow — and one of them is a rule against lying.

The system is about to start spending real money on real AI. It is **not** about
to start editing code or running tests. A language model returning a confident
answer is not the same as the job being done, and that gap is exactly where a
project starts overstating itself. So it is now a documented violation for any
part of this project — code, records, demos, write-ups — to claim it fixed
anything or that tests passed, unless a repository was genuinely changed and
tests genuinely ran.

There is a second rule of the same kind already in place: imaginary dollars may
not be called by a real currency's name. This is that rule applied to results
instead of money.

We also chose to lose something rather than fake it. A demonstration we had
planned needs three kinds of workflow, and the current design can honestly
express only one of them. Rather than squeeze the other two into a shape that
would report prices and probabilities for work that never happened, we left the
design alone and wrote down that changing it properly is a separate job.

---

**This document explains; it does not govern.** The product definition,
architecture document, task specifications, and the code and its tests are the
authoritative record. Where this explanation and the repository disagree, the
repository is correct.
