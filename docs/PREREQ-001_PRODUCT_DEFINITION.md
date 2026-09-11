# PREREQ-001 — Product Definition

**Status:** Authoritative
**Type:** Prerequisite (must be agreed before any implementation task)
**Owner:** Human product owner
**Supersedes:** Nothing

This document defines what Radhanite is. Every task in `tasks/` must be
traceable to something stated here. If an implementation cannot be justified by
this document, it is out of scope.

---

## 1. Statement of the product

**Radhanite is the economic control layer for autonomous work.**

A user gives an autonomous agent a task, a declared task value, a maximum
autonomous spend, constraints, and a success condition. Radhanite decides which
external capability — which **skill** — is economically worth acquiring next, if
any, in order to complete the task.

That paragraph is the product. The rest of this document explains it and fixes
its boundaries.

### 1.1 The distinction that defines the product

> **Payment infrastructure answers "How can the machine pay?"**
> **Radhanite answers "Should the machine pay, and what is worth buying?"**

A great deal of work is going into the first question — wallets, stablecoins,
payment protocols, agent-payable endpoints. That work is necessary, and
Radhanite does not duplicate any of it. It makes the second question urgent
without answering it.

An agent that can pay and cannot decide is a spending limit with extra steps.
Radhanite is the layer above the payment rail that decides whether a purchase is
worth making at all, and stops when nothing further is.

## 2. The problem

Autonomous agents today are instructed with prompts and constrained by nothing.
The person operating the agent has no principled answer to three questions:

1. **How much should this task cost?** Spend is discovered after the fact.
2. **When should more capability be bought?** Escalation is a habit, a guess, or
   a default setting — not a decision.
3. **When should the agent give up?** Agents retry until a context window, a
   rate limit, or a human's patience runs out.

The result is that inference spend is uncorrelated with task value. A trivial
task and an unsolvable task can cost the same, and neither cost was chosen.

### 2.1 Who this is for

**Historical/current TASK-001 V1 framing — autonomous software engineering:**

| | Who |
|---|---|
| **User** | Engineering teams operating autonomous coding agents. |
| **Operator** | The person responsible for deploying and supervising those agents — an engineering lead, AI platform engineer, developer-tooling owner, or equivalent. |
| **Buyer** | Engineering or AI-platform leadership accountable for both agent performance and inference spend — a CTO, VP Engineering, Head of AI Platform, or equivalent owner. |

The operator runs the agents day to day. The buyer answers for what they cost
and whether they worked. Radhanite exists because those two concerns are
currently unconnected.

**The problem they have is not that inference is expensive.** Expense is fine
when the outcome is worth it. The problem is that these teams have no
*task-level economic control layer* — nothing that decides how much intelligence
an autonomous coding agent should purchase to reach a measurable engineering
outcome within a finite budget.

Without one, spend cannot be tied to completed engineering outcomes, and teams
fail in both directions: over-spending on premium inference where it changes
nothing, or under-spending and lowering task-completion quality. Neither failure
is visible until the money is already gone.

**Beyond V1**

Radhanite is intended to generalize beyond software engineering, to
organizations deploying autonomous agents across business workflows. Over time
those agents may purchase inference, tools, data, compute, and specialist
machine services in order to achieve measurable business outcomes.

The buyer widens accordingly: CTO, CIO, Head of AI, AI-platform leadership,
FinOps and AI FinOps, and business-unit owners accountable for the economics of
autonomous work.

This records intended direction, not authorization. **Nothing in this section
is authorized**, and neither is the demonstration direction in §6 — see §6.6 for
what is implemented, what is merely frozen direction, and what is authorized.

### 2.2 Why this matters now: agents that pay

The problem in §2 has existed for as long as agents have. What changes it from a
budgeting annoyance into a control problem is that **agents are beginning to hold
wallets and pay for things themselves** — inference, tools, data, compute, and
services offered by other agents.

Once an agent can pay, three things stop being hypothetical:

1. **Every purchase is a decision somebody has to be accountable for**, made
   without a human present at the moment it happens.
2. **Spending is no longer bounded by an invoice arriving later.** It is bounded
   by whatever the agent decides, or by nothing.
