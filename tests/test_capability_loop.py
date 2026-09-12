"""TASK-007 final loop — critical orchestration behavior.

**Implementation agent: Manus.**

These tests cover only the minimum provider-neutral loop: precedence, TASK-006
selection reuse, one execution per iteration, updater sequencing, accounting,
history, terminal classification, and termination safeguards.
"""

from __future__ import annotations

import unittest
from unittest.mock import patch

from radhanite import loop as loop_module
from radhanite.capability import Candidate
from radhanite.capability_execution import ExecutionResult
from radhanite.money import Money
from radhanite.policy import RunPolicy
from radhanite.probability import Probability
from radhanite.runstate import RunState, RunStatus, begin_run
from radhanite.selection import SelectionOutcome
from radhanite.loop import TaskStateUpdate, run_capability_loop


class CandidateSourceFixture:
    def __init__(self, offers: list[tuple[Candidate, ...]]) -> None:
        self.offers = list(offers)
        self.calls: list[tuple[object, RunState]] = []

    def get_candidates(self, task_state: object, run_state: RunState):
        self.calls.append((task_state, run_state))
        if self.offers:
            return self.offers.pop(0)
        return ()


class ExecutorFixture:
    def __init__(self, results: list[ExecutionResult]) -> None:
        self.results = list(results)
        self.calls: list[tuple[Candidate, RunState, Money]] = []

    def execute(
        self,
        selected_candidate: Candidate,
        current_state: RunState,
        maximum_authorized_cost: Money,
    ) -> ExecutionResult:
        self.calls.append((selected_candidate, current_state, maximum_authorized_cost))
        return self.results.pop(0)


class UpdaterFixture:
    def __init__(self, updates: list[TaskStateUpdate]) -> None:
        self.updates = list(updates)
        self.calls: list[tuple[object, ExecutionResult]] = []

    def update(self, previous_task_state: object, execution_result: ExecutionResult):
        self.calls.append((previous_task_state, execution_result))
        return self.updates.pop(0)


def candidate(identifier: str, cost: str = "1.00", probability: str = "0.60") -> Candidate:
    return Candidate(identifier, Money(cost), Probability(probability))


def successful(cost: str = "1.00") -> ExecutionResult:
    return ExecutionResult(True, Money(cost), {"outcome": "success"})


def failed(cost: str = "0.00") -> ExecutionResult:
    return ExecutionResult(False, Money(cost), {"outcome": "failure"})


def a_run(**overrides) -> RunState:
    arguments = {
        "task_value": Money("100.00"),
        "initial_budget": Money("10.00"),
        "remaining_budget": Money("10.00"),
        "policy": RunPolicy(max_capability_steps=4),
        "task_state": {"phase": 0},
        "current_success_probability": Probability("0.10"),
    }
    arguments.update(overrides)
    if "status" not in arguments:
        return begin_run(**arguments)
    initial_budget = arguments["initial_budget"]
    return RunState(
        total_spend=initial_budget - arguments["remaining_budget"],
        consumed_candidate_ids=(),
        capability_step_count=0,
        history=(),
        **arguments,
    )


