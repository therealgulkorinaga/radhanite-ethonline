# PR-023 — Choosing the best of several things worth buying

**Pull request:** #23
**Authorized task:** TASK-006 §2.4, §2.5
**Author:** Claude Code, under human product owner authorization

---

## 0. A note on the order this was built in

The product owner's authorization required a **test-first** sequence: write the
tests, run them, watch them fail because ranking is not implemented, then
implement.

**That is not quite what happened, and the record should say so.**

The implementation was written earlier in the same working session, when the
instruction was simply *"start PR C"*. The test-first authorization arrived
afterwards. Nothing had been committed, so the requirement was met as closely as
it honestly could be: **the ranking was removed, the tests were run against a
selector that could not rank, the genuine failures were recorded (§10a), and the
ranking was then restored.**

What that demonstrates is real — the tests do detect the absence of ranking, and
which ones detect it is now on the record. What it does not demonstrate is tests
written in ignorance of a working implementation. **The author had prior
knowledge of the design.** A reader should weigh the evidence in §10a with that
in mind.

## 1. Purpose of this PR

The third piece of TASK-006. Given several candidates that all pass the
eligibility test, **pick one** — deterministically, with no way for the order
they arrived in to change the answer.

Or, when none passes, **stop**.

## 2. What changed

| File | What it is |
|---|---|
| `radhanite/selection.py` | **New.** The ranking, its tie-breaks, and the stop |
| `tests/test_selection.py` | **New.** 77 tests |
| `radhanite/__init__.py` | Exports the new pieces; its status note updated |
| `docs/reviews/PR-023_CODEX_REVIEW.md` | The review prompt, **committed before the review runs** |
| `docs/reviews/README.md` | Its row in the review index |
| `docs/pr_explanations/PR-023_...md` | This document |

Six files. **No new dependency** — the project still has none.

## 3. Why the change was needed

PR #22 could tell you whether *one* thing was worth buying. It had no opinion
about which of five to buy, which is the actual question.

## 4. How this worked before

There was no way to ask. Eligibility answered one candidate at a time, and
nothing compared the answers.

## 5. How it works after

Every candidate is assessed. Among those that pass, one wins:

| | Rule |
|---|---|
| **1** | The **best net value** — what it is worth, minus what it costs |
| **2** | If two tie exactly — the **cheaper** one |
| **3** | If they tie on price too — the one whose **identifier sorts first** |

**Rule 2 has a reason.** Two candidates delivering the same net value differ only
in how much budget they burn doing it, and the cheaper one leaves more for
whatever comes next.

**Rule 3 has none, deliberately.** It exists only so the answer is never
ambiguous. It is not an economic judgement and must never be described as one —
there is a test asserting a candidate cannot win on its name while another has a
better net value.

### Why the order candidates arrive in cannot matter

Because those three rules always produce an answer, and identifiers are unique
within an offer, **no two candidates can tie at every level**. The ordering is
total, so shuffling the input cannot change the winner.

That is a real departure from the delivered system, where the declared order of
the catalogue *was* the policy. Tests run every permutation of a three-candidate
offer — including one where all three tie on net value and two tie on price as
well — and require the same winner every time.

### The test that makes cheap-routing and uplift-routing impossible

Three candidates, chosen so that the obvious wrong implementations pick the
wrong one:

| | Cost | Chance after | Worth | **Net** |
|---|---|---|---|---|
| A | $8.00 | 0.95 — **best odds** | $9.00 | $1.00 |
| B | $0.10 — **cheapest** | 0.53 | $0.60 | $0.50 |
| C | $2.00 | 0.80 | $6.00 | **$4.00** |

**C must win.** An implementation that reached for the biggest improvement would
pick A; one that reached for the cheapest would pick B. A companion test first
asserts the premises actually hold — that A really is the biggest uplift and B
really is the cheapest — because otherwise the conclusion would prove nothing.

### When nothing wins

**Stop.** Not an error, not an exception, not an empty result to be worked
around — a first-class correct outcome, exactly as it is in the delivered
system.

And a stop knows *why*. If every candidate was refused by a safety rule —
already bought, or the run's purchase allowance spent — the stop says so
explicitly, because the economics never weighed those candidates at all.
A stop where even one candidate was refused on economic grounds is not a safety
stop, and there is a test with one of each to prove the distinction is not
merely cosmetic.

