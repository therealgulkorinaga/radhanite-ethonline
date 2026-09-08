"""The loop: every purchase weighed, the ceiling never breached, everything recorded.

TASK-001 §5 deliverable 1, §2.6, and acceptance criteria 1, 12 and 14.
"""

import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from radhanite.escalation import Decision, FailedCondition
from radhanite.evaluation import Verdict
from radhanite.execution import Observation, ScriptedSimulator
from radhanite.money import Money
from radhanite.probability import Probability
from radhanite.run import RunOutcome, RunRecord, run
from radhanite.strategy import DECLARED_STRATEGIES, Strategy
from radhanite.task import Task

WON = Observation(satisfied=("tests pass",), note="the suite went green")
PARTIAL = Observation(satisfied=("code compiles",), note="it builds, tests still red")
LOST = Observation(satisfied=(), note="nothing worked")


def a_task(**overrides) -> Task:
    fields = {
        "description": "Fix GitHub issue #184",
        "budget": Money("2.00"),
        "task_value": Money("20.00"),
        "success_condition": "tests pass",
        "constraints": ("no dependency changes",),
    }
    fields.update(overrides)
    return Task(**fields)


def a_run(script, task=None, strategies=DECLARED_STRATEGIES) -> RunRecord:
    return run(task or a_task(), strategies, ScriptedSimulator(script))


class TheSuccessPathTests(unittest.TestCase):
    """Criterion 1: a task with all five inputs runs end to end."""

    def test_a_task_that_succeeds_first_time(self) -> None:
        record = a_run([WON])
        self.assertIs(record.outcome, RunOutcome.SUCCEEDED)
        self.assertTrue(record.succeeded)
        self.assertEqual(record.spent, Money("0.02"))
        self.assertEqual(record.remaining, Money("1.98"))
        self.assertEqual(len(record.steps), 1)

    def test_success_after_escalating(self) -> None:
        record = a_run([LOST, WON])
        self.assertTrue(record.succeeded)
        self.assertEqual(len(record.steps), 2)
        self.assertTrue(record.steps[1].escalating)
        self.assertEqual(record.spent, Money("0.10"))

    def test_the_run_stops_the_moment_it_succeeds(self) -> None:
        # Nothing is bought after the condition is met.
        record = a_run([WON, WON, WON])
        self.assertEqual(len(record.steps), 1)


class EveryPurchaseIsWeighedTests(unittest.TestCase):
    """Including the first. There is no free opening attempt."""

    def test_the_opening_attempt_is_weighed_like_any_other(self) -> None:
        record = a_run([WON])
        opening = record.steps[0].decision
        self.assertEqual(opening.current_success_probability, Probability("0"))
        self.assertEqual(
            opening.post_escalation_success_probability, Probability("0.35")
        )

    def test_a_task_worth_less_than_the_cheapest_attempt_buys_nothing(self) -> None:
        # 0.35 x $0.05 = $0.0175, which does not exceed the $0.02 it costs.
        record = a_run([WON], task=a_task(task_value=Money("0.05")))
        self.assertIs(record.outcome, RunOutcome.STOPPED)
        self.assertEqual(record.spent, Money("0"))
        self.assertFalse(any(step.bought for step in record.steps))

    def test_a_worthless_task_buys_nothing(self) -> None:
        record = a_run([WON], task=a_task(task_value=Money("0")))
        self.assertIs(record.outcome, RunOutcome.STOPPED)
        self.assertEqual(record.spent, Money("0"))


