"""A probability of success, held exactly.

The escalation rule multiplies a *change* in probability by a task's value. If
that change is even slightly wrong, the resulting expected value is wrong, and
TASK-001 §2.5 compares it against a cost with a strict `>` — so a small error
lands on the wrong side of the comparison and the wrong decision is made, with
nothing in the record to show why.

Probabilities are therefore exact for the same reasons money is, and are refused
outright when built from a float.

In TASK-001 these values are **static declared constants** attached to strategy
fixtures. They are never estimated, learned, inferred, or updated from run
history — that is `BL-05`/`BL-06` in the backlog and is unauthorized.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, localcontext

from radhanite._exactness import exact as _exact

__all__ = ["Probability"]

_ZERO = Decimal(0)
_ONE = Decimal(1)


@dataclass(frozen=True, order=True)
class Probability:
    """A probability between 0 and 1 inclusive.

    >>> Probability("0.80") - Probability("0.50")
    Decimal('0.30')
    """

    value: Decimal

    def __post_init__(self) -> None:
        raw = self.value
        if isinstance(raw, bool) or isinstance(raw, float):
            raise TypeError(
                f"Probability cannot be built from a float ({raw!r}); floats "
                "cannot represent most decimal values exactly. Use a string, "
                "int, or Decimal."
            )
        if isinstance(raw, (str, int)):
            try:
                raw = Decimal(raw)
            except InvalidOperation as exc:
                raise ValueError(f"{self.value!r} is not a valid probability.") from exc
            object.__setattr__(self, "value", raw)
        elif not isinstance(raw, Decimal):
            raise TypeError(
                "Probability requires a str, int, or Decimal, not "
                f"{type(raw).__name__}."
            )

        if not self.value.is_finite():
            raise ValueError(
                f"Probability must be finite, got {self.value}."
            )
        if not (_ZERO <= self.value <= _ONE):
            raise ValueError(
                f"Probability must be between 0 and 1 inclusive, got {self.value}."
            )

    def __sub__(self, other: Probability) -> Decimal:
        """The change from one probability to another.

        Returns a plain `Decimal`, not a `Probability`. A difference is not
        itself a probability: it ranges from -1 to 1, and TASK-001 §2.5 requires
        the negative case — a strategy that makes success *less* likely — to
        fall out of the arithmetic rather than be special-cased.
        """
        if not isinstance(other, Probability):
            return NotImplemented
        with localcontext(_exact()):
            return self.value - other.value

    def __str__(self) -> str:
        return f"{self.value}"
