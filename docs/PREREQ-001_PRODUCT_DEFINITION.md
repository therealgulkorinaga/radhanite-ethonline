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

## 6. The ETHOnline demonstration

The primary demonstration is **supplier onboarding and due diligence**: deciding
whether a prospective supplier should be approved, escalated to a human, or
rejected — and deciding what evidence is economically worth buying in order to
answer that.

The user supplies the five inputs of §4:

```
Task:              Assess prospective supplier for onboarding
Task value:        the declared economic value of a correct decision
Max autonomous spend: the ceiling the agent may not exceed
Constraints:       what it may and may not do
Success condition: the completion contract in §6.5
```

**Target output: `APPROVE` / `ESCALATE` / `REJECT`.**

**The recommendation is the output. It is not the success condition.** Whether
a supplier *should* be approved is a judgement, and §4.5 requires a success
condition evaluable without human judgment. What is machine-checkable is whether
the run produced a **complete, evidence-linked, in-budget** decision — the
deterministic completion contract in **§6.5**.

This vertical is chosen because the economic question is unavoidable in it.
Diligence evidence is genuinely purchasable, genuinely priced, and genuinely
optional — buying more is always possible and is not always worth it. That is
precisely the decision Radhanite exists to make.

### 6.1 Intended external capabilities

| Environment | Capability |
|---|---|
| **Hedera** | An **Independent Second Opinion** skill — one x402-gated service |
| **Circle Agent Marketplace** | **Tavily-backed** current web research |
| **Circle Agent Marketplace** | **BlockRun** structured analysis, *only if economically justified* |

**None of these integrations is authorized.** This section records intended
direction; building any of it requires its own authorized task.

### 6.2 An illustrative path

One economically coherent run might go:

```
initial assessment
  → economically justify a second opinion
  → purchase on Hedera
  → new task state, new evidence
  → economically justify research
  → purchase via Circle / Tavily
  → optionally justify structured analysis (BlockRun)
  → success condition met
  → STOP
```

### 6.3 This is not a hard-coded sponsor sequence

**The path in §6.2 is one possible outcome, not a script.** A run that always
performs the same purchases in the same order is a demonstration of wiring, not
of economic reasoning, and would falsify the product's central claim.

All of the following are **valid, correct Radhanite runs**:

- stop without buying anything at all;
- stop after the Hedera second opinion;
- stop after the second opinion and the research;
- buy the structured analysis **only** where the economic rule justifies it.

A capability is purchased when — and only when — the economics say it is worth
buying. Any implementation in which a sponsor's service is called because it is
a sponsor's service has violated §5.4 and `ARCHITECTURE.md` §1.

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
binary, machine-checkable and impossible to negotiate with. The supplier
diligence vertical must meet the same bar — §4.5 is unchanged, and a success
condition that needs a human to interpret it is still not a Radhanite task.

Real repository execution and a live test-suite signal remain unauthorized
(`BL-07`, `BL-08`), exactly as before.

### 6.5 The machine-checkable success condition

§4.5 requires a success condition evaluable **without human judgment**. "A
defensible recommendation" is not one: defensibility is exactly the judgement
§4.5 excludes. The demonstration's success condition is therefore a
**deterministic completion contract**, checked by field and state validation
rather than by reading the recommendation.

**A run is complete when all six hold:**

1. **Exactly one** allowed recommendation has been produced, from the closed
   set `APPROVE` | `ESCALATE` | `REJECT`. Zero is incomplete; two is invalid.
2. **Every required evidence category** defined by the demonstration fixture
   carries exactly one status from the closed set `resolved` | `unresolved` |
   `not_found`. A category with no status is incomplete.
3. **Every material claim** in the recommendation is linked to at least one
   evidence record, **or** is explicitly marked `unresolved`. An unlinked,
   unmarked claim fails the contract.
4. **No required material evidence gap is silently omitted.** A gap must appear
   as a record with a status, per clause 2 — absence is not a way of passing.
5. **Either** the run's declared confidence threshold is met, **or** the
   recommendation is `ESCALATE` *because* a material unresolved evidence gap
   remains. Escalating to a human on an unresolved gap is a pass, not a failure.
6. **Total autonomous spend ≤ the task budget.** The §4.2 ceiling, unchanged.

Every clause is a check on **fields and states**, not on the quality of a
judgement. Two runs reaching opposite recommendations on the same evidence can
both satisfy the contract, and that is correct: Radhanite is not being evaluated
on whether the supplier was in fact creditworthy. It is being evaluated on
whether it bought the right evidence, linked what it claimed, and stopped inside
its budget.

**Confidence is a declared fixture.** The threshold in clause 5, and any
confidence figure compared against it, are declared benchmark values — numbers
someone typed so the contract can be exercised. They are **not** measurements,
and nothing here asserts that a confident recommendation is a correct one.
Describing them otherwise is a boundary violation under
[`ARCHITECTURE.md`](ARCHITECTURE.md) §6 item 12.

### 6.6 Two framings, and the status of each

This document contains two use cases, and they are at different stages. Neither
supersedes the other by being mentioned later.

| | Implemented V1 | ETHOnline demonstration |
|---|---|---|
| **Vertical** | Autonomous software engineering | Supplier onboarding / due diligence |
| **Where** | §6.4, [`TASK-001`](../tasks/TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md) | §6, §6.5 |
| **Success condition** | The repository's tests pass | The completion contract, §6.5 |
| **Status** | **Implemented and merged.** The delivered two-tier deterministic kernel | **Frozen direction. Not implemented** |
| **Authorization** | Authorized; delivered | **Not authorized** |

Three statements, and all three are true at once:

1. **TASK-001 was built under the software-engineering framing**, remains
   implemented, and remains historically authoritative for TASK-001. It is what
   runs today.
2. **Supplier onboarding is the frozen primary ETHOnline demonstration
   direction.** It is not implemented, and appearing in this document does not
   authorize it. A product definition states what Radhanite *is*; it is never
   permission to build — §9.
3. **It remains subject to implementation authorization**, including the
   `BL-11` vertical boundary where that applies. `BL-11` is neither retired nor
   completed by this document.

**Radhanite is not a supplier-compliance product.** Supplier diligence is a
vertical chosen to demonstrate the economic layer, in the same way software
engineering was. The product is §1, and §7 still governs what Radhanite is not.

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
