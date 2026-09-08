"""The economic loop, and the record of what it did.

TASK-001 §5 deliverable 1, §2.6, and acceptance criteria 1, 12 and 14.

The loop follows §2's pipeline in the order §2 gives it:

    task
      → deterministic strategy selection   (§2.2)
      → simulated execution                (§2.3)
      → outcome evaluation                 (§2.4)
      → economic escalation/stop decision  (§2.5)
      → run record                         (§2.6)

Three things about that order are load-bearing, and an earlier version of this
module got all three wrong.

**The escalation rule runs after a verdict, never before one.** §2.5 makes its
decision "from the verdict, the spend so far, and the remaining budget". Before
the opening attempt there is no verdict, so there is nothing for it to decide.
The opening attempt is selected and executed; the rule first speaks when the
first attempt has been judged.

**A Stop decision stops the run.** §2.5 says "terminate and report the task
incomplete", and PREREQ-001 §5.4 says the same. A Stop cannot be reinterpreted
as "skip this one and try another" — that would turn the rule's only refusal
into a suggestion.

**Selection chooses the next action; the rule then judges that one action.**
Because a Stop terminates, the loop must not offer the rule a candidate it means
to skip. Selection therefore picks the best next purchase available — the first,
in declared order, that is affordable and offers a better chance of success than
has already been achieved — and §2.5 rules on that single candidate.

The budget is spent through a ledger that refuses to go below zero. `Money`
permits negative amounts by design, so it cannot catch an overspend; the review
of PR-006 noted that a running balance would have to enforce this itself, and
this is where that happens.
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
    """One action the loop took, and everything behind it.

    `selection_reason` records **why this candidate** — §2.6 requires "the
    strategy chosen and why", and a record that showed only the economic verdict
    would leave a reader unable to audit how the candidate was arrived at.

    `decision` is `None` for the opening attempt only. §2.5 decides from a
    verdict, and before the first attempt there is none.
    """

    number: int
    strategy_name: str | None
    escalating: bool
    selection_reason: str
    decision: EscalationDecision | None = None
    attempt: Attempt | None = None
    evaluation: Evaluation | None = None

    @property
    def bought(self) -> bool:
        return self.attempt is not None

    def __str__(self) -> str:
        if self.strategy_name is None:
            return f"{self.number}. {self.selection_reason}"
        stage = "escalate" if self.escalating else "start"
        head = f"{self.number}. {self.strategy_name} ({stage}) — {self.selection_reason}"
        if self.decision is not None:
            head += f" — {self.decision.reason}"
        if not self.bought:
            return head
        return f"{head} → {self.attempt.observation.note} → {self.evaluation.reason}"


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
    record: dict = {
        "number": step.number,
        "strategy": step.strategy_name,
        "escalating": step.escalating,
        # §2.6 requires the strategy chosen *and why*. Without this a reader can
        # recheck the economics but cannot audit how the candidate was arrived
        # at, or what was passed over to reach it.
        "selection_reason": step.selection_reason,
        "decision": None,
        "attempt": None,
        "evaluation": None,
    }
    if step.decision is not None:
        decision = step.decision
        record["decision"] = {
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


@dataclass(frozen=True, slots=True)
class _Candidate:
    """One purchase that could be made next."""

    strategy: Strategy
    escalating: bool

    @property
    def cost(self) -> Money:
        return (
            self.strategy.escalation_cost
            if self.escalating
            else self.strategy.initial_cost
        )

    @property
    def offers(self) -> Probability:
        return (
            self.strategy.escalated_success_probability
            if self.escalating
            else self.strategy.initial_success_probability
        )

    @property
    def stage(self) -> str:
        return "escalate" if self.escalating else "start"


def _next_action(
    available: list[_Candidate], achieved: Probability, remaining: Money
) -> tuple[_Candidate | None, str]:
    """Choose what to do next, by fixed rules, and say why.

    The first candidate in declared order that is **affordable** and **offers a
    better chance than has already been achieved**.

    Both conditions belong to selection rather than to §2.5. A candidate that
    cannot be afforded, or that offers nothing new, is not a purchase the rule
    should be asked to rule on — because §2.5's Stop terminates the run, so
    offering it a candidate meant to be skipped would turn its refusal into a
    suggestion.
    """
    passed_over: list[str] = []
    for candidate in available:
        if candidate.offers <= achieved:
            passed_over.append(
                f"{candidate.strategy.name} ({candidate.stage}) offers "
                f"{candidate.offers} against {achieved} already achieved"
            )
            continue
        if candidate.cost > remaining:
            passed_over.append(
                f"{candidate.strategy.name} ({candidate.stage}) costs "
                f"{candidate.cost} and only {remaining} remains"
            )
            continue
        reason = (
            f"First in declared order that is affordable and improves on what "
            f"has been achieved: costs {candidate.cost} of {remaining} "
            f"remaining, and offers {candidate.offers} against {achieved}."
        )
        if passed_over:
            reason += " Passed over: " + "; ".join(passed_over) + "."
        return candidate, reason

    if not passed_over:
        return None, "Nothing remains untried."
    return None, "Nothing left is worth selecting. " + "; ".join(passed_over) + "."


def _cheapest(available: list[_Candidate]) -> _Candidate | None:
    return min(available, key=lambda c: c.cost.amount, default=None)


def run(
    task: Task,
    strategies: Sequence[Strategy],
    simulator: ScriptedSimulator,
    record_directory: str | Path | None = "runs",
) -> RunRecord:
    """Attempt a task until it succeeds or continuing is not worth the money.

    Writes the record as JSON into `record_directory`, which criterion 14 and
    §2.6 require of every run. Pass `None` to skip writing — used by tests that
    have no business touching the filesystem.

    A run that stops without succeeding is not an error: it is the system
    declining to spend more on something not worth it (PREREQ-001 §5.4).
    """
    if not isinstance(task, Task):
        raise TypeError(f"task must be a Task, got {type(task).__name__}.")
    if isinstance(strategies, (str, bytes)) or not isinstance(strategies, Sequence):
        # select() refuses unordered collections, but run() used to convert to a
        # list before calling it, which slipped straight past that guard: a set
        # of strategies gave a different first choice on different hash seeds.
        raise TypeError(
            "strategies must be an ordered sequence, not "
            f"{type(strategies).__name__}. Selection depends on declared order, "
            "so an unordered collection cannot produce a deterministic run."
        )

    ledger = _Ledger(task.budget)
    steps: list[Step] = []
    available = [_Candidate(strategy, False) for strategy in strategies]

    # §2's pipeline opens with selection and execution. §2.5 decides from a
    # verdict, and there is not one yet, so the rule is not consulted here.
    opening = select(list(strategies), ledger.remaining)
    if opening is None:
        steps.append(
            Step(
                1, None, False,
                f"No strategy is affordable: {ledger.remaining} remains and the "
                "cheapest costs more than that. Nothing was attempted.",
            )
        )
        return _finish(task, RunOutcome.STOPPED, steps, ledger,
                       steps[-1].selection_reason, record_directory)

    candidate = _Candidate(opening, False)
    step, achieved = _buy(task, candidate, ledger, simulator, len(steps) + 1,
                          selection_reason=(
                              f"Opening attempt: first strategy in declared order "
                              f"affordable within {ledger.remaining}. §2.5 is not "
                              "consulted before an attempt has been judged."
                          ),
                          decision=None)
    steps.append(step)
    if step.evaluation.succeeded:
        return _finish(task, RunOutcome.SUCCEEDED, steps, ledger,
                       step.evaluation.reason, record_directory)
    available = _advance(available, candidate)

    while True:
        candidate, why = _next_action(available, achieved, ledger.remaining)

        if candidate is None:
            # §2.5 must still speak when something untried remains, so that the
            # record carries the condition that ended the run rather than only
            # a sentence about it.
            fallback = _cheapest(available)
            if fallback is not None:
                decision = decide(
                    current_success_probability=achieved,
                    post_escalation_success_probability=fallback.offers,
                    task_value=task.task_value,
                    escalation_cost=fallback.cost,
                    remaining_budget=ledger.remaining,
                )
                steps.append(
                    Step(len(steps) + 1, fallback.strategy.name,
                         fallback.escalating, why, decision)
                )
                # The run's summary reason is the selection reason, which names
                # every remaining candidate and why each was unusable. The §2.5
                # decision is recorded on the step, but it speaks only about the
                # cheapest leftover and so does not explain the run's ending.
                return _finish(task, RunOutcome.STOPPED, steps, ledger, why,
                               record_directory)
            steps.append(Step(len(steps) + 1, None, False, why))
            return _finish(task, RunOutcome.STOPPED, steps, ledger, why,
                           record_directory)

        decision = decide(
            current_success_probability=achieved,
            post_escalation_success_probability=candidate.offers,
            task_value=task.task_value,
            escalation_cost=candidate.cost,
            remaining_budget=ledger.remaining,
        )
        if decision.decision is Decision.STOP:
            # §2.5: "Terminate and report the task incomplete." A Stop is not a
            # suggestion to try something else.
            steps.append(
                Step(len(steps) + 1, candidate.strategy.name,
                     candidate.escalating, why, decision)
            )
            return _finish(task, RunOutcome.STOPPED, steps, ledger,
                           decision.reason, record_directory)

        step, achieved = _buy(task, candidate, ledger, simulator,
                              len(steps) + 1, why, decision)
        steps.append(step)
        if step.evaluation.succeeded:
            return _finish(task, RunOutcome.SUCCEEDED, steps, ledger,
                           step.evaluation.reason, record_directory)
        available = _advance(available, candidate)


def _advance(available: list[_Candidate], bought: _Candidate) -> list[_Candidate]:
    """Retire a candidate, and open its escalation if it had one."""
    position = available.index(bought)
    remaining = available[:position] + available[position + 1:]
    if not bought.escalating:
        remaining.insert(position, _Candidate(bought.strategy, True))
    return remaining


def _buy(
    task: Task,
    candidate: _Candidate,
    ledger: _Ledger,
    simulator: ScriptedSimulator,
    number: int,
    selection_reason: str,
    decision: EscalationDecision | None,
) -> tuple[Step, Probability]:
    """Make the purchase, execute it, and judge the result."""
    ledger.spend(candidate.cost)
    attempt = simulator.execute(candidate.strategy, escalated=candidate.escalating)
    evaluation = evaluate(attempt, task.success_condition)
    step = Step(
        number, candidate.strategy.name, candidate.escalating,
        selection_reason, decision, attempt, evaluation,
    )
    return step, candidate.offers


def _next_record_number(directory: Path) -> int:
    existing = sorted(directory.glob("run-*.json")) if directory.exists() else []
    numbers = []
    for path in existing:
        stem = path.stem.removeprefix("run-")
        if stem.isdigit():
            numbers.append(int(stem))
    return max(numbers, default=0) + 1


def _finish(
    task: Task,
    outcome: RunOutcome,
    steps: list[Step],
    ledger: _Ledger,
    reason: str,
    record_directory: str | Path | None,
) -> RunRecord:
    record = RunRecord(
        task=task,
        outcome=outcome,
        steps=tuple(steps),
        spent=ledger.spent,
        remaining=ledger.remaining,
        reason=reason,
    )
    if record_directory is not None:
        directory = Path(record_directory)
        record.write(directory / f"run-{_next_record_number(directory):03d}.json")
    return record
