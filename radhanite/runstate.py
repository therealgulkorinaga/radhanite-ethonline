"""What a capability run carries, and the snapshots that make it auditable.

TASK-007 §3. **State only.** Nothing here executes a capability, consumes a
candidate, advances a counter, classifies a terminal condition, or drives a
loop — those are later steps of TASK-007, and a state model that quietly did any
of them would be the loop wearing a different name.

Three things this module is careful about.

**`task_state` is opaque — §3.1.** TASK-007 *stores and passes* it and **never
reads inside it**. It is held **by reference**, which is the only contract
consistent with that prohibition: copying or freezing an arbitrary object means
inspecting it, and deep-copying one would break the perfectly reasonable states
that cannot be copied. The consequence is stated plainly in `RunState` rather
than left for someone to discover.

**The ledger is bounded at both ends — §3.2.1.** `Money` represents negative
amounts, so `total_spend + remaining_budget == initial_budget` is not sufficient
on its own; `remaining_budget > initial_budget` would satisfy it while producing
a negative spend. Both bounds are checked.

**Pre-loop spend is preserved, not assumed away — §3.2.** `initial_budget` is
the original run budget. A run may enter with `remaining_budget` already lower
because earlier work spent money, and `total_spend` is derived from the
difference rather than starting at zero.
"""

from __future__ import annotations

from collections.abc import Collection
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from radhanite._immutable import refuse_rehydration

from radhanite.money import Money
from radhanite.policy import RunPolicy
from radhanite.probability import Probability
from radhanite.selection import Selection

__all__ = [
    "RunSnapshot",
    "RunState",
    "RunStatus",
    "TransitionRecord",
    "begin_run",
]


class RunStatus(Enum):
    """Where a run stands — TASK-007 §6.

    The four terminal values are declared here because the state model has to
    be able to *hold* one. **Deciding which applies is not this step's job**:
    §6.1's precedence and §6.2's classification arrive with the loop.
    """

    RUNNING = "running"
    TASK_COMPLETE = "task_complete"
    ECONOMIC_STOP = "economic_stop"
    SAFETY_STOP = "safety_stop"
    EXECUTION_FAILURE = "execution_failure"

    @property
    def is_terminal(self) -> bool:
        return self is not RunStatus.RUNNING


@refuse_rehydration
@dataclass(frozen=True, slots=True)
class RunSnapshot:
    """Every §3 field except `history` — TASK-007 §3.3.

    The exclusion is the point. A history holds snapshots; a snapshot holding a
    history would make the record recursively self-containing and impossible to
    construct, which is what `CODEX-PR027-02` caught in the specification.
    """

    task_value: Money
    initial_budget: Money
    policy: RunPolicy
    task_state: Any
    current_success_probability: Probability
    remaining_budget: Money
    total_spend: Money
    consumed_candidate_ids: tuple[str, ...]
    capability_step_count: int
    status: RunStatus


@refuse_rehydration
@dataclass(frozen=True, slots=True)
class TransitionRecord:
    """One iteration of the loop, as a fact rather than a reconstruction.

    Defined here because `RunState.history` needs a member type. **No transition
    is produced by this step** — building these is the loop's job.

    `execution` is deliberately untyped for now: the execution result belongs to
    a later TASK-007 step, and inventing its shape here would be an abstraction
    justified only by future work (`ARCHITECTURE.md` §6 item 7). It is `None` on
    a STOP iteration in any case, per §3.3.
    """

    before: RunSnapshot
    selection: Selection
    after: RunSnapshot
    execution: Any = None


@refuse_rehydration
@dataclass(frozen=True, slots=True)
class RunState:
    """The state a capability run carries — TASK-007 §3.

    Immutable per transition: an iteration produces a **new** state rather than
    mutating this one.

    **`task_state` is held by reference and never inspected.** A caller that
    mutates the object it handed in will therefore change what every snapshot
    appears to have recorded. The specification requires opacity, and opacity
    and defensive copying are mutually exclusive — so the obligation sits with
    the caller: **supply state that does not change underneath the run.**

    >>> run = begin_run(
    ...     task_value=Money("50000.00"),
    ...     initial_budget=Money("250.00"),
    ...     remaining_budget=Money("180.00"),
    ...     policy=RunPolicy(max_capability_steps=4),
    ...     task_state={"evidence": []},
    ...     current_success_probability=Probability("0.20"),
    ... )
    >>> str(run.total_spend), run.capability_step_count, run.status.value
    ('$70.00', 0, 'running')
    """

    task_value: Money
    initial_budget: Money
    policy: RunPolicy
    task_state: Any
    current_success_probability: Probability
    remaining_budget: Money
    total_spend: Money
    consumed_candidate_ids: tuple[str, ...]
    capability_step_count: int
    status: RunStatus
    history: tuple[TransitionRecord, ...] = ()

    @property
    def max_capability_steps(self) -> int:
        """The ceiling, read from the policy rather than duplicated."""
        return self.policy.max_capability_steps

    def snapshot(self) -> RunSnapshot:
        """This state, minus the history, for a transition record to hold.

        Takes nothing from the run and changes nothing in it.
        """
        return RunSnapshot(
            task_value=self.task_value,
            initial_budget=self.initial_budget,
            policy=self.policy,
            task_state=self.task_state,
            current_success_probability=self.current_success_probability,
            remaining_budget=self.remaining_budget,
            total_spend=self.total_spend,
            consumed_candidate_ids=self.consumed_candidate_ids,
            capability_step_count=self.capability_step_count,
            status=self.status,
        )


