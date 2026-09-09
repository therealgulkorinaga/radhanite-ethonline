"""One candidate, six conditions, and the figures needed to explain the answer.

TASK-006 §2.3 fixes the eligibility test exactly. Nothing here selects between
candidates; that is a later step.
"""

import doctest
import unittest
from decimal import Decimal

from radhanite import eligibility as eligibility_module
from radhanite.capability import Candidate
from radhanite.eligibility import Assessment, Ineligibility, assess
from radhanite.money import Money
from radhanite.probability import Probability


def a_candidate(**overrides) -> Candidate:
    fields = {
        "candidate_id": "second-opinion-001",
        "cost": Money("0.50"),
        "success_probability": Probability("0.80"),
    }
    fields.update(overrides)
    return Candidate(**fields)


def an_assessment(**overrides) -> Assessment:
    arguments = {
        "candidate": a_candidate(),
        "current_success_probability": Probability("0.50"),
        "task_value": Money("20.00"),
        "remaining_budget": Money("2.00"),
        "max_capability_steps": 4,
    }
    arguments.update(overrides)
    return assess(**arguments)


class EligibleTests(unittest.TestCase):
    def test_all_six_conditions_met_is_eligible(self) -> None:
        self.assertTrue(an_assessment().eligible)
        self.assertEqual(an_assessment().failed_conditions, ())

    def test_the_economic_figures(self) -> None:
        # (0.80 - 0.50) × $20.00 = $6.00; net $6.00 - $0.50 = $5.50
        a = an_assessment()
        self.assertEqual(a.incremental_expected_value, Money("6.00"))
        self.assertEqual(a.net_expected_value, Money("5.50"))

    def test_the_reason_explains_rather_than_logs(self) -> None:
        reason = an_assessment().reason
        for figure in ("$0.50", "0.50", "0.80", "$20.00", "$6.00", "$5.50"):
            self.assertIn(figure, reason)

    def test_the_assessment_carries_every_input(self) -> None:
        # TASK-006 §8: an assessment that cannot be recomputed from what it
        # recorded does not make the decision inspectable.
        a = an_assessment()
        self.assertEqual(a.candidate, a_candidate())
        self.assertEqual(a.current_success_probability, Probability("0.50"))
        self.assertEqual(a.task_value, Money("20.00"))
        self.assertEqual(a.remaining_budget, Money("2.00"))
        self.assertEqual(a.capability_step_count, 0)
        self.assertEqual(a.max_capability_steps, 4)


class CostNotPositiveTests(unittest.TestCase):
    """§2.5 A. Unreachable through Candidate, checked anyway."""

    def _defeat_the_constructor(self, cost: Money) -> Candidate:
        # _immutable.py documents that object.__setattr__ writes straight
        # through a slot descriptor. A termination safeguard that lapses when
        # the constructor is bypassed is not a safeguard, so the rule is checked
        # on its own terms.
        candidate = a_candidate()
        object.__setattr__(candidate, "cost", cost)
        return candidate

    def test_the_constructor_normally_makes_this_unreachable(self) -> None:
        with self.assertRaises(ValueError):
            a_candidate(cost=Money("0.00"))

    def test_a_zero_cost_candidate_is_ineligible(self) -> None:
        a = an_assessment(candidate=self._defeat_the_constructor(Money("0.00")))
        self.assertFalse(a.eligible)
        self.assertIn(Ineligibility.COST_NOT_POSITIVE, a.failed_conditions)

    def test_a_negative_cost_candidate_is_ineligible(self) -> None:
        a = an_assessment(candidate=self._defeat_the_constructor(Money("-1.00")))
        self.assertIn(Ineligibility.COST_NOT_POSITIVE, a.failed_conditions)


class BudgetConditionTests(unittest.TestCase):
    def test_exactly_affordable_is_affordable(self) -> None:
        a = an_assessment(remaining_budget=Money("0.50"))
        self.assertNotIn(Ineligibility.BUDGET, a.failed_conditions)
        self.assertTrue(a.eligible)

    def test_a_penny_short_is_not(self) -> None:
        a = an_assessment(remaining_budget=Money("0.49"))
        self.assertFalse(a.eligible)
        self.assertIn(Ineligibility.BUDGET, a.failed_conditions)

    def test_a_zero_budget_refuses_everything(self) -> None:
        self.assertIn(
            Ineligibility.BUDGET,
            an_assessment(remaining_budget=Money("0.00")).failed_conditions,
        )

    def test_a_negative_budget_is_a_fault_not_a_situation(self) -> None:
        with self.assertRaises(ValueError):
            an_assessment(remaining_budget=Money("-0.01"))


