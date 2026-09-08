# PR-006 — Money that is exact, and the shape of a task

**Pull request:** #6
**Authority:** TASK-001 (authorized task)
**Author:** Claude Code, under human product owner authorization

---

## 1. Purpose of this PR

To build the two things every later part of Radhanite will handle: **an amount
of money**, and **a task**.

Neither decides anything yet. They are the nouns the rest of the system will use.

## 2. What changed

| File | What it is |
|---|---|
| `radhanite/money.py` | An amount of US dollars that is always exact |
| `radhanite/task.py` | The five things that define a piece of work |
| `tests/test_money.py` | 31 checks on the money type |
| `tests/test_task.py` | 18 checks on the task type |
| `radhanite/__init__.py` | Updated to say what is now built and what is not |
| `docs/pr_explanations/PR-006_...md` | This document |
| `docs/reviews/PR-006_CODEX_REVIEW.md` | The independent review of this pull request |
| `docs/reviews/README.md` | Its row added to the index of reviews |

The test count went from 3 to 52.

This pull request was **rejected on its first review** and revised. Seven
problems were found and fixed. The full record is in
`docs/reviews/PR-006_CODEX_REVIEW.md`, and the sections below describe the
corrected state.

## 3. Why the change was needed

Radhanite's entire job is deciding whether one amount of money is worth spending
to gain another. Before it can decide anything, it needs to be able to *hold* an
amount of money without getting it wrong, and to *hold a task* without losing
one of the five things that define it.

## 4. How this worked before

Nothing existed but an empty package. There was no way to express a sum of money
or a piece of work.

## 5. How it works after

### Money that cannot quietly be wrong

Computers store fractions in a way that cannot represent most decimal amounts
exactly. The classic demonstration is that a computer asked for `0.1 + 0.2`
answers `0.30000000000000004`, not `0.3`.

Usually that is harmless. For Radhanite it is not. Every decision this system
makes is a comparison between two amounts — *is what I would gain worth more
than what I would spend?* — and an error of a fraction of a penny is invisible
right up until it lands on the wrong side of such a comparison. Then the system
makes the wrong decision, confidently, with nothing in the record to show why.

So money here is exact. It also **refuses to be created from the inexact kind of
number at all**, so the mistake cannot be made by accident later:

```
Money("0.10") + Money("0.20") == Money("0.30")     always true
Money(0.1)                                          refused outright
```

Being careful once turned out not to be enough. The reviewer found that simply
using the exact kind of number still permits silent rounding, because the tool
Python provides works to a default of 28 significant digits and any code running
alongside can change that setting. So money now does its arithmetic under its own
settings, with a much larger limit, and with an instruction that **if an answer
ever would be rounded, stop and raise an error instead of returning it**. Amounts
are exact or the program halts. Nothing is ever almost right.

Amounts that are not real quantities are refused too. Infinity and
"not-a-number" are perfectly valid values in that number system and are not
amounts of money. An infinite budget in particular would not be the hard ceiling
the product definition requires.

One deliberate choice: amounts are allowed to be negative. That looks wrong for
money, and it is there for a reason. The rule for deciding whether to spend more
works out how much a stronger attempt would improve the chance of success — and
if the answer is "it wouldn't", that number is zero or below. The task
specification requires that case to fall naturally out of the arithmetic rather
than be caught by a special rule, so negatives must be representable.

Amounts also keep their precision below a penny. Buying intelligence costs
fractions of a cent at a time, and rounding those away for display would hide
what was actually spent.

### A task, whole

A task is the five things the product definition says it is: **what to do, how
much may be spent, what success is worth, what must not be done, and how success
will be measured.** A task missing any of them is refused.

Two of those are easy to confuse, and the code deliberately keeps them apart:

- **Budget** is the most that may be spent. A ceiling.
- **Task value** is what getting it done is worth. The thing spending is weighed
  against.

Neither is calculated from the other. A budget alone answers *can I afford this?*
Only value answers *is it worth buying?* Take value away and Radhanite becomes a
spending limit rather than an economic decision, so the code refuses a task that
lacks either, and the tests deliberately cover an outcome worth far more than
the budget, an outcome worth less, and the two being equal.

**Checking is deliberately thin, and one round of it was removed.** The first
version refused a budget of zero and a value of zero as invalid. The reviewer
pointed out that nothing in the specification says they are, and that the rule
for deciding whether to spend already handles both correctly — a budget of zero
cannot afford anything, and an outcome worth zero can never be worth buying, so
both cases stop of their own accord. Refusing them up front invented a product
rule nobody authorized, and made the "stop, this is not worth it" outcome
unreachable for those tasks. Zero is now accepted. Only negative amounts are
refused, since those are not quantities either question can weigh.

## 6. What goes into the system

The five inputs, exactly as the product definition states them:

```
Task:              Fix GitHub issue #184
Budget:            $2.00
Task value:        $20.00
Constraints:       no dependency changes
Success condition: tests pass
```

## 7. What the system decides

**Nothing yet.** This pull request adds no decision-making at all.