3. **"Can I afford it?" and "is it worth it?" come apart.** A wallet answers the
   first. Nothing answers the second.

An agent with a wallet and no answer to the second question is a spending limit
with extra steps. It will exhaust its balance on work that was never worth
finishing, and stop short of work that was, and in both cases the money is gone
before anyone knows.

Radhanite is the layer that answers the second question. That is why the input
contract in §4 carries **task value** alongside budget, and why §5.4's decision
is an economic judgement rather than a spending check. It is also why the
measurable success condition in §4.5 is not optional: an agent that pays for
outcomes must be able to tell whether it got one.

Making the agent an actual payer — rather than a decider about someone else's
money — is specified in
[`TASK-004`](../tasks/TASK-004_AGENTIC_PAYMENTS_VIA_HEDERA_AND_X402.md) and is
not authorized.

### 2.3 From buying inference to buying capability

This document previously defined the product as the allocation of **inference
expenditure** — deciding how much model capability to purchase. That framing is
now too narrow, and §1 has been changed accordingly.

The reason is that inference is only one of the things an autonomous agent can
buy. Research, verification, independent judgment, structured analysis,
specialist data, and human review are all purchasable, all priced, and all
capable of changing whether a task succeeds. A layer that reasons only about
model spend cannot decide between them, and deciding between them is the
economically interesting problem.

**This is a change of direction, not a rewriting of history.** Two facts are
recorded here so that neither is later misread:

1. [`TASK-001`](../tasks/TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md) specified and
   delivered a **two-tier, inference-oriented** economic loop: one opening
   attempt and one optional escalation, with declared costs and declared success
   probabilities. That is what was built, what was reviewed, and what runs
   today.
2. TASK-001 **did not** specify dynamic skill acquisition, and must never be
   described as though it did. Its specification stands unaltered as the record
   of the delivered implementation.

The generalization from two fixed tiers to a set of candidate capabilities is a
change to the economic policy itself. It is `BL-13`, it is unauthorized, and
[`ARCHITECTURE.md`](ARCHITECTURE.md) §2.2 governs it.

## 3. The shift in the unit of instruction

The core idea of Radhanite is a change in what the user hands to the system.

| | Prompt-driven agents | Radhanite |
|---|---|---|
| **User supplies** | A prompt | A task, a budget, what success is worth, constraints, and a success condition |
| **Value of success** | Unknown to the system | Declared by the user, and decisive |
| **System optimizes** | Response quality | Outcome achieved per unit of spend |
| **Termination** | Context, rate limit, or human intervention | An economic decision |
| **Success is judged by** | A human reading output | An objective, measurable condition |

A user does not tell Radhanite *how* to do the work. A user tells Radhanite
*what must become true*, *what that outcome is worth*, *what it may spend to
make it true*, and *what it may not do along the way*.

Stated as a sentence:

> Give Radhanite a task, what success is worth, how much it may spend, and the
> constraints it must obey.

## 4. The five inputs

Every Radhanite task is defined by exactly five things.

```
task + budget + task_value + constraints + success condition
```

### 4.1 Business task
What the user wants accomplished, stated as work rather than as instructions to
a model.

### 4.2 Budget
The maximum economic expenditure authorized for this task — the agent's maximum
autonomous spend. Budget is a hard ceiling, not a hint. Radhanite may finish
under budget; it may never silently exceed it.

> **Budget is permission to spend, not a target to spend.**

A run that reaches the success condition having spent a fraction of the budget
has not underperformed, and a run that stops early with most of the budget
unspent has not failed. Consuming an authorized budget is never itself a
measure of success.

### 4.3 Task value
The economic value to the user of **successfully completing** the task. It is
declared by the user, explicitly, as a first-class input.

Budget and task value are fundamentally different quantities and must never be
conflated or derived from one another:

| | Meaning | Role in the decision |
|---|---|---|
| **Budget** | The maximum the agent is *allowed to spend* | A hard ceiling |
| **Task value** | What successful completion is *worth* | The thing spend is weighed against |

