"""Execution strategies, and the rule for choosing between them.

A strategy is a way of attempting a task, with a declared cost and a declared
chance of success — and a second, dearer attempt it can be escalated to.

**These numbers are declared constants, not measurements.** They are fixtures
that exist so the economic loop can be exercised deterministically. Nothing in
Radhanite estimates them, learns them, or updates them from what happened on
previous runs; that is `BL-05` and `BL-06` in the backlog and is unauthorized.
No document or output may present them as measured performance.

Selection is deterministic, per TASK-001 §2.2: identical inputs produce an
identical choice, every time. The rule is deliberately the simplest one that can
be inspected and checked —

    take the first strategy, in declared order, whose opening attempt the
    remaining budget can cover

— which makes the **order of the catalogue itself the policy**. That order is
declared data sitting in plain sight, not a judgement made at runtime, which is
what §2.2 means by rules that are fixed and inspectable.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from radhanite.money import Money
from radhanite.probability import Probability

__all__ = ["DECLARED_STRATEGIES", "Strategy", "select"]


@dataclass(frozen=True)
class Strategy:
    """One way of attempting a task, and the dearer attempt it escalates to.

    >>> s = Strategy(
    ...     name="Progressive Escalation",
    ...     initial_cost=Money("0.10"),
    ...     initial_success_probability=Probability("0.55"),
    ...     escalation_cost=Money("0.40"),
    ...     escalated_success_probability=Probability("0.85"),
    ... )
    >>> print(s.name, s.initial_cost, s.escalation_cost)
    Progressive Escalation $0.10 $0.40
    """

    name: str
    initial_cost: Money
    initial_success_probability: Probability
    escalation_cost: Money
    escalated_success_probability: Probability

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("A strategy needs a name; run records refer to it.")

        for label, cost in (
            ("initial_cost", self.initial_cost),
            ("escalation_cost", self.escalation_cost),
        ):
            if not isinstance(cost, Money):
                raise TypeError(f"{label} must be a Money amount.")
            if cost.is_negative:
                raise ValueError(f"{label} cannot be negative, got {cost}.")

        for label, chance in (
            ("initial_success_probability", self.initial_success_probability),
            ("escalated_success_probability", self.escalated_success_probability),
        ):
            if not isinstance(chance, Probability):
                raise TypeError(f"{label} must be a Probability.")

        # Deliberately NOT checked: that escalating improves the chance of
        # success. A strategy whose escalation is worthless, or actively worse,
        # is an economic situation rather than an invalid one — TASK-001 §2.5
        # requires the escalation rule to answer it with Stop, and that outcome
        # must stay reachable. Rejecting it here would invent a product rule,
        # which was finding CODEX-PR006-04.

    def __str__(self) -> str:
        return self.name


#: The declared strategy fixtures for TASK-001.
#:
#: Ordered cheapest opening attempt first, which is what makes the selection
#: rule pick the cheapest affordable option. The order is the policy; see the
#: module docstring.
#:
#: These figures are **declared benchmark assumptions**, chosen to exercise the
#: economic loop. They are not measurements of anything.
DECLARED_STRATEGIES: tuple[Strategy, ...] = (
    Strategy(
        name="Direct Attempt",
        initial_cost=Money("0.02"),
        initial_success_probability=Probability("0.35"),
        escalation_cost=Money("0.08"),
        escalated_success_probability=Probability("0.55"),
    ),
    Strategy(
        name="Progressive Escalation",
        initial_cost=Money("0.10"),
        initial_success_probability=Probability("0.55"),
        escalation_cost=Money("0.40"),
        escalated_success_probability=Probability("0.85"),
    ),
    Strategy(
        name="Exhaustive Attempt",
        initial_cost=Money("0.50"),
        initial_success_probability=Probability("0.75"),
        escalation_cost=Money("1.50"),
        escalated_success_probability=Probability("0.92"),
    ),
)


def select(
    strategies: Sequence[Strategy], remaining_budget: Money
) -> Strategy | None:
    """Choose a strategy, or report that none can be afforded.

    Takes the first strategy in declared order whose opening attempt the budget
    can cover. Returns `None` when none can be, which is not a failure: it is
    the budget condition of TASK-001 §2.5 arriving before any attempt is made,
    and the caller is expected to stop.

    The task itself is deliberately **not** a parameter. Nothing in the selection
    rule authorized by §2.2 consults it, and a parameter that is accepted and
    ignored is an abstraction justified only by a future task — ARCHITECTURE.md
    §6 item 7. It can be added when a rule actually needs it.

    >>> select(DECLARED_STRATEGIES, Money("2.00")).name
    'Direct Attempt'
    >>> select(DECLARED_STRATEGIES, Money("0.01")) is None
    True
    """
    if remaining_budget.is_negative:
        raise ValueError(
            f"remaining_budget cannot be negative, got {remaining_budget}. "
            "The budget ceiling has already been breached."
        )
    for strategy in strategies:
        if remaining_budget >= strategy.initial_cost:
            return strategy
    return None
