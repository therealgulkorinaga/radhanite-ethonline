"""TASK-007 PR B — one provider-neutral capability execution transition.

These tests are written before the implementation. They deliberately import the
new boundary so the pre-implementation run records the expected missing-module
failure rather than silently testing the legacy TASK-001 simulator.
"""

import inspect
import unittest
from decimal import Decimal
from types import MappingProxyType
from unittest.mock import patch

import radhanite.selection as selection_module
from radhanite.capability import Candidate
from radhanite.eligibility import assess
from radhanite.money import Money
from radhanite.policy import RunPolicy
from radhanite.probability import Probability
from radhanite.runstate import RunState, RunStatus, TransitionRecord, begin_run
from radhanite.selection import Selection, SelectionOutcome, select_capability
from radhanite.capability_execution import (
    CapabilityExecutor,
    ExecutionResult,
    apply_execution,
)


class _IntWithBaggage(int):
    def __init__(self, value: int) -> None:
        self.baggage = []


class _MoneyWithBaggage(Money):
    pass


class _EvidenceIntWithBaggage(int):
    def __init__(self, value: int) -> None:
        self.baggage = []


class _ExecutionResultSubclass(ExecutionResult):
    pass


class _Executor:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def execute(self, selected_candidate, current_state):
        self.calls.append((selected_candidate, current_state))
        return self.result


def a_run(**overrides) -> RunState:
    arguments = {
        "task_value": Money("50.00"),
        "initial_budget": Money("2.00"),
        "remaining_budget": Money("2.00"),
        "policy": RunPolicy(max_capability_steps=4),
        "task_state": {"marker": "before"},
        "current_success_probability": Probability("0.20"),
    }
    status = overrides.pop("status", None)
    arguments.update(overrides)
    run = begin_run(**arguments)
    if status is None:
        return run
    return RunState(
        task_value=run.task_value,
        initial_budget=run.initial_budget,
        policy=run.policy,
        task_state=run.task_state,
        current_success_probability=run.current_success_probability,
        remaining_budget=run.remaining_budget,
        total_spend=run.total_spend,
        consumed_candidate_ids=run.consumed_candidate_ids,
        capability_step_count=run.capability_step_count,
        status=status,
        history=run.history,
    )


def a_candidate(*, candidate_id="capability-001", cost="0.75") -> Candidate:
    return Candidate(
        candidate_id=candidate_id,
        cost=Money(cost),
        success_probability=Probability("0.80"),
    )


def a_selection(run: RunState, candidate: Candidate | None = None) -> Selection:
    candidate = candidate or a_candidate()
    assessment = assess(
        candidate=candidate,
        current_success_probability=run.current_success_probability,
        task_value=run.task_value,
        remaining_budget=run.remaining_budget,
        consumed_candidate_ids=run.consumed_candidate_ids,
        capability_step_count=run.capability_step_count,
        max_capability_steps=run.max_capability_steps,
    )
    return select_capability(
        assessments=(assessment,),
        current_success_probability=run.current_success_probability,
        task_value=run.task_value,
        remaining_budget=run.remaining_budget,
        consumed_candidate_ids=run.consumed_candidate_ids,
        capability_step_count=run.capability_step_count,
        max_capability_steps=run.max_capability_steps,
    )


