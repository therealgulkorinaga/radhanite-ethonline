# PR-017 — Radhanite decides what is worth buying, not how much inference to buy

**Pull request:** #17
**Authority:** prerequisite amendment to `PREREQ-001`, authorized by the human product owner
**Author:** Claude Code, under human product owner authorization

---

## 1. Purpose of this PR

To change what Radhanite **is**, in writing, in the documents that decide it —
and to do that without pretending the change has already been built.

Radhanite used to be defined as a layer that decided *how much inference to
buy*. It is now defined as a layer that decides *which external capability is
worth acquiring next, if any*.

**Nothing is built by this pull request. No product code changed. No integration
became authorized.** Every file in it is documentation.

## 2. What changed

| File | What it is |
|---|---|
| `docs/PREREQ-001_PRODUCT_DEFINITION.md` | The definition of the product itself — the new statement, what a "skill" is, the demonstration |
| `docs/ARCHITECTURE.md` | What is built today versus where it is going, kept strictly apart; new rules about telling the truth |
| `tasks/BACKLOG.md` | Which future work the pivot does and does not carry forward |
| `tasks/TASK-002` … `TASK-005` | One note each: written before the pivot, preserved, not automatically still next |
| `README.md` | Corrections — it was saying things that are no longer true |
| `docs/pr_explanations/PR-017_...md` | This document |

Nine files. No `.py` file. The test count is unchanged at 242.

## 3. Why the change was needed

### The old framing

Radhanite was *"an economic control layer for autonomous AI agents"* that
*"allocates inference expenditure across the task."* The decision it made was
essentially: **is a stronger model worth the money?**

### Why that stopped being enough

Inference is only one of the things an autonomous agent can buy. It can also buy
research, a second opinion, verification, structured analysis, specialist data,
or a human's review. All of those are priced. All of them can change whether a
task succeeds.

A layer that reasons only about model spend **cannot choose between them** — and
choosing between them is the economically interesting problem. The old framing
had quietly narrowed the product to one row of a much wider table.

### The new framing

> Radhanite is the economic control layer for autonomous work. A user gives an
> autonomous agent a task, a declared task value, a maximum autonomous spend,
> constraints, and a success condition. Radhanite decides which external
> capability — which **skill** — is economically worth acquiring next, if any.

And the sentence that separates it from everything else being built right now:

> **Payment infrastructure answers "How can the machine pay?"**
> **Radhanite answers "Should the machine pay, and what is worth buying?"**

A great deal of excellent work is going into the first question — wallets,
stablecoins, payment protocols, agent-payable endpoints. None of it answers the
second. An agent that can pay but cannot decide is a spending limit with extra
steps.

## 4. How this worked before

The repository described a product built around **inference expenditure**, and
contained a working implementation of a **two-tier** economic loop:

- one opening attempt, at a declared cost, with a declared chance of success;
- one optional escalation, dearer, with a better declared chance;
- a rule deciding whether that escalation was worth buying;
- and a stop, when it was not.

That loop is real, it is merged, and 242 tests cover it.

## 5. How it works after

**The running code is identical.** Not one line changed.

What changed is the description of what the code is *part of*, and an explicit
statement of where it falls short of the new definition. `ARCHITECTURE.md` §2.2
now has two clearly separated halves:

| | |
|---|---|
| **§2.2.1 — implemented** | The two-tier model. Deterministic. Exactly two tiers. `initial_*` → `escalated_*`. This is what runs |
| **§2.2.2 — direction only** | Provider-neutral candidate capabilities. Potentially many candidates, not one escalation. Selection driven by what the task currently is. **Not implemented** |

§2.2.2 carries an explicit warning that **nothing in it describes code that
exists.**

### What TASK-001 still means, and why it was not rewritten

`TASK-001` is the specification of the two-tier loop that was actually
delivered. It was **not** edited to match the new product direction, and this
was deliberate.

Rewriting it would have produced a document claiming that dynamic skill
acquisition was specified in the first place, reviewed in the first place, and
delivered in the first place. **None of that is true.** Fourteen review passes
and forty-two corrected findings were spent on the loop as it was actually
specified, and a rewritten specification would have made that record
unreadable — and the repository would have been lying about its own history.

