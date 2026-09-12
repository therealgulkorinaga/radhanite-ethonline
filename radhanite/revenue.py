"""TASK-009 revenue-opportunity benchmark state and updater.

**Implementation agent: Manus.**

This module is the benchmark-specific domain layer above TASK-007. It interprets
small declared evidence fixtures into a new immutable opportunity state, a new
declared probability, and a completion verdict. It does not select candidates,
read candidate prices, rank providers, or perform external calls.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import replace
from types import MappingProxyType
from typing import Any, TypeAlias

from radhanite.capability_execution import ExecutionResult
from radhanite.loop import TaskStateUpdate
from radhanite.money import Money
from radhanite.policy import RunPolicy
from radhanite.probability import Probability
from radhanite.runstate import RunState, RunStatus, begin_run

__all__ = [
    "BENCHMARK_INITIAL_BUDGET",
    "BENCHMARK_INITIAL_PROBABILITY",
    "BENCHMARK_OPPORTUNITY_VALUE",
    "BENCHMARK_P1_PROBABILITY",
    "BENCHMARK_P2_PROBABILITY",
    "BenchmarkEvidence",
    "RevenueOpportunityState",
    "RevenueOpportunityUpdater",
    "benchmark_opportunity",
    "initialize_benchmark_run",
    "make_evidence",
]


BENCHMARK_OPPORTUNITY_VALUE = Money("50000.00")
BENCHMARK_INITIAL_BUDGET = Money("250.00")
BENCHMARK_INITIAL_PROBABILITY = Probability("0.08")
BENCHMARK_P1_PROBABILITY = Probability("0.14")
BENCHMARK_P2_PROBABILITY = Probability("0.17")
BENCHMARK_POLICY = RunPolicy(max_capability_steps=4)

_MARKET_SIGNAL = "market_signal"
_COMMERCIAL_FIT = "commercial_fit"
_POSITIVE_MARKET_SIGNAL = "positive_market_signal"
_POSITIVE_COMMERCIAL_FIT = "positive_commercial_fit"
_ALLOWED_OUTCOMES = frozenset({_POSITIVE_MARKET_SIGNAL, _POSITIVE_COMMERCIAL_FIT})

BenchmarkEvidence: TypeAlias = Mapping[str, object]
RevenueOpportunityState: TypeAlias = Mapping[str, object]


def make_evidence(
    *,
    capability_key: str,
    evidence_type: str,
    facts: Sequence[str],
    source_reference: str | None,
    outcome_key: str,
) -> BenchmarkEvidence:
    """Build the smallest immutable benchmark evidence record.

    ``source_reference`` is deliberately opaque metadata. It may identify a
    later adapter's source, but it is never passed into TASK-006. The benchmark
    fixture's ``outcome_key`` is the only field interpreted by this module.
    """
    _exact_str(capability_key, "capability_key")
    _nonempty(capability_key, "capability_key")
    _exact_str(evidence_type, "evidence_type")
    _nonempty(evidence_type, "evidence_type")
    _exact_str(outcome_key, "outcome_key")
    if outcome_key not in _ALLOWED_OUTCOMES:
        raise ValueError(f"unknown outcome_key {outcome_key!r}.")
    if source_reference is not None:
        _exact_str(source_reference, "source_reference")
    if isinstance(facts, (str, bytes)) or not isinstance(facts, Sequence):
        raise TypeError("facts must be an ordered sequence of strings.")
    frozen_facts = tuple(facts)
    for index, fact in enumerate(frozen_facts):
        _exact_str(fact, f"facts[{index}]")
    return MappingProxyType({
        "capability_key": capability_key,
        "evidence_type": evidence_type,
        "facts": frozen_facts,
        "source_reference": source_reference,
        "outcome_key": outcome_key,
    })


def benchmark_opportunity(*, already_complete: bool = False) -> RevenueOpportunityState:
    """Return the immutable benchmark opportunity state at initialization."""
    if type(already_complete) is not bool:
        raise TypeError("already_complete must be exactly bool.")
    unresolved = () if already_complete else (_MARKET_SIGNAL, _COMMERCIAL_FIT)
    outcome = "PURSUE" if already_complete else None
    return _state(
        evidence=(),
        unresolved_questions=unresolved,
        declared_success_probability=BENCHMARK_INITIAL_PROBABILITY,
        outcome=outcome,
    )


def initialize_benchmark_run(
    *,
    already_complete: bool = False,
    task_value: Money = BENCHMARK_OPPORTUNITY_VALUE,
    initial_budget: Money = BENCHMARK_INITIAL_BUDGET,
    remaining_budget: Money | None = None,
    policy: RunPolicy = BENCHMARK_POLICY,
) -> RunState:
    """Create the benchmark's domain-initialized TASK-007 run state."""
    if type(already_complete) is not bool:
        raise TypeError("already_complete must be exactly bool.")
    if remaining_budget is None:
        remaining_budget = initial_budget
    running = begin_run(
        task_value=task_value,
        initial_budget=initial_budget,
        remaining_budget=remaining_budget,
        policy=policy,
        task_state=benchmark_opportunity(already_complete=already_complete),
        current_success_probability=BENCHMARK_INITIAL_PROBABILITY,
    )
    if not already_complete:
        return running
    return replace(running, status=RunStatus.TASK_COMPLETE)


