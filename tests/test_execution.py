"""The simulator is controllable, deterministic, and invents nothing.

TASK-001 §2.3 and criterion 3: success, failure and partial progress must each
be exercisable on demand, and the same script must produce the same run twice.
"""

import doctest
import unittest

from radhanite import execution as execution_module
from radhanite.execution import Attempt, Observation, ScriptedSimulator
from radhanite.money import Money
from radhanite.probability import Probability
from radhanite.strategy import DECLARED_STRATEGIES, Strategy

CHEAP = DECLARED_STRATEGIES[0]
MIDDLE = DECLARED_STRATEGIES[1]

WON = Observation(satisfied=("tests pass",), note="the suite went green")
PARTIAL = Observation(satisfied=("code compiles",), note="it builds, tests still red")
LOST = Observation(satisfied=(), note="nothing worked")


class ObservationTests(unittest.TestCase):
    def test_conditions_are_held_as_a_set_of_trimmed_strings(self) -> None:
        observation = Observation(satisfied=[" tests pass ", "code compiles"], note="x")
        self.assertEqual(observation.satisfied, frozenset({"tests pass", "code compiles"}))

    def test_achieving_nothing_is_a_valid_observation(self) -> None:
        self.assertEqual(Observation(satisfied=(), note="nothing").satisfied, frozenset())

    def test_a_bare_string_of_conditions_is_refused(self) -> None:
        # Would otherwise become a set of single characters.
        with self.assertRaises(TypeError):
            Observation(satisfied="tests pass", note="x")

    def test_non_strings_and_blanks_are_refused(self) -> None:
        with self.assertRaises(TypeError):
            Observation(satisfied=(1,), note="x")
        with self.assertRaises(ValueError):
            Observation(satisfied=("  ",), note="x")

    def test_a_note_is_required(self) -> None:
        with self.assertRaises(ValueError):
            Observation(satisfied=("tests pass",), note="   ")


class DrivableOnDemandTests(unittest.TestCase):
    """Criterion 3: success, failure and partial progress, each on demand."""

    def test_each_shape_of_result_can_be_produced(self) -> None:
        for observation in (WON, PARTIAL, LOST):
            with self.subTest(note=observation.note):
                simulator = ScriptedSimulator([observation])
                self.assertEqual(
                    simulator.execute(CHEAP, escalated=False).observation, observation
                )

    def test_a_script_is_followed_in_order(self) -> None:
        script = [LOST, PARTIAL, WON]
        simulator = ScriptedSimulator(script)
        produced = [
            simulator.execute(CHEAP, escalated=False).observation for _ in script
        ]
        self.assertEqual(produced, script)

    def test_remaining_counts_down(self) -> None:
        simulator = ScriptedSimulator([WON, LOST])
        self.assertEqual(simulator.remaining, 2)
        simulator.execute(CHEAP, escalated=False)
        self.assertEqual(simulator.remaining, 1)


class ChargesTheDeclaredPriceTests(unittest.TestCase):
    def test_an_initial_attempt_costs_the_initial_price(self) -> None:
        attempt = ScriptedSimulator([WON]).execute(MIDDLE, escalated=False)
        self.assertEqual(attempt.cost, Money("0.10"))
        self.assertEqual(attempt.success_probability, Probability("0.55"))
        self.assertFalse(attempt.escalated)

    def test_an_escalated_attempt_costs_the_escalation_price(self) -> None:
        attempt = ScriptedSimulator([WON]).execute(MIDDLE, escalated=True)
        self.assertEqual(attempt.cost, Money("0.40"))
        self.assertEqual(attempt.success_probability, Probability("0.85"))
        self.assertTrue(attempt.escalated)

    def test_the_simulator_invents_no_figures_of_its_own(self) -> None:
        strategy = Strategy(
            name="Made Up",
            initial_cost=Money("1.23"),
            initial_success_probability=Probability("0.11"),
            escalation_cost=Money("4.56"),
            escalated_success_probability=Probability("0.99"),
        )
        attempt = ScriptedSimulator([LOST]).execute(strategy, escalated=False)
        self.assertEqual(attempt.strategy_name, "Made Up")
        self.assertEqual(attempt.cost, Money("1.23"))
        self.assertEqual(attempt.success_probability, Probability("0.11"))


