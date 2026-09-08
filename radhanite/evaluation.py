"""Outcome evaluation.

TASK-001 §2.4: compare the outcome against the task's measurable success
condition and produce an objective verdict.

> Evaluation reports what happened. It does not interpret, soften, or infer
> partial success that the condition does not define.

Two things follow, and both are load-bearing.

**The comparison is real.** The verdict is decided by whether the task's success
condition is among the conditions the attempt actually satisfied. An earlier
version of this module derived the verdict from a `SUCCESS`/`FAILURE` label the
simulator supplied, which meant the simulator had already decided and evaluation
was a relabelling step — the same attempt counted as success against *any*
condition, including one it plainly had not met. §2.3 and §2.4 are separate
stages, and this is where the condition is checked.

**Partial progress is not success.** An attempt that satisfied something, but
not the condition asked for, has not met it. Softening that is the most damaging
mistake available in this system: the escalation rule would be told the task was
finished, stop spending, and report a success that never happened.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from radhanite._immutable import refuse_rehydration
from radhanite.execution import Attempt

__all__ = ["Evaluation", "Verdict", "evaluate"]


class Verdict(Enum):
    """Whether the success condition is satisfied. There is no third state."""

    MET = "met"
    NOT_MET = "not_met"


@refuse_rehydration
@dataclass(frozen=True, slots=True)
class Evaluation:
    """A verdict, with what it was judged against and why."""

    verdict: Verdict
    success_condition: str
    satisfied: frozenset[str]
    reason: str

    @property
    def succeeded(self) -> bool:
        return self.verdict is Verdict.MET

    def __str__(self) -> str:
        return self.reason


def evaluate(attempt: Attempt, success_condition: str) -> Evaluation:
    """Judge one attempt against the task's success condition.

    The condition is met if, and only if, it is among the conditions the attempt
    satisfied. Nothing else is consulted — not the strategy, not its stated
    chance of success, and not the attempt's own description of itself.

    >>> from radhanite.execution import Observation, ScriptedSimulator
    >>> from radhanite.strategy import DECLARED_STRATEGIES
    >>> simulator = ScriptedSimulator([
    ...     Observation(satisfied=("code compiles",), note="it builds, tests still red"),
    ... ])
    >>> attempt = simulator.execute(DECLARED_STRATEGIES[0], escalated=False)
    >>> evaluation = evaluate(attempt, "tests pass")
    >>> evaluation.verdict
    <Verdict.NOT_MET: 'not_met'>
    >>> print(evaluation)
    Not met: "tests pass" is not among what the attempt achieved (code compiles).
    """
    if not isinstance(attempt, Attempt):
        raise TypeError(f"attempt must be an Attempt, got {type(attempt).__name__}.")
    if not success_condition or not success_condition.strip():
        raise ValueError(
            "Cannot judge an attempt without a success condition. PREREQ-001 §4.5: "
            "if success cannot be measured, Radhanite cannot make economic "
            "decisions about the task."
        )

    condition = success_condition.strip()
    satisfied = attempt.observation.satisfied

    if condition in satisfied:
        return Evaluation(
            verdict=Verdict.MET,
            success_condition=condition,
            satisfied=satisfied,
            reason=f'Met: the attempt achieved "{condition}".',
        )

    if satisfied:
        # Something was achieved, but not the thing that was asked for. §2.4
        # forbids reading that as partial success: the condition is met or it is
        # not, and progress towards it is not a third verdict.
        achieved = ", ".join(sorted(satisfied))
        return Evaluation(
            verdict=Verdict.NOT_MET,
            success_condition=condition,
            satisfied=satisfied,
            reason=(
                f'Not met: "{condition}" is not among what the attempt achieved '
                f"({achieved})."
            ),
        )

    return Evaluation(
        verdict=Verdict.NOT_MET,
        success_condition=condition,
        satisfied=satisfied,
        reason=f'Not met: the attempt achieved nothing, so "{condition}" was not met.',
    )
