"""TASK-010 Circle discovery and Gateway/x402 execution adapter.

**Implementation agent: Manus.**

This module is the provider-specific edge of Radhanite. It reads Circle's public
Discovery API, converts one exact pre-purchase Gateway quote through TASK-008,
and retains Circle metadata only for the executor. TASK-006 sees only its three
Candidate fields. Payment is delegated to the official Circle CLI so the normal
Python package remains standard-library-only; the opt-in smoke command supplies
credentials through the environment and never runs during unit tests.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import urllib.parse
import urllib.request
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Protocol

from radhanite.acquisition import CapabilityCatalog, CapabilityDescriptor, normalize
from radhanite.capability import Candidate
from radhanite.capability_execution import ExecutionResult
from radhanite.money import Money
from radhanite.probability import Probability
from radhanite.revenue import make_evidence

__all__ = [
    "CircleCapabilityCatalog",
    "CircleCapabilityExecutor",
    "CircleCliPaymentClient",
    "CircleDiscoveryError",
    "CircleOffer",
    "CirclePaymentReceipt",
    "CirclePostAttemptError",
    "CirclePreAttemptError",
    "catalog_from_circle_response",
    "live_circle_discovery",
]

DISCOVERY_URL = "https://api.circle.com/v2/x402/discovery/resources"
_USDC_MICRO_UNITS = Decimal("1000000")
_DEFAULT_QUERY = {"ids": "bitcoin,ethereum", "vs_currencies": "usd"}


class CircleDiscoveryError(ValueError):
    """The live or captured Circle response cannot produce an exact candidate."""


class CirclePreAttemptError(RuntimeError):
    """The payment failed before a request or financial commitment began."""


class CirclePostAttemptError(RuntimeError):
    """The payment may have committed, but the provider did not return a receipt."""


@dataclass(frozen=True, slots=True)
class CircleOffer:
    """Provider-specific metadata retained outside TASK-006."""

    descriptor_id: str
    resource: str
    name: str
    method: str
    network: str
    quoted_cost: Money
    source_reference: str
    request_url: str | None = None

    @property
    def payable_url(self) -> str:
        return self.request_url or self.resource


@dataclass(frozen=True, slots=True)
class CirclePaymentReceipt:
    """Exact adapter receipt before conversion to provider-neutral ExecutionResult."""

    succeeded: bool
    committed_cost: Money
    evidence: Mapping[str, object]


@dataclass(frozen=True, slots=True)
class CircleCapabilityCatalog:
    """TASK-008 catalog plus the provider metadata required after selection."""

    catalog: CapabilityCatalog
    offers: tuple[CircleOffer, ...]

    @property
    def candidates(self) -> tuple[Candidate, ...]:
        return self.catalog.candidates

    @property
    def descriptors(self) -> tuple[CapabilityDescriptor, ...]:
        return self.catalog.descriptors

    def descriptor_for(self, candidate_id: str) -> CapabilityDescriptor:
        return self.catalog.descriptor_for(candidate_id)

    def offer_for(self, candidate_id: str) -> CircleOffer:
        for offer in self.offers:
            if offer.descriptor_id == candidate_id:
                return offer
        raise KeyError(f"No Circle offer retained for candidate {candidate_id!r}.")

    def __len__(self) -> int:
        return len(self.catalog)


class CirclePaymentClient(Protocol):
    def pay(self, offer: CircleOffer, maximum_authorized_cost: Money) -> CirclePaymentReceipt:
        """Pay one selected offer and report exact committed cost."""
        ...


class CircleCapabilityExecutor:
    """Adapt one selected TASK-006 candidate to a Circle payment client."""

    def __init__(self, *, catalog: CircleCapabilityCatalog, payment_client: CirclePaymentClient) -> None:
        self.catalog = catalog
        self.payment_client = payment_client

    def execute(
        self,
        selected_candidate: Candidate,
        current_state: Any,
        maximum_authorized_cost: Money,
    ) -> ExecutionResult:
        if type(selected_candidate) is not Candidate:
            raise TypeError("selected_candidate must be exactly Candidate.")
        if type(maximum_authorized_cost) is not Money:
            raise TypeError("maximum_authorized_cost must be exactly Money.")
        offer = self.catalog.offer_for(selected_candidate.candidate_id)
        if selected_candidate.cost != offer.quoted_cost:
            raise ValueError("candidate cost differs from Circle's pre-purchase quote.")
        if maximum_authorized_cost > offer.quoted_cost:
            raise ValueError("authorization ceiling exceeds Circle's quoted cost.")
        receipt = self.payment_client.pay(offer, maximum_authorized_cost)
        if type(receipt) is not CirclePaymentReceipt:
            raise TypeError("Circle payment client must return exactly CirclePaymentReceipt.")
        if receipt.committed_cost > maximum_authorized_cost:
            raise ValueError(
                f"Circle committed {receipt.committed_cost}, above authorization "
                f"ceiling {maximum_authorized_cost}; no silent clamping is permitted."
            )
        return ExecutionResult(
            succeeded=receipt.succeeded,
            committed_cost=receipt.committed_cost,
            evidence=receipt.evidence,
        )


class CircleCliPaymentClient:
    """Use the official Circle CLI for an explicit, opt-in x402 payment.

    The CLI owns wallet signing and Circle Gateway settlement. This adapter does
    not create a wallet, accept private keys, or silently retry. Exact x402
    pricing means a successful response commits the quoted amount. If a failed
    command says payment was submitted, the same exact quote is recorded as
    committed; otherwise the failure is treated as pre-attempt and no spend is
    fabricated.
    """

    def __init__(
        self,
        *,
        cli: str = "circle",
        wallet_address: str | None = None,
        chain: str | None = None,
        runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
        outcome_key: str = "positive_market_signal",
    ) -> None:
        self.cli = cli
        self.wallet_address = wallet_address or os.environ.get("CIRCLE_WALLET_ADDRESS")
        self.chain = chain or os.environ.get("CIRCLE_CHAIN", "BASE")
        self.runner = runner
        self.outcome_key = outcome_key

    def pay(self, offer: CircleOffer, maximum_authorized_cost: Money) -> CirclePaymentReceipt:
        if shutil.which(self.cli) is None and self.cli == "circle":
            raise CirclePreAttemptError(
                "Circle CLI is not installed. Install the official CLI and complete "
                "agent-wallet login before running the opt-in smoke command."
            )
        if not self.wallet_address:
            raise CirclePreAttemptError(
                "CIRCLE_WALLET_ADDRESS is required; no payment attempt was made."
            )
        if offer.method not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
            raise CirclePreAttemptError(f"Unsupported seller method {offer.method!r}.")
        command = [
            self.cli,
            "services",
            "pay",
            offer.payable_url,
            "-X",
            offer.method,
            "--address",
            self.wallet_address,
            "--chain",
            self.chain,
            "--max-amount",
            str(maximum_authorized_cost.amount),
            "--output",
            "json",
        ]
        completed = self.runner(command, capture_output=True, text=True, check=False)
        output = (completed.stdout or "").strip()
        error = (completed.stderr or "").strip()
        if completed.returncode != 0:
            combined = f"{output}\n{error}"
            if "PAYMENT WAS SUBMITTED" in combined.upper() or "paymentSubmitted" in combined:
                return CirclePaymentReceipt(
                    succeeded=False,
                    committed_cost=offer.quoted_cost,
                    evidence=self._evidence(offer, combined, "payment submitted but service failed"),
                )
            raise CirclePreAttemptError(
                "Circle CLI failed before payment commitment; no spend was recorded: "
                + (error or output or "unknown CLI error")
            )
        if not output:
            raise CirclePostAttemptError(
                "Circle CLI returned success without a response body or payment receipt."
            )
        return CirclePaymentReceipt(
            succeeded=True,
            committed_cost=offer.quoted_cost,
            evidence=self._evidence(offer, output, "Circle service response received"),
        )

    def _evidence(self, offer: CircleOffer, response: str, fact: str):
        safe_response = response.replace("\n", " ")[:240]
        return make_evidence(
            capability_key="circle-market-data",
            evidence_type="circle_x402_response",
            facts=(fact, safe_response),
            source_reference=offer.resource,
            outcome_key=self.outcome_key,
        )


def live_circle_discovery(
    *,
    opener: Callable[..., Any] | None = None,
    expected_post_action_success_probability: Probability,
    payment_client: Any | None = None,
    network: str = "eip155:8453",
    request_query: str | None = None,
) -> CircleCapabilityCatalog:
    """Fetch Circle's keyless live catalog without making a payment."""
    del payment_client  # discovery and payment are deliberately separate acts
    if opener is None:
        opener = urllib.request.urlopen
    query = request_query
    if query is None:
        query = urllib.parse.urlencode(_DEFAULT_QUERY)
    url = DISCOVERY_URL + ("?" + query if query else "")
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "radhanite-task-010/1.0",
        },
    )
    try:
        response = opener(request)
        payload = response if isinstance(response, Mapping) else json.loads(response.read())
    except Exception as exc:
        raise CircleDiscoveryError(f"Circle Discovery request failed: {exc}") from exc
    return catalog_from_circle_response(
        payload,
        expected_post_action_success_probability=expected_post_action_success_probability,
        network=network,
        request_query=query,
    )


