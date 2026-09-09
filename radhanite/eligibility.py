"""Whether one candidate may be bought, and what buying it would be worth.

TASK-006 §2.3 fixes the test, and it is not open to reinterpretation:

    incremental_expected_value =
        (candidate_success_probability - current_success_probability)
        × task_value

    net_expected_value = incremental_expected_value - candidate_cost

    A candidate is ELIGIBLE only when ALL SIX hold:
        candidate_cost > 0
        candidate_cost <= remaining_budget
        candidate_success_probability > current_success_probability
        incremental_expected_value > candidate_cost
        candidate_id has not already been consumed in this run
        capability_step_count < max_capability_steps

    Otherwise it is INELIGIBLE, which is an ordinary outcome and not an error.

**This module assesses one candidate. It selects nothing.** Ranking eligible
candidates against each other, and deciding what a run does next, are later
steps of TASK-006 and must not appear here.

Properties that must survive any implementation, each covered by a test:

**The test is marginal, not cumulative.** It weighs *this* purchase against the
gain from *that purchase*. Spend already incurred appears nowhere, so this
function is not told what a run has spent — only what it has left.

**Ties are ineligible.** The value condition is a strict `>`. Where the gain
exactly equals the cost, buying it changes nothing worth having.

**Budget and value never substitute for each other.** `remaining_budget` appears
only in the affordability condition and `task_value` only in the value one. An
implementation that swapped them would still run, and would have destroyed the
economic model.

**Economic figures are computed for ineligible candidates too.** TASK-006 §8
requires the run record to show why an alternative was *not* bought, and a
record carrying figures only for the winner cannot answer that.

**The last two conditions are not economic.** A consumed candidate and an
exhausted step budget are the termination safeguards of §2.5, and a run record
must not present them as judgements about value — see `Ineligibility`.
"""

from __future__ import annotations

from collections.abc import Collection
from dataclasses import dataclass
from enum import Enum

from radhanite._immutable import refuse_rehydration

from radhanite.capability import Candidate
from radhanite.money import Money
from radhanite.probability import Probability

__all__ = ["Assessment", "Ineligibility", "assess"]


class Ineligibility(Enum):
    """Which of the six conditions in TASK-006 §2.3 was not met.

    Several can fail at once, so an assessment carries a tuple of these rather
    than a single cause.

    The first four are economic. `CONSUMED` and `STEP_CEILING` are the
    termination safeguards of §2.5, and §8 requires a run record to keep that
    distinction: a candidate refused because the run has bought enough already
    was never assessed on its merits, and reporting it as though the economics
    rejected it would claim a judgement that was never made.
    """

    COST_NOT_POSITIVE = "cost_not_positive"
    BUDGET = "budget"
    UPLIFT = "uplift"
    VALUE = "value"
    CONSUMED = "consumed"
    STEP_CEILING = "step_ceiling"

    @property
    def is_economic(self) -> bool:
        """False for the §2.5 termination safeguards."""
        return self not in (Ineligibility.CONSUMED, Ineligibility.STEP_CEILING)


@refuse_rehydration
@dataclass(frozen=True, slots=True)
class Assessment:
    """One candidate weighed, with everything needed to recompute the answer.

    TASK-006 §8 requires every decision to be explicable after the fact. An
    assessment that cannot be recomputed from what it recorded does not satisfy
    that, so every input is carried here alongside the conclusion.
    """

    candidate: Candidate
    reason: str
    incremental_expected_value: Money
    net_expected_value: Money
    current_success_probability: Probability
    task_value: Money
    remaining_budget: Money
    capability_step_count: int
    max_capability_steps: int
    failed_conditions: tuple[Ineligibility, ...]

    @property
    def eligible(self) -> bool:
        """True when no condition failed. Ineligible is ordinary, not an error."""
        return not self.failed_conditions

    @property
    def refused_without_economic_judgement(self) -> bool:
        """True when every failure was a §2.5 safeguard rather than economics.

        A run record must not present such a refusal as a verdict on value —
        §2.5's step-ceiling STOP is a safety stop, and this is the same
        distinction at the level of one candidate.
        """
        return bool(self.failed_conditions) and not any(
            condition.is_economic for condition in self.failed_conditions
        )

    def __str__(self) -> str:
        return self.reason


