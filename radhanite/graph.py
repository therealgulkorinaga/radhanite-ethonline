"""TASK-011 The Graph onchain evidence adapter.

This module is a provider-specific edge, exactly as `circle.py` is. It buys
**onchain information** from a subgraph on The Graph's decentralized network and
hands the result to TASK-009 as evidence. It is not part of the economic
decision, and nothing here may become part of one.

**The premise, TASK-011 §1.** The Graph is not a privileged source. It is one
capability among the candidates on offer, priced before purchase, judged by the
ordinary rule:

    incremental_expected_value > candidate_cost

Buying information is a purchase like any other. It has a price, it may improve
the odds, and it is not exempt from `value > cost` because it happens to be data
rather than judgement.

**What this module must never do, TASK-011 §3.** Provider identity stays out of
selection. `GraphQuerySpec` holds the subgraph ID, the query document and the
endpoint; TASK-006 sees only the three `Candidate` fields, through TASK-008's
`normalize`. There is deliberately no field, branch, weighting, tie-break or
"trusted source" concept anywhere on the selection path — a capability backed by
a subgraph and one computed locally are indistinguishable to the rule.

**Probability is not touched here.** Returned data becomes a
`make_evidence` record for TASK-009, which owns the judgement of what it means.
This adapter never computes, adjusts or infers a probability — TASK-011 §6.3
belongs to the task-state layer, and this module does not annex it.

The three decisions TASK-011 §6 left open are resolved **narrowly**, as the
minimum that lets the capability exist at all:

- **§6.1, what is one candidate.** One candidate is one *query shape* — a named
  GraphQL document against one named subgraph. The pair is the identity, so a
  stable `descriptor_id` identifies something that does not drift, and TASK-006
  §2.5a's single-use rule has a fixed thing to consume.
- **§6.2, where the price comes from.** The price is **declared before the
  call**, as a benchmark fixture, and is strictly positive. Gateway query
  pricing is only knowable afterwards, which TASK-006 §2.3 does not accept, so
  the adapter refuses to construct a spec without an exact pre-purchase price.
  Nothing here discovers a price by paying for one.
- **§6.3, how evidence becomes a probability.** It does not, here. See above.

Standard library only, matching the rest of the package.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Protocol

from radhanite.acquisition import CapabilityCatalog, CapabilityDescriptor, normalize
from radhanite.capability import Candidate
from radhanite.capability_execution import ExecutionResult
from radhanite.money import Money
from radhanite.probability import Probability
from radhanite.revenue import make_evidence

__all__ = [
    "GATEWAY_URL_TEMPLATE",
    "GraphCapabilityCatalog",
    "GraphCapabilityExecutor",
    "GraphGatewayClient",
    "GraphQueryError",
    "GraphQueryReceipt",
    "GraphQuerySpec",
    "GraphCommitmentUnresolvedError",
    "GraphPostAttemptError",
    "GraphPreAttemptError",
    "catalog_from_query_specs",
]

GATEWAY_URL_TEMPLATE = "https://gateway.thegraph.com/api/subgraphs/id/{subgraph_id}"

_EVIDENCE_TYPE = "graph_onchain_evidence"
_USER_AGENT = "radhanite/0.1.0 (+https://github.com/therealgulkorinaga/radhanite-ethonline)"
_FACT_EXCERPT_LENGTH = 240


class GraphQueryError(ValueError):
    """The gateway response cannot produce usable onchain evidence."""


class GraphPreAttemptError(RuntimeError):
    """The query failed before any request or financial commitment began."""


class GraphPostAttemptError(RuntimeError):
    """The query was served, but no usable result could be recovered."""


class GraphCommitmentUnresolvedError(GraphPostAttemptError):
    """The gateway answered, but whether it billed the query is unknown."""


@dataclass(frozen=True, slots=True)
class GraphQuerySpec:
    """One priced query shape: provider metadata retained outside TASK-006.

    The subgraph ID and the document together are the capability's identity —
    §6.1. Neither ever reaches `Candidate`.
    """

    descriptor_id: str
    name: str
    subgraph_id: str
    document: str
    declared_cost: Money
    fact_fields: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for label, text in (
            ("descriptor_id", self.descriptor_id),
            ("name", self.name),
            ("subgraph_id", self.subgraph_id),
            ("document", self.document),
        ):
            if type(text) is not str:
                raise TypeError(f"{label} must be exactly str, got {type(text).__name__}.")
            if not text.strip():
                raise ValueError(f"{label} cannot be empty or whitespace.")
        if self.descriptor_id != self.descriptor_id.strip():
            raise ValueError(
                f"descriptor_id cannot be whitespace-padded, got {self.descriptor_id!r}."
            )
        if type(self.declared_cost) is not Money:
            # TASK-011 §6.2. There is no representation for a price discovered
            # after the call, and that is the invariant rather than an omission.
            raise TypeError(
                "declared_cost must be exactly Money, known before the query is "
                f"sent; got {type(self.declared_cost).__name__}. Gateway pricing "
                "that is only knowable afterwards does not satisfy TASK-006 §2.3."
            )
        if not self.declared_cost.is_positive:
            raise ValueError(
                f"declared_cost must be greater than zero, got {self.declared_cost}. "
                "TASK-006 §2.5 A excludes free capabilities so the loop terminates."
            )
        if isinstance(self.fact_fields, (str, bytes)) or not isinstance(
            self.fact_fields, Sequence
        ):
            raise TypeError("fact_fields must be an ordered sequence of strings.")
        frozen = tuple(self.fact_fields)
        for index, field in enumerate(frozen):
            if type(field) is not str:
                raise TypeError(f"fact_fields[{index}] must be exactly str.")
        object.__setattr__(self, "fact_fields", frozen)

    @property
    def endpoint(self) -> str:
        return GATEWAY_URL_TEMPLATE.format(subgraph_id=self.subgraph_id)

    def descriptor(self) -> CapabilityDescriptor:
        """The TASK-008 view: an identifier, a name, a price, a handle."""
        return CapabilityDescriptor(
            descriptor_id=self.descriptor_id,
            name=self.name,
            cost=self.declared_cost,
            source_reference=self.subgraph_id,
        )


@dataclass(frozen=True, slots=True)
class GraphQueryReceipt:
    """Exact adapter receipt, before conversion to a neutral ExecutionResult."""

    succeeded: bool
    committed_cost: Money
    evidence: Mapping[str, object]


@dataclass(frozen=True, slots=True)
class GraphCapabilityCatalog:
    """TASK-008 catalog plus the provider metadata needed after selection."""

    catalog: CapabilityCatalog
    specs: tuple[GraphQuerySpec, ...]

    @property
    def candidates(self) -> tuple[Candidate, ...]:
        return self.catalog.candidates

    @property
    def descriptors(self) -> tuple[CapabilityDescriptor, ...]:
        return self.catalog.descriptors

    def descriptor_for(self, candidate_id: str) -> CapabilityDescriptor:
        return self.catalog.descriptor_for(candidate_id)

    def spec_for(self, candidate_id: str) -> GraphQuerySpec:
        for spec in self.specs:
            if spec.descriptor_id == candidate_id:
                return spec
        raise KeyError(f"No Graph query spec retained for candidate {candidate_id!r}.")

    def __len__(self) -> int:
        return len(self.catalog)


def catalog_from_query_specs(
    specs: Sequence[GraphQuerySpec],
    *,
    expected_post_action_success_probability: Probability,
) -> GraphCapabilityCatalog:
    """Normalize priced query shapes into candidates TASK-006 can judge.

    The probability is a **declared benchmark fixture** supplied by the caller,
    as everywhere else in the package. Nothing here estimates one, and nothing
    here derives one from who is answering the query.
    """
    if isinstance(specs, (str, bytes)) or not isinstance(specs, Sequence):
        raise TypeError("specs must be an ordered sequence of GraphQuerySpec.")
    frozen = tuple(specs)
    if not frozen:
        raise GraphQueryError("No Graph query specs were supplied; the offer would be empty.")
    for index, spec in enumerate(frozen):
        if type(spec) is not GraphQuerySpec:
            raise TypeError(f"specs[{index}] must be exactly GraphQuerySpec.")
    if type(expected_post_action_success_probability) is not Probability:
        raise TypeError("expected_post_action_success_probability must be exactly Probability.")

    entries = []
    for spec in frozen:
        descriptor = spec.descriptor()
        candidate = normalize(
            descriptor,
            expected_post_action_success_probability=expected_post_action_success_probability,
        )
        entries.append((candidate, descriptor))
    return GraphCapabilityCatalog(catalog=CapabilityCatalog(entries=entries), specs=frozen)


class GraphQueryClient(Protocol):
    """The provider-specific query contract this adapter executes against."""

    def query(self, spec: GraphQuerySpec, maximum_authorized_cost: Money) -> GraphQueryReceipt:
        """Run one query shape and report its exact committed cost."""
        ...


class GraphGatewayClient:
    """Query one subgraph over The Graph's decentralized gateway.

    **Commitment accounting.** The gateway bills for a query an indexer serves,
    and the response is the only thing this client can see. Three cases, and the
    distinction between them is the point rather than a detail:

    - **Nothing was served.** A failure before the request is sent — no API key,
      cost above the ceiling — or a non-200 status, which is the gateway or its
      edge refusing the request before any indexer saw it. `GraphPreAttemptError`,
      and nothing is recorded as spent.
    - **Served and answered.** HTTP 200 carrying `data`: the declared cost is
      committed.
    - **Answered, but billing unknown.** HTTP 200 carrying `errors`, or neither
      `data` nor `errors`. Whether an indexer served and billed it cannot be read
      off the response, so this raises `GraphCommitmentUnresolvedError` rather
      than inventing an amount in either direction — the same stance
      `CirclePaymentCommitmentUnresolvedError` takes in `circle.py`. Subgraph
      Studio's query count is the authority, and a human resolves it there.

    The API key is read from the environment and is never written into evidence,
    a run record, a fact, or an error message.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        timeout: float = 30.0,
        opener: Any = None,
        outcome_key: str = "positive_market_signal",
    ) -> None:
        self.api_key = api_key if api_key is not None else os.environ.get("RADHANITE_GRAPH_API_KEY")
        self.timeout = timeout
        self.opener = opener or urllib.request.urlopen
        self.outcome_key = outcome_key

    def query(self, spec: GraphQuerySpec, maximum_authorized_cost: Money) -> GraphQueryReceipt:
        if type(spec) is not GraphQuerySpec:
            raise TypeError("spec must be exactly GraphQuerySpec.")
        if type(maximum_authorized_cost) is not Money:
            raise TypeError("maximum_authorized_cost must be exactly Money.")
        if not self.api_key:
            raise GraphPreAttemptError(
                "RADHANITE_GRAPH_API_KEY is required; no query was sent and "
                "nothing was spent."
            )
        if spec.declared_cost > maximum_authorized_cost:
            raise GraphPreAttemptError(
                f"Declared cost {spec.declared_cost} exceeds the authorization "
                f"ceiling {maximum_authorized_cost}; no query was sent."
            )

        body = json.dumps({"query": spec.document}).encode("utf-8")
        request = urllib.request.Request(
            spec.endpoint,
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                # The gateway sits behind an edge that rejects the stdlib
                # default agent outright (Cloudflare 1010). Identify honestly.
                "User-Agent": _USER_AGENT,
            },
        )
        try:
            with self.opener(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            # A non-200 status is the gateway or its edge refusing the request
            # before an indexer served it — auth rejection, rate limit, edge
            # block, outage. Nothing was served, so nothing was billed.
            raise GraphPreAttemptError(
                f"The Graph gateway refused the request with HTTP {exc.code}; "
                f"no query was served and nothing was spent: "
                f"{_truncate(_safe_read(exc))}"
            ) from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise GraphPreAttemptError(
                f"Could not reach The Graph gateway; no query was served: {exc}"
            ) from exc

        payload = _parse_json(raw)
        if payload is None:
            raise GraphPostAttemptError(
                "The Graph gateway returned a non-JSON body: " + _truncate(raw)
            )
        errors = payload.get("errors")
        if errors:
            raise GraphCommitmentUnresolvedError(
                "The Graph gateway returned query errors; whether an indexer "
                "served and billed the query is unresolved. Subgraph Studio's "
                "query count is the authority: " + _truncate(json.dumps(errors))
            )
        data = payload.get("data")
        if not isinstance(data, Mapping) or not data:
            raise GraphCommitmentUnresolvedError(
                "The Graph gateway returned neither data nor errors; whether the "
                "query was billed is unresolved: " + _truncate(raw)
            )

        return GraphQueryReceipt(
            succeeded=True,
            committed_cost=spec.declared_cost,
            evidence=self._evidence(
                spec,
                facts=("onchain evidence retrieved", *_facts_from(data, spec.fact_fields)),
            ),
        )

    def _evidence(self, spec: GraphQuerySpec, *, facts: Sequence[str]) -> Mapping[str, object]:
        return make_evidence(
            capability_key=spec.descriptor_id,
            evidence_type=_EVIDENCE_TYPE,
            facts=tuple(facts),
            source_reference=spec.subgraph_id,
            outcome_key=self.outcome_key,
        )


class GraphCapabilityExecutor:
    """Adapt one selected TASK-006 candidate to a Graph query client.

    Mirrors `CircleCapabilityExecutor` deliberately: the generic layer must not
    be able to tell these two apart by anything except the candidates they
    produced.
    """

    def __init__(self, *, catalog: GraphCapabilityCatalog, query_client: GraphQueryClient) -> None:
        self.catalog = catalog
        self.query_client = query_client

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
        spec = self.catalog.spec_for(selected_candidate.candidate_id)
        if selected_candidate.cost != spec.declared_cost:
            raise ValueError("candidate cost differs from the declared pre-query price.")
        if maximum_authorized_cost > spec.declared_cost:
            raise ValueError("authorization ceiling exceeds the declared query cost.")
        receipt = self.query_client.query(spec, maximum_authorized_cost)
        if type(receipt) is not GraphQueryReceipt:
            raise TypeError("Graph query client must return exactly GraphQueryReceipt.")
        if receipt.committed_cost > maximum_authorized_cost:
            raise ValueError(
                f"The Graph committed {receipt.committed_cost}, above authorization "
                f"ceiling {maximum_authorized_cost}; no silent clamping is permitted."
            )
        return ExecutionResult(
            succeeded=receipt.succeeded,
            committed_cost=receipt.committed_cost,
            evidence=receipt.evidence,
        )


def _parse_json(raw: str) -> Mapping[str, Any] | None:
    try:
        payload = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, Mapping) else None


