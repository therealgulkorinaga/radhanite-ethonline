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

## Notes

BL-05 and BL-06 are the natural successors to TASK-001's deterministic rules and
are the most likely to be built by accident. They are explicitly excluded from
TASK-001 in that task's §3, and remain unauthorized here.

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
