"""Outcome evaluation.

TASK-001 §2.4: compare the outcome against the task's measurable success
condition and produce an objective verdict.

> Evaluation reports what happened. It does not interpret, soften, or infer
> partial success that the condition does not define.

That sentence does most of the work here. An attempt that made progress without
meeting the condition **has not succeeded**, and evaluation says so plainly.
Softening it would be the most natural mistake in the system and the most
damaging: the escalation rule would then be told the task was done, stop
spending, and report a success that never happened.

In TASK-001 the outcome of an attempt is a controlled input rather than
something observed — the simulator is told what happened and reports it (§2.3).
Evaluation therefore turns a reported outcome into a verdict against the
declared condition. When real execution arrives, this is where the condition is
actually checked; the verdict it produces, and the rule that partial progress is
not success, do not change.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from radhanite._immutable import refuse_rehydration
from radhanite.execution import Attempt, Outcome

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
    outcome: Outcome
    success_condition: str
    reason: str

    @property
    def succeeded(self) -> bool:
        return self.verdict is Verdict.MET

    def __str__(self) -> str:
        return self.reason


def evaluate(attempt: Attempt, success_condition: str) -> Evaluation:
    """Judge one attempt against the task's success condition.

    >>> from radhanite.execution import ScriptedSimulator
    >>> from radhanite.strategy import DECLARED_STRATEGIES
    >>> simulator = ScriptedSimulator([Outcome.PARTIAL_PROGRESS])
    >>> attempt = simulator.execute(DECLARED_STRATEGIES[0], escalated=False)
    >>> evaluation = evaluate(attempt, "tests pass")
    >>> evaluation.verdict
    <Verdict.NOT_MET: 'not_met'>
    >>> print(evaluation)
    Not met: the attempt made partial progress, which is not "tests pass".
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

    if attempt.outcome is Outcome.SUCCESS:
        return Evaluation(
            verdict=Verdict.MET,
            outcome=attempt.outcome,
            success_condition=condition,
            reason=f'Met: the attempt achieved "{condition}".',
        )

    if attempt.outcome is Outcome.PARTIAL_PROGRESS:
        # §2.4 forbids inferring partial success the condition does not define.
        # The condition is met or it is not; progress towards it is not a third
        # verdict, and treating it as one would tell the escalation rule to stop
        # spending on a task that was never finished.
        return Evaluation(
            verdict=Verdict.NOT_MET,
            outcome=attempt.outcome,
            success_condition=condition,
            reason=(
                f'Not met: the attempt made partial progress, which is not '
                f'"{condition}".'
            ),
        )

    return Evaluation(
        verdict=Verdict.NOT_MET,
        outcome=attempt.outcome,
        success_condition=condition,
        reason=f'Not met: the attempt failed, and "{condition}" was not achieved.',
    )