**Without both, Radhanite cannot make a genuine economic decision.** A budget
alone answers only "may I afford this?" — never "is this worth buying?". Value
is what converts a spending limit into an economic judgment, and it is the
reason Radhanite is a control layer rather than a rate limiter.

Task value must not be derived from budget. A user who authorizes $2.00 of spend
on a $20.00 outcome is expressing two independent facts, and the gap between
them is precisely where Radhanite operates.

### 4.4 Constraints
Boundaries on how the work may be performed — what may be touched, what may not,
and any limits on time, scope, or method.

### 4.5 Measurable success condition
An objective, machine-checkable statement of what "done" means. It must be
evaluable without human judgment. If success cannot be measured, Radhanite
cannot make economic decisions about it, and the task is not a Radhanite task.

## 4a. What Radhanite buys: skills

A **skill** — used interchangeably with **capability** — is a *priced external
capability that may improve a task's prospects*. Concretely, it may improve any
of:

- the **probability of success**,
- the **information state** (what is known),
- the **quality** of the result,
- the **confidence** in the result,
- the **speed** of reaching it, or
- the **completion** of the task outright.

Skills are not limited to model inference. They may include reasoning,
research, independent judgment, verification, execution, data, specialist
machine services, and human review.

What makes something a skill is not what it is made of. It is that **it has a
price and it changes the task's prospects**. Those two properties are what the
economic decision needs, and nothing else about a capability is Radhanite's
concern.

### 4a.1 Providers sit beneath the economic layer

Skills are supplied by external providers, over external payment networks.
**Those providers and networks sit beneath Radhanite, not beside it.** Radhanite
decides *whether* and *what* to buy; a provider supplies it; a payment network
settles it.

> **No provider, sponsor, or payment integration may redefine Radhanite's core
> economic domain model.**

An integration adapts a provider to Radhanite's model of a priced capability. If
an integration would require the domain model to change shape, that is a product
decision for the human product owner in this document — never something an
integration settles on its way past. This is the same principle as
[`ARCHITECTURE.md`](ARCHITECTURE.md) §6 item 7, applied to the product
definition rather than to code.

### 4a.2 One task, one budget, many environments

A single task may purchase capabilities across **several independent service and
payment environments**, which need not share a chain, a currency rail, or an
account.

**Radhanite enforces one aggregate task budget above all of them.** The ceiling
in §4.2 is a property of the task, not of any one account or environment. An
environment that cannot see the others is not a reason for the ceiling to be
enforced anywhere but in one place.

## 5. The five responsibilities

Given those inputs, Radhanite is responsible for five things.

### 5.1 Capability selection
Choosing *how* to attempt the task: which capability to acquire, at what
expected cost, given what the task currently is. Different tasks justify
different choices, and the same task may justify a different choice once an
attempt has changed what is known.

### 5.2 Expenditure allocation
Deciding how the budget is spent across the life of the task. Budget is not
consumed uniformly. Radhanite decides how much of the remaining budget any
single acquisition is entitled to.

### 5.3 Result evaluation
Checking outcomes against the measurable success condition. Evaluation is
objective — it reports what happened, not what the system hoped happened.

### 5.4 The escalation-or-stop decision
After each attempt, Radhanite decides one of:

- **Succeeded** — the success condition is met; stop and report.
- **Escalate** — additional or more capable intelligence is economically
  justified; spend more.
- **Stop** — further spend is not economically justified; terminate and report
  honestly that the task was not completed.

**Stopping is a first-class successful behavior of the system.** An agent that
correctly refuses to keep spending on an unwinnable task has done its job. This
must never be treated as a failure mode to be engineered away.

### 5.5 Aggregate task-budget enforcement
Holding the ceiling in §4.2 across everything the task buys, from wherever it
buys it. Where §5.2 decides how much any one acquisition may have, this is the
guarantee that the total cannot be exceeded — including when purchases are made
in several environments that cannot see each other's spending, per §4a.2.

## 6. The ETHOnline benchmark

The current benchmark is **autonomous revenue opportunity pursuit**: an agent
pursuing a deal it could win, deciding what evidence and judgement are worth
buying on the way.