So the old framing is preserved rather than deleted, in `PREREQ-001` §6.4 and
§2.3. A reader who wants to understand why the code looks the way it does can
still find the definition it was built against.

### Why the generalization did not happen in this PR

The two-tier model cannot honestly express "choose one of five candidates."
Forcing it to would make the recorded costs and probabilities describe something
that did not happen.

Changing the model changes what *escalation means*, and therefore changes the
economic policy — the actual product. That is `BL-13`, and the architecture
already required it to be its own authorized task rather than something that
arrives inside a sponsor integration. **This PR does not relax that rule. It
strengthens it.**

## 6. What goes into the system

Unchanged: a task, its declared value, a maximum autonomous spend, constraints,
and a measurable success condition. Five inputs, as before.

Two things were made explicit:

- **Budget is permission to spend, not a target to spend.** A run that succeeds
  having spent a fraction of its budget has not underperformed.
- **Task value is still never derived from budget.** These are two independent
  facts and the gap between them is where Radhanite operates.

## 7. What the system decides

The list of responsibilities gained a fifth entry and one was renamed:

1. **Capability selection** — which skill to acquire (was "execution-strategy selection")
2. **Expenditure allocation** — how much any one acquisition may have (was "inference expenditure allocation")
3. **Result evaluation** — unchanged
4. **The escalation-or-stop decision** — unchanged; stopping is still a success
5. **Aggregate task-budget enforcement** — new

The fifth exists because of a real problem. A single task may buy from several
**independent** environments — different chains, different accounts, no shared
state. Each environment can only see its own spending. The task's ceiling must
still hold across all of them, so it is enforced in one place, above them all.

### What a "skill" is

A skill (or capability) is **a priced external capability that may improve a
task's prospects** — its probability of success, what is known, the quality or
confidence of the result, the speed of getting there, or completion itself.

It may be reasoning, research, independent judgment, verification, execution,
data, a specialist machine service, or human review.

What makes something a skill is not what it is made of. It is that **it has a
price and it changes the task's prospects.** Nothing else about it is
Radhanite's concern.

## 8. What comes out

No change to any output, run record, or file format — no code ran differently.

The demonstration's intended output is now recorded: **`APPROVE` / `ESCALATE` /
`REJECT`** for a supplier onboarding decision.

### The ETHOnline demonstration

**Supplier onboarding and due diligence.** Should this supplier be approved,
sent to a human, or rejected — and what evidence is worth paying for in order to
answer that?

It was chosen because the economic question is unavoidable in it. Diligence
evidence is genuinely purchasable, genuinely priced, and genuinely optional.
Buying more is always possible and is not always worth it.

| Environment | Intended capability |
|---|---|
| **Hedera** | An Independent Second Opinion skill — one x402-gated service |
| **Circle Agent Marketplace** | Tavily-backed current web research |
| **Circle Agent Marketplace** | BlockRun structured analysis, *only if economically justified* |

An illustrative run: initial assessment → justify a second opinion → buy on
Hedera → new evidence → justify research → buy via Circle → optionally justify
structured analysis → success condition met → stop.

**That is one possible outcome, not a script.** A run that always makes the same
purchases in the same order demonstrates wiring, not economic reasoning, and
would falsify the product's central claim. All of these are equally correct
runs:

- stop without buying anything at all;
- stop after the Hedera second opinion;
- stop after the second opinion and the research;
- buy the structured analysis only where the economics justify it.

A capability is purchased when — and only when — the economics say so. Calling a
sponsor's service *because* it is a sponsor's service is a boundary violation.

## 9. How it can fail

The failure mode this PR is most concerned with is **not a crash. It is a
sentence that is not true.** Documents and demonstrations can overclaim in ways
code cannot, so three new violations were added to the architecture's list, and
all of them bind documents and demos as tightly as they bind code.

**Testnet value is not real value.** Arc Testnet USDC is a test fixture that
happens to be on-chain. It must never be described, totalled, or demonstrated as
production-value USDC.

