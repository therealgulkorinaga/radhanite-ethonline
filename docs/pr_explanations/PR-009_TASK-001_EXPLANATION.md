# PR-009 — The decision the whole product exists to make

**Pull request:** #9
**Authority:** TASK-001 (authorized task)
**Author:** Claude Code, under human product owner authorization

---

## 1. Purpose of this PR

To build the rule that decides **whether buying more intelligence is worth the
money**.

Everything before this was groundwork. This is the thing Radhanite is for.

## 2. What changed

| File | What it is |
|---|---|
| `radhanite/escalation.py` | The rule itself |
| `radhanite/probability.py` | A chance of success, held exactly |
| `radhanite/_exactness.py` | The shared arithmetic settings both use |
| `radhanite/money.py` | Now shares those settings; tidier display |
| `radhanite/__init__.py` | Updated to say what is now built |
| `tests/test_escalation.py` | 31 checks on the rule |
| `tests/test_probability.py` | 13 checks on probabilities |
| `tests/test_money.py` | 2 added for the tidier display |
| `docs/pr_explanations/PR-009_...md` | This document |
| `docs/reviews/PR-009_CODEX_REVIEW.md` | The review prompt, committed before the review |
| `docs/reviews/README.md` | Its row added to the index of reviews |

Eleven files, and the test count went from 57 to 103.

This pull request was **approved with corrections** on review. Three problems
were found — none in the rule itself, all in what the documentation and tests
claimed. The record is in `docs/reviews/PR-009_CODEX_REVIEW.md`.

## 3. Why the change was needed

An agent that can spend money needs an answer to one question, over and over:
*is it worth spending more?*

Without one, an agent either stops too early and fails work it could have
finished, or keeps paying long after the work stopped being worth the money.
Both are invisible until the bill arrives.

## 4. How this worked before

Radhanite could hold an amount of money and describe a piece of work. It could
not decide anything at all.

## 5. How it works after

Given five things — how likely success is now, how likely it would be after
spending more, what the outcome is worth, what spending more costs, and how much
budget is left — the rule answers **escalate** or **stop**, and explains why in
a sentence.

The arithmetic is simple, and that is deliberate:

> Work out how much a stronger attempt would improve the chance of success.
> Multiply that improvement by what the outcome is worth — that is what the
> improvement is worth in money. Spend only if that exceeds what the attempt
> costs, **and** the remaining budget can cover it.

The specification's own example, which the code reproduces exactly:

```
The outcome is worth        $20.00
Success is currently        50% likely
Spending more would make it 80% likely
That attempt would cost     $0.50

The improvement is 30 percentage points, worth 30% of $20.00 = $6.00
$6.00 is more than $0.50, and the budget can cover $0.50

Decision: ESCALATE
```

Spend fifty cents to gain six dollars of expected value.

### Four things the rule must never do

Each of these is enforced by a test, not by good intentions.

**It must ignore money already spent.** The rule weighs the *next* purchase
against what *that purchase* gains. What has been spent so far is gone whatever
it decides, and letting it count is the "we've come this far" fallacy that keeps
people paying for lost causes. The function is not even told the amount, and a
test checks it stays that way.

**A tie must not spend.** If the improvement is worth exactly what it costs,
the rule stops. Breaking even is not a reason to spend money.

**No improvement must stop by itself.** If a stronger attempt would not raise
the chance of success, its value is zero, and zero is not more than a cost. If
the attempt would make things *worse*, the value is below zero. Neither needs a
special rule; both fall out of the arithmetic, which is what the specification
requires.

**The budget and the value must never stand in for each other.** A vast budget
cannot make a worthless attempt worth buying, and a hugely valuable outcome
cannot be bought with money that is not there. They answer different questions,
and both tests exist to catch an implementation that confused them — which would
still run, and would have destroyed the whole idea.

### Every decision explains itself

The product definition requires that any decision can be inspected afterwards.
Recording *that* a decision happened is not the same as recording *why*, so each
decision carries the numbers that produced it and a sentence a person can check:

```
Escalate: spending $0.50 buys more than it costs — raising the chance of success
from 0.50 to 0.80 on a $20.00 outcome is worth $6.00, against a cost of $0.50,
with $2.00 of budget remaining.

Stop: it would not improve the chance of success at all (still 0.50), so it is
worth nothing against a cost of $0.50.

Stop: only $0.20 remains, which cannot cover the $0.50 this would cost.
```

A test re-derives the entire verdict — not merely the arithmetic — using only
what the decision recorded, applying both of the rule's conditions
independently and comparing the conclusion. A decision that could not be
reconstructed from its own record would fail that test.

## 6. What goes into the system

Five quantities: the current chance of success, the chance after spending more,
what the outcome is worth, what the next attempt costs, and the budget
remaining.

