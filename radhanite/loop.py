"""The provider-neutral TASK-007 capability run loop.

**Implementation agent: Manus.**

This module orchestrates existing TASK-006 selection and TASK-007 PR-B
execution. It does not interpret opaque task state, derive economics, discover
providers, retry failures, or implement a domain-specific updater.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from radhanite._immutable import refuse_rehydration
from radhanite.capability import Candidate, validate_candidates
from radhanite.capability_execution import CapabilityExecutor, ExecutionResult, apply_execution
from radhanite.eligibility import assess
from radhanite.money import Money
from radhanite.probability import Probability
from radhanite.runstate import RunState, RunStatus, TransitionRecord, _frozen
from radhanite.selection import Selection, SelectionOutcome, select_capability

__all__ = [
    "CandidateSource",
    "TaskStateUpdate",
    "TaskStateUpdater",
    "run_capability_loop",
]


@refuse_rehydration
@dataclass(frozen=True, slots=True)
class TaskStateUpdate:
    """Opaque task-state output supplied by the injected updater boundary."""

    task_state: Any
    current_success_probability: Probability
    task_complete: bool

    def __post_init__(self) -> None:
        object.__setattr__(self, "task_state", _frozen(self.task_state))
        if type(self.current_success_probability) is not Probability:
            raise TypeError(
                "current_success_probability must be exactly Probability, got "
                f"{type(self.current_success_probability).__name__}."
            )
        if type(self.task_complete) is not bool:
            raise TypeError(
                f"task_complete must be exactly bool, got "
                f"{type(self.task_complete).__name__}."
            )


class CandidateSource(Protocol):
    """Provider-neutral source of the candidates offered this iteration."""

    def get_candidates(self, task_state: Any, run_state: RunState) -> Any:
        """Return the ordered candidates currently available."""
        ...


class TaskStateUpdater(Protocol):
    """Provider-neutral interpreter of one successful execution result."""

    def update(
        self, previous_task_state: Any, execution_result: ExecutionResult
    ) -> TaskStateUpdate:
        """Return the next opaque state, probability, and completion verdict."""
        ...


def run_capability_loop(
    *,
    state: RunState,
    candidate_source: CandidateSource,
    executor: CapabilityExecutor,
    updater: TaskStateUpdater,
) -> RunState:
    """Run TASK-006 selection and at most one execution per iteration.

    The task-complete check is first. A terminal input state is returned without
    asking the candidate source, executing, or updating. Every non-terminal
    iteration retains exactly one complete ``Selection`` and one before/after
    snapshot; STOP iterations retain ``execution=None``.
    """
    _require_state(state)

    current = state
    while True:
        # The terminal/completion check remains first on every pass. The updater
        # changes status only after a successful execution, so no opaque
        # task-state field is inspected here.
        if current.status.is_terminal:
            return current

        # An incomplete zero-step run is an immediate safety stop. This follows
        # the already-complete check and does not call the candidate source.
        if current.max_capability_steps == 0:
            selection = select_capability(
                assessments=(),
                current_success_probability=current.current_success_probability,
                task_value=current.task_value,
                remaining_budget=current.remaining_budget,
                consumed_candidate_ids=current.consumed_candidate_ids,
                capability_step_count=current.capability_step_count,
                max_capability_steps=current.max_capability_steps,
            )
            return _append_transition(
                current,
                selection=selection,
                execution=None,
                status=RunStatus.SAFETY_STOP,
                task_state=current.task_state,
                current_success_probability=current.current_success_probability,
            )

        offered = validate_candidates(
            candidate_source.get_candidates(current.task_state, current)
        )
        assessments = tuple(
            assess(
                candidate=candidate,
                current_success_probability=current.current_success_probability,
                task_value=current.task_value,
                remaining_budget=current.remaining_budget,
                consumed_candidate_ids=current.consumed_candidate_ids,
                capability_step_count=current.capability_step_count,
                max_capability_steps=current.max_capability_steps,
            )
            for candidate in offered
        )
        selection = select_capability(
            assessments=assessments,
            current_success_probability=current.current_success_probability,
            task_value=current.task_value,
            remaining_budget=current.remaining_budget,
            consumed_candidate_ids=current.consumed_candidate_ids,
            capability_step_count=current.capability_step_count,
            max_capability_steps=current.max_capability_steps,
        )

        if selection.outcome is SelectionOutcome.STOP:
            status = _classify_stop(current, selection)
            return _append_transition(
                current,
                selection=selection,
                execution=None,
                status=status,
                task_state=current.task_state,
                current_success_probability=current.current_success_probability,
            )

        attempted = apply_execution(
            state=current,
            selection=selection,
            executor=executor,
        )
        execution = attempted.history[-1].execution
        assert type(execution) is ExecutionResult

        if attempted.status is RunStatus.EXECUTION_FAILURE:
            return attempted

        update = updater.update(current.task_state, execution)
        if type(update) is not TaskStateUpdate:
            raise TypeError(
                "updater must return exactly TaskStateUpdate, got "
                f"{type(update).__name__}."
            )

        updated_status = (
            RunStatus.TASK_COMPLETE if update.task_complete else RunStatus.RUNNING
        )
        current = _replace_execution_after(
            attempted,
            update=update,
            status=updated_status,
        )

        if current.status is RunStatus.TASK_COMPLETE:
            return current

    return current


def _require_state(state: RunState) -> None:
    if type(state) is not RunState:
        raise TypeError(
            f"state must be exactly RunState, got {type(state).__name__}."
        )


def _classify_stop(state: RunState, selection: Selection) -> RunStatus:
    """Read TASK-006's refusal classification without recomputing economics."""
    if state.capability_step_count >= state.max_capability_steps:
        return RunStatus.SAFETY_STOP
    if selection.stopped_without_economic_judgement:
        return RunStatus.SAFETY_STOP
    return RunStatus.ECONOMIC_STOP


