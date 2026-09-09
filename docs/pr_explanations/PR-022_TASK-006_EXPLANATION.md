# PR-022 — Deciding whether one thing is worth buying

**Pull request:** #22
**Authorized task:** TASK-006 §2.3
**Author:** Claude Code, under human product owner authorization

---

## 1. Purpose of this PR

The second piece of TASK-006: given where a task currently stands and **one**
thing it could buy, decide whether that purchase is allowed — and work out what
it would be worth either way.

**It chooses nothing.** Comparing candidates against each other, picking a
winner, and deciding what a run does next are later steps. This answers one
question about one candidate.

## 2. What changed

| File | What it is |
|---|---|
| `radhanite/eligibility.py` | **New.** The six-condition test, and the figures behind it |
| `tests/test_eligibility.py` | **New.** 68 tests |
| `radhanite/__init__.py` | Exports the new pieces; its status note updated |
| `docs/reviews/PR-022_CODEX_REVIEW.md` | The review prompt, **committed before the review runs** |
| `docs/reviews/README.md` | Its row in the review index |
| `docs/pr_explanations/PR-022_...md` | This document |

Six files. **No new dependency** — the project still has none.

## 3. Why the change was needed

PR #21 gave the system a way to describe something it could buy. Nothing yet
had an opinion about whether buying it was a good idea.

This is the arithmetic Radhanite exists to perform. Everything else — the
ranking, the run loop, the eventual purchase — is machinery around this
judgement.

## 4. How this worked before

The delivered system could answer one narrow version of the question: *is the
one dearer option worth taking?* It was hardwired to a two-tier strategy and
could not be asked about anything else.

## 5. How it works after

Given the current chance of success, what success is worth, what budget remains,
how many purchases the run has already made, which candidates it has already
bought, and **one** candidate — the answer is **eligible** or **ineligible**,
with the reasons and the money.

### The two numbers

**What the improvement is worth:**

> (the chance after buying it − the chance now) × what success is worth

**And what it is worth net of its price:**

> that value − the price

Worked through: a candidate costing $0.50 that lifts the chance from 0.50 to
0.80, on an outcome worth $20.00, is worth $6.00 — **$5.50 net**.

### Six conditions, all of which must hold

| | |
|---|---|
| **1** | It costs more than nothing |
| **2** | Its price fits the remaining budget |
| **3** | It actually improves the odds |
| **4** | What it is worth **exceeds** what it costs |
| **5** | This run has not already bought it |
| **6** | The run has not used up its allowance of purchases |

**Condition 4 is a strict "exceeds", and that is deliberate.** A candidate worth
exactly its price buys nothing — you hand over $0.50 and get $0.50 of expected
value back. Making this "at least" instead would be a defect, not a rounding
choice, and there is a test that fails if anyone does it.

**All failures are reported, not just the first.** A candidate can fail four
conditions at once, and a run record that showed only one would misdescribe why
it was rejected.

### Three of the six conditions are not economic, and the code says so

Conditions 1, 5 and 6 are the **termination safeguards**. A candidate refused
because the run has already bought its allowance, or because it is free, was
never assessed on its merits at all — the economics did not reject it, a safety
rule did.

**A price of zero is not a cheap price.** Free candidates are excluded so that
the loop is guaranteed to end, and that refusal says nothing about whether the
candidate was worth having. *(This originally classed condition 1 as economic.
See §14a.)*

The distinction is carried in the code, not just in prose: each reason knows
whether it is economic, and an assessment can say *"this was refused without any
judgement about its value."* A run record that blurred the two would claim a
verdict nobody reached.

### Condition 3 looks redundant, and is not

If a candidate costs something and success is worth something, then "worth more
than it costs" already implies "improves the odds". The specification insists on
stating it anyway, and there is a test showing why.

Give the task a **negative** value — which nothing should, but which this
function cannot rule out — and a candidate that makes things *worse* produces a
positive-looking worth of $12.00 and sails through condition 4. Condition 3 is
the only thing that catches it.

### What it refuses to answer at all

A **negative remaining budget** is not an economic situation, it is a broken
one: the ceiling has already been breached, and whatever tracks the balance is
wrong. The function stops rather than producing a confident answer from a broken
state.

## 6. What goes into the system

The current chance of success, what success is worth, the remaining budget, the
purchase count and its limit, the identifiers already bought, and one candidate.

**Not** what the run has spent. Money already gone is irrelevant to whether the
next purchase is worth making, so the function is not even told — a test asserts
the parameter does not exist.

## 7. What the system decides

**Whether one candidate may be bought.** Not which one to buy.

## 8. What comes out

An assessment carrying the verdict, a sentence explaining it, both money
figures, and every input that produced it — **including the list of
already-bought identifiers it was measured against** — so the answer can be
recomputed later rather than taken on trust.

That list is stored sorted, with duplicates removed, and copied. Sorted because
a record whose contents reorder between identical runs cannot be compared
against itself; copied because a caller changing their own list afterwards must
not be able to change what the record says it was computed against.

**The money is calculated for rejected candidates too.** A record that showed
figures only for the winner could never answer why the alternatives lost.

## 9. How it can fail

Two kinds of thing, kept firmly apart.