class TheBudgetCeilingTests(unittest.TestCase):
    """Criterion 12: never exceeded, on any path."""

    def test_spending_never_exceeds_the_budget(self) -> None:
        # Six observations covers the most a run can buy: three strategies,
        # two attempts each. A shorter script would run the simulator dry and
        # test the fixture rather than the ceiling.
        scripts = [
            [LOST] * 6,
            [PARTIAL] * 6,
            [LOST, PARTIAL, LOST, PARTIAL, LOST, PARTIAL],
            [PARTIAL, PARTIAL, PARTIAL, PARTIAL, PARTIAL, WON],
        ]
        budgets = ["0", "0.01", "0.02", "0.09", "0.10", "0.55", "2.00", "100.00"]
        for script in scripts:
            for budget in budgets:
                with self.subTest(script=len(script), budget=budget):
                    record = a_run(script, task=a_task(budget=Money(budget)))
                    self.assertLessEqual(record.spent, Money(budget))
                    self.assertFalse(record.remaining.is_negative)
                    self.assertEqual(
                        record.spent + record.remaining, Money(budget)
                    )

    def test_a_zero_budget_buys_nothing(self) -> None:
        record = a_run([WON], task=a_task(budget=Money("0")))
        self.assertIs(record.outcome, RunOutcome.STOPPED)
        self.assertEqual(record.spent, Money("0"))

    def test_the_budget_condition_is_what_stops_an_exhausted_run(self) -> None:
        # $0.09 affords the $0.02 opening but not the $0.08 escalation.
        record = a_run([LOST], task=a_task(budget=Money("0.09")))
        self.assertIs(record.outcome, RunOutcome.STOPPED)
        self.assertIn(
            FailedCondition.BUDGET, record.steps[-1].decision.failed_conditions
        )

    def test_stopping_with_money_left_is_a_correct_outcome(self) -> None:
        # PREREQ-001 §5.4: refusing to keep spending is the system working.
        record = a_run([LOST] + [PARTIAL] * 5)
        self.assertIs(record.outcome, RunOutcome.STOPPED)
        self.assertTrue(record.remaining.is_positive)


class EveryStrategyIsConsideredTests(unittest.TestCase):
    def test_a_refusal_ends_a_strategy_not_the_run(self) -> None:
        # Progressive Escalation offers no gain over an escalated Direct Attempt
        # (both 0.55) and is refused, but Exhaustive Attempt at 0.75 is still
        # worth buying. Stopping at the first refusal would leave the task
        # unfinished with money unspent.
        # Direct Attempt is bought and escalated, both fall short. Progressive
        # Escalation offers no gain over it (both 0.55) and is refused. If the
        # run stopped there it would leave the task unfinished with $1.90
        # unspent — but Exhaustive Attempt at 0.75 is still worth buying, and
        # it succeeds.
        record = a_run([LOST, PARTIAL, WON])
        names = [step.strategy_name for step in record.steps]
        self.assertIn("Exhaustive Attempt", names)
        self.assertTrue(record.succeeded)
        refused = [s for s in record.steps if not s.bought]
        self.assertTrue(refused, "the run should have refused at least one purchase")
        self.assertNotEqual(refused[0].number, len(record.steps))

    def test_a_strategy_is_never_tried_twice(self) -> None:
        record = a_run([PARTIAL] * 8)
        seen = [(s.strategy_name, s.escalating) for s in record.steps]
        self.assertEqual(len(seen), len(set(seen)))

    def test_a_run_ends_when_every_strategy_is_exhausted(self) -> None:
        record = a_run([PARTIAL] * 8, task=a_task(budget=Money("100.00")))
        self.assertIs(record.outcome, RunOutcome.STOPPED)
        self.assertIn("Every strategy has been tried", record.reason)

    def test_no_strategies_at_all_stops_immediately(self) -> None:
        record = a_run([], strategies=())
        self.assertIs(record.outcome, RunOutcome.STOPPED)
        self.assertEqual(record.steps, ())


class DeterminismTests(unittest.TestCase):
    def test_the_same_scenario_gives_the_same_run(self) -> None:
        outcomes = set()
        for _ in range(20):
            record = a_run([LOST, PARTIAL, WON])
            outcomes.add((record.outcome, record.spent, len(record.steps), record.reason))
        self.assertEqual(len(outcomes), 1)