def assess(
    *,
    candidate: Candidate,
    current_success_probability: Probability,
    task_value: Money,
    remaining_budget: Money,
    consumed_candidate_ids: Collection[str] = (),
    capability_step_count: int = 0,
    max_capability_steps: int,
) -> Assessment:
    """Apply TASK-006 §2.3 to one candidate.

    Arguments are keyword-only. Several are interchangeable by shape and none by
    meaning, which is exactly the situation in which a positional call silently
    swaps two of them.

    >>> from radhanite.capability import Candidate
    >>> a = assess(
    ...     candidate=Candidate("second-opinion-001", Money("0.50"),
    ...                         Probability("0.80")),
    ...     current_success_probability=Probability("0.50"),
    ...     task_value=Money("20.00"),
    ...     remaining_budget=Money("2.00"),
    ...     max_capability_steps=4,
    ... )
    >>> a.eligible
    True
    >>> str(a.incremental_expected_value), str(a.net_expected_value)
    ('$6.00', '$5.50')
    """
    if not isinstance(candidate, Candidate):
        raise TypeError(f"candidate must be a Candidate, got {type(candidate).__name__}.")
    if not isinstance(current_success_probability, Probability):
        raise TypeError("current_success_probability must be a Probability.")
    if not isinstance(task_value, Money):
        raise TypeError("task_value must be a Money amount.")
    if not isinstance(remaining_budget, Money):
        raise TypeError("remaining_budget must be a Money amount.")

    if remaining_budget.is_negative:
        # A negative remaining budget means the ceiling in TASK-006 §2.6 has
        # already been breached. That is a fault in whatever tracks the balance,
        # not an economic situation to reason about, so it stops here rather
        # than producing a confident answer from a broken state.
        raise ValueError(
            f"remaining_budget cannot be negative, got {remaining_budget}. "
            "The budget ceiling has already been breached."
        )

    consumed = _checked_consumed(consumed_candidate_ids)
    step_count = _checked_step("capability_step_count", capability_step_count)
    step_limit = _checked_step("max_capability_steps", max_capability_steps)

    change = candidate.success_probability - current_success_probability
    incremental_expected_value = task_value * change
    net_expected_value = incremental_expected_value - candidate.cost

    failed: list[Ineligibility] = []

    if not candidate.cost.is_positive:
        # Unreachable through `Candidate`, which refuses a non-positive cost at
        # construction (TASK-006 §2.5 A). Checked anyway: §2.3 states six
        # conditions and this rule is correct on its own terms rather than only
        # while another module holds. `_immutable.py` documents that
        # object.__setattr__ can defeat the constructor, and a termination
        # safeguard that silently lapses when it is defeated is not a safeguard.
        failed.append(Ineligibility.COST_NOT_POSITIVE)
    if not remaining_budget >= candidate.cost:
        failed.append(Ineligibility.BUDGET)
    if not candidate.success_probability > current_success_probability:
        # Redundant while cost is positive and task_value is not negative, and
        # deliberately kept — TASK-006 §2.3. It is what makes the rule correct
        # for a negative task_value, where a *worsening* candidate would produce
        # a positive incremental value and pass the condition below.
        failed.append(Ineligibility.UPLIFT)
    if not incremental_expected_value > candidate.cost:
        failed.append(Ineligibility.VALUE)
    if candidate.candidate_id in consumed:
        failed.append(Ineligibility.CONSUMED)
    if not step_count < step_limit:
        failed.append(Ineligibility.STEP_CEILING)

    return Assessment(
        candidate=candidate,
        reason=_explain(
            candidate=candidate,
            failed=tuple(failed),
            incremental_expected_value=incremental_expected_value,
            net_expected_value=net_expected_value,
            current=current_success_probability,
            task_value=task_value,
            remaining_budget=remaining_budget,
            step_count=step_count,
            step_limit=step_limit,
        ),
        incremental_expected_value=incremental_expected_value,
        net_expected_value=net_expected_value,
        current_success_probability=current_success_probability,
        task_value=task_value,
        remaining_budget=remaining_budget,
        capability_step_count=step_count,
        max_capability_steps=step_limit,
        failed_conditions=tuple(failed),
    )


def _checked_consumed(consumed_candidate_ids: Collection[str]) -> frozenset[str]:
    if isinstance(consumed_candidate_ids, (str, bytes)):
        # `"a" in "abc"` is a substring test, so a bare string would quietly
        # consume candidates whose identifiers merely appear inside it.
        raise TypeError(
            "consumed_candidate_ids must be a collection of identifiers, not a "
            "string. Membership in a string is a substring test and would "
            "consume candidates that were never bought."
        )
    if not isinstance(consumed_candidate_ids, Collection):
        raise TypeError(
            "consumed_candidate_ids must be a collection, got "
            f"{type(consumed_candidate_ids).__name__}."
        )
    for consumed_id in consumed_candidate_ids:
        if not isinstance(consumed_id, str):
            raise TypeError(
                "consumed_candidate_ids must contain identifiers, found "
                f"{type(consumed_id).__name__}."
            )
    return frozenset(consumed_candidate_ids)


def _checked_step(label: str, value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{label} must be an int, got {type(value).__name__}.")
    if value < 0:
        raise ValueError(f"{label} cannot be negative, got {value}.")
    return value


def _explain(
    *,
    candidate: Candidate,
    failed: tuple[Ineligibility, ...],
    incremental_expected_value: Money,
    net_expected_value: Money,
    current: Probability,
    task_value: Money,
    remaining_budget: Money,
    step_count: int,
    step_limit: int,
) -> str:
    if not failed:
        return (
            f"Eligible: {candidate.candidate_id} costs {candidate.cost} and "
            f"raising the chance of success from {current} to "
            f"{candidate.success_probability} on a {task_value} outcome is "
            f"worth {incremental_expected_value} — a net "
            f"{net_expected_value}, with {remaining_budget} of budget "
            f"remaining and {step_count} of {step_limit} capability steps used."
        )

    parts: list[str] = []
    for condition in failed:
        if condition is Ineligibility.COST_NOT_POSITIVE:
            parts.append(
                f"its cost of {candidate.cost} is not above zero, so it is not "
                "a purchasable capability"
            )
        elif condition is Ineligibility.BUDGET:
            parts.append(
                f"it costs {candidate.cost} and only {remaining_budget} remains"
            )
        elif condition is Ineligibility.UPLIFT:
            parts.append(
                f"it offers {candidate.success_probability} against the current "
                f"{current}, which is no improvement"
            )
        elif condition is Ineligibility.VALUE:
            parts.append(
                f"it is worth {incremental_expected_value}, which does not "
                f"exceed the {candidate.cost} it costs"
            )
        elif condition is Ineligibility.CONSUMED:
            parts.append("it has already been bought in this run")
        elif condition is Ineligibility.STEP_CEILING:
            parts.append(
                f"the run has used {step_count} of its {step_limit} capability "
                "steps, so nothing further may be bought"
            )

    return f"Ineligible: {candidate.candidate_id} — " + "; ".join(parts) + "."
