"""Turning what is on offer into something the economic rule can judge.

TASK-008 is the boundary between **external capability sources** and TASK-006's
`Candidate`. It answers one question:

    given a capability that is actually available, at a price already known,
    what does the economic rule need to know about it?

The answer is deliberately almost nothing — an identifier, a cost, and a claimed
resulting probability. Everything else an adapter needs to *invoke* the thing
stays on this side of the line.

**The asymmetry is the point.** Acquisition knows who is selling; the decision
does not. That is what lets adapters be provider-specific while TASK-006 §2.1
stays neutral, and it is why `CapabilityDescriptor` and `Candidate` are separate
types rather than one type with optional fields.

**This module normalizes and nothing else.** It selects nothing, executes
nothing, pays nothing, and updates no task state. Those are TASK-006, the
adapters, and TASK-009 respectively.

**The known-price invariant, TASK-008 §6.2.** A capability may enter the
candidate set only when its exact cost is known **before purchase**, because the
comparison TASK-006 exists to make —

    incremental_expected_value > candidate_cost

— cannot be made against a price nobody has yet. There is deliberately **no
representation for an unknown cost**: a source that cannot quote cannot build a
descriptor at all. Reading a price is not buying anything, and nothing here pays
to discover one.

**Probabilities are supplied, never computed.** The expected post-action
probability is a declared benchmark figure handed in by the caller. Nothing here
estimates, learns, or infers it — least of all from who is selling, which this
module must never treat as evidence of anything.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from radhanite._immutable import refuse_rehydration

from radhanite.capability import Candidate
from radhanite.money import Money
from radhanite.probability import Probability

__all__ = [
    "CapabilityCatalog",
    "CapabilityDescriptor",
    "acquire",
    "normalize",
]


@refuse_rehydration
@dataclass(frozen=True, slots=True)
class CapabilityDescriptor:
    """One externally available capability, as its source describes it.

    Four fields, which is the minimum that lets an adapter recover its own
    handle after selection without TASK-008 understanding what that handle
    means.

    >>> d = CapabilityDescriptor(
    ...     descriptor_id="second-opinion-001",
    ...     name="Independent second opinion",
    ...     cost=Money("0.50"),
    ...     source_reference="opaque-handle-abc",
    ... )
    >>> print(d.descriptor_id, d.cost)
    second-opinion-001 $0.50
    """

    descriptor_id: str
    name: str
    cost: Money
    source_reference: str

    def __post_init__(self) -> None:
        for label, text in (
            ("descriptor_id", self.descriptor_id),
            ("name", self.name),
            ("source_reference", self.source_reference),
        ):
            if not isinstance(text, str):
                raise TypeError(f"{label} must be a string, got {type(text).__name__}.")
        if not self.descriptor_id.strip():
            raise ValueError(
                "A descriptor needs an identifier; it becomes the candidate's, "
                "and the run refers to what it bought by that."
            )
        if self.descriptor_id != self.descriptor_id.strip():
            raise ValueError(
                f"descriptor_id cannot be whitespace-padded, got {self.descriptor_id!r}."
            )
        if not self.name.strip():
            raise ValueError("A descriptor needs a name; a run record has to say what was bought.")

        if not isinstance(self.cost, Money):
            # There is no representation for an unknown or estimated price, and
            # that is the invariant rather than an oversight — TASK-008 §6.2.
            raise TypeError(
                "cost must be a Money amount, known before purchase. A source "
                f"that cannot quote a price cannot offer a capability; got "
                f"{type(self.cost).__name__}."
            )
        if not self.cost.is_positive:
            raise ValueError(
                f"cost must be greater than zero and known before purchase, got "
                f"{self.cost}. TASK-006 §2.5 A excludes free capabilities so the "
                "loop terminates, and §2.3 needs a real price to compare against."
            )

        # Deliberately NOT checked: whether this capability is worth buying.
        # A descriptor describes what is on offer. Whether it beats the task's
        # current probability is a question about a decision, and answering it
        # here would put economics in the acquisition layer.

    def __str__(self) -> str:
        return self.descriptor_id


@refuse_rehydration
@dataclass(frozen=True, slots=True)
class CapabilityCatalog:
    """What was acquired: candidates for the decision, descriptors for later.

    TASK-007 §5.2 hands an executor the candidate TASK-006 selected. The
    executor needs the descriptor behind it, and `Candidate` deliberately cannot
    carry one — so the mapping lives here, owned by the layer that made it.
    """

    entries: tuple[tuple[Candidate, CapabilityDescriptor], ...]

    @property
    def candidates(self) -> tuple[Candidate, ...]:
        """The offer, in the order it was acquired, ready for TASK-006."""
        return tuple(candidate for candidate, _ in self.entries)

    @property
    def descriptors(self) -> tuple[CapabilityDescriptor, ...]:
        return tuple(descriptor for _, descriptor in self.entries)

    def descriptor_for(self, candidate_id: str) -> CapabilityDescriptor:
        """Recover what a selected candidate actually was.

        Raises `KeyError` for an identifier this catalogue did not produce —
        deterministically, rather than returning something plausible.
        """
        for candidate, descriptor in self.entries:
            if candidate.candidate_id == candidate_id:
                return descriptor
        raise KeyError(
            f"No capability in this catalogue has candidate_id {candidate_id!r}. "
            "A selection can only be executed against the catalogue it came from."
        )

    def __len__(self) -> int:
        return len(self.entries)


def normalize(
    descriptor: CapabilityDescriptor,
    *,
    expected_post_action_success_probability: Probability,
) -> Candidate:
    """Make one descriptor into a candidate the economic rule can judge.

    **Identity rule:** the candidate takes the descriptor's identifier,
    unchanged. One rule, no derivation, nothing to drift — and a capability
    offered again after the task state changes arrives as a *new* descriptor
    with a new identifier from its source, which is what makes it a new
    candidate under TASK-006 §2.5a.

    The probability is keyword-only: a `Money` and a `Probability` are not
    interchangeable, but a positional call site reads as though the order were
    arbitrary.

    >>> d = CapabilityDescriptor("research-042", "Market research",
    ...                          Money("0.40"), "opaque-ref")
    >>> c = normalize(d, expected_post_action_success_probability=Probability("0.85"))
    >>> print(c.candidate_id, c.cost, c.success_probability)
    research-042 $0.40 0.85
    """
    if not isinstance(descriptor, CapabilityDescriptor):
        raise TypeError(
            f"descriptor must be a CapabilityDescriptor, got {type(descriptor).__name__}."
        )
    if not isinstance(expected_post_action_success_probability, Probability):
        raise TypeError(
            "expected_post_action_success_probability must be a Probability. It "
            "is a declared benchmark figure supplied by the caller; nothing here "
            "estimates or learns it."
        )

    return Candidate(
        candidate_id=descriptor.descriptor_id,
        cost=descriptor.cost,
        success_probability=expected_post_action_success_probability,
    )


def acquire(
    offers: Sequence[tuple[CapabilityDescriptor, Probability]],
) -> CapabilityCatalog:
    """Normalize a whole offer, and keep the mapping back to its descriptors.

    Duplicate identifiers are **refused, not resolved**: TASK-006 §2.4's
    tie-break terminates on the identifier and §2.5a makes an offer single-use
    by it, so two capabilities sharing one would leave both undefined. The same
    refusal `validate_candidates` makes, applied one layer earlier where the
    duplicate actually originates.

    >>> offer = [(CapabilityDescriptor("a", "A", Money("0.10"), "r1"), Probability("0.6"))]
    >>> catalog = acquire(offer)
    >>> catalog.candidates[0].candidate_id, catalog.descriptor_for("a").name
    ('a', 'A')
    """
    if not isinstance(offers, Sequence) or isinstance(offers, (str, bytes)):
        # Selection is order-independent, but the run record is not — TASK-006
        # §2.2. An unordered offer cannot produce a reproducible one.
        raise TypeError(
            "offers must be an ordered sequence of (descriptor, probability) "
            f"pairs, not {type(offers).__name__}."
        )

    entries: list[tuple[Candidate, CapabilityDescriptor]] = []
    seen: dict[str, int] = {}

    for position, offer in enumerate(offers):
        if not isinstance(offer, tuple) or len(offer) != 2:
            raise TypeError(
                f"offers[{position}] must be a (descriptor, probability) pair."
            )
        descriptor, probability = offer

        candidate = normalize(
            descriptor, expected_post_action_success_probability=probability
        )

        first = seen.get(candidate.candidate_id)
        if first is not None:
            raise ValueError(
                f"Duplicate capability identifier {candidate.candidate_id!r} at "
                f"positions {first} and {position}. Identifiers must be unique "
                "within one offer — TASK-006 §2.2."
            )
        seen[candidate.candidate_id] = position
        entries.append((candidate, descriptor))

    return CapabilityCatalog(entries=tuple(entries))
