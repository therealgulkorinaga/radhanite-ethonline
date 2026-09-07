"""The five inputs that define a Radhanite task.

PREREQ-001 §4 fixes the input contract:

    task + budget + task_value + constraints + success condition

Budget and task value are separate, and neither is derived from the other. A
budget alone answers "may I afford this?"; only a value answers "is it worth
buying?". Without both, no genuine economic decision is possible — which is why
`Task` requires them independently and never computes one from the other.

Validation here is deliberately thin. A zero budget and a zero task value are
both accepted, because TASK-001 §2.5 assigns those outcomes to the escalation
rule: a zero budget fails the budget condition, and a zero value fails the value
condition, and in both cases the rule returns Stop. Rejecting them up front
would invent a product rule neither authoritative document states, and would
prevent the specified Stop outcome from ever being reached. Negative amounts are
refused, since they are not quantities either condition can meaningfully weigh.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from radhanite.money import Money

__all__ = ["Task"]


@dataclass(frozen=True)
class Task:
    """A unit of work with an economic frame around it.

    >>> t = Task(
    ...     description="Fix GitHub issue #184",
    ...     budget=Money("2.00"),
    ...     task_value=Money("20.00"),
    ...     success_condition="tests pass",
    ...     constraints=("no dependency changes",),
    ... )
    >>> print(t.budget, t.task_value)
    $2.00 $20.00
    """

    description: str
    budget: Money
    task_value: Money
    success_condition: str
    constraints: tuple[str, ...] = field(default=())

    def __post_init__(self) -> None:
        if not self.description or not self.description.strip():
            raise ValueError("A task needs a description of the work to be done.")

        if not isinstance(self.budget, Money):
            raise TypeError("budget must be a Money amount.")
        if self.budget.is_negative:
            raise ValueError(f"budget cannot be negative, got {self.budget}.")

        if not isinstance(self.task_value, Money):
            raise TypeError("task_value must be a Money amount.")
        if self.task_value.is_negative:
            raise ValueError(
                f"task_value cannot be negative, got {self.task_value}."
            )

        if not self.success_condition or not self.success_condition.strip():
            raise ValueError(
                "A task needs a measurable success condition. Without one, "
                "Radhanite cannot judge whether spending achieved anything, and "
                "the task is not a Radhanite task (PREREQ-001 §4.5)."
            )

        if isinstance(self.constraints, str):
            raise TypeError(
                "constraints must be a tuple of strings, not a single string."
            )
        object.__setattr__(self, "constraints", tuple(self.constraints))
