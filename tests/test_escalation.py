"""The escalation rule — TASK-001 §2.5.

This is the decision the product exists to make, so these tests are written
against the specification's exact wording rather than against the code.
"""

import doctest
import unittest
from decimal import Decimal

from radhanite import escalation as escalation_module
from radhanite.escalation import Decision, FailedCondition, decide
from radhanite.money import Money
from radhanite.probability import Probability


def ruling(**overrides):
    """The specification's worked example, with any quantity replaceable."""
    args = {
        "current_success_probability": Probability("0.50"),
        "post_escalation_success_probability": Probability("0.80"),
        "task_value": Money("20.00"),
        "escalation_cost": Money("0.50"),
        "remaining_budget": Money("2.00"),
    }
    args.update(overrides)
    return decide(**args)


class TheWorkedExampleTests(unittest.TestCase):
    """TASK-001 §2.5 states this example and requires it to be reproducible."""

    def test_the_specifications_worked_example(self) -> None:
        d = ruling()
        # (0.80 - 0.50) x $20.00 = $6.00
        self.assertEqual(d.incremental_expected_value, Money("6.00"))
        self.assertIs(d.decision, Decision.ESCALATE)
        self.assertEqual(d.failed_conditions, ())

    def test_the_worked_example_prints_the_specifications_figure(self) -> None:
        self.assertEqual(str(ruling().incremental_expected_value), "$6.00")


class BothConditionsTests(unittest.TestCase):
    def test_escalates_only_when_both_conditions_hold(self) -> None:
        self.assertTrue(ruling().escalated)

    def test_stops_when_the_budget_cannot_cover_the_cost(self) -> None:
        d = ruling(remaining_budget=Money("0.20"))
        self.assertIs(d.decision, Decision.STOP)
        self.assertEqual(d.failed_conditions, (FailedCondition.BUDGET,))

    def test_stops_when_the_gain_does_not_justify_the_cost(self) -> None:
        d = ruling(post_escalation_success_probability=Probability("0.51"))
        # (0.51 - 0.50) x $20.00 = $0.20, which does not exceed $0.50
        self.assertEqual(d.incremental_expected_value, Money("0.20"))
        self.assertIs(d.decision, Decision.STOP)
        self.assertEqual(d.failed_conditions, (FailedCondition.VALUE,))

    def test_records_both_conditions_when_both_fail(self) -> None:
        d = ruling(
            post_escalation_success_probability=Probability("0.51"),
            remaining_budget=Money("0.20"),
        )
        self.assertEqual(
            d.failed_conditions, (FailedCondition.BUDGET, FailedCondition.VALUE)
        )


class TheBudgetConditionTests(unittest.TestCase):
    def test_exactly_affordable_is_allowed(self) -> None:
        # The condition is >=, so spending the last of the budget is permitted.
        d = ruling(remaining_budget=Money("0.50"))
        self.assertNotIn(FailedCondition.BUDGET, d.failed_conditions)
        self.assertTrue(d.escalated)

    def test_one_cent_short_is_not(self) -> None:
        d = ruling(remaining_budget=Money("0.49"))
        self.assertEqual(d.failed_conditions, (FailedCondition.BUDGET,))

    def test_a_free_escalation_is_always_affordable(self) -> None:
        d = ruling(escalation_cost=Money("0"), remaining_budget=Money("0"))
        self.assertNotIn(FailedCondition.BUDGET, d.failed_conditions)