class ExecutionResultTests(unittest.TestCase):
    def test_successful_positive_cost_result(self) -> None:
        result = ExecutionResult(
            succeeded=True,
            committed_cost=Money("0.40"),
            evidence={"answer": "yes"},
        )
        self.assertIs(result.succeeded, True)
        self.assertEqual(result.committed_cost, Money("0.40"))
        self.assertEqual(result.evidence, {"answer": "yes"})

    def test_successful_zero_cost_result(self) -> None:
        result = ExecutionResult(
            succeeded=True, committed_cost=Money("0.00"), evidence=None
        )
        self.assertIs(result.succeeded, True)
        self.assertEqual(result.committed_cost, Money("0.00"))

    def test_failed_positive_cost_result(self) -> None:
        result = ExecutionResult(
            succeeded=False,
            committed_cost=Money("0.20"),
            evidence={"partial": True},
        )
        self.assertIs(result.succeeded, False)
        self.assertEqual(result.committed_cost, Money("0.20"))

    def test_failed_zero_cost_result(self) -> None:
        result = ExecutionResult(
            succeeded=False, committed_cost=Money("0.00"), evidence="no result"
        )
        self.assertIs(result.succeeded, False)
        self.assertEqual(result.committed_cost, Money("0.00"))

    def test_negative_committed_cost_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ExecutionResult(
                succeeded=False, committed_cost=Money("-0.01"), evidence=None
            )

    def test_exact_money_object_is_preserved(self) -> None:
        cost = Money("0.40")
        result = ExecutionResult(succeeded=True, committed_cost=cost, evidence=None)
        self.assertIs(result.committed_cost, cost)
        self.assertIsInstance(result.committed_cost, Money)
        self.assertNotIsInstance(result.committed_cost, float)

    def test_mutable_evidence_is_detached_and_frozen(self) -> None:
        supplied = {"items": ["before"], "nested": {"answer": 42}}
        result = ExecutionResult(
            succeeded=True, committed_cost=Money("0.00"), evidence=supplied
        )
        supplied["items"].append("after")
        supplied["nested"]["answer"] = 99
        self.assertIsInstance(result.evidence, MappingProxyType)
        self.assertEqual(result.evidence["items"], ("before",))
        self.assertEqual(result.evidence["nested"]["answer"], 42)
        with self.assertRaises(TypeError):
            result.evidence["new"] = "value"
        with self.assertRaises(AttributeError):
            result.evidence["items"].append("after")

    def test_cyclic_evidence_is_rejected(self) -> None:
        evidence = {"self": []}
        evidence["self"].append(evidence)
        with self.assertRaises(ValueError):
            ExecutionResult(succeeded=False, committed_cost=Money("0.00"), evidence=evidence)

    def test_scalar_subclass_escape_hatch_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            ExecutionResult(
                succeeded=_IntWithBaggage(1),
                committed_cost=Money("0.00"),
                evidence=None,
            )
        with self.assertRaises(TypeError):
            ExecutionResult(
                succeeded=True,
                committed_cost=_MoneyWithBaggage("0.10"),
                evidence=None,
            )
        with self.assertRaises(TypeError):
            ExecutionResult(
                succeeded=True,
                committed_cost=Money("0.10"),
                evidence=_EvidenceIntWithBaggage(1),
            )

    def test_result_is_immutable_and_has_no_arbitrary_provider_fields(self) -> None:
        result = ExecutionResult(True, Money("0.10"), evidence=None)
        with self.assertRaises(Exception):
            result.succeeded = False
        self.assertFalse(hasattr(result, "__dict__"))
        for field in result.__dataclass_fields__:
            self.assertNotIn(
                field,
                {"provider", "network", "wallet", "payment", "source", "endpoint"},
            )


class ExecutorBoundaryTests(unittest.TestCase):
    def test_protocol_has_only_candidate_and_state_inputs(self) -> None:
        signature = inspect.signature(CapabilityExecutor.execute)
        self.assertEqual(
            tuple(signature.parameters),
            ("self", "selected_candidate", "current_state"),
        )

    def test_executor_receives_selected_candidate_and_current_state(self) -> None:
        run = a_run()
        candidate = a_candidate()
        selection = a_selection(run, candidate)
        executor = _Executor(
            ExecutionResult(True, Money("0.40"), evidence={"ok": True})
        )

        apply_execution(state=run, selection=selection, executor=executor)

        self.assertEqual(len(executor.calls), 1)
        self.assertIs(executor.calls[0][0], candidate)
        self.assertIs(executor.calls[0][1], run)

    def test_executor_is_called_exactly_once(self) -> None:
        run = a_run()
        selection = a_selection(run)
        executor = _Executor(ExecutionResult(False, Money("0.10"), evidence=None))

        apply_execution(state=run, selection=selection, executor=executor)

        self.assertEqual(len(executor.calls), 1)

    def test_transition_does_not_select_or_rank(self) -> None:
        run = a_run()
        selection = a_selection(run)
        executor = _Executor(ExecutionResult(True, Money("0.10"), evidence=None))

        with patch.object(
            selection_module,
            "select_capability",
            side_effect=AssertionError("selection must happen before execution"),
        ):
            apply_execution(state=run, selection=selection, executor=executor)


