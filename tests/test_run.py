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
    return run(
        task or a_task(), strategies, ScriptedSimulator(script),
        record_directory=None,
    )


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


class TheRuleRunsAfterAVerdictTests(unittest.TestCase):
    """§2.5 decides from a verdict. Before the opening attempt there is none.

    An earlier version applied the rule to the opening attempt against a
    synthetic probability of zero, which denied a low-value task its first
    selected attempt under a rule authorized only for additional expenditure.
    """

    def test_the_opening_attempt_carries_no_economic_decision(self) -> None:
        record = a_run([WON])
        self.assertIsNone(record.steps[0].decision)
        self.assertTrue(record.steps[0].bought)

    def test_every_later_step_does_carry_one(self) -> None:
        for step in a_run([LOST, PARTIAL, WON]).steps[1:]:
            with self.subTest(step=step.number):
                self.assertIsNotNone(step.decision)

    def test_a_low_value_task_still_gets_its_opening_attempt(self) -> None:
        # The rule may refuse to spend *more*; it does not gate the first
        # attempt, which §2's pipeline places before any decision.
        record = a_run([WON], task=a_task(task_value=Money("0.05")))
        self.assertTrue(record.steps[0].bought)
        self.assertEqual(record.spent, Money("0.02"))

    def test_a_low_value_task_is_refused_further_spending(self) -> None:
        record = a_run([LOST] + [PARTIAL] * 5, task=a_task(task_value=Money("0.30")))
        self.assertIs(record.outcome, RunOutcome.STOPPED)
        self.assertEqual(record.spent, Money("0.02"))


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


class AStopTerminatesTheRunTests(unittest.TestCase):
    """§2.5: "Terminate and report the task incomplete." Not a suggestion.

    An earlier version treated a Stop as "skip this candidate", which turned the
    rule's only refusal into advice and let a run continue — and even succeed —
    after being told to stop.
    """

    def test_a_value_condition_stop_ends_the_run(self) -> None:
        record = a_run([LOST] + [PARTIAL] * 5, task=a_task(task_value=Money("0.30")))
        self.assertIs(record.outcome, RunOutcome.STOPPED)
        last = record.steps[-1]
        self.assertIs(last.decision.decision, Decision.STOP)
        self.assertFalse(last.bought)

    def test_nothing_is_bought_after_a_stop(self) -> None:
        record = a_run([LOST] + [PARTIAL] * 5, task=a_task(task_value=Money("0.30")))
        stopped_at = next(
            i for i, s in enumerate(record.steps)
            if s.decision is not None and s.decision.decision is Decision.STOP
        )
        self.assertEqual(stopped_at, len(record.steps) - 1)

    def test_a_budget_condition_stop_ends_the_run(self) -> None:
        record = a_run([LOST] * 6, task=a_task(budget=Money("0.09")))
        self.assertIs(record.outcome, RunOutcome.STOPPED)
        self.assertIn(
            FailedCondition.BUDGET, record.steps[-1].decision.failed_conditions
        )


class SelectionPassesOverWhatIsNotWorthRulingOnTests(unittest.TestCase):
    def test_a_useless_candidate_is_passed_over_in_selection(self) -> None:
        # Progressive Escalation offers no gain over an escalated Direct Attempt
        # (both 0.55) and is refused, but Exhaustive Attempt at 0.75 is still
        # worth buying. Stopping at the first refusal would leave the task
        # unfinished with money unspent.
        # Direct Attempt is bought and escalated, both fall short. Progressive
        # Escalation offers no gain over it (both 0.55) and is refused. If the
        # run stopped there it would leave the task unfinished with $1.90
        # unspent — but Exhaustive Attempt at 0.75 is still worth buying, and
        # it succeeds.
        # Progressive Escalation offers 0.55 against 0.55 already achieved, so
        # selection never offers it to the rule — a Stop would have ended the
        # run. It is recorded as passed over, and Exhaustive Attempt is chosen.
        record = a_run([LOST, PARTIAL, WON])
        names = [step.strategy_name for step in record.steps]
        self.assertIn("Exhaustive Attempt", names)
        self.assertNotIn("Progressive Escalation", names)
        self.assertTrue(record.succeeded)
        self.assertIn("Passed over", record.steps[-1].selection_reason)
        self.assertIn("Progressive Escalation", record.steps[-1].selection_reason)

    def test_a_strategy_is_never_tried_twice(self) -> None:
        record = a_run([PARTIAL] * 8)
        seen = [(s.strategy_name, s.escalating) for s in record.steps]
        self.assertEqual(len(seen), len(set(seen)))

    def test_the_summary_reason_explains_the_ending_not_the_cheapest_leftover(self) -> None:
        # The recorded §2.5 decision speaks about whichever candidate was
        # cheapest, which need not be the one whose unaffordability ended the
        # run. The summary must name every remaining candidate and why.
        record = a_run([LOST] * 6)
        self.assertIn("Nothing left is worth selecting", record.reason)
        self.assertIn("Exhaustive Attempt", record.reason)
        self.assertIn("only", record.reason)

    def test_a_run_ends_when_nothing_is_left_to_select(self) -> None:
        record = a_run([PARTIAL] * 8, task=a_task(budget=Money("100.00")))
        self.assertIs(record.outcome, RunOutcome.STOPPED)

    def test_no_strategies_at_all_stops_with_a_recorded_reason(self) -> None:
        # §2.6: the record must say why, even when nothing was attempted.
        record = a_run([], strategies=())
        self.assertIs(record.outcome, RunOutcome.STOPPED)
        self.assertEqual(len(record.steps), 1)
        self.assertIn("No strategy is affordable", record.steps[0].selection_reason)

    def test_an_unaffordable_budget_records_why_nothing_happened(self) -> None:
        record = a_run([], task=a_task(budget=Money("0.01")))
        self.assertEqual(len(record.as_dict()["steps"]), 1)
        self.assertIn("affordable", record.as_dict()["steps"][0]["selection_reason"])


