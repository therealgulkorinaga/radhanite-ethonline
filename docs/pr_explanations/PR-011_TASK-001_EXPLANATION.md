# PR-011 — The ways of attempting a task, and how one is chosen

**Pull request:** #11
**Authority:** TASK-001 (authorized task)
**Author:** Claude Code, under human product owner authorization

---

## 1. Purpose of this PR

To give Radhanite something to actually choose between, and a rule for choosing
that always makes the same choice given the same situation.

## 2. What changed

| File | What it is |
|---|---|
| `radhanite/strategy.py` | The ways of attempting a task, and the rule for picking one |
| `tests/test_strategy.py` | 24 checks on those |
| `radhanite/money.py` | Amounts can now be laid out in columns, not only printed |
| `tests/test_money.py` | 3 added for that |
| `radhanite/__init__.py` | Updated to say what is now built |
| `docs/pr_explanations/PR-011_...md` | This document |
| `docs/reviews/PR-011_CODEX_REVIEW.md` | The review prompt, committed before the review |

Seven files. The test count went from 106 to 130.

## 3. Why the change was needed

The rule for deciding whether to spend more is built, but it had nothing to
decide *about*. It needs to be told what an attempt would cost and how much it
would improve the chance of success. Those figures have to come from somewhere,
and something has to pick which way of working to try first.

## 4. How this worked before

Radhanite could hold money, describe a task, and weigh one spending decision. It
had no notion of *how* a task might be attempted.

## 5. How it works after

### A strategy

A strategy is one way of going about a task. Each declares four things: what a
first attempt costs and how likely it is to succeed, and what a stronger second
attempt costs and how likely *that* is to succeed.

Three are declared, cheapest first:

| Strategy | First attempt | Chance | Escalates to | Chance |
|---|---|---|---|---|
| Direct Attempt | $0.02 | 35% | $0.08 | 55% |
| Progressive Escalation | $0.10 | 55% | $0.40 | 85% |
| Exhaustive Attempt | $0.50 | 75% | $1.50 | 92% |

**These numbers are made up, on purpose, and that is stated everywhere they
appear.** They are not measurements of anything. They exist so the economic
reasoning can be exercised and checked. A real system would learn them from
experience — that is explicitly future work and explicitly not permitted here,
because a system that learned its own numbers could not be tested for making the
same decision twice.

A test writes all twelve figures out longhand and checks each one. If anything
ever starts *calculating* these rather than *declaring* them, that test fails.

### Choosing one

The rule is deliberately the plainest thing that could work:

> Take the first strategy on the list that the remaining budget can afford.

Because the list runs cheapest-first, that means starting cheap. If nothing on
the list is affordable, it says so, and the answer is to stop — not a failure,
just the budget running out before anything is attempted.

The important property is that **the order of the list is the policy**. Nothing
is weighed or judged at the moment of choosing; the decision was made when
somebody wrote the list down, and anybody can read it. A test reverses the list
and shows the choice changes, which proves the order really is what decides.

That matters because the task specification demands the same situation always
produce the same choice. That is tested rather than asserted: fifty repeated
choices at each of five budgets, all identical; choices unaffected by other
choices made in between; and the function checked to confirm it remembers
nothing between calls.

### Two things deliberately not done

**A strategy is allowed to have a useless escalation** — one that would not
improve the chance of success, or would make it worse. That looks like something
to forbid. It is not: it is a real economic situation, and the spending rule
already answers it correctly by refusing to pay. Forbidding it here would make
that correct answer unreachable, which is a mistake this project has already
made once and had caught in review.

**Choosing does not look at the task.** Nothing in the rule uses it, and
accepting something only to ignore it is how unused machinery accumulates. It
can be added when a rule actually needs it.

### An unrelated small fix

Amounts of money could be printed but not laid out — putting one in a column of
fixed width failed outright. This surfaced while printing budgets against
chosen strategies, which is precisely where it would have surfaced later, in
output nobody had tested. Fixed.

## 6. What goes into the system

For a strategy: a name, two costs, and two chances of success. For choosing: the
list of strategies and the money remaining.

## 7. What the system decides

Which way of attempting the task to try, or that none can be afforded.

This is **not** the economic decision — nothing here weighs value against cost.
It only answers "what can we afford to try?", leaving "is it worth it?" to the
rule built previously.

## 8. What comes out

A strategy, or nothing.

## 9. How it can fail

- **The declared numbers could be wrong.** They are invented. Every decision
  downstream is only as good as they are, and nothing here can tell.
- **The choosing rule is crude.** It picks the cheapest affordable option, which
  is not always the wisest — a cheap attempt with a poor chance may waste money
  a dearer one would have earned back. That is a decision for the specification
  to revisit, not for this code to improvise.
- **Nothing checks that a strategy is sensible.** A strategy that costs a
  fortune and never works is accepted; the spending rule declines to buy it.

## 10. Tests run, and their results

```
$ python --version
Python 3.12.13

$ python -m unittest discover
Ran 130 tests in 0.008s
OK
```

27 tests are new: 24 on strategies and selection, 3 on laying out amounts. The
ones that matter most:

- All twelve declared figures, each asserted individually.
- The list cannot be added to after the fact, and names do not repeat, since a
  run record refers to a strategy by name.
- Reversing the list changes the choice — proving the order is the policy.
- Exactly affordable counts as affordable; a penny short does not.
- Fifty repeated choices at each of five budgets give one answer.
- The chooser's own signature is asserted, so it cannot quietly gain a memory.

## 11. Assumptions made

- That the simplest defensible choosing rule is the right one while the point is
  to prove the economics, and that a cleverer one would be inventing policy
  nobody authorized.
- That the order of the list is a legitimate way to express policy, because it
  is visible and fixed rather than computed.
- That a strategy with a pointless escalation should be allowed and then
  declined on economic grounds, rather than rejected as invalid.

## 12. Known limitations

- The figures are invented.
- Choosing considers only affordability, not whether a dearer strategy would be
  a better buy.
- Nothing yet attempts anything, evaluates anything, or records anything.

## 13. Functionality explicitly left out of scope

No execution, no evaluation of outcomes, no loop, no run record, no command to
run a task. Nothing excluded by TASK-001 §3 appears: no model APIs, no wallets,
no tokens, no interface, and **no learning of any kind** — the chances of
success are declared and stay declared. **The project still depends on nothing
but Python itself.**

## 14. Deferred to future tasks

The simulator, evaluating outcomes against the success condition, the loop that
drives everything, the run record, and a command that runs one task end to end.

## 15. How to explain this to a judge

Radhanite now has a menu. Three ways to attempt a piece of work, each with a
price and a stated chance of succeeding, and a dearer version of itself it can
escalate to.

Choosing is deliberately boring: take the cheapest one you can afford. All the
intelligence lives in the *other* rule — the one that decides whether escalating
is worth the money — and keeping the choice dumb is what makes that rule
testable, because the same situation always produces the same choice.

The honest caveat, which is stated in the code, the commit and this document:
**those chances of success are invented.** They are there so the economics can
be exercised. A real system would learn them from its own history, and that is
deliberately not built here, because a system that learns its own numbers cannot
be tested for deciding the same way twice — and proving the decision is sound is
the whole point of this stage.

---

**This document explains; it does not govern.** The product definition,
architecture document, task specification, and the code and its tests are the
authoritative record. Where this explanation and the repository disagree, the
repository is correct.
