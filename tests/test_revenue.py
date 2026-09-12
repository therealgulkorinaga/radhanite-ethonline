"""TASK-009 revenue-opportunity state and updater tests.

**Implementation agent: Manus.**

These tests cover only the authorized benchmark boundary: immutable opportunity
state, declared fixture probabilities, deterministic evidence interpretation,
initializer completion ownership, and one TASK-006/TASK-007 end-to-end path.
"""

from __future__ import annotations

import unittest
from types import MappingProxyType
from unittest.mock import patch

from radhanite.capability import Candidate
from radhanite.capability_execution import ExecutionResult
from radhanite.loop import run_capability_loop
from radhanite.money import Money
from radhanite.policy import RunPolicy
from radhanite.probability import Probability
from radhanite.revenue import (
    BENCHMARK_INITIAL_PROBABILITY,
    BENCHMARK_P1_PROBABILITY,
    BENCHMARK_P2_PROBABILITY,
    BenchmarkEvidence,
    RevenueOpportunityUpdater,
    benchmark_opportunity,
    initialize_benchmark_run,
    make_evidence,
)
from radhanite.runstate import RunState, RunStatus


class RevenueCandidateSource:
    """Offer a fixture sequence based on opaque state, not updater order."""

    def __init__(self, offers: list[tuple[Candidate, ...]]) -> None:
        self.offers = list(offers)
        self.calls: list[object] = []

    def get_candidates(self, task_state: object, run_state: RunState):
        self.calls.append(task_state)
        return self.offers.pop(0) if self.offers else ()


class RevenueExecutor:
    def __init__(self, results: list[ExecutionResult]) -> None:
        self.results = list(results)
        self.calls: list[Candidate] = []

    def execute(self, selected_candidate, current_state, maximum_authorized_cost):
        self.calls.append(selected_candidate)
        return self.results.pop(0)


def candidate(
    identifier: str, cost: str = "1.00", probability: str = "0.90"
) -> Candidate:
    return Candidate(identifier, Money(cost), Probability(probability))


