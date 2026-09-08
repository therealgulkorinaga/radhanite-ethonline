"""Simulated execution.

TASK-001 §2.3: a strategy is executed against a **simulator, not a model**. The
simulator produces an outcome and a cost, and must be deterministic and
controllable so that success, failure and partial progress can each be exercised
on demand.

The simulator is a **test fixture standing in for the eventual inference
layer**. It is not a model of intelligence and must never be presented as one.
It does no work, decides nothing, and knows nothing about the task: it is told
what happens and reports it, charging the strategy's declared price.

That is the point. TASK-001 exists to prove the economic reasoning is correct
and inspectable, which requires the outcome of an attempt to be a controlled
input rather than something to be discovered. Real execution is `BL-07` in the
backlog and is unauthorized.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum

from radhanite._immutable import refuse_rehydration
from radhanite.money import Money
from radhanite.probability import Probability
from radhanite.strategy import Strategy

__all__ = ["Attempt", "Outcome", "ScriptedSimulator"]


class Outcome(Enum):
    """What an attempt turned out to have achieved.

    `PARTIAL_PROGRESS` exists because real work often ends that way, and because
    TASK-001 §2.4 requires evaluation to refuse to treat it as success. Having
    the case available is what lets that refusal be tested.
    """

    SUCCESS = "success"
    PARTIAL_PROGRESS = "partial_progress"
    FAILURE = "failure"


@refuse_rehydration
@dataclass(frozen=True, slots=True)
class Attempt:
    """One execution of a strategy, and what it cost.

    Carries everything needed to reconstruct the attempt, since TASK-001 §2.6
    requires a run record from which every decision can be recomputed.
    """

    strategy_name: str
    escalated: bool
    outcome: Outcome
    cost: Money
    success_probability: Probability

    def __str__(self) -> str:
        stage = "escalated" if self.escalated else "initial"
        return (
            f"{self.strategy_name} ({stage} attempt, {self.success_probability} "
            f"likely) cost {self.cost} and ended in {self.outcome.value}"
        )


class ScriptedSimulator:
    """Reports outcomes that were decided in advance, in order.

    Deterministic by construction: the same script produces the same outcomes,
    in the same order, every time. Nothing is inferred, sampled, or derived from
    the strategy's stated chance of success — a simulator that rolled dice
    against those probabilities would make the economic loop untestable, which
    is exactly what TASK-001 §2.3 is avoiding.

    >>> from radhanite.strategy import DECLARED_STRATEGIES
    >>> simulator = ScriptedSimulator([Outcome.FAILURE, Outcome.SUCCESS])
    >>> strategy = DECLARED_STRATEGIES[0]
    >>> simulator.execute(strategy, escalated=False).outcome
    <Outcome.FAILURE: 'failure'>
    >>> simulator.execute(strategy, escalated=True).outcome
    <Outcome.SUCCESS: 'success'>
    >>> simulator.remaining
    0
    """

    __slots__ = ("_script", "_position")

    def __init__(self, script: Sequence[Outcome]) -> None:
        if isinstance(script, (str, bytes)) or not isinstance(script, Sequence):
            raise TypeError(
                "script must be an ordered sequence of Outcome values, not "
                f"{type(script).__name__}. An unordered collection could not "
                "produce the same run twice."
            )
        for step in script:
            if not isinstance(step, Outcome):
                raise TypeError(f"script may contain only Outcome values, got {step!r}.")
        self._script: tuple[Outcome, ...] = tuple(script)
        self._position = 0

    @property
    def remaining(self) -> int:
        return len(self._script) - self._position

    def execute(self, strategy: Strategy, *, escalated: bool) -> Attempt:
        """Carry out one attempt and report what happened.

        The cost and the stated chance of success come from the strategy's
        declared figures — the initial pair, or the escalated pair. The simulator
        adds nothing of its own.
        """
        if not isinstance(strategy, Strategy):
            raise TypeError(f"strategy must be a Strategy, got {type(strategy).__name__}.")
        if self._position >= len(self._script):
            raise RuntimeError(
                "The simulator has run out of scripted outcomes. Something asked "
                f"for attempt {self._position + 1} of a script with "
                f"{len(self._script)}. That is a fault in whatever is driving "
                "the loop, not an outcome to report."
            )

        outcome = self._script[self._position]
        self._position += 1
        return Attempt(
            strategy_name=strategy.name,
            escalated=escalated,
            outcome=outcome,
            cost=strategy.escalation_cost if escalated else strategy.initial_cost,
            success_probability=(
                strategy.escalated_success_probability
                if escalated
                else strategy.initial_success_probability
            ),
        )