## 6. What goes into the system

The offer, the current chance of success, what success is worth, the remaining
budget, what has already been bought, and the purchase count and its limit.

## 7. What the system decides

**Which one candidate wins, or that none does.** Nothing else.

It does not buy anything, does not mark the winner as bought, does not advance
the purchase count, and does not re-decide eligibility — it reads the
assessments the eligibility rule produced.

## 8. What comes out

A selection carrying the winner, **every candidate that was considered including
the losers**, each with its figures and the reason it lost, the decision-level
inputs, and a sentence explaining the outcome.

Keeping the losers is the point: a record showing only what was bought cannot
answer why the alternatives were not.

## 9. How it can fail

Ordinary outcomes: a winner, or a stop.

Genuine faults raise — two assessments for the same identifier, an unordered
collection, something that is not an assessment, or assessments computed against
a task state other than the one supplied.

*(As first written, these checks were performed on candidates by the function
delivered in PR #21. After the correction in §14a they are performed on
assessments by a sibling function, and PR #21's `validate_candidates` no longer
has a caller — see §14a.)*

## 10. Tests run and their results

```
$ python3.12 -m unittest discover -q
Ran 423 tests in 0.15s
OK
```

**423 passing — 346 existing, unchanged, plus 77 new** (54 with the original
work, 23 more with the corrections in §14a).

## 10a. What the tests do when the ranking is not there

Two states were measured, with compiled bytecode cleared each time.

**With no selection module at all** — the true "before" — the test file cannot
import and reports a single collection error.

**With the module present but the ranking removed** — everything else intact, so
the failures isolate ranking specifically:

```
Ran 54 tests
FAILED (failures=3, errors=30)
```

**33 failures across 18 distinct test methods.** Every ranking, tie-break and
order-independence test fails, including the A/B/C test above. The tests that
kept passing are the ones that do not depend on ranking — the stop behaviour,
the record contents, the boundary checks — which is the discrimination one would
want.

See §0 for what this evidence does and does not establish.

## 10b. Deliberate faults, and whether they were caught

Eight faults, introduced one at a time, bytecode cleared between each:

| Fault introduced | Result |
|---|---|
| Choose the biggest uplift instead of the best net value | **8 failures** |
| Choose the cheapest instead of the best net value | **10 failures** |
| Reverse the cost tie-break | **8 failures** |
| Reverse the identifier tie-break | **1 failure** |
| Let ineligible candidates compete | **7 failures** |
| Keep the first eligible candidate, never compare | **14 failures** |
| Skip the duplicate-identifier check | **2 failures** |
| "All refusals were safety rules" becomes "any of them was" | **1 failure** |

**All eight caught.**

An earlier run of this exercise reported two of them as *surviving*. That was
wrong, and the cause is worth recording: stale compiled bytecode from a previous
mutation was being reused, so the test suite was not running the code on disk.
It also produced a genuine false result inside the suite itself. Clearing
`__pycache__` between runs fixed both, and the numbers above are from clean
runs.

One test was rewritten as a result. A "mixed stop" case had been built so that
*both* candidates failed on economics, which meant it could not distinguish
"all refusals were safety rules" from "any of them was". It now has one
candidate refused purely by a safety rule and one purely on economics.

One further assertion was deleted before this shipped. It compared two sums that
were algebraically identical, so it would have passed whatever the code did.

## 11. Assumptions made

- **Identifiers are unique within an offer.** Enforced in PR #21, and what makes
  the ordering total.
- **Assessments arrive already computed.** This step does not re-run the
  eligibility rule.
- **The task's success condition was checked before this was called.** It is the
  other reason to stop, and it belongs to a layer this module is never told
  about.

## 12. Known limitations

- **Nothing runs a loop yet.** One decision, one offer, one answer. Maintaining
  the purchase count and the list of things already bought belongs to the run
  loop, which does not exist.
- **The numbers are still declared fixtures**, as everywhere in this project.
- **The evidence in §10a is weaker than a true test-first sequence**, for the
  reason given in §0.

## 13. Explicitly out of scope

Candidate generation, changes to the eligibility rule, marking a candidate as
bought, advancing the purchase count, execution, task-state updates, the run
loop, and every integration. No provider, no payment, no wallet — enforced by a
test that reads the source file.

