# PR-019 — Writing down how Radhanite will choose between things it could buy

**Pull request:** #19
**Authority:** specification of `BL-13`, authorized by the human product owner
**Author:** Claude Code, under human product owner authorization

---

## 1. Purpose of this PR

To write down, precisely, how Radhanite should decide **which of several things
to buy** — and to stop there.

Today the system can only ask one question: *"should I escalate to the dearer
option?"* There is exactly one dearer option, and the answer is yes or no. The
new model asks a harder question: *"here are five things I could buy at five
prices, each claiming to improve my chances by a different amount — which one,
if any?"*

**Nothing is built by this pull request.** It is a specification. Under this
repository's rules a specification is not permission to implement, and this one
is explicitly not authorized.

## 2. What changed

| File | What it is |
|---|---|
| `tasks/TASK-006_GENERALIZED_CAPABILITY_SELECTION.md` | **New.** The specification itself |
| `tasks/BACKLOG.md` | `BL-13` moves from a one-line idea to a specified task, still unauthorized |
| `docs/ARCHITECTURE.md` | Two pointers to the new specification |
| `docs/pr_explanations/PR-019_...md` | This document |

Four files. No `.py` file, no dependency, no configuration. The test count is
unchanged at 242.

## 3. Why the change was needed

The product definition changed in PR #17: Radhanite decides which **capability**
is worth acquiring, not merely how much inference to buy. The delivered code
cannot express that — it knows about exactly two tiers.

The architecture document has said for some time that closing this gap must be
its own authorized task, and must never arrive quietly inside a sponsor
integration. The reason is that this is not a refactor. **Changing how
escalation works changes what escalation means, and that is the product.**

So the gap gets a specification of its own, in advance, where it can be argued
with before anything is built.

## 4. How this worked before

A strategy was a pair:

- an **opening attempt** — a price and a claimed chance of success;
- one **escalation** — a higher price and a better claimed chance.

After the opening attempt, one question was asked: *is the escalation worth its
price, given what success is worth and what budget remains?* Yes meant spend;
no meant stop.

That works, it is delivered, and 242 tests cover it. It simply cannot represent
a choice between more than one option.

## 5. How it works after

**Nothing works differently yet.** This is what the specification says should be
built.

```
current task state
  → zero or more candidate capabilities
  → deterministic economic selection
  → execute the selected capability, or STOP
```

A **candidate capability** is a priced action that might improve the chance of
finishing the task. It could be a stronger model, a second opinion, a piece of
research, a verification step, or a person reviewing something.

### The rule knows three things about a candidate, and only three

Its **identifier**, its **price**, and **the chance of success it claims to
leave you with**. That is the entire input to the decision.

This is deliberate and it is the most important constraint in the document.
**The rule must not know who is selling.** A capability bought on Hedera and one
computed locally have to be indistinguishable to it, because the moment a
provider can influence selection by being that provider, the layer has stopped
being economic. Naming any provider, network, or payment system inside the core
model is a boundary violation.

### How a winner is picked

For each candidate, the existing arithmetic is unchanged — what the improvement
is worth, minus what it costs. A candidate is only in the running if it fits the
budget, actually improves the odds, and is worth more than it costs.

Among those that qualify, the one with the **highest value after subtracting its
price** wins. Exact ties fall to the **cheaper** candidate, and if prices are
identical too, to the alphabetically first identifier.

The second rule is not arbitrary: two candidates delivering the same net value
differ only in how much budget they consume doing it, and the cheaper one leaves
more for whatever comes next. The third exists purely so the answer is never
ambiguous, and carries no economic meaning at all.

**If nothing qualifies, the answer is STOP** — and so it is if the task is
already done. Stopping remains a correct outcome, not a failure.

### Three rules that exist to make the loop stop

Added when the open questions below were settled, and all three are required.

**Nothing free is for sale.** Every candidate must cost something. Free or local
actions are simply not purchasable capabilities, so every purchase leaves less
budget than before.

**Each offer can be taken once.** Once a specific candidate has been bought, that
exact offer is off the table for the rest of the run. But the *kind* of thing it
was can be offered again once the situation has changed — a run can buy a second
opinion, learn something from it, and then buy another. The rule enforces this
purely by identifier; it has no idea that two candidates are "the same sort of
thing", and deliberately must not acquire one.

**There is a hard limit on how many things a run may buy.** Every run carries a
maximum number of purchases, and on reaching it the answer is STOP — whatever
the budget says, however good the offers look. The demonstration sets this to
**four**. That is a setting, not a law of the product, and the specification
forbids writing the number into the rule.

The third one matters most because it is the only safeguard that does not depend
on the other two being implemented correctly.

### Where the starting number comes from

Every comparison is measured against the current chance of success. That number
is **not** something the user types, and **not** a free "do nothing" option
competing with the rest. It is a fact about where the task has got to, handed to
the decision:

```
the user's task → a first attempt, and an assessment of it → the current state
  → this decision
```

Producing that state is somebody else's job — a separate layer, specified
separately, authorized separately. This task receives the number.

## 6. What goes into the system

Unchanged: a task, what success is worth, the maximum spend, constraints, and a
success condition.

New at each decision: **the set of candidates on offer**, **the current chance
of success** to measure them against, **how much budget is left**, and **how
many purchases this run has already made** against its limit.

Where that candidate set comes from is deliberately not this task's problem.
Finding out what is for sale is a separate concern from deciding what is worth
buying.

## 7. What the system decides

One thing: **which candidate to buy next, or to stop.**

