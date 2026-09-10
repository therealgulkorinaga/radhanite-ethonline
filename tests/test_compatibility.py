"""Criterion 14 — the delivered two-tier scenarios decide identically.

TASK-006 §7 maps TASK-001 onto the generalized model:

    the initial attempt  ->  the baseline; its declared probability IS the
                             current_success_probability the decision compares
                             against
    the escalation       ->  one candidate capability
    §2.5's rule          ->  §2.3 eligibility over a candidate set of size one

§7 requires that mapping to be **demonstrated by test rather than argued**, and
says outright that if the demonstration fails the compatibility claim is
withdrawn rather than qualified. This module is that demonstration.

Every scenario below runs twice — once through TASK-001's `decide`, once through
the TASK-006 path — and asserts the two reach the same economic decision.
"""

import unittest

from radhanite.capability import Candidate
from radhanite.eligibility import assess
from radhanite.escalation import Decision, decide
from radhanite.money import Money
from radhanite.policy import RunPolicy
from radhanite.probability import Probability
from radhanite.selection import SelectionOutcome, select_capability
from radhanite.strategy import DECLARED_STRATEGIES, Strategy

POLICY = RunPolicy(max_capability_steps=1)


def historical(strategy: Strategy, *, task_value: Money, remaining_budget: Money):
    """TASK-001 §2.5, exactly as delivered."""
    return decide(
        current_success_probability=strategy.initial_success_probability,
        post_escalation_success_probability=strategy.escalated_success_probability,
        task_value=task_value,
        escalation_cost=strategy.escalation_cost,
        remaining_budget=remaining_budget,
    )


def generalized(strategy: Strategy, *, task_value: Money, remaining_budget: Money):
    """The same scenario through TASK-006 §2.3 and §2.4."""
    state = {
        "current_success_probability": strategy.initial_success_probability,
        "task_value": task_value,
        "remaining_budget": remaining_budget,
        "capability_step_count": 0,
        "max_capability_steps": POLICY.max_capability_steps,
    }
    candidate = Candidate(
        candidate_id="escalation-of-" + strategy.name.lower().replace(" ", "-"),
        cost=strategy.escalation_cost,
        success_probability=strategy.escalated_success_probability,
    )
    return select_capability(assessments=[assess(candidate=candidate, **state)], **state)


def a_strategy(**overrides) -> Strategy:
    fields = {
        "name": "Progressive Escalation",
        "initial_cost": Money("0.10"),
        "initial_success_probability": Probability("0.50"),
        "escalation_cost": Money("0.50"),
        "escalated_success_probability": Probability("0.80"),
    }
    fields.update(overrides)
    return Strategy(**fields)


class CompatibilityHarness(unittest.TestCase):
    def assertSameDecision(self, strategy, *, task_value, remaining_budget, expected):
        """Both models must agree, and agree with what the branch expects."""
        old = historical(strategy, task_value=task_value, remaining_budget=remaining_budget)
        new = generalized(strategy, task_value=task_value, remaining_budget=remaining_budget)

        old_buys = old.decision is Decision.ESCALATE
        new_buys = new.outcome is SelectionOutcome.SELECTED

        self.assertEqual(
            old_buys, new_buys,
            f"models disagree: TASK-001 {'escalates' if old_buys else 'stops'}, "
            f"TASK-006 {'selects' if new_buys else 'stops'} — {strategy.name}",
        )
        self.assertEqual(old_buys, expected)

        # The arithmetic must agree too, not merely the verdict.
        self.assertEqual(
            old.incremental_expected_value,
            new.assessments[0].incremental_expected_value,
        )


class DeclaredStrategyTests(CompatibilityHarness):
    """The three fixtures the repository actually contains — §7's scope."""

    def test_every_declared_strategy_decides_identically_when_bought(self) -> None:
        for strategy in DECLARED_STRATEGIES:
            with self.subTest(strategy=strategy.name):
                self.assertSameDecision(
                    strategy, task_value=Money("20.00"),
                    remaining_budget=Money("5.00"), expected=True,
                )

    def test_every_declared_strategy_decides_identically_when_unaffordable(self) -> None:
        for strategy in DECLARED_STRATEGIES:
            with self.subTest(strategy=strategy.name):
                self.assertSameDecision(
                    strategy, task_value=Money("20.00"),
                    remaining_budget=Money("0.01"), expected=False,
                )

    def test_every_declared_strategy_stops_on_a_worthless_task(self) -> None:
        for strategy in DECLARED_STRATEGIES:
            with self.subTest(strategy=strategy.name):
                self.assertSameDecision(
                    strategy, task_value=Money("0.00"),
                    remaining_budget=Money("5.00"), expected=False,
                )


