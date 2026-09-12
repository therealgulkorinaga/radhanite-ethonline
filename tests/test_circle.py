"""TASK-010 Circle discovery and Arc/Gateway adapter tests.

**Implementation agent: Manus.**

These tests cover the thin provider boundary only: exact pre-purchase quotes,
provider-neutral normalization, safe descriptor recovery, selection-before-payment,
explicit authorization ceilings, exact committed-cost accounting, and benchmark
evidence handoff. External HTTP and Circle CLI calls are mocked.
"""

from __future__ import annotations

import json
import unittest
from unittest.mock import Mock, patch

from radhanite.capability import Candidate
from radhanite.capability_execution import ExecutionResult
from radhanite.circle import (
    CircleCapabilityExecutor,
    CircleDiscoveryError,
    CircleOffer,
    CirclePaymentReceipt,
    catalog_from_circle_response,
    live_circle_discovery,
)
from radhanite.loop import run_capability_loop
from radhanite.money import Money
from radhanite.policy import RunPolicy
from radhanite.probability import Probability
from radhanite.revenue import (
    BENCHMARK_INITIAL_PROBABILITY,
    RevenueOpportunityUpdater,
    initialize_benchmark_run,
    make_evidence,
)
from radhanite.runstate import RunStatus


RESOURCE = "https://api.aisa.one/apis/v2/coingecko/simple/price"


def discovery_payload(*, amount: str = "12000", supports_gateway: bool = True) -> dict:
    return {
        "x402Version": 2,
        "items": [
            {
                "resource": RESOURCE,
                "type": "http",
                "x402Version": 2,
                "accepts": [
                    {
                        "scheme": "exact",
                        "network": "eip155:8453",
                        "asset": "0x833589fcd6edb6e08f4c7c32d4f71b54bdA02913",
                        "payTo": "0xBd7b9f3e0CD3E1f6e698D0eeBb99F96E093BdeE3",
                        "amount": amount,
                        "maxTimeoutSeconds": 604900,
                        "extra": {
                            "name": "GatewayWalletBatched",
                            "version": "1",
                        },
                    }
                ],
                "metadata": {
                    "description": "Simple Price",
                    "method": "GET",
                    "provider": {
                        "name": "AIsa API",
                        "category": "FINANCIAL_ANALYSIS",
                    },
                    "input": {
                        "queryParams": {
                            "required": ["ids", "vs_currencies"],
                        }
                    },
                    "supportsCircleGateway": supports_gateway,
                    "supportsVanillax402": False,
                },
            }
        ],
    }


