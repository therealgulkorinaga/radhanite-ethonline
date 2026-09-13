"""Critical TASK-015 Arc Testnet wallet/x402 boundary tests.

**Implementation agent: Manus.**

External Circle SDK, wallet, HTTP, and seller calls are mocked. These tests
prove that Arc is explicit, selection precedes payment, exact amounts and
references are retained, ambiguous commitment fails closed, and TASK-009
feeds the next TASK-006 decision.
"""

from __future__ import annotations

import json
import subprocess
import unittest
from dataclasses import replace
from decimal import Decimal, localcontext
from unittest.mock import Mock

from radhanite.arc import (
    ARC_TESTNET_GATEWAY_WALLET,
    ARC_TESTNET_NETWORK,
    ARC_TESTNET_USDC,
    ArcPaymentError,
    ArcPaymentCommitmentUnresolvedError,
    CircleArcDeveloperWalletPaymentClient,
    _money_to_atomic,
    arc_setup_blockers,
    arc_demo_catalog,
)
from radhanite.capability_execution import ExecutionResult
from radhanite.circle import CircleCapabilityExecutor, CirclePaymentReceipt
from radhanite.loop import run_capability_loop
from radhanite.money import Money
from radhanite.probability import Probability
from radhanite.revenue import RevenueOpportunityUpdater, initialize_benchmark_run, make_evidence
from radhanite.runstate import RunStatus


RESOURCE = "https://arc-demo.example.test/api/premium/quote"
WALLET_ID = "wallet-id"
WALLET_ADDRESS = "0x1111111111111111111111111111111111111111"


def arc_offer_catalog(*, price: str = "0.001", probability: str = "0.14", resource: str = RESOURCE):
    return arc_demo_catalog(
        resource=resource,
        price=Money(price),
        expected_post_action_success_probability=Probability(probability),
    )


def receipt_json(
    *, amount="0.001", asset=ARC_TESTNET_USDC, status="gateway_accepted",
    reference="ref", response_status=200, service_result=None,
    service_outcome="positive_market_signal", commitment_status="committed",
    phase="complete",
    wallet_id=WALLET_ID, wallet_address=WALLET_ADDRESS,
):
    if service_result is None:
        service_result = (
            {"capability": "arc-demo-quote", "result": "Circle Arc Testnet x402 demo result", "outcome": service_outcome}
            if response_status in {200, 201, 202}
            else {"error": f"service failed with HTTP {response_status}"}
        )
    return json.dumps({
        "phase": phase,
        "status": status,
        "commitment_status": commitment_status,
        "settlement_status": "gateway_accepted",
        "network": ARC_TESTNET_NETWORK,
        "asset": asset,
        "amount": amount,
        "amount_atomic": str(int(Decimal(amount) * Decimal(10**6))),
        "wallet_id": wallet_id,
        "wallet_address": wallet_address,
        "payment_reference": reference,
        "response_status": response_status,
        "service_outcome": service_outcome,
        "service_result": service_result,
    })


