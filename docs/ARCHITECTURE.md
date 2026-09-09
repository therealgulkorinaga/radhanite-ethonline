# Architecture

**Status:** Authoritative for system boundaries
**Owner:** Human product owner

This document defines what Radhanite owns, what it must never reimplement, and
which integrations are authorized. It is a boundary document, not an
implementation design.

---

## 1. Design principle

> Radhanite owns **economic decisions**. It does not own execution
> infrastructure, identity, money movement, or settlement.

Every external system named below exists because it already solves a problem
well. Radhanite integrates with them later; it never rebuilds them. Reimplementing
any of them would be scope drift and must be rejected in review.

## 2. What Radhanite owns

These are Radhanite's responsibilities. They are not delegated to any external
system.

### 2.1 Task decomposition
Turning a business task into units of work that can be attempted, measured, and
priced.

### 2.2 Execution-strategy selection
Choosing how a unit of work is attempted — approach and capability tier — with a
declared expected cost.

**The two-tier model merged in TASK-001 is authoritative.** A strategy is an
opening attempt and one optional escalation, each with a declared cost and a
declared success probability. §2.5's rule is defined against that shape.

A richer model — an ordered plan of stages, which would express a single premium
attempt, or parallel candidates followed by adjudication — is a change to what
escalation *means*, and therefore to the economic policy itself. It requires its
own authorized task (`BL-13`) and must not arrive inside an integration.

Until then, strategies that the two-tier model cannot represent honestly are
**not to be approximated by it**. Forcing a one-shot or a parallel workflow into
an initial-plus-escalation shape would make the recorded costs and probabilities
describe something other than what happened.

### 2.3 Budget allocation
Deciding how the authorized budget is distributed across attempts. Enforcing the
budget ceiling absolutely.

### 2.4 Escalation
Deciding that a failed or insufficient attempt justifies more expenditure or
more capability, and by how much.

### 2.5 Stopping
Deciding that further expenditure is not economically justified, and terminating
the task with an honest report.

This set — decompose, select, allocate, escalate, stop — is the product. It is
the only thing Radhanite is uniquely qualified to own.

## 3. What Radhanite does not own

| Concern | Intended external system | Status |
|---|---|---|
| Inference execution | OpenRouter | **Not authorized yet** |
| Programmable authority over the agent, and its wallet | Privy | **Not authorized yet** |
| Agent economic budget | Arc / USDC | **Not authorized yet** |
| Agent payments, outbound and inbound | Hedera / x402 | **Not authorized yet** |

### 3.1 OpenRouter — inference execution infrastructure
Intended later as the way Radhanite actually executes inference across model
providers. Radhanite must **not** reimplement model routing, provider fallback,
provider-specific clients, or inference billing.

Radhanite's job stops at deciding *what capability tier to buy and how much to
spend*. Actually purchasing and executing that inference is OpenRouter's job.

### 3.2 Privy — programmable authority over the agent

Intended later for the agent's wallet, its custody, and — the part that matters
— **authority the agent cannot grant itself**: what it may spend, on what terms,
granted and enforced and revoked from outside.

Wallet creation is the least of it. Any keypair makes a wallet. What Radhanite
needs is the answer to a question its own economics cannot answer.

Radhanite decides **whether a purchase is worth the money**. That is a judgement
it makes about its own spending, enforced by a ledger it owns, inside a process
it controls. If the escalation rule is wrong, nothing outside notices. An agent
that decides its own limits has the same circularity as one that sets its own
budget.

Programmable authority closes that: a spend outside the granted scope is refused
by the wallet rather than by Radhanite's own check, and the agent cannot widen
what it was granted.

This is the principle `AI_BUILD_GOVERNANCE.md` §1.1 already applies to code —
the implementing agent may not authorize its own work — applied to money.

Radhanite must **not** implement custody, key management, or an authentication
system. It holds authority; it does not issue it.

