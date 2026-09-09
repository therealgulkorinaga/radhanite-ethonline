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

## 6. What goes into the system

Unchanged: a task, what success is worth, the maximum spend, constraints, and a
success condition.

New at each decision: **the set of candidates on offer**, and **the current
chance of success** to measure them against.

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

The specification names three ways this could go wrong, and does not pretend any
of them is settled. They are in §12.

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

**Three product decisions are unresolved, and implementation cannot start
without them.** They are recorded as unresolved rather than guessed at.

**Where does the first probability come from?** Every comparison is relative to
the current chance of success. At the very first decision nothing has been
attempted, and the specification does not say what that number is. The old model
never had to answer this, because there was always an opening attempt to measure
from.

**Can the same capability be bought twice?** Buying two independent second
opinions is a reasonable thing to want. So is the intuition that once you have
acquired a capability you have it. The answer determines whether the candidate
set changes as a run proceeds, which is structural rather than a detail.

**What guarantees the loop ever stops?** The old model stopped because there
were only two tiers. Now termination rests entirely on the budget shrinking with
every purchase — and **that argument breaks for anything priced at zero.** A
free candidate that improves the odds would be chosen, and then be equally
eligible on identical terms, forever.

That last one is the reason this is a specification and not an implementation.
It was found by writing the rule down carefully, which is exactly what writing
it down is for.

## 13. Explicitly out of scope

No integration, no provider discovery, no payment or wallet logic, no real
pricing, no learned estimates, no supplier-diligence rules, no interface. No
change to how a task's state or evidence evolves beyond supplying the one number
the decision needs.

**And no implementation of TASK-006 itself.** This pull request specifies it.

## 14. Deferred to future tasks

Everything the specification describes. It becomes buildable when the product
owner resolves the three open decisions in §12 and authorizes the work — two
separate acts, in that order.

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
> And we haven't built it. Writing it down surfaced three questions we can't
> answer yet — including one where the loop provably never terminates if a
> capability is free. Those are in the document, unresolved, rather than
> discovered halfway through implementation.
