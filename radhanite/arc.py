"""TASK-015 Arc Testnet payment boundary.

**Implementation agent: Manus.**

This module keeps Circle's Arc-specific wallet and x402 concerns outside the
TASK-006 economic kernel. Discovery currently supplies marketplace evidence on
other networks; the Arc capability below is an explicitly identified demo
seller derived from Circle's official Arc nanopayments sample.

The Python package remains dependency-free. The opt-in payment client invokes
``scripts/arc_x402_pay.mjs`` which uses Circle's official Developer-Controlled
Wallet SDK and x402 batching SDK. Circle credentials are read only by that
helper from the process environment.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from radhanite.acquisition import CapabilityCatalog, CapabilityDescriptor, normalize
from radhanite.circle import (
    CircleCapabilityCatalog,
    CircleOffer,
    CirclePaymentReceipt,
)
from radhanite.money import Money
from radhanite.probability import Probability
from radhanite.revenue import make_evidence

__all__ = [
    "ARC_TESTNET_NETWORK",
    "ARC_TESTNET_CHAIN_ID",
    "ARC_TESTNET_WALLET_CHAIN",
    "ARC_TESTNET_USDC",
    "ARC_TESTNET_GATEWAY_WALLET",
    "ARC_TESTNET_GATEWAY_DOMAIN",
    "ARC_X402_VERSION",
    "ARC_X402_SCHEME",
    "ARC_X402_BATCHING_NAME",
    "ARC_X402_BATCHING_VERSION",
    "CircleArcDeveloperWalletPaymentClient",
    "ArcPaymentError",
    "ArcPaymentCommitmentUnresolvedError",
    "ARC_REQUIRED_ENVIRONMENT",
    "arc_setup_blockers",
    "arc_demo_catalog",
]

ARC_TESTNET_NETWORK = "eip155:5042002"
ARC_TESTNET_CHAIN_ID = 5_042_002
ARC_TESTNET_WALLET_CHAIN = "ARC-TESTNET"
ARC_TESTNET_USDC = "0x3600000000000000000000000000000000000000"
ARC_TESTNET_GATEWAY_WALLET = "0x0077777d7EBA4688BDeF3E311b846F25870A19B9"
ARC_TESTNET_GATEWAY_DOMAIN = 26
ARC_X402_VERSION = 2
ARC_X402_SCHEME = "exact"
ARC_X402_BATCHING_NAME = "GatewayWalletBatched"
ARC_X402_BATCHING_VERSION = "1"
ARC_DEMO_SOURCE_REFERENCE = (
    "official Circle Arc nanopayments sample / separate demo seller"
)
ARC_REQUIRED_ENVIRONMENT = (
    "CIRCLE_API_KEY",
    "CIRCLE_ENTITY_SECRET",
    "CIRCLE_ARC_WALLET_ID",
    "CIRCLE_ARC_WALLET_ADDRESS",
    "RADHANITE_ARC_RESOURCE",
    "RADHANITE_ARC_PRICE",
)


class ArcPaymentError(RuntimeError):
    """The Arc x402 helper failed before a trustworthy receipt was returned."""


@dataclass(frozen=True, slots=True)
class CircleArcDeveloperWalletPaymentClient:
    """Call the official Circle SDK-backed Arc x402 helper.

    The helper signs the x402 authorization with a Circle EOA Developer-
    Controlled Wallet. The Radhanite executor supplies the selected offer and
    authorization ceiling; this client never ranks candidates or changes the
    budget decision.
    """

    node: str = "node"
    helper: str = "scripts/arc_x402_pay.mjs"
    wallet_id: str | None = None
    wallet_address: str | None = None
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run
    environment: Mapping[str, str] | None = None

    def pay(self, offer: CircleOffer, maximum_authorized_cost: Money) -> CirclePaymentReceipt:
        if offer.network != ARC_TESTNET_NETWORK:
            raise ValueError(
                f"Arc wallet client accepts only {ARC_TESTNET_NETWORK!r}; "
                f"received {offer.network!r}."
            )
        if _normalize_evm_address(offer.asset, "Arc offer asset") != ARC_TESTNET_USDC.lower():
            raise ValueError("Arc offer must use the Arc Testnet USDC asset.")
        if offer.scheme != ARC_X402_SCHEME:
            raise ValueError("Arc offer must use the x402 exact scheme.")
        if offer.extra_name != ARC_X402_BATCHING_NAME:
            raise ValueError("Arc offer must use GatewayWalletBatched x402 metadata.")
        if offer.extra_version != ARC_X402_BATCHING_VERSION:
            raise ValueError("Arc offer must use GatewayWalletBatched version 1.")
        if _normalize_evm_address(
            offer.verifying_contract, "Arc offer verifying contract"
        ) != ARC_TESTNET_GATEWAY_WALLET.lower():
            raise ValueError("Arc offer must verify against the Arc GatewayWallet contract.")
        if maximum_authorized_cost != offer.quoted_cost:
            raise ValueError(
                "Arc payment authorization must equal the selected pre-purchase quote."
            )
        if not offer.payable_url.startswith(("http://", "https://")):
            raise ValueError("Arc x402 seller URL must be an HTTP(S) URL.")

        wallet_id = self.wallet_id or _environment_value(self.environment, "CIRCLE_ARC_WALLET_ID")
        wallet_address = self.wallet_address or _environment_value(
            self.environment, "CIRCLE_ARC_WALLET_ADDRESS"
        )
        if not wallet_id or not wallet_address:
            raise ArcPaymentError(
                "Arc wallet readiness requires CIRCLE_ARC_WALLET_ID and "
                "CIRCLE_ARC_WALLET_ADDRESS."
            )

        command = [
            self.node,
            self.helper,
            "--url",
            offer.payable_url,
            "--method",
            offer.method,
            "--amount",
            str(maximum_authorized_cost.amount),
            "--network",
            ARC_TESTNET_NETWORK,
            "--asset",
            ARC_TESTNET_USDC,
            "--gateway-wallet",
            ARC_TESTNET_GATEWAY_WALLET,
            "--wallet-id",
            wallet_id,
            "--wallet-address",
            wallet_address,
        ]
        completed = self.runner(
            command,
            capture_output=True,
            text=True,
            check=False,
            env=dict(self.environment) if self.environment is not None else None,
        )
        payload = _parse_result(completed.stdout)
        if completed.returncode != 0:
            detail = _safe_error(payload, completed.stderr, completed.stdout)
            if payload and payload.get("commitment_status") == "unresolved":
                raise ArcPaymentCommitmentUnresolvedError(
                    "Arc payment may have been submitted; exact commitment is unresolved."
                )
            raise ArcPaymentError(f"Arc x402 payment failed: {detail}")
        if payload is None:
            raise ArcPaymentError("Arc x402 helper returned no JSON result.")
        _validate_result(payload, offer, maximum_authorized_cost)
        payment_reference = payload.get("payment_reference")
        if not isinstance(payment_reference, str) or not payment_reference.strip():
            raise ArcPaymentError("Arc x402 result omitted a payment reference.")
        committed_cost = Money(str(payload["amount"]))
        evidence = make_evidence(
            capability_key="arc-demo-x402",
            evidence_type="arc_x402_payment",
            facts=(
                "Arc Testnet x402 payment accepted by the identified seller",
                f"payment_reference={payment_reference}",
                f"wallet_address={payload.get('wallet_address', 'unknown')}",
                f"network={ARC_TESTNET_NETWORK}",
                f"asset={ARC_TESTNET_USDC}",
                f"settlement_status={payload.get('settlement_status')}",
                "reference_semantics=Gateway acceptance; on-chain finality not asserted",
            ),
            source_reference=offer.source_reference,
            outcome_key="positive_market_signal",
        )
        return CirclePaymentReceipt(
            succeeded=True,
            committed_cost=committed_cost,
            evidence=evidence,
        )


class ArcPaymentCommitmentUnresolvedError(ArcPaymentError):
    """A signed/submitted payment may have committed without exact evidence."""


def arc_demo_catalog(
    *,
    resource: str,
    price: Money,
    expected_post_action_success_probability: Probability,
    method: str = "GET",
    name: str = "Circle official Arc nanopayments demo seller",
) -> CircleCapabilityCatalog:
    """Create one exact-price Arc offer from the separately identified demo seller."""
    if not isinstance(resource, str) or not resource.startswith(("http://", "https://")):
        raise ValueError("resource must be an HTTP(S) URL.")
    if not isinstance(price, Money) or not price.is_positive:
        raise ValueError("price must be a positive Money amount known before purchase.")
    if method not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
        raise ValueError(f"unsupported HTTP method {method!r}")
    atomic = _money_to_atomic(price)
    descriptor_id = "arc-demo:" + resource.rstrip("/").rsplit("/", 1)[-1]
    descriptor = CapabilityDescriptor(
        descriptor_id=descriptor_id,
        name=name,
        cost=price,
        source_reference=ARC_DEMO_SOURCE_REFERENCE,
    )
    candidate = normalize(
        descriptor,
        expected_post_action_success_probability=expected_post_action_success_probability,
    )
    offer = CircleOffer(
        descriptor_id=descriptor_id,
        resource=resource,
        name=name,
        method=method,
        network=ARC_TESTNET_NETWORK,
        quoted_cost=price,
        source_reference=ARC_DEMO_SOURCE_REFERENCE,
        request_url=resource,
        asset=ARC_TESTNET_USDC,
        scheme=ARC_X402_SCHEME,
        atomic_amount=atomic,
        extra_name=ARC_X402_BATCHING_NAME,
        extra_version=ARC_X402_BATCHING_VERSION,
        verifying_contract=ARC_TESTNET_GATEWAY_WALLET,
    )
    return CircleCapabilityCatalog(
        catalog=CapabilityCatalog(entries=((candidate, descriptor),)),
        offers=(offer,),
    )


def _money_to_atomic(value: Money) -> str:
    units = value.amount * Decimal(10**6)
    if units != units.to_integral_value():
        raise ValueError("Arc x402 price must have at most 6 USDC decimal places.")
    return str(int(units))


def _normalize_evm_address(value: object, label: str) -> str:
    if not isinstance(value, str) or re.fullmatch(r"0x[0-9a-fA-F]{40}", value) is None:
        raise ValueError(
            f"{label} must have a 0x prefix and exactly 40 hexadecimal characters."
        )
    return value.lower()


def arc_setup_blockers(environment: Mapping[str, str] | None = None) -> tuple[str, ...]:
    """Return pure configuration blockers without initializing Circle or paying."""
    values = os.environ if environment is None else environment
    blockers = [f"missing {name}" for name in ARC_REQUIRED_ENVIRONMENT if not values.get(name)]
    address = values.get("CIRCLE_ARC_WALLET_ADDRESS")
    if address:
        try:
            _normalize_evm_address(address, "CIRCLE_ARC_WALLET_ADDRESS")
        except ValueError as exc:
            blockers.append(str(exc))
    price = values.get("RADHANITE_ARC_PRICE")
    if price:
        try:
            parsed = Money(price)
            if not parsed.is_positive:
                blockers.append("RADHANITE_ARC_PRICE must be positive")
            _money_to_atomic(parsed)
        except (TypeError, ValueError) as exc:
            blockers.append(f"invalid RADHANITE_ARC_PRICE: {exc}")
    resource = values.get("RADHANITE_ARC_RESOURCE")
    if resource and not resource.startswith(("http://", "https://")):
        blockers.append("RADHANITE_ARC_RESOURCE must be an HTTP(S) URL")
    return tuple(blockers)


def _environment_value(environment: Mapping[str, str] | None, name: str) -> str | None:
    if environment is None:
        return os.environ.get(name)
    return environment.get(name)


def _parse_result(stdout: str | None) -> Mapping[str, Any] | None:
    if not stdout:
        return None
    for line in reversed(stdout.splitlines()):
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, Mapping):
            return payload
    return None


def _safe_error(
    payload: Mapping[str, Any] | None, stderr: str | None, stdout: str | None
) -> str:
    if payload:
        message = payload.get("error") or payload.get("message")
        if isinstance(message, str) and message:
            return message[:240]
    return (stderr or stdout or "unknown helper error").strip()[:240]


def _validate_result(
    payload: Mapping[str, Any], offer: CircleOffer, authorized: Money
) -> None:
    if payload.get("status") != "gateway_accepted":
        raise ArcPaymentError(f"Arc helper did not report Gateway acceptance: {payload!r}")
    if payload.get("settlement_status") != "gateway_accepted":
        raise ArcPaymentError("Arc helper returned an unsupported settlement status.")
    if payload.get("network") != ARC_TESTNET_NETWORK:
        raise ArcPaymentError("Arc helper returned a non-Arc network.")
    if _normalize_evm_address(payload.get("asset"), "Arc helper asset") != ARC_TESTNET_USDC.lower():
        raise ArcPaymentError("Arc helper returned a non-Arc-USDC asset.")
    try:
        actual = Money(str(payload.get("amount")))
    except (TypeError, ValueError) as exc:
        raise ArcPaymentError("Arc helper returned an invalid committed amount.") from exc
    if actual != authorized or actual != offer.quoted_cost:
        raise ArcPaymentError(
            f"Arc helper committed {actual}, expected exactly {authorized}."
        )
    if payload.get("response_status") not in {200, 201, 202}:
        raise ArcPaymentError("Arc helper did not receive a successful seller response.")
    reference = payload.get("payment_reference")
    if not isinstance(reference, str) or not reference.strip():
        raise ArcPaymentError("Arc helper returned no Gateway payment reference.")
