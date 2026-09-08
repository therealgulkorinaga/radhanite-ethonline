# PR-012 — Doing the work, and judging whether it worked

**Pull request:** #12
**Authority:** TASK-001 (authorized task)
**Author:** Claude Code, under human product owner authorization

---

## 1. Purpose of this PR

To give Radhanite something that *attempts* a task, and something that decides
**honestly** whether the attempt succeeded.

## 2. What changed

| File | What it is |
|---|---|
| `radhanite/execution.py` | The stand-in for doing the work |
| `radhanite/evaluation.py` | Judging whether the work met the requirement |
| `tests/test_execution.py` | 16 checks on the first |
| `tests/test_evaluation.py` | 14 checks on the second |
| `radhanite/__init__.py` | Updated to say what is now built |
| `docs/pr_explanations/PR-012_...md` | This document |
| `docs/reviews/PR-012_CODEX_REVIEW.md` | The review prompt, committed before the review |
| `docs/reviews/README.md` | Its row added to the index of reviews |

Eight files. The test count went from 139 to 169 — 30 new.

## 3. Why the change was needed

Radhanite could describe a task, price three ways of attempting it, pick one,
and weigh whether spending more was worth it. It could not attempt anything, and
had no idea whether anything had worked.

## 4. How this worked before

Nothing executed and nothing was judged.

## 5. How it works after

### Attempting the work

The thing that "does the work" does no work at all. It is **told in advance what
happens** — succeed, fail, or get part of the way — and reports that, charging
the price the chosen strategy declared.

That sounds like cheating, and it is deliberate. The task specification requires
it. The purpose of this stage is to prove the *economic reasoning* is right, and
you cannot test reasoning about uncertain outcomes while the outcomes are
themselves uncertain. Fixing what happens is what makes the money decisions
checkable.

The point is easy to get wrong in a specific way, so there is a test for it: a
strategy declared to succeed **zero percent** of the time is run twenty times
against a script saying "success", and succeeds every time. Nothing is being
rolled or sampled. If it were, the same run would give different answers on
different days and none of the economic decisions could be checked at all.

Asking for more attempts than the scenario described is treated as a fault
rather than an outcome — it means whatever is driving the work asked for
something that was never described, and inventing an answer there would be worse
than stopping.

### Judging the result

Two verdicts: the requirement was met, or it was not. There is deliberately no
third, and a test asserts there are exactly two so a third cannot be quietly
added.

**The important part is what happens to partial progress.** An attempt that got
part of the way is **not met**. That is the single most dangerous mistake
available in this whole system: if "made progress" were treated as success,
Radhanite would conclude the job was finished, stop spending, and report an
outcome that never happened. The specification forbids it in those words, and
four separate tests hold the line.

Partial progress and outright failure share a verdict but not a record. Both are
"not met", and the record keeps which actually happened, with a different
sentence for each, so nothing is lost.

A task with no way of measuring success is refused outright. Without one there
is nothing to judge, and — as the product definition puts it — nothing Radhanite
can make an economic decision about.

### The four pieces now run together

```
chose     Direct Attempt
attempt   Direct Attempt (initial attempt, 0.35 likely) cost $0.02, ended in partial_progress
verdict   Not met: the attempt made partial progress, which is not "tests pass".
decision  ESCALATE — raising the chance of success from 0.35 to 0.55 on a $20.00
          outcome is worth $4.00, against a cost of $0.08, with $1.98 remaining.
```

That is a task being attempted, honestly judged as unfinished, and a reasoned
decision to spend eight more cents. Nothing yet strings those steps into a loop —
that is the next piece of work.

## 6. What goes into the system

For attempting: a chosen strategy, whether this is the first or the dearer
second attempt, and a script of what happens. For judging: an attempt, and the
task's measure of success.

## 7. What the system decides

Whether the requirement was met. Nothing else — no economic judgement is made
here.

## 8. What comes out

A record of the attempt (which strategy, first or second, what happened, what it
cost, what its stated chance was) and a verdict with the reason for it. Neither
can be altered afterwards.

## 9. How it can fail

- **Nothing here is real work.** The whole thing reports what it was told. It is
  a rehearsal for the economic machinery, and any claim it demonstrates the
  ability to *do* software engineering would be false.
- **The judgement is only as good as the input.** Since the outcome is supplied
  rather than observed, this stage cannot detect a scenario that describes
  something implausible.
- **The verdict follows the outcome, not an independent check.** Judging is
  where a real requirement would actually be tested, once real work exists.
  Today it turns a reported outcome into a verdict against a recorded
  requirement.
- **Softening remains the risk.** Every future change here should be read with
  one question in mind: does this make "nearly done" count as done?

## 10. Tests run, and their results

```
$ python --version
Python 3.12.13

$ python -m unittest discover
Ran 169 tests in 0.018s
OK
```

30 tests are new: 16 on attempting, 14 on judging. The ones that matter most:

- Partial progress is not success, checked four ways, including one test
  asserting there are exactly two possible verdicts.
- Partial progress and failure keep different records despite sharing a verdict.
- A strategy that never succeeds still reports a scripted success, twenty times
  over — proof that nothing is being sampled.
- The same script produces the same run, twenty times over.
- Each of the three outcomes can be produced on demand.
- A first attempt is charged the first price and a second the second, with the
  matching stated chance of success.
- Asking for an unscripted attempt raises rather than inventing one.
- A missing measure of success is refused.
- Records cannot be altered after the fact, including by the back door found in
  the previous pull request's review.

## 11. Assumptions made

- That the outcome of an attempt must be an input rather than something
  discovered, because the specification asks for exactly that and because
  economic reasoning cannot be tested against results that vary.
- That partial progress deserves to exist as a distinct outcome even though it
  never counts as success, because a run record that could not tell it apart
  from failure would lose real information.
- That asking for an attempt the scenario never described is a fault in the
  caller rather than an outcome to invent.

## 12. Known limitations

- No real work is done, and none is authorized.
- The judgement mirrors the supplied outcome rather than independently checking
  anything.
- Nothing yet drives these steps in a loop, tracks the running budget, or writes
  a record of the whole run.

## 13. Functionality explicitly left out of scope

No loop, no run record, no command to run a task. Nothing excluded by TASK-001
§3 appears: no model APIs, no real execution against a repository, no wallets,
no tokens, no interface, and no learning. **The project still depends on nothing
but Python itself.**

## 14. Deferred to future tasks

The loop that ties the pieces together while enforcing the budget ceiling, the
run record, and a command that runs one task end to end.

## 15. How to explain this to a judge

Radhanite can now attempt a task and judge whether the attempt worked.

The attempting is deliberately fake — it is told what happens and reports it.
That is not a shortcut, it is the requirement: you cannot prove that reasoning
about uncertain outcomes is *correct* while the outcomes are themselves
uncertain. Fix what happens, and every money decision becomes checkable. Real
execution is a later, separate piece of work that is explicitly not authorized
yet.

The judging is where the honesty lives. There are two verdicts — met, or not —
and an attempt that got *part* of the way counts as **not met**. That sounds
harsh, and it is the most important line in this pull request. If "nearly there"
counted as success, Radhanite would decide the job was finished, stop spending
your money, and tell you it had succeeded at something it had not. The
specification forbids that in those words, and four tests hold it in place.

---

**This document explains; it does not govern.** The product definition,
architecture document, task specification, and the code and its tests are the
authoritative record. Where this explanation and the repository disagree, the
repository is correct.
