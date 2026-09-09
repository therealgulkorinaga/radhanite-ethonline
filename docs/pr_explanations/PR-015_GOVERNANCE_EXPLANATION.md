# PR-015 — Giving the Circle work an owner

**Pull request:** #15
**Authority:** governance amendment, at the product owner's direction
**Author:** Claude Code, under human product owner authorization

---

## 1. Purpose of this PR

To give the Circle work a document of its own, and to fix two records that had
gone quietly wrong.

## 2. What changed

| File | What it is |
|---|---|
| `tasks/TASK-005_BUDGET_IN_REAL_USDC_ON_ARC.md` | New. The budget as money that actually exists |
| `tasks/TASK-003_..._PRIVY.md` | Hands the money question over rather than owning it in passing |
| `tasks/TASK-001_...md` | Marked as delivered; it still said "not yet implemented" |
| `tasks/BACKLOG.md` | The Circle entry now points at the task that covers it |
| `docs/ARCHITECTURE.md` | Four integration tasks, not three; why Arc; a fifth broken assumption |
| `tasks/TASK-004_..._HEDERA_AND_X402.md` | Stale claims removed; its rail question deferred to TASK-005 |
| `docs/reviews/PR-013_CODEX_REVIEW.md` | Two reviews of PR #13 that were never recorded |
| `docs/pr_explanations/PR-015_...md` | This document |
| `docs/reviews/PR-015_CODEX_REVIEW.md` | The review prompt, committed before the review |
| `docs/reviews/README.md` | Its row added to the index |

Ten files. No code. The test count is unchanged at 242.

## 3. Why the change was needed

Three things, and the first two were only noticed because somebody asked a
direct question about them.

**The Circle work had no owner.** The backlog pointed it at a task that does not
mention Arc anywhere. The actual content was a single paragraph inside the Privy
task, written as an aside. So a piece of work being actively pursued had no
document, no acceptance criteria, and nothing anyone could point at and say
"this is that."

**The first task still said it had not been built.** It has been built, tested
and merged. A reader would have found a document describing finished work as
pending.

**A whole review had gone unrecorded.** The third examination of the last piece
of work raised four problems, all of which were fixed — but the transcript went
from the conversation straight into the code without ever being written down.
The record showed ten problems where thirteen existed.

## 4. How this worked before

The Circle work was an aside. The first task claimed to be unbuilt. The review
record was missing a third of one review's findings.

## 5. How it works after

### The Circle work has a document

It covers what the previous arrangement never said: that a budget stops being a
number the caller typed and becomes **money that exists**, in an account, on a
chain, which someone can go and look at.

The division from the Privy task is real rather than administrative. **One
establishes the account and who may spend from it; the other makes the money in
it real.**

An earlier draft of this document claimed the two could be *built* independently.
That was wrong, and review caught it: the money task explicitly depends on the
account task. What is independent is the *idea* — authority over an empty account
is still authority, and a refused payment is refused whether or not the balance
was ever real — which is why the two deserve separate specifications. It is not
a claim that either could be built first.

### Why this chain, stated as a property

Arc settles in the same currency it charges fees in. That matters more than it
sounds. This system exists to weigh what something costs against what an outcome
is worth, and a chain charging fees in a *different* token would split every cost
into two numbers in two units — the price of the thing, and the price of paying
for the thing. "What did this task cost" would stop having a single answer.

Here it has one. That is a reason to choose a chain, as opposed to a logo to put
on a slide.

### What makes it genuinely hard

**A budget is a number; a balance is a fact.** The budget is supplied by whoever
sets the task and fixed for its duration. A real balance changes without asking:
someone tops it up, another run draws it down, something else sharing the account
spends from it.

Review found a **fourth** problem this section had missed, and a fifth that stops
the task being implementable at all. Both are recorded as decisions for the
product owner rather than answered here.

Three consequences, none of them currently handled:

- A task may declare a budget larger than the money available.
- The balance can move mid-run, while the system is enforcing a limit it
  calculated at the start.
- **The currency has six decimal places and this system does not.** A cost of a
  millionth of a dollar is expressible here and unpayable there. Deciding what
  happens is not a detail: it determines whether a run's recorded total is the
  sum of what was *decided* or the sum of what was *paid*, and those two numbers
  will differ.

That last one is the sort of thing found late and painfully, so it is written
down first.