They must be passed **by name**. Five numbers of two kinds, several
interchangeable in shape and none in meaning, is exactly the situation where
passing them in order silently swaps two and produces a confident wrong answer.

## 7. What the system decides

Escalate, or stop. That is the entire decision.

Both conditions are always checked, never abandoned as soon as one fails, so a
stop can report *everything* that was wrong rather than only the first thing.

## 8. What comes out

A decision carrying: the verdict, a plain-English reason, what the improvement
was worth in money, all five inputs, and which conditions failed. It cannot be
altered afterwards.

## 9. How it can fail

- **The chances of success are declared, not measured.** They are fixed numbers
  attached to strategies, chosen by a person. If they are wrong, the rule will
  make well-reasoned decisions from bad premises. Measuring them properly is
  future work and deliberately not authorized.
- **The rule cannot see a run's history.** By design — but it means it cannot
  notice that five attempts in a row have failed. Whatever drives the loop must
  handle that.
- **A budget already overspent raises rather than deciding.** That state should
  be impossible; the rule refuses to produce a confident answer from a broken
  one, which surfaces the fault instead of hiding it.
- **The explanations are prose.** They can be read by a person, but not
  reliably parsed by a machine.
- **The chances are exact, but the arithmetic is only as good as its inputs.**
  Review generated 26,136 input combinations and found the rule matched the
  specification in every one; that establishes the rule is implemented
  correctly, not that the numbers fed to it are right.

## 10. Tests run, and their results

```
$ python --version
Python 3.12.13

$ python -m unittest discover
Ran 103 tests in 0.006s
OK
```

46 tests are new. The ones that matter most:

- The specification's worked example, reproduced exactly, down to the `$6.00`.
- The tie: an improvement worth exactly its cost stops.
- One cent either side of the tie decides opposite ways — $5.99 escalates,
  $6.01 stops, against a gain of exactly $6.00.
- No improvement stops; a worsening attempt stops.
- The budget being exactly enough is allowed; a penny short is not.
- A vast budget cannot rescue a worthless attempt, and a valuable outcome cannot
  be bought without budget.
- The rule's own list of inputs is asserted, so money already spent cannot be
  added later without a test failing.
- The whole verdict is re-derived from only what a decision recorded — both
  conditions applied independently, across six cases including each single
  failure and both failing together. Verified by mutation: forcing the rule to
  always escalate makes 18 tests fail.

Three tests failed when first written. Two were my error — they set a cost
higher than the budget, so both conditions failed rather than the one under
test. The third was a documentation example still showing the old display. All
three were faults in the tests, not the rule.

## 11. Assumptions made

- That the rule should be a single function that decides and explains, holding
  no state of its own.
- That refusing to decide on an impossible input — a budget already overspent —
  is better than answering confidently from a broken state.
- That both conditions should always be evaluated, so a stop can report every
  reason rather than the first.
- That trailing zeros in a displayed amount are noise; `$6.0000` tells a reader
  nothing `$6.00` does not.

## 12. Known limitations

- The rule decides one step. Nothing yet drives it repeatedly, tracks the
  budget, or records a run.
- Chances of success are fixed declared numbers, not learned from anything.
- There is still no running-balance type. When one is built it must refuse to
  go below zero itself; the money type permits negatives by design and will not
  catch it.

## 13. Functionality explicitly left out of scope

No strategies, no execution, no evaluation of outcomes, no loop, no run record,
no command to run a task. Nothing excluded by TASK-001 §3 appears: no model
APIs, no wallets, no tokens, no interface, and no learning of any kind. **The
project still depends on nothing but Python itself.**

## 14. Deferred to future tasks

The strategy fixtures, deterministic selection between them, the simulator,
outcome evaluation, the loop that ties them together, the run record, and a
command that runs one task end to end.

## 15. How to explain this to a judge

This is the part worth stopping on.

Every AI agent can spend money. Almost none can tell you whether spending more
was worth it. Radhanite answers that with one rule: work out how much a stronger
attempt would improve the chance of success, multiply by what success is worth,
and spend only if that exceeds the cost and the budget can cover it.

The specification's example: an outcome worth $20, currently 50% likely, 80%
likely after an attempt costing 50 cents. The improvement is worth $6. Spend the
50 cents. That is a real economic decision, made without a human present, and it
is now in the code with a test proving it.

The interesting part is what the rule refuses to do. It ignores money already
spent, so it never throws good money after bad. It refuses to spend on a
break-even. It stops on its own when a stronger attempt would not actually help
— not because anyone wrote a rule saying "give up", but because the arithmetic
says the gain is zero and zero does not beat a cost.

**Stopping is a correct answer here, not a failure.** An agent that declines to
keep spending on something not worth it has done its job.

---

**This document explains; it does not govern.** The product definition,
architecture document, task specification, and the code and its tests are the
authoritative record. Where this explanation and the repository disagree, the
repository is correct.
