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

### 2.2 Capability selection
Choosing how a unit of work is attempted — which capability to acquire, at what
declared expected cost.

Two things are described below and they must never be confused. One is running
code. The other is a direction that has been agreed and not built.

#### 2.2.1 Current implemented architecture — TASK-001

**What runs today is the two-tier model merged in TASK-001, and it remains
authoritative for the implementation.**

- **Deterministic** — identical inputs produce an identical choice.
- **Exactly two tiers** — an opening attempt and one optional escalation.
- Shaped as `initial_cost` / `initial_success_probability` →
  `escalation_cost` / `escalated_success_probability`.
- §2.5's escalation rule is defined against precisely that shape.

Every acceptance criterion in TASK-001, every field in the run record documented
in [`RUN_RECORDS.md`](RUN_RECORDS.md), and all 242 tests are written against
this model. It is the delivered product.

#### 2.2.2 Authorized migration direction — not implemented

The product definition has moved from allocating inference spend to deciding
which **capability** to acquire — [`PREREQ-001`](PREREQ-001_PRODUCT_DEFINITION.md)
§2.3 and §4a. The architecture that direction implies is:

- **provider-neutral candidate capabilities**, rather than tiers of one kind of
  thing;
- **potentially N candidate actions** at a decision point, rather than exactly
  one escalation;
- **task-state-driven selection** — what is worth buying next depends on what
  the previous purchase revealed;
- **dynamic skill acquisition** across independent environments.

> **The kernel described above is implemented. A working generalized runtime is
> not.** Those are different claims and this section keeps them apart.

**What exists** — `radhanite/capability.py`, `eligibility.py`, `selection.py`,
`policy.py`:

- the **candidate model**, three fields, provider-neutral;
- the **eligibility rule**, all six conditions of TASK-006 §2.3;
- **deterministic ranking and selection**, §2.4's three levels, order-independent;
- **declared candidate fixtures**, a benchmark catalogue of three;
- **run policy**, carrying the purchase ceiling with no default;
- **compatibility tests** demonstrating that TASK-001's scenarios decide
  identically under the generalized rule.

**What does not exist.** The generalized kernel **is not driving the runtime**.
`python -m radhanite` still runs TASK-001's two-tier loop, which has not been
replaced and is still what §2.2.1 describes. There is no run loop over
capabilities: nothing accumulates spend across purchases, nothing re-evaluates
task state between them, and nothing decides that a task has already succeeded.
That orchestration is **unauthorized and unimplemented** — `BL-16`.

**An implemented kernel is not a working autonomous runtime**, and no document
in this repository may imply otherwise.

That specification now exists:
[TASK-006](../tasks/TASK-006_GENERALIZED_CAPABILITY_SELECTION.md) defines the
model — current task state, zero or more candidate capabilities, deterministic
economic selection, execute or STOP — together with the ranking rule, the
provider-neutrality constraint, and how TASK-001's two tiers remain
representable under it. Its open product decisions were resolved — the baseline
success probability is an input from the task-state layer, candidate offers are
single-use while capability types may recur, and termination is guaranteed by a
positive-cost invariant, single-use IDs, and a hard capability-step ceiling
independent of budget.

**TASK-006 is authorized and its kernel is implemented; the task is not closed.**
Two of its acceptance criteria have no owner inside it — TASK-006 §5a. Until a
run loop exists, §2.2.1 still describes what actually runs.

#### 2.2.3 The generalization requires its own authorized task

This rule is unchanged and is not relaxed by the product pivot.

Moving from §2.2.1 to §2.2.2 changes what escalation *means*, and therefore
changes the economic policy itself. **It requires its own authorized task —
`BL-13` — and must not arrive inside a provider or sponsor integration.**

Until that task exists and is authorized, capabilities that the two-tier model
cannot represent honestly are **not to be approximated by it**. Forcing a
one-shot, a parallel workflow, or an N-candidate choice into an
initial-plus-escalation shape would make the recorded costs and probabilities
describe something other than what happened.

`BL-13` is specified as
[TASK-006](../tasks/TASK-006_GENERALIZED_CAPABILITY_SELECTION.md), and the human
product owner **authorized it on 2026-09-09**. Its three open product decisions
were resolved first, and authorization followed as a separate act.