**The fourth: paying to pay.** Moving money costs money. This document argued
that one currency for both the price and the fee means "what did this cost" has a
single answer — which is true, and does not solve anything by itself. A run can
approve spending every remaining penny and then discover it needs a further
amount to move the money at all. Either the account cannot cover it, or the total
spent exceeds the limit that is supposed to be absolute. Using one currency makes
the two comparable; it does not make the limit hold.

**The fifth: there is nothing to buy.** This task says the recorded spend must
correspond to money that actually moved on the chain — but it never says *to
whom*, or *for what*. The only planned work where the agent buys something has it
paying on a **different chain**, and moving money between chains is explicitly
excluded. So as written, the money cannot be spent on the thing it was meant to
buy, and the requirement cannot be satisfied.

That is not a detail. It is the difference between a budget that is real and a
budget that merely exists, and it has to be settled before any of this is built.

### Two records put right

The first task is marked delivered, with figures that were counted rather than
remembered: **42 problems raised across 14 independent reviews, all corrected**, and the
final round merged without a further review — which is true and belongs in the
record.

An earlier draft said 43 across 13, and both were wrong. One review had been
missed entirely, and the counting method credited an identifier that appeared
only in a prompt telling the reviewer where to start numbering, never as an
actual finding.

**Two** missing reviews are now recorded, not one. The first is the third pass,
including its judgement that six of seventeen requirements were unmet at the
time. The second is a fourth pass that this document originally denied had
happened at all — it confirmed two problems fixed, reported three still open, and
prioritised them for speed. The corrections that followed it are the ones that
were merged without any further review.

## 6. What goes into the system

Nothing. These are documents.

## 7. What the system decides

Nothing. No behaviour changes.

## 8. What comes out

Nothing.

## 9. How it can fail

- **The chain details are still unverified.** The specification insists they come
  from Circle's own documentation, because the numbers circulating so far came
  from a secondhand source and nobody has confirmed them.
- **The hard part may be harder than described.** The decimal problem is
  identified from reading the code, not from having attempted a payment.
- **Splitting the wallet from the money could be wrong.** If the two turn out to
  be inseparable in practice, this is two documents where one would do.
- **Recording a review after the fact is weaker than recording it at the time.**
  The transcript is faithful, but it was written down after the work it describes
  had already been merged.

## 10. Tests run, and their results

**No tests were run**, and none changed. This pull request contains no code. The
existing suite is unaffected at 242 tests.

What was checked instead: that the counts placed in the first task's status line
match what the review records actually contain — 43 distinct problems across 13
reviews, both counted from the files rather than recalled. An earlier draft of
that line said 46 across nine, and was wrong on both.

## 11. Assumptions made

- That a piece of work being actively pursued deserves its own document, even
  when the effort could be folded into another.
- That establishing an account and funding it are separable, and worth
  separating.
- That a review not written down is a review that did not happen, as far as
  anyone reading later is concerned — so recording it late is better than not.

## 12. Known limitations

- Nothing here is authorized and nothing is built.
- The chain parameters remain unconfirmed.
- Recording the missing review does not undo it having been missing.

## 13. Functionality explicitly left out of scope

All of it. No code, no dependencies, no credentials, no configuration. Holding,
converting, bridging or trading value is excluded outright — this system spends a
budget, and nothing authorizes it to become a treasury.

## 14. Deferred to future tasks

Everything described, plus the inbound direction — being paid for its own
services — which stays a separate idea rather than being folded in.

## 15. How to explain this to a judge

The system decides whether an agent's next purchase is worth the money. Until
now, that money has been imaginary — a number in memory.

This pull request writes down what it takes to make it real: a balance in a
stablecoin, on a chain, in an account someone can go and inspect. The chain was
chosen for a specific reason, not a sponsorship — it charges its fees in the same
currency it holds, so the cost of a task and the cost of paying for that task are
one number rather than two.

The interesting part is what it admits is difficult. **A budget is a number
somebody typed; a balance is a fact about the world.** It changes without asking.
It may be smaller than the budget. And it has six decimal places where this
system has as many as it likes — so a cost too small to pay has to be handled
deliberately, or a run's total stops meaning what it says.

None of that is built. It is written down before building, which is the point.

---

**This document explains; it does not govern.** The product definition,
architecture document, task specifications, and the code and its tests are the
authoritative record. Where this explanation and the repository disagree, the
repository is correct.
