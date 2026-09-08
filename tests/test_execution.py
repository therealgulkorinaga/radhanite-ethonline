"""The simulator is controllable, deterministic, and invents nothing.

TASK-001 §2.3 and criterion 3: success, failure and partial progress must each
be exercisable on demand, and the same script must produce the same run twice.
"""

import doctest
import unittest

from radhanite import execution as execution_module
from radhanite.execution import Attempt, Outcome, ScriptedSimulator
from radhanite.money import Money
from radhanite.probability import Probability
from radhanite.strategy import DECLARED_STRATEGIES, Strategy

CHEAP = DECLARED_STRATEGIES[0]
MIDDLE = DECLARED_STRATEGIES[1]


class DrivableOnDemandTests(unittest.TestCase):
    """Criterion 3: each of the three outcomes on demand."""

    def test_every_outcome_can_be_produced(self) -> None:
        for outcome in Outcome:
            with self.subTest(outcome=outcome):
                simulator = ScriptedSimulator([outcome])
                self.assertIs(
                    simulator.execute(CHEAP, escalated=False).outcome, outcome
                )

    def test_a_script_is_followed_in_order(self) -> None:
        script = [Outcome.FAILURE, Outcome.PARTIAL_PROGRESS, Outcome.SUCCESS]
        simulator = ScriptedSimulator(script)
        produced = [
            simulator.execute(CHEAP, escalated=False).outcome for _ in script
        ]
        self.assertEqual(produced, script)

    def test_remaining_counts_down(self) -> None:
        simulator = ScriptedSimulator([Outcome.SUCCESS, Outcome.FAILURE])
        self.assertEqual(simulator.remaining, 2)
        simulator.execute(CHEAP, escalated=False)
        self.assertEqual(simulator.remaining, 1)


class ChargesTheDeclaredPriceTests(unittest.TestCase):
    def test_an_initial_attempt_costs_the_initial_price(self) -> None:
        attempt = ScriptedSimulator([Outcome.SUCCESS]).execute(
            MIDDLE, escalated=False
        )
        self.assertEqual(attempt.cost, Money("0.10"))
        self.assertEqual(attempt.success_probability, Probability("0.55"))
        self.assertFalse(attempt.escalated)

    def test_an_escalated_attempt_costs_the_escalation_price(self) -> None:
        attempt = ScriptedSimulator([Outcome.SUCCESS]).execute(
            MIDDLE, escalated=True
        )
        self.assertEqual(attempt.cost, Money("0.40"))
        self.assertEqual(attempt.success_probability, Probability("0.85"))
        self.assertTrue(attempt.escalated)

    def test_the_simulator_invents_no_figures_of_its_own(self) -> None:
        # Everything on the attempt comes from the strategy or the script.
        strategy = Strategy(
            name="Made Up",
            initial_cost=Money("1.23"),
            initial_success_probability=Probability("0.11"),
            escalation_cost=Money("4.56"),
            escalated_success_probability=Probability("0.99"),
        )
        attempt = ScriptedSimulator([Outcome.FAILURE]).execute(
            strategy, escalated=False
        )
        self.assertEqual(attempt.strategy_name, "Made Up")
        self.assertEqual(attempt.cost, Money("1.23"))
        self.assertEqual(attempt.success_probability, Probability("0.11"))


class DeterminismTests(unittest.TestCase):
    def test_the_same_script_produces_the_same_run(self) -> None:
        script = [Outcome.FAILURE, Outcome.PARTIAL_PROGRESS, Outcome.SUCCESS]
        runs = []
        for _ in range(20):
            simulator = ScriptedSimulator(script)
            runs.append(
                tuple(
                    (a.outcome, a.cost, a.success_probability)
                    for a in (
                        simulator.execute(MIDDLE, escalated=bool(i % 2))
                        for i in range(len(script))
                    )
                )
            )
        self.assertEqual(len(set(runs)), 1)

    def test_nothing_is_sampled_against_the_stated_probability(self) -> None:
        # A simulator that rolled dice against a strategy's stated chance would
        # make the economic loop untestable. A strategy that "never works" still
        # reports success if the script says so.
        never_works = Strategy(
            name="Hopeless",
            initial_cost=Money("0.01"),
            initial_success_probability=Probability("0"),
            escalation_cost=Money("0.01"),
            escalated_success_probability=Probability("0"),
        )
        for _ in range(20):
            attempt = ScriptedSimulator([Outcome.SUCCESS]).execute(
                never_works, escalated=False
            )
            self.assertIs(attempt.outcome, Outcome.SUCCESS)


class RefusalTests(unittest.TestCase):
    def test_running_past_the_end_of_the_script_is_a_fault(self) -> None:
        # Not an outcome to report: whatever drives the loop asked for an
        # attempt the scenario never described.
        simulator = ScriptedSimulator([Outcome.SUCCESS])
        simulator.execute(CHEAP, escalated=False)
        with self.assertRaises(RuntimeError):
            simulator.execute(CHEAP, escalated=False)

    def test_an_unordered_script_is_refused(self) -> None:
        with self.assertRaises(TypeError):
            ScriptedSimulator({Outcome.SUCCESS, Outcome.FAILURE})

    def test_a_script_of_the_wrong_thing_is_refused(self) -> None:
        with self.assertRaises(TypeError):
            ScriptedSimulator(["success"])

    def test_an_empty_script_is_allowed_until_something_asks(self) -> None:
        simulator = ScriptedSimulator([])
        self.assertEqual(simulator.remaining, 0)
        with self.assertRaises(RuntimeError):
            simulator.execute(CHEAP, escalated=False)

    def test_something_other_than_a_strategy_is_refused(self) -> None:
        with self.assertRaises(TypeError):
            ScriptedSimulator([Outcome.SUCCESS]).execute("cheap", escalated=False)


class AttemptTests(unittest.TestCase):
    def test_an_attempt_cannot_be_changed_after_the_fact(self) -> None:
        attempt = ScriptedSimulator([Outcome.SUCCESS]).execute(
            CHEAP, escalated=False
        )
        with self.assertRaises(Exception):
            attempt.cost = Money("999.00")
        with self.assertRaises(TypeError):
            attempt.__setstate__({"cost": Money("999.00")})

    def test_an_attempt_reads_as_a_sentence(self) -> None:
        attempt = ScriptedSimulator([Outcome.FAILURE]).execute(
            MIDDLE, escalated=True
        )
        rendered = str(attempt)
        for fragment in ("Progressive Escalation", "escalated", "0.85", "$0.40", "failure"):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, rendered)


def load_tests(loader, tests, ignore):
    tests.addTests(
        doctest.DocTestSuite(execution_module, optionflags=doctest.ELLIPSIS)
    )
    return tests