```
Opportunity        a $50,000 crypto-native infrastructure contract
Operating budget   $250
Available          research, onchain intelligence, specialist analysis,
                   independent review — each priced, each optional
Question           what should it spend next, if anything, to raise the
                   probability of winning?
```

**Target output:** exactly one of **`PURSUE`** / **`ABANDON`** / **`ESCALATE`**,
reached having spent what the opportunity justified and no more.

**The outcome is the output. It is not the success condition** — §4.5 requires
one evaluable without human judgment, and whether a deal *should* be pursued is
a judgement. What is machine-checkable is the deterministic completion contract
in **§6.5**.

### 6.0 Why this benchmark

Because the economic question is unavoidable in it, and because it makes the
failure mode visible.

**A large opportunity does not justify spending badly.** A $50,000 contract and
a $250 budget look like permission to buy everything available — and an agent
that does has made no economic decision at all. The benchmark is designed so
that **poor execution strategy destroys margin even when the opportunity is
large**, which is exactly the thing nobody currently measures.

Unused budget is **retained margin**, not a shortfall. §4.2's rule — budget is
permission to spend, not a target — is the whole point rather than a caveat.

### 6.1 Where capabilities come from

Three external layers sit **beneath** Radhanite. None of them decides anything.

| Layer | What it supplies |
|---|---|
| **Circle / Arc** | Marketplace and service discovery, machine-readable capability descriptors and prices, agent wallet and gateway infrastructure, and settlement over x402 or Nanopayments |
| **The Graph** | Live onchain commercial intelligence — protocol activity, chain and stablecoin usage, treasury and adoption signals, contract relationships |
| **Hedera** | One paid independent specialist: a structured second opinion on the current assessment |

> **Circle tells the agent what it can buy and how to pay. The Graph and Hedera
> are things it can buy. Radhanite decides what is worth buying.**

Marketplace services — Tavily-backed research, BlockRun analysis — are
**candidates**, discovered and evaluated. **None is a mandatory step**, and a run
that rejects all of them is a correct run.

**None of these integrations is authorized.** TASK-010, TASK-011 and TASK-012
specify them; specification is not permission.

### 6.2 The order is not fixed

The same engine must produce different sequences from different evidence:

| | |
|---|---|
| **Onchain first** | A cheap onchain signal is decisive — buy it, then stop |
| **Research first** | The opportunity is off-chain; research earns its price first |
| **Deep pursuit** | Several capabilities as the probability climbs |
| **Abandon cheaply** | Early evidence discourages — stop, having spent almost nothing |

### 6.3 This is not a hard-coded sponsor sequence

**A run that always makes the same purchases in the same order demonstrates
wiring, not economic reasoning**, and would falsify the product's central claim.

All of these are correct runs: buying nothing at all; buying one capability and
stopping; buying several; rejecting a marketplace service on price. A capability
is purchased when — and only when — the economics say so, and any implementation
calling a sponsor's service *because* it is a sponsor's service has violated §5.4
and `ARCHITECTURE.md` §1.

### 6.3a Supplier onboarding — the previous benchmark

Before this section was rewritten, the benchmark was **supplier onboarding and
due diligence**: approve, escalate to a human, or reject, deciding what evidence
was worth buying to answer that.

It is preserved here rather than deleted, because documents committed while it
was current refer to it and a reader should be able to tell which framing they
are looking at. It was never implemented, and nothing was lost by moving on.

The reasoning that chose it holds for the current benchmark too — evidence that
is genuinely purchasable, genuinely priced and genuinely optional. What revenue
pursuit adds is a **margin** to destroy, which makes bad economic behaviour
visible rather than merely wasteful.

**The completion contract in §6.5 is unchanged** and applies to the current
benchmark: the recommendation is the output, never the success condition.

### 6.4 The software-engineering framing, and what it was

Before this section was rewritten, the V1 vertical was **autonomous software
engineering**, with "the repository's tests pass" as the success condition:

```
Task:              Fix GitHub issue #184
Budget:            $2.00
Task value:        $20.00
Constraints:       no dependency changes
Success condition: tests pass
```

