"""Explicit TASK-011 live Graph query smoke command.

Run with ``python3 -m radhanite.graph_smoke`` after exporting a Subgraph Studio
**query** API key:

    export RADHANITE_GRAPH_API_KEY=...

The command never runs from the unit-test suite, and the key is never printed.

It drives the real loop rather than calling the gateway directly: the priced
query shape becomes a TASK-008 descriptor, TASK-006 decides whether it is worth
buying, TASK-007 executes the selection, and TASK-009 interprets the evidence.
If the economics say STOP, no query is sent and no money is spent — which is the
correct outcome, not a failure of the integration.
"""

from __future__ import annotations

import os
import sys

from radhanite.graph import (
    GraphCapabilityExecutor,
    GraphGatewayClient,
    GraphPreAttemptError,
    GraphQuerySpec,
    catalog_from_query_specs,
)
from radhanite.loop import run_capability_loop
from radhanite.money import Money
from radhanite.probability import Probability
from radhanite.revenue import RevenueOpportunityUpdater, initialize_benchmark_run
from radhanite.runstate import RunStatus

# The benchmark's declared onchain-evidence offer. The price is a fixture known
# before the call (TASK-011 §6.2) and the probability is benchmark-declared, as
# everywhere else in the package — neither is measured or predicted here.
DEFAULT_SUBGRAPH_ID = "5zvR82QoaXYFyDEKLZ9t6v9adgnptxYpKpSbxtgVENFV"
DEFAULT_DOCUMENT = (
    "{ factories(first: 1) { poolCount txCount totalVolumeUSD } "
    "_meta { block { number } } }"
)


def benchmark_spec() -> GraphQuerySpec:
    return GraphQuerySpec(
        descriptor_id="graph-onchain-liquidity-001",
        name="Onchain liquidity and volume snapshot",
        subgraph_id=os.environ.get("RADHANITE_GRAPH_SUBGRAPH_ID", DEFAULT_SUBGRAPH_ID),
        document=os.environ.get("RADHANITE_GRAPH_DOCUMENT", DEFAULT_DOCUMENT),
        declared_cost=Money(os.environ.get("RADHANITE_GRAPH_PRICE", "0.40")),
        fact_fields=(
            "factories.0.poolCount",
            "factories.0.txCount",
            "factories.0.totalVolumeUSD",
            "_meta.block.number",
        ),
    )


def main() -> int:
    if not os.environ.get("RADHANITE_GRAPH_API_KEY"):
        print(
            "Missing RADHANITE_GRAPH_API_KEY; no query was sent and nothing was spent.",
            file=sys.stderr,
        )
        return 2

    spec = benchmark_spec()
    catalog = catalog_from_query_specs(
        [spec],
        expected_post_action_success_probability=Probability(
            os.environ.get("RADHANITE_GRAPH_POST_PROBABILITY", "0.17")
        ),
    )
    (candidate,) = catalog.candidates

    print("source=live")
    print(f"subgraph_id={spec.subgraph_id}")
    print(f"endpoint={spec.endpoint}")
    print(f"candidate_id={candidate.candidate_id}")
    print(f"declared_cost={candidate.cost}")
    print(f"expected_post_action_probability={candidate.success_probability}")

    executor = GraphCapabilityExecutor(
        catalog=catalog, query_client=GraphGatewayClient()
    )
    initial = initialize_benchmark_run()
    print(f"initial_probability={initial.current_success_probability}")
    print(f"initial_budget={initial.remaining_budget}")

    class OneShotSource:
        """Offer the priced query once; TASK-006 decides the rest."""

        def __init__(self) -> None:
            self._first = True

        def get_candidates(self, task_state, run_state):
            if self._first:
                self._first = False
                return (candidate,)
            return ()

    try:
        result = run_capability_loop(
            state=initial,
            candidate_source=OneShotSource(),
            executor=executor,
            updater=RevenueOpportunityUpdater(),
        )
    except GraphPreAttemptError as exc:
        print(f"query=not_attempted reason={exc}", file=sys.stderr)
        return 2

    print(f"status={result.status.value}")
    print(f"total_spend={result.total_spend}")
    if result.history and result.history[0].execution is not None:
        execution = result.history[0].execution
        print(f"execution_succeeded={execution.succeeded}")
        print(f"execution_committed_cost={execution.committed_cost}")
        print(f"evidence_outcome={execution.evidence.get('outcome_key')}")
        for fact in execution.evidence.get("facts", ()):
            print(f"fact={fact}")
    else:
        print("execution=none (the economics declined to buy; nothing was spent)")
    print(f"next_probability={result.current_success_probability}")
    return 0 if result.status is not RunStatus.EXECUTION_FAILURE else 1


if __name__ == "__main__":
    raise SystemExit(main())