## 14. Deferred to future tasks

The run loop, and the demonstration that the delivered two-tier scenarios still
decide identically.

## 14a. Corrections after the Codex review

The review **rejected** this pull request. Three findings, none about the
ranking rule itself — that was validated as correct and is preserved unchanged.
All three were about the **boundary** the ranking sits behind, and about what
the record says.

**These corrections were written test-first, properly.** Unlike the original
work (§0), the regression tests were written and run *before* any correction
existed. They failed: **90 failures across 70 test methods**, every one rooted in

```
TypeError: select_capability() got an unexpected keyword argument 'assessments'
```

— the boundary simply did not exist yet. Then the corrections were implemented,
and the same tests re-run green.

### `CODEX-PR023-01` — the ranking was computing its own eligibility

It accepted raw candidates and ran the eligibility rule itself. That is one
layer owning two decisions, and it could reach a different answer from the
record its caller already held.

It now takes **assessments the caller has already computed**. It never calls the
eligibility rule — a test replaces that rule with something that explodes on
contact and requires selection to work anyway. It checks that identifiers are
unique by reading the assessments, not by re-deciding anything. And it changes
nothing it is given: tests compare every field of every assessment, and the
candidates behind them, before and after.

**One check was added that nobody asked for**, because the refactor would
otherwise have opened a hole it did not previously have. When ranking computed
its own assessments, they could not disagree with the task state it was told
about. Now they are supplied separately, so a caller could hand over assessments
computed against a $2 budget while claiming a $10 one. Selection refuses that
rather than producing a record that quietly contradicts itself.

### `CODEX-PR023-02` — the run forgot what it had already bought

The list of already-purchased identifiers was read off the first assessment. If
no candidates were offered there was nothing to read, so a stop on an empty
offer reported *nothing bought* even for a run that had bought three things.

Already-bought identifiers belong to **the run**, not to whatever happens to be
on offer at one moment. They are now normalized from the argument directly and
survive an empty offer.

### `CODEX-PR023-03` — a safety stop was being reported as an economic one

When the purchase allowance was spent **and** the candidates would also have
failed on price, the stop was described as *"nothing was worth buying"*.

That is not what happened. The run was already forbidden from buying anything
before a single candidate was weighed. **The ceiling now takes precedence**: if
the allowance is spent, the stop is a safety stop and says so, whatever else was
true of the offer. The candidates' economic failures are still recorded against
them individually — both facts survive — but they no longer supply the reason
the run ended.

### Deliberate faults, all caught

Eight, one at a time, with bytecode writing disabled so stale compiled files
could not repeat the problem described in §10b:

| Fault introduced | Result |
|---|---|
| Make the eligibility rule reachable from selection again | **1 failure** |
| Have selection recompute assessments itself | **2 failures** |
| Reset already-bought identifiers on an empty offer | **3 failures** |
| Ceiling loses precedence — the classification | **3 failures** |
| Ceiling loses precedence — the explanation | **2 failures** |
| Let an ineligible assessment win | **14 failures** |
| Reverse the cost tie-break | **9 failures** |
| Reverse the identifier tie-break | **1 failure** |

### One consequence worth naming

`validate_candidates`, delivered in PR #21, **no longer has a caller**. Ranking
used to call it; it now checks assessments instead, through a sibling function.
That was the exact concern flagged on PR #21, briefly resolved by this pull
request, and reopened by this correction. It is stated here rather than left for
someone to notice.

## 15. How to explain this to a judge

> Five things you could buy, five prices, five claims about how much they would
> help. Which one?
>
> Work out what each is worth, subtract what it costs, take the best. If two are
> exactly equal, take the cheaper — it leaves more money for later. If they cost
> the same too, take whichever name sorts first, purely so the answer is never
> ambiguous.
>
> The important property is that shuffling the list cannot change the answer. We
> test every possible ordering, including the nastiest case where everything
> ties.
>
> And there is one test built specifically so that the two tempting shortcuts —
> "buy the biggest improvement" and "buy the cheapest" — each pick the wrong
> candidate. If someone ever implements one of those by accident, that test
> fails.
>
> We also checked the tests themselves by breaking the code eight different ways
> on purpose. All eight were caught — though the first attempt at that check was
> itself wrong, because of stale compiled files, and that is written down too.
