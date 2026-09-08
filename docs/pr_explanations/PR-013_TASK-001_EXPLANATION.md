# PR-013 — Putting it together, and finishing TASK-001

**Pull request:** #13
**Authority:** TASK-001 (authorized task)
**Author:** Claude Code, under human product owner authorization

---

## 1. Purpose of this PR

To join the pieces into something that actually runs a task from start to
finish, keep an honest record of what it did, and provide a way to watch it
happen. **This completes the first authorized piece of work.**

## 2. What changed

| File | What it is |
|---|---|
| `radhanite/run.py` | The loop, and the record of what it did |
| `radhanite/cli.py` | A way to run it and see the result |
| `radhanite/__main__.py` | Lets `python -m radhanite` work |
| `tests/test_run.py` | 27 checks on the loop and the record |
| `tests/test_cli.py` | 6 checks on the entry point |
| `docs/RUN_RECORDS.md` | A guide to reading a record, for a non-technical reader |
| `radhanite/__init__.py` | Updated to say the task is complete |
| `.gitignore` | Generated records are not committed |
| `docs/pr_explanations/PR-013_...md` | This document |
| `docs/reviews/PR-013_CODEX_REVIEW.md` | The review prompt, committed before the review |
| `docs/reviews/README.md` | Its row added to the index of reviews |

Eleven files. The test count went from 183 to 216 — 33 new.

## 3. Why the change was needed

Every part existed and none of them were connected. Radhanite could price a way
of working, decide whether spending was justified, pretend to do the work, and
judge the result — but nothing carried a task through all of that, kept count of
the money, or wrote down what happened.

## 4. How this worked before

The pieces sat side by side. There was no way to run a task, and nothing
produced a record.

## 5. How it works after

### What actually happens

```
python -m radhanite
```

Three scenarios run against the same task — fix an issue, $2.00 to spend, worth
$20.00 if finished, done when the tests pass. Here is the one that matters most:

```
1. Direct Attempt (start) — Escalate: spending $0.02 buys more than it costs —
   raising the chance of success from 0 to 0.35 on a $20.00 outcome is worth
   $7.00, against a cost of $0.02, with $2.00 of budget remaining.
   → nothing worked → Not met.

2. Direct Attempt (escalate) — Escalate: spending $0.08 ... is worth $4.00,
   against a cost of $0.08 → it builds, tests still red → Not met.

3. Progressive Escalation (start) — Stop: it would not improve the chance of
   success at all (still 0.55), so it is worth nothing against a cost of $0.10.

4. Exhaustive Attempt (start) — Escalate: ... 0.55 to 0.75 ... is worth $4.00,
   against a cost of $0.50 → nothing worked → Not met.

5. Exhaustive Attempt (escalate) — Stop: only $1.40 remains, which cannot cover
   the $1.50 this would cost.

STOPPED: none of what remains is worth buying, and $1.40 is unspent.
spent $0.60 of $2.00
```

Read that again, because it is the whole product. It bought two cheap attempts.
It **refused** a third that would not have improved anything. It bought a dearer
one that would. Then it **stopped, with 70% of the money still there**, because
what was left could not be afforded.

Nobody told it to stop. It worked out that stopping was the right answer.

### Three decisions that were not forced

The specification does not settle these. Each was chosen, and each is flagged
for the reviewer, because deciding something the specification did not say is
how this project has gone wrong before.

**Every purchase is weighed, including the first.** There is no free opening
attempt. Buying one lifts the chance of success from nothing to whatever that
way of working offers, which is exactly the question the spending rule answers.
A job worth a penny does not get a two-penny attempt merely because it is the
first one, and a test covers precisely that: a task worth $0.05 buys **nothing
at all**.

**Choosing a dearer approach is weighed the same way.** "Is the next, more
expensive approach worth buying?" is the same question as "is spending more on
this one worth it?" — how much would it improve the chances, and is that worth
more than it costs. The rule already agreed for one is used unchanged for the
other, rather than inventing a second.

**A refusal ends an approach, not the run.** The first version of this stopped
the moment anything was refused. That was wrong, and running it showed why: it
walked away from a job it could still have finished, with $1.90 of $2.00
unspent, because the *cheapest* remaining option happened to be a poor buy. A
dearer one was worth buying and was never considered. Each purchase is judged on
its own merits.

### The money cannot be overspent

Spending goes through a running balance that refuses to go below zero. That is
not decoration: the money type deliberately permits negative amounts because the
value arithmetic needs them, so it cannot notice an overspend. An earlier review
pointed out that a running balance would have to catch it, and this is that
balance.

The ceiling is checked across 32 combinations of scenario and budget — including
budgets of zero, budgets that fall between two prices, and budgets far larger
than anything could spend — confirming each time that spending never exceeds the
budget, the remainder never goes negative, and the two always add back up.

### The record

