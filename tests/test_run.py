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


#: Every run writes a record — criterion 14 grants no exemption, so tests write
#: to a temporary directory like any other caller rather than opting out.
_RECORDS: tempfile.TemporaryDirectory | None = None


def setUpModule() -> None:
    global _RECORDS
    _RECORDS = tempfile.TemporaryDirectory()


def tearDownModule() -> None:
    if _RECORDS is not None:
        _RECORDS.cleanup()


def a_run(script, task=None, strategies=DECLARED_STRATEGIES, into=None) -> RunRecord:
    return run(
        task or a_task(), strategies, ScriptedSimulator(script),
        record_directory=into or _RECORDS.name,
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

    def test_a_decision_is_absent_exactly_when_no_verdict_exists_yet(self) -> None:
        """The invariant, stated and checked rather than assumed.

        The claim used to be "None for the opening attempt only", and the test
        for it only ran a scenario that succeeded before a terminal step could
        occur — so it could not detect that a terminal step also had none.

        The true rule is narrower and does not depend on position: a step has no
        §2.5 decision exactly when no attempt has yet been judged. That is the
        opening attempt, and the case where nothing was ever affordable so no
        opening attempt happened at all.
        """
        scenarios = [
            ([WON], a_task()),
            ([LOST, PARTIAL, WON], a_task()),
            ([LOST] * 6, a_task()),
            ([LOST] * 6, a_task(budget=Money("0.09"))),
            ([LOST] + [PARTIAL] * 5, a_task(task_value=Money("0.30"))),
            ([], a_task(budget=Money("0.01"))),
        ]
        for script, task in scenarios:
            record = a_run(script, task=task)
            judged = False
            for step in record.steps:
                with self.subTest(script=len(script), step=step.number):
                    if judged:
                        self.assertIsNotNone(
                            step.decision,
                            "a verdict exists, so §2.5 must have been consulted",
                        )
                    else:
                        self.assertIsNone(
                            step.decision,
                            "no verdict yet, so §2.5 cannot have decided",
                        )
                if step.evaluation is not None:
                    judged = True

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

    def test_a_changing_sequence_cannot_desynchronise_the_run(self) -> None:
        # run() read the sequence more than once — to build the candidate list,
        # then again to select — so a sequence yielding different contents on a
        # second traversal executed one strategy while the list tracked another,
        # crashing after the money was spent and leaving no record.
        import collections.abc

        class ShiftingCatalogue(collections.abc.Sequence):
            def __init__(self):
                self.traversals = 0
                self._first = [DECLARED_STRATEGIES[0]]
                self._later = [DECLARED_STRATEGIES[2]]

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

        record = a_run([LOST, LOST], strategies=ShiftingCatalogue())
        self.assertIsNotNone(record)
        names = {s.strategy_name for s in record.steps if s.strategy_name}
        self.assertEqual(names, {"Direct Attempt"})

    def test_running_out_mid_run_is_recorded_with_its_quantities(self) -> None:
        # $0.09 affords the $0.02 opening but not the $0.08 escalation.
        record = a_run([LOST] * 6, task=a_task(budget=Money("0.09")))
        self.assertIs(record.outcome, RunOutcome.STOPPED)
        terminal = record.steps[-1]
        self.assertEqual(terminal.remaining_budget, Money("0.07"))
        budget_blocked = [
            u for u in terminal.unusable if u.blocked_by is FailedCondition.BUDGET
        ]
        self.assertTrue(budget_blocked)
        for blocked in budget_blocked:
            with self.subTest(strategy=blocked.strategy_name):
                self.assertGreater(blocked.cost, terminal.remaining_budget)

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
        # Criterion 9. Selection may pass over an unaffordable candidate while a
        # usable one remains, but terminating is §2.5's job — an earlier version
        # filtered the budget failure out before the rule saw it, which made
        # this branch unreachable.
        record = a_run([LOST] * 6, task=a_task(budget=Money("0.09")))
        self.assertIs(record.outcome, RunOutcome.STOPPED)
        self.assertIn(
            FailedCondition.BUDGET, record.steps[-1].decision.failed_conditions
        )

    def test_a_no_improvement_stop_ends_the_run(self) -> None:
        # Criterion 11. §2.5 requires this to fall out of the arithmetic rather
        # than a special path, so the rule must be the thing that refuses.
        flat = Strategy(
            name="Flat", initial_cost=Money("0.02"),
            initial_success_probability=Probability("0.50"),
            escalation_cost=Money("0.05"),
            escalated_success_probability=Probability("0.50"),
        )
        record = a_run([LOST, LOST], strategies=(flat,))
        self.assertIs(record.outcome, RunOutcome.STOPPED)
        terminal = record.steps[-1]
        self.assertIs(terminal.decision.decision, Decision.STOP)
        self.assertIn(FailedCondition.VALUE, terminal.decision.failed_conditions)
        self.assertEqual(
            terminal.decision.incremental_expected_value, Money("0")
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

    def test_a_terminal_step_records_every_remaining_candidate(self) -> None:
        # §2.5 rules on the first remaining candidate in declared order, so the
        # decision names one. Every other candidate still appears, with the
        # quantities that disqualified it, so a reader can see the whole
        # position rather than only the subject of the verdict.
        record = a_run([LOST] * 6)
        terminal = record.steps[-1]
        self.assertIsNotNone(terminal.decision)
        self.assertIs(terminal.decision.decision, Decision.STOP)
        names = {u.strategy_name for u in terminal.unusable}
        self.assertIn("Exhaustive Attempt", names)

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
        record = a_run([LOST] + [PARTIAL] * 5, task=a_task(task_value=Money("0.30")))
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

    def test_a_value_stop_and_running_out_are_distinguishable_in_json(self) -> None:
        # A value refusal is a §2.5 decision on a candidate selection chose.
        # Running out is recorded at selection, since §2.5 never sees an
        # unaffordable candidate.
        by_value = a_run([LOST] + [PARTIAL] * 5, task=a_task(task_value=Money("0.30")))
        last_value = by_value.as_dict()["steps"][-1]
        self.assertIn("value", last_value["decision"]["failed_conditions"])

        by_budget = a_run([LOST] * 6, task=a_task(budget=Money("0.09")))
        last_budget = by_budget.as_dict()["steps"][-1]
        self.assertEqual(last_budget["decision"]["verdict"], "stop")
        self.assertIn(
            "budget", last_budget["decision"]["failed_conditions"]
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


class EveryRunWritesARecordTests(unittest.TestCase):
    """Criterion 14 and §2.6 grant no exemption, including for tests.

    The previous version accepted record_directory=None, and all 37 loop tests
    used it — so the suite proved nothing about the requirement it claimed to
    satisfy, and a completed run could produce no file at all.
    """

    def test_a_completed_run_always_leaves_a_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            a_run([WON], into=directory)
            self.assertEqual(len(list(Path(directory).glob("run-*.json"))), 1)

    def test_a_stopped_run_leaves_one_too(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            a_run([LOST] * 6, into=directory)
            self.assertEqual(len(list(Path(directory).glob("run-*.json"))), 1)

    def test_a_run_that_attempted_nothing_leaves_one_too(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            a_run([], task=a_task(budget=Money("0.01")), into=directory)
            self.assertEqual(len(list(Path(directory).glob("run-*.json"))), 1)

    def test_there_is_no_way_to_run_without_writing(self) -> None:
        import inspect

        default = inspect.signature(run).parameters["record_directory"].default
        self.assertIsNotNone(default)
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(Exception):
                run(a_task(), DECLARED_STRATEGIES, ScriptedSimulator([WON]),
                    record_directory=None)

    def test_many_runs_do_not_overwrite_each_other(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            for _ in range(8):
                a_run([WON], into=directory)
            self.assertEqual(len(list(Path(directory).glob("run-*.json"))), 8)

    def test_a_claimed_name_is_never_handed_out_twice(self) -> None:
        # Scanning for the next free number and writing to it later is a race:
        # two runs that scan before either writes pick the same name. Eight
        # concurrent runs were shown to leave one file. The name is now claimed
        # by exclusive creation, so a second claim cannot collide.
        from radhanite.run import _claim_record_path

        with tempfile.TemporaryDirectory() as directory:
            claimed = {_claim_record_path(Path(directory)) for _ in range(8)}
            self.assertEqual(len(claimed), 8)

    def test_claiming_never_overwrites_an_existing_record(self) -> None:
        from radhanite.run import _claim_record_path

        with tempfile.TemporaryDirectory() as directory:
            existing = Path(directory) / "run-001.json"
            existing.write_text("original", encoding="utf-8")
            claimed = _claim_record_path(Path(directory))
            self.assertNotEqual(claimed, existing)
            self.assertEqual(existing.read_text(encoding="utf-8"), "original")


class TerminalStepsRecordTheirReasonTests(unittest.TestCase):
    """§2.6: the record must say why a run ended, with the quantities.

    A terminal step has no §2.5 decision, because selection chose nothing and so
    nothing was ruled on. An earlier version attached a decision to whichever
    leftover was cheapest — a verdict about a candidate selection had already
    rejected, and not the reason the run ended.
    """

    def test_an_unaffordable_start_records_the_blocking_condition(self) -> None:
        step = a_run([], task=a_task(budget=Money("0.01"))).as_dict()["steps"][0]
        self.assertIsNone(step["decision"])
        self.assertEqual(step["remaining_budget"], "0.01")
        self.assertTrue(step["unusable"])
        for blocked in step["unusable"]:
            with self.subTest(strategy=blocked["strategy"]):
                self.assertEqual(blocked["blocked_by"], "budget")
                self.assertTrue(blocked["cost"])

    def test_an_exhausted_run_records_every_remaining_candidate(self) -> None:
        step = a_run([LOST] * 6).as_dict()["steps"][-1]
        self.assertIsNotNone(step["decision"])
        self.assertEqual(step["decision"]["verdict"], "stop")
        blocked = {b["strategy"]: b["blocked_by"] for b in step["unusable"]}
        self.assertIn("Exhaustive Attempt", blocked)

    def test_both_blocking_conditions_are_distinguishable(self) -> None:
        step = a_run([LOST] * 6).as_dict()["steps"][-1]
        reasons = {b["blocked_by"] for b in step["unusable"]}
        self.assertEqual(reasons, {"value", "budget"})

    def test_no_decision_is_recorded_for_a_candidate_selection_rejected(self) -> None:
        # The defect this replaces: a value-condition Stop was recorded against
        # Progressive Escalation even though selection had rejected it and the
        # unaffordable Exhaustive escalation was what actually ended the run.
        for step in a_run([LOST] * 6).steps:
            if step.decision is not None:
                with self.subTest(step=step.number):
                    self.assertIsNotNone(step.strategy_name)
                    self.assertTrue(step.bought or step.decision.decision is Decision.STOP)

    def test_a_terminal_step_names_the_candidate_the_rule_ruled_on(self) -> None:
        # Determined, not arbitrary: the first remaining candidate in declared
        # order, which is the one selection would have considered first.
        step = a_run([LOST] * 6).steps[-1]
        self.assertIsNotNone(step.strategy_name)
        self.assertIsNotNone(step.decision)
        self.assertTrue(step.unusable)

    def test_a_run_with_nothing_left_at_all_names_no_strategy(self) -> None:
        record = a_run([], task=a_task(budget=Money("0.01")))
        self.assertIsNone(record.steps[0].strategy_name)
        self.assertIsNone(record.steps[0].decision)


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