class TheValueConditionTests(unittest.TestCase):
    def test_a_tie_does_not_escalate(self) -> None:
        # §2.5: the value condition is a strict >. Gain exactly equal to cost
        # is Stop. (0.80 - 0.50) x $20.00 = $6.00, cost $6.00. The budget is
        # raised so that only the value condition is under test.
        d = ruling(escalation_cost=Money("6.00"), remaining_budget=Money("10.00"))
        self.assertEqual(d.incremental_expected_value, d.escalation_cost)
        self.assertIs(d.decision, Decision.STOP)
        self.assertEqual(d.failed_conditions, (FailedCondition.VALUE,))

    def test_a_penny_below_the_tie_does_escalate(self) -> None:
        # Gain $6.00 against a cost of $5.99.
        d = ruling(escalation_cost=Money("5.99"), remaining_budget=Money("10.00"))
        self.assertTrue(d.escalated)

    def test_a_penny_above_the_tie_does_not(self) -> None:
        # Gain $6.00 against a cost of $6.01. The other side of the boundary,
        # which the explanation claimed and no test covered.
        d = ruling(escalation_cost=Money("6.01"), remaining_budget=Money("10.00"))
        self.assertIs(d.decision, Decision.STOP)
        self.assertEqual(d.failed_conditions, (FailedCondition.VALUE,))

    def test_no_improvement_stops_with_no_special_case(self) -> None:
        # §2.5: equal probabilities give exactly zero, which fails the strict >.
        d = ruling(post_escalation_success_probability=Probability("0.50"))
        self.assertEqual(d.incremental_expected_value, Money("0"))
        self.assertIs(d.decision, Decision.STOP)

    def test_a_worsening_strategy_stops(self) -> None:
        d = ruling(post_escalation_success_probability=Probability("0.40"))
        self.assertEqual(d.incremental_expected_value, Money("-2.00"))
        self.assertIs(d.decision, Decision.STOP)

    def test_a_worthless_task_can_never_justify_a_cost(self) -> None:
        # PR-006 left this to the rule rather than rejecting it as invalid.
        d = ruling(task_value=Money("0"))
        self.assertEqual(d.incremental_expected_value, Money("0"))
        self.assertIs(d.decision, Decision.STOP)

    def test_a_zero_budget_task_stops_on_the_budget_condition(self) -> None:
        d = ruling(remaining_budget=Money("0"))
        self.assertIn(FailedCondition.BUDGET, d.failed_conditions)
        self.assertIs(d.decision, Decision.STOP)


class MarginalNotCumulativeTests(unittest.TestCase):
    """§2.5: spend already incurred must not influence the decision."""

    def test_the_rule_is_not_told_what_has_been_spent(self) -> None:
        import inspect

        parameters = set(inspect.signature(decide).parameters)
        self.assertEqual(
            parameters,
            {
                "current_success_probability",
                "post_escalation_success_probability",
                "task_value",
                "escalation_cost",
                "remaining_budget",
            },
        )

    def test_identical_marginal_terms_decide_identically(self) -> None:
        # Two runs that have spent wildly different amounts but face the same
        # next purchase must decide the same way, because sunk cost is not part
        # of the rule. Only the remaining budget differs, and both can afford it.
        early = ruling(remaining_budget=Money("100.00"))
        late = ruling(remaining_budget=Money("0.50"))
        self.assertEqual(early.decision, late.decision)
        self.assertEqual(
            early.incremental_expected_value, late.incremental_expected_value
        )


class BudgetAndValueDoNotSubstituteTests(unittest.TestCase):
    """§2.5: budget appears only in the first condition, value only in the second."""

    def test_a_large_budget_cannot_rescue_a_worthless_escalation(self) -> None:
        d = ruling(
            task_value=Money("0.10"), remaining_budget=Money("1000000.00")
        )
        self.assertIs(d.decision, Decision.STOP)
        self.assertEqual(d.failed_conditions, (FailedCondition.VALUE,))

    def test_a_valuable_escalation_cannot_be_bought_without_budget(self) -> None:
        d = ruling(task_value=Money("1000000.00"), remaining_budget=Money("0.10"))
        self.assertIs(d.decision, Decision.STOP)
        self.assertEqual(d.failed_conditions, (FailedCondition.BUDGET,))


class BrokenStateTests(unittest.TestCase):
    def test_a_negative_remaining_budget_is_a_fault_not_a_decision(self) -> None:
        # The ceiling in TASK-001 criterion 12 has already been breached; the
        # rule refuses to produce a confident answer from a broken state.
        with self.assertRaises(ValueError):
            ruling(remaining_budget=Money("-0.01"))

    def test_a_negative_cost_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            ruling(escalation_cost=Money("-1.00"))