def begin_run(
    *,
    task_value: Money,
    initial_budget: Money,
    remaining_budget: Money,
    policy: RunPolicy,
    task_state: Any,
    current_success_probability: Probability,
    consumed_candidate_ids: Collection[str] = (),
    capability_step_count: int = 0,
) -> RunState:
    """Build a valid starting state, deriving the ledger from the budget.

    Keyword-only: three `Money` amounts that are not interchangeable by meaning
    would be silently swappable positionally.

    `total_spend` is **derived**, never supplied — §3.2. A caller cannot state a
    spend that disagrees with the budget it also states.

    >>> run = begin_run(
    ...     task_value=Money("100.00"), initial_budget=Money("10.00"),
    ...     remaining_budget=Money("10.00"), policy=RunPolicy(max_capability_steps=2),
    ...     task_state=None, current_success_probability=Probability("0.5"),
    ... )
    >>> str(run.total_spend)
    '$0.00'
    """
    for label, amount in (
        ("task_value", task_value),
        ("initial_budget", initial_budget),
        ("remaining_budget", remaining_budget),
    ):
        if not isinstance(amount, Money):
            raise TypeError(f"{label} must be a Money amount.")

    if not isinstance(policy, RunPolicy):
        raise TypeError("policy must be a RunPolicy; the ceiling is run policy.")
    if not isinstance(current_success_probability, Probability):
        raise TypeError("current_success_probability must be a Probability.")

    if initial_budget.is_negative:
        raise ValueError(f"initial_budget cannot be negative, got {initial_budget}.")
    if remaining_budget.is_negative:
        raise ValueError(
            f"remaining_budget cannot be negative, got {remaining_budget}. The "
            "budget ceiling has already been breached."
        )
    if remaining_budget > initial_budget:
        # §3.2.1. Without this the identity below still holds while total_spend
        # comes out negative, which is not a coherent ledger.
        raise ValueError(
            f"remaining_budget {remaining_budget} exceeds initial_budget "
            f"{initial_budget}. A run cannot hold more than it was given."
        )

    total_spend = initial_budget - remaining_budget

    return RunState(
        task_value=task_value,
        initial_budget=initial_budget,
        policy=policy,
        task_state=task_state,
        current_success_probability=current_success_probability,
        remaining_budget=remaining_budget,
        total_spend=total_spend,
        consumed_candidate_ids=_checked_consumed(consumed_candidate_ids),
        capability_step_count=_checked_count(capability_step_count),
        status=RunStatus.RUNNING,
        history=(),
    )


def _checked_consumed(consumed_candidate_ids: Collection[str]) -> tuple[str, ...]:
    """Sorted, de-duplicated, frozen — the same normalization as eligibility.

    Sorted because a set's iteration order depends on the process hash seed and
    a record that reorders between identical runs cannot be compared with
    itself. Copied so a caller mutating their own collection afterwards cannot
    change what the run says it knew.
    """
    if isinstance(consumed_candidate_ids, (str, bytes)):
        # `"a" in "abc"` is a substring test, which would treat candidates as
        # consumed that never were.
        raise TypeError(
            "consumed_candidate_ids must be a collection of identifiers, not a "
            "string. Membership in a string is a substring test."
        )
    if not isinstance(consumed_candidate_ids, Collection):
        raise TypeError(
            "consumed_candidate_ids must be a collection, got "
            f"{type(consumed_candidate_ids).__name__}."
        )
    for consumed_id in consumed_candidate_ids:
        if not isinstance(consumed_id, str):
            raise TypeError(
                "consumed_candidate_ids must contain identifiers, found "
                f"{type(consumed_id).__name__}."
            )
    return tuple(sorted(set(consumed_candidate_ids)))


def _checked_count(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        # bool subclasses int, so True would otherwise pass as a count of one.
        raise TypeError(
            f"capability_step_count must be a whole number, got "
            f"{type(value).__name__}."
        )
    if value < 0:
        raise ValueError(
            f"capability_step_count cannot be negative, got {value}."
        )
    return value