class UpliftConditionTests(unittest.TestCase):
    def test_an_equal_probability_offers_no_uplift(self) -> None:
        a = an_assessment(
            candidate=a_candidate(success_probability=Probability("0.50"))
        )
        self.assertIn(Ineligibility.UPLIFT, a.failed_conditions)

    def test_a_worsening_candidate_offers_no_uplift(self) -> None:
        a = an_assessment(
            candidate=a_candidate(success_probability=Probability("0.20"))
        )
        self.assertIn(Ineligibility.UPLIFT, a.failed_conditions)

    def test_the_uplift_condition_is_not_merely_decorative(self) -> None:
        # TASK-006 §2.3 keeps this condition although it is redundant while cost
        # is positive and task_value is non-negative. Here it is the only thing
        # standing between the rule and a wrong answer: a negative task value
        # turns a *worsening* candidate into a positive incremental value, which
        # passes the value condition.
        a = an_assessment(
            candidate=a_candidate(success_probability=Probability("0.20")),
            current_success_probability=Probability("0.80"),
            task_value=Money("-20.00"),
        )
        self.assertEqual(a.incremental_expected_value, Money("12.00"))
        self.assertNotIn(Ineligibility.VALUE, a.failed_conditions)
        self.assertIn(Ineligibility.UPLIFT, a.failed_conditions)
        self.assertFalse(a.eligible)


class ValueConditionTests(unittest.TestCase):
    def test_worth_exactly_its_cost_is_ineligible(self) -> None:
        # (0.55 - 0.50) × $10.00 = $0.50, exactly the cost. TASK-006 §2.3: the
        # comparison is a strict >, and a >= here is a defect rather than a
        # rounding preference.
        a = an_assessment(
            candidate=a_candidate(success_probability=Probability("0.55")),
            task_value=Money("10.00"),
        )
        self.assertEqual(a.incremental_expected_value, Money("0.50"))
        self.assertEqual(a.candidate.cost, Money("0.50"))
        self.assertFalse(a.eligible)
        self.assertIn(Ineligibility.VALUE, a.failed_conditions)

    def test_a_penny_more_than_its_cost_is_eligible(self) -> None:
        a = an_assessment(
            candidate=a_candidate(success_probability=Probability("0.551")),
            task_value=Money("10.00"),
        )
        self.assertEqual(a.incremental_expected_value, Money("0.51"))
        self.assertTrue(a.eligible)

    def test_a_worthless_task_makes_everything_ineligible(self) -> None:
        a = an_assessment(task_value=Money("0.00"))
        self.assertEqual(a.incremental_expected_value, Money("0.00"))
        self.assertIn(Ineligibility.VALUE, a.failed_conditions)


class ConsumedConditionTests(unittest.TestCase):
    """§2.5 B, and §2.5a: an offer is single-use."""

    def test_a_consumed_candidate_is_ineligible(self) -> None:
        a = an_assessment(consumed_candidate_ids={"second-opinion-001"})
        self.assertFalse(a.eligible)
        self.assertEqual(a.failed_conditions, (Ineligibility.CONSUMED,))

    def test_it_is_ineligible_however_attractive(self) -> None:
        # Criterion 19: refused even where it would otherwise win outright.
        a = an_assessment(
            candidate=a_candidate(success_probability=Probability("1")),
            consumed_candidate_ids=["second-opinion-001"],
        )
        self.assertFalse(a.eligible)

    def test_a_different_identifier_is_unaffected(self) -> None:
        # Criterion 20: the same kind of capability may return under a new
        # identifier once the state has changed. Matching is by identifier
        # alone, and the rule has no notion of type.
        a = an_assessment(
            candidate=a_candidate(candidate_id="second-opinion-002"),
            consumed_candidate_ids={"second-opinion-001"},
        )
        self.assertTrue(a.eligible)

    def test_nothing_consumed_by_default(self) -> None:
        self.assertTrue(an_assessment().eligible)

    def test_a_bare_string_is_refused(self) -> None:
        # `"a" in "abc"` is a substring test, which would consume candidates
        # that were never bought.
        with self.assertRaises(TypeError):
            an_assessment(consumed_candidate_ids="second-opinion-0011")

    def test_members_must_be_identifiers(self) -> None:
        with self.assertRaises(TypeError):
            an_assessment(consumed_candidate_ids=[1])

    def test_any_collection_is_accepted(self) -> None:
        for collection in (set(), frozenset(), [], ()):
            self.assertTrue(an_assessment(consumed_candidate_ids=collection).eligible)


