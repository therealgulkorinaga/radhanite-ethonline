"""Critical TASK-010 Arc testnet wallet/x402 boundary tests.

**Implementation agent: Manus.**

External Circle SDK, wallet, HTTP, and seller calls are mocked. These tests
prove that Arc is explicit, selection precedes payment, exact amounts and
references are retained, and TASK-009 receives the execution evidence.
"""

from __future__ import annotations

import json
import subprocess
import unittest
from dataclasses import replace
from unittest.mock import Mock

from radhanite.arc import (
    ARC_TESTNET_NETWORK,
    ARC_TESTNET_USDC,
    CircleArcDeveloperWalletPaymentClient,
    arc_demo_catalog,
)
from radhanite.capability_execution import ExecutionResult
from radhanite.circle import CircleCapabilityExecutor, CirclePaymentReceipt
from radhanite.loop import run_capability_loop
from radhanite.money import Money
from radhanite.probability import Probability
from radhanite.revenue import RevenueOpportunityUpdater, initialize_benchmark_run
from radhanite.runstate import RunStatus


RESOURCE = "https://arc-demo.example.test/api/premium/quote"


def arc_offer_catalog():
    return arc_demo_catalog(
        resource=RESOURCE,
        price=Money("0.001"),
        expected_post_action_success_probability=Probability("0.14"),
    )


class ArcTests(unittest.TestCase):
    def test_arc_constants_and_demo_offer_are_explicit(self) -> None:
        catalog = arc_offer_catalog()
        offer = catalog.offer_for(catalog.candidates[0].candidate_id)
        self.assertEqual(offer.network, ARC_TESTNET_NETWORK)
        self.assertEqual(offer.asset, ARC_TESTNET_USDC)
        self.assertEqual(offer.quoted_cost, Money("0.001"))
        self.assertEqual(offer.scheme, "GatewayWalletBatched")
        self.assertIn("official Circle Arc", offer.source_reference)

    def test_base_offer_cannot_masquerade_as_arc(self) -> None:
        client = CircleArcDeveloperWalletPaymentClient(
            runner=Mock(), wallet_address="0xarc", node="node"
        )
        catalog = arc_offer_catalog()
        offer = catalog.offer_for(catalog.candidates[0].candidate_id)
        bad_offer = replace(offer, network="eip155:8453")
        with self.assertRaises(ValueError):
            client.pay(bad_offer, Money("0.001"))

    def test_wrong_network_is_rejected_before_signing(self) -> None:
        runner = Mock()
        client = CircleArcDeveloperWalletPaymentClient(
            runner=runner, wallet_address="0xarc", node="node"
        )
        catalog = arc_offer_catalog()
        offer = catalog.offer_for(catalog.candidates[0].candidate_id)
        with self.assertRaises(ValueError):
            client.pay(offer, Money("0.002"))
        runner.assert_not_called()

    def test_arc_payment_preserves_exact_amount_and_reference(self) -> None:
        runner = Mock(
            return_value=subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout=json.dumps(
                    {
                        "status": "settled",
                        "network": ARC_TESTNET_NETWORK,
                        "asset": ARC_TESTNET_USDC,
                        "amount": "0.001",
                        "payment_reference": "0xarc-payment-reference",
                        "response_status": 200,
                        "result": {"quote": "42"},
                    }
                ),
                stderr="",
            )
        )
        client = CircleArcDeveloperWalletPaymentClient(
            runner=runner, wallet_address="0xarc", node="node"
        )
        offer = arc_offer_catalog().offer_for("arc-demo:quote")
        receipt = client.pay(offer, Money("0.001"))
        self.assertIsInstance(receipt, CirclePaymentReceipt)
        self.assertEqual(receipt.committed_cost, Money("0.001"))
        self.assertIn(
            "payment_reference=0xarc-payment-reference",
            receipt.evidence["facts"],
        )
        command = runner.call_args.args[0]
        self.assertIn(ARC_TESTNET_NETWORK, command)
        self.assertIn("0.001", command)
        self.assertIn("--wallet-address", command)

    def test_non_selected_arc_capability_is_never_paid(self) -> None:
        first = arc_demo_catalog(
            resource=RESOURCE,
            price=Money("0.001"),
            expected_post_action_success_probability=Probability("0.14"),
        )
        second = arc_demo_catalog(
            resource=RESOURCE + "/other",
            price=Money("0.002"),
            expected_post_action_success_probability=Probability("0.14"),
        )
        candidates = first.candidates + second.candidates
        offers = first.offers + second.offers
        catalog = type(first)(
            catalog=type(first.catalog)(entries=(
                (candidates[0], first.descriptor_for(candidates[0].candidate_id)),
                (candidates[1], second.descriptor_for(candidates[1].candidate_id)),
            )),
            offers=offers,
        )
        runner = Mock(
            return_value=subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout=json.dumps(
                    {
                        "status": "settled",
                        "network": ARC_TESTNET_NETWORK,
                        "asset": ARC_TESTNET_USDC,
                        "amount": "0.001",
                        "payment_reference": "ref",
                        "response_status": 200,
                    }
                ),
                stderr="",
            )
        )
        payment = CircleArcDeveloperWalletPaymentClient(
            runner=runner, wallet_address="0xarc", node="node"
        )
        result = run_capability_loop(
            state=initialize_benchmark_run(),
            candidate_source=type(
                "Source", (), {"get_candidates": lambda self, task_state, run_state: candidates}
            )(),
            executor=CircleCapabilityExecutor(
                catalog=catalog, payment_client=payment
            ),
            updater=RevenueOpportunityUpdater(),
        )
        self.assertEqual(runner.call_count, 1)
        self.assertEqual(result.history[0].execution.committed_cost, Money("0.001"))

    def test_arc_execution_evidence_reaches_task009(self) -> None:
        catalog = arc_offer_catalog()
        runner = Mock(
            return_value=subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout=json.dumps(
                    {
                        "status": "settled",
                        "network": ARC_TESTNET_NETWORK,
                        "asset": ARC_TESTNET_USDC,
                        "amount": "0.001",
                        "payment_reference": "arc-ref",
                        "response_status": 200,
                    }
                ),
                stderr="",
            )
        )
        result = run_capability_loop(
            state=initialize_benchmark_run(),
            candidate_source=type(
                "Source", (), {"get_candidates": lambda self, task_state, run_state: catalog.candidates}
            )(),
            executor=CircleCapabilityExecutor(
                catalog=catalog,
                payment_client=CircleArcDeveloperWalletPaymentClient(
                    runner=runner, wallet_address="0xarc", node="node"
                ),
            ),
            updater=RevenueOpportunityUpdater(),
        )
        self.assertEqual(result.status, RunStatus.ECONOMIC_STOP)
        self.assertEqual(result.total_spend, Money("0.001"))
        facts = result.history[0].execution.evidence["facts"]
        self.assertIn("payment_reference=arc-ref", facts)
        self.assertIn(f"network={ARC_TESTNET_NETWORK}", facts)
        self.assertIsInstance(result.history[0].execution, ExecutionResult)


if __name__ == "__main__":
    unittest.main()
