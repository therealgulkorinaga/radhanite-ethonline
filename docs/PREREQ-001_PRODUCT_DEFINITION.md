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

**Radhanite is an economic control layer for autonomous AI agents.**

A user gives Radhanite a business task, budget, task value, constraints and
measurable success condition rather than a prompt. Radhanite selects an
execution strategy, allocates inference expenditure across the task, evaluates
results, and decides whether additional intelligence is economically justified.

That paragraph is the product. The rest of this document explains it and fixes
its boundaries.

## 2. The problem

Autonomous agents today are instructed with prompts and constrained by nothing.
The person operating the agent has no principled answer to three questions:

1. **How much should this task cost?** Spend is discovered after the fact.
2. **When should a stronger model be used?** Escalation is a habit, a guess, or
   a default setting — not a decision.
3. **When should the agent give up?** Agents retry until a context window, a
   rate limit, or a human's patience runs out.

The result is that inference spend is uncorrelated with task value. A trivial
task and an unsolvable task can cost the same, and neither cost was chosen.

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
The maximum economic expenditure authorized for this task. Budget is a hard
ceiling, not a hint. Radhanite may finish under budget; it may never silently
exceed it.

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

## 5. The four responsibilities

Given those inputs, Radhanite is responsible for four things.

### 5.1 Execution-strategy selection
Choosing *how* to attempt the task: what approach to use, at what capability
level, with what expected cost. Different tasks justify different strategies,
and the same task may justify a different strategy on a second attempt.

### 5.2 Inference expenditure allocation
Deciding how the budget is spent across the life of the task. Budget is not
consumed uniformly. Radhanite decides how much of the remaining budget any
single attempt is entitled to.

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

## 6. ETHOnline V1 use case

The V1 vertical is **autonomous software engineering**.

- **Input:** a coding task, a budget, a task value, and constraints.
- **Output:** successful task completion, or termination when further spend is
  not justified.
- **Objective success condition:** the repository's tests pass.

A complete V1 task looks like this:

```
Task:              Fix GitHub issue #184
Budget:            $2.00
Task value:        $20.00
Constraints:       no dependency changes
Success condition: tests pass
```

Software engineering is chosen deliberately: "the tests pass" is objective,
binary, machine-checkable, and impossible to negotiate with. It gives the
economic layer an honest signal to reason about. Verticals with softer success
conditions come later, if at all.

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

Implementation is authorized one task at a time in `tasks/`. The only currently
authorized task is
[`TASK-001`](../tasks/TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md), which builds a
deterministic, simulated version of the loop described in section 5 — with no
real model calls, no payments, and no external integrations.

System boundaries and the components Radhanite must **not** reimplement are
defined in [`ARCHITECTURE.md`](ARCHITECTURE.md).