class ArcTests(unittest.TestCase):
    def test_arc_atomic_conversion_is_context_independent_and_exact(self) -> None:
        with localcontext() as context:
            context.prec = 3
            self.assertEqual(_money_to_atomic(Money("123.456789")), "123456789")
            self.assertEqual(_money_to_atomic(Money("0.000001")), "1")
            self.assertEqual(_money_to_atomic(Money("0.012")), "12000")
            with self.assertRaises(ValueError):
                _money_to_atomic(Money("0.0000001"))

    def test_arc_setup_blockers_require_authorized_uppercase_configuration(self) -> None:
        blockers = arc_setup_blockers({})
        self.assertEqual(
            blockers,
            (
                "missing CIRCLE_API_KEY",
                "missing CIRCLE_ENTITY_SECRET",
                "missing CIRCLE_ARC_WALLET_ID",
                "missing CIRCLE_ARC_WALLET_ADDRESS",
                "missing RADHANITE_ARC_RESOURCE",
                "missing RADHANITE_ARC_PRICE",
            ),
        )

    def test_arc_constants_and_demo_offer_are_explicit(self) -> None:
        catalog = arc_offer_catalog()
        offer = catalog.offer_for(catalog.candidates[0].candidate_id)
        self.assertEqual(offer.network, ARC_TESTNET_NETWORK)
        self.assertEqual(offer.asset, ARC_TESTNET_USDC)
        self.assertEqual(offer.quoted_cost, Money("0.001"))
        self.assertEqual(offer.scheme, "exact")
        self.assertEqual(offer.extra_name, "GatewayWalletBatched")
        self.assertEqual(offer.extra_version, "1")
        self.assertEqual(offer.verifying_contract, ARC_TESTNET_GATEWAY_WALLET)
        self.assertIn("official Circle Arc", offer.source_reference)

    def test_base_offer_cannot_masquerade_as_arc(self) -> None:
        client = CircleArcDeveloperWalletPaymentClient(runner=Mock(), wallet_id=WALLET_ID, wallet_address=WALLET_ADDRESS, node="node")
        offer = replace(arc_offer_catalog().offers[0], network="eip155:8453")
        with self.assertRaises(ValueError):
            client.pay(offer, Money("0.001"))

    def test_wrong_network_is_rejected_before_signing(self) -> None:
        runner = Mock()
        client = CircleArcDeveloperWalletPaymentClient(runner=runner, wallet_id=WALLET_ID, wallet_address=WALLET_ADDRESS, node="node")
        with self.assertRaises(ValueError):
            client.pay(arc_offer_catalog().offers[0], Money("0.002"))
        runner.assert_not_called()

    def test_malformed_arc_asset_is_rejected_before_signing(self) -> None:
        runner = Mock()
        client = CircleArcDeveloperWalletPaymentClient(runner=runner, wallet_id=WALLET_ID, wallet_address=WALLET_ADDRESS, node="node")
        offer = replace(arc_offer_catalog().offers[0], asset="not-an-address")
        with self.assertRaises(ValueError):
            client.pay(offer, Money("0.001"))
        runner.assert_not_called()

    def test_wrong_arc_asset_is_rejected_before_signing(self) -> None:
        runner = Mock()
        client = CircleArcDeveloperWalletPaymentClient(runner=runner, wallet_id=WALLET_ID, wallet_address=WALLET_ADDRESS, node="node")
        offer = replace(arc_offer_catalog().offers[0], asset="0x" + "1" * 40)
        with self.assertRaises(ValueError):
            client.pay(offer, Money("0.001"))
        runner.assert_not_called()

    def test_arc_payment_preserves_exact_amount_and_reference(self) -> None:
        runner = Mock(return_value=subprocess.CompletedProcess(
            args=[], returncode=0, stdout=receipt_json(reference="0xarc-payment-reference"), stderr=""
        ))
        client = CircleArcDeveloperWalletPaymentClient(runner=runner, wallet_id=WALLET_ID, wallet_address=WALLET_ADDRESS, node="node")
        receipt = client.pay(arc_offer_catalog().offers[0], Money("0.001"))
        self.assertIsInstance(receipt, CirclePaymentReceipt)
        self.assertEqual(receipt.committed_cost, Money("0.001"))
        self.assertIn("payment_reference=0xarc-payment-reference", receipt.evidence["facts"])
        self.assertIn('service_result={"capability": "arc-demo-quote", "outcome": "positive_market_signal", "result": "Circle Arc Testnet x402 demo result"}', receipt.evidence["facts"])
        command = runner.call_args.args[0]
        self.assertIn(ARC_TESTNET_NETWORK, command)
        self.assertIn("0.001", command)
        self.assertIn("--wallet-address", command)
        self.assertIn("--wallet-id", command)
        self.assertIn("wallet-id", command)
        self.assertIn("0x1111111111111111111111111111111111111111", command)
        self.assertNotIn("--deposit", command)

    def test_nonzero_no_json_is_unresolved(self) -> None:
        runner = Mock(return_value=subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr="killed"))
        client = CircleArcDeveloperWalletPaymentClient(runner=runner, wallet_id=WALLET_ID, wallet_address=WALLET_ADDRESS)
        with self.assertRaises(ArcPaymentCommitmentUnresolvedError) as caught:
            client.pay(arc_offer_catalog().offers[0], Money("0.001"))
        self.assertNotIn("killed", str(caught.exception))
        self.assertEqual(runner.call_count, 1)

    def test_unresolved_helper_detail_is_bounded_and_preserved(self) -> None:
        detail = "seller returned diagnostic-safe failure"
        runner = Mock(return_value=subprocess.CompletedProcess(
            args=[], returncode=1,
            stdout=json.dumps({
                "phase": "post_submit",
                "status": "error",
                "signing_started": True,
                "payment_submitted": True,
                "commitment_status": "unresolved",
                "error": detail,
            }),
            stderr="",
        ))
        client = CircleArcDeveloperWalletPaymentClient(
            runner=runner, wallet_id=WALLET_ID, wallet_address=WALLET_ADDRESS
        )
        with self.assertRaises(ArcPaymentCommitmentUnresolvedError) as caught:
            client.pay(arc_offer_catalog().offers[0], Money("0.001"))
        self.assertIn(detail, str(caught.exception))
        self.assertIs(type(caught.exception), ArcPaymentCommitmentUnresolvedError)
        self.assertEqual(runner.call_count, 1)

    def test_unresolved_diagnostic_redacts_circle_credentials(self) -> None:
        api_key = "api-key-diagnostic-secret"
        entity_secret = "entity-secret-diagnostic-secret"
        runner = Mock(return_value=subprocess.CompletedProcess(
            args=[], returncode=1,
            stdout=json.dumps({
                "phase": "post_submit",
                "status": "error",
                "signing_started": True,
                "payment_submitted": True,
                "commitment_status": "unresolved",
                "error": f"provider diagnostic {api_key} / {entity_secret}",
            }),
            stderr="",
        ))
        client = CircleArcDeveloperWalletPaymentClient(
            runner=runner,
            wallet_id=WALLET_ID,
            wallet_address=WALLET_ADDRESS,
            environment={
                "CIRCLE_API_KEY": api_key,
                "CIRCLE_ENTITY_SECRET": entity_secret,
            },
        )
        with self.assertRaises(ArcPaymentCommitmentUnresolvedError) as caught:
            client.pay(arc_offer_catalog().offers[0], Money("0.001"))
        message = str(caught.exception)
        self.assertNotIn(api_key, message)
        self.assertNotIn(entity_secret, message)
        self.assertIn("[REDACTED]", message)
        self.assertEqual(runner.call_count, 1)

    def test_malformed_json_is_unresolved(self) -> None:
        runner = Mock(return_value=subprocess.CompletedProcess(args=[], returncode=1, stdout="not-json", stderr=""))
        client = CircleArcDeveloperWalletPaymentClient(runner=runner, wallet_id=WALLET_ID, wallet_address=WALLET_ADDRESS)
        with self.assertRaises(ArcPaymentCommitmentUnresolvedError):
            client.pay(arc_offer_catalog().offers[0], Money("0.001"))

    def test_helper_process_exception_is_unresolved(self) -> None:
        runner = Mock(side_effect=subprocess.TimeoutExpired(cmd="node", timeout=1))
        client = CircleArcDeveloperWalletPaymentClient(runner=runner, wallet_id=WALLET_ID, wallet_address=WALLET_ADDRESS)
        with self.assertRaises(ArcPaymentCommitmentUnresolvedError):
            client.pay(arc_offer_catalog().offers[0], Money("0.001"))

    def test_structured_pre_sign_validation_failure_is_pre_attempt(self) -> None:
        runner = Mock(return_value=subprocess.CompletedProcess(
            args=[], returncode=1,
            stdout=json.dumps({
                "phase": "pre_sign", "status": "error",
                "signing_started": False, "payment_submitted": False,
                "commitment_status": "not_committed", "error": "wrong Arc asset",
            }), stderr="",
        ))
        client = CircleArcDeveloperWalletPaymentClient(runner=runner, wallet_id=WALLET_ID, wallet_address=WALLET_ADDRESS)
        with self.assertRaises(ArcPaymentError) as caught:
            client.pay(arc_offer_catalog().offers[0], Money("0.001"))
        self.assertNotIsInstance(caught.exception, ArcPaymentCommitmentUnresolvedError)

    def test_incomplete_or_contradictory_pre_sign_envelope_is_unresolved(self) -> None:
        base = {
            "phase": "pre_sign", "status": "error",
            "signing_started": False, "payment_submitted": False,
            "commitment_status": "not_committed", "error": "setup failure",
        }
        for mutation in (
            {"commitment_status": "unresolved"},
            {"commitment_status": None},
            {"payment_submitted": True},
            {"signing_started": True},
            {"phase": "unexpected"},
            {"status": "not_error"},
        ):
            payload = {**base, **mutation}
            runner = Mock(return_value=subprocess.CompletedProcess(
                args=[], returncode=1, stdout=json.dumps(payload), stderr="",
            ))
            client = CircleArcDeveloperWalletPaymentClient(
                runner=runner, wallet_id=WALLET_ID, wallet_address=WALLET_ADDRESS
            )
            with self.assertRaises(ArcPaymentCommitmentUnresolvedError):
                client.pay(arc_offer_catalog().offers[0], Money("0.001"))

    def test_success_with_unresolved_commitment_is_rejected(self) -> None:
        runner = Mock(return_value=subprocess.CompletedProcess(
            args=[], returncode=0,
            stdout=receipt_json(commitment_status="unresolved"), stderr="",
        ))
        client = CircleArcDeveloperWalletPaymentClient(runner=runner, wallet_id=WALLET_ID, wallet_address=WALLET_ADDRESS)
        with self.assertRaises(ArcPaymentCommitmentUnresolvedError):
            client.pay(arc_offer_catalog().offers[0], Money("0.001"))

    def test_wrong_amount_and_wallet_are_unresolved_after_commit(self) -> None:
        for payload in (
            receipt_json(amount="0.002"),
            receipt_json(wallet_address="0x2222222222222222222222222222222222222222"),
        ):
            runner = Mock(return_value=subprocess.CompletedProcess(args=[], returncode=0, stdout=payload, stderr=""))
            client = CircleArcDeveloperWalletPaymentClient(runner=runner, wallet_id=WALLET_ID, wallet_address=WALLET_ADDRESS)
            with self.assertRaises(ArcPaymentCommitmentUnresolvedError):
                client.pay(arc_offer_catalog().offers[0], Money("0.001"))

    def test_committed_failure_service_500_and_404_retain_exact_commitment(self) -> None:
        for response_status in (500, 404):
            runner = Mock(return_value=subprocess.CompletedProcess(
                args=[], returncode=1,
                stdout=receipt_json(
                    phase="post_submit", status="error", response_status=response_status,
                    service_outcome="service_failure",
                ), stderr="",
            ))
            receipt = CircleArcDeveloperWalletPaymentClient(
                runner=runner, wallet_id=WALLET_ID, wallet_address=WALLET_ADDRESS
            ).pay(arc_offer_catalog().offers[0], Money("0.001"))
            self.assertFalse(receipt.succeeded)
            self.assertEqual(receipt.committed_cost, Money("0.001"))
            self.assertIn(f"service_status={response_status}", receipt.evidence["facts"])
            self.assertIn(f' service_result={{"error": "service failed with HTTP {response_status}"}}'.strip(), receipt.evidence["facts"])

    def test_committed_failure_malformed_or_unexpected_service_body_retains_reference(self) -> None:
        for service_result in (
            {"error": "Arc seller returned non-JSON service result"},
            {"error": "Arc seller returned an unrecognized demo service result"},
        ):
            runner = Mock(return_value=subprocess.CompletedProcess(
                args=[], returncode=1,
                stdout=receipt_json(
                    phase="post_submit", status="error", response_status=200,
                    service_outcome="service_failure", service_result=service_result,
                ), stderr="",
            ))
            receipt = CircleArcDeveloperWalletPaymentClient(
                runner=runner, wallet_id=WALLET_ID, wallet_address=WALLET_ADDRESS
            ).pay(arc_offer_catalog().offers[0], Money("0.001"))
            self.assertFalse(receipt.succeeded)
            self.assertEqual(receipt.committed_cost, Money("0.001"))
            self.assertIn("payment_reference=ref", receipt.evidence["facts"])

    def test_missing_settlement_reference_remains_unresolved(self) -> None:
        runner = Mock(return_value=subprocess.CompletedProcess(
            args=[], returncode=1,
            stdout=receipt_json(
                phase="post_submit", status="error", response_status=500,
                service_outcome="service_failure", reference="",
            ), stderr="",
        ))
        client = CircleArcDeveloperWalletPaymentClient(
            runner=runner, wallet_id=WALLET_ID, wallet_address=WALLET_ADDRESS
        )
        with self.assertRaises(ArcPaymentCommitmentUnresolvedError):
            client.pay(arc_offer_catalog().offers[0], Money("0.001"))

    def test_neutral_service_result_does_not_emit_positive_outcome(self) -> None:
        payload = receipt_json(
            service_outcome="neutral",
            service_result={"capability": "arc-demo-quote", "result": "Circle Arc Testnet x402 demo result", "outcome": "neutral"},
        )
        runner = Mock(return_value=subprocess.CompletedProcess(args=[], returncode=0, stdout=payload, stderr=""))
        receipt = CircleArcDeveloperWalletPaymentClient(
            runner=runner, wallet_id=WALLET_ID, wallet_address=WALLET_ADDRESS
        ).pay(arc_offer_catalog().offers[0], Money("0.001"))
        self.assertFalse(receipt.succeeded)
        self.assertIn("service_outcome=neutral", receipt.evidence["facts"])
        self.assertIn('service_result={"capability": "arc-demo-quote", "outcome": "neutral", "result": "Circle Arc Testnet x402 demo result"}', receipt.evidence["facts"])

    def test_malformed_service_result_is_unresolved(self) -> None:
        payload = receipt_json(service_result={"unexpected": True})
        runner = Mock(return_value=subprocess.CompletedProcess(args=[], returncode=0, stdout=payload, stderr=""))
        client = CircleArcDeveloperWalletPaymentClient(runner=runner, wallet_id=WALLET_ID, wallet_address=WALLET_ADDRESS)
        with self.assertRaises(ArcPaymentCommitmentUnresolvedError):
            client.pay(arc_offer_catalog().offers[0], Money("0.001"))

    def test_non_selected_arc_capability_is_never_paid(self) -> None:
        first = arc_offer_catalog(price="0.001")
        second = arc_offer_catalog(price="0.002", resource=RESOURCE + "/other")
        candidates = first.candidates + second.candidates
        catalog = type(first)(
            catalog=type(first.catalog)(entries=(
                (candidates[0], first.descriptor_for(candidates[0].candidate_id)),
                (candidates[1], second.descriptor_for(candidates[1].candidate_id)),
            )),
            offers=first.offers + second.offers,
        )
        runner = Mock(return_value=subprocess.CompletedProcess(args=[], returncode=0, stdout=receipt_json(amount="0.001"), stderr=""))
        result = run_capability_loop(
            state=initialize_benchmark_run(),
            candidate_source=type("Source", (), {"get_candidates": lambda self, task_state, run_state: candidates})(),
            executor=CircleCapabilityExecutor(catalog=catalog, payment_client=CircleArcDeveloperWalletPaymentClient(runner=runner, wallet_id=WALLET_ID, wallet_address=WALLET_ADDRESS, node="node")),
            updater=RevenueOpportunityUpdater(),
        )
        self.assertEqual(runner.call_count, 1)
        self.assertEqual(result.history[0].execution.committed_cost, Money("0.001"))

    def test_ambiguous_arc_commitment_fails_closed_without_retry(self) -> None:
        runner = Mock(return_value=subprocess.CompletedProcess(
            args=[], returncode=1,
            stdout=json.dumps({"error": "seller response unavailable", "commitment_status": "unresolved"}),
            stderr="",
        ))
        client = CircleArcDeveloperWalletPaymentClient(runner=runner, wallet_id=WALLET_ID, wallet_address=WALLET_ADDRESS, node="node")
        with self.assertRaises(ArcPaymentCommitmentUnresolvedError):
            client.pay(arc_offer_catalog().offers[0], Money("0.001"))
        self.assertEqual(runner.call_count, 1)

    def test_arc_execution_evidence_reaches_task009(self) -> None:
        runner = Mock(return_value=subprocess.CompletedProcess(args=[], returncode=0, stdout=receipt_json(reference="arc-ref"), stderr=""))
        catalog = arc_offer_catalog()
        result = run_capability_loop(
            state=initialize_benchmark_run(),
            candidate_source=type("Source", (), {"get_candidates": lambda self, task_state, run_state: catalog.candidates})(),
            executor=CircleCapabilityExecutor(catalog=catalog, payment_client=CircleArcDeveloperWalletPaymentClient(runner=runner, wallet_id=WALLET_ID, wallet_address=WALLET_ADDRESS, node="node")),
            updater=RevenueOpportunityUpdater(),
        )
        self.assertEqual(result.status, RunStatus.ECONOMIC_STOP)
        self.assertEqual(result.total_spend, Money("0.001"))
        facts = result.history[0].execution.evidence["facts"]
        self.assertIn("payment_reference=arc-ref", facts)
        self.assertIn(f"network={ARC_TESTNET_NETWORK}", facts)
        self.assertIsInstance(result.history[0].execution, ExecutionResult)

    def test_task009_update_is_visible_to_next_task006_decision(self) -> None:
        first = arc_offer_catalog(probability="0.14", resource=RESOURCE + "/market")
        second = arc_offer_catalog(probability="0.17", resource=RESOURCE + "/fit")
        candidates = first.candidates + second.candidates
        catalog = type(first)(
            catalog=type(first.catalog)(entries=(
                (candidates[0], first.descriptor_for(candidates[0].candidate_id)),
                (candidates[1], second.descriptor_for(candidates[1].candidate_id)),
            )),
            offers=first.offers + second.offers,
        )
        class Source:
            calls = 0

            def get_candidates(self, task_state, run_state):
                self.calls += 1
                return (candidates[self.calls - 1],)

        source = Source()

        class PaymentClient:
            calls = 0

            def pay(self, offer, maximum_authorized_cost):
                self.calls += 1
                outcome = "positive_market_signal" if self.calls == 1 else "positive_commercial_fit"
                reference = "market-ref" if self.calls == 1 else "fit-ref"
                return CirclePaymentReceipt(
                    succeeded=True,
                    committed_cost=maximum_authorized_cost,
                    evidence=make_evidence(
                        capability_key="arc-demo-x402",
                        evidence_type="arc_x402_payment",
                        facts=(f"payment_reference={reference}",),
                        source_reference=offer.source_reference,
                        outcome_key=outcome,
                    ),
                )

        result = run_capability_loop(
            state=initialize_benchmark_run(),
            candidate_source=source,
            executor=CircleCapabilityExecutor(catalog=catalog, payment_client=PaymentClient()),
            updater=RevenueOpportunityUpdater(),
        )
        self.assertEqual(result.history[0].execution.committed_cost, Money("0.001"))
        self.assertEqual(result.history[1].selection.current_success_probability, Probability("0.14"))
        self.assertEqual(result.current_success_probability, Probability("0.17"))
        self.assertEqual(result.status, RunStatus.TASK_COMPLETE)


if __name__ == "__main__":
    unittest.main()
