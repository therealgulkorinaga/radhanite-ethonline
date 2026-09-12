"""One provider-neutral capability execution and its immutable state transition.

TASK-007 PR B implements exactly one already-selected capability attempt. It does
not select, acquire, interpret evidence, update task state, classify economic or
safety stops, retry, or run an iteration loop.

A compliant executor receives the selected candidate, the current run state, and
the exact maximum authorized commitment. It must know that ceiling before any
external side effect, never exceed it, and normalize every post-attempt provider
failure into an exact ``ExecutionResult``. A raw exception is therefore defined
as a failure before an execution attempt or financial commitment began; the
generic transition cannot infer actual spend from an arbitrary exception.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from radhanite._immutable import refuse_rehydration
from radhanite.capability import Candidate
from radhanite.eligibility import Assessment, Ineligibility
from radhanite.money import Money
from radhanite.probability import Probability
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
    """The provider-neutral executor contract required by TASK-007.

    ``maximum_authorized_cost`` is computed by the generic layer as
    ``min(candidate.cost, current_state.remaining_budget)`` and is supplied
    before the executor may perform a side effect. A compliant implementation
    must never commit more than that amount. It must convert every provider or
    internal failure after an attempt into an exact failed ``ExecutionResult``
    containing the actual committed amount, including a non-zero amount.

    A raw exception is permitted only when the executor failed before an
    execution attempt or financial commitment began. The generic layer cannot
    infer actual spend from an arbitrary exception and therefore never fabricates
    accounting or silently treats one as a paid attempt.
    """

    def execute(
        self,
        selected_candidate: Candidate,
        current_state: RunState,
        maximum_authorized_cost: Money,
    ) -> ExecutionResult:
        """Attempt one selected candidate under the explicit cost ceiling."""
        ...


def apply_execution(
    *,
    state: RunState,
    selection: Selection,
    executor: CapabilityExecutor,
) -> RunState:
    """Execute one selected candidate and append one immutable transition.

    The executor is called exactly once, and only after the complete retained
    selection graph has been checked and its decision context has been matched
    to ``state``. Every valid attempt consumes the selected candidate ID and
    increments the capability-step count exactly once, regardless of success or
    committed cost. A failed result terminates the new state as
    ``EXECUTION_FAILURE``; a successful result leaves task state, probability,
    and status unchanged because the updater is out of scope.

    A raw executor exception is deliberately propagated as a pre-attempt
    executor failure. A compliant executor must normalize any post-attempt
    failure into ``ExecutionResult(succeeded=False, committed_cost=..., ...)``;
    arbitrary generic code cannot be made auditable after it commits money and
    then loses the committed amount.
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

    _validate_selection_graph(selection, state)
    if selection.outcome is not SelectionOutcome.SELECTED:
        raise ValueError("one execution transition requires a SELECTED selection.")

    selected = selection.selected
    # _validate_selection_graph establishes this exact structural boundary.
    assert type(selected) is Assessment
    candidate = selected.candidate
    assert type(candidate) is Candidate
    candidate_id = candidate.candidate_id
    if candidate_id in state.consumed_candidate_ids:
        raise ValueError(
            f"candidate {candidate_id!r} has already been consumed and cannot "
            "execute again."
        )

    maximum_authorized_cost = min(candidate.cost, state.remaining_budget)
    # A raw exception here means the executor contract says no attempt or
    # commitment began. Post-attempt failures must be returned as ExecutionResult.
    result = executor.execute(candidate, state, maximum_authorized_cost)
    if type(result) is not ExecutionResult:
        raise TypeError(
            "executor contract violation: executor must return exactly "
            f"ExecutionResult, got {type(result).__name__}. A malformed result "
            "cannot be converted into invented accounting."
        )

    committed_cost = result.committed_cost
    if type(committed_cost) is not Money:
        raise TypeError(
            "executor contract violation: committed_cost must be exactly Money."
        )
    if committed_cost > maximum_authorized_cost:
        raise ValueError(
            f"executor contract violation: committed_cost {committed_cost} "
            f"exceeds maximum authorized cost {maximum_authorized_cost}. No "
            "silent clamping is permitted."
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


def _validate_selection_graph(selection: Selection, state: RunState) -> None:
    """Validate every object retained by the complete TASK-006 decision record."""

    _exact(selection.outcome, SelectionOutcome, "selection.outcome")
    _exact(selection.reason, str, "selection.reason")
    _exact(selection.assessments, tuple, "selection.assessments")
    _exact(selection.current_success_probability, Probability,
           "selection.current_success_probability")
    _exact(selection.task_value, Money, "selection.task_value")
    _exact(selection.remaining_budget, Money, "selection.remaining_budget")
    _exact(selection.consumed_candidate_ids, tuple,
           "selection.consumed_candidate_ids")
    _exact(selection.capability_step_count, int,
           "selection.capability_step_count")
    _exact(selection.max_capability_steps, int,
           "selection.max_capability_steps")
    for position, candidate_id in enumerate(selection.consumed_candidate_ids):
        _exact(candidate_id, str, f"selection.consumed_candidate_ids[{position}]")

    _context_match(
        "selection",
        selection.current_success_probability,
        selection.task_value,
        selection.remaining_budget,
        selection.consumed_candidate_ids,
        selection.capability_step_count,
        selection.max_capability_steps,
        state,
    )

    seen_candidate_ids: set[str] = set()
    for position, assessment in enumerate(selection.assessments):
        _validate_assessment_graph(assessment, position)
        candidate_id = assessment.candidate.candidate_id
        if candidate_id in seen_candidate_ids:
            raise ValueError(
                f"selection.assessments[{position}] repeats candidate ID "
                f"{candidate_id!r}; TASK-006 selections must contain unique "
                "candidate IDs."
            )
        seen_candidate_ids.add(candidate_id)
        if (
            assessment.current_success_probability
            != selection.current_success_probability
            or assessment.task_value != selection.task_value
            or assessment.remaining_budget != selection.remaining_budget
            or assessment.consumed_candidate_ids
            != selection.consumed_candidate_ids
            or assessment.capability_step_count
            != selection.capability_step_count
            or assessment.max_capability_steps
            != selection.max_capability_steps
        ):
            raise ValueError(
                f"selection.assessments[{position}] was computed against a "
                "different decision context than the Selection."
            )

    selected = selection.selected
    if selection.outcome is SelectionOutcome.SELECTED:
        if type(selected) is not Assessment:
            raise TypeError(
                "a SELECTED selection must carry exactly an Assessment, got "
                f"{type(selected).__name__}."
            )
        if not any(selected is assessment for assessment in selection.assessments):
            raise ValueError(
                "the selected assessment must be one of the retained assessments."
            )
        if not selected.eligible:
            raise ValueError(
                "a SELECTED selection must retain an eligible selected assessment."
            )
    elif selection.outcome is SelectionOutcome.STOP:
        if selected is not None:
            raise ValueError("a STOP selection cannot retain a selected assessment.")
        if any(assessment.eligible for assessment in selection.assessments):
            raise ValueError(
                "a STOP selection cannot retain an eligible assessment."
            )
    else:
        raise ValueError(
            f"selection.outcome is not an authorized SelectionOutcome: {selected!r}."
        )


def _validate_assessment_graph(assessment: Assessment, position: int) -> None:
    label = f"selection.assessments[{position}]"
    _exact(assessment, Assessment, label)
    _validate_candidate_graph(assessment.candidate, f"{label}.candidate")
    _exact(assessment.reason, str, f"{label}.reason")
    _exact(assessment.incremental_expected_value, Money,
           f"{label}.incremental_expected_value")
    _exact(assessment.net_expected_value, Money,
           f"{label}.net_expected_value")
    _exact(assessment.current_success_probability, Probability,
           f"{label}.current_success_probability")
    _exact(assessment.task_value, Money, f"{label}.task_value")
    _exact(assessment.remaining_budget, Money, f"{label}.remaining_budget")
    _exact(assessment.consumed_candidate_ids, tuple,
           f"{label}.consumed_candidate_ids")
    for index, candidate_id in enumerate(assessment.consumed_candidate_ids):
        _exact(candidate_id, str, f"{label}.consumed_candidate_ids[{index}]")
    _exact(assessment.capability_step_count, int,
           f"{label}.capability_step_count")
    _exact(assessment.max_capability_steps, int,
           f"{label}.max_capability_steps")
    _exact(assessment.failed_conditions, tuple, f"{label}.failed_conditions")
    for index, condition in enumerate(assessment.failed_conditions):
        _exact(condition, Ineligibility, f"{label}.failed_conditions[{index}]")


def _validate_candidate_graph(candidate: Candidate, label: str) -> None:
    _exact(candidate, Candidate, label)
    _exact(candidate.candidate_id, str, f"{label}.candidate_id")
    if not candidate.candidate_id or candidate.candidate_id.strip() != candidate.candidate_id:
        raise ValueError(f"{label}.candidate_id violates Candidate identity invariants.")
    _exact(candidate.cost, Money, f"{label}.cost")
    if not candidate.cost.is_positive:
        raise ValueError(f"{label}.cost must be positive.")
    _exact(candidate.success_probability, Probability,
           f"{label}.success_probability")


def _context_match(
    label: str,
    current_success_probability: Probability,
    task_value: Money,
    remaining_budget: Money,
    consumed_candidate_ids: tuple[str, ...],
    capability_step_count: int,
    max_capability_steps: int,
    state: RunState,
) -> None:
    expected = (
        state.current_success_probability,
        state.task_value,
        state.remaining_budget,
        state.consumed_candidate_ids,
        state.capability_step_count,
        state.max_capability_steps,
    )
    actual = (
        current_success_probability,
        task_value,
        remaining_budget,
        consumed_candidate_ids,
        capability_step_count,
        max_capability_steps,
    )
    if actual != expected:
        raise ValueError(
            f"{label} decision context does not match the current RunState; "
            "the Selection is stale or forged and cannot authorize execution."
        )


def _exact(value: Any, expected: type, label: str) -> None:
    if type(value) is not expected:
        raise TypeError(
            f"{label} must be exactly {expected.__name__}, got "
            f"{type(value).__name__}; subclasses and mutable escape hatches are "
            "not retained in execution history."
        )