def catalog_from_circle_response(
    payload: Mapping[str, Any],
    *,
    expected_post_action_success_probability: Probability,
    network: str = "eip155:8453",
    request_query: str | None = None,
) -> CircleCapabilityCatalog:
    """Convert only exact Circle Gateway offers into TASK-008 candidates."""
    if not isinstance(payload, Mapping):
        raise CircleDiscoveryError("Circle Discovery response must be an object.")
    if not isinstance(expected_post_action_success_probability, Probability):
        raise TypeError("expected_post_action_success_probability must be Probability.")
    items = payload.get("items")
    if not isinstance(items, Sequence) or isinstance(items, (str, bytes)):
        raise CircleDiscoveryError("Circle Discovery response has no ordered items.")

    pairs: list[tuple[CapabilityDescriptor, Probability]] = []
    offers: list[CircleOffer] = []
    seen: set[str] = set()
    for item in items:
        if not isinstance(item, Mapping):
            continue
        metadata = item.get("metadata")
        if not isinstance(metadata, Mapping) or metadata.get("supportsCircleGateway") is not True:
            continue
        resource = item.get("resource")
        method = metadata.get("method", "GET")
        if not isinstance(resource, str) or not resource.startswith(("http://", "https://")):
            continue
        if method not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
            continue
        term = _gateway_term(item.get("accepts"), network)
        if term is None:
            continue
        amount = term.get("amount")
        try:
            quoted_cost = Money(str(Decimal(str(amount)) / _USDC_MICRO_UNITS))
        except Exception:
            continue
        if not quoted_cost.is_positive:
            continue
        name = metadata.get("description") or (metadata.get("provider") or {}).get("name")
        if not isinstance(name, str) or not name.strip():
            continue
        request_url = resource
        if request_query:
            request_url += "?" + request_query
        descriptor_id = "circle:" + hashlib.sha256(
            f"{resource}|{request_url}|{network}|{amount}".encode("utf-8")
        ).hexdigest()[:24]
        if descriptor_id in seen:
            continue
        seen.add(descriptor_id)
        source_reference = resource
        descriptor = CapabilityDescriptor(
            descriptor_id=descriptor_id,
            name=name,
            cost=quoted_cost,
            source_reference=source_reference,
        )
        pairs.append((descriptor, expected_post_action_success_probability))
        offers.append(
            CircleOffer(
                descriptor_id=descriptor_id,
                resource=resource,
                name=name,
                method=method,
                network=network,
                quoted_cost=quoted_cost,
                source_reference=source_reference,
                request_url=request_url,
            )
        )

    if not pairs:
        raise CircleDiscoveryError(
            f"Circle returned no exact Circle Gateway offer on network {network!r}; "
            "unknown, vanilla-only, zero, and non-exact prices are excluded."
        )
    return CircleCapabilityCatalog(catalog=CapabilityCatalog(
        entries=[
            (normalize(descriptor, expected_post_action_success_probability=probability), descriptor)
            for descriptor, probability in pairs
        ]
    ), offers=tuple(offers))


def _gateway_term(accepts: Any, network: str) -> Mapping[str, Any] | None:
    if not isinstance(accepts, Sequence) or isinstance(accepts, (str, bytes)):
        return None
    for term in accepts:
        if not isinstance(term, Mapping):
            continue
        if term.get("scheme") != "exact" or term.get("network") != network:
            continue
        extra = term.get("extra")
        if isinstance(extra, Mapping) and extra.get("name") == "GatewayWalletBatched":
            return term
    return None