class DeterminismTests(unittest.TestCase):
    def test_the_same_script_produces_the_same_run(self) -> None:
        script = [LOST, PARTIAL, WON]
        runs = set()
        for _ in range(20):
            simulator = ScriptedSimulator(script)
            runs.add(
                tuple(
                    (a.observation, a.cost, a.success_probability)
                    for a in (
                        simulator.execute(MIDDLE, escalated=bool(i % 2))
                        for i in range(len(script))
                    )
                )
            )
        self.assertEqual(len(runs), 1)

    def test_nothing_is_sampled_against_the_stated_probability(self) -> None:
        # A simulator that rolled dice against a strategy's stated chance would
        # make the economic loop untestable.
        never_works = Strategy(
            name="Hopeless",
            initial_cost=Money("0.01"),
            initial_success_probability=Probability("0"),
            escalation_cost=Money("0.01"),
            escalated_success_probability=Probability("0"),
        )
        for _ in range(20):
            attempt = ScriptedSimulator([WON]).execute(never_works, escalated=False)
            self.assertEqual(attempt.observation.satisfied, frozenset({"tests pass"}))

    def test_two_simulators_do_not_interfere(self) -> None:
        script = [WON, LOST]
        first, second = ScriptedSimulator(script), ScriptedSimulator(script)
        first.execute(CHEAP, escalated=False)
        self.assertEqual(first.remaining, 1)
        self.assertEqual(second.remaining, 2)
        self.assertEqual(
            second.execute(CHEAP, escalated=False).observation, WON
        )

    def test_changing_the_source_list_afterwards_changes_nothing(self) -> None:
        script = [WON]
        simulator = ScriptedSimulator(script)
        script.append(LOST)
        self.assertEqual(simulator.remaining, 1)


class WhatIsValidatedIsWhatIsStoredTests(unittest.TestCase):
    """A sequence read twice could store something that was never checked."""

    def test_a_sequence_that_changes_between_reads_cannot_smuggle_anything_in(self) -> None:
        # A genuine Sequence whose contents differ on a second traversal. The
        # simulator used to validate the argument and then copy it separately,
        # so it could store something it had never checked.
        import collections.abc

        class ShiftingSequence(collections.abc.Sequence):
            def __init__(self):
                self.traversals = 0
                self._first = [WON]
                self._later = ["not-an-observation"]

            def _contents(self):
                return self._first if self.traversals == 0 else self._later

            def __len__(self):
                return len(self._contents())

            def __getitem__(self, index):
                contents = self._contents()
                item = contents[index]
                if index == len(contents) - 1:
                    self.traversals += 1
                return item

        shifting = ShiftingSequence()
        simulator = ScriptedSimulator(shifting)
        self.assertGreaterEqual(shifting.traversals, 1)

        # Whatever was read is what was kept, and it was checked.
        attempt = simulator.execute(CHEAP, escalated=False)
        self.assertIsInstance(attempt.observation, Observation)
        self.assertEqual(attempt.observation, WON)

    def test_an_invalid_element_is_refused_however_late_it_appears(self) -> None:
        with self.assertRaises(TypeError):
            ScriptedSimulator([WON, PARTIAL, "not-an-observation"])

    def test_a_sequence_whose_first_read_is_invalid_is_refused(self) -> None:
        with self.assertRaises(TypeError):
            ScriptedSimulator(["not-an-observation"])


class RefusalTests(unittest.TestCase):
    def test_running_past_the_end_of_the_script_is_a_fault(self) -> None:
        simulator = ScriptedSimulator([WON])
        simulator.execute(CHEAP, escalated=False)
        with self.assertRaises(RuntimeError):
            simulator.execute(CHEAP, escalated=False)

    def test_an_unordered_script_is_refused(self) -> None:
        with self.assertRaises(TypeError):
            ScriptedSimulator({WON, LOST})

    def test_an_empty_script_is_allowed_until_something_asks(self) -> None:
        simulator = ScriptedSimulator([])
        self.assertEqual(simulator.remaining, 0)
        with self.assertRaises(RuntimeError):
            simulator.execute(CHEAP, escalated=False)

    def test_something_other_than_a_strategy_is_refused(self) -> None:
        with self.assertRaises(TypeError):
            ScriptedSimulator([WON]).execute("cheap", escalated=False)


class AttemptTests(unittest.TestCase):
    def test_ordinary_assignment_and_rehydration_are_refused(self) -> None:
        # Bounded, not absolute: object.__setattr__ and ctypes remain open by
        # design. radhanite/_immutable.py states exactly what is prevented.
        attempt = ScriptedSimulator([WON]).execute(CHEAP, escalated=False)
        with self.assertRaises(Exception):
            attempt.cost = Money("999.00")
        with self.assertRaises(AttributeError):
            attempt.__dict__["cost"] = Money("999.00")
        with self.assertRaises(TypeError):
            attempt.__setstate__({"cost": Money("999.00")})

    def test_an_attempt_reads_as_a_sentence(self) -> None:
        attempt = ScriptedSimulator([PARTIAL]).execute(MIDDLE, escalated=True)
        rendered = str(attempt)
        for fragment in ("Progressive Escalation", "escalated", "0.85", "$0.40", "tests still red"):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, rendered)


def load_tests(loader, tests, ignore):
    tests.addTests(
        doctest.DocTestSuite(execution_module, optionflags=doctest.ELLIPSIS)
    )
    return tests