That framing is what
[`TASK-001`](../tasks/TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md) was specified and
built against, and it is preserved here rather than deleted, because the
delivered implementation is only intelligible against it.

It was chosen for a good reason that still holds: "the tests pass" is objective,
binary, machine-checkable and impossible to negotiate with. The current
benchmark must meet the same bar — §4.5 is unchanged, and a success
condition that needs a human to interpret it is still not a Radhanite task.

Real repository execution and a live test-suite signal remain unauthorized
(`BL-07`, `BL-08`), exactly as before.

### 6.5 The machine-checkable completion contract

§4.5 requires a success condition evaluable **without human judgment**. "A
defensible decision" is not one: defensibility is exactly the judgement §4.5
excludes. The benchmark's success condition is therefore a **deterministic
completion contract**, checked by field and state validation rather than by
reading the outcome.

#### The terminal outcome set

Exactly one of three, defined narrowly:

| | |
|---|---|
| **`PURSUE`** | Benchmark evidence and state are sufficient to continue the commercial pursuit under the benchmark's success threshold |
| **`ABANDON`** | The opportunity should no longer receive autonomous pursuit spend under the benchmark state |
| **`ESCALATE`** | A material unresolved condition prevents autonomous completion and requires an external or human decision |

**These are benchmark outcomes, not predictions.** `PURSUE` does not assert the
deal will be won, and `ABANDON` does not assert it was unwinnable. Radhanite
does not forecast real-world sales outcomes and no document may say it does.

#### A run is complete when all nine hold

1. **Exactly one** terminal outcome has been produced, from the closed set
   `PURSUE` | `ABANDON` | `ESCALATE`. Zero is incomplete; two is invalid.
2. **Every required benchmark state field** defined by the benchmark fixture is
   accounted for. A required field with no value is incomplete.
3. **Every material unresolved question is explicitly represented**, not
   silently omitted. Absence is not a way of passing — an unknown must appear as
   an unknown.
4. **The current success probability is represented** according to the
   benchmark's fixture and state contract.
5. **Total capability spend is within the operating budget.** The §4.2 ceiling,
   unchanged.
6. **No execution occurred beyond the hard capability-step ceiling.**
7. **No consumed candidate ID was reused.**
8. **The terminal reason is deterministic** — which of the four terminal states
   ended the run, and why.
9. **The run record is sufficient to audit why Radhanite stopped**, including
   the candidates it considered and rejected.

Every clause checks **fields and states**, not the quality of a judgement. Two
runs reaching opposite outcomes on the same evidence can both satisfy the
contract, and that is correct: Radhanite is not evaluated on whether the
opportunity was in fact winnable. It is evaluated on whether it **bought the
right evidence, represented what it did not know, and stopped inside its
budget.**

**This contract is not the economic rule.** Clauses 5 to 7 restate constraints
TASK-006 and TASK-007 already enforce; the contract checks that a completed run
satisfied them, and decides nothing itself. Selection remains
[`TASK-006`](../tasks/TASK-006_GENERALIZED_CAPABILITY_SELECTION.md)'s and is
untouched by anything here.

**Probabilities and thresholds are declared fixtures.** The success threshold in
the `PURSUE` definition, and any probability compared against it, are declared
benchmark values — numbers someone typed so the contract can be exercised. They
are **not** measurements, estimates or predictions, and remain so unless a
separately authorized task owns learned estimation. Describing them otherwise is
a boundary violation under [`ARCHITECTURE.md`](ARCHITECTURE.md) §6 item 12.

#### The previous contract

The supplier benchmark used `APPROVE` | `ESCALATE` | `REJECT` over evidence
categories carrying `resolved` | `unresolved` | `not_found`. That contract
belongs to the framing in §6.3a and is **historical**. Its shape survives here —
a closed outcome set, explicit representation of what is unknown, and spend
inside the ceiling — because the shape was right and only the vocabulary was
supplier-specific.

### 6.6 Two framings, and the status of each

This document contains two use cases, and they are at different stages. Neither
supersedes the other by being mentioned later.

