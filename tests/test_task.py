"""A task is the five inputs, and it refuses to be less than that.

PREREQ-001 §4: task + budget + task_value + constraints + success condition.
The tests that matter most here are the ones proving budget and task value stay
independent, since collapsing them would remove the economic decision entirely.
"""

import doctest
import unittest
from decimal import Decimal

from radhanite import task as task_module
from radhanite.money import Money
from radhanite.task import Task


def a_task(**overrides) -> Task:
    """A valid task, with fields replaceable one at a time."""
    fields = {
        "description": "Fix GitHub issue #184",
        "budget": Money("2.00"),
        "task_value": Money("20.00"),
        "success_condition": "tests pass",
        "constraints": ("no dependency changes",),
    }
    fields.update(overrides)
    return Task(**fields)


class AcceptanceTests(unittest.TestCase):
    def test_accepts_all_five_inputs(self) -> None:
        t = a_task()
        self.assertEqual(t.description, "Fix GitHub issue #184")
        self.assertEqual(t.budget, Money("2.00"))
        self.assertEqual(t.task_value, Money("20.00"))
        self.assertEqual(t.success_condition, "tests pass")
        self.assertEqual(t.constraints, ("no dependency changes",))

    def test_constraints_are_optional(self) -> None:
        self.assertEqual(a_task(constraints=()).constraints, ())

    def test_constraints_are_normalised_to_a_tuple(self) -> None:
        self.assertEqual(a_task(constraints=["a", "b"]).constraints, ("a", "b"))


class BudgetAndValueAreIndependentTests(unittest.TestCase):
    """PREREQ-001 §4.3: neither is derived from the other."""

    def test_value_far_exceeding_budget_is_normal(self) -> None:
        t = a_task(budget=Money("2.00"), task_value=Money("20.00"))
        self.assertNotEqual(t.budget, t.task_value)
        self.assertEqual(t.headroom_ratio, Decimal("10"))

    def test_value_below_budget_is_permitted(self) -> None:
        # Economically unwise, but not the type's business to forbid: the
        # escalation rule will simply refuse to spend.
        t = a_task(budget=Money("20.00"), task_value=Money("2.00"))
        self.assertEqual(t.task_value, Money("2.00"))

    def test_equal_budget_and_value_are_permitted(self) -> None:
        t = a_task(budget=Money("5.00"), task_value=Money("5.00"))
        self.assertEqual(t.headroom_ratio, Decimal("1"))


class RejectionTests(unittest.TestCase):
    def test_rejects_empty_description(self) -> None:
        with self.assertRaises(ValueError):
            a_task(description="   ")

    def test_rejects_zero_budget(self) -> None:
        with self.assertRaises(ValueError):
            a_task(budget=Money("0"))

    def test_rejects_negative_budget(self) -> None:
        with self.assertRaises(ValueError):
            a_task(budget=Money("-1.00"))

    def test_rejects_zero_task_value(self) -> None:
        # A task worth nothing can never justify any expenditure, so the
        # escalation rule would have nothing to weigh.
        with self.assertRaises(ValueError):
            a_task(task_value=Money("0"))

    def test_rejects_negative_task_value(self) -> None:
        with self.assertRaises(ValueError):
            a_task(task_value=Money("-5.00"))

    def test_rejects_missing_success_condition(self) -> None:
        with self.assertRaises(ValueError) as caught:
            a_task(success_condition="")
        self.assertIn("success condition", str(caught.exception))

    def test_rejects_plain_numbers_for_money(self) -> None:
        with self.assertRaises(TypeError):
            a_task(budget="2.00")
        with self.assertRaises(TypeError):
            a_task(task_value=20)

    def test_rejects_a_bare_string_of_constraints(self) -> None:
        # Would otherwise silently become a tuple of characters.
        with self.assertRaises(TypeError):
            a_task(constraints="no dependency changes")


class ImmutabilityTests(unittest.TestCase):
    def test_a_task_cannot_be_changed_after_creation(self) -> None:
        with self.assertRaises(Exception):
            a_task().budget = Money("999.00")


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(task_module, optionflags=doctest.ELLIPSIS))
    return tests
