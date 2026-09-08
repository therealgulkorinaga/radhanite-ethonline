"""What immutability can and cannot mean here.

Radhanite's declared figures — a strategy's costs and success probabilities —
must be static constants (TASK-001 criterion 13). Several layers keep them that
way, and it is worth being exact about where those layers stop, because a
guarantee overstated is worse than one honestly bounded.

**Prevented:**

- ordinary assignment, by ``frozen=True``;
- writing through the instance dictionary, by ``slots=True`` — there is none;
- wholesale state replacement through ``__setstate__``, by `refuse_rehydration`.

**Not prevented, and not preventable:**

- ``object.__setattr__(obj, "field", value)``. A slotted attribute is written
  through a slot descriptor and ``object.__setattr__`` goes straight to it.
  Closing this would mean holding no attributes at all — a tuple subclass rather
  than a dataclass — which trades one set of surprises for another, since a
  tuple subclass compares equal to a plain tuple and can be indexed and
  iterated.
- ``ctypes``. It can rewrite the memory of any CPython object, including the
  contents of a genuine tuple. No Python-level construct survives it.

So the honest claim is: **these values cannot be changed by accident or by any
ordinary route, and are not defended against a caller determined to change
them.** Criterion 13 is a requirement on what Radhanite itself does — it never
estimates, learns, or updates these figures — and that is enforced by a test
which reads the source, not by making the objects bulletproof.
"""

from __future__ import annotations

__all__ = ["refuse_rehydration"]


def refuse_rehydration(cls: type) -> type:
    """Stop a frozen slotted dataclass having its whole state replaced.

    `dataclass(frozen=True, slots=True)` generates a `__setstate__` for
    unpickling. It writes every field at once through the slot descriptors and
    so ignores the frozen check entirely. Nothing in Radhanite pickles these
    objects, so the route is closed rather than kept for a use that does not
    exist.

    Applied after the class is built, because a method defined on a base class
    is shadowed by the one the dataclass machinery generates.
    """

    def __setstate__(self, state: object) -> None:
        raise TypeError(
            f"{type(self).__name__} cannot have its state replaced. These are "
            "declared constants; see radhanite/_immutable.py for exactly what "
            "that does and does not guarantee."
        )

    cls.__setstate__ = __setstate__
    return cls
