"""Simulated execution.

TASK-001 §2.3: a strategy is executed against a **simulator, not a model**. The
simulator produces an outcome and a cost, and must be deterministic and
controllable so that success, failure and partial progress can each be exercised
on demand.

The simulator is a **test fixture standing in for the eventual inference
layer**. It is not a model of intelligence and must never be presented as one.
It does no work and decides nothing: it is told what became true and reports it,
charging the strategy's declared price.

What it reports is deliberately *evidence*, not a verdict. An attempt yields an
`Observation` — the set of conditions that now hold — and it is
`radhanite.evaluation` that decides whether those satisfy the task. An earlier
version of this module reported `SUCCESS` or `FAILURE` directly, which meant the
simulator was handing down the verdict and evaluation was only relabelling it.
§2.3 and §2.4 are separate stages on purpose.

Real execution is `BL-07` in the backlog and is unauthorized.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from enum import Enum

from radhanite._immutable import refuse_rehydration
from radhanite.money import Money
from radhanite.probability import Probability
from radhanite.strategy import Strategy

__all__ = ["Attempt", "Observation", "ScriptedSimulator"]


@refuse_rehydration
@dataclass(frozen=True, slots=True)
class Observation:
    """What became true as a result of an attempt.

    `satisfied` is the evidence: the conditions that now hold. It is what
    evaluation compares a task's success condition against, and it is the only
    thing that determines a verdict.

    `note` describes what happened for a human reader, and is never consulted by
    any decision.

    >>> Observation(satisfied=("tests pass",), note="the suite went green").satisfied
    frozenset({'tests pass'})
    >>> Observation(satisfied=(), note="nothing worked").satisfied
    frozenset()
    """

    satisfied: frozenset[str]
    note: str

    def __post_init__(self) -> None:
        raw = self.satisfied
        if isinstance(raw, (str, bytes)) or not isinstance(raw, Iterable):
            raise TypeError(
                "satisfied must be a collection of condition strings, not "
                f"{type(raw).__name__}."
            )
        conditions = []
        for condition in raw:
            if not isinstance(condition, str):
                raise TypeError(
                    f"satisfied may contain only strings, got {condition!r}."
                )
            if not condition.strip():
                raise ValueError("A satisfied condition cannot be blank.")
            conditions.append(condition.strip())
        object.__setattr__(self, "satisfied", frozenset(conditions))

        if not self.note or not self.note.strip():
            raise ValueError("An observation needs a note describing what happened.")
        object.__setattr__(self, "note", self.note.strip())

    def __str__(self) -> str:
        return self.note


@refuse_rehydration
@dataclass(frozen=True, slots=True)
class Attempt:
    """One execution of a strategy, what it cost, and what it achieved.

    Carries everything needed to reconstruct the attempt, since TASK-001 §2.6
    requires a run record from which every decision can be recomputed.
    """

    strategy_name: str
    escalated: bool
    cost: Money
    success_probability: Probability
    observation: Observation

    def __str__(self) -> str:
        stage = "escalated" if self.escalated else "initial"
        return (
            f"{self.strategy_name} ({stage} attempt, {self.success_probability} "
            f"likely) cost {self.cost}: {self.observation.note}"
        )


class ScriptedSimulator:
    """Reports observations that were decided in advance, in order.

    Deterministic by construction: the same script produces the same run, every
    time. Nothing is inferred, sampled, or derived from the strategy's stated
    chance of success — a simulator that rolled dice against those probabilities
    would make the economic loop untestable, which is exactly what §2.3 avoids.

    >>> from radhanite.strategy import DECLARED_STRATEGIES
    >>> simulator = ScriptedSimulator([
    ...     Observation(satisfied=(), note="the build broke"),
    ...     Observation(satisfied=("tests pass",), note="the suite went green"),
    ... ])
    >>> strategy = DECLARED_STRATEGIES[0]
    >>> simulator.execute(strategy, escalated=False).observation.satisfied
    frozenset()
    >>> simulator.execute(strategy, escalated=True).observation.satisfied
    frozenset({'tests pass'})
    >>> simulator.remaining
    0
    """

    __slots__ = ("_script", "_position")

    def __init__(self, script: Sequence[Observation]) -> None:
        if isinstance(script, (str, bytes)) or not isinstance(script, Sequence):
            raise TypeError(
                "script must be an ordered sequence of Observations, not "
                f"{type(script).__name__}. An unordered collection could not "
                "produce the same run twice."
            )
        # Snapshot once, then validate the snapshot. Validating the argument and
        # then copying it separately reads the sequence twice, so a sequence
        # that yields different values on a second traversal could store
        # something that was never checked.
        snapshot = tuple(script)
        for step in snapshot:
            if not isinstance(step, Observation):
                raise TypeError(
                    f"script may contain only Observations, got {step!r}."
                )
        self._script: tuple[Observation, ...] = snapshot
        self._position = 0

    @property
    def remaining(self) -> int:
        return len(self._script) - self._position

    def execute(self, strategy: Strategy, *, escalated: bool) -> Attempt:
        """Carry out one attempt and report what became true.

        The cost and the stated chance of success come from the strategy's
        declared figures — the initial pair, or the escalated pair. The simulator
        adds nothing of its own.
        """
        if not isinstance(strategy, Strategy):
            raise TypeError(f"strategy must be a Strategy, got {type(strategy).__name__}.")
        if self._position >= len(self._script):
            raise RuntimeError(
                "The simulator has run out of scripted observations. Something "
                f"asked for attempt {self._position + 1} of a script with "
                f"{len(self._script)}. That is a fault in whatever is driving "
                "the loop, not an outcome to report."
            )

        observation = self._script[self._position]
        self._position += 1
        return Attempt(
            strategy_name=strategy.name,
            escalated=escalated,
            cost=strategy.escalation_cost if escalated else strategy.initial_cost,
            success_probability=(
                strategy.escalated_success_probability
                if escalated
                else strategy.initial_success_probability
            ),
            observation=observation,
        )
