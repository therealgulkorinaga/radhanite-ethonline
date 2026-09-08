"""Money is exact, and refuses the inexact.

Every economic decision Radhanite makes is a comparison between two amounts.
These tests exist because a rounding error of a fraction of a cent is invisible
right up until it flips such a comparison.
"""

import doctest
import unittest
from decimal import Decimal, Inexact, localcontext

from radhanite import money
from radhanite.money import Money


class ConstructionTests(unittest.TestCase):
    def test_builds_from_string_int_and_decimal(self) -> None:
        self.assertEqual(Money("2.00").amount, Decimal("2.00"))
        self.assertEqual(Money(2).amount, Decimal("2"))
        self.assertEqual(Money(Decimal("2.00")).amount, Decimal("2.00"))

    def test_rejects_floats(self) -> None:
        # The whole point of the type. 0.1 is not 0.1 in binary floating point.
        with self.assertRaises(TypeError) as caught:
            Money(0.1)
        self.assertIn("float", str(caught.exception))

    def test_rejects_bool(self) -> None:
        # bool is a subclass of int, so it would otherwise slip through.
        with self.assertRaises(TypeError):
            Money(True)

    def test_rejects_other_types(self) -> None:
        with self.assertRaises(TypeError):
            Money(None)


class FiniteTests(unittest.TestCase):
    """Infinity and NaN are valid Decimals and are not amounts of money."""

    def test_rejects_infinity(self) -> None:
        for value in ("Infinity", "-Infinity", "inf"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                Money(value)

    def test_rejects_nan(self) -> None:
        with self.assertRaises(ValueError):
            Money("NaN")

    def test_rejects_non_finite_decimals_too(self) -> None:
        with self.assertRaises(ValueError):
            Money(Decimal("Infinity"))

    def test_rejects_unparseable_strings(self) -> None:
        with self.assertRaises(ValueError):
            Money("two dollars")


class ExactnessTests(unittest.TestCase):
    """Wrapping Decimal is not enough on its own.

    Decimal obeys an ambient context that defaults to 28 significant digits and
    that any code in the process may change. Money runs arithmetic in its own
    context instead, with Inexact trapped.
    """

    def test_addition_beyond_the_default_context_precision(self) -> None:
        # Under the ambient 28-digit default this rounds to ...679. It must not.
        total = Money("1.234567890123456789012345678") + Money(
            "0.0000000000000000000000000009"
        )
        self.assertEqual(total.amount, Decimal("1.2345678901234567890123456789"))

    def test_ambient_precision_cannot_change_the_answer(self) -> None:
        with localcontext() as ctx:
            ctx.prec = 5
            total = Money("1.11111111") + Money("2.22222222")
        self.assertEqual(total.amount, Decimal("3.33333333"))

    def test_multiplication_ignores_ambient_precision(self) -> None:
        with localcontext() as ctx:
            ctx.prec = 3
            product = Money("1.11111111") * Decimal("2")
        self.assertEqual(product.amount, Decimal("2.22222222"))

    def test_an_operation_that_would_round_raises_instead(self) -> None:
        # Far beyond any real amount of money, but the point is that rounding is
        # never silent: it stops the program rather than returning almost-right.
        huge = Money("1." + "1" * 150)
        with self.assertRaises(Inexact):
            huge * Decimal("1." + "1" * 150)

    def test_negation_ignores_ambient_precision(self) -> None:
        # Negation previously bypassed the exact context entirely: under an
        # ambient precision of 3 it silently returned -1.23.
        with localcontext() as ctx:
            ctx.prec = 3
            negated = -Money("1.23456789")
        self.assertEqual(negated.amount, Decimal("-1.23456789"))

    def test_display_ignores_ambient_precision(self) -> None:
        # Formatting previously went through ambient arithmetic, so a lowered
        # precision rounded the displayed amount to $1230.00000.
        with localcontext() as ctx:
            ctx.prec = 3
            shown = str(Money("1234.56789"))
        self.assertEqual(shown, "$1234.56789")

    def test_display_does_not_raise_under_an_ambient_trap(self) -> None:
        # Merely printing money must never raise because some unrelated code
        # armed a trap.
        with localcontext() as ctx:
            ctx.traps[Inexact] = True
            self.assertEqual(str(Money("1234.56789")), "$1234.56789")

    def test_display_keeps_more_digits_than_the_default_context(self) -> None:
        # 29 significant digits: one more than the default context allows.
        amount = "1.2345678901234567890123456789"
        self.assertEqual(str(Money(amount)), f"${amount}")

    def test_the_exact_context_cannot_be_tampered_with(self) -> None:
        # A shared, mutable Context could have its precision lowered or its
        # traps cleared by anything holding a reference, silently removing the
        # guarantee. There is no shared context to reach for.
        import radhanite.money as money_module

        self.assertFalse(hasattr(money_module, "EXACT"))
        self.assertNotIn("EXACT", money_module.__all__)

    def test_a_decimal_built_from_a_float_still_gets_through(self) -> None:
        # Known limitation, recorded rather than hidden. Once a float has been
        # converted to Decimal by the caller, its provenance is unrecoverable.
        sneaky = Money(Decimal(0.1))
        self.assertNotEqual(sneaky, Money("0.1"))


class ArithmeticTests(unittest.TestCase):
    def test_addition_is_exact(self) -> None:
        # 0.1 + 0.2 != 0.3 in floating point. Here it must.
        self.assertEqual(Money("0.1") + Money("0.2"), Money("0.3"))

    def test_subtraction_is_exact(self) -> None:
        self.assertEqual(Money("2.00") - Money("0.40"), Money("1.60"))

    def test_repeated_subtraction_does_not_drift(self) -> None:
        remaining = Money("1.00")
        for _ in range(10):
            remaining = remaining - Money("0.10")
        self.assertEqual(remaining, Money("0.00"))

    def test_multiplication_by_decimal(self) -> None:
        # (0.80 - 0.50) x $20.00 = $6.00 — the worked example in TASK-001 §2.5.
        self.assertEqual(Money("20.00") * Decimal("0.30"), Money("6.000"))

    def test_multiplication_by_int(self) -> None:
        self.assertEqual(Money("0.50") * 3, Money("1.50"))

    def test_rejects_multiplication_by_float(self) -> None:
        with self.assertRaises(TypeError):
            Money("20.00") * 0.3

    def test_negation(self) -> None:
        self.assertEqual(-Money("0.50"), Money("-0.50"))


class SignTests(unittest.TestCase):
    def test_negative_amounts_are_allowed(self) -> None:
        # Required by TASK-001 §2.5: a strategy offering no improvement yields
        # zero or a negative incremental expected value — zero when the
        # probabilities are equal, negative when the next strategy is worse. The
        # rule says that must fall out of the arithmetic, not be special-cased.
        self.assertEqual((Money("20.00") * Decimal("-0.10")).amount, Decimal("-2.000"))

    def test_equal_probabilities_give_exactly_zero(self) -> None:
        # The equality case §2.5 calls out: zero, not negative.
        self.assertEqual((Money("20.00") * Decimal("0")).amount, Decimal("0.00"))

    def test_is_positive(self) -> None:
        self.assertTrue(Money("0.01").is_positive)
        self.assertFalse(Money("0").is_positive)
        self.assertFalse(Money("-1").is_positive)


class ComparisonTests(unittest.TestCase):
    def test_ordering(self) -> None:
        self.assertLess(Money("0.50"), Money("6.00"))
        self.assertGreater(Money("2.00"), Money("1.99"))

    def test_equality_ignores_trailing_zeros(self) -> None:
        self.assertEqual(Money("2.0"), Money("2.00"))

    def test_greater_or_equal_boundary(self) -> None:
        # The budget condition in TASK-001 §2.5 is >=, so the exact-equality
        # case must compare as satisfied.
        self.assertGreaterEqual(Money("0.50"), Money("0.50"))


class PresentationTests(unittest.TestCase):
    def test_shows_two_places_by_default(self) -> None:
        self.assertEqual(str(Money("2")), "$2.00")

    def test_drops_trailing_zeros(self) -> None:
        # $20.00 x 0.30 produces $6.0000. The extra zeros are an artefact of how
        # the amount was reached, not information about it, and TASK-001 §2.5
        # states the worked example's figure as $6.00.
        self.assertEqual(str(Money("20.00") * Decimal("0.30")), "$6.00")
        self.assertEqual(str(Money("6.0000")), "$6.00")

    def test_dropping_zeros_does_not_drop_real_precision(self) -> None:
        self.assertEqual(str(Money("0.0000150")), "$0.000015")

    def test_keeps_sub_cent_precision(self) -> None:
        # Inference is priced well below a cent; rounding it away for display
        # would hide what was actually spent.
        self.assertEqual(str(Money("0.000015")), "$0.000015")

    def test_negative_reads_naturally(self) -> None:
        self.assertEqual(str(Money("-0.50")), "-$0.50")


class FormattingTests(unittest.TestCase):
    def test_can_be_padded_in_a_column(self) -> None:
        # f"{money}" worked while f"{money:>9}" raised TypeError, which would
        # have surfaced first in a column of output nobody tested.
        self.assertEqual(f"{Money('2.00'):>9}", "    $2.00")
        self.assertEqual(f"{Money('2.00'):<9}|", "$2.00    |")

    def test_plain_interpolation_still_works(self) -> None:
        self.assertEqual(f"{Money('2.00')}", "$2.00")

    def test_numeric_specs_are_refused_rather_than_guessed_at(self) -> None:
        with self.assertRaises(ValueError):
            f"{Money('2.00'):.2f}"

    def test_truncating_specs_are_refused(self) -> None:
        # format(Money("123.456"), ".2") returned "$1" — a different amount
        # entirely, produced silently. An amount that quietly becomes another
        # amount defeats both exactness and inspectability.
        for spec in (".2", ".4", ".10"):
            with self.subTest(spec=spec), self.assertRaises(ValueError):
                format(Money("123.456"), spec)

    def test_a_dot_fill_is_not_mistaken_for_a_precision(self) -> None:
        # "{:.>10}" pads with dots — a dot-leader column, which is exactly what
        # a table of amounts wants. The first guard against truncation refused
        # any spec containing a dot and so refused this too.
        self.assertEqual(format(Money("2.00"), ".>10"), ".....$2.00")
        self.assertEqual(format(Money("2.00"), ".<10"), "$2.00.....")
        self.assertEqual(format(Money("2.00"), ".^10"), "..$2.00...")

    def test_a_precision_after_a_dot_fill_is_still_refused(self) -> None:
        with self.assertRaises(ValueError):
            format(Money("123.456"), ".>10.2")

    def test_alignment_still_works_on_a_long_amount(self) -> None:
        self.assertEqual(format(Money("123.456"), ">10"), "  $123.456")


class ImmutabilityTests(unittest.TestCase):
    def test_cannot_be_mutated(self) -> None:
        with self.assertRaises(Exception):
            Money("1.00").amount = Decimal("999")


def load_tests(loader, tests, ignore):
    """Also run the examples in the module's own docstrings."""
    tests.addTests(doctest.DocTestSuite(money, optionflags=doctest.ELLIPSIS))
    return tests
