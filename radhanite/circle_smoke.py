"""Explicit TASK-010 Circle discovery/payment smoke command.

**Implementation agent: Manus.**

Run with ``python3.12 -m radhanite.circle_smoke`` only after installing the
official Circle CLI, logging in, funding the agent/Gateway wallet, and setting
``CIRCLE_WALLET_ADDRESS``. The command never runs from the unit-test suite.
"""

from __future__ import annotations

import os
import sys

from radhanite.circle import (
    CircleCapabilityExecutor,
    CircleCliPaymentClient,
    CircleDiscoveryError,
    CirclePaymentCommitmentUnresolvedError,
    CirclePaymentMetadataError,
    CirclePreAttemptError,
    live_circle_discovery,
)
from radhanite.loop import run_capability_loop
from radhanite.probability import Probability
from radhanite.revenue import RevenueOpportunityUpdater, initialize_benchmark_run
from radhanite.runstate import RunStatus


def main() -> int:
    network = os.environ.get("CIRCLE_DISCOVERY_NETWORK", "eip155:8453")
    chain = os.environ.get("CIRCLE_CHAIN", "BASE")
    allow_mainnet = os.environ.get("CIRCLE_SMOKE_ALLOW_MAINNET") == "1"
    if not os.environ.get("CIRCLE_WALLET_ADDRESS"):
        print("Missing CIRCLE_WALLET_ADDRESS; no payment was attempted.", file=sys.stderr)
        return 2
    if network != "eip155:5042002" and not allow_mainnet:
        print(
            "Refusing a live payment on a non-Arc-testnet network. Set "
            "CIRCLE_SMOKE_ALLOW_MAINNET=1 only after explicitly accepting the "
            "mainnet/testnet choice.",
            file=sys.stderr,
        )
        return 2
    try:
        catalog = live_circle_discovery(
            expected_post_action_success_probability=Probability("0.14"),
            network=network,
        )
    except CircleDiscoveryError as exc:
        print(f"Live Circle discovery failed: {exc}", file=sys.stderr)
        return 1

    print("discovery=live")
    print(f"network={network}")
    print(f"offers={len(catalog)}")
    for candidate in catalog.candidates:
        offer = catalog.offer_for(candidate.candidate_id)
        print(
            f"offer candidate_id={candidate.candidate_id} name={offer.name!r} "
            f"quoted_cost={offer.quoted_cost} resource={offer.resource} method={offer.method}"
        )

    requested_resource = os.environ.get(
        "CIRCLE_RESOURCE",
        "https://api.aisa.one/apis/v2/coingecko/simple/price",
    )
    selected_candidate = next(
        (
            candidate
            for candidate in catalog.candidates
            if catalog.offer_for(candidate.candidate_id).resource == requested_resource
        ),
        None,
    )
    if selected_candidate is None:
        print(
            f"No live Circle offer matched CIRCLE_RESOURCE={requested_resource!r}; "
            "no payment was attempted.",
            file=sys.stderr,
        )
        return 2

    executor = CircleCapabilityExecutor(
        catalog=catalog,
        payment_client=CircleCliPaymentClient(chain=chain),
    )
    initial = initialize_benchmark_run()

    class OneShotSource:
        def __init__(self) -> None:
            self._first = True

        def get_candidates(self, task_state, run_state):
            if self._first:
                self._first = False
                return (selected_candidate,)
            return ()

    try:
        result = run_capability_loop(
            state=initial,
            candidate_source=OneShotSource(),
            executor=executor,
            updater=RevenueOpportunityUpdater(),
        )
    except CirclePreAttemptError as exc:
        print(f"payment=not_attempted reason={exc}", file=sys.stderr)
        return 2
    except CirclePaymentCommitmentUnresolvedError as exc:
        print(f"payment=unresolved_commitment reason={exc}", file=sys.stderr)
        return 2
    except CirclePaymentMetadataError as exc:
        print(f"payment=metadata_rejected reason={exc}", file=sys.stderr)
        return 2

    print(f"status={result.status.value}")
    print(f"committed_cost={result.total_spend}")
    if result.history and result.history[0].execution is not None:
        execution = result.history[0].execution
        print(f"execution_succeeded={execution.succeeded}")
        print(f"execution_committed_cost={execution.committed_cost}")
        print(f"evidence_outcome={execution.evidence.get('outcome_key')}")
    print(f"next_probability={result.current_success_probability}")
    return 0 if result.status is not RunStatus.EXECUTION_FAILURE else 1


if __name__ == "__main__":
    raise SystemExit(main())