**Ineligibility is not failure.** It is the ordinary answer, reported with
reasons.

**Genuine faults raise** — a negative budget, a negative purchase count,
something that is not exact money where money is required, a purchase count that
is not a whole number, or a required setting omitted.

One guard is worth naming. The list of already-bought identifiers refuses a bare
piece of text, because asking whether `"a"` is in `"abc"` is a *substring* test
in Python — it would have silently marked candidates as bought that never were.

## 10. Tests run and their results

```
$ python3.12 -m unittest discover -q
Ran 346 tests in 0.08s
OK
```

**346 passing — 278 existing, unchanged, plus 68 new** (56 with the original
work, 12 more with the corrections in §14a).

Twelve deliberate faults were introduced one at a time to check the tests detect
what they claim. Every one was caught.

Eight for the rule itself:

| Fault introduced | Result |
|---|---|
| "Worth exactly its cost" becomes eligible | **1 failure** |
| "Exactly affordable" becomes unaffordable | **1 failure** |
| "No improvement" becomes an improvement | **2 failures** |
| Allow one purchase past the limit | **6 failures** |
| Stop checking what was already bought | **5 failures** |
| Allow a free candidate | **1 failure** |
| Use the budget where the task's value belongs | **12 failures** |
| Forget to subtract the price | **5 failures** |

And four for the corrections:

| Fault introduced | Result |
|---|---|
| Class a free candidate as an economic refusal again | **3 failures** |
| Record the already-bought list unsorted and undeduplicated | **4 failures** |
| Stop recording the already-bought list at all | **7 failures** |
| Sort the list but keep duplicates | **1 failure** |

The file was restored and the suite re-run green after each.

## 11. Assumptions made

- **The purchase limit is supplied, always.** There is no default, because a
  default would make a safety limit optional. A test asserts omitting it is an
  error.
- **A limit of zero is a legitimate policy** meaning "buy nothing", not a fault.
- **Already-bought candidates are matched by identifier alone.** The rule has no
  idea that two candidates are the same sort of thing, and deliberately must
  not.

## 12. Known limitations

- **Nothing is selected yet.** One candidate in, one verdict out. The ranking
  arrives next.
- **Condition 1 cannot normally be reached.** A free candidate is already
  refused when it is built, so this check only fires if that refusal is
  deliberately bypassed. It is kept, and tested by bypassing it, because a
  safety rule that quietly lapses when defeated elsewhere is not a safety rule —
  but a reviewer should judge whether that is defence in depth or dead code.
- **Nothing tracks what has been bought.** The list of consumed identifiers is
  passed in. Maintaining it belongs to the run loop, which does not exist yet.

## 13. Explicitly out of scope

Ranking and tie-breaking, the run loop, candidate generation, task-state
evaluation, execution, and every integration. No provider, no payment, no wallet
— enforced by a test that reads the source file.

## 14. Deferred to future tasks

The ranking and its three tie-breaks; the run loop that maintains the purchase
count and the consumed list; and a demonstration that the existing two-tier
scenarios still decide identically.

## 14a. Corrections after the Codex review

The review returned **two findings**, both about auditability rather than about
the rule. The original text above is left standing where it was wrong, with
pointers here, so what changed stays legible.

**`CODEX-PR022-01` — the record could not be recomputed.** An assessment claimed
to carry every input behind its answer, and did not carry the list of
already-bought identifiers. Two assessments computed against different lists
would have been indistinguishable, and nobody could have checked the
already-bought condition from the record alone.

The normalized list is now part of the assessment: **sorted, de-duplicated,
copied**. Sorted because a set's order varies between runs and a record that
reorders cannot be compared with itself. Copied because a caller must not be
able to change what an assessment says it was measured against, after the fact.
It holds identifiers and nothing else — consumption is by identifier, and no
notion of capability type arrives through it.

**`CODEX-PR022-02` — a safeguard was labelled as economics.** The refusal of a
free candidate was classified as an economic judgement. It is not one:
TASK-006 §2.5 A excludes free candidates so the loop terminates, and the refusal
carries no view about whether the candidate was worth buying. A run record built
on the old classification would have reported that the economics rejected
something the economics never assessed.

Three conditions are now safeguards — free, already bought, allowance spent —
and three are economic. **The check itself is unchanged**; only its label was
wrong. A new test asserts every condition is classified one way or the other, so
a condition added later cannot default silently into the wrong group.

## 15. How to explain this to a judge

> This is the sum the whole product is built around.
>
> Something costs $0.50 and would lift your chance of success from 50% to 80%.
> The outcome is worth $20. So the improvement is worth $6, and you are being
> asked for 50p. Buy it.
>
> Six checks have to pass, and two of them are not about money at all — you
> cannot buy the same thing twice, and every run has a hard cap on how many
> things it may buy. Those are what guarantee the system stops. The code knows
> the difference, so a run report never claims the economics rejected something
> when really it just hit the limit.
>
> One check looks pointless — "does it actually improve the odds?" — when the
> value test seems to cover it. We kept it, and there is a test showing the one
> situation where it is the only thing standing between the system and a wrong
> answer.
>
> And we broke the code on purpose in eight different ways to check the tests
> would notice. They noticed every time.