class StepCeilingTests(unittest.TestCase):
    """§2.5 C — deterministic, and independent of the budget."""

    def test_below_the_ceiling_is_fine(self) -> None:
        a = an_assessment(capability_step_count=3, max_capability_steps=4)
        self.assertTrue(a.eligible)

    def test_at_the_ceiling_is_ineligible(self) -> None:
        a = an_assessment(capability_step_count=4, max_capability_steps=4)
        self.assertFalse(a.eligible)
        self.assertEqual(a.failed_conditions, (Ineligibility.STEP_CEILING,))

    def test_beyond_the_ceiling_is_ineligible(self) -> None:
        a = an_assessment(capability_step_count=5, max_capability_steps=4)
        self.assertIn(Ineligibility.STEP_CEILING, a.failed_conditions)

    def test_a_ceiling_of_zero_refuses_everything(self) -> None:
        a = an_assessment(capability_step_count=0, max_capability_steps=0)
        self.assertIn(Ineligibility.STEP_CEILING, a.failed_conditions)

    def test_it_refuses_with_budget_to_spare(self) -> None:
        # Criterion 22: termination does not depend on budget depletion.
        a = an_assessment(
            remaining_budget=Money("1000000.00"),
            capability_step_count=4,
            max_capability_steps=4,
        )
        self.assertFalse(a.eligible)
        self.assertEqual(a.failed_conditions, (Ineligibility.STEP_CEILING,))

    def test_the_ceiling_is_required_and_has_no_default(self) -> None:
        # A default would make run policy optional, which TASK-006 §5 forbids.
        with self.assertRaises(TypeError):
            assess(
                candidate=a_candidate(),
                current_success_probability=Probability("0.50"),
                task_value=Money("20.00"),
                remaining_budget=Money("2.00"),
            )

    def test_step_figures_must_be_whole_numbers(self) -> None:
        for wrong in (1.0, Decimal("1"), "1", True):
            with self.assertRaises(TypeError):
                an_assessment(max_capability_steps=wrong)
            with self.assertRaises(TypeError):
                an_assessment(capability_step_count=wrong)

    def test_negative_step_figures_are_a_fault(self) -> None:
        with self.assertRaises(ValueError):
            an_assessment(capability_step_count=-1)
        with self.assertRaises(ValueError):
            an_assessment(max_capability_steps=-1)


class SeveralConditionsTests(unittest.TestCase):
    def test_every_failure_is_reported_not_just_the_first(self) -> None:
        a = an_assessment(
            candidate=a_candidate(success_probability=Probability("0.50")),
            remaining_budget=Money("0.10"),
            consumed_candidate_ids={"second-opinion-001"},
            capability_step_count=4,
            max_capability_steps=4,
        )
        self.assertEqual(
            set(a.failed_conditions),
            {
                Ineligibility.BUDGET,
                Ineligibility.UPLIFT,
                Ineligibility.VALUE,
                Ineligibility.CONSUMED,
                Ineligibility.STEP_CEILING,
            },
        )

    def test_the_reason_names_each_one(self) -> None:
        a = an_assessment(
            remaining_budget=Money("0.10"),
            consumed_candidate_ids={"second-opinion-001"},
        )
        self.assertIn("only $0.10 remains", a.reason)
        self.assertIn("already been bought", a.reason)

    def test_failures_are_reported_in_the_order_the_rule_states_them(self) -> None:
        a = an_assessment(
            remaining_budget=Money("0.10"),
            consumed_candidate_ids={"second-opinion-001"},
            capability_step_count=4,
            max_capability_steps=4,
        )
        self.assertEqual(
            a.failed_conditions,
            (Ineligibility.BUDGET, Ineligibility.CONSUMED, Ineligibility.STEP_CEILING),
        )


class EconomicFiguresForIneligibleTests(unittest.TestCase):
    """§8 — a record showing only the winner cannot explain the alternatives."""

    def test_figures_are_computed_when_the_budget_fails(self) -> None:
        a = an_assessment(remaining_budget=Money("0.10"))
        self.assertEqual(a.incremental_expected_value, Money("6.00"))
        self.assertEqual(a.net_expected_value, Money("5.50"))

    def test_figures_are_computed_when_the_step_ceiling_fails(self) -> None:
        a = an_assessment(capability_step_count=4, max_capability_steps=4)
        self.assertEqual(a.incremental_expected_value, Money("6.00"))

    def test_a_worsening_candidate_has_a_negative_net(self) -> None:
        a = an_assessment(
            candidate=a_candidate(success_probability=Probability("0.30"))
        )
        self.assertEqual(a.incremental_expected_value, Money("-4.00"))
        self.assertEqual(a.net_expected_value, Money("-4.50"))


