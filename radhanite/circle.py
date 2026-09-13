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
import re
import shutil
import subprocess
import urllib.parse
import urllib.request
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
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
    "CirclePaymentCommitmentUnresolvedError",
    "CirclePaymentMetadataError",
    "CirclePostAttemptError",
    "CirclePreAttemptError",
    "catalog_from_circle_response",
    "live_circle_discovery",
]

DISCOVERY_URL = "https://api.circle.com/v2/x402/discovery/resources"
_USDC_DECIMAL_PLACES = 6
_SUPPORTED_USDC_ASSETS = {
    "eip155:8453": "0x833589fcd6edb6e08f4c7c32d4f71b54bdA02913",
}
_NETWORK_TO_CLI_CHAIN = {
    "eip155:8453": "BASE",
}
_ATOMIC_AMOUNT_RE = re.compile(r"^[0-9]+$")
_DEFAULT_QUERY = {"ids": "bitcoin,ethereum", "vs_currencies": "usd"}


class CircleDiscoveryError(ValueError):
    """The live or captured Circle response cannot produce an exact candidate."""


class CirclePreAttemptError(RuntimeError):
    """The payment failed before a request or financial commitment began."""


class CirclePostAttemptError(RuntimeError):
    """The payment may have committed, but the provider did not return a receipt."""


class CirclePaymentCommitmentUnresolvedError(CirclePostAttemptError):
    """The provider may have charged, but no exact committed amount is known."""


