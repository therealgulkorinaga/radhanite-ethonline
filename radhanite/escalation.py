"""The escalation rule: whether buying more intelligence is worth it.

This is the decision Radhanite exists to make. TASK-001 §2.5 fixes it, and it is
not open to reinterpretation:

    incremental_expected_value =
        (post_escalation_success_probability - current_success_probability)
        × task_value

    Escalate if and only if BOTH:
        remaining_budget >= escalation_cost
        incremental_expected_value > escalation_cost

    Otherwise, Stop.

Four properties of that rule must survive contact with any implementation, and
each is covered by a test:

**The test is marginal, not cumulative.** It weighs the *next* purchase against
the gain from *that purchase*. Spend already incurred appears nowhere. Sunk cost
must not influence the decision, so this function is not even told what has been
spent so far.

**Ties do not escalate.** The value condition is a strict `>`. Where the gain
exactly equals the cost, the decision is Stop.

**No expected improvement means Stop**, with no special case. Equal
probabilities give an incremental expected value of exactly zero, and a
worsening strategy gives a negative one; neither exceeds a non-negative cost, so
the condition simply fails.

**Budget and value never substitute for each other.** `remaining_budget` appears
only in the first condition and `task_value` only in the second. An
implementation that used one in place of the other would still run, and would
have destroyed the economic model.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from radhanite.money import Money
from radhanite.probability import Probability

__all__ = ["Decision", "EscalationDecision", "FailedCondition", "decide"]


class Decision(Enum):
    """What the rule concluded."""

    ESCALATE = "escalate"
    STOP = "stop"


class FailedCondition(Enum):
    """Which of the rule's two conditions was not met.

    TASK-001 §2.5 requires a Stop to record which condition failed. Both can
    fail at once, so a decision carries a tuple of these rather than one.
    """

    BUDGET = "budget"
    VALUE = "value"


@dataclass(frozen=True, slots=True)
class EscalationDecision:
    """A decision, with everything needed to recompute it.

    TASK-001 §2.6 requires every decision in a run record to be explicable after
    the fact. A decision that cannot be recomputed from what was recorded does
    not satisfy that, so every input is carried here alongside the conclusion.
    """

    decision: Decision
    reason: str
    incremental_expected_value: Money
    current_success_probability: Probability
    post_escalation_success_probability: Probability
    task_value: Money
    escalation_cost: Money
    remaining_budget: Money
    failed_conditions: tuple[FailedCondition, ...]

    @property
    def escalated(self) -> bool:
        return self.decision is Decision.ESCALATE

    def __str__(self) -> str:
        return self.reason


def decide(
    *,
    current_success_probability: Probability,
    post_escalation_success_probability: Probability,
    task_value: Money,
    escalation_cost: Money,
    remaining_budget: Money,
) -> EscalationDecision:
    """Apply the escalation rule.

    Arguments are keyword-only. Five quantities of two types, several
    interchangeable by shape and none by meaning, is precisely the situation in
    which a positional call silently swaps two of them.

    >>> d = decide(
    ...     current_success_probability=Probability("0.50"),
    ...     post_escalation_success_probability=Probability("0.80"),
    ...     task_value=Money("20.00"),
    ...     escalation_cost=Money("0.50"),
    ...     remaining_budget=Money("2.00"),
    ... )
    >>> d.decision
    <Decision.ESCALATE: 'escalate'>
    >>> str(d.incremental_expected_value)
    '$6.00'
    """
    if escalation_cost.is_negative:
        raise ValueError(
            f"escalation_cost cannot be negative, got {escalation_cost}."
        )
    if remaining_budget.is_negative:
        # A negative remaining budget means the ceiling in TASK-001 criterion 12
        # has already been breached. That is a fault in whatever is tracking the
        # balance, not an economic situation to reason about, so it stops here
        # rather than producing a confident decision from a broken state.
        raise ValueError(
            f"remaining_budget cannot be negative, got {remaining_budget}. "
            "The budget ceiling has already been breached."
        )

    change = post_escalation_success_probability - current_success_probability
    incremental_expected_value = task_value * change

    budget_allows = remaining_budget >= escalation_cost
    value_justifies = incremental_expected_value > escalation_cost

    failed: list[FailedCondition] = []
    if not budget_allows:
        failed.append(FailedCondition.BUDGET)
    if not value_justifies:
        failed.append(FailedCondition.VALUE)

    decision = Decision.ESCALATE if not failed else Decision.STOP
    reason = _explain(
        decision=decision,
        failed=tuple(failed),
        change=change,
        incremental_expected_value=incremental_expected_value,
        current=current_success_probability,
        post=post_escalation_success_probability,
        task_value=task_value,
        escalation_cost=escalation_cost,
        remaining_budget=remaining_budget,
    )

    return EscalationDecision(
        decision=decision,
        reason=reason,
        incremental_expected_value=incremental_expected_value,
        current_success_probability=current_success_probability,
        post_escalation_success_probability=post_escalation_success_probability,
        task_value=task_value,
        escalation_cost=escalation_cost,
        remaining_budget=remaining_budget,
        failed_conditions=tuple(failed),
    )


def _explain(
    *,
    decision: Decision,
    failed: tuple[FailedCondition, ...],
    change,
    incremental_expected_value: Money,
    current: Probability,
    post: Probability,
    task_value: Money,
    escalation_cost: Money,
    remaining_budget: Money,
) -> str:
    """State the decision in terms a person can check.

    PREREQ-001 §8 requires every economic decision to be inspectable and
    explicable after the fact. Recording *that* a decision happened is not the
    same as recording why, so the reason names the quantities that produced it.
    """
    gain = (
        f"raising the chance of success from {current} to {post} on a "
        f"{task_value} outcome is worth {incremental_expected_value}"
    )
    if decision is Decision.ESCALATE:
        return (
            f"Escalate: spending {escalation_cost} buys more than it costs — "
            f"{gain}, against a cost of {escalation_cost}, with "
            f"{remaining_budget} of budget remaining."
        )

    reasons = []
    if FailedCondition.BUDGET in failed:
        reasons.append(
            f"only {remaining_budget} remains, which cannot cover the "
            f"{escalation_cost} this would cost"
        )
    if FailedCondition.VALUE in failed:
        if change == 0:
            reasons.append(
                f"it would not improve the chance of success at all (still "
                f"{current}), so it is worth nothing against a cost of "
                f"{escalation_cost}"
            )
        elif change < 0:
            reasons.append(
                f"it would make success less likely ({current} to {post}), so "
                f"it is worth less than nothing against a cost of "
                f"{escalation_cost}"
            )
        else:
            reasons.append(
                f"{gain}, which does not exceed the {escalation_cost} it costs"
            )
    return "Stop: " + "; and ".join(reasons) + "."
