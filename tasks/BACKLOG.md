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

| ID | Concept | Status |
|---|---|---|
| BL-01 | Real inference execution via OpenRouter | **UNAUTHORIZED** |
| BL-02 | Wallet and permission model via Privy | **UNAUTHORIZED** |
| BL-03 | Agent budget denominated in Arc / USDC | **UNAUTHORIZED** |
| BL-04 | Radhanite exposed as a paid machine service via Hedera / x402 | **UNAUTHORIZED** |

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

## Notes

BL-05 and BL-06 are the natural successors to TASK-001's deterministic rules and
are the most likely to be built by accident. They are explicitly excluded from
TASK-001 in that task's §3, and remain unauthorized here.

BL-01 through BL-04 correspond to the systems Radhanite must never reimplement.
When they are eventually authorized, they will be integrations at the boundary —
not features Radhanite builds itself.