def _safe_read(exc: urllib.error.HTTPError) -> str:
    try:
        return exc.read().decode("utf-8")
    except Exception:  # pragma: no cover - defensive, body may be absent
        return ""


def _truncate(text: str) -> str:
    return text.replace("\n", " ")[:_FACT_EXCERPT_LENGTH]


def _facts_from(data: Mapping[str, Any], fact_fields: Sequence[str]) -> tuple[str, ...]:
    """Render the named response fields as flat, human-readable facts.

    Deliberately dumb. Interpreting what the numbers *mean* is TASK-009's, and
    doing it here would put judgement in the adapter.
    """
    if not fact_fields:
        return (_truncate(json.dumps(data, sort_keys=True)),)
    facts = []
    for field in fact_fields:
        facts.append(f"{field}={_truncate(json.dumps(_dig(data, field), sort_keys=True))}")
    return tuple(facts)


def _dig(data: Any, dotted: str) -> Any:
    """Follow a dotted path, returning None rather than raising when absent."""
    current: Any = data
    for part in dotted.split("."):
        if isinstance(current, Sequence) and not isinstance(current, (str, bytes)):
            try:
                index = int(part)
            except ValueError:
                return None
            current = current[index] if 0 <= index < len(current) else None
            continue
        if not isinstance(current, Mapping) or part not in current:
            return None
        current = current[part]
    return current
