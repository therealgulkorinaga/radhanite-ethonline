# PR-021 — What a thing Radhanite could buy looks like

**Pull request:** #21
**Authorized task:** TASK-006 §2.2, §2.5 A
**Author:** Claude Code, under human product owner authorization

---

## 1. Purpose of this PR

The first piece of TASK-006: **the shape of a candidate capability** — one thing
the system could buy — and the checks an offer must pass before any decision is
made over it.

**It contains no economic rule.** Nothing here decides whether a candidate is
worth buying, ranks candidates against each other, or stops a run. Those arrive
in the next steps.

## 2. What changed

| File | What it is |
|---|---|
| `radhanite/capability.py` | **New.** The candidate, and the checks on an offer |
| `tests/test_capability.py` | **New.** 36 tests |
| `radhanite/__init__.py` | Exports the new pieces; its status note updated |
| `docs/pr_explanations/PR-021_...md` | This document |

Four files. **No new dependency** — the project still has none.

## 3. Why the change was needed

TASK-006 was authorized in PR #20. This is where building it starts.

Everything else in the task depends on this piece. You cannot write a rule that
compares candidates until there is a candidate to compare, and the rule's most
important property — that it cannot tell who is selling — is a property of this
shape rather than of the rule itself.

## 4. How this worked before

There was no such thing. The delivered system knows about a **strategy**: an
opening attempt and one dearer escalation, bolted together in a single object.
Nothing existed that could represent "here is one thing you could buy" on its
own.

## 5. How it works after

A **candidate** carries exactly three things:

| | |
|---|---|
| **an identifier** | e.g. `second-opinion-001` — stable, and unique within one decision |
| **a cost** | what it costs to take this action |
| **a success probability** | the chance of the task succeeding *after* it |

**Three, and no more.** There is a test asserting the count, because a fourth
field is exactly how a provider-shaped idea would arrive in a model that must
stay provider-neutral. Nothing here records who supplies a capability, how it
would be paid for, or what network it lives on — and a test reads the source
file to confirm none of those words appears in it.

### What the candidate refuses to be built with

**A cost of zero, or less.** This one is worth explaining, because it looks like
an economic rule and is not.

It is a *termination safeguard*. A free capability that improved the odds even
slightly would always be worth taking, so it would be taken — and since these
probabilities are fixed numbers that do not move when a capability runs, it would
be worth taking again on identical terms, forever, without ever spending a penny
over budget. The loop would never end and no budget check would notice.

Refusing a free candidate at construction closes that off before it can happen.
Free or local actions are simply not purchasable capabilities.

**A blank or padded identifier.** `"a "` and `"a"` would read as one candidate in
a run record while being two under the rule that an offer can only be taken
once — so one could be marked as used while the other stayed on the table.

### What it deliberately does *not* refuse

**A candidate that is not worth buying.** A hopeless one, an outrageously
expensive one, one that makes things no better — all are perfectly valid
objects. Whether an offer beats the task's current position is a question about
a *decision*, not about the offer, and the candidate cannot see the budget or
the current state anyway.

Rejecting them here would turn an ordinary economic situation into an invalid
object. TASK-001 made that mistake once and an independent review caught it.

### Checking an offer

Before a decision is made over a group of candidates, two things are refused
outright rather than tidied up:

**An unordered collection.** Selecting is order-independent — that is
guaranteed by the ranking rule, in a later step. But the *record* is not: it
lists every candidate considered, and a record whose order changes between
identical runs cannot be reproduced.

**Duplicate identifiers.** Two candidates sharing an identifier leave the
decision undefined, because the final tie-break is on the identifier itself; and
marking one as used would silently mark the other. Refused, never resolved.

The check also hands back a frozen copy, so a caller cannot change the offer
underneath a decision after passing it in.

## 6. What goes into the system

A candidate's three values, supplied by whatever generated the offer. Generating
offers is not this task's job.

## 7. What the system decides

**Nothing.** This piece makes no decision at all. It says what a candidate is,
and refuses inputs over which no sound decision could be made.

That refusal is the only judgement here, and it is about well-formedness rather
than about value.

## 8. What comes out

A validated candidate, or a validated offer as a frozen sequence — or an error
explaining precisely which rule was broken and, where it helps, where.

No run record changed. No output of the existing system changed.

## 9. How it can fail

Every failure is a refusal at the boundary, raised immediately with a reason:

- a cost of zero or less, or a cost that is not exact money;
- a missing, blank, padded, or non-text identifier;
- a probability that is not a probability;
- an offer that is not an ordered sequence, or contains something that is not a
  candidate;
- two candidates in one offer sharing an identifier.

Each says which rule it broke. The duplicate error names both positions and the
identifier; the wrong-type error names the position.

## 10. Tests run and their results

```
$ python3.12 -m unittest discover -q
Ran 278 tests in 0.11s
OK
```

**278 passing — 242 existing, unchanged, plus 36 new.**

The new tests were then checked against deliberate breakage, because a test that
passes whatever the code does is worse than no test. Five separate faults were
introduced into the module one at a time, and every one was caught:

| Fault introduced | Result |
|---|---|
| Allow a zero cost (check only for negatives) | **2 failures** |
| Stop rejecting padded identifiers | **1 failure** |
| Accept unordered collections | **1 failure** |
| Stop detecting duplicate identifiers | **3 failures** |
| Stop taking a frozen copy of the offer | **5 failures** |

The file was restored and the full suite re-run green afterwards.

## 11. Assumptions made

- **Identifiers are compared exactly as given.** `"A"` and `"a"` are two
  different candidates. Folding case would quietly change which one wins a
  tie-break, so it is not done.
- **An offer arrives as an ordered sequence.** A list or a tuple; not a set, not
  a generator.
- **The numbers are declared fixtures.** As everywhere else in this project,
  nothing here measures or learns anything.

## 12. Known limitations

- **Nothing decides anything yet.** This is one piece of TASK-006, not TASK-006.
  A reader should not conclude the capability model works — it does not exist
  as a working thing until the rule that uses it does.
- **The check for an offer has no caller yet.** It is a behaviour TASK-006 §2.2
  specifies and this step delivers, tested directly; the selection rule that
  uses it arrives next. Worth naming, because "code with no caller" is normally
  a smell.
- **Single-use candidates are not enforced here.** That belongs to a run, which
  tracks what it has already bought. A test asserts this module has *not*
  quietly acquired a memory of candidates it has seen.

## 13. Explicitly out of scope

The eligibility rule, the ranking and its tie-breaks, the termination
safeguards, the run loop, candidate generation, task-state evaluation, and every
integration. No provider, no payment, no wallet — enforced by a test that reads
the source.

## 14. Deferred to future tasks

The remaining steps of TASK-006: eligibility, ranking and tie-breaking, the
consumed-candidate and step-ceiling safeguards, and a demonstration that the
existing two-tier scenarios still decide identically.

## 15. How to explain this to a judge

> Before the system can choose what to buy, it needs to know what a thing you
> could buy looks like. That is this change.
>
> It is three facts: what it is called, what it costs, and how likely you are to
> succeed after buying it. Three, deliberately — because a fourth would let the
> rule notice *who is selling*, and the whole claim of this project is that the
> decision is about value, not about suppliers. There is a test that reads our
> own source code to make sure no supplier's name appears in it.
>
> One rule looks odd until you see why: nothing free can be a candidate. A free
> thing that helps is always worth taking, so the system would take it forever
> and never spend a penny over budget while doing so. Refusing free offers is
> how the loop is guaranteed to end.
>
> And we checked the tests by breaking the code on purpose in five different
> ways. All five were caught.