### 3.3 Arc / USDC — the agent's economic budget
Intended later to make the budget real value rather than an internal number.
Radhanite must **not** implement token accounting, transfers, or settlement.

Specified in [TASK-005](../tasks/TASK-005_BUDGET_IN_REAL_USDC_ON_ARC.md), which
is where the prohibition in §6 item 8 is lifted — and only for values that are
genuinely USDC.

Arc is chosen for a property rather than a logo: it settles in USDC and charges
gas in USDC, so a budget, a spend and a fee are one unit. A chain charging fees
in a second token would split every cost into the price of the thing and the
price of paying for it, and "what did this task cost" would stop having a single
answer.

Until Arc is authorized, budget and task value are **USD-denominated decimal
numbers** internal to Radhanite. They must not be named, labelled, or described
as USDC. Simulated numbers are not a currency, and calling them one before real
USDC exists would misrepresent what the system does.

### 3.4 Hedera / x402 — payments, in both directions

There are two distinct features here and they were previously conflated.

**Outbound — the agent pays for what it buys.** Radhanite decides a purchase is
worth making, and the agent settles it itself, over x402, on Hedera, from its own
wallet. This is the direction that makes Radhanite an economic control layer for
*agentic payments* rather than for somebody else's spending: an agent that can
pay needs something deciding whether each purchase is justified, and that is what
Radhanite is.

**Inbound — Radhanite is itself a paid service.** Other machines pay to use
Radhanite's capability. Legitimate, and a separate feature with separate work.

Radhanite must **not** implement a payment protocol, metering rail, or settlement
layer in either direction. x402 is the protocol; Hedera is the rail. Radhanite
decides *whether* to pay and *how much*.

## 4. Integration authorization status

**No external integration is authorized at this time.**

Specifically, **none** of OpenRouter, Privy, Arc/USDC, Hedera, or x402 is
authorized in [`TASK-001`](../tasks/TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md).
Any code, dependency, configuration, credential, or network call touching them
is out of scope and must be rejected in review, regardless of how small.

Integrations become authorized only when the human product owner issues a task
file that names them explicitly. Entries in
[`BACKLOG.md`](../tasks/BACKLOG.md) are placeholders, not authorization.

## 4a. The integration phase

TASK-001 builds the economic loop with nothing real attached. Four tasks then
make it real, in an order set by what each depends on:

| Task | What becomes real | Backlog entries retired |
|---|---|---|
| [TASK-002](../tasks/TASK-002_REAL_INFERENCE_VIA_OPENROUTER.md) | Inference, and therefore the spend | `BL-01` |
| [TASK-003](../tasks/TASK-003_PROGRAMMABLE_AUTHORITY_VIA_PRIVY.md) | Authority the agent cannot grant itself, over an account on Arc | `BL-02` |
| [TASK-005](../tasks/TASK-005_BUDGET_IN_REAL_USDC_ON_ARC.md) | The budget itself, as USDC that exists on a chain | `BL-03` |
| [TASK-004](../tasks/TASK-004_AGENTIC_PAYMENTS_VIA_HEDERA_AND_X402.md) | The agent paying for its own purchases | `BL-04` |

**None of these is authorized.** A task file specifies work; it does not permit
it. §4 above is unchanged: an integration becomes authorized only when the human
product owner says so.

### Why this order, and an alternative that was rejected

The order follows dependency. Inference comes first because until it is real,
every figure a chain integration settles is one somebody typed. The account
exists before the money in it is real, and the agent pays for its own purchases
only once it has both.

An alternative was considered and **rejected**: beginning with a payment
primitive — a headless process sending real USDC through a Privy-controlled
wallet — before any economic policy or inference. It would have produced
verifiable on-chain evidence sooner.

It was rejected for two reasons. It crosses the boundary between TASK-003 and
TASK-005, collapsing *who may spend* and *what the money is* into one
undifferentiated piece of infrastructure; and it contradicts the dependency
order above. Recorded here because a rejected alternative with its reasoning is
worth more to a later reader than an order presented as inevitable.