It refuses only what could never support a decision: an input that is missing
entirely, or an amount below zero. It deliberately **accepts** a budget of zero
and an outcome worth zero, because those are economic situations rather than
invalid ones, and the rule for deciding whether to spend already answers them
correctly — with "stop, this is not worth it", which is a correct outcome and
must remain reachable.

## 8. What comes out

Nothing. These are things to be held and passed around, not run.

## 9. How it can fail

- **A wrong amount could still be typed in.** The code guarantees arithmetic is
  exact; it cannot know that `$2.00` was the number you meant.
- **A number that was already inexact before it arrived still gets through.** If
  a caller converts one of the inexact kind of numbers themselves and hands over
  the result, its history cannot be recovered. This is tested and recorded rather
  than hidden.
- **A task could be accepted that is economically hopeless** — a budget far too
  small for the work, or an outcome worth nothing. That is not rejected here,
  deliberately: it is the spending rule's job to notice and stop, and stopping is
  a correct outcome.
- **Precision is kept, not enforced elsewhere.** Nothing rounds amounts to whole
  cents, because sub-penny costs are real. Display was itself a defect once —
  the printed amount could be rounded by unrelated settings — and now runs under
  the same exact rules as the arithmetic. Any *other* place that formats an
  amount could still round it badly.

## 10. Tests run, and their results

```
$ python --version
Python 3.12.13

$ python -m unittest discover
....................................................
Ran 52 tests in 0.005s
OK
```

49 of those tests are new. Notable ones:

- `0.1 + 0.2` equals exactly `0.3`, and subtracting ten cents from a dollar ten
  times lands on exactly zero rather than drifting.
- A sum that the ordinary settings would round is computed exactly, and changing
  those settings from outside cannot alter the answer — for arithmetic,
  negation, and for the printed form of an amount.
- Printing an amount cannot be made to round, and cannot be made to fail, by
  settings changed elsewhere in the program.
- An operation that genuinely could not be represented exactly raises an error
  rather than returning an approximation.
- Infinity and "not-a-number" are refused at creation.
- Creating money from the inexact kind of number is refused, including the
  disguised case where a true/false value is used as a number.
- The worked example from the task specification — a thirty-percentage-point
  improvement on a $20.00 outcome — computes to exactly $6.00, and the
  no-improvement case computes to exactly zero.
- A task is refused when any of its five inputs is missing, including the one
  that can legitimately be empty. That test was checked by deliberately
  reintroducing the defect and confirming it fails.
- The examples written into the code's own documentation are executed as tests,
  so they cannot quietly become wrong.

## 11. Assumptions made

- That exactness matters more than convenience, so the inexact number type is
  refused outright, and an operation that would round stops the program rather
  than returning an approximation.
- That the success condition is recorded as a written statement for now. Judging
  it comes later, in the part of the system that evaluates outcomes.
- That a task with a hopeless budget — including one of exactly zero — should be
  accepted and then stopped on economic grounds, rather than rejected up front.
- That all five inputs must be supplied explicitly, so a task with nothing
  forbidden says so rather than leaving the field out.

## 12. Known limitations

- Nothing here decides anything; these are only the building blocks.
- Amounts are US dollars only. TASK-001 §6.6 fixes that for now, and they are
  internal accounting numbers rather than any real currency.
- A number that was already inexact before reaching this code cannot be
  detected.
- There is no running-balance type yet. When one is built, it will have to
  refuse to go below zero at that boundary, because the money type deliberately
  permits negatives and will not catch it.

## 13. Functionality explicitly left out of scope

No strategy selection, no execution, no evaluation, no spending decision, no run
record. Nothing excluded by TASK-001 §3 appears: no model APIs, no wallets, no
tokens, no interface, no learning. **The project still depends on nothing but
Python itself.**

## 14. Deferred to future tasks

The rule for deciding whether to spend more, the strategies, the simulator, the
loop, the run record, and a command to run one task end to end.

## 15. How to explain this to a judge

Radhanite decides whether buying more intelligence is worth the money. Every one
of those decisions is a comparison between two amounts, so this pull request
makes sure the system can hold an amount of money without ever being slightly
wrong about it — because slightly wrong, at the wrong moment, means the wrong
decision with nothing in the record to explain it.

It also fixes what a task is: what to do, how much may be spent, **what success
is worth**, what must not be done, and how success will be measured.

That third one is the unusual part. Most systems know their budget. Almost none
know what the outcome is worth to you — and without that, an agent can only ask
"can I afford this?", never "is this worth buying?". Radhanite keeps the two
apart on purpose, and refuses a task that is missing either.

This pull request was also rejected on its first review, and that is worth
saying. The reviewer found seven problems, including that the money could still
be rounded silently in extreme cases, that it would accept an infinite budget,
and that the code was rejecting a budget of zero on a rule nobody had ever
authorized. All seven were fixed rather than argued with.

---

**This document explains; it does not govern.** The product definition,
architecture document, task specification, and the code and its tests are the
authoritative record. Where this explanation and the repository disagree, the
repository is correct.