class RevenueOpportunityUpdater:
    """Interpret declared benchmark evidence after a successful capability."""

    def update(
        self,
        previous_task_state: Any,
        execution_result: ExecutionResult,
    ) -> TaskStateUpdate:
        """Apply one declared evidence transition without economic reasoning."""
        _validate_state(previous_task_state)
        if type(execution_result) is not ExecutionResult:
            raise TypeError(
                "execution_result must be exactly ExecutionResult, got "
                f"{type(execution_result).__name__}."
            )
        if not execution_result.succeeded:
            raise ValueError(
                "RevenueOpportunityUpdater accepts only successful execution results."
            )

        evidence = _validate_evidence(execution_result.evidence)
        previous_probability = previous_task_state["declared_success_probability"]
        next_probability, resolved_question = _transition(
            previous_probability, evidence["outcome_key"]
        )
        unresolved = tuple(
            question
            for question in previous_task_state["unresolved_questions"]
            if question != resolved_question
        )
        complete = len(unresolved) == 0
        updated = _state(
            evidence=previous_task_state["evidence"] + (evidence,),
            unresolved_questions=unresolved,
            declared_success_probability=next_probability,
            outcome="PURSUE" if complete else None,
        )
        return TaskStateUpdate(
            task_state=updated,
            current_success_probability=next_probability,
            task_complete=complete,
        )


def _transition(probability: Probability, outcome_key: str) -> tuple[Probability, str]:
    if outcome_key == _POSITIVE_MARKET_SIGNAL:
        expected, next_probability, question = (
            BENCHMARK_INITIAL_PROBABILITY,
            BENCHMARK_P1_PROBABILITY,
            _MARKET_SIGNAL,
        )
    elif outcome_key == _POSITIVE_COMMERCIAL_FIT:
        expected, next_probability, question = (
            BENCHMARK_P1_PROBABILITY,
            BENCHMARK_P2_PROBABILITY,
            _COMMERCIAL_FIT,
        )
    else:
        raise ValueError(f"unknown outcome_key {outcome_key!r}.")
    if probability != expected:
        raise ValueError(
            f"outcome_key {outcome_key!r} is not valid at declared probability "
            f"{probability}; expected {expected}."
        )
    return next_probability, question


