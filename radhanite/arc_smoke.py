"""Explicit opt-in TASK-015 Arc Testnet smoke command.

**Implementation agent: Manus.**

This command never runs during normal tests and never falls back to Base. It
assumes a pre-provisioned Circle Developer-Controlled Wallet EOA and a
pre-funded Gateway balance; it never creates or funds either one.
"""

from __future__ import annotations

import json
import os

from radhanite.arc import (
    ARC_TESTNET_NETWORK,
    ARC_TESTNET_USDC,
    CircleArcDeveloperWalletPaymentClient,
    arc_demo_catalog,
    arc_setup_blockers,
)
from radhanite.circle import CircleCapabilityExecutor
from radhanite.money import Money
from radhanite.probability import Probability
from radhanite.revenue import RevenueOpportunityUpdater, initialize_benchmark_run
from radhanite.loop import run_capability_loop


def main() -> int:
    blockers = arc_setup_blockers()
    if blockers:
        return _blocker("Arc setup is not ready", "; ".join(blockers))
    try:
        resource = os.environ["RADHANITE_ARC_RESOURCE"]
        price = Money(os.environ["RADHANITE_ARC_PRICE"])
        probability = Probability(os.environ.get("RADHANITE_ARC_PROBABILITY", "0.14"))
        catalog = arc_demo_catalog(
            resource=resource,
            price=price,
            expected_post_action_success_probability=probability,
        )
        offer = catalog.offers[0]
        state = initialize_benchmark_run()
        payment_client = CircleArcDeveloperWalletPaymentClient(
            wallet_id=os.environ["CIRCLE_ARC_WALLET_ID"],
            wallet_address=os.environ["CIRCLE_ARC_WALLET_ADDRESS"],
        )
        result = run_capability_loop(
            state=state,
            candidate_source=_OneOfferSource(catalog.candidates),
            executor=_ReportingExecutor(catalog=catalog, payment_client=payment_client),
            updater=RevenueOpportunityUpdater(),
        )
        transition = result.history[0]
        execution = transition.execution
        selection = transition.selection
        selected = selection.selected
        if selected is None:
            print(json.dumps({"status": "stopped", "task006_decision": selection.reason}))
            return 0
        facts = execution.evidence["facts"] if execution else ()
        print(json.dumps({
            "status": "ok",
            "wallet_model": "Circle Developer-Controlled Wallet EOA",
            "wallet_id": os.environ["CIRCLE_ARC_WALLET_ID"],
            "wallet_address": os.environ["CIRCLE_ARC_WALLET_ADDRESS"],
            "network": ARC_TESTNET_NETWORK,
            "asset": ARC_TESTNET_USDC,
            "resource": resource,
            "quoted_testnet_usdc": str(offer.quoted_cost.amount),
            "task006_selected_candidate": selected.candidate.candidate_id,
            "x402_payment_execution": "completed",
            "run_status": result.status.value,
            "committed_testnet_usdc": str(execution.committed_cost.amount) if execution else None,
            "payment_facts": facts,
            "service_result_summary": "service response retained in Arc payment evidence",
            "task009_probability": str(result.current_success_probability.value),
            "task009_evidence_count": len(result.task_state["evidence"]),
        }))
        return 0
    except Exception as exc:  # Safe, actionable human blocker; no secret output.
        return _blocker("Arc smoke stopped before a trustworthy result", str(exc))


class _OneOfferSource:
    def __init__(self, candidates):
        self._candidates = tuple(candidates)

    def get_candidates(self, task_state, run_state):
        return self._candidates


class _ReportingExecutor(CircleCapabilityExecutor):
    """Print the selected TASK-006 economics immediately before payment."""

    def execute(self, selected_candidate, current_state, maximum_authorized_cost):
        incremental = current_state.task_value * (
            selected_candidate.success_probability - current_state.current_success_probability
        )
        print(json.dumps({
            "status": "selected_before_signing",
            "wallet_model": "Circle Developer-Controlled Wallet EOA",
            "wallet_id": os.environ["CIRCLE_ARC_WALLET_ID"],
            "wallet_address": os.environ["CIRCLE_ARC_WALLET_ADDRESS"],
            "network": ARC_TESTNET_NETWORK,
            "resource": os.environ["RADHANITE_ARC_RESOURCE"],
            "exact_testnet_usdc_quote": str(selected_candidate.cost.amount),
            "current_success_probability": str(current_state.current_success_probability.value),
            "expected_post_action_probability": str(selected_candidate.success_probability.value),
            "incremental_expected_value": str(incremental.amount),
            "maximum_authorized_spend": str(maximum_authorized_cost.amount),
            "task006_selection_result": "selected; TASK-007 execution begins now",
        }))
        return super().execute(selected_candidate, current_state, maximum_authorized_cost)


def _blocker(summary: str, detail: str) -> int:
    print(json.dumps({
        "status": "blocked",
        "network": ARC_TESTNET_NETWORK,
        "summary": summary,
        "detail": detail[:500],
        "required_setup": [
            "CIRCLE_API_KEY",
            "CIRCLE_ENTITY_SECRET",
            "CIRCLE_ARC_WALLET_ID",
            "CIRCLE_ARC_WALLET_ADDRESS",
            "RADHANITE_ARC_RESOURCE",
            "RADHANITE_ARC_PRICE",
            "pre-provisioned EOA Developer-Controlled Wallet on ARC-TESTNET",
            "testnet USDC funded from the Circle Faucet",
            "Gateway balance deposited for nanopayments",
        ],
        "fallback": "none; Base is not used as an Arc fallback",
    }))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
