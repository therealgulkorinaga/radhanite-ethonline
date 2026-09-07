"""Exact US dollar amounts.

Every economic decision Radhanite makes is a comparison between two amounts of
money, so those amounts must be exact. Binary floating point is not: `0.1 + 0.2`
is famously not `0.3`. An error of a fraction of a cent is invisible until it
flips a comparison, and a flipped comparison is a wrong decision that leaves no
trace.

`Money` therefore wraps `decimal.Decimal` and refuses to be built from a float
at all, so the mistake cannot be made quietly.

TASK-001 §6.6 fixes the unit as USD-denominated decimal values for this task.
These are internal accounting numbers. They are **not** USDC and must not be
described as USDC until a real USDC integration exists — see ARCHITECTURE.md §6
item 8.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

CURRENCY = "USD"

__all__ = ["CURRENCY", "Money"]


@dataclass(frozen=True, order=True)
class Money:
    """An exact amount of US dollars.

    Build from a string, an int, or a Decimal:

        >>> Money("2.00") + Money("0.50")
        Money('2.50')

    Floats are rejected, because they cannot represent most decimal amounts
    exactly:

        >>> Money(0.1)
        Traceback (most recent call last):
        TypeError: Money cannot be built from a float ...

    Amounts may be negative. That is not an oversight: the escalation rule in
    TASK-001 §2.5 computes an incremental expected value that is negative
    whenever a strategy offers no improvement, and the rule requires that case
    to fall out of the arithmetic rather than be special-cased.
    """

    amount: Decimal

    def __post_init__(self) -> None:
        value = self.amount
        if isinstance(value, bool) or isinstance(value, float):
            raise TypeError(
                f"Money cannot be built from a float ({value!r}); floats cannot "
                "represent decimal amounts exactly. Use a string, int, or Decimal."
            )
        if isinstance(value, (str, int)):
            object.__setattr__(self, "amount", Decimal(value))
        elif not isinstance(value, Decimal):
            raise TypeError(
                f"Money requires a str, int, or Decimal, not {type(value).__name__}."
            )

    # -- arithmetic ------------------------------------------------------

    def __add__(self, other: Money) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        return Money(self.amount + other.amount)

    def __sub__(self, other: Money) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        return Money(self.amount - other.amount)

    def __mul__(self, factor: Decimal | int) -> Money:
        """Scale an amount, e.g. a probability change times a task value."""
        if isinstance(factor, bool) or isinstance(factor, float):
            raise TypeError(
                f"Money cannot be multiplied by a float ({factor!r}). "
                "Use a Decimal or an int."
            )
        if not isinstance(factor, (Decimal, int)):
            return NotImplemented
        return Money(self.amount * Decimal(factor))

    __rmul__ = __mul__

    def __neg__(self) -> Money:
        return Money(-self.amount)

    # -- presentation ----------------------------------------------------

    def __str__(self) -> str:
        exponent = self.amount.as_tuple().exponent
        places = max(2, -exponent) if isinstance(exponent, int) else 2
        sign = "-" if self.amount < 0 else ""
        return f"{sign}${abs(self.amount):.{places}f}"

    def __repr__(self) -> str:
        return f"Money('{self.amount}')"

    @property
    def is_positive(self) -> bool:
        return self.amount > 0
