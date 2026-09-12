"""One provider-neutral capability execution and its immutable state transition.

TASK-007 PR B implements exactly one already-selected capability attempt. It does
not select, acquire, interpret evidence, update task state, classify economic or
safety stops, retry, or run an iteration loop.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from radhanite._immutable import refuse_rehydration
from radhanite.capability import Candidate
from radhanite.eligibility import Assessment
from radhanite.money import Money
from radhanite.runstate import RunState, RunStatus, TransitionRecord, _frozen
from radhanite.selection import Selection, SelectionOutcome

__all__ = ["CapabilityExecutor", "ExecutionResult", "apply_execution"]


@refuse_rehydration
@dataclass(frozen=True, slots=True)
class ExecutionResult:
    """The provider-neutral result of one selected capability attempt.

    ``evidence`` is structurally frozen without being interpreted. The result
    reports what execution actually committed, including a non-zero amount on a
    failed attempt. It carries no provider, payment, network, or wallet identity.
    """

    succeeded: bool
    committed_cost: Money
    evidence: Any

    def __post_init__(self) -> None:
        if type(self.succeeded) is not bool:
            raise TypeError(
                "succeeded must be exactly bool, got "
                f"{type(self.succeeded).__name__}."
            )
        if type(self.committed_cost) is not Money:
            raise TypeError(
                "committed_cost must be exactly Money, got "
                f"{type(self.committed_cost).__name__}."
            )
        if self.committed_cost.is_negative:
            raise ValueError(
                f"committed_cost cannot be negative, got {self.committed_cost}."
            )
        object.__setattr__(self, "evidence", _frozen(self.evidence))


class CapabilityExecutor(Protocol):
    """The smallest provider-neutral executor boundary required by TASK-007."""

    def execute(
        self,
        selected_candidate: Candidate,
        current_state: RunState,
    ) -> ExecutionResult:
        """Attempt one already-selected candidate against the current state."""
        ...


def apply_execution(
    *,
    state: RunState,
    selection: Selection,
    executor: CapabilityExecutor,
) -> RunState:
    """Execute one selected candidate and append one immutable transition.

    The executor is called exactly once. Every valid attempt consumes the
    selected candidate ID and increments the capability-step count exactly once,
    regardless of success or committed cost. A failed result terminates the new
    state as ``EXECUTION_FAILURE``; a successful result leaves task state,
    probability, and status unchanged because the updater is out of scope.
    """

    if type(state) is not RunState:
        raise TypeError(
            f"state must be exactly RunState, got {type(state).__name__}."
        )
    if type(selection) is not Selection:
        raise TypeError(
            f"selection must be exactly Selection, got {type(selection).__name__}."
        )
    if state.status is not RunStatus.RUNNING:
        raise ValueError(
            "execution is not permitted after a terminal run status: "
            f"{state.status.value}."
        )
    if state.capability_step_count >= state.max_capability_steps:
        raise ValueError(
            "execution is not permitted after the capability-step ceiling has "
            f"been reached: {state.capability_step_count} >= "
            f"{state.max_capability_steps}."
        )
    if selection.outcome is not SelectionOutcome.SELECTED:
        raise ValueError("one execution transition requires a SELECTED selection.")

    selected = selection.selected
    if not isinstance(selected, Assessment):
        raise TypeError(
            "a SELECTED selection must carry an Assessment, got "
            f"{type(selected).__name__}."
        )
    candidate = selected.candidate
    if not isinstance(candidate, Candidate):
        raise TypeError(
            "the selected assessment must carry a Candidate, got "
            f"{type(candidate).__name__}."
        )
    candidate_id = candidate.candidate_id
    if candidate_id in state.consumed_candidate_ids:
        raise ValueError(
            f"candidate {candidate_id!r} has already been consumed and cannot "
            "execute again."
        )

    result = executor.execute(candidate, state)
    if type(result) is not ExecutionResult:
        raise TypeError(
            "executor must return exactly ExecutionResult, got "
            f"{type(result).__name__}."
        )

    committed_cost = result.committed_cost
    if committed_cost > candidate.cost:
        raise ValueError(
            f"committed_cost {committed_cost} exceeds candidate cost "
            f"{candidate.cost}. No silent clamping is permitted."
        )
    if committed_cost > state.remaining_budget:
        raise ValueError(
            f"committed_cost {committed_cost} exceeds remaining budget "
            f"{state.remaining_budget}. No silent clamping is permitted."
        )

    before = state.snapshot()
    consumed = tuple(sorted((*state.consumed_candidate_ids, candidate_id)))
    after_status = (
        RunStatus.RUNNING if result.succeeded else RunStatus.EXECUTION_FAILURE
    )
    after = RunState(
        task_value=state.task_value,
        initial_budget=state.initial_budget,
        policy=state.policy,
        task_state=state.task_state,
        current_success_probability=state.current_success_probability,
        remaining_budget=state.remaining_budget - committed_cost,
        total_spend=state.total_spend + committed_cost,
        consumed_candidate_ids=consumed,
        capability_step_count=state.capability_step_count + 1,
        status=after_status,
        history=state.history,
    )
    record = TransitionRecord(
        before=before,
        selection=selection,
        after=after.snapshot(),
        execution=result,
    )
    return RunState(
        task_value=after.task_value,
        initial_budget=after.initial_budget,
        policy=after.policy,
        task_state=after.task_state,
        current_success_probability=after.current_success_probability,
        remaining_budget=after.remaining_budget,
        total_spend=after.total_spend,
        consumed_candidate_ids=after.consumed_candidate_ids,
        capability_step_count=after.capability_step_count,
        status=after.status,
        history=after.history + (record,),
    )