| | Implemented V1 | ETHOnline benchmark |
|---|---|---|
| **Vertical** | Autonomous software engineering | Revenue opportunity pursuit |
| **Where** | §6.4, [`TASK-001`](../tasks/TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md) | §6, §6.5 |
| **Success condition** | The repository's tests pass | The completion contract, §6.5 |
| **Status** | **Implemented and merged.** The delivered two-tier deterministic kernel | **Frozen direction. Not implemented** |
| **Authorization** | Authorized; delivered | **Not authorized** |

Three statements, and all three are true at once:

1. **TASK-001 was built under the software-engineering framing**, remains
   implemented, and remains historically authoritative for TASK-001. It is what
   runs today.
2. **Revenue opportunity pursuit is the current ETHOnline benchmark.** It is not implemented, and appearing in this document does not
   authorize it. A product definition states what Radhanite *is*; it is never
   permission to build — §9.
3. **It remains subject to implementation authorization**, including the
   `BL-11` vertical boundary where that applies. `BL-11` is neither retired nor
   completed by this document.

**Radhanite is not a sales product.** Revenue pursuit is a vertical chosen to
demonstrate the economic layer, in the same way software engineering and supplier
diligence were. The long-term product is broader than sales: Radhanite manages
the unit economics of autonomous work. The product is §1, and §7 still governs what Radhanite is not.

## 7. What Radhanite is not

Stating this precisely prevents scope drift.

- **Not an agent framework.** It does not compete with agent-authoring tools.
- **Not an inference provider.** It does not serve models or reimplement model
  routing infrastructure.
- **Not a prompt optimizer.** It does not improve prompts; it decides how much
  intelligence to purchase.
- **Not an evaluation harness.** It consumes an objective success signal; it
  does not exist to produce benchmarks.
- **Not an autonomy maximizer.** More autonomy is not the goal. Correct economic
  decisions are the goal, and one correct decision is to stop.
- **Not a marketplace.** It does not list, host, rank, or broker capabilities for
  sale. It buys from marketplaces that already exist.
- **Not a model router.** It does not choose providers for a given model call, or
  balance traffic across them.
- **Not a wallet.** It holds no keys and issues no authority. See
  [`ARCHITECTURE.md`](ARCHITECTURE.md) §3.2.
- **Not an x402 router.** It does not implement, proxy, or route a payment
  protocol.
- **Not a cross-chain payment product.** It moves no value between chains and
  requires no bridge. See `ARCHITECTURE.md` §4b.
- **Not a procurement marketplace.** It decides what is worth buying for one
  task; it is not a purchasing platform, a vendor catalogue, or a spend-management
  suite.

The first five entries name things Radhanite must not *become*. The last six name
things it must not be *mistaken for* — every one of them sits either above or
below Radhanite in the stack, and none of them answers the question in §1.1.

## 8. Success criteria for the product

Radhanite is working if, for a given task, budget, task value, constraints, and
success condition:

1. It reaches the success condition when the task is achievable within budget.
2. It terminates, without exhausting the budget, when the task is not
   economically worth continuing.
3. Every economic decision it made can be inspected and explained after the
   fact.

The third criterion is as important as the first two. An economic control layer
whose decisions cannot be audited is not a control layer.

## 9. Relationship to implementation

This document describes the product. It does not authorize any implementation.

Implementation is authorized one task at a time in `tasks/`.

**Delivered:** [`TASK-001`](../tasks/TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md) —
a deterministic, simulated version of the loop in §5, with no real model calls,
no payments, and no external integrations. It implements the **two-tier** model
described in §2.3, not the capability selection of §5.1.

**Not implemented, and not authorized by this document:** everything else on
this page. In particular, §4a's skills, §5.5's cross-environment enforcement and
§6's demonstration describe the product direction; none of them describes code
that exists. The generalization of the strategy model that §5.1 would require is
`BL-13`, and [`ARCHITECTURE.md`](ARCHITECTURE.md) §2.2 requires it to have its
own authorized task rather than arriving inside an integration.

A statement in this document is a decision about what Radhanite **is**. It is
never permission to build it.

System boundaries and the components Radhanite must **not** reimplement are
defined in [`ARCHITECTURE.md`](ARCHITECTURE.md).
