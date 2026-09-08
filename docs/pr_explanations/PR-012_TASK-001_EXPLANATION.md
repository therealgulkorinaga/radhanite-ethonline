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
| `tests/test_execution.py` | 26 checks on the first |
| `tests/test_evaluation.py` | 18 checks on the second |
| `radhanite/__init__.py` | Updated to say what is now built |
| `docs/pr_explanations/PR-012_...md` | This document |
| `docs/reviews/PR-012_CODEX_REVIEW.md` | The review prompt, committed before the review |
| `docs/reviews/README.md` | Its row added to the index of reviews |

Eight files. The test count went from 139 to 183 — 44 new.

This pull request was **rejected on review** and substantially reworked. Three
problems were found, one of them serious enough that the judging step had to be
rebuilt. The record is in `docs/reviews/PR-012_CODEX_REVIEW.md`.

## 3. Why the change was needed

Radhanite could describe a task, price three ways of attempting it, pick one,
and weigh whether spending more was worth it. It could not attempt anything, and
had no idea whether anything had worked.

## 4. How this worked before

Nothing executed and nothing was judged.

## 5. How it works after

### Attempting the work

The thing that "does the work" does no work at all. It is **told in advance what
becomes true** — and reports that, charging the price the chosen strategy
declared.

What it reports is *evidence*, not a verdict, and the difference turned out to
matter enormously. The first version of this pull request had it report
"success" or "failure" directly. The reviewer pointed out that this meant the
pretend-worker was handing down the answer and the judging step was only
relabelling it — the same attempt counted as a success against **any**
requirement, including ones it plainly had not met. Judging something is not the
same as being told the answer, and the two stages exist separately for that
reason.

So an attempt now reports **which conditions became true**, plus a sentence
describing what happened for a human reader. Nothing decides anything from that
sentence.

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

The requirement is met if, and only if, it is among the things the attempt
actually achieved. Same attempt, three different requirements:

```
achieved "tests pass"   judged against "tests pass"        ->  met
achieved "tests pass"   judged against "issue #184 closed"  ->  not met
achieved "tests pass"   judged against "2 + 2 == 5"         ->  not met
```

That is the comparison the specification asks for, and the first version of this
pull request did not have it.

There is no partial credit for near misses either. An attempt that achieved
"the tests pass" has **not** achieved "tests pass" — no synonyms, no
approximate matching. Inventing either would be exactly the interpretation the
specification forbids, and there is a test for it.

Two verdicts: met, or not. There is deliberately no third, and a test asserts
there are exactly two so a third cannot be quietly added.

**The important part is what happens to partial progress.** An attempt that
achieved *something else* has not achieved what was asked for. That is the
single most dangerous mistake available in this whole system: if "made progress"
were treated as success, Radhanite would conclude the job was finished, stop
spending, and report an outcome that never happened. The specification forbids
it in those words.

It now falls out of the comparison rather than needing a rule of its own, which
is better — there is no "partial" case to accidentally soften. Progress and
outright failure share a verdict but not a record: both are "not met", and the
record keeps exactly what *was* achieved, so nothing is lost.

A task with no way of measuring success is refused outright. Without one there
is nothing to judge, and — as the product definition puts it — nothing Radhanite
can make an economic decision about.

### The four pieces now run together

```
chose     Direct Attempt
attempt   Direct Attempt (initial attempt, 0.35 likely) cost $0.02: it builds, tests still red
verdict   Not met: "tests pass" is not among what the attempt achieved (code compiles).
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

A record of the attempt (which strategy, first or second, what became true, what
it cost, what its stated chance was) and a verdict with the reason for it.

Neither can be altered by ordinary assignment, by reaching into the object's
internals, or by having its contents replaced wholesale. Neither is proof
against a caller who deliberately goes around the language's normal mechanisms —
`radhanite/_immutable.py` sets out precisely what is and is not prevented, and
why the stronger guarantee is not available.

## 9. How it can fail

- **Nothing here is real work.** The whole thing reports what it was told. It is
  a rehearsal for the economic machinery, and any claim it demonstrates the
  ability to *do* software engineering would be false.
- **The judgement is only as good as the input.** Since the outcome is supplied
  rather than observed, this stage cannot detect a scenario that describes
  something implausible.
- **The evidence is supplied, not gathered.** The comparison is real, but what
  it compares against is written into the scenario rather than observed from a
  running system. Once real work exists, this is where a real requirement gets
  checked against a real result; the comparison itself does not change.
- **Softening remains the risk.** Every future change here should be read with
  one question in mind: does this make "nearly done" count as done?

## 10. Tests run, and their results

```
$ python --version
Python 3.12.13

$ python -m unittest discover
Ran 183 tests in 0.015s
OK
```

44 tests are new: 26 on attempting, 18 on judging. The ones that matter most:

- **The same attempt is judged differently against different requirements.**
  This is the test the reworked design exists for; the first version could not
  have passed it.
- The sentence describing an attempt is never consulted — one claiming "complete
  and total success" while achieving nothing is still judged a failure.
- Achieving something under a slightly different name does not count.
- Achieving something *other* than what was asked is not met, however much of it
  there is.
- Progress and total failure keep different records despite sharing a verdict.
- Exactly two verdicts exist.
- A strategy that never succeeds still reports a scripted achievement, twenty
  times over — proof nothing is being sampled.
- The same script produces the same run, twenty times over, and two runs of one
  script do not interfere.
- A scenario that changes between readings cannot smuggle in something
  unchecked. Verified by reverting the fix and watching the test fail.
- Asking for an unscripted attempt raises rather than inventing one.
- A missing measure of success is refused.
- Records refuse ordinary alteration and refuse to be rebuilt wholesale. They
  are **not** proof against a caller deliberately reaching past the language's
  normal mechanisms — `radhanite/_immutable.py` states exactly what is and is
  not prevented, and the test names now say so too.

## 11. Assumptions made

- That what an attempt achieves must be an input rather than something
  discovered, because the specification asks for exactly that and because
  economic reasoning cannot be tested against results that vary.
- That the pretend-worker should report *evidence* and the judge should reach
  the *verdict*, rather than the worker reporting a verdict. This was the
  correction forced by review, and it is the right division regardless.
- That matching a requirement should be exact. Synonyms and approximate matching
  are precisely the interpretation the specification forbids.
- That asking for an attempt the scenario never described is a fault in the
  caller rather than an outcome to invent.

## 12. Known limitations

- No real work is done, and none is authorized.
- The comparison is real, but the evidence it compares is written into the
  scenario rather than observed from a running system.
- Records are protected against accident and ordinary misuse, not against a
  determined caller. The limits are documented rather than claimed away.
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

The judging is where the honesty lives, and it is where this pull request was
initially wrong. The first version had the pretend-worker announce "success" and
the judge simply agree — which meant one attempt counted as a success against
*any* requirement, including "2 + 2 == 5". An independent review caught it and
rejected the work.

It now compares properly: an attempt reports what it actually achieved, and the
requirement is met only if it is among those things. An attempt that got *part*
of the way counts as **not met**. That sounds harsh, and it is the most
important line here. If "nearly there" counted as success, Radhanite would
decide the job was finished, stop spending your money, and tell you it had
succeeded at something it had not.

---

**This document explains; it does not govern.** The product definition,
architecture document, task specification, and the code and its tests are the
authoritative record. Where this explanation and the repository disagree, the
repository is correct.