Every run writes a file listing every purchase it considered — including the
ones it refused, and why. Each records the numbers the decision was made from.

**Any decision can be checked by hand.** Subtract the two probabilities,
multiply by what the job is worth, compare against the cost. Every number needed
is in the file. A test does exactly that for every step of a run: first from the
objects, then again from the saved file, confirming the verdict matches.

Amounts are saved as text rather than numbers, so that whoever reads the file
cannot silently convert them into the inexact form the money type exists to
avoid.

`docs/RUN_RECORDS.md` explains all of this for someone who does not program.

## 6. What goes into the system

A task — the job, the budget, what finishing is worth, the constraints, and how
success is measured — together with the available ways of working and a scenario
saying what each attempt achieves.

## 7. What the system decides

Everything the product exists to decide: which approach to buy, whether buying
it is justified, whether the job is finished, and when to stop.

## 8. What comes out

A printed account, and a saved record. A run ends **succeeded** or **stopped**,
and stopped is not a failure — it is the system declining to spend more on
something not worth it, which is the behaviour the whole product is for.

## 9. How it can fail

- **The work is still simulated.** Nothing connects to a real repository or a
  real model. The reasoning is real; the work is not.
- **The chances of success are invented.** Every decision is only as good as
  those figures, and nothing here can tell whether they are right.
- **The three unforced decisions above could be wrong.** They are choices, not
  consequences, and the reviewer is asked about each by name.
- **Stopping early could be the wrong call** in a case nobody has thought of.
  The rule is deliberately simple; simple rules have edges.
- **The demonstration is a fixed scenario.** It shows the machinery working, not
  that it would work on real jobs.

## 10. Tests run, and their results

```
$ python --version
Python 3.12.13

$ python -m unittest discover
Ran 216 tests in 0.036s
OK
```

33 tests are new: 27 on the loop and record, 6 on the entry point. The ones that
matter most:

- Spending never exceeds the budget, across 32 combinations of scenario and
  budget, with the remainder never negative and always adding back up.
- A task worth less than the cheapest attempt buys nothing at all.
- A run stops with money unspent, and that counts as a correct outcome.
- A refusal does not end the run: a dearer approach is still considered, and the
  scenario proving it would have failed under the first version of the loop.
- No approach is ever tried twice.
- Every decision recomputed from the record — from the objects, and again from
  the saved file.
- The same scenario produces the same run, twenty times over.
- The demonstration produces **both** outcomes; a demonstration that only ever
  succeeded would hide the product's actual claim.

## 11. Assumptions made

- That the spending rule applies to every purchase, not only to escalations.
- That choosing a dearer approach is the same economic question, so the same
  rule serves.
- That a refusal ends an approach rather than the run — corrected after watching
  the first version abandon a winnable job with most of the money unspent.
- That saving amounts as text is worth the small awkwardness, because the
  alternative risks a wrong number in the permanent record.

## 12. Known limitations

- The work is simulated and the success figures are invented.
- The loop tries each approach at most once; nothing revisits one.
- The record grows with the number of purchases considered and nothing prunes
  it.
- The entry point runs fixed scenarios; there is no way to describe your own
  from the command line, which is deliberate — the specification asks for a
  developer-facing way to run a task, not an interface.

## 13. Functionality explicitly left out of scope

Nothing excluded by TASK-001 §3 appears: no model APIs, no real execution
against a repository, no wallets, no tokens, no payment, no production
interface, and no learning of any kind. **The project depends on nothing but
Python itself.**

## 14. Deferred to future tasks

Everything beyond TASK-001, all of it unauthorized: real inference, a wallet, a
real budget in real money, a payable service, learning the success figures from
experience, and any interface for people who are not developers.

## 15. How to explain this to a judge

Give Radhanite a job, a budget, what finishing is worth, and a way of telling
whether it is done. It works out which approach to buy, whether buying it is
worth the money, whether the job got finished, and **when to walk away**.

In the demonstration it spends two cents, fails, spends eight more, fails again,
**refuses** an option that would not have helped, buys a better one for fifty
cents, fails once more, and then stops — with $1.40 of $2.00 still unspent —
because what remained cost more than it was worth.

That refusal is the product. Any agent can spend your money. This one can tell
you, in a sentence, why it declined to spend more: *"only $1.40 remains, which
cannot cover the $1.50 this would cost."*

And every one of those decisions can be checked. The record keeps the numbers
each was made from, so you can redo the arithmetic yourself rather than taking
its word for it.

The work being simulated is not a hedge. It is the point of this stage: you
cannot prove reasoning about uncertain outcomes is *correct* while the outcomes
themselves vary. Fix what happens, and every decision becomes checkable. Real
work comes next, and is deliberately not built yet.

---

**This document explains; it does not govern.** The product definition,
architecture document, task specification, and the code and its tests are the
authoritative record. Where this explanation and the repository disagree, the
repository is correct.