### Five assumptions the loop makes that reality breaks

Each is named in the task that has to answer it, and each is a genuine design
question rather than a matter of wiring:

1. **Cost is known before the purchase.** A strategy declares its price, the
   ledger is charged before execution, and the escalation rule weighs that same
   figure. Real inference costs are known *after*, from tokens consumed. The
   loop needs an estimate to decide with and an actual to reconcile against —
   TASK-002 §3.
2. **A purchase cannot fail.** The loop goes: ledger permits, purchase happens,
   outcome observed. Real payments decline, time out, and settle late. *Decided
   to spend*, *paid*, and *received what was paid for* become three states the
   loop does not currently distinguish — TASK-004 §4.
3. **The budget is per-run.** Each run builds a ledger from its task's budget
   and discards it. A wallet persists and is shared, and one task can drain what
   the next needs. Allocating across tasks is `BL-09` and is not authorized —
   TASK-003 §7.4.
4. **A budget is a number; a balance is a fact.** `Task.budget` is supplied by
   the caller and fixed for the run. A USDC balance changes without asking — it
   can be topped up, drawn down by another run, or spent by anything else
   holding the wallet. A budget can also exceed it, and USDC's six decimals
   cannot express a cost that `Money` can. Deciding what happens then is not
   wiring; it determines whether a run record's total is what was decided or
   what was paid — TASK-005 §4.
5. **Every limit is self-imposed.** The ceiling holds because Radhanite's own
   code respects it. Nothing outside the agent can refuse a spend, and nothing
   stops a later change quietly raising a limit. An authority layer introduces a
   refusal the agent cannot overrule — and with it a new outcome the loop has no
   path for: the economics say buy, and authority says no — TASK-003 §2, §7.3.

None is fatal. Two are additions at the execution boundary, which is where §5
always said integrations would land. The third and fourth are genuine
differences in shape — a budget belonging to a run rather than an account, and a
number that is only a fact about the world once it is money. The fifth is the
most interesting: it is not a limitation of the code but of who the code answers
to, and it cannot be fixed from inside.

## 5. Boundary posture for TASK-001

Because no integration is authorized, TASK-001 is built so that the economic
loop is complete and testable **without** any of them:

- Execution is **simulated** and deterministic — no real model APIs.
- Budget and task value are **internal accounting numbers**, USD-denominated
  decimals — no tokens, no transfers, and never labelled USDC.
- There is **no identity or wallet layer** — no Privy.
- There is **no payable endpoint** — no Hedera, no x402.

The intent is that when integrations are later authorized, they replace
simulated pieces at the boundary without changing the economic decision logic.
This is a stated design intent, not a promise of a particular interface shape —
no abstraction is authorized to be built ahead of the task that needs it.

## 6. Boundary violations

The following are architecture violations and must fail review:

1. Any implementation of inference routing or provider clients.
2. Any implementation of custody, keys, or authentication.
3. Any implementation of token accounting, transfer, or settlement.
4. Any implementation of a payment or metering protocol.
5. Any network call to an unauthorized external service.
6. Any dependency added in anticipation of an unauthorized integration.
7. Any abstraction whose only justification is a future unauthorized task.
8. Describing simulated USD values as USDC, or otherwise presenting a simulated
   quantity as a real economic one.
9. Claiming that Radhanite fixed code, changed a repository, or passed tests,
   where no repository was modified and no test runner executed. Until real
   repository execution is separately authorized (`BL-07`), a model's output is
   **evidence within a declared scenario** and nothing more. This binds every
   document, run record, demonstration and pull request explanation, not only
   the code.

Items 7, 8 and 9 are the ones that let unauthorized scope or an untrue claim
into a repository without anyone deciding to add it. Item 9 is the same rule as
item 8 applied to outcomes rather than to money: real inference producing a
plausible answer is not the same as the work having been done, and the
difference must never be blurred by a form of words.