class RuleBranchTests(CompatibilityHarness):
    """Every branch TASK-001 §2.5 names as a property that must survive."""

    def test_both_conditions_hold_and_the_purchase_is_made(self) -> None:
        # The specification's own worked example: 0.50 -> 0.80, $20.00, $0.50.
        self.assertSameDecision(
            a_strategy(), task_value=Money("20.00"),
            remaining_budget=Money("2.00"), expected=True,
        )

    def test_exactly_affordable_is_allowed(self) -> None:
        self.assertSameDecision(
            a_strategy(), task_value=Money("20.00"),
            remaining_budget=Money("0.50"), expected=True,
        )

    def test_one_cent_short_is_not(self) -> None:
        self.assertSameDecision(
            a_strategy(), task_value=Money("20.00"),
            remaining_budget=Money("0.49"), expected=False,
        )

    def test_a_tie_does_not_escalate(self) -> None:
        # (0.55 - 0.50) x $10.00 = $0.50, exactly the cost. Strict > on value.
        self.assertSameDecision(
            a_strategy(escalated_success_probability=Probability("0.55")),
            task_value=Money("10.00"), remaining_budget=Money("5.00"), expected=False,
        )

    def test_a_penny_above_the_tie_does_escalate(self) -> None:
        self.assertSameDecision(
            a_strategy(escalated_success_probability=Probability("0.551")),
            task_value=Money("10.00"), remaining_budget=Money("5.00"), expected=True,
        )

    def test_zero_uplift_stops(self) -> None:
        self.assertSameDecision(
            a_strategy(escalated_success_probability=Probability("0.50")),
            task_value=Money("20.00"), remaining_budget=Money("5.00"), expected=False,
        )

    def test_a_worsening_capability_stops(self) -> None:
        self.assertSameDecision(
            a_strategy(escalated_success_probability=Probability("0.20")),
            task_value=Money("20.00"), remaining_budget=Money("5.00"), expected=False,
        )

    def test_a_zero_budget_stops(self) -> None:
        self.assertSameDecision(
            a_strategy(), task_value=Money("20.00"),
            remaining_budget=Money("0.00"), expected=False,
        )

    def test_a_large_budget_cannot_rescue_a_worthless_capability(self) -> None:
        self.assertSameDecision(
            a_strategy(escalated_success_probability=Probability("0.50")),
            task_value=Money("20.00"), remaining_budget=Money("1000.00"), expected=False,
        )

    def test_a_valuable_capability_cannot_be_bought_without_budget(self) -> None:
        self.assertSameDecision(
            a_strategy(escalated_success_probability=Probability("0.99")),
            task_value=Money("1000.00"), remaining_budget=Money("0.10"), expected=False,
        )


class BudgetAndValueDoNotSubstituteTests(CompatibilityHarness):
    """TASK-001 §2.5: swapping them would still run, and destroy the model."""

    def test_swapping_budget_and_value_changes_both_models_the_same_way(self) -> None:
        strategy = a_strategy()
        straight = generalized(strategy, task_value=Money("20.00"), remaining_budget=Money("2.00"))
        swapped = generalized(strategy, task_value=Money("2.00"), remaining_budget=Money("20.00"))
        self.assertNotEqual(
            straight.assessments[0].incremental_expected_value,
            swapped.assessments[0].incremental_expected_value,
        )
        old_straight = historical(strategy, task_value=Money("20.00"), remaining_budget=Money("2.00"))
        old_swapped = historical(strategy, task_value=Money("2.00"), remaining_budget=Money("20.00"))
        self.assertEqual(
            old_straight.incremental_expected_value,
            straight.assessments[0].incremental_expected_value,
        )
        self.assertEqual(
            old_swapped.incremental_expected_value,
            swapped.assessments[0].incremental_expected_value,
        )


class TheOneNarrowingTests(unittest.TestCase):
    """§7 records exactly one case that does NOT carry over. It is not hidden."""

    def test_a_zero_cost_escalation_is_expressible_in_task_001(self) -> None:
        free = a_strategy(escalation_cost=Money("0.00"))
        self.assertEqual(free.escalation_cost, Money("0.00"))
        old = historical(free, task_value=Money("20.00"), remaining_budget=Money("5.00"))
        self.assertIs(old.decision, Decision.ESCALATE)

    def test_and_is_refused_outright_by_the_generalized_model(self) -> None:
        # TASK-006 §2.5 A, the positive-cost invariant — a termination
        # safeguard. §7 states this narrowing rather than claiming total
        # compatibility, and criterion 14 is scoped to the declared fixtures,
        # all three of which have positive escalation costs.
        with self.assertRaises(ValueError):
            Candidate("free", Money("0.00"), Probability("0.80"))

    def test_no_declared_strategy_is_affected_by_the_narrowing(self) -> None:
        for strategy in DECLARED_STRATEGIES:
            with self.subTest(strategy=strategy.name):
                self.assertTrue(strategy.escalation_cost.is_positive)


class NoProviderBehaviourTests(unittest.TestCase):
    def test_the_candidate_identifier_cannot_change_the_outcome(self) -> None:
        strategy = a_strategy()
        state = {
            "current_success_probability": strategy.initial_success_probability,
            "task_value": Money("20.00"),
            "remaining_budget": Money("2.00"),
            "capability_step_count": 0,
            "max_capability_steps": POLICY.max_capability_steps,
        }
        outcomes = set()
        for name in ("a", "zzz", "hedera-ish", "the-graph-ish", "x402-ish"):
            candidate = Candidate(name, strategy.escalation_cost,
                                  strategy.escalated_success_probability)
            s = select_capability(
                assessments=[assess(candidate=candidate, **state)], **state
            )
            outcomes.add((s.outcome, s.selected.net_expected_value))
        self.assertEqual(len(outcomes), 1)


if __name__ == "__main__":
    unittest.main()
