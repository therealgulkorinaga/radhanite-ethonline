"""Exact US dollar amounts.

Every economic decision Radhanite makes is a comparison between two amounts of
money, so those amounts must be exact. Binary floating point is not: `0.1 + 0.2`
is famously not `0.3`. An error of a fraction of a cent is invisible until it
flips a comparison, and a flipped comparison is a wrong decision that leaves no
trace.

`Money` therefore wraps `decimal.Decimal` and refuses to be built from a float
at all, so the mistake cannot be made quietly.

Wrapping `Decimal` is not by itself enough. Decimal arithmetic obeys an ambient
context that defaults to 28 significant digits and that any code in the process
can change; beyond that precision it rounds, silently. `Money` therefore runs
every operation in its own context with a far larger precision and with
`Inexact` trapped, so an operation that would round raises instead. Amounts are
exact or the program stops — never almost right.

Non-finite values are refused as well. `Decimal("Infinity")` and `Decimal("NaN")`
are perfectly good Decimals and are not amounts of money.

TASK-001 §6.6 fixes the unit as USD-denominated decimal values for this task.
These are internal accounting numbers. They are **not** USDC and must not be
described as USDC until a real USDC integration exists — see ARCHITECTURE.md §6
item 8.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import (
    Context,
    Decimal,
    DivisionByZero,
    Inexact,
    InvalidOperation,
    Overflow,
    localcontext,
)

CURRENCY = "USD"

#: Arithmetic runs in this context rather than the ambient one.
#:
#: Two things matter here. The precision is far larger than any real amount of
#: money needs, and `Inexact` is trapped — so if an operation ever *would* round,
#: it raises instead of silently returning an almost-right answer. Radhanite's
#: decisions are comparisons between amounts, and an almost-right amount is how
#: a comparison flips without anyone noticing.
#:
#: The ambient decimal context defaults to 28 significant digits and can be
#: changed by any code in the process. Neither is acceptable as a basis for
#: deciding how to spend money, so Money never uses it.
EXACT = Context(
    prec=200,
    traps=[Inexact, InvalidOperation, DivisionByZero, Overflow],
)

__all__ = ["CURRENCY", "EXACT", "Money"]


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
    TASK-001 §2.5 computes an incremental expected value that is **zero or
    negative** when a strategy offers no improvement — zero when the
    probabilities are equal, negative when the next strategy is worse. The rule
    requires that case to fall out of the arithmetic rather than be
    special-cased, so negative amounts must be representable.
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
            try:
                value = Decimal(value)
            except InvalidOperation as exc:
                raise ValueError(f"{value!r} is not a valid amount.") from exc
            object.__setattr__(self, "amount", value)
        elif not isinstance(value, Decimal):
            raise TypeError(
                f"Money requires a str, int, or Decimal, not {type(value).__name__}."
            )

        if not self.amount.is_finite():
            # Infinity and NaN are representable as Decimals and are not amounts
            # of money. An infinite budget is not the hard ceiling PREREQ-001
            # §4.2 requires, and NaN would fail unpredictably at comparison time
            # rather than here, where the problem actually is.
            raise ValueError(
                f"Money must be a finite amount, got {self.amount}. "
                "Infinity and NaN are not amounts of money."
            )

    # -- arithmetic ------------------------------------------------------

    def __add__(self, other: Money) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        with localcontext(EXACT):
            return Money(self.amount + other.amount)

    def __sub__(self, other: Money) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        with localcontext(EXACT):
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
        with localcontext(EXACT):
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

    @property
    def is_negative(self) -> bool:
        return self.amount < 0
