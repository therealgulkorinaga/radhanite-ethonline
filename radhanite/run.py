"""The economic loop, and the record of what it did.

TASK-001 §5 deliverable 1, §2.6, and acceptance criteria 1, 12 and 14.

The loop is deliberately thin. Every part of it was built and reviewed
separately, and this only arranges them:

    select a strategy the budget can afford        (§2.2)
    ask whether buying it is economically justified (§2.5)
    execute it                                      (§2.3)
    judge the result against the success condition  (§2.4)
    repeat, or stop

**Every purchase is weighed before it is made**, including the first. There is
no free opening attempt: buying the first attempt raises the chance of success
from nothing to whatever that strategy declares, which is exactly the question
§2.5's rule answers. A task worth a penny does not get a two-penny attempt
merely because it is the first one.

**Moving to a dearer strategy is weighed by the same rule.** When a strategy is
exhausted, the question "is the next, dearer strategy worth buying?" is the same
economic question as "is escalating worth it?" — how much would this purchase
improve the chance of success, and is that worth more than it costs. The rule
authorized in §2.5 is applied unchanged rather than a second rule being invented
for the purpose.

**The budget is spent through a ledger that refuses to go below zero.** The
money type deliberately permits negative amounts, so it cannot catch an
overspend; the review of PR-006 noted that a running balance would have to
enforce this itself, and this is where that happens.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from radhanite._immutable import refuse_rehydration
from radhanite.escalation import Decision, EscalationDecision, decide
from radhanite.evaluation import Evaluation, evaluate
from radhanite.execution import Attempt, ScriptedSimulator
from radhanite.money import CURRENCY, Money
from radhanite.probability import Probability
from radhanite.strategy import Strategy, select
from radhanite.task import Task

__all__ = ["RunOutcome", "RunRecord", "Step", "run"]

#: Before anything has been attempted, the chance of success is nothing.
_NOTHING_ATTEMPTED = Probability("0")


class RunOutcome(Enum):
    """How a run ended.

    Stopping is a **correct outcome**, not a failure — PREREQ-001 §5.4. An agent
    that refuses to keep spending on work not worth the money has done its job.
    """

    SUCCEEDED = "succeeded"
    STOPPED = "stopped"


class _Ledger:
    """The remaining budget, which cannot go below zero.

    `Money` permits negative amounts by design, because §2.5's expected-value
    arithmetic needs them. That means it cannot catch an overspend, and the
    PR-006 review recorded that a running balance would have to enforce the
    ceiling itself. This is that balance.
    """

    __slots__ = ("_budget", "_spent")

    def __init__(self, budget: Money) -> None:
        if budget.is_negative:
            raise ValueError(f"A budget cannot be negative, got {budget}.")
        self._budget = budget
        self._spent = Money("0")

    @property
    def spent(self) -> Money:
        return self._spent

    @property
    def remaining(self) -> Money:
        return self._budget - self._spent

    def spend(self, amount: Money) -> None:
        if amount.is_negative:
            raise ValueError(f"Cannot spend a negative amount, got {amount}.")
        if amount > self.remaining:
            # Criterion 12: the ceiling is never exceeded. Reaching here means
            # something bought what it had already been told it could not
            # afford, which is a fault rather than an outcome.
            raise RuntimeError(
                f"Spending {amount} would exceed the budget: only "
                f"{self.remaining} remains of {self._budget}."
            )
        self._spent = self._spent + amount


@refuse_rehydration
@dataclass(frozen=True, slots=True)
class Step:
    """One purchase considered, and what came of it.

    A step always has a decision. It has an attempt and an evaluation only if
    that decision was to spend — which is what makes the record show *why* every
    purchase happened, and why the run stopped when it did.
    """

    number: int
    strategy_name: str
    escalating: bool
    decision: EscalationDecision
    attempt: Attempt | None = None
    evaluation: Evaluation | None = None

    @property
    def bought(self) -> bool:
        return self.attempt is not None

    def __str__(self) -> str:
        stage = "escalate" if self.escalating else "start"
        if not self.bought:
            return f"{self.number}. {self.strategy_name} ({stage}) — {self.decision.reason}"
        return (
            f"{self.number}. {self.strategy_name} ({stage}) — "
            f"{self.decision.reason} → {self.attempt.observation.note} → "
            f"{self.evaluation.reason}"
        )


@refuse_rehydration
@dataclass(frozen=True, slots=True)
class RunRecord:
    """Everything that happened, and why.

    TASK-001 §2.6 requires a record from which every decision can be recomputed,
    and PREREQ-001 §8 requires that every economic decision be inspectable after
    the fact. Each step carries the decision that produced it, with all of the
    quantities that decision was made from.
    """

    task: Task
    outcome: RunOutcome
    steps: tuple[Step, ...]
    spent: Money
    remaining: Money
    reason: str

    @property
    def succeeded(self) -> bool:
        return self.outcome is RunOutcome.SUCCEEDED

    def as_dict(self) -> dict:
        """The whole run, as plain data.

        Every quantity that went into a decision is present, so any decision can
        be recomputed from the record alone — which is what §2.6 requires and
        what makes PREREQ-001 §8's inspectability real rather than claimed.

        Amounts and probabilities are written as strings. Writing them as JSON
        numbers would hand them to a reader's floating-point parser, and an
        amount that arrives slightly wrong is exactly the failure the money type
        exists to prevent.
        """
        return {
            "task": {
                "description": self.task.description,
                "budget": str(self.task.budget.amount),
                "task_value": str(self.task.task_value.amount),
                "currency": CURRENCY,
                "constraints": list(self.task.constraints),
                "success_condition": self.task.success_condition,
            },
            "outcome": self.outcome.value,
            "reason": self.reason,
            "spent": str(self.spent.amount),
            "remaining": str(self.remaining.amount),
            "steps": [_step_as_dict(step) for step in self.steps],
        }

    def write(self, path: str | Path) -> Path:
        """Write the record as JSON, creating the directory if needed."""
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(self.as_dict(), indent=2) + "\n", encoding="utf-8"
        )
        return destination

    def __str__(self) -> str:
        lines = [f"{self.task.description}", f"  budget {self.task.budget}, worth {self.task.task_value}"]
        lines += [f"  {step}" for step in self.steps]
        lines.append(f"  {self.outcome.value.upper()}: {self.reason}")
        lines.append(f"  spent {self.spent} of {self.task.budget}, {self.remaining} unspent")
        return "\n".join(lines)


def _step_as_dict(step: Step) -> dict:
    decision = step.decision
    record = {
        "number": step.number,
        "strategy": step.strategy_name,
        "escalating": step.escalating,
        "decision": {
            "verdict": decision.decision.value,
            "reason": decision.reason,
            "failed_conditions": [c.value for c in decision.failed_conditions],
            # Everything §2.5's rule was applied to, so it can be recomputed.
            "current_success_probability": str(decision.current_success_probability.value),
            "post_escalation_success_probability": str(
                decision.post_escalation_success_probability.value
            ),
            "task_value": str(decision.task_value.amount),
            "escalation_cost": str(decision.escalation_cost.amount),
            "remaining_budget": str(decision.remaining_budget.amount),
            "incremental_expected_value": str(
                decision.incremental_expected_value.amount
            ),
        },
        "attempt": None,
        "evaluation": None,
    }
    if step.attempt is not None:
        record["attempt"] = {
            "cost": str(step.attempt.cost.amount),
            "success_probability": str(step.attempt.success_probability.value),
            "achieved": sorted(step.attempt.observation.satisfied),
            "note": step.attempt.observation.note,
        }
    if step.evaluation is not None:
        record["evaluation"] = {
            "verdict": step.evaluation.verdict.value,
            "success_condition": step.evaluation.success_condition,
            "reason": step.evaluation.reason,
        }
    return record


def run(
    task: Task,
    strategies: Sequence[Strategy],
    simulator: ScriptedSimulator,
) -> RunRecord:
    """Attempt a task until it succeeds or is not worth continuing.

    Returns a record of every decision, whether or not the task was completed.
    A run that stops without succeeding is not an error: it is the system
    declining to spend more on something not worth it.
    """
    if not isinstance(task, Task):
        raise TypeError(f"task must be a Task, got {type(task).__name__}.")

    ledger = _Ledger(task.budget)
    achieved = _NOTHING_ATTEMPTED
    untried = list(strategies)
    steps: list[Step] = []

    while untried:
        strategy = select(untried, ledger.remaining)
        if strategy is None:
            return _finish(
                task, RunOutcome.STOPPED, steps, ledger,
                f"Nothing affordable remains: {ledger.remaining} left, and no "
                "untried strategy costs that little.",
            )
        untried.remove(strategy)

        # The opening attempt, weighed like any other purchase.
        step, achieved, succeeded = _consider(
            task, strategy, escalating=False, achieved=achieved,
            ledger=ledger, simulator=simulator, number=len(steps) + 1,
        )
        steps.append(step)
        if succeeded:
            return _finish(task, RunOutcome.SUCCEEDED, steps, ledger, step.evaluation.reason)

        if step.bought:
            # Escalating within the same strategy.
            step, achieved, succeeded = _consider(
                task, strategy, escalating=True, achieved=achieved,
                ledger=ledger, simulator=simulator, number=len(steps) + 1,
            )
            steps.append(step)
            if succeeded:
                return _finish(task, RunOutcome.SUCCEEDED, steps, ledger, step.evaluation.reason)

        # A refusal ends this strategy, not the run. A dearer strategy may still
        # be worth buying: the rule weighs each purchase on its own merits, and
        # the cheapest option being a bad buy says nothing about the others.
        # Stopping here would leave money unspent on a task still worth
        # finishing, which is the opposite of the mistake §2.5 guards against.

    return _finish(
        task, RunOutcome.STOPPED, steps, ledger,
        "Every strategy has been tried or refused; none of what remains is "
        f"worth buying, and {ledger.remaining} of the budget is unspent.",
    )


def _consider(
    task: Task,
    strategy: Strategy,
    *,
    escalating: bool,
    achieved: Probability,
    ledger: _Ledger,
    simulator: ScriptedSimulator,
    number: int,
) -> tuple[Step, Probability, bool]:
    """Weigh one purchase, and make it if the rule says so."""
    cost = strategy.escalation_cost if escalating else strategy.initial_cost
    offered = (
        strategy.escalated_success_probability
        if escalating
        else strategy.initial_success_probability
    )

    decision = decide(
        current_success_probability=achieved,
        post_escalation_success_probability=offered,
        task_value=task.task_value,
        escalation_cost=cost,
        remaining_budget=ledger.remaining,
    )
    if decision.decision is Decision.STOP:
        return Step(number, strategy.name, escalating, decision), achieved, False

    ledger.spend(cost)
    attempt = simulator.execute(strategy, escalated=escalating)
    evaluation = evaluate(attempt, task.success_condition)
    step = Step(number, strategy.name, escalating, decision, attempt, evaluation)
    return step, offered, evaluation.succeeded


def _finish(
    task: Task,
    outcome: RunOutcome,
    steps: list[Step],
    ledger: _Ledger,
    reason: str,
) -> RunRecord:
    return RunRecord(
        task=task,
        outcome=outcome,
        steps=tuple(steps),
        spent=ledger.spent,
        remaining=ledger.remaining,
        reason=reason,
    )