def _append_transition(
    state: RunState,
    *,
    selection: Selection,
    execution: ExecutionResult | None,
    status: RunStatus,
    task_state: Any,
    current_success_probability: Probability,
) -> RunState:
    """Append one non-recursive transition to a state without mutating it."""
    before = state.snapshot()
    after_without_history = RunState(
        task_value=state.task_value,
        initial_budget=state.initial_budget,
        policy=state.policy,
        task_state=task_state,
        current_success_probability=current_success_probability,
        remaining_budget=state.remaining_budget,
        total_spend=state.total_spend,
        consumed_candidate_ids=state.consumed_candidate_ids,
        capability_step_count=state.capability_step_count,
        status=status,
        history=state.history,
    )
    record = TransitionRecord(
        before=before,
        selection=selection,
        after=after_without_history.snapshot(),
        execution=execution,
    )
    return RunState(
        task_value=after_without_history.task_value,
        initial_budget=after_without_history.initial_budget,
        policy=after_without_history.policy,
        task_state=after_without_history.task_state,
        current_success_probability=after_without_history.current_success_probability,
        remaining_budget=after_without_history.remaining_budget,
        total_spend=after_without_history.total_spend,
        consumed_candidate_ids=after_without_history.consumed_candidate_ids,
        capability_step_count=after_without_history.capability_step_count,
        status=after_without_history.status,
        history=state.history + (record,),
    )


def _replace_execution_after(
    attempted: RunState,
    *,
    update: TaskStateUpdate,
    status: RunStatus,
) -> RunState:
    """Replace PR-B's pre-updater after-snapshot with the final loop snapshot."""
    if not attempted.history:
        raise RuntimeError("execution transition did not append a history record")
    prior_history = attempted.history[:-1]
    prior_record = attempted.history[-1]
    final_without_history = RunState(
        task_value=attempted.task_value,
        initial_budget=attempted.initial_budget,
        policy=attempted.policy,
        task_state=update.task_state,
        current_success_probability=update.current_success_probability,
        remaining_budget=attempted.remaining_budget,
        total_spend=attempted.total_spend,
        consumed_candidate_ids=attempted.consumed_candidate_ids,
        capability_step_count=attempted.capability_step_count,
        status=status,
        history=prior_history,
    )
    replaced_record = TransitionRecord(
        before=prior_record.before,
        selection=prior_record.selection,
        after=final_without_history.snapshot(),
        execution=prior_record.execution,
    )
    return RunState(
        task_value=final_without_history.task_value,
        initial_budget=final_without_history.initial_budget,
        policy=final_without_history.policy,
        task_state=final_without_history.task_state,
        current_success_probability=final_without_history.current_success_probability,
        remaining_budget=final_without_history.remaining_budget,
        total_spend=final_without_history.total_spend,
        consumed_candidate_ids=final_without_history.consumed_candidate_ids,
        capability_step_count=final_without_history.capability_step_count,
        status=final_without_history.status,
        history=prior_history + (replaced_record,),
    )
