# Radhanite

**An economic control layer for autonomous AI agents.**

Radhanite is being built for ETHOnline 2026.

**TASK-001 is implemented and merged.** What runs today is the deterministic
**two-tier economic kernel**: an opening attempt and one optional escalation,
with declared costs and declared success probabilities. **242 tests pass on
Python 3.12.**

**Dynamic capability acquisition — deciding which external skill is worth buying
next — is specified and authorized as
[TASK-006](tasks/TASK-006_GENERALIZED_CAPABILITY_SELECTION.md), and is not yet
implemented.** The distinction between what runs and what is authorized to be
built is kept deliberately sharp throughout this repository.

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

## ETHOnline demonstration

**Supplier onboarding and due diligence** — deciding whether a prospective
supplier should be approved, escalated to a human, or rejected, and deciding
what evidence is economically worth buying to answer that.

| | |
|---|---|
| **Input** | The task, its value, a maximum autonomous spend, and constraints |
| **Output** | `APPROVE` / `ESCALATE` / `REJECT`, or termination when further spend is not justified |
| **Success condition** | The deterministic completion contract in `PREREQ-001` §6.5 — *not* the recommendation itself |

Buying diligence evidence is always possible and is not always worth it, which
is exactly the decision Radhanite exists to make. A run that stops without
buying anything is a correct run.

**This demonstration is frozen direction, not implemented, and not authorized.**
The implemented V1 is still autonomous software engineering — TASK-001, merged.
Both framings and the status of each are tabulated in
[`docs/PREREQ-001_PRODUCT_DEFINITION.md`](docs/PREREQ-001_PRODUCT_DEFINITION.md)
§6.6; the earlier framing is preserved in §6.4 rather than deleted. None of the
external integrations named here is authorized either.

## Repository status

| Item | Status |
|---|---|
| Governance and planning scaffolding | Present |
| Product code | **Present** — the deterministic two-tier economic kernel |
| TASK-001 | **Implemented and merged.** All seventeen acceptance criteria met |
| Tests | **242 passing** on Python 3.12 |
| Language | Python 3.12, standard library only — no external dependencies |
| Dynamic capability acquisition | **Authorized, not yet implemented** — [TASK-006](tasks/TASK-006_GENERALIZED_CAPABILITY_SELECTION.md) (`BL-13`) |
| External integrations (OpenRouter, Privy, Arc/USDC, Hedera/x402, Circle) | **Not authorized** |

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
radhanite/                 The economic kernel (TASK-001, implemented)
tests/                     The test suite — 242 tests, standard library only
tasks/                     Authorized work, one file per task
  TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md   Implemented and merged
  TASK-002 .. TASK-005                      Proposed, none authorized
  BACKLOG.md                                Unauthorized future placeholders
prompts/                   Preserved AI prompts that caused repository changes
site/                      The public ETHOnline progress page (§3.2)
```

## How work happens here

Radhanite is built by AI agents under human authorization. The rules are not
advisory:

- A **human product owner** authorizes tasks and performs all merges.
- **Claude Code** implements only tasks that have been explicitly authorized.
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
