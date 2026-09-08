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
| `tests/test_run.py` | 52 checks on the loop and the record |
| `tests/test_cli.py` | 6 checks on the entry point |
| `docs/RUN_RECORDS.md` | A guide to reading a record, for a non-technical reader |
| `radhanite/__init__.py` | Updated to say the task is complete |
| `.gitignore` | Generated records are not committed |
| `docs/pr_explanations/PR-013_...md` | This document |
| `docs/reviews/PR-013_CODEX_REVIEW.md` | The review prompt, committed before the review |
| `docs/reviews/README.md` | Its row added to the index of reviews |

Eleven files. The test count went from 183 to 241 — 58 new.

This pull request was **rejected three times** and the loop was rebuilt twice.
Thirteen problems in total. Several were mistakes of exactly the kind this
document flagged in advance as possible — decisions the specification did not
force, which turned out to be wrong — and one was a fix that overcorrected into a
different mistake. The record is in `docs/reviews/PR-013_CODEX_REVIEW.md`.

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
1. Direct Attempt (start) — no economic decision: nothing has been judged yet,
   so there is nothing for the spending rule to weigh.
   → nothing worked → Not met.

2. Direct Attempt (escalate) — Escalate: raising the chance from 0.35 to 0.55 on
   a $20.00 outcome is worth $4.00, against a cost of $0.08.
   → nothing worked → Not met.

3. Exhaustive Attempt (start) — Escalate: 0.55 to 0.75 is worth $4.00, against a
   cost of $0.50. Passed over: Progressive Escalation offers 0.55 against 0.55
   already achieved.
   → nothing worked → Not met.

4. Progressive Escalation (start) — Stop: it would not improve the chance of
   success at all (still 0.75), so it is worth nothing against a cost of $0.10.
   Also unusable: Exhaustive Attempt (escalate) costs $1.50 and only $1.40
   remains.

STOPPED. spent $0.60 of $2.00, $1.40 unspent
```

Read that again, because it is the whole product. It bought two cheap attempts.
It **passed over** one that would not have improved anything, while a better
option remained. It bought that better one. Then, with nothing left worth
choosing, it asked the spending rule about what remained and was **refused** —
stopping with 70% of the money still there.

Two steps are worth noticing. Step 1 has **no economic decision at all**, on
purpose: the rule decides from a result, and before the first attempt there is
not one. Step 4 is the opposite — nothing was left worth choosing, so the rule
was asked about the first remaining option and refused it. That refusal is what
ended the run, and it is the product working.

Nobody told it to stop. It worked out that stopping was the right answer.

### Two decisions that were wrong, and how

This document originally flagged three decisions the specification did not force
and asked the reviewer to judge them. Two were wrong. Both failed in the same
way: they treated the spending rule as something to consult whenever convenient,
rather than as one step of a sequence with a fixed place and a final answer.

**The rule was being asked before there was anything to decide.** The original
loop weighed even the very first attempt, against a made-up starting chance of
zero. That reads plausibly — surely the first purchase should be justified too —
but the specification sets out an order: choose an approach, do the work, judge
the result, *then* decide whether to spend more. The rule decides **from a
result**, and before the first attempt there is no result. The consequence was
not academic: a low-value job was refused its first attempt entirely, by a rule
that only ever had authority over *additional* spending.

The first attempt is now simply chosen and made. The rule speaks once there is
something for it to speak about.

**"Stop" did not stop.** The original loop treated a refusal as "skip this one
and look at something else". A run could be told to stop and then carry on to
succeed. That quietly demoted the rule's only refusal into a suggestion — and it
is the refusal that the entire product is *for*.

The fix came from the reviewer, and is better than a patch. The loop now decides
**what to do next** before asking whether to do it: it picks the first option
that is affordable and actually improves on what has already been achieved.
Skipping something that offers no improvement is a matter of *choosing*, not of
economics. So the rule is only ever asked about an option genuinely worth
considering — and when it says stop, the run stops. Always.

The third decision — that choosing a dearer approach is the same economic
question as spending more on the current one — was accepted.

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

Every run writes a file. That was not true when this was first submitted — the
record was built in memory and only saved if the caller happened to ask, which
meant most runs left no trace at all while this document claimed otherwise.
Saving it is now part of running.

The file lists every step, including the ones where nothing was bought, and each
records **why that option was chosen** as well as the numbers behind the money
decision. The original recorded only the second of those, so a reader could
recheck the economics but could not see how the option had been arrived at, or
what had been passed over to reach it.

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
- **The rule for choosing what to do next is a choice, not a consequence.**
  Taking the first affordable option that improves on what has been achieved is
  simple and inspectable, and it is not the only defensible rule. A cleverer one
  might spend better.
- **Skipping is invisible to the money rule.** An option passed over during
  choosing never reaches the spending rule at all. That is deliberate — it is
  what lets a refusal be final — but it means the choosing rule now carries
  weight it did not before, and a bad choosing rule would not be caught by the
  economics.
- **Stopping early could be the wrong call** in a case nobody has thought of.
  Simple rules have edges.
- **The demonstration is a fixed scenario.** It shows the machinery working, not
  that it would work on real jobs.

## 10. Tests run, and their results

```
$ python --version
Python 3.12.13

