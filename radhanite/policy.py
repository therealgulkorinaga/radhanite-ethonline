"""What a run is permitted to do, stated by the run rather than assumed.

TASK-006 §2.2a: `max_capability_steps` is **authoritative run policy**. It is
not a sixth user input under `PREREQ-001` §4, and it is not something the
economic rule may supply for itself.

§2.5 C makes the ceiling a **termination safeguard**, deliberately independent
of the budget: once a run has bought its allowance, it stops whatever else is
true of the candidates on offer. §5 forbids a default that would make it
optional, and forbids a literal ceiling anywhere in the selection logic. The
demonstration configures four; four is a setting, not a property of the product.

**This object carries the ceiling and nothing else.** It is not a home for
configuration in general, and it drives nothing: no run loop lives here, no
counter is incremented, and no orchestration happens. A run reads the number and
passes it to the decision.
"""

from __future__ import annotations

from dataclasses import dataclass

from radhanite._immutable import refuse_rehydration

__all__ = ["RunPolicy"]


@refuse_rehydration
@dataclass(frozen=True, slots=True)
class RunPolicy:
    """The maximum number of paid capability steps permitted for one run.

    >>> RunPolicy(max_capability_steps=4).max_capability_steps
    4
    """

    max_capability_steps: int

    def __post_init__(self) -> None:
        value = self.max_capability_steps

        if isinstance(value, bool) or not isinstance(value, int):
            # bool is a subclass of int, so True would otherwise pass as a
            # ceiling of one — a caller error that would silently permit exactly
            # one purchase.
            raise TypeError(
                "max_capability_steps must be a whole number of steps, got "
                f"{type(value).__name__}."
            )

        if value < 1:
            # Zero is refused here although the decision primitives tolerate it.
            # A policy is a statement that a run may buy capabilities; a run
            # permitted none has no use for the economic rule at all, and
            # TASK-006 §7 requires at least one step for the delivered two-tier
            # scenarios to reproduce.
            raise ValueError(
                f"max_capability_steps must be at least 1, got {value}. A run "
                "that may buy nothing does not need a capability decision."
            )
