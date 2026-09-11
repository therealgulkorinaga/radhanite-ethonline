"""What a run is permitted to do, stated by the run rather than assumed.

TASK-006 §2.2a: `max_capability_steps` is **authoritative run policy**. It is
not a sixth user input under `PREREQ-001` §4, and it is not something the
economic rule may supply for itself.

§2.5 C makes the ceiling a **termination safeguard**, deliberately independent
of the budget: once a run has bought its allowance, it stops whatever else is
true of the candidates on offer. §5 forbids a default that would make it
optional, and forbids a literal ceiling anywhere in the selection logic. The
demonstration configures four; four is a setting, not a property of the product.

**Zero is a valid policy**, meaning a run explicitly permitted to purchase
nothing. This object states what a run may do; it does not decide which runs are
worth having.

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
    >>> RunPolicy(max_capability_steps=0).max_capability_steps
    0
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

        if value < 0:
            raise ValueError(
                f"max_capability_steps cannot be negative, got {value}."
            )

        # Zero is VALID and means exactly what it says: this run is permitted to
        # purchase zero capabilities. An earlier revision refused it on the
        # grounds that such a run has no use for a capability decision — which
        # was a product rule this object had no authority to invent. TASK-006
        # authorizes no minimum of one, and §2.5 C's condition
        # `capability_step_count >= max_capability_steps` is unchanged and
        # already gives zero the right behaviour: nothing is ever eligible.
        # CODEX-PR026-02.