class RevenueStateTests(unittest.TestCase):
    def test_initializer_produces_running_for_incomplete_opportunity(self) -> None:
        run = initialize_benchmark_run()

        self.assertIs(run.status, RunStatus.RUNNING)
        self.assertEqual(run.current_success_probability, BENCHMARK_INITIAL_PROBABILITY)
        self.assertEqual(run.task_state["unresolved_questions"], (
            "market_signal",
            "commercial_fit",
        ))

    def test_initializer_produces_task_complete_for_already_complete_opportunity(self) -> None:
        run = initialize_benchmark_run(already_complete=True)

        self.assertIs(run.status, RunStatus.TASK_COMPLETE)
        self.assertEqual(run.task_state["unresolved_questions"], ())
        self.assertEqual(run.task_state["outcome"], "PURSUE")

    def test_initial_probability_is_the_declared_fixture_exactly(self) -> None:
        state = benchmark_opportunity()

        self.assertIs(state["declared_success_probability"], BENCHMARK_INITIAL_PROBABILITY)
        self.assertEqual(BENCHMARK_INITIAL_PROBABILITY, Probability("0.08"))

    def test_state_and_evidence_are_immutable_and_do_not_alias_inputs(self) -> None:
        facts = ["protocol activity confirmed"]
        evidence = make_evidence(
            capability_key="signal-a",
            evidence_type="commercial_signal",
            facts=facts,
            source_reference="fixture:signal-a",
            outcome_key="positive_market_signal",
        )
        state = benchmark_opportunity()
        facts.append("caller mutation")

        self.assertIsInstance(evidence, MappingProxyType)
        self.assertEqual(evidence["facts"], ("protocol activity confirmed",))
        self.assertIsInstance(state, MappingProxyType)
        with self.assertRaises(TypeError):
            state["opportunity_id"] = "changed"  # type: ignore[index]

    def test_successful_evidence_updates_state_and_declared_probability(self) -> None:
        previous = benchmark_opportunity()
        execution = ExecutionResult(True, Money("0.00"), make_evidence(
            capability_key="signal-a",
            evidence_type="commercial_signal",
            facts=("activity confirmed",),
            source_reference=None,
            outcome_key="positive_market_signal",
        ))

        update = RevenueOpportunityUpdater().update(previous, execution)

        self.assertEqual(update.current_success_probability, BENCHMARK_P1_PROBABILITY)
        self.assertEqual(update.task_state["declared_success_probability"], BENCHMARK_P1_PROBABILITY)
        self.assertEqual(update.task_state["unresolved_questions"], ("commercial_fit",))
        self.assertEqual(len(update.task_state["evidence"]), 1)
        self.assertFalse(update.task_complete)
        self.assertEqual(BENCHMARK_P1_PROBABILITY, Probability("0.14"))

    def test_second_declared_fixture_transition_completes_task(self) -> None:
        previous = RevenueOpportunityUpdater().update(
            benchmark_opportunity(),
            ExecutionResult(True, Money("1.00"), make_evidence(
                capability_key="signal-a",
                evidence_type="commercial_signal",
                facts=("activity confirmed",),
                source_reference=None,
                outcome_key="positive_market_signal",
            )),
        ).task_state
        execution = ExecutionResult(True, Money("99.00"), make_evidence(
            capability_key="signal-b",
            evidence_type="commercial_fit",
            facts=("fit confirmed",),
            source_reference=None,
            outcome_key="positive_commercial_fit",
        ))

        update = RevenueOpportunityUpdater().update(previous, execution)

        self.assertEqual(update.current_success_probability, BENCHMARK_P2_PROBABILITY)
        self.assertTrue(update.task_complete)
        self.assertEqual(update.task_state["unresolved_questions"], ())
        self.assertEqual(update.task_state["outcome"], "PURSUE")
        self.assertEqual(BENCHMARK_P2_PROBABILITY, Probability("0.17"))

    def test_non_completion_evidence_returns_false(self) -> None:
        execution = ExecutionResult(True, Money("1.00"), make_evidence(
            capability_key="signal-a",
            evidence_type="commercial_signal",
            facts=("activity confirmed",),
            source_reference=None,
            outcome_key="positive_market_signal",
        ))

        update = RevenueOpportunityUpdater().update(benchmark_opportunity(), execution)

        self.assertFalse(update.task_complete)

    def test_malformed_or_unknown_evidence_is_rejected_deterministically(self) -> None:
        updater = RevenueOpportunityUpdater()
        malformed = MappingProxyType({"outcome_key": "positive_market_signal"})
        unknown = MappingProxyType({
            "capability_key": "signal-x",
            "evidence_type": "unknown",
            "facts": (),
            "source_reference": None,
            "outcome_key": "invented_outcome",
        })

        with self.assertRaisesRegex(TypeError, "evidence"):
            updater.update(benchmark_opportunity(), ExecutionResult(True, Money("0.00"), malformed))
        with self.assertRaisesRegex(ValueError, "outcome_key"):
            updater.update(benchmark_opportunity(), ExecutionResult(True, Money("0.00"), unknown))

    def test_failed_execution_result_is_rejected_by_domain_updater(self) -> None:
        execution = ExecutionResult(False, Money("1.00"), MappingProxyType({}))

        with self.assertRaisesRegex(ValueError, "successful"):
            RevenueOpportunityUpdater().update(benchmark_opportunity(), execution)

    def test_updater_does_not_use_cost_or_select_capabilities(self) -> None:
        evidence = make_evidence(
            capability_key="signal-a",
            evidence_type="commercial_signal",
            facts=("activity confirmed",),
            source_reference=None,
            outcome_key="positive_market_signal",
        )
        updater = RevenueOpportunityUpdater()

        with patch("radhanite.selection.select_capability") as selector:
            first = updater.update(
                benchmark_opportunity(), ExecutionResult(True, Money("0.00"), evidence)
            )
            second = updater.update(
                benchmark_opportunity(), ExecutionResult(True, Money("99.00"), evidence)
            )

        self.assertEqual(first.task_state, second.task_state)
        self.assertEqual(first.current_success_probability, second.current_success_probability)
        selector.assert_not_called()

    def test_provider_identity_is_not_required_by_evidence_contract(self) -> None:
        evidence = make_evidence(
            capability_key="signal-a",
            evidence_type="commercial_signal",
            facts=("activity confirmed",),
            source_reference=None,
            outcome_key="positive_market_signal",
        )

        self.assertNotIn("provider", evidence)
        update = RevenueOpportunityUpdater().update(
            benchmark_opportunity(), ExecutionResult(True, Money("1.00"), evidence)
        )
        self.assertNotIn("provider", update.task_state["evidence"][0])

    def test_task007_full_loop_uses_real_task009_updater(self) -> None:
        source = RevenueCandidateSource([
            (candidate("signal-a", "1.00"),),
            (candidate("signal-b", "1.00", probability="0.17"),),
        ])
        executor = RevenueExecutor([
            ExecutionResult(True, Money("1.00"), make_evidence(
                capability_key="signal-a",
                evidence_type="commercial_signal",
                facts=("activity confirmed",),
                source_reference=None,
                outcome_key="positive_market_signal",
            )),
            ExecutionResult(True, Money("1.00"), make_evidence(
                capability_key="signal-b",
                evidence_type="commercial_fit",
                facts=("fit confirmed",),
                source_reference=None,
                outcome_key="positive_commercial_fit",
            )),
        ])

        result = run_capability_loop(
            state=initialize_benchmark_run(),
            candidate_source=source,
            executor=executor,
            updater=RevenueOpportunityUpdater(),
        )

        self.assertIs(result.status, RunStatus.TASK_COMPLETE)
        self.assertEqual(result.current_success_probability, BENCHMARK_P2_PROBABILITY)
        self.assertEqual(result.task_state["outcome"], "PURSUE")
        self.assertEqual([item.candidate_id for item in executor.calls], ["signal-a", "signal-b"])
        self.assertEqual(len(result.history), 2)
        self.assertEqual(
            [state["declared_success_probability"] for state in source.calls],
            [BENCHMARK_INITIAL_PROBABILITY, BENCHMARK_P1_PROBABILITY],
        )
        second_selection = result.history[1].selection
        self.assertEqual(
            second_selection.current_success_probability,
            BENCHMARK_P1_PROBABILITY,
        )
        self.assertEqual(
            second_selection.selected.incremental_expected_value,
            Money("1500.00"),
        )


if __name__ == "__main__":
    unittest.main()
