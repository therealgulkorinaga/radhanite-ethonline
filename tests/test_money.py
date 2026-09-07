"""Money is exact, and refuses the inexact.

Every economic decision Radhanite makes is a comparison between two amounts.
These tests exist because a rounding error of a fraction of a cent is invisible
right up until it flips such a comparison.
"""

import doctest
import unittest
from decimal import Decimal

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
        # Required by TASK-001 §2.5: a strategy offering no improvement yields a
        # negative incremental expected value, and the rule says that must fall
        # out of the arithmetic rather than be special-cased.
        self.assertEqual((Money("20.00") * Decimal("-0.10")).amount, Decimal("-2.000"))

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

    def test_keeps_sub_cent_precision(self) -> None:
        # Inference is priced well below a cent; rounding it away for display
        # would hide what was actually spent.
        self.assertEqual(str(Money("0.000015")), "$0.000015")

    def test_negative_reads_naturally(self) -> None:
        self.assertEqual(str(Money("-0.50")), "-$0.50")


class ImmutabilityTests(unittest.TestCase):
    def test_cannot_be_mutated(self) -> None:
        with self.assertRaises(Exception):
            Money("1.00").amount = Decimal("999")


def load_tests(loader, tests, ignore):
    """Also run the examples in the module's own docstrings."""
    tests.addTests(doctest.DocTestSuite(money, optionflags=doctest.ELLIPSIS))
    return tests
