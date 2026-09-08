"""The arithmetic context every exact calculation in Radhanite runs under.

Shared by `radhanite.money` and `radhanite.probability` so that both obey the
same guarantee and neither can drift from it.
"""

from __future__ import annotations

from decimal import Context, DivisionByZero, Inexact, InvalidOperation, Overflow

#: Precision far larger than any real amount of money or probability needs.
PRECISION = 200

__all__ = ["PRECISION", "exact"]


def exact() -> Context:
    """A fresh arithmetic context, built new for every operation.

    Two things matter here. The precision is far larger than anything Radhanite
    handles, and `Inexact` is trapped — so if an operation ever *would* round, it
    raises instead of silently returning an almost-right answer. Radhanite's
    decisions are comparisons between quantities, and an almost-right quantity is
    how a comparison flips without anyone noticing.

    The ambient decimal context defaults to 28 significant digits and can be
    changed by any code in the process. Neither is acceptable as a basis for
    deciding how to spend money.

    This is a **factory rather than a shared constant**. A `Context` is mutable:
    a single shared one could have its precision lowered or its traps cleared by
    anything holding a reference, silently removing the guarantee everything here
    depends on. Building a new one each time costs nothing that matters and
    cannot be tampered with.
    """
    return Context(
        prec=PRECISION,
        traps=[Inexact, InvalidOperation, DivisionByZero, Overflow],
    )
