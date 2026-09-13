"""TASK-011 adapter tests. No network access occurs here."""

from __future__ import annotations

import json
import unittest
import urllib.error
from contextlib import contextmanager

from radhanite.acquisition import CapabilityDescriptor
from radhanite.capability import Candidate
from radhanite.capability_execution import ExecutionResult
from radhanite.graph import (
    GATEWAY_URL_TEMPLATE,
    GraphCapabilityCatalog,
    GraphCapabilityExecutor,
    GraphGatewayClient,
    GraphPreAttemptError,
    GraphQueryError,
    GraphQueryReceipt,
    GraphQuerySpec,
    catalog_from_query_specs,
)
from radhanite.money import Money
from radhanite.probability import Probability

SUBGRAPH = "5zvR82QoaXYFyDEKLZ9t6v9adgnptxYpKpSbxtgVENFV"
DOCUMENT = "{ _meta { block { number } } }"


def spec(**overrides) -> GraphQuerySpec:
    fields = {
        "descriptor_id": "graph-uniswap-v3-liquidity-001",
        "name": "Uniswap V3 onchain liquidity snapshot",
        "subgraph_id": SUBGRAPH,
        "document": DOCUMENT,
        "declared_cost": Money("0.40"),
        "fact_fields": ("factories.0.poolCount",),
    }
    fields.update(overrides)
    return GraphQuerySpec(**fields)


@contextmanager
def _response(body: str):
    class _Body:
        def read(self) -> bytes:
            return body.encode("utf-8")

    yield _Body()


def opener_returning(body: str, captured: list | None = None):
    def _open(request, timeout=None):
        if captured is not None:
            captured.append(request)
        return _response(body)

    return _open


def opener_raising(error: Exception):
    def _open(request, timeout=None):
        raise error

    return _open


class QuerySpecTests(unittest.TestCase):
    def test_endpoint_is_the_decentralized_gateway(self) -> None:
        self.assertEqual(
            spec().endpoint, GATEWAY_URL_TEMPLATE.format(subgraph_id=SUBGRAPH)
        )

    def test_descriptor_carries_only_the_task_008_fields(self) -> None:
        descriptor = spec().descriptor()
        self.assertIsInstance(descriptor, CapabilityDescriptor)
        self.assertEqual(descriptor.descriptor_id, "graph-uniswap-v3-liquidity-001")
        self.assertEqual(descriptor.cost, Money("0.40"))
        self.assertEqual(descriptor.source_reference, SUBGRAPH)

    def test_price_must_be_known_before_the_query(self) -> None:
        # TASK-011 §6.2 — a cost discovered after the call cannot be represented.
        with self.assertRaisesRegex(TypeError, "known before the query is sent"):
            spec(declared_cost="0.40")

    def test_free_capability_is_refused(self) -> None:
        with self.assertRaisesRegex(ValueError, "greater than zero"):
            spec(declared_cost=Money("0.00"))

    def test_empty_identity_fields_are_refused(self) -> None:
        for field in ("descriptor_id", "name", "subgraph_id", "document"):
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError, "cannot be empty"):
                    spec(**{field: "   "})


class CatalogTests(unittest.TestCase):
    def test_candidate_carries_no_provider_identity(self) -> None:
        # TASK-011 §3 — the whole boundary, asserted directly.
        catalog = catalog_from_query_specs(
            [spec()], expected_post_action_success_probability=Probability("0.17")
        )
        (candidate,) = catalog.candidates
        self.assertEqual(candidate.candidate_id, "graph-uniswap-v3-liquidity-001")
        self.assertEqual(candidate.cost, Money("0.40"))
        self.assertEqual(candidate.success_probability, Probability("0.17"))
        self.assertEqual(
            set(Candidate.__dataclass_fields__),
            {"candidate_id", "cost", "success_probability"},
        )
        rendered = repr(candidate)
        self.assertNotIn(SUBGRAPH, rendered)
        self.assertNotIn("thegraph", rendered)
        self.assertNotIn("subgraph", rendered)

    def test_spec_is_recoverable_after_selection(self) -> None:
        catalog = catalog_from_query_specs(
            [spec()], expected_post_action_success_probability=Probability("0.17")
        )
        self.assertEqual(
            catalog.spec_for("graph-uniswap-v3-liquidity-001").subgraph_id, SUBGRAPH
        )
        with self.assertRaises(KeyError):
            catalog.spec_for("absent")

    def test_empty_offer_is_refused(self) -> None:
        with self.assertRaisesRegex(GraphQueryError, "No Graph query specs"):
            catalog_from_query_specs(
                [], expected_post_action_success_probability=Probability("0.17")
            )

    def test_probability_must_be_declared_exactly(self) -> None:
        with self.assertRaisesRegex(TypeError, "exactly Probability"):
            catalog_from_query_specs(
                [spec()], expected_post_action_success_probability=0.17
            )


