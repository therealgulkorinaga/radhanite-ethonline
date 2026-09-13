"""Explicit opt-in TASK-010 Arc Testnet smoke command.

**Implementation agent: Manus.**

This command never runs during normal tests and never falls back to Base. It
requires a URL for an official Circle Arc x402 demo seller, then runs the
normal Radhanite selection and execution boundaries around one exact quote.
"""

from __future__ import annotations

import json
import os
import sys

from radhanite.arc import (
    ARC_TESTNET_NETWORK,
    ARC_TESTNET_USDC,
    CircleArcDeveloperWalletPaymentClient,
    arc_demo_catalog,
)
from radhanite.circle import CircleCapabilityExecutor
from radhanite.money import Money
from radhanite.probability import Probability
from radhanite.revenue import RevenueOpportunityUpdater, initialize_benchmark_run
from radhanite.loop import run_capability_loop


def main() -> int:
    resource = os.environ.get("Radhanite_ARC_RESOURCE")
    if not resource:
        return _blocker(
            "Radhanite_ARC_RESOURCE is missing",
            "Set it to the official Circle Arc x402 demo seller URL.",
        )
    try:
        price = Money(os.environ.get("Radhanite_ARC_PRICE", "0.001"))
        probability = Probability(os.environ.get("Radhanite_ARC_PROBABILITY", "0.14"))
        catalog = arc_demo_catalog(
            resource=resource,
            price=price,
            expected_post_action_success_probability=probability,
        )
        offer = catalog.offers[0]
        state = initialize_benchmark_run()
        result = run_capability_loop(
            state=state,
            candidate_source=_OneOfferSource(catalog.candidates),
            executor=CircleCapabilityExecutor(
                catalog=catalog,
                payment_client=CircleArcDeveloperWalletPaymentClient(
                    wallet_address=os.environ.get("CIRCLE_ARC_WALLET_ADDRESS"),
                ),
            ),
            updater=RevenueOpportunityUpdater(),
        )
        execution = result.history[0].execution
        facts = execution.evidence["facts"] if execution else ()
        print(json.dumps({
            "status": "ok",
            "wallet_model": "Circle Developer-Controlled Wallet EOA",
            "network": ARC_TESTNET_NETWORK,
            "asset": ARC_TESTNET_USDC,
            "quoted_price": str(offer.quoted_cost.amount),
            "run_status": result.status.value,
            "total_spend": str(result.total_spend.amount),
            "payment_facts": facts,
            "task009_probability": str(result.current_success_probability.value),
            "task009_evidence_count": len(result.task_state["evidence"]),
        }))
        return 0
    except Exception as exc:  # The report is a safe, actionable human blocker.
        return _blocker("Arc smoke stopped before a trustworthy result", str(exc))


class _OneOfferSource:
    def __init__(self, candidates):
        self._candidates = tuple(candidates)

    def get_candidates(self, task_state, run_state):
        return self._candidates


def _blocker(summary: str, detail: str) -> int:
    print(json.dumps({
        "status": "blocked",
        "network": ARC_TESTNET_NETWORK,
        "summary": summary,
        "detail": detail[:500],
        "required_setup": [
            "CIRCLE_API_KEY",
            "CIRCLE_ENTITY_SECRET",
            "an EOA Developer-Controlled Wallet on ARC-TESTNET",
            "testnet USDC funded from the Circle Faucet",
            "Gateway balance deposited for nanopayments",
            "Radhanite_ARC_RESOURCE pointing to an official Arc x402 demo seller",
        ],
        "fallback": "none; Base is not used as an Arc fallback",
    }))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
