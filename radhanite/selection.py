"""Choosing one capability from an offer, or stopping.

TASK-006 §2.4 fixes the ranking, and it is authoritative:

    Among ELIGIBLE candidates, select the highest net_expected_value.
    Ties are broken deterministically, in this order:
        1. higher net_expected_value wins
        2. if exactly equal, LOWER COST wins
        3. if cost is also exactly equal, the lexicographically SMALLER
           stable candidate ID wins

**The ranking is total, so the order candidates arrive in cannot affect the
result.** That is a real change from TASK-001, where the declared order of the
catalogue *was* the policy. Rule 3 exists only to make the order total; it
carries no economic meaning and must never be described as though it did.

Rule 2 does carry meaning. Because `incremental_expected_value = net + cost`,
two candidates with equal net expected value differ only in how much budget they
consume to deliver it, and the cheaper one leaves more for whatever comes next.

**STOP** is returned when no candidate is eligible, including when none was
offered — TASK-006 §2.5. Stopping is a first-class successful behaviour
(`PREREQ-001` §5.4), not a failure to be worked around.

The other terminal condition in §2.5 — the task's success condition already
being satisfied — is **not** decided here. It is a question about the task
state, answered before selection is considered at all, and this module is never
told the answer. §2.7 keeps selection separate from evaluation.

**This module selects. It does not execute, evaluate, generate candidates, or
advance a run.** The step count and the consumed identifiers are inputs it
reads, never state it keeps: a selector holding its own memory across decisions
has taken on the run loop's job — §2.7.
"""

from __future__ import annotations

from collections.abc import Collection, Sequence
from dataclasses import dataclass
from enum import Enum

from radhanite._immutable import refuse_rehydration

from radhanite.capability import Candidate, validate_candidates
from radhanite.eligibility import Assessment, assess
from radhanite.money import Money
from radhanite.probability import Probability

__all__ = ["Selection", "SelectionOutcome", "select_capability"]


class SelectionOutcome(Enum):
    """What the decision concluded."""

    SELECTED = "selected"
    STOP = "stop"


@refuse_rehydration
@dataclass(frozen=True, slots=True)
class Selection:
    """One decision, with every candidate it was made over.

    TASK-006 §8 requires the run record to expose the candidates that were
    *rejected*, with their figures and the reason each failed. A record showing
    only what was bought cannot answer why the alternatives were not, so the
    assessments are carried whole rather than summarized.

    The decision-level inputs are carried too, because with zero candidates
    there is no assessment to read them from.
    """

    outcome: SelectionOutcome
    reason: str
    selected: Assessment | None
    assessments: tuple[Assessment, ...]
    current_success_probability: Probability
    task_value: Money
    remaining_budget: Money
    consumed_candidate_ids: tuple[str, ...]
    capability_step_count: int
    max_capability_steps: int

    @property
    def stopped(self) -> bool:
        return self.outcome is SelectionOutcome.STOP

    @property
    def eligible(self) -> tuple[Assessment, ...]:
        """Every candidate that passed all six conditions, in offer order."""
        return tuple(a for a in self.assessments if a.eligible)

    @property
    def rejected(self) -> tuple[Assessment, ...]:
        """Every candidate that did not, in offer order."""
        return tuple(a for a in self.assessments if not a.eligible)

    @property
    def stopped_without_economic_judgement(self) -> bool:
        """True when a STOP rests entirely on §2.5's safeguards.

        §8 requires a safety stop to be recorded as one. A run that halted
        because it had bought its allowance did not decide the remaining
        candidates were poor value — it never weighed them at all, and a record
        implying otherwise claims a verdict nobody reached.

        An empty offer is not a safety stop: nothing was refused, so there is no
        refusal to characterize.
        """
        return (
            self.stopped
            and bool(self.assessments)
            and all(a.refused_without_economic_judgement for a in self.assessments)
        )

    def __str__(self) -> str:
        return self.reason