class Task007FinalLoopTests(unittest.TestCase):
    def test_already_complete_precedes_candidates_and_execution(self) -> None:
        run = a_run(status=RunStatus.TASK_COMPLETE)
        source = CandidateSourceFixture([(candidate("unused"),)])
        executor = ExecutorFixture([successful()])
        updater = UpdaterFixture([])

        result = run_capability_loop(
            state=run, candidate_source=source, executor=executor, updater=updater
        )

        self.assertIs(result, run)
        self.assertEqual(source.calls, [])
        self.assertEqual(executor.calls, [])
        self.assertEqual(updater.calls, [])

    def test_successful_execution_calls_updater_and_completes(self) -> None:
        source = CandidateSourceFixture([(candidate("one"),)])
        executor = ExecutorFixture([successful()])
        updater = UpdaterFixture([
            TaskStateUpdate({"phase": 1}, Probability("0.90"), True)
        ])

        result = run_capability_loop(
            state=a_run(), candidate_source=source, executor=executor, updater=updater
        )

        self.assertIs(result.status, RunStatus.TASK_COMPLETE)
        self.assertEqual(result.task_state, {"phase": 1})
        self.assertEqual(result.current_success_probability, Probability("0.90"))
        self.assertEqual(len(result.history), 1)
        self.assertEqual(len(updater.calls), 1)
        self.assertIs(updater.calls[0][1], result.history[0].execution)

    def test_multiple_successful_iterations_use_one_transition_each(self) -> None:
        first = candidate("one")
        second = candidate("two")
        source = CandidateSourceFixture([(first,), (second,), ()])
        executor = ExecutorFixture([successful(), successful()])
        updater = UpdaterFixture([
            TaskStateUpdate({"phase": 1}, Probability("0.30"), False),
            TaskStateUpdate({"phase": 2}, Probability("0.50"), False),
        ])

        result = run_capability_loop(
            state=a_run(), candidate_source=source, executor=executor, updater=updater
        )

        self.assertIs(result.status, RunStatus.ECONOMIC_STOP)
        self.assertEqual(result.capability_step_count, 2)
        self.assertEqual(result.total_spend, Money("2.00"))
        self.assertEqual(result.remaining_budget, Money("8.00"))
        self.assertEqual(len(result.history), 3)
        self.assertEqual([r.execution is None for r in result.history], [False, False, True])
        self.assertEqual(result.history[-1].selection.assessments, ())

    def test_economic_stop_retains_complete_selection(self) -> None:
        poor = candidate("poor", probability="0.10")
        source = CandidateSourceFixture([(poor,)])

        result = run_capability_loop(
            state=a_run(),
            candidate_source=source,
            executor=ExecutorFixture([]),
            updater=UpdaterFixture([]),
        )

        self.assertIs(result.status, RunStatus.ECONOMIC_STOP)
        self.assertEqual(len(result.history), 1)
        record = result.history[0]
        self.assertIsNone(record.execution)
        self.assertEqual(record.selection.outcome, SelectionOutcome.STOP)
        self.assertEqual(len(record.selection.assessments), 1)

    def test_ceiling_is_always_safety_stop(self) -> None:
        source = CandidateSourceFixture([(candidate("at-ceiling"),)])
        run = a_run(policy=RunPolicy(max_capability_steps=1), capability_step_count=1)

        result = run_capability_loop(
            state=run,
            candidate_source=source,
            executor=ExecutorFixture([]),
            updater=UpdaterFixture([]),
        )

        self.assertIs(result.status, RunStatus.SAFETY_STOP)
        self.assertEqual(result.capability_step_count, 1)
        self.assertIsNone(result.history[0].execution)

    def test_zero_step_policy_is_immediate_safety_stop(self) -> None:
        source = CandidateSourceFixture([(candidate("zero-step"),)])
        run = a_run(policy=RunPolicy(max_capability_steps=0))

        result = run_capability_loop(
            state=run,
            candidate_source=source,
            executor=ExecutorFixture([]),
            updater=UpdaterFixture([]),
        )

        self.assertIs(result.status, RunStatus.SAFETY_STOP)
        self.assertEqual(result.capability_step_count, 0)
        self.assertEqual(len(result.history), 1)
        self.assertEqual(source.calls, [])

    def test_execution_failure_terminates_and_updater_is_not_called(self) -> None:
        source = CandidateSourceFixture([(candidate("fails", cost="2.00"),)])
        executor = ExecutorFixture([failed("2.00")])
        updater = UpdaterFixture([])

        result = run_capability_loop(
            state=a_run(), candidate_source=source, executor=executor, updater=updater
        )

        self.assertIs(result.status, RunStatus.EXECUTION_FAILURE)
        self.assertEqual(result.total_spend, Money("2.00"))
        self.assertEqual(result.remaining_budget, Money("8.00"))
        self.assertEqual(result.capability_step_count, 1)
        self.assertEqual(result.consumed_candidate_ids, ("fails",))
        self.assertEqual(updater.calls, [])

    def test_zero_cost_execution_still_increments_step_count(self) -> None:
        source = CandidateSourceFixture([(candidate("free-result"),)])
        executor = ExecutorFixture([successful("0.00")])
        updater = UpdaterFixture([
            TaskStateUpdate({"phase": 1}, Probability("0.20"), True)
        ])

        result = run_capability_loop(
            state=a_run(), candidate_source=source, executor=executor, updater=updater
        )

        self.assertEqual(result.capability_step_count, 1)
        self.assertEqual(result.total_spend, Money("0.00"))

    def test_consumed_candidate_cannot_execute_again(self) -> None:
        reused = candidate("same-id")
        source = CandidateSourceFixture([(reused,), (reused,)])
        executor = ExecutorFixture([successful()])
        updater = UpdaterFixture([
            TaskStateUpdate({"phase": 1}, Probability("0.20"), False)
        ])

        result = run_capability_loop(
            state=a_run(), candidate_source=source, executor=executor, updater=updater
        )

        self.assertIs(result.status, RunStatus.SAFETY_STOP)
        self.assertEqual(len(executor.calls), 1)
        self.assertEqual(result.history[-1].selection.assessments[0].candidate.candidate_id, "same-id")

    def test_same_conceptual_capability_with_new_id_can_execute(self) -> None:
        source = CandidateSourceFixture([
            (candidate("research-1"),),
            (candidate("research-2"),),
        ])
        executor = ExecutorFixture([successful(), successful()])
        updater = UpdaterFixture([
            TaskStateUpdate({"phase": 1}, Probability("0.20"), False),
            TaskStateUpdate({"phase": 2}, Probability("0.30"), True),
        ])

        result = run_capability_loop(
            state=a_run(), candidate_source=source, executor=executor, updater=updater
        )

        self.assertIs(result.status, RunStatus.TASK_COMPLETE)
        self.assertEqual([call[0].candidate_id for call in executor.calls], ["research-1", "research-2"])

    def test_total_spend_never_exceeds_budget_and_exact_exhaustion_is_valid(self) -> None:
        first = candidate("first", cost="5.00")
        second = candidate("second", cost="5.00")
        source = CandidateSourceFixture([(first,), (second,), ()])
        executor = ExecutorFixture([successful("5.00"), successful("5.00")])
        updater = UpdaterFixture([
            TaskStateUpdate({"phase": 1}, Probability("0.20"), False),
            TaskStateUpdate({"phase": 2}, Probability("0.30"), False),
        ])

        result = run_capability_loop(
            state=a_run(), candidate_source=source, executor=executor, updater=updater
        )

        self.assertEqual(result.total_spend, Money("10.00"))
        self.assertEqual(result.remaining_budget, Money("0.00"))
        self.assertLessEqual(result.total_spend, result.initial_budget)

    def test_pre_loop_spend_is_preserved(self) -> None:
        source = CandidateSourceFixture([(candidate("remaining", cost="5.00"),)])
        executor = ExecutorFixture([successful("5.00")])
        updater = UpdaterFixture([
            TaskStateUpdate({"phase": 1}, Probability("0.20"), True)
        ])

        result = run_capability_loop(
            state=a_run(remaining_budget=Money("5.00")),
            candidate_source=source,
            executor=executor,
            updater=updater,
        )

        self.assertEqual(result.total_spend, Money("10.00"))
        self.assertEqual(result.remaining_budget, Money("0.00"))
        self.assertEqual(result.history[0].before.total_spend, Money("5.00"))

    def test_task006_selector_is_reused_not_reimplemented(self) -> None:
        source = CandidateSourceFixture([(candidate("selected"),)])
        executor = ExecutorFixture([successful()])
        updater = UpdaterFixture([
            TaskStateUpdate({"phase": 1}, Probability("0.20"), True)
        ])

        with patch.object(
            loop_module, "select_capability", wraps=loop_module.select_capability
        ) as selector:
            run_capability_loop(
                state=a_run(),
                candidate_source=source,
                executor=executor,
                updater=updater,
            )

        selector.assert_called_once()


if __name__ == "__main__":
    unittest.main()
