# Backlog

**Status of everything in this file: UNAUTHORIZED**

This file reserves conceptual space for work that may be authorized later. It is
a list of ideas that have deliberately **not** been approved.

## Rules for this file

1. **Nothing here is authorized.** Presence in this backlog confers no
   permission to build, prototype, stub, or prepare for an item.
2. **No implementation specifications.** Entries are one-line concepts only. No
   designs, interfaces, schemas, data models, dependencies, or file layouts.
   If an entry starts to look like a spec, it has grown too far and must be cut
   back.
3. **Authorization happens elsewhere.** Work becomes authorized only when the
   human product owner creates a task file in `tasks/` naming it explicitly.
4. **No anticipatory abstraction.** Code must not be shaped in advance to
   accommodate anything on this list. See
   [`ARCHITECTURE.md`](../docs/ARCHITECTURE.md) §6.

An AI agent that implements anything from this file has violated
[`AI_BUILD_GOVERNANCE.md`](../docs/AI_BUILD_GOVERNANCE.md) §2.

---

## Integration placeholders

These four now have task files. **A task file is a specification, not an
authorization** — each remains unauthorized until the human product owner says
otherwise, exactly as `BACKLOG.md`'s rules require.

**All four predate the product pivot** recorded in
[`PREREQ-001`](../docs/PREREQ-001_PRODUCT_DEFINITION.md) §2.3, which moved the
product from allocating inference spend to deciding which capability is worth
acquiring. They are preserved as **proposed specifications and historical
record**; their substantive technical decisions are untouched.

> **Their dependency chain is not automatically authorized to proceed under the
> new product direction.**

TASK-003 depending on TASK-002, and TASK-004 on TASK-003, described an order
that assumed real inference was the first thing to make real. Under the new
direction that assumption is no longer self-evident. Which integration comes
first — and whether TASK-002 is still it — is an open product decision belonging
to the human product owner, not an order inherited by default. See
[`ARCHITECTURE.md`](../docs/ARCHITECTURE.md) §4a.

| ID | Concept | Specified in | Status |
|---|---|---|---|
| BL-01 | Real inference execution via OpenRouter | [TASK-002](TASK-002_REAL_INFERENCE_VIA_OPENROUTER.md) | **UNAUTHORIZED** |
| BL-02 | Programmable authority over the agent, via Privy | [TASK-003](TASK-003_PROGRAMMABLE_AUTHORITY_VIA_PRIVY.md) | **UNAUTHORIZED** |
| BL-03 | Agent budget denominated in real USDC on Arc | [TASK-005](TASK-005_BUDGET_IN_REAL_USDC_ON_ARC.md) | **UNAUTHORIZED** |
| BL-04 | The agent paying for its own purchases, over x402 on Hedera | [TASK-004](TASK-004_AGENTIC_PAYMENTS_VIA_HEDERA_AND_X402.md) | **UNAUTHORIZED** |
| BL-04b | Radhanite consumed as a paid machine service — the inbound direction | *(none)* | **UNAUTHORIZED** |

`BL-03` previously pointed at TASK-004, which does not mention Arc at all: the
Circle work had been folded into a paragraph of TASK-003 as an aside, so a track
being targeted had no task file, no acceptance criteria, and nothing a reader
could point at. TASK-005 owns it now. TASK-003 establishes the wallet and the
authority over it; TASK-005 makes the budget in that wallet real money.

`BL-04` previously described only the inbound direction — other machines paying
Radhanite. The outbound direction, Radhanite's agent paying for what it buys, is
the one that makes this an economic control layer for agentic payments, and it
had no entry at all. It has one now, and `BL-04b` keeps the inbound direction
recorded separately rather than letting the two blur.

## Capability placeholders

| ID | Concept | Status |
|---|---|---|
| BL-05 | Adaptive strategy selection replacing deterministic rules | **UNAUTHORIZED** |
| BL-06 | Learning from historical run records to inform allocation | **UNAUTHORIZED** |
| BL-07 | Real software-engineering execution against a live repository | **UNAUTHORIZED** |
| BL-08 | Test-suite outcome as the live success signal | **UNAUTHORIZED** |
| BL-09 | Multi-task budget allocation across a portfolio of tasks | **UNAUTHORIZED** |
| BL-10 | Human-facing UI for submitting tasks and reviewing run records | **UNAUTHORIZED** |
| BL-11 | Verticals beyond software engineering | **UNAUTHORIZED** |
| BL-12 | Several Radhanite agents under shared, externally granted authority | **UNAUTHORIZED** |
| BL-13 | Selection among candidate capabilities, rather than one attempt and one escalation — specified as [TASK-006](TASK-006_GENERALIZED_CAPABILITY_SELECTION.md) | **SPECIFIED — UNAUTHORIZED** |
| BL-14 | Radhanite hosting a paid x402 endpoint as hackathon test infrastructure | **UNAUTHORIZED** |