def select_capability(
    *,
    candidates: Sequence[Candidate],
    current_success_probability: Probability,
    task_value: Money,
    remaining_budget: Money,
    consumed_candidate_ids: Collection[str] = (),
    capability_step_count: int = 0,
    max_capability_steps: int,
) -> Selection:
    """Apply TASK-006 §2.3 to every candidate, then §2.4 to the survivors.

    Arguments are keyword-only, for the reason `assess` gives: several are
    interchangeable by shape and none by meaning.

    >>> from radhanite.capability import Candidate
    >>> cheap = Candidate("a-cheap", Money("0.10"), Probability("0.60"))
    >>> strong = Candidate("b-strong", Money("0.50"), Probability("0.80"))
    >>> s = select_capability(
    ...     candidates=[cheap, strong],
    ...     current_success_probability=Probability("0.50"),
    ...     task_value=Money("20.00"),
    ...     remaining_budget=Money("2.00"),
    ...     max_capability_steps=4,
    ... )
    >>> s.selected.candidate.candidate_id
    'b-strong'
    >>> str(s.selected.net_expected_value)
    '$5.50'
    """
    offer = validate_candidates(candidates)

    assessments = tuple(
        assess(
            candidate=candidate,
            current_success_probability=current_success_probability,
            task_value=task_value,
            remaining_budget=remaining_budget,
            consumed_candidate_ids=consumed_candidate_ids,
            capability_step_count=capability_step_count,
            max_capability_steps=max_capability_steps,
        )
        for candidate in offer
    )

    winner: Assessment | None = None
    for assessment in assessments:
        if not assessment.eligible:
            continue
        if winner is None or _outranks(assessment, winner):
            winner = assessment

    outcome = SelectionOutcome.STOP if winner is None else SelectionOutcome.SELECTED

    # Every assessment normalized the same input identically, so any of them
    # carries the canonical form. With no candidates there is none to ask, and
    # the offer was empty of anything that could have consumed an identifier.
    consumed = assessments[0].consumed_candidate_ids if assessments else ()

    return Selection(
        outcome=outcome,
        reason=_explain(
            winner=winner,
            assessments=assessments,
            capability_step_count=capability_step_count,
            max_capability_steps=max_capability_steps,
        ),
        selected=winner,
        assessments=assessments,
        current_success_probability=current_success_probability,
        task_value=task_value,
        remaining_budget=remaining_budget,
        consumed_candidate_ids=consumed,
        capability_step_count=capability_step_count,
        max_capability_steps=max_capability_steps,
    )


def _outranks(challenger: Assessment, incumbent: Assessment) -> bool:
    """TASK-006 §2.4's three levels, in order, written out rather than encoded.

    A strict total order: identifiers are unique within an offer, so no two
    candidates can tie at every level. That is what makes the result independent
    of the order candidates arrived in.
    """
    if challenger.net_expected_value != incumbent.net_expected_value:
        return challenger.net_expected_value > incumbent.net_expected_value
    if challenger.candidate.cost != incumbent.candidate.cost:
        return challenger.candidate.cost < incumbent.candidate.cost
    return challenger.candidate.candidate_id < incumbent.candidate.candidate_id


def _explain(
    *,
    winner: Assessment | None,
    assessments: tuple[Assessment, ...],
    capability_step_count: int,
    max_capability_steps: int,
) -> str:
    considered = len(assessments)

    if winner is not None:
        eligible = sum(1 for a in assessments if a.eligible)
        against = (
            f" against {eligible - 1} other eligible candidate"
            f"{'s' if eligible - 1 != 1 else ''}"
            if eligible > 1
            else ""
        )
        return (
            f"Selected {winner.candidate.candidate_id}: the best net value of "
            f"{winner.net_expected_value}{against}, from {considered} "
            f"considered."
        )

    if considered == 0:
        return (
            "Stop: no capability was offered, so there is nothing to weigh. "
            f"{capability_step_count} of {max_capability_steps} capability "
            "steps used."
        )

    if all(a.refused_without_economic_judgement for a in assessments):
        return (
            f"Stop: none of the {considered} candidate"
            f"{'s' if considered != 1 else ''} offered could be bought, and "
            "none was refused on economic grounds — this is a safety stop, not "
            "a judgement that they were poor value."
        )

    return (
        f"Stop: none of the {considered} candidate"
        f"{'s' if considered != 1 else ''} offered is worth buying within the "
        "budget that remains."
    )