It does **not** decide how to execute the purchase. Selection and execution are
separated on purpose — a later task may make execution a local function call, an
HTTP request, or a paid API purchase, and none of that may reach back into the
rule that chose.

## 8. What comes out

No output changes today, because nothing is built.

The specification does fix what the eventual record must show, and one point in
it matters more than the rest: **the record must include the candidates that
were rejected**, with each one's price, claimed improvement, and the reason it
did not qualify.

A record showing only what was bought cannot answer why the alternatives were
not, and this repository already requires every economic decision to be
inspectable after the fact.

## 9. How it can fail

The three open questions this specification originally named have since been
answered by the product owner and frozen into it. §12 records what they were and
what was decided — kept rather than deleted, because the answers only make sense
against the problems.

The failure mode the document guards hardest against is subtler: **a rule that
quietly stops being about economics.** If a provider's name ever enters the
decision — as a field, a special case, or a tie-break — then Radhanite is
choosing suppliers rather than choosing value, while still describing itself as
an economic layer. The review notes require a reviewer to check for that
specifically, including in test names and comments.

## 10. Tests run and their results

```
$ python3.12 -m unittest discover -q
Ran 242 tests in 0.10s
OK
```

**242 passing, unchanged.** No test could have been affected — this pull request
contains no code. The suite was run to confirm the repository is still green.

The specification defines **seventeen acceptance criteria** for whoever
eventually implements it, including the awkward ones: zero candidates, a
candidate worth exactly what it costs, two candidates that tie perfectly, and a
proof that shuffling the candidate list changes nothing.

## 11. Assumptions made

- **The delivered two-tier behaviour survives.** With one candidate, the new
  rule reduces to the old one, so the existing scenarios should decide
  identically. The specification treats this as a claim to be **demonstrated by
  test**, not assumed — and says outright that if the demonstration fails, the
  compatibility claim is withdrawn rather than qualified.
- **The candidate set is supplied, not discovered.** Where it comes from is out
  of scope.
- **All the numbers are still made up.** Every probability is a declared
  fixture. A candidate list looks like a market, which makes it tempting to
  present its figures as market data; they are numbers someone typed.

## 12. Known limitations

### The three open decisions, and how they were settled

The first version of this specification could not be implemented: three
questions had no answers. They are recorded here with their resolutions, because
the answers are hard to judge without the problems.

**Where does the first probability come from?** — *Resolved.* It is an **input**,
supplied by the layer that ran the first attempt and assessed it. Not a user
input, and not a free "do nothing" candidate. Building that layer is a separate,
unauthorized piece of work; this task simply receives the number.

**Can the same capability be bought twice?** — *Resolved.* **A specific offer is
single-use; the kind of thing is repeatable once the situation changes.** Buying
a second opinion, learning from it, and then buying another is allowed. Buying
the identical offer twice on identical terms is not. Enforced by identifier
alone, so the rule never learns to group candidates by type.

**What guarantees the loop ever stops?** — *Resolved*, and this was the serious
one. Budget depletion alone was not a proof: a free candidate that improved the
odds would be bought forever without ever exceeding budget. Three safeguards now
close it — nothing free is purchasable, an offer cannot be taken twice, and a
hard ceiling on the number of purchases stops the run regardless of budget. The
ceiling holds even if the other two were implemented wrongly.

### What is still true

- **The candidate set is supplied, not discovered.** Where offers come from is
  out of scope, as is the layer that establishes the task state.
- **All the numbers are still made up.** Every probability is a declared
  fixture.
- **Compatibility with the delivered system is near-total, not total.** The
  positive-cost rule means a hypothetical free escalation could be expressed
  under the old model and cannot under this one. Every scenario the repository
  actually contains is unaffected, and the specification states the exception
  rather than claiming compatibility it does not have.

## 13. Explicitly out of scope

No integration, no provider discovery, no payment or wallet logic, no real
pricing, no learned estimates, no supplier-diligence rules, no interface. No
change to how a task's state or evidence evolves beyond supplying the one number
the decision needs.

**And no implementation of TASK-006 itself.** This pull request specifies it.

## 14. Deferred to future tasks

Everything the specification describes. The three open decisions are now
settled, so what remains is **authorization** — a separate act, and one this
pull request does not perform. `BL-13` and TASK-006 stay **SPECIFIED —
UNAUTHORIZED**.

Execution of a selected capability is a different task again, as is the run-record
schema that would carry the new figures.

## 14a. A note on merge order

This branch is built on top of **PR #17**, not on `main`. The specification
refers to sections of `ARCHITECTURE.md` and `PREREQ-001` that exist only on that
branch. **PR #17 should merge first**; merging this one first would leave
pointers to sections that are not there.

## 15. How to explain this to a judge

> Right now our system can ask one question: *should I pay for the better
> option?* One better option, yes or no.
>
> That is not the real problem. The real problem is: *here are five things I
> could buy, at five different prices, each claiming to help by a different
> amount — which one, if any?*
>
> This document specifies that decision exactly. Rank everything that fits the
> budget and is worth more than it costs, take the best value for money, and if
> nothing clears the bar, stop and say so.
>
> The part we care most about is what the rule is **not** allowed to know: who
> is selling. Price and effect, nothing else. The moment a provider's name can
> tip a decision, you have a procurement preference dressed up as economics.
>
> And we haven't built it. Writing it down surfaced three questions we couldn't
> answer — including one where the loop provably never terminates if a
> capability is free. We answered them before writing any code: nothing free is
> for sale, an offer can be taken once, and there is a hard cap on how many
> things a run may buy, independent of the budget.
>
> Finding that in a document is cheap. Finding it in a demo is not.