$ python -m unittest discover
Ran 241 tests in 0.101s
OK
```

58 tests are new: 52 on the loop and record, 6 on the entry point. The ones that
matter most:

- The first attempt carries no money decision, and every later one does.
- A low-value job still gets its first attempt, and is then refused further
  spending — the corrected behaviour, where the original refused it outright.
- A refusal ends the run. Nothing is bought after one, checked for both reasons
  a refusal can happen — and both reasons are produced by the spending rule
  itself rather than by the step that chooses what to consider.
- A decision is absent **exactly when nothing has been judged yet**, checked
  across six scenarios and verified by deliberately issuing one too early.
- A list of options that changes while being read cannot desynchronise a run.
- Eight runs into one directory leave eight records; a claimed name is never
  handed out twice.
- An option offering no improvement is passed over while *choosing*, and the
  record names it as passed over.
- Spending never exceeds the budget, across 32 combinations of scenario and
  budget, with the remainder never negative and always adding back up.
- Every decision recomputed from the record — from the objects, and again from
  the saved file.
- A saved record says which condition failed, an approved one says none failed,
  and the two kinds of refusal are distinguishable. Verified by deleting that
  field and confirming four tests fail; before the review, deleting it broke
  nothing.
- A run that could not afford anything still records why nothing happened.
- The same scenario produces the same run, twenty times over.
- The demonstration produces **both** outcomes.

## 11. Assumptions made

- That choosing a dearer approach is the same economic question as spending more
  on the current one, so the same rule serves. This was the one of three flagged
  decisions that survived review.
- That skipping an option which offers no improvement belongs to *choosing*
  rather than to the money rule — which is what allows a refusal to be final.
- That the first attempt is not the money rule's business, because the rule
  decides from a result and there is not one yet.
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
**passes over** an option that would not have improved anything, buys a better
one for fifty cents, fails once more, and then stops — with $1.40 of $2.00 still
unspent — because what remained cost more than it was worth.

That refusal is the product. Any agent can spend your money. This one can tell
you, in a sentence, why it declined to spend more: *"only $1.40 remains, which
cannot cover the $1.50 this would cost."*

And every one of those decisions can be checked. The record keeps the numbers
each was made from, so you can redo the arithmetic yourself rather than taking
its word for it.

It is worth adding that this pull request was rejected the first time. The loop
asked the money question before there was anything to answer it about, and
treated the answer "stop" as a suggestion rather than an instruction — so a run
could be told to stop and carry on anyway. An independent review caught both,
and the fix for the second came from the reviewer rather than from us. The
version described here is the corrected one.

The work being simulated is not a hedge. It is the point of this stage: you
cannot prove reasoning about uncertain outcomes is *correct* while the outcomes
themselves vary. Fix what happens, and every decision becomes checkable. Real
work comes next, and is deliberately not built yet.

---

**This document explains; it does not govern.** The product definition,
architecture document, task specification, and the code and its tests are the
authoritative record. Where this explanation and the repository disagree, the
repository is correct.