## Notes

BL-05 and BL-06 are the natural successors to TASK-001's deterministic rules and
are the most likely to be built by accident. They are explicitly excluded from
TASK-001 in that task's §3, and remain unauthorized here.

`BL-13` is what the intended three-strategy demonstration actually requires. A
single premium attempt has no escalation, and parallel candidates followed by
adjudication is several cheap calls and then a strong one — neither is
expressible as one attempt plus one escalation. Approximating them in the
two-tier model would make the recorded costs and probabilities describe
something other than what happened, so the model has to change first, and
changing it changes what escalation means and therefore the economic policy.
That is why it is a task of its own rather than something an integration does on
the way past.

**`BL-13` is now also what the product pivot requires.** `PREREQ-001` §5.1 and
§4a describe selecting among candidate *capabilities* — provider-neutral, N of
them, chosen against the current state of the task. The delivered two-tier model
cannot express that. `ARCHITECTURE.md` §2.2.2 records the direction; §2.2.3
requires it to arrive as its own authorized task.

**`BL-13` is now specified as
[TASK-006](TASK-006_GENERALIZED_CAPABILITY_SELECTION.md), and is still
UNAUTHORIZED.** A task file is a specification, not an authorization — the same
rule that governs TASK-002 through TASK-005 above. Rule 1 at the top of this
file is unchanged: nothing here confers permission to build.

Specifying it refined the concept. The entry above previously read *"an ordered
plan of stages"*, which was the shape the problem looked like from outside. What
the economics actually need is a **set of candidates ranked by net expected
value** — an order over options at one decision point, not a plan laid out in
advance. The row is updated to say so.

TASK-006 carried three unresolved product decisions when first specified — the
starting success probability, whether a capability may be bought twice, and what
guarantees the loop terminates. **All three are now resolved** by the human
product owner and frozen in TASK-006 §6.6–§6.8. Resolving them did not authorize
the work: the task remains **SPECIFIED — UNAUTHORIZED**, and authorization is a
separate act.

`BL-14` is distinct from `BL-04b`. `BL-04b` is Radhanite sold as a paid service —
a product direction. `BL-14` is a seller endpoint stood up only so that the
outbound purchase in TASK-004 has something real to buy from. If a bounty
requires one, it is **hackathon test infrastructure and must be represented as
such**, not allowed to become part of the product architecture by having been
built.

`BL-11` needs a note after the product pivot. `PREREQ-001` §6 now names
**supplier onboarding and due diligence** as the frozen primary ETHOnline
demonstration direction, which is a vertical beyond software engineering.

**That settles direction only.** `BL-11` covers *implementing* another vertical,
and it is:

- **not retired** — the entry stands, unchanged, above;
- **not completed** — nothing has been built against it;
- **still UNAUTHORIZED** — no execution against a real diligence workflow, no
  supplier data, no live success signal.

A product definition states what Radhanite *is*. It is never permission to build
it, and a demonstration direction appearing in `PREREQ-001` authorizes nothing —
`PREREQ-001` §6.6 and §9. `BL-07` and `BL-08` are likewise untouched.

The software-engineering framing that TASK-001 was built under is preserved in
`PREREQ-001` §6.4, and the status of both framings is tabulated in §6.6.
TASK-001 remains implemented and historically authoritative for itself.

BL-12 is distinct from `BL-09`, and the difference is worth stating. `BL-09` is
Radhanite dividing a budget across several tasks — one agent, many jobs. `BL-12`
is several agents under one grant of authority, which raises a limit no single
agent can enforce: ten agents each correctly respecting a $2 budget is $20 of
exposure nobody authorized, and none of them can see the others. It is the
strongest argument for `BL-02`'s authority layer being an external grant rather
than an internal check, and it is recorded here so that argument does not get
mistaken for permission to build a fleet.

BL-01 through BL-04 correspond to the systems Radhanite must never reimplement.
When they are eventually authorized, they will be integrations at the boundary —
not features Radhanite builds itself.