class GatewayClientTests(unittest.TestCase):
    def test_successful_query_commits_the_declared_cost(self) -> None:
        body = json.dumps({"data": {"factories": [{"poolCount": "24601"}]}})
        client = GraphGatewayClient(api_key="k", opener=opener_returning(body))
        receipt = client.query(spec(), Money("0.40"))
        self.assertTrue(receipt.succeeded)
        self.assertEqual(receipt.committed_cost, Money("0.40"))
        self.assertEqual(receipt.evidence["evidence_type"], "graph_onchain_evidence")
        self.assertEqual(receipt.evidence["source_reference"], SUBGRAPH)
        self.assertIn('factories.0.poolCount="24601"', receipt.evidence["facts"])

    def test_request_targets_the_gateway_with_bearer_auth(self) -> None:
        captured: list = []
        body = json.dumps({"data": {"ok": 1}})
        client = GraphGatewayClient(
            api_key="secret-key", opener=opener_returning(body, captured)
        )
        client.query(spec(fact_fields=()), Money("0.40"))
        (request,) = captured
        self.assertEqual(
            request.full_url, GATEWAY_URL_TEMPLATE.format(subgraph_id=SUBGRAPH)
        )
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.headers["Authorization"], "Bearer secret-key")
        self.assertEqual(json.loads(request.data.decode())["query"], DOCUMENT)

    def test_api_key_never_reaches_evidence(self) -> None:
        body = json.dumps({"data": {"ok": 1}})
        client = GraphGatewayClient(api_key="secret-key", opener=opener_returning(body))
        receipt = client.query(spec(fact_fields=()), Money("0.40"))
        self.assertNotIn(
            "secret-key", json.dumps(dict(receipt.evidence), default=str)
        )

    def test_graphql_errors_are_a_committed_failure(self) -> None:
        # The gateway served the query, so it was paid for. Reporting this as a
        # pre-attempt failure would understate real spend.
        body = json.dumps({"errors": [{"message": "auth error: API key not found"}]})
        client = GraphGatewayClient(api_key="k", opener=opener_returning(body))
        receipt = client.query(spec(), Money("0.40"))
        self.assertFalse(receipt.succeeded)
        self.assertEqual(receipt.committed_cost, Money("0.40"))
        self.assertIn("gateway returned GraphQL errors", receipt.evidence["facts"])

    def test_http_error_status_is_a_committed_failure(self) -> None:
        error = urllib.error.HTTPError(
            url="https://gateway.thegraph.com",
            code=402,
            msg="Payment Required",
            hdrs=None,
            fp=None,
        )
        client = GraphGatewayClient(api_key="k", opener=opener_raising(error))
        receipt = client.query(spec(), Money("0.40"))
        self.assertFalse(receipt.succeeded)
        self.assertEqual(receipt.committed_cost, Money("0.40"))
        self.assertIn("gateway returned HTTP 402", receipt.evidence["facts"])

    def test_unreachable_gateway_commits_nothing(self) -> None:
        client = GraphGatewayClient(
            api_key="k", opener=opener_raising(urllib.error.URLError("no route"))
        )
        with self.assertRaisesRegex(GraphPreAttemptError, "no query was served"):
            client.query(spec(), Money("0.40"))

    def test_missing_api_key_commits_nothing(self) -> None:
        client = GraphGatewayClient(
            api_key="", opener=opener_raising(AssertionError("sent!"))
        )
        with self.assertRaisesRegex(GraphPreAttemptError, "nothing was spent"):
            client.query(spec(), Money("0.40"))

    def test_cost_above_ceiling_is_refused_before_sending(self) -> None:
        client = GraphGatewayClient(
            api_key="k", opener=opener_raising(AssertionError("sent!"))
        )
        with self.assertRaisesRegex(GraphPreAttemptError, "no query was sent"):
            client.query(spec(), Money("0.10"))

    def test_non_json_body_is_a_committed_failure(self) -> None:
        client = GraphGatewayClient(
            api_key="k", opener=opener_returning("<html>502</html>")
        )
        receipt = client.query(spec(), Money("0.40"))
        self.assertFalse(receipt.succeeded)
        self.assertIn("gateway response was not JSON", receipt.evidence["facts"])

    def test_empty_data_is_a_committed_failure(self) -> None:
        client = GraphGatewayClient(
            api_key="k", opener=opener_returning(json.dumps({"data": {}}))
        )
        receipt = client.query(spec(), Money("0.40"))
        self.assertFalse(receipt.succeeded)
        self.assertIn("gateway returned no data", receipt.evidence["facts"])