class CircleTests(unittest.TestCase):
    def test_live_discovery_uses_public_endpoint_and_exact_quote(self) -> None:
        opener = Mock(return_value=discovery_payload())

        catalog = live_circle_discovery(
            opener=opener,
            expected_post_action_success_probability=Probability("0.14"),
            request_query="ids=bitcoin%2 ethereum&vs_currencies=usd".replace("%2 ", "%2C"),
            network="eip155:8453",
        )

        opener.assert_called_once()
        self.assertIn("api.circle.com/v2/x402/discovery/resources", opener.call_args.args[0].full_url)
        self.assertIn("ids=bitcoin%2Cethereum", opener.call_args.args[0].full_url)
        self.assertEqual(len(catalog), 1)
        candidate = catalog.candidates[0]
        self.assertEqual(candidate.cost, Money("0.012"))
        self.assertEqual(candidate.success_probability, Probability("0.14"))
        self.assertNotIn("AIsa", vars(candidate) if hasattr(candidate, "__dict__") else {})
        self.assertEqual(catalog.descriptor_for(candidate.candidate_id).name, "Simple Price")

    def test_unknown_or_non_gateway_price_is_excluded(self) -> None:
        with self.assertRaises(CircleDiscoveryError):
            catalog_from_circle_response(
                discovery_payload(supports_gateway=False),
                expected_post_action_success_probability=Probability("0.14"),
                network="eip155:8453",
            )

    def test_provider_metadata_stays_on_offer_not_candidate(self) -> None:
        catalog = catalog_from_circle_response(
            discovery_payload(),
            expected_post_action_success_probability=Probability("0.14"),
            network="eip155:8453",
        )
        candidate = catalog.candidates[0]
        descriptor = catalog.descriptor_for(candidate.candidate_id)
        self.assertEqual(
            set(candidate.__dataclass_fields__),
            {"candidate_id", "cost", "success_probability"},
        )
        self.assertEqual(catalog.offer_for(candidate.candidate_id).name, "Simple Price")
        self.assertEqual(descriptor.source_reference, RESOURCE)
        self.assertNotIn("GatewayWalletBatched", repr(candidate))

    def test_discovery_does_not_call_payment_client(self) -> None:
        opener = Mock(return_value=discovery_payload())
        payment = Mock()
        live_circle_discovery(
            opener=opener,
            expected_post_action_success_probability=Probability("0.14"),
            payment_client=payment,
            network="eip155:8453",
        )
        payment.assert_not_called()

    def test_candidate_maps_back_to_provider_offer(self) -> None:
        catalog = catalog_from_circle_response(
            discovery_payload(),
            expected_post_action_success_probability=Probability("0.14"),
            network="eip155:8453",
        )
        offer = catalog.descriptor_for(catalog.candidates[0].candidate_id)
        self.assertEqual(offer.source_reference, RESOURCE)

    def test_executor_receives_selected_candidate_and_authorization_ceiling(self) -> None:
        catalog = catalog_from_circle_response(
            discovery_payload(),
            expected_post_action_success_probability=Probability("0.14"),
            network="eip155:8453",
        )
        receipt = CirclePaymentReceipt(
            succeeded=True,
            committed_cost=Money("0.012"),
            evidence=make_evidence(
                capability_key="circle-market-data",
                evidence_type="market-data",
                facts=("bitcoin price returned",),
                source_reference=RESOURCE,
                outcome_key="positive_market_signal",
            ),
        )
        payment = Mock()
        payment.pay.return_value = receipt
        executor = CircleCapabilityExecutor(catalog=catalog, payment_client=payment)
        state = initialize_benchmark_run()
        candidate = catalog.candidates[0]

        result = executor.execute(candidate, state, Money("0.012"))

        self.assertIsInstance(result, ExecutionResult)
        payment.pay.assert_called_once()
        self.assertEqual(payment.pay.call_args.args[1], Money("0.012"))

    def test_non_selected_candidate_is_never_paid(self) -> None:
        first = discovery_payload()
        second = discovery_payload(amount="13000")
        second["items"][0]["resource"] += "/other"
        response = {"x402Version": 2, "items": first["items"] + second["items"]}
        catalog = catalog_from_circle_response(
            response,
            expected_post_action_success_probability=Probability("0.14"),
            network="eip155:8453",
        )
        payment = Mock()
        payment.pay.return_value = CirclePaymentReceipt(
            True,
            Money("0.012"),
            make_evidence(
                capability_key="circle-market-data",
                evidence_type="market-data",
                facts=("signal",),
                source_reference=RESOURCE,
                outcome_key="positive_market_signal",
            ),
        )
        executor = CircleCapabilityExecutor(catalog=catalog, payment_client=payment)
        state = initialize_benchmark_run()
        result = run_capability_loop(
            state=state,
            candidate_source=type("Source", (), {"get_candidates": lambda self, task_state, run_state: catalog.candidates})(),
            executor=executor,
            updater=RevenueOpportunityUpdater(),
        )
        self.assertEqual(result.status, RunStatus.ECONOMIC_STOP)
        self.assertEqual(payment.pay.call_count, 1)
        self.assertEqual(
            payment.pay.call_args.args[0].descriptor_id,
            catalog.candidates[0].candidate_id,
        )

    def test_executor_rejects_over_authorized_commitment(self) -> None:
        catalog = catalog_from_circle_response(
            discovery_payload(),
            expected_post_action_success_probability=Probability("0.14"),
            network="eip155:8453",
        )
        payment = Mock()
        payment.pay.return_value = CirclePaymentReceipt(
            True,
            Money("0.013"),
            {},
        )
        executor = CircleCapabilityExecutor(catalog=catalog, payment_client=payment)
        with self.assertRaises(ValueError):
            executor.execute(catalog.candidates[0], initialize_benchmark_run(), Money("0.012"))

    def test_successful_payment_records_exact_cost_and_reaches_revenue_updater(self) -> None:
        catalog = catalog_from_circle_response(
            discovery_payload(),
            expected_post_action_success_probability=Probability("0.14"),
            network="eip155:8453",
        )
        payment = Mock()
        payment.pay.return_value = CirclePaymentReceipt(
            True,
            Money("0.012"),
            make_evidence(
                capability_key="circle-market-data",
                evidence_type="market-data",
                facts=("bitcoin price returned",),
                source_reference=RESOURCE,
                outcome_key="positive_market_signal",
            ),
        )
        result = run_capability_loop(
            state=initialize_benchmark_run(),
            candidate_source=type("Source", (), {"get_candidates": lambda self, task_state, run_state: catalog.candidates})(),
            executor=CircleCapabilityExecutor(catalog=catalog, payment_client=payment),
            updater=RevenueOpportunityUpdater(),
        )
        self.assertEqual(result.total_spend, Money("0.012"))
        self.assertEqual(result.current_success_probability, Probability("0.14"))
        self.assertEqual(result.history[0].execution.committed_cost, Money("0.012"))
        self.assertEqual(result.history[0].execution.evidence["outcome_key"], "positive_market_signal")
        self.assertEqual(result.status, RunStatus.ECONOMIC_STOP)

    def test_attempted_failure_records_actual_committed_cost_and_stops(self) -> None:
        catalog = catalog_from_circle_response(
            discovery_payload(),
            expected_post_action_success_probability=Probability("0.14"),
            network="eip155:8453",
        )
        payment = Mock()
        payment.pay.return_value = CirclePaymentReceipt(
            False,
            Money("0.007"),
            make_evidence(
                capability_key="circle-market-data",
                evidence_type="circle_x402_response",
                facts=("payment accepted but service failed",),
                source_reference=RESOURCE,
                outcome_key="positive_market_signal",
            ),
        )
        result = run_capability_loop(
            state=initialize_benchmark_run(),
            candidate_source=type("Source", (), {"get_candidates": lambda self, task_state, run_state: catalog.candidates})(),
            executor=CircleCapabilityExecutor(catalog=catalog, payment_client=payment),
            updater=RevenueOpportunityUpdater(),
        )
        self.assertEqual(result.status, RunStatus.EXECUTION_FAILURE)
        self.assertEqual(result.total_spend, Money("0.007"))
        self.assertEqual(result.history[0].execution.committed_cost, Money("0.007"))

    def test_cli_payment_client_requires_explicit_credentials_before_side_effect(self) -> None:
        from radhanite.circle import CircleCliPaymentClient, CirclePreAttemptError

        client = CircleCliPaymentClient(cli="definitely-not-installed-circle")
        offer = CircleOffer(
            descriptor_id="circle:test",
            resource=RESOURCE,
            name="Simple Price",
            method="GET",
            network="eip155:8453",
            quoted_cost=Money("0.012"),
            source_reference=RESOURCE,
        )
        with self.assertRaises(CirclePreAttemptError):
            client.pay(offer, Money("0.012"))

    def test_cli_payment_client_uses_explicit_method_chain_and_cap(self) -> None:
        from radhanite.circle import CircleCliPaymentClient

        runner = Mock(
            return_value=__import__("subprocess").CompletedProcess(
                args=[], returncode=0, stdout='{"price":"0.012"}', stderr=""
            )
        )
        client = CircleCliPaymentClient(
            cli="circle",
            wallet_address="0xwallet",
            chain="BASE",
            runner=runner,
        )
        offer = CircleOffer(
            descriptor_id="circle:test",
            resource=RESOURCE,
            name="Simple Price",
            method="GET",
            network="eip155:8453",
            quoted_cost=Money("0.012"),
            source_reference=RESOURCE,
        )
        with patch("radhanite.circle.shutil.which", return_value="/usr/bin/circle"):
            receipt = client.pay(offer, Money("0.012"))
        command = runner.call_args.args[0]
        self.assertEqual(command[:4], ["circle", "services", "pay", RESOURCE])
        self.assertIn("-X", command)
        self.assertIn("GET", command)
        self.assertIn("--chain", command)
        self.assertIn("BASE", command)
        self.assertIn("--max-amount", command)
        self.assertIn("0.012", command)
        self.assertTrue(receipt.succeeded)
        self.assertEqual(receipt.committed_cost, Money("0.012"))

    def test_cli_payment_failure_before_commit_is_not_recorded_as_spend(self) -> None:
        from radhanite.circle import CircleCliPaymentClient, CirclePreAttemptError

        runner = Mock(
            return_value=__import__("subprocess").CompletedProcess(
                args=[], returncode=1, stdout="", stderr="invalid request"
            )
        )
        client = CircleCliPaymentClient(
            cli="circle", wallet_address="0xwallet", runner=runner
        )
        offer = CircleOffer(
            descriptor_id="circle:test",
            resource=RESOURCE,
            name="Simple Price",
            method="GET",
            network="eip155:8453",
            quoted_cost=Money("0.012"),
            source_reference=RESOURCE,
        )
        with self.assertRaises(CirclePreAttemptError):
            client.pay(offer, Money("0.012"))


if __name__ == "__main__":
    unittest.main()