class SafeguardsAreNotEconomicJudgementsTests(unittest.TestCase):
    """§2.5, §8 — a safety refusal must not read as a verdict on value."""

    def test_the_safeguards_are_marked_as_not_economic(self) -> None:
        self.assertFalse(Ineligibility.CONSUMED.is_economic)
        self.assertFalse(Ineligibility.STEP_CEILING.is_economic)

    def test_the_four_economic_conditions_are_marked_economic(self) -> None:
        for condition in (
            Ineligibility.COST_NOT_POSITIVE,
            Ineligibility.BUDGET,
            Ineligibility.UPLIFT,
            Ineligibility.VALUE,
        ):
            self.assertTrue(condition.is_economic)

    def test_a_step_ceiling_refusal_carries_no_economic_judgement(self) -> None:
        a = an_assessment(capability_step_count=4, max_capability_steps=4)
        self.assertTrue(a.refused_without_economic_judgement)

    def test_a_budget_refusal_does_carry_one(self) -> None:
        a = an_assessment(remaining_budget=Money("0.10"))
        self.assertFalse(a.refused_without_economic_judgement)

    def test_an_eligible_candidate_was_not_refused_at_all(self) -> None:
        self.assertFalse(an_assessment().refused_without_economic_judgement)


class RulePropertiesTests(unittest.TestCase):
    def test_the_rule_is_marginal_not_cumulative(self) -> None:
        # Sunk cost must not influence the decision, so the function is not even
        # told what has been spent. If it were, this signature would accept it.
        import inspect

        parameters = set(inspect.signature(eligibility_module.assess).parameters)
        for absent in ("spent", "total_spent", "spend_so_far", "budget"):
            self.assertNotIn(absent, parameters)

    def test_budget_and_value_are_not_interchangeable(self) -> None:
        # Swapping them would still run. It would also have destroyed the model.
        swapped = an_assessment(
            task_value=Money("2.00"), remaining_budget=Money("20.00")
        )
        self.assertNotEqual(
            swapped.incremental_expected_value,
            an_assessment().incremental_expected_value,
        )

    def test_no_float_reaches_the_arithmetic(self) -> None:
        a = an_assessment()
        self.assertIsInstance(a.incremental_expected_value, Money)
        self.assertIsInstance(a.net_expected_value, Money)

    def test_repeated_assessment_is_identical(self) -> None:
        self.assertEqual(an_assessment().reason, an_assessment().reason)
        self.assertEqual(
            an_assessment().failed_conditions, an_assessment().failed_conditions
        )

    def test_the_rule_selects_nothing(self) -> None:
        # This step assesses one candidate. Ranking is a later step and must not
        # appear here.
        exported = set(vars(eligibility_module))
        for absent in ("select", "rank", "best", "choose", "decide"):
            self.assertNotIn(absent, exported)


class InputValidationTests(unittest.TestCase):
    def test_the_candidate_must_be_a_candidate(self) -> None:
        with self.assertRaises(TypeError):
            an_assessment(candidate="second-opinion-001")

    def test_probabilities_and_money_must_be_the_exact_types(self) -> None:
        with self.assertRaises(TypeError):
            an_assessment(current_success_probability=Decimal("0.50"))
        with self.assertRaises(TypeError):
            an_assessment(task_value=Decimal("20.00"))
        with self.assertRaises(TypeError):
            an_assessment(remaining_budget=20.0)

    def test_arguments_are_keyword_only(self) -> None:
        with self.assertRaises(TypeError):
            assess(a_candidate(), Probability("0.50"), Money("20.00"), Money("2.00"))


class ImmutabilityTests(unittest.TestCase):
    def test_ordinary_assignment_is_refused(self) -> None:
        a = an_assessment()
        with self.assertRaises(Exception):
            a.reason = "something else"

    def test_rehydration_is_refused(self) -> None:
        with self.assertRaises(TypeError):
            an_assessment().__setstate__({"reason": "something else"})

    def test_there_is_no_instance_dictionary(self) -> None:
        self.assertFalse(hasattr(an_assessment(), "__dict__"))


class ProviderNeutralityTests(unittest.TestCase):
    def test_no_provider_or_payment_concept_appears(self) -> None:
        import pathlib

        text = pathlib.Path(eligibility_module.__file__).read_text().lower()
        for forbidden in (
            "hedera",
            "circle",
            "tavily",
            "blockrun",
            "openrouter",
            "x402",
            "wallet",
            "usdc",
        ):
            self.assertNotIn(forbidden, text)


class DoctestTests(unittest.TestCase):
    def test_module_doctests_pass(self) -> None:
        results = doctest.testmod(eligibility_module, verbose=False)
        self.assertEqual(results.failed, 0)
        self.assertGreater(results.attempted, 0)


if __name__ == "__main__":
    unittest.main()
