"""A probability is exact, bounded, and its difference is not a probability."""

import doctest
import unittest
from decimal import Decimal, localcontext

from radhanite import probability as probability_module
from radhanite.probability import Probability


class ConstructionTests(unittest.TestCase):
    def test_builds_from_string_int_and_decimal(self) -> None:
        self.assertEqual(Probability("0.55").value, Decimal("0.55"))
        self.assertEqual(Probability(1).value, Decimal(1))
        self.assertEqual(Probability(Decimal("0.5")).value, Decimal("0.5"))

    def test_rejects_floats(self) -> None:
        with self.assertRaises(TypeError):
            Probability(0.55)

    def test_rejects_bool(self) -> None:
        with self.assertRaises(TypeError):
            Probability(True)

    def test_rejects_non_finite(self) -> None:
        for value in ("NaN", "Infinity"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                Probability(value)


class BoundsTests(unittest.TestCase):
    def test_zero_and_one_are_valid(self) -> None:
        self.assertEqual(Probability("0").value, Decimal("0"))
        self.assertEqual(Probability("1").value, Decimal("1"))

    def test_rejects_below_zero(self) -> None:
        with self.assertRaises(ValueError):
            Probability("-0.01")

    def test_rejects_above_one(self) -> None:
        with self.assertRaises(ValueError):
            Probability("1.01")


class DifferenceTests(unittest.TestCase):
    def test_difference_is_a_plain_decimal_not_a_probability(self) -> None:
        # A difference ranges from -1 to 1, so it is not itself a probability.
        change = Probability("0.80") - Probability("0.50")
        self.assertIsInstance(change, Decimal)
        self.assertNotIsInstance(change, Probability)
        self.assertEqual(change, Decimal("0.30"))

    def test_equal_probabilities_give_exactly_zero(self) -> None:
        self.assertEqual(Probability("0.55") - Probability("0.55"), Decimal("0"))

    def test_a_worsening_strategy_gives_a_negative_change(self) -> None:
        # TASK-001 §2.5 requires this case to fall out of the arithmetic.
        self.assertEqual(Probability("0.40") - Probability("0.70"), Decimal("-0.30"))

    def test_difference_ignores_ambient_precision(self) -> None:
        with localcontext() as ctx:
            ctx.prec = 3
            change = Probability("0.87654321") - Probability("0.12345678")
        self.assertEqual(change, Decimal("0.75308643"))


class OrderingTests(unittest.TestCase):
    def test_probabilities_compare(self) -> None:
        self.assertLess(Probability("0.5"), Probability("0.8"))
        self.assertEqual(Probability("0.50"), Probability("0.5"))


def load_tests(loader, tests, ignore):
    tests.addTests(
        doctest.DocTestSuite(probability_module, optionflags=doctest.ELLIPSIS)
    )
    return tests