**Who was paid is a fact, not an inference.** Hedera and Arc/Circle are separate
environments with separate accounts; no bridge between them is built or needed,
and no value moves between chains. And a purchase through a marketplace is a
purchase *from that marketplace*: a Circle Marketplace request backed by Tavily
must not be described as Radhanite paying Tavily directly, unless that is
factually the seller relationship in the live integration.

**Declared numbers must not be called learned ones.** Every success probability,
cost and uplift in the system is a **declared benchmark fixture** — a number
someone typed so the loop could be exercised. They must never be described as
learned, measured, inferred from historical performance, or estimated at
runtime. They stay fixtures until a learning system is separately authorized and
actually exists.

## 10. Tests run and their results

```
$ python3.12 -m unittest discover -q
Ran 242 tests in 0.09s
OK
```

**242 passing, unchanged.** No test was added, removed, or modified — this PR
contains no code. The suite was run to confirm the repository is still green,
not because anything in it could have moved.

That exact command is now written into `README.md`. It was previously
undocumented in any authoritative file: it appeared only inside historical PR
explanations, which are records rather than instructions.

## 11. Assumptions made

- **The pivot is the product owner's decision, and is final.** It was
  authorized explicitly. This PR records it; it does not argue it.
- **Preserving history beats tidiness.** Old framings are marked as superseded
  rather than deleted, even where that leaves the documents longer.
- **The named services are intended, not verified.** Hedera's second-opinion
  service, Tavily research and BlockRun analysis are recorded as *intended*
  capabilities. No integration was tested, and none is authorized.

## 12. Known limitations

- **The definition is now ahead of the implementation, deliberately.**
  `PREREQ-001` describes capability selection; the code does two fixed tiers.
  That gap is stated in `PREREQ-001` §9 and `ARCHITECTURE.md` §2.2.2 rather than
  hidden, but it is real and it is the largest thing in the repository.
- **`TASK-002` through `TASK-005` are now of uncertain relevance.** They were
  written under the old definition. They are preserved unaltered, marked as
  predating the pivot, and their dependency chain is explicitly **not**
  automatically authorized to proceed. Which integration is genuinely next is an
  open decision for the product owner.
- **The demonstration has no implementation of any kind.** Not a stub, not a
  scaffold, not a dependency.
- **Historical review records and old PR explanations were not touched**, so
  they still speak in the old framing. That is intended: they are records of what
  was true when written.

## 13. Explicitly out of scope

This PR authorizes **none** of the following, and none of it exists:

`BL-13` strategy generalization · task-state implementation · skill runtime
interfaces · Hedera integration · Circle integration · Tavily integration ·
BlockRun integration · OpenRouter implementation · Privy implementation

Also unchanged and still unauthorized: real repository execution (`BL-07`), a
live test-suite success signal (`BL-08`), any learning from history (`BL-05`,
`BL-06`), and implementing a vertical beyond software engineering (`BL-11`) —
the demonstration's *direction* is settled, its implementation is not.

## 14. Deferred to future tasks

**The next technical step is specifying and authorizing `BL-13`** — generalizing
the strategy model from two fixed tiers to candidate capabilities. Everything in
the new product definition that the current code cannot express is waiting
behind it.

That deliberately did not happen here. A product direction being agreed is not
permission to build what it implies, and the same rule that stopped the
generalization arriving inside a sponsor integration also stops it arriving
inside the PR that made it necessary.

## 15. How to explain this to a judge

> Everyone in this space is building the plumbing for machines to pay each
> other — wallets, stablecoins, payment protocols. That plumbing answers *"how
> can the machine pay?"*
>
> Nobody is answering *"should it?"*
>
> Radhanite is that layer. You give an agent a task, what success is worth, and
> the most it may spend. Radhanite decides what capability is worth buying next
> to get there — a second opinion, some research, an expert analysis — and when
> to stop buying. Stopping early with money unspent is a correct answer, not a
> failure.
>
> What's running today is the economic engine: it decides, with exact
> arithmetic, whether the next purchase is worth its price against the value of
> the outcome. What's next is letting it choose between many different kinds of
> capability instead of two fixed tiers.
>
> And we'll tell you exactly which half is which. That line is written into the
> architecture document, because a repository that blurs what it built with what
> it plans isn't worth reading.