class ExecutionTransitionTests(unittest.TestCase):
    def test_success_consumes_candidate_and_increments_once(self) -> None:
        run = a_run()
        selection = a_selection(run)
        executor = _Executor(ExecutionResult(True, Money("0.40"), evidence="done"))

        after = apply_execution(state=run, selection=selection, executor=executor)

        self.assertIsNot(after, run)
        self.assertEqual(after.consumed_candidate_ids, ("capability-001",))
        self.assertEqual(after.capability_step_count, 1)
        self.assertIs(after.status, RunStatus.RUNNING)
        self.assertEqual(after.total_spend, Money("0.40"))
        self.assertEqual(after.remaining_budget, Money("1.60"))
        self.assertEqual(after.total_spend + after.remaining_budget, after.initial_budget)

    def test_zero_cost_success_still_consumes_and_increments(self) -> None:
        run = a_run()
        selection = a_selection(run)
        executor = _Executor(ExecutionResult(True, Money("0.00"), evidence=None))

        after = apply_execution(state=run, selection=selection, executor=executor)

        self.assertEqual(after.consumed_candidate_ids, ("capability-001",))
        self.assertEqual(after.capability_step_count, 1)
        self.assertEqual(after.total_spend, Money("0.00"))
        self.assertEqual(after.remaining_budget, Money("2.00"))

    def test_failed_positive_cost_consumes_increments_and_charges(self) -> None:
        run = a_run()
        selection = a_selection(run)
        executor = _Executor(ExecutionResult(False, Money("0.25"), evidence="partial"))

        after = apply_execution(state=run, selection=selection, executor=executor)

        self.assertIs(after.status, RunStatus.EXECUTION_FAILURE)
        self.assertEqual(after.consumed_candidate_ids, ("capability-001",))
        self.assertEqual(after.capability_step_count, 1)
        self.assertEqual(after.total_spend, Money("0.25"))
        self.assertEqual(after.remaining_budget, Money("1.75"))

    def test_failed_zero_cost_consumes_and_increments(self) -> None:
        run = a_run()
        selection = a_selection(run)
        executor = _Executor(ExecutionResult(False, Money("0.00"), evidence=None))

        after = apply_execution(state=run, selection=selection, executor=executor)

        self.assertIs(after.status, RunStatus.EXECUTION_FAILURE)
        self.assertEqual(after.consumed_candidate_ids, ("capability-001",))
        self.assertEqual(after.capability_step_count, 1)

    def test_success_preserves_opaque_state_and_probability(self) -> None:
        run = a_run(task_state={"evidence": ["before"]})
        selection = a_selection(run)
        executor = _Executor(ExecutionResult(True, Money("0.10"), evidence="opaque"))

        after = apply_execution(state=run, selection=selection, executor=executor)

        self.assertEqual(after.task_state, run.task_state)
        self.assertEqual(
            after.current_success_probability, run.current_success_probability
        )
        self.assertIs(after.status, RunStatus.RUNNING)

    def test_before_and_after_snapshots_are_exact_and_non_recursive(self) -> None:
        run = a_run(remaining_budget=Money("1.50"))
        selection = a_selection(run)
        result = ExecutionResult(True, Money("0.40"), evidence={"ok": True})
        after = apply_execution(state=run, selection=selection, executor=_Executor(result))

        self.assertEqual(len(after.history), 1)
        record = after.history[0]
        self.assertIsInstance(record, TransitionRecord)
        self.assertEqual(record.before, run.snapshot())
        self.assertEqual(record.after, after.snapshot())
        self.assertIs(record.selection, selection)
        self.assertEqual(record.execution, result)
        self.assertNotIn("history", record.before.__dataclass_fields__)
        self.assertNotIn("history", record.after.__dataclass_fields__)

    def test_execution_result_is_retained_as_exact_audit_record_member(self) -> None:
        run = a_run()
        selection = a_selection(run)
        result = ExecutionResult(True, Money("0.10"), evidence={"items": [1]})
        after = apply_execution(state=run, selection=selection, executor=_Executor(result))
        self.assertIs(type(after.history[0].execution), ExecutionResult)
        self.assertEqual(after.history[0].execution.evidence["items"], (1,))

    def test_committed_cost_equal_to_remaining_budget_is_allowed(self) -> None:
        run = a_run(remaining_budget=Money("0.75"))
        selection = a_selection(run, a_candidate(cost="0.75"))
        executor = _Executor(ExecutionResult(True, Money("0.75"), evidence=None))

        after = apply_execution(state=run, selection=selection, executor=executor)

        self.assertEqual(after.remaining_budget, Money("0.00"))
        self.assertEqual(after.total_spend, Money("2.00"))

    def test_cost_above_candidate_cost_is_rejected_without_retry(self) -> None:
        run = a_run()
        selection = a_selection(run, a_candidate(cost="0.40"))
        executor = _Executor(ExecutionResult(True, Money("0.41"), evidence=None))

        with self.assertRaises(ValueError):
            apply_execution(state=run, selection=selection, executor=executor)
        self.assertEqual(len(executor.calls), 1)

    def test_cost_above_remaining_budget_is_rejected_without_retry(self) -> None:
        run = a_run(remaining_budget=Money("0.50"))
        # The candidate was selected while the run had enough budget; the
        # transition must still enforce the current state's remaining budget.
        selection = a_selection(a_run(), a_candidate(cost="0.75"))
        executor = _Executor(ExecutionResult(True, Money("0.51"), evidence=None))

        with self.assertRaisesRegex(ValueError, "remaining budget"):
            apply_execution(state=run, selection=selection, executor=executor)
        self.assertEqual(len(executor.calls), 1)

    def test_same_candidate_id_cannot_execute_twice(self) -> None:
        run = a_run()
        selection = a_selection(run)
        first_executor = _Executor(ExecutionResult(True, Money("0.10"), evidence=None))
        after = apply_execution(state=run, selection=selection, executor=first_executor)
        second_executor = _Executor(ExecutionResult(True, Money("0.10"), evidence=None))

        with self.assertRaises(ValueError):
            apply_execution(state=after, selection=selection, executor=second_executor)
        self.assertEqual(second_executor.calls, [])

    def test_terminal_state_cannot_execute(self) -> None:
        run = a_run(status=RunStatus.EXECUTION_FAILURE)
        selection = a_selection(run)
        executor = _Executor(ExecutionResult(True, Money("0.10"), evidence=None))

        with self.assertRaises(ValueError):
            apply_execution(state=run, selection=selection, executor=executor)
        self.assertEqual(executor.calls, [])

    def test_step_ceiling_cannot_execute(self) -> None:
        run = a_run(
            policy=RunPolicy(max_capability_steps=1), capability_step_count=1
        )
        selection = a_selection(run)
        executor = _Executor(ExecutionResult(True, Money("0.10"), evidence=None))

        with self.assertRaises(ValueError):
            apply_execution(state=run, selection=selection, executor=executor)
        self.assertEqual(executor.calls, [])

    def test_stop_selection_cannot_execute(self) -> None:
        run = a_run()
        stop = Selection(
            outcome=SelectionOutcome.STOP,
            reason="stop",
            selected=None,
            assessments=(),
            current_success_probability=run.current_success_probability,
            task_value=run.task_value,
            remaining_budget=run.remaining_budget,
            consumed_candidate_ids=(),
            capability_step_count=0,
            max_capability_steps=4,
        )
        executor = _Executor(ExecutionResult(True, Money("0.10"), evidence=None))

        with self.assertRaises(ValueError):
            apply_execution(state=run, selection=stop, executor=executor)
        self.assertEqual(executor.calls, [])

    def test_invalid_executor_result_is_rejected(self) -> None:
        run = a_run()
        selection = a_selection(run)
        for invalid in (None, {}, run, run.snapshot()):
            executor = _Executor(invalid)
            with self.assertRaises((TypeError, ValueError)):
                apply_execution(state=run, selection=selection, executor=executor)

    def test_execution_result_subclass_is_rejected_by_transition_record(self) -> None:
        run = a_run()
        snap = run.snapshot()
        selection = a_selection(run)
        result = _ExecutionResultSubclass(True, Money("0.10"), evidence=None)
        with self.assertRaises(TypeError):
            TransitionRecord(
                before=snap, selection=selection, after=snap, execution=result
            )

    def test_arbitrary_execution_payloads_remain_rejected(self) -> None:
        run = a_run()
        snap = run.snapshot()
        selection = a_selection(run)
        for payload in ([], {}, run, snap, Decimal("1.0")):
            with self.assertRaises((TypeError, ValueError)):
                TransitionRecord(
                    before=snap, selection=selection, after=snap, execution=payload
                )

    def test_old_state_is_not_mutated(self) -> None:
        run = a_run()
        before = (
            run.task_state,
            run.remaining_budget,
            run.total_spend,
            run.consumed_candidate_ids,
            run.capability_step_count,
            run.status,
            run.history,
        )
        after = apply_execution(
            state=run,
            selection=a_selection(run),
            executor=_Executor(ExecutionResult(True, Money("0.10"), evidence=None)),
        )

        self.assertEqual(
            (
                run.task_state,
                run.remaining_budget,
                run.total_spend,
                run.consumed_candidate_ids,
                run.capability_step_count,
                run.status,
                run.history,
            ),
            before,
        )
        self.assertEqual(after.capability_step_count, 1)


if __name__ == "__main__":
    unittest.main()