class TheDecisionRecordTests(unittest.TestCase):
    """§2.6 and PREREQ-001 §8: a decision must be recomputable and explicable."""

    def test_every_input_is_carried_on_the_decision(self) -> None:
        d = ruling()
        self.assertEqual(d.current_success_probability, Probability("0.50"))
        self.assertEqual(d.post_escalation_success_probability, Probability("0.80"))
        self.assertEqual(d.task_value, Money("20.00"))
        self.assertEqual(d.escalation_cost, Money("0.50"))
        self.assertEqual(d.remaining_budget, Money("2.00"))

    def test_the_decision_can_be_recomputed_from_what_it_recorded(self) -> None:
        """Re-derive the whole verdict from the record alone, not just the value.

        §2.6 requires a decision to be recomputable from what was recorded. That
        means the verdict and the failed conditions, not only the arithmetic
        that fed them — so this applies both of §2.5's conditions independently
        and checks the conclusion matches.
        """
        for case in (
            {},
            {"remaining_budget": Money("0.20")},
            {"post_escalation_success_probability": Probability("0.51")},
            {
                "post_escalation_success_probability": Probability("0.51"),
                "remaining_budget": Money("0.20"),
            },
            {"escalation_cost": Money("6.00"), "remaining_budget": Money("10.00")},
            {"post_escalation_success_probability": Probability("0.40")},
        ):
            with self.subTest(case=case):
                d = ruling(**case)

                change = (
                    d.post_escalation_success_probability
                    - d.current_success_probability
                )
                expected_value = d.task_value * change
                self.assertEqual(expected_value, d.incremental_expected_value)

                budget_allows = d.remaining_budget >= d.escalation_cost
                value_justifies = expected_value > d.escalation_cost

                expected_failures = tuple(
                    condition
                    for condition, held in (
                        (FailedCondition.BUDGET, budget_allows),
                        (FailedCondition.VALUE, value_justifies),
                    )
                    if not held
                )
                expected_decision = (
                    Decision.ESCALATE if not expected_failures else Decision.STOP
                )

                self.assertEqual(d.failed_conditions, expected_failures)
                self.assertEqual(d.decision, expected_decision)

    def test_the_reason_names_the_quantities_that_produced_it(self) -> None:
        reason = ruling().reason
        for quantity in ("$0.50", "0.50", "0.80", "$20.00", "$6.00", "$2.00"):
            with self.subTest(quantity=quantity):
                self.assertIn(quantity, reason)

    def test_a_stop_says_which_condition_failed_and_why(self) -> None:
        reason = ruling(remaining_budget=Money("0.20")).reason
        self.assertTrue(reason.startswith("Stop:"))
        self.assertIn("$0.20", reason)
        self.assertIn("cannot cover", reason)

    def test_no_improvement_is_explained_as_such(self) -> None:
        reason = ruling(
            post_escalation_success_probability=Probability("0.50")
        ).reason
        self.assertIn("would not improve", reason)

    def test_a_worsening_strategy_is_explained_as_such(self) -> None:
        reason = ruling(
            post_escalation_success_probability=Probability("0.40")
        ).reason
        self.assertIn("less likely", reason)

    def test_ordinary_assignment_and_rehydration_are_refused(self) -> None:
        # Bounded, not absolute: object.__setattr__ and ctypes remain open
        # by design. radhanite/_immutable.py states what is prevented.
        decision = ruling()
        with self.assertRaises(Exception):
            decision.decision = Decision.STOP
        with self.assertRaises(AttributeError):
            decision.__dict__["decision"] = Decision.STOP
        with self.assertRaises(TypeError):
            decision.__setstate__({"decision": Decision.STOP})


class DeterminismTests(unittest.TestCase):
    def test_identical_inputs_decide_identically(self) -> None:
        first, second = ruling(), ruling()
        self.assertEqual(first.decision, second.decision)
        self.assertEqual(
            first.incremental_expected_value, second.incremental_expected_value
        )
        self.assertEqual(first.reason, second.reason)


def load_tests(loader, tests, ignore):
    tests.addTests(
        doctest.DocTestSuite(escalation_module, optionflags=doctest.ELLIPSIS)
    )
    return tests
