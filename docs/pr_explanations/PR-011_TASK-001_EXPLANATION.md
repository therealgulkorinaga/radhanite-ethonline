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
| `tests/test_strategy.py` | 29 checks on those |
| `radhanite/_immutable.py` | Exactly what "unchangeable" does and does not mean here |
| `radhanite/money.py` | Amounts can be laid out in columns; truncating formats refused |
| `tests/test_money.py` | 7 added for that |
| `radhanite/probability.py` | Hardened so its value cannot be rewritten from outside |
| `radhanite/task.py` | Hardened the same way |
| `radhanite/escalation.py` | Hardened the same way |
| `radhanite/__init__.py` | Updated to say what is now built |
| `docs/pr_explanations/PR-011_...md` | This document |
| `docs/reviews/PR-011_CODEX_REVIEW.md` | The review prompt and findings |
| `docs/reviews/README.md` | Its row added to the index of reviews |

Twelve files. The test count went from 103 to 139 — 36 new.

This pull request was **rejected twice**. The first review found six problems;
the second found that four of the six fixes were not good enough, and added one
more. Eleven findings in total, all now fixed, and the sections below describe
the corrected state. The record is in `docs/reviews/PR-011_CODEX_REVIEW.md`.

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

A test writes all twelve figures out longhand and checks each one. That alone
was too weak: comparing values cannot tell a *declared* 0.35 from a *calculated*
0.30 + 0.05, since both come out equal, and the reviewer proved the test passed
after making exactly that substitution.

A second test now reads the source code itself. The first version of that was
also defeated — it checked only what was handed to the money and probability
types, so a helper could quietly supply the real value while a decoy literal sat
beside it. It now permits *nothing* in that part of the source except the lists
themselves, direct calls to the three value types, and plain text. Arithmetic, a
lookup by name, a helper call, or a subscript all fail. All three of the
reviewer's substitutions were replayed against it and all three now fail.

The figures also could not be relied on to *stay* declared. The objects holding
them were supposedly unchangeable and were not — the reviewer altered a
strategy's price from outside and changed which strategy got chosen. Two rounds
of fixing later, here is the honest position, because the first two attempts at
stating it were both wrong:

**Prevented:** ordinary assignment; writing through the object's internal
dictionary, which no longer exists; and replacing the whole object's contents at
once.

**Not prevented, and not preventable:** a caller who deliberately reaches past
the normal mechanism using the language's own low-level tools. Python offers no
way to stop that for an object that holds named values, and the `ctypes` module
can rewrite the memory of *anything*, including things the language calls
immutable.

So the claim is bounded: **these figures cannot be changed by accident or by any
ordinary route, and are not defended against somebody determined to change
them.** What the task actually requires is that Radhanite itself never
calculates or updates them, and that is enforced by reading the source code, not
by armouring the objects.

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
choices at each of five budgets, all identical, and choices unaffected by other
choices made in between.

Two holes in that were found on review.

**An unordered collection was accepted.** Handed a set of strategies rather than
a list, the code would happily work through it in whatever order the language
felt like that day — and the reviewer got three different answers from the same
budget. A collection with no order cannot produce the same answer twice, so one
is now refused outright rather than turned into an economic decision that
depends on the weather.

**The staleness check checked nothing.** The test that claimed the chooser
remembers nothing between calls only looked at the list of arguments it takes —
so the reviewer added a hidden running log and the test carried on passing. The
first repair was still too shallow, and the reviewer defeated it four more ways.

It now looks everywhere a test can reach: values the module holds, anything
attached to the function, what the function closes over, its default arguments,
whether it has been wrapped in a cache, and anything stored on the types the
module defines. All four hiding places now fail it.

One limit remains and is stated rather than glossed: state hidden inside a
*different* module cannot be seen from here.

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

### A small fix, and the bigger one hiding behind it

Amounts of money could be printed but not laid out — putting one in a column of
fixed width failed outright. This surfaced while printing budgets against chosen
strategies, which is precisely where it would have surfaced later, in output
nobody had tested.

The fix was too permissive, and review caught it. It accepted any instruction at
all, including ones that **shortened the number**: asked to show `$123.456` in a
narrow form, it produced `$1` — silently, a different amount entirely. An amount
that quietly becomes another amount defeats the whole point of holding money
exactly. Instructions that would shorten a value are now refused; laying one out
in a column still works.

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
- **Guarantees have to be closed deliberately.** Three of the six problems found
  on review were ways around a promise the code appeared to make. Each is shut
  now, and each was invisible until somebody tried it.

## 10. Tests run, and their results

```
$ python --version
Python 3.12.13

$ python -m unittest discover
Ran 139 tests in 0.012s
OK
```

36 tests are new: 29 on strategies and selection, 7 on displaying amounts. The
ones that matter most:

- All twelve declared figures, each asserted individually — **and** the source
  itself read to confirm each is written as a literal rather than calculated.
- A declared strategy cannot be altered from outside, by any route.
- An unordered collection of strategies is refused.
- A display instruction that would shorten an amount is refused.
- Reversing the list changes the choice — proving the order is the policy.
- Exactly affordable counts as affordable; a penny short does not.
- Fifty repeated choices at each of five budgets give one answer.
- Nothing accumulates between calls, checked by taking a full picture of what
  the module and the function hold rather than by reading the argument list.

Each of the last several was confirmed by deliberately reintroducing the fault
and watching the test fail — including all seven of the ways the reviewer
defeated the earlier versions of these tests.

One correction to how that checking was done. An early run reported the hidden
running log as *undetected*. That was a stale compiled-code cache rather than a
passing test: re-run in isolation with caches cleared, it failed as it should.
The first result was wrong, and it is recorded here rather than quietly dropped,
because a verification method that can report a false pass is worth knowing
about.

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

This pull request was rejected on its first review, and it is worth saying why.
Three of the six problems were promises the code appeared to keep and did not: a
strategy's price could be changed from outside despite being declared fixed, an
unordered list of strategies would produce a different answer on different days,
and asking to display an amount narrowly could silently turn `$123.456` into
`$1`. None was visible by reading the code. All three were found by somebody
trying to break it.

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