def _state(
    *,
    evidence: tuple[BenchmarkEvidence, ...],
    unresolved_questions: tuple[str, ...],
    declared_success_probability: Probability,
    outcome: str | None,
) -> RevenueOpportunityState:
    if type(evidence) is not tuple:
        raise TypeError("evidence must be exactly tuple.")
    if type(unresolved_questions) is not tuple:
        raise TypeError("unresolved_questions must be exactly tuple.")
    if type(declared_success_probability) is not Probability:
        raise TypeError("declared_success_probability must be exactly Probability.")
    if outcome is not None:
        _exact_str(outcome, "outcome")
        if outcome not in {"PURSUE", "ABANDON", "ESCALATE"}:
            raise ValueError(f"unknown benchmark outcome {outcome!r}.")
    for index, item in enumerate(evidence):
        _validate_evidence(item, label=f"evidence[{index}]")
    for index, question in enumerate(unresolved_questions):
        _exact_str(question, f"unresolved_questions[{index}]")
    return MappingProxyType({
        "opportunity_id": "ethonline-crypto-infrastructure-contract",
        "opportunity_description": "A crypto-native infrastructure contract.",
        "potential_contract_value": Money("50000.00"),
        "evidence": evidence,
        "unresolved_questions": unresolved_questions,
        "declared_success_probability": declared_success_probability,
        "completion_condition": "all_required_questions_resolved",
        "outcome": outcome,
    })


def _validate_state(state: Any) -> None:
    if type(state) is not MappingProxyType:
        raise TypeError(
            "previous_task_state must be exactly an immutable benchmark state "
            "created by benchmark_opportunity."
        )
    required = {
        "opportunity_id",
        "opportunity_description",
        "potential_contract_value",
        "evidence",
        "unresolved_questions",
        "declared_success_probability",
        "completion_condition",
        "outcome",
    }
    if set(state) != required:
        raise TypeError("previous_task_state has an invalid benchmark state shape.")
    _exact_str(state["opportunity_id"], "opportunity_id")
    _exact_str(state["opportunity_description"], "opportunity_description")
    if type(state["potential_contract_value"]) is not Money:
        raise TypeError("potential_contract_value must be exactly Money.")
    if type(state["evidence"]) is not tuple:
        raise TypeError("state evidence must be exactly tuple.")
    for index, item in enumerate(state["evidence"]):
        _validate_evidence(item, label=f"state evidence[{index}]")
    if type(state["unresolved_questions"]) is not tuple:
        raise TypeError("unresolved_questions must be exactly tuple.")
    for index, item in enumerate(state["unresolved_questions"]):
        _exact_str(item, f"unresolved_questions[{index}]")
    if type(state["declared_success_probability"]) is not Probability:
        raise TypeError("declared_success_probability must be exactly Probability.")
    if state["completion_condition"] != "all_required_questions_resolved":
        raise ValueError("unsupported completion_condition.")
    if state["outcome"] is not None:
        _exact_str(state["outcome"], "outcome")


def _validate_evidence(evidence: Any, *, label: str = "evidence") -> BenchmarkEvidence:
    if type(evidence) is not MappingProxyType:
        raise TypeError(f"{label} must be an immutable benchmark evidence mapping.")
    required = {
        "capability_key",
        "evidence_type",
        "facts",
        "source_reference",
        "outcome_key",
    }
    if set(evidence) != required:
        raise TypeError(f"{label} has an invalid evidence shape.")
    _exact_str(evidence["capability_key"], f"{label}.capability_key")
    _exact_str(evidence["evidence_type"], f"{label}.evidence_type")
    if type(evidence["facts"]) is not tuple:
        raise TypeError(f"{label}.facts must be exactly tuple.")
    for index, fact in enumerate(evidence["facts"]):
        _exact_str(fact, f"{label}.facts[{index}]")
    source = evidence["source_reference"]
    if source is not None:
        _exact_str(source, f"{label}.source_reference")
    _exact_str(evidence["outcome_key"], f"{label}.outcome_key")
    if evidence["outcome_key"] not in _ALLOWED_OUTCOMES:
        raise ValueError(f"unknown outcome_key {evidence['outcome_key']!r}.")
    return evidence


def _exact_str(value: Any, label: str) -> None:
    if type(value) is not str:
        raise TypeError(f"{label} must be exactly str, got {type(value).__name__}.")


def _nonempty(value: str, label: str) -> None:
    if not value or value.strip() != value:
        raise ValueError(f"{label} must be non-empty and trimmed.")
