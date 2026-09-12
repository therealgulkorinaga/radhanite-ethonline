# Radhanite

**An economic control layer for autonomous AI agents.**

Radhanite is being built for ETHOnline 2026.

**TASK-001 is implemented and merged.** It remains the active CLI/runtime path:
the deterministic **two-tier economic kernel** makes an opening attempt and one
optional escalation, with declared costs and declared success probabilities.
The full suite currently passes **684 tests on Python 3.12**.

The generalized capability-selection kernel in
[TASK-006](tasks/TASK-006_GENERALIZED_CAPABILITY_SELECTION.md) is implemented but
not closed. TASK-007 PR A provides the immutable run-state foundation, and PR B
now provides the provider-neutral execution result, executor boundary, and one
execution transition on this review branch. TASK-008 PR A provides the
descriptor-to-candidate acquisition/catalog boundary. The remaining TASK-007
task-state updater, terminal classification, and full loop, TASK-008
source-specific candidate generation, the benchmark, and external adapters are
not yet implemented. The distinction between what runs, what is partially
implemented, and what is authorized to be built remains deliberate throughout
this repository.

---

## What Radhanite is

Today, using an AI agent means writing a prompt and hoping the result is worth
what it cost. Radhanite changes the unit of instruction.

A user gives Radhanite a **business task, a budget, a task value, constraints,
and a measurable success condition** — not a prompt. Radhanite then:

1. selects a capability to acquire,
2. allocates expenditure across the task,
3. evaluates results against the success condition, and
4. decides whether buying more is economically justified.

The last point is the product:

> **Payment infrastructure answers "How can the machine pay?"**
> **Radhanite answers "Should the machine pay, and what is worth buying?"**

Radhanite is not another agent framework, and not a payment rail. It is the
layer above the rail that decides **what is worth buying, when to buy more, and
when to stop paying**.

> Give Radhanite a task, what success is worth, how much it may spend, and the
> constraints it must obey.

Budget and task value are separate inputs and neither is derived from the other.
A budget alone answers "may I afford this?" — only value answers "is it worth
buying?". That distinction is what makes the decision economic rather than a
spending limit.

The full statement of the product is in
[`docs/PREREQ-001_PRODUCT_DEFINITION.md`](docs/PREREQ-001_PRODUCT_DEFINITION.md).

## ETHOnline benchmark

**Autonomous revenue opportunity pursuit** — an agent pursuing a deal it could
win, deciding what evidence and judgement are worth buying on the way.

| | |
|---|---|
| **Opportunity** | A $50,000 crypto-native infrastructure contract |
| **Operating budget** | $250 |
| **Available** | Research, onchain intelligence, specialist analysis, independent review — each priced, each optional |
| **The question** | What should it spend next, if anything, to raise the probability of winning? |

A large opportunity does not justify spending badly. The benchmark is built so
that **poor execution strategy destroys margin even when the opportunity is
large** — and unused budget is retained margin, not a shortfall.

Circle/Arc supplies discovery and payment; The Graph and Hedera are capabilities
the agent may buy. **Radhanite decides what is worth buying.** None of those
integrations is authorized, and the capability order is not hard-coded: a run
that buys nothing is a correct run. See
[`docs/PREREQ-001_PRODUCT_DEFINITION.md`](docs/PREREQ-001_PRODUCT_DEFINITION.md)
§6.

## Repository status

| Item | Status |
|---|---|
| Governance and planning scaffolding | Present |
| Product code | **Present** — TASK-001’s active runtime plus the TASK-006 kernel, TASK-007 PR A state foundation and PR B one-execution boundary, and TASK-008 PR A acquisition/catalog boundary |
| TASK-001 | **Implemented and merged.** All seventeen acceptance criteria met |
| Tests | **684 passing** on Python 3.12 |
| Language | Python 3.12, standard library only — no external dependencies |
| Capability selection engine | **Implemented** — [TASK-006](tasks/TASK-006_GENERALIZED_CAPABILITY_SELECTION.md); the task is not closed |
| TASK-007 run loop | **PR B in review** — state model, immutable snapshots, executor/result boundary, and one execution transition; updater, classification, and loop remain incomplete |
| TASK-008 acquisition | **PR A implemented** — normalization/catalog boundary; source-specific generation and adapters remain incomplete |
| Benchmark and adapters | **Specified, not implemented** — TASK-009 … TASK-014 |
| External integrations (Circle/Arc, The Graph, Hedera, OpenRouter) | **Not authorized** |
| Privy | **Deprioritized** — superseded on the active path ([TASK-003](tasks/TASK-003_PROGRAMMABLE_AUTHORITY_VIA_PRIVY.md)) |

## Running the tests

```
python3.12 -m unittest discover -q
```

Python 3.12 specifically — `pyproject.toml` pins `>=3.12,<3.13` and a test
asserts the running version, so the suite fails by design on anything else.
There is nothing to install: the project declares no third-party packages and no
build backend, and is run directly from the source tree.

## Repository layout

```
README.md                  This file
docs/                      Product definition, architecture, rules, governance
  PREREQ-001_PRODUCT_DEFINITION.md   What Radhanite is and why
  ARCHITECTURE.md                    System boundaries and ownership
  HACKATHON_RULES.md                 ETHOnline constraints we build under
  AI_BUILD_GOVERNANCE.md             How AI agents are permitted to build here
radhanite/                 The economic kernel and generalized foundations
tests/                     The test suite — 684 tests, standard library only
tasks/                     Authorized work, one file per task
  TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md   Implemented and merged
  TASK-006                                  Kernel implemented, not closed
  TASK-007                                  PR A state foundation; PR B in review
  TASK-008                                  PR A acquisition/catalog boundary implemented
  TASK-002 .. TASK-005, TASK-009 .. TASK-014 Proposed or specified, not authorized
  BACKLOG.md                                Unauthorized future placeholders
prompts/                   Preserved AI prompts that caused repository changes
site/                      The public ETHOnline progress page (§3.2)
```

## How work happens here

Radhanite is built by AI agents under human authorization. The rules are not
advisory:

- A **human product owner** authorizes tasks and performs all merges.
- **Manus** implements only tasks that have been explicitly authorized.
- Every implementation step carries the bold textual attribution
  **Implementation agent: Manus.**
- **Codex** independently reviews implementations against the specification.
- Future scope is never silently implemented. If it is not in an authorized
  task, it does not get built.

See [`docs/AI_BUILD_GOVERNANCE.md`](docs/AI_BUILD_GOVERNANCE.md) for the full
process, and [`prompts/README.md`](prompts/README.md) for how prompts are
preserved.

## Hackathon constraints

This project starts from scratch, uses version control from the first commit,
commits frequently and meaningfully, remains public, and is open source. Details
in [`docs/HACKATHON_RULES.md`](docs/HACKATHON_RULES.md).

## License

MIT. See [`LICENSE`](LICENSE). The project is open source, as required by
ETHOnline.