class _StubClient:
    def __init__(self, receipt) -> None:
        self.receipt = receipt
        self.calls = 0

    def query(self, spec, maximum_authorized_cost):
        self.calls += 1
        return self.receipt


class ExecutorTests(unittest.TestCase):
    def _catalog(self) -> GraphCapabilityCatalog:
        return catalog_from_query_specs(
            [spec()], expected_post_action_success_probability=Probability("0.17")
        )

    def _executor(self, receipt) -> tuple[GraphCapabilityExecutor, _StubClient]:
        client = _StubClient(receipt)
        return (
            GraphCapabilityExecutor(catalog=self._catalog(), query_client=client),
            client,
        )

    def test_returns_a_provider_neutral_result(self) -> None:
        receipt = GraphQueryReceipt(
            succeeded=True,
            committed_cost=Money("0.40"),
            evidence={"capability_key": "graph-uniswap-v3-liquidity-001"},
        )
        executor, client = self._executor(receipt)
        (candidate,) = executor.catalog.candidates
        result = executor.execute(candidate, None, Money("0.40"))
        self.assertIsInstance(result, ExecutionResult)
        self.assertTrue(result.succeeded)
        self.assertEqual(result.committed_cost, Money("0.40"))
        self.assertEqual(client.calls, 1)

    def test_failed_query_still_reports_committed_cost(self) -> None:
        receipt = GraphQueryReceipt(
            succeeded=False, committed_cost=Money("0.40"), evidence={"k": "v"}
        )
        executor, _ = self._executor(receipt)
        (candidate,) = executor.catalog.candidates
        result = executor.execute(candidate, None, Money("0.40"))
        self.assertFalse(result.succeeded)
        self.assertEqual(result.committed_cost, Money("0.40"))

    def test_overspend_is_refused_rather_than_clamped(self) -> None:
        receipt = GraphQueryReceipt(
            succeeded=True, committed_cost=Money("0.90"), evidence={"k": "v"}
        )
        executor, _ = self._executor(receipt)
        (candidate,) = executor.catalog.candidates
        with self.assertRaisesRegex(ValueError, "no silent clamping"):
            executor.execute(candidate, None, Money("0.40"))

    def test_ceiling_above_declared_cost_is_refused(self) -> None:
        receipt = GraphQueryReceipt(
            succeeded=True, committed_cost=Money("0.40"), evidence={"k": "v"}
        )
        executor, _ = self._executor(receipt)
        (candidate,) = executor.catalog.candidates
        with self.assertRaisesRegex(ValueError, "authorization ceiling exceeds"):
            executor.execute(candidate, None, Money("0.90"))

    def test_unknown_candidate_is_refused(self) -> None:
        receipt = GraphQueryReceipt(
            succeeded=True, committed_cost=Money("0.40"), evidence={"k": "v"}
        )
        executor, _ = self._executor(receipt)
        stranger = Candidate(
            candidate_id="not-from-this-catalog",
            cost=Money("0.40"),
            success_probability=Probability("0.17"),
        )
        with self.assertRaises(KeyError):
            executor.execute(stranger, None, Money("0.40"))


if __name__ == "__main__":
    unittest.main()
