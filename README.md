# Radhanite

**An economic control layer for autonomous AI agents.**

Radhanite is being built for ETHOnline 2026. This repository currently contains
governance and planning scaffolding only. No product code has been written yet.

---

## What Radhanite is

Today, using an AI agent means writing a prompt and hoping the result is worth
what it cost. Radhanite changes the unit of instruction.

A user gives Radhanite a **business task, a budget, a task value, constraints,
and a measurable success condition** — not a prompt. Radhanite then:

1. selects an execution strategy,
2. allocates inference expenditure across the task,
3. evaluates results against the success condition, and
4. decides whether additional intelligence is economically justified.

The last point is the product. Radhanite is not another agent framework; it is
the layer that decides **how much intelligence to buy, when to buy more, and
when to stop paying**.

> Give Radhanite a task, what success is worth, how much it may spend, and the
> constraints it must obey.

Budget and task value are separate inputs and neither is derived from the other.
A budget alone answers "may I afford this?" — only value answers "is it worth
buying?". That distinction is what makes the decision economic rather than a
spending limit.

The full statement of the product is in
[`docs/PREREQ-001_PRODUCT_DEFINITION.md`](docs/PREREQ-001_PRODUCT_DEFINITION.md).

## V1 use case (ETHOnline)

Autonomous software engineering.

| | |
|---|---|
| **Input** | A coding task, a budget, a task value, and constraints |
| **Output** | Successful task completion, or termination when further spend is not justified |
| **Objective success condition** | The repository's tests pass |

A complete V1 task:

```
Task:              Fix GitHub issue #184
Budget:            $2.00
Task value:        $20.00
Constraints:       no dependency changes
Success condition: tests pass
```

Tests passing is a machine-checkable, non-negotiable success signal. That is why
software engineering is the first vertical: the success condition cannot be
argued with, so the economic decisions can be evaluated honestly.

## Repository status

| Item | Status |
|---|---|
| Governance and planning scaffolding | Present |
| Product code | **None written** |
| Authorized task in progress | TASK-001 (specified, all decisions resolved, not yet implemented) |
| Language | Python 3.12 (decided; nothing written yet) |
| External integrations (OpenRouter, Privy, Arc/USDC, Hedera/x402) | **Not authorized** |

## Repository layout

```
README.md                  This file
docs/                      Product definition, architecture, rules, governance
  PREREQ-001_PRODUCT_DEFINITION.md   What Radhanite is and why
  ARCHITECTURE.md                    System boundaries and ownership
  HACKATHON_RULES.md                 ETHOnline constraints we build under
  AI_BUILD_GOVERNANCE.md             How AI agents are permitted to build here
tasks/                     Authorized work, one file per task
  TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md   The only authorized task
  BACKLOG.md                                Unauthorized future placeholders
prompts/                   Preserved AI prompts that caused repository changes
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

To be selected by the product owner before the first release. The project will
be open source, as required by ETHOnline.