**This is the second authorized implementation task in the project**, after
TASK-001, and its authorization reaches TASK-006's §2 and nothing further.
TASK-006 §3 still excludes provider discovery, payment execution, the task-state
layer, and candidate generation; §4 above is unchanged for every integration.

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
| Programmable authority over the agent, and its wallet | Privy | **Not authorized — deprioritized**, §3.2 |
| Onchain information as a purchasable capability | The Graph | **Not authorized yet** |
| Agent economic budget | Arc / USDC | **Not authorized yet** |
| Agent payments, outbound and inbound | Hedera / x402 | **Not authorized yet** |
| Capability discovery and marketplace settlement | Circle Agent Marketplace | **Not authorized yet** |

**Every system in this table sits beneath Radhanite, not beside it.** Radhanite
decides *whether* and *what* to buy; these supply it, or settle it.

> **No provider, sponsor, or payment integration may redefine Radhanite's core
> economic domain model.**

An integration adapts a provider to Radhanite's model of a priced capability. If
an integration appears to require the domain model to change shape, that is a
product decision belonging to
[`PREREQ-001`](PREREQ-001_PRODUCT_DEFINITION.md) §4a.1 and to the human product
owner — never something the integration settles on its way past. Making that
change inside an integration is a §6 item 7 violation.

### 3.1 OpenRouter — inference execution infrastructure
Intended later as the way Radhanite actually executes inference across model
providers. Radhanite must **not** reimplement model routing, provider fallback,
provider-specific clients, or inference billing.

Radhanite's job stops at deciding *what capability tier to buy and how much to
spend*. Actually purchasing and executing that inference is OpenRouter's job.

### 3.2 Privy — programmable authority over the agent *(deprioritized)*

> **Not on the active integration path.** Deprioritized 2026-09-11: Circle Agent
> Wallets and Arc cover the relevant wallet and payment infrastructure for the
> current build, so Privy would add overlap rather than a distinct economic
> capability — and wallet authorization is not Radhanite's differentiation.
> [TASK-003](../tasks/TASK-003_PROGRAMMABLE_AUTHORITY_VIA_PRIVY.md) records the
> decision in full.
>
> **The argument below is unaffected and is kept.** An agent that enforces its
> own spending limits is circular, and a refusal it cannot overrule has to come
> from outside. That remains true, remains unbuilt, and remains the reason this
> would be worth doing later. Deprioritizing work is not discovering it was
> wrong.

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

### 3.5 The Graph — onchain information Radhanite may buy

Intended later as **one capability among the candidates**, not as a component of
the decision. It would return structured onchain evidence — wallet, protocol or
entity activity — which changes what the task knows and therefore what the next
decision is measured against.

Radhanite must **not** reimplement indexing, subgraph infrastructure, or query
execution. It decides *whether the evidence is worth its price*.

**The prohibition that matters here is §2.1's, and it is not relaxed.** A
capability backed by a subgraph and one computed locally are indistinguishable
to the selection rule: same three fields, same six conditions, same ranking. No
provider earns a preference, a tie-break or a "trusted source" exemption by
identity. If onchain evidence deserves to win, it wins on price and effect.

Specified as a placeholder in
[TASK-007](../tasks/TASK-007_ONCHAIN_INFORMATION_VIA_THE_GRAPH.md), which
carries three unresolved decisions and authorizes nothing.

## 4. Integration authorization status

**No external integration is authorized at this time.**

Specifically, **none** of OpenRouter, Arc/USDC, Hedera, x402, The Graph, or
Privy is authorized in [`TASK-001`](../tasks/TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md).
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
| [TASK-005](../tasks/TASK-005_BUDGET_IN_REAL_USDC_ON_ARC.md) | The budget itself, as USDC that exists on a chain | `BL-03` |
| [TASK-004](../tasks/TASK-004_AGENTIC_PAYMENTS_VIA_HEDERA_AND_X402.md) | The agent paying for its own purchases | `BL-04` |

**None of these is authorized.** A task file specifies work; it does not permit
it. §4 above is unchanged: an integration becomes authorized only when the human
product owner says so.

### The active integration path, in priority order

Set by the human product owner on 2026-09-11. Nothing here is authorized; this
is the order work would be taken in if it were.