class DeterminismTests(unittest.TestCase):
    def test_the_same_scenario_gives_the_same_run(self) -> None:
        outcomes = set()
        for _ in range(20):
            record = a_run([LOST, PARTIAL, WON])
            outcomes.add((record.outcome, record.spent, len(record.steps), record.reason))
        self.assertEqual(len(outcomes), 1)


class TheRunRecordTests(unittest.TestCase):
    """Criterion 14 and §2.6: every decision recomputable from the record."""

    def test_every_step_records_why_its_candidate_was_selected(self) -> None:
        # §2.6 requires "the strategy chosen and why", not only the economics.
        for step in a_run([LOST, PARTIAL, WON]).steps:
            with self.subTest(step=step.number):
                self.assertTrue(step.selection_reason)

    def test_the_record_names_what_selection_passed_over(self) -> None:
        record = a_run([LOST, PARTIAL, WON])
        self.assertIn("Passed over", record.steps[-1].selection_reason)

    def test_a_step_has_an_attempt_only_if_it_bought_one(self) -> None:
        record = a_run([LOST] * 6, task=a_task(budget=Money("0.09")))
        for step in (s for s in record.steps if s.decision is not None):
            with self.subTest(step=step.number):
                if step.decision.decision is Decision.STOP:
                    self.assertIsNone(step.attempt)
                    self.assertIsNone(step.evaluation)
                else:
                    self.assertIsNotNone(step.attempt)
                    self.assertIsNotNone(step.evaluation)

    def test_every_decision_can_be_recomputed_from_the_record(self) -> None:
        for step in (s for s in a_run([LOST, PARTIAL, WON]).steps if s.decision):
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
        data = a_run([LOST, PARTIAL, WON]).as_dict()
        self.assertIsInstance(data["spent"], str)
        self.assertIsInstance(data["task"]["budget"], str)
        self.assertIsInstance(
            data["steps"][1]["decision"]["incremental_expected_value"], str
        )

    def test_the_json_records_which_condition_failed(self) -> None:
        # Removing failed_conditions from the JSON left all 33 loop and CLI
        # tests passing: the "carries everything" test checked only the six
        # numbers, and the recomputation test only the verdict. §2.5 requires a
        # Stop to record which condition failed, so it is asserted directly.
        record = a_run([LOST] * 6, task=a_task(budget=Money("0.09")))
        stops = [
            step for step in record.as_dict()["steps"]
            if step["decision"] and step["decision"]["verdict"] == "stop"
        ]
        self.assertTrue(stops, "this scenario should end in a stop")
        for step in stops:
            with self.subTest(step=step["number"]):
                self.assertIn("failed_conditions", step["decision"])
                self.assertTrue(
                    step["decision"]["failed_conditions"],
                    "a stop must say which condition failed",
                )
                for condition in step["decision"]["failed_conditions"]:
                    self.assertIn(condition, {"budget", "value"})

    def test_an_escalate_records_no_failed_conditions(self) -> None:
        record = a_run([LOST, PARTIAL, WON])
        for step in record.as_dict()["steps"]:
            if step["decision"] and step["decision"]["verdict"] == "escalate":
                with self.subTest(step=step["number"]):
                    self.assertEqual(step["decision"]["failed_conditions"], [])

    def test_a_value_stop_and_a_budget_stop_are_distinguishable_in_json(self) -> None:
        by_value = a_run([LOST] + [PARTIAL] * 5, task=a_task(task_value=Money("0.30")))
        by_budget = a_run([LOST] * 6, task=a_task(budget=Money("0.09")))
        self.assertIn(
            "value", by_value.as_dict()["steps"][-1]["decision"]["failed_conditions"]
        )
        self.assertIn(
            "budget", by_budget.as_dict()["steps"][-1]["decision"]["failed_conditions"]
        )

    def test_the_json_carries_everything_a_decision_was_made_from(self) -> None:
        decision = a_run([LOST, PARTIAL, WON]).as_dict()["steps"][1]["decision"]
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
            if step["decision"] is None:
                continue
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
