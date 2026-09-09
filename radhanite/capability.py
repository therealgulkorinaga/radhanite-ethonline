"""A candidate capability: something priced that a task could buy.

TASK-006 §2.2 fixes what the economic rule may know about a purchasable action,
and it is deliberately almost nothing:

    a stable identifier, a cost, and the probability of task success it
    claims to leave behind

**Nothing else may enter the decision.** A capability bought from a marketplace
and one computed locally are the same shape here, and that is the point — a
field that let the rule tell them apart would let a provider influence a choice
by being that provider, which §2.1 forbids and which would make this something
other than an economic layer.

**These figures are declared constants, not measurements.** Radhanite does not
estimate them, learn them, or update them from what happened on previous runs;
that is `BL-05` and `BL-06` in the backlog and is unauthorized. No document or
output may present them as measured performance — TASK-006 §9.

This module holds the *shape* of a candidate and the checks an offer must pass
to be decided over. **It contains no economic rule.** Eligibility, ranking and
the termination safeguards arrive in later steps of TASK-006, and this file must
not anticipate them.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from radhanite._immutable import refuse_rehydration

from radhanite.money import Money
from radhanite.probability import Probability

__all__ = ["Candidate", "validate_candidates"]


@refuse_rehydration
@dataclass(frozen=True, slots=True)
class Candidate:
    """One priced action the task could buy, and what it claims to be worth.

    >>> c = Candidate(
    ...     candidate_id="second-opinion-001",
    ...     cost=Money("0.50"),
    ...     success_probability=Probability("0.80"),
    ... )
    >>> print(c, c.cost, c.success_probability)
    second-opinion-001 $0.50 0.80
    """

    candidate_id: str
    cost: Money
    success_probability: Probability

    def __post_init__(self) -> None:
        if not isinstance(self.candidate_id, str):
            raise TypeError(
                "candidate_id must be a string; run records and the "
                "single-use rule both refer to candidates by it."
            )
        if not self.candidate_id or not self.candidate_id.strip():
            raise ValueError(
                "A candidate needs an identifier. TASK-006 §2.5a makes an offer "
                "single-use by identity, so a candidate without one cannot be "
                "recorded as consumed."
            )
        if self.candidate_id != self.candidate_id.strip():
            # "a " and "a" would be two candidates that read as one in a run
            # record, and one could be consumed while the other stayed on offer.
            raise ValueError(
                "candidate_id cannot begin or end with whitespace, got "
                f"{self.candidate_id!r}."
            )

        if not isinstance(self.cost, Money):
            raise TypeError("cost must be a Money amount.")
        if not self.cost.is_positive:
            # TASK-006 §2.5 A, the positive-cost invariant. This is a
            # termination safeguard rather than an economic preference: a free
            # candidate with any positive uplift would be eligible, be selected,
            # and — since these probabilities are declared fixtures that do not
            # move when a capability executes — be eligible again on identical
            # terms, forever, without ever exceeding the budget. Refused here,
            # at construction, so the condition cannot be reached at all.
            raise ValueError(
                f"cost must be greater than zero, got {self.cost}. A zero-cost "
                "or local action is not a purchasable capability — TASK-006 "
                "§2.5 A."
            )

        if not isinstance(self.success_probability, Probability):
            raise TypeError("success_probability must be a Probability.")

        # Deliberately NOT checked: that this candidate improves on anything.
        # A candidate is constructed knowing only itself, and whether its
        # probability beats the task's current one is a question about a
        # decision, not about the offer. TASK-006 §2.3 answers it, and answering
        # it here would both need state this object does not have and make a
        # perfectly ordinary economic situation — an offer not worth taking —
        # into an invalid one. TASK-001 refused the same temptation for a
        # worthless escalation; that was finding CODEX-PR006-04.

    def __str__(self) -> str:
        return self.candidate_id


def validate_candidates(candidates: Sequence[Candidate]) -> tuple[Candidate, ...]:
    """Check an offer is something a decision can be made over, and freeze it.

    Returns the candidates as a tuple, so that what a decision reads cannot be
    changed underneath it by whoever passed it in.

    Two things are refused rather than resolved, both because they would leave
    the outcome undefined rather than merely awkward — TASK-006 §2.2.

    >>> a = Candidate("a", Money("0.10"), Probability("0.60"))
    >>> b = Candidate("b", Money("0.20"), Probability("0.70"))
    >>> [str(c) for c in validate_candidates([a, b])]
    ['a', 'b']
    >>> validate_candidates([])
    ()
    """
    if not isinstance(candidates, Sequence) or isinstance(candidates, (str, bytes)):
        # A set is not a Sequence, and iterating one yields its members in an
        # order that depends on the process's hash seed. Selection itself is
        # order-independent — TASK-006 §2.4's ranking is total — but the run
        # record lists every candidate considered, and a record whose contents
        # reorder between identical runs is not reproducible. Refused at the
        # boundary rather than silently producing a different document each
        # time, exactly as TASK-001's select() refuses an unordered catalogue.
        raise TypeError(
            "candidates must be an ordered sequence, not "
            f"{type(candidates).__name__}. Selection does not depend on order, "
            "but the run record does, and an unordered collection cannot "
            "produce a reproducible one."
        )

    frozen = tuple(candidates)

    for position, candidate in enumerate(frozen):
        if not isinstance(candidate, Candidate):
            raise TypeError(
                f"candidates[{position}] must be a Candidate, got "
                f"{type(candidate).__name__}."
            )

    seen: dict[str, int] = {}
    for position, candidate in enumerate(frozen):
        first = seen.get(candidate.candidate_id)
        if first is not None:
            # The tie-break in TASK-006 §2.4 terminates on the identifier, so
            # two candidates sharing one leave selection undefined; and §2.5a
            # makes an offer single-use by identity, so consuming one would
            # silently consume the other. Refused rather than resolved: an input
            # that cannot produce a deterministic answer is not processed into
            # one.
            raise ValueError(
                f"Duplicate candidate_id {candidate.candidate_id!r} at "
                f"positions {first} and {position}. Identifiers must be unique "
                "within one decision — TASK-006 §2.2."
            )
        seen[candidate.candidate_id] = position

    return frozen