| | Integration | What it contributes |
|---|---|---|
| 1 | **Hedera / x402** — [TASK-004](../tasks/TASK-004_AGENTIC_PAYMENTS_VIA_HEDERA_AND_X402.md) | A paid independent-judgement capability |
| 2 | **Circle / Arc** — [TASK-005](../tasks/TASK-005_BUDGET_IN_REAL_USDC_ON_ARC.md) | The marketplace and payment environment, and research |
| 3 | **The Graph** — [TASK-007](../tasks/TASK-007_ONCHAIN_INFORMATION_VIA_THE_GRAPH.md) | A paid onchain-information capability |

**Privy is not on this path.** [TASK-003](../tasks/TASK-003_PROGRAMMABLE_AUTHORITY_VIA_PRIVY.md)
is deprioritized and records why; its specification is preserved unaltered.

All three are capabilities the agent could **buy**, which is the shape the
product definition now takes. That is the substantive difference from the
authority Privy would have supplied, and the reason for the reordering.

**This table predates the product pivot in
[`PREREQ-001`](PREREQ-001_PRODUCT_DEFINITION.md) §2.3, and its dependency chain
is not automatically authorized to proceed under the new direction.** The four
task files remain in `tasks/` as proposed specifications and historical record.
Which of them is still the right next integration — and in what order — is an
open product decision, not something inherited by default. See
[`BACKLOG.md`](../tasks/BACKLOG.md).

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

## 4b. Settlement environments are independent

The demonstration in [`PREREQ-001`](PREREQ-001_PRODUCT_DEFINITION.md) §6 buys
from more than one environment. The following are fixed, and none of them may be
blurred in a document, a run record, a demonstration, or a pull request.

1. **Hedera and Arc/Circle are independent execution and payment environments.**
   They do not share state, accounts, or balances.
2. **No bridge between them is required**, and none is built. Radhanite moves no
   value between chains — `PREREQ-001` §7.
3. **Radhanite maintains one economic task budget above the underlying execution
   accounts.** The ceiling is a property of the task, not of any account, and it
   holds across every environment the task buys from — `PREREQ-001` §4a.2, §5.5.
4. **Arc Testnet USDC is not production-value USDC** and must never be described
   as though it were. A testnet token is a test fixture that happens to be
   on-chain.
5. **A marketplace purchase is a purchase from the marketplace.** A
   Circle Marketplace request backed by Tavily must not be described as Radhanite
   paying Tavily directly, unless that is factually the seller relationship in
   the live integration. Who was actually paid is a fact to be checked, not
   inferred from whose technology answered.

Points 4 and 5 are the same rule as §6 item 8 applied to a different confusion:
value that is not real, and a payee that is not the one named.

## 5. Boundary posture for TASK-001

Because no integration is authorized, TASK-001 is built so that the economic
loop is complete and testable **without** any of them:

- Execution is **simulated** and deterministic — no real model APIs.
- Budget and task value are **internal accounting numbers**, USD-denominated
  decimals — no tokens, no transfers, and never labelled USDC.
- There is **no identity or wallet layer** — no Privy, and none of its
  successors.
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
10. Presenting **testnet value as production value**. Arc Testnet USDC — or any
    testnet token — is a test fixture that happens to be on-chain, and must
    never be described, totalled, or demonstrated as production-value USDC.
11. **Misdescribing who was paid.** Naming an upstream technology provider as
    the payee when the actual seller was a marketplace or intermediary, or
    otherwise stating a settlement relationship that was not the one that
    occurred. See §4b item 5.
12. Describing declared success probabilities, costs, or uplifts as **learned,
    measured, inferred from historical performance, or dynamically estimated at
    runtime**, when they are declared benchmark fixtures. They remain fixtures
    unless and until a learning system is separately authorized (`BL-05`,
    `BL-06`) and actually exists. This binds documents and demonstrations as
    much as code.

Items 7 through 12 are the ones that let unauthorized scope or an untrue claim
into a repository without anyone deciding to add it. Items 9 to 12 are all the
same rule as item 8, applied to a different confusion each time — outcomes
rather than money, value that is not real, a payee that is not the one named,
and a number that was typed rather than learned. Real inference producing a
plausible answer is not the same as the work having been done, and the
difference must never be blurred by a form of words.