class CirclePaymentMetadataError(ValueError):
    """The authoritative Circle payment metadata is missing or inconsistent."""


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
    asset: str = _SUPPORTED_USDC_ASSETS["eip155:8453"]
    scheme: str = "GatewayWalletBatched"
    atomic_amount: str = "12000"

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
    not create a wallet, accept private keys, or silently retry. The official
    JSON envelope is the only payment-accounting source of truth: successful and
    definitely submitted responses must expose matching amount, network, chain,
    scheme, and asset metadata. A possibly submitted response without an exact
    amount fails closed because TASK-007 cannot record an unknown spend.
    """

    def __init__(
        self,
        *,
        cli: str = "circle",
        wallet_address: str | None = None,
        chain: str | None = None,
        allow_mainnet: bool | None = None,
        runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
        outcome_key: str = "positive_market_signal",
    ) -> None:
        self.cli = cli
        self.wallet_address = wallet_address or os.environ.get("CIRCLE_WALLET_ADDRESS")
        self.chain_override = chain if chain is not None else os.environ.get("CIRCLE_CHAIN")
        self.allow_mainnet = (
            allow_mainnet
            if allow_mainnet is not None
            else os.environ.get("CIRCLE_SMOKE_ALLOW_MAINNET") == "1"
        )
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
        expected_chain = _cli_chain_for_network(offer.network)
        payment_chain = self.chain_override or expected_chain
        if payment_chain != expected_chain:
            raise CirclePaymentMetadataError(
                f"Circle offer network {offer.network!r} requires CLI chain "
                f"{expected_chain!r}; received {payment_chain!r}."
            )
        if payment_chain == "BASE" and not self.allow_mainnet:
            raise CirclePreAttemptError(
                "Refusing a Base-mainnet payment without explicit mainnet consent; "
                "set CIRCLE_SMOKE_ALLOW_MAINNET=1."
            )
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
            payment_chain,
            "--max-amount",
            str(maximum_authorized_cost.amount),
            "--output",
            "json",
        ]
        completed = self.runner(command, capture_output=True, text=True, check=False)
        output = (completed.stdout or "").strip()
        error = (completed.stderr or "").strip()
        if completed.returncode != 0:
            payload = _parse_json_envelope(output)
            if payload is not None and payload.get("paymentSubmitted") is True:
                metadata = _payment_metadata(payload)
                if metadata is None or "amount" not in metadata:
                    raise CirclePaymentCommitmentUnresolvedError(
                        "payment may have been submitted; exact commitment unresolved; "
                        "inspect Circle payment records"
                    )
                committed_cost = _validate_payment_metadata(offer, metadata)
                return CirclePaymentReceipt(
                    succeeded=False,
                    committed_cost=committed_cost,
                    evidence=self._evidence(
                        offer, output, "payment submitted but service failed"
                    ),
                )
            raise CirclePreAttemptError(
                "Circle CLI failed before payment commitment; no spend was recorded: "
                + (error or output or "unknown CLI error")
            )
        if not output:
            raise CirclePostAttemptError(
                "Circle CLI returned success without a response body or payment receipt."
            )
        payload = _parse_json_envelope(output)
        if payload is None:
            raise CirclePaymentMetadataError(
                "Circle CLI success output was not a JSON payment envelope."
            )
        metadata = _payment_metadata(payload)
        if metadata is None:
            raise CirclePaymentMetadataError(
                "Circle CLI success JSON did not contain authoritative payment metadata."
            )
        committed_cost = _validate_payment_metadata(offer, metadata)
        return CirclePaymentReceipt(
            succeeded=True,
            committed_cost=committed_cost,
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


def _parse_json_envelope(response: str) -> Mapping[str, Any] | None:
    try:
        payload = json.loads(response)
    except (TypeError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, Mapping) else None


def _payment_metadata(payload: Mapping[str, Any]) -> Mapping[str, Any] | None:
    for key in ("payment", "paymentMetadata", "paymentDetails", "receipt"):
        value = payload.get(key)
        if isinstance(value, Mapping):
            return value
    if any(key in payload for key in ("amount", "network", "chain", "scheme", "asset")):
        return payload
    return None


def _cli_chain_for_network(network: str) -> str:
    try:
        return _NETWORK_TO_CLI_CHAIN[network]
    except KeyError as exc:
        raise CirclePaymentMetadataError(
            f"Circle offer network {network!r} has no supported CLI chain mapping."
        ) from exc


def _atomic_amount_to_money(value: object) -> Money:
    if type(value) is not str:
        raise TypeError("Circle atomic amount must be an exact decimal digit string.")
    if not _ATOMIC_AMOUNT_RE.fullmatch(value):
        raise ValueError("Circle atomic amount must contain decimal digits only.")
    units = int(value)
    if units <= 0:
        raise ValueError("Circle atomic amount must be positive.")
    whole, fractional = divmod(units, 10**_USDC_DECIMAL_PLACES)
    return Money(f"{whole}.{fractional:0{_USDC_DECIMAL_PLACES}d}")


def _validate_payment_metadata(
    offer: CircleOffer, metadata: Mapping[str, Any]
) -> Money:
    amount = metadata.get("amount")
    committed_cost = _atomic_amount_to_money(amount)
    expected_cost = _atomic_amount_to_money(offer.atomic_amount)
    expected_asset = offer.asset
    expected_chain = _cli_chain_for_network(offer.network)
    checks = (
        (metadata.get("network"), offer.network, "network"),
        (metadata.get("chain"), expected_chain, "chain"),
        (metadata.get("scheme"), offer.scheme, "scheme"),
        (metadata.get("asset"), expected_asset, "asset"),
    )
    for actual, expected, label in checks:
        if actual != expected:
            raise CirclePaymentMetadataError(
                f"Circle payment {label} mismatch: expected {expected!r}, got {actual!r}."
            )
    if committed_cost != expected_cost:
        raise CirclePaymentMetadataError(
            f"Circle payment amount mismatch: expected {offer.atomic_amount!r} "
            f"atomic units, got {amount!r}."
        )
    return committed_cost


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
    if network not in _SUPPORTED_USDC_ASSETS:
        raise CircleDiscoveryError(
            f"Circle Discovery network {network!r} has no supported USDC asset mapping."
        )
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
            quoted_cost = _atomic_amount_to_money(amount)
        except (TypeError, ValueError) as exc:
            raise CircleDiscoveryError(
                f"Circle Gateway offer has invalid atomic amount {amount!r}."
            ) from exc
        expected_asset = _SUPPORTED_USDC_ASSETS[network]
        if term.get("asset") != expected_asset:
            raise CircleDiscoveryError(
                f"Circle Gateway offer does not use supported USDC asset for {network!r}."
            )
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
                asset=expected_asset,
                scheme=str(term["scheme"]),
                atomic_amount=amount,
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