class TheRunRecordTests(unittest.TestCase):
    """Criterion 14 and §2.6: every decision recomputable from the record."""

    def test_every_step_carries_the_decision_that_produced_it(self) -> None:
        for step in a_run([LOST, PARTIAL, WON]).steps:
            with self.subTest(step=step.number):
                self.assertIsNotNone(step.decision)
                self.assertTrue(step.decision.reason)

    def test_a_step_has_an_attempt_only_if_it_bought_one(self) -> None:
        record = a_run([LOST], task=a_task(budget=Money("0.09")))
        for step in record.steps:
            with self.subTest(step=step.number):
                if step.decision.decision is Decision.STOP:
                    self.assertIsNone(step.attempt)
                    self.assertIsNone(step.evaluation)
                else:
                    self.assertIsNotNone(step.attempt)
                    self.assertIsNotNone(step.evaluation)

    def test_every_decision_can_be_recomputed_from_the_record(self) -> None:
        for step in a_run([LOST, PARTIAL, WON]).steps:
            with self.subTest(step=step.number):
                d = step.decision
                change = (
                    d.post_escalation_success_probability
                    - d.current_success_probability
                )
                self.assertEqual(
                    d.task_value * change, d.incremental_expected_value
                )
                budget_ok = d.remaining_budget >= d.escalation_cost
                value_ok = d.incremental_expected_value > d.escalation_cost
                expected = (
                    Decision.ESCALATE if budget_ok and value_ok else Decision.STOP
                )
                self.assertEqual(d.decision, expected)

    def test_the_money_adds_up(self) -> None:
        record = a_run([LOST, PARTIAL, WON])
        charged = sum(
            (s.attempt.cost for s in record.steps if s.bought), Money("0")
        )
        self.assertEqual(charged, record.spent)


class TheJsonRecordTests(unittest.TestCase):
    def test_the_record_serialises_to_json(self) -> None:
        record = a_run([LOST, PARTIAL, WON])
        text = json.dumps(record.as_dict())
        self.assertIn("Fix GitHub issue #184", text)

    def test_amounts_are_written_as_strings_not_numbers(self) -> None:
        # A JSON number would be parsed as floating point by whoever reads it,
        # and an amount that arrives slightly wrong is the failure the money
        # type exists to prevent.
        data = a_run([WON]).as_dict()
        self.assertIsInstance(data["spent"], str)
        self.assertIsInstance(data["task"]["budget"], str)
        self.assertIsInstance(
            data["steps"][0]["decision"]["incremental_expected_value"], str
        )

    def test_the_json_carries_everything_a_decision_was_made_from(self) -> None:
        decision = a_run([WON]).as_dict()["steps"][0]["decision"]
        for quantity in (
            "current_success_probability",
            "post_escalation_success_probability",
            "task_value",
            "escalation_cost",
            "remaining_budget",
            "incremental_expected_value",
        ):
            with self.subTest(quantity=quantity):
                self.assertIn(quantity, decision)

    def test_a_decision_can_be_recomputed_from_the_json_alone(self) -> None:
        for step in a_run([LOST, PARTIAL, WON]).as_dict()["steps"]:
            with self.subTest(step=step["number"]):
                d = step["decision"]
                change = Decimal(d["post_escalation_success_probability"]) - Decimal(
                    d["current_success_probability"]
                )
                self.assertEqual(
                    Decimal(d["task_value"]) * change,
                    Decimal(d["incremental_expected_value"]),
                )
                budget_ok = Decimal(d["remaining_budget"]) >= Decimal(d["escalation_cost"])
                value_ok = Decimal(d["incremental_expected_value"]) > Decimal(
                    d["escalation_cost"]
                )
                self.assertEqual(
                    d["verdict"], "escalate" if budget_ok and value_ok else "stop"
                )

    def test_achieved_conditions_are_sorted_so_the_file_is_stable(self) -> None:
        many = Observation(satisfied=("b", "a", "c"), note="x")
        data = a_run([many] + [LOST] * 5).as_dict()
        self.assertEqual(data["steps"][0]["attempt"]["achieved"], ["a", "b", "c"])

    def test_writing_the_record_creates_the_file_and_its_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "runs" / "run-001.json"
            written = a_run([WON]).write(destination)
            self.assertEqual(written, destination)
            reloaded = json.loads(destination.read_text(encoding="utf-8"))
            self.assertEqual(reloaded["outcome"], "succeeded")


class RefusalTests(unittest.TestCase):
    def test_something_other_than_a_task_is_refused(self) -> None:
        with self.assertRaises(TypeError):
            run("fix the tests", DECLARED_STRATEGIES, ScriptedSimulator([WON]))

    def test_a_record_cannot_be_altered_by_ordinary_means(self) -> None:
        # Bounded, not absolute — radhanite/_immutable.py states the limits.
        record = a_run([WON])
        with self.assertRaises(Exception):
            record.outcome = RunOutcome.STOPPED
        with self.assertRaises(TypeError):
            record.__setstate__({"outcome": RunOutcome.STOPPED})
