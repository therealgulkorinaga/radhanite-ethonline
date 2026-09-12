"""What a capability run carries, and the snapshots that make it auditable.

TASK-007 §3. **State only.** Nothing here executes a capability, consumes a
candidate, advances a counter, classifies a terminal condition, or drives a
loop — those are later steps of TASK-007, and a state model that quietly did any
of them would be the loop wearing a different name.

Three things this module is careful about.

**Types are matched exactly, never by `isinstance` — §3.4.** Every record here
is frozen, but a *subclass* of a frozen record can add a field holding a list,
and a frozen reference to a list is not an immutable list. The same is true one
level down: a `str` subclass makes a fine identifier and a fine place to keep
mutable state. Anything this module **retains** is therefore matched by exact
type. Containers it merely reads and rebuilds are not.

**`task_state` is opaque, and opacity is not aliasing — §3.1.** TASK-007 never
interprets what the state *means*. It does **not** follow that TASK-007 may hold
a live reference to a mutable object the caller still owns: an earlier revision
concluded that it did, and `CODEX-PR030-02` corrected it. Retaining an alias
means a caller can change what an already-written audit record appears to say,
and can inject a back-reference that makes the record recursive after the fact.

So opaque state is **frozen structurally on the way in** — containers become
immutable equivalents, cycles are refused, and anything that cannot be frozen is
refused rather than aliased. Freezing reads *shape*, never meaning: no key,
value or attribute is interpreted, and no domain concept appears here.

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

from collections.abc import Collection, Sequence
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from types import MappingProxyType
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


#: Values that pass through `_frozen` unchanged, matched by **exact type**.
#:
#: Exact, not `isinstance` — `CODEX-PR030-02`. A subclass of an immutable
#: scalar is not immutable: `class Smuggler(int): ...` satisfies
#: `isinstance(x, int)` while carrying a list the caller still owns, and
#: passing it through would store that list by reference through a type check
#: that looked airtight.
#:
#: `Enum` is deliberately absent for the same reason, one level up: an Enum
#: member's `value` can be a list, and every member has an instance
#: dictionary that arbitrary attributes can hang off. No Enum is blanket-safe,
#: and narrowing this to specific authorized Enum types is not PR A's call.
#:
#: `Money`, `Probability` and `RunPolicy` are here because their exact types
#: are frozen slotted values in this repository — a claim about their
#: construction, not about what they represent.
_IMMUTABLE_EXACT_TYPES = frozenset({
    type(None), bool, int, float, complex, str, bytes, Decimal,
    Money, Probability, RunPolicy,
})

#: Container types converted to immutable equivalents, also matched exactly.
#: `MappingProxyType`, `tuple` and `frozenset` are rebuilt rather than passed
#: through: a proxy can wrap a dict the caller still holds, and a subclass of
#: any of them can carry mutable attributes.
_FROZEN_AS_MAPPING = (dict, MappingProxyType)
_FROZEN_AS_TUPLE = (list, tuple)
_FROZEN_AS_FROZENSET = (set, frozenset)


def _frozen(value: Any, _path: frozenset[int] = frozenset()) -> Any:
    """Return an immutable equivalent of `value`, or refuse it.

    Structural only, and matched on **exact type** throughout. Mappings,
    sequences and sets become immutable equivalents with their members frozen
    the same way; the known immutable scalars pass through; **anything else is
    refused rather than aliased.**

    Matching exactly also closes a quieter hole: a `str` subclass is a
    `Sequence`, so an `isinstance` rule would convert `"abc"` into
    `("a", "b", "c")` and record that as the caller's state.

    Cycles are refused deterministically rather than recursed into — a caller
    handing in self-referential state would otherwise either hang the run or
    produce a record that contains itself, which is the defect §3.3 exists to
    prevent.
    """
    kind = type(value)
    if kind in _IMMUTABLE_EXACT_TYPES:
        return value

    if id(value) in _path:
        raise ValueError(
            "task_state contains a cycle. Opaque state is frozen on the way in, "
            "and a self-referential structure cannot be frozen into an "
            "auditable record — TASK-007 §3.3."
        )
    deeper = _path | {id(value)}

    if kind in _FROZEN_AS_MAPPING:
        return MappingProxyType(
            {_frozen(k, deeper): _frozen(v, deeper) for k, v in value.items()}
        )
    if kind in _FROZEN_AS_FROZENSET:
        return frozenset(_frozen(item, deeper) for item in value)
    if kind in _FROZEN_AS_TUPLE:
        return tuple(_frozen(item, deeper) for item in value)

    raise TypeError(
        f"task_state contains {kind.__name__}, which cannot be frozen. TASK-007 "
        "stores opaque state without interpreting it, but it may not hold a "
        "live reference to something the caller can still change, and a "
        "subclass of an immutable type is not immutable — CODEX-PR030-02. "
        "Supply exactly immutable values, or dicts, lists, tuples, sets and "
        "frozensets of them."
    )


def _exactly(value: Any, expected: type, label: str) -> Any:
    """Require `value` to be *exactly* `expected`, not merely an instance of it.

    `CODEX-PR030-01`. Every record here is a frozen slotted dataclass, but a
    subclass of one need not be: it can add a field holding a list, and a frozen
    reference to a list is not an immutable list. Accepted into an audit record,
    that list is caller-owned mutable state inside history — the defect the
    `task_state` freeze closed, arriving through the type system rather than
    past it.

    Subclasses are refused rather than inspected. Deciding *which* subclasses
    happen to be safe would mean walking their fields at construction time and
    would still be wrong the moment one of them grew a field.
    """
    if type(value) is not expected:
        raise TypeError(
            f"{label} must be exactly a {expected.__name__}, got "
            f"{type(value).__name__}. A subclass may add mutable fields that "
            "escape this model, so subclasses are refused — CODEX-PR030-01."
        )
    return value


def _checked_status(status: Any) -> RunStatus:
    return _exactly(status, RunStatus, "status")


def _checked_history(history: Any) -> tuple[TransitionRecord, ...]:
    # `isinstance` is right for the *container*: it is never retained, only
    # read once and rebuilt as a tuple, so a subclass of it changes nothing.
    # The members are retained, which is why they are matched exactly.
    if not isinstance(history, Sequence) or isinstance(history, (str, bytes)):
        raise TypeError(
            f"history must be an ordered sequence, got {type(history).__name__}."
        )
    frozen = tuple(history)
    for position, record in enumerate(frozen):
        _exactly(record, TransitionRecord, f"history[{position}]")
    return frozen


#: The ten §3 fields a run and a snapshot both carry, in specification order.
_SHARED_FIELDS = (
    "task_value",
    "initial_budget",
    "policy",
    "task_state",
    "current_success_probability",
    "remaining_budget",
    "total_spend",
    "consumed_candidate_ids",
    "capability_step_count",
    "status",
)


def _normalise(record: Any) -> None:
    """Check and normalize the ten shared fields, in place, at construction.

    Called from `__post_init__`, so **there is no way to build one of these
    records that skips it** — `CODEX-PR030-01`. `begin_run` is a convenience
    that derives `total_spend`; it is not the only validated path, because a
    validated path that can be sidestepped validates nothing.

    Normalization writes through `object.__setattr__` because the record is
    frozen: the field is being *established*, not changed afterwards.
    """
    for label in ("task_value", "initial_budget", "remaining_budget", "total_spend"):
        _exactly(getattr(record, label), Money, label)
    _exactly(record.policy, RunPolicy, "policy")
    _exactly(
        record.current_success_probability, Probability, "current_success_probability"
    )

    if record.initial_budget.is_negative:
        raise ValueError(
            f"initial_budget cannot be negative, got {record.initial_budget}."
        )
    if record.remaining_budget.is_negative:
        raise ValueError(
            f"remaining_budget cannot be negative, got {record.remaining_budget}. "
            "The budget ceiling has already been breached."
        )
    if record.total_spend.is_negative:
        raise ValueError(
            f"total_spend cannot be negative, got {record.total_spend}. A run "
            "cannot un-spend money."
        )
    if record.remaining_budget > record.initial_budget:
        # §3.2.1. Without this the identity below still holds while total_spend
        # comes out negative, which is not a coherent ledger.
        raise ValueError(
            f"remaining_budget {record.remaining_budget} exceeds initial_budget "
            f"{record.initial_budget}. A run cannot hold more than it was given."
        )
    if record.total_spend > record.initial_budget:
        raise ValueError(
            f"total_spend {record.total_spend} exceeds initial_budget "
            f"{record.initial_budget}."
        )
    if record.total_spend + record.remaining_budget != record.initial_budget:
        # §3.2. The ledger is an identity, not two independent numbers that
        # happen to be written down next to each other.
        raise ValueError(
            f"the ledger does not balance: total_spend {record.total_spend} + "
            f"remaining_budget {record.remaining_budget} != initial_budget "
            f"{record.initial_budget}."
        )

    object.__setattr__(record, "status", _checked_status(record.status))
    object.__setattr__(
        record, "capability_step_count", _checked_count(record.capability_step_count)
    )
    object.__setattr__(
        record,
        "consumed_candidate_ids",
        _checked_consumed(record.consumed_candidate_ids),
    )
    object.__setattr__(record, "task_state", _frozen(record.task_state))


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

    def __post_init__(self) -> None:
        # A snapshot is normally taken from a run that has already been
        # validated, so this repeats work. It is here because a snapshot is
        # public and directly constructible, and the record that gets *audited*
        # is the one that must not be able to hold an aliased task_state or an
        # incoherent ledger.
        _normalise(self)


@refuse_rehydration
@dataclass(frozen=True, slots=True)
class TransitionRecord:
    """One iteration of the loop, as a fact rather than a reconstruction.

    Defined here because `RunState.history` needs a member type. **No transition
    is produced by this step** — building these is the loop's job.

    **`execution` is `None` for STOP iterations and the exact authorized
    `ExecutionResult` for execution transitions** — TASK-007 PR B. The field
    remains provider-neutral and refuses every other payload.

    Accepting anything else would be a live alias inside an audit record, and a
    `RunState` here would put a history inside a history. The exact-type check
    keeps the audit boundary closed without making execution generic.
    """

    before: RunSnapshot
    selection: Selection
    after: RunSnapshot
    execution: Any = None

    def __post_init__(self) -> None:
        # Structural, not economic. A record holding a `RunState` where a
        # snapshot belongs would put a history inside a history, which is the
        # recursion §3.3 exists to prevent.
        for label in ("before", "after"):
            # Exact: a RunState here would put a history inside a history, and a
            # RunSnapshot *subclass* would put a mutable field there.
            _exactly(getattr(self, label), RunSnapshot, label)
        _exactly(self.selection, Selection, "selection")
        if self.execution is not None:
            # Local import avoids a module cycle: capability_execution imports
            # the state records in this module to build one transition.
            from radhanite.capability_execution import ExecutionResult

            if type(self.execution) is not ExecutionResult:
                raise TypeError(
                    "execution must be exactly ExecutionResult or None, got "
                    f"{type(self.execution).__name__}. Arbitrary payloads, "
                    "RunState, RunSnapshot and subclasses are not execution "
                    "results — TASK-007 PR B."
                )


@refuse_rehydration
@dataclass(frozen=True, slots=True)
class RunState:
    """The state a capability run carries — TASK-007 §3.

    Immutable per transition: an iteration produces a **new** state rather than
    mutating this one.

    **Every construction is validated — `CODEX-PR030-01`.** `begin_run` is a
    convenience that derives `total_spend` from the budgets; it is not a
    privileged entrance. The invariants live in `__post_init__`, so calling
    `RunState(...)` directly enforces exactly the same ones.

    **`task_state` is opaque but not aliased — `CODEX-PR030-02`.** It is frozen
    structurally on the way in and never interpreted. A caller may therefore
    hand in anything immutable, or any container of immutable things; a mutable
    object the caller keeps hold of is **refused**, not stored.

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

    def __post_init__(self) -> None:
        _normalise(self)
        object.__setattr__(self, "history", _checked_history(self.history))

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

    This is the *convenient* path, not the *safe* one: `RunState` validates
    itself, so constructing one directly is equally safe and merely requires
    stating the spend. `CODEX-PR030-01`.

    >>> run = begin_run(
    ...     task_value=Money("100.00"), initial_budget=Money("10.00"),
    ...     remaining_budget=Money("10.00"), policy=RunPolicy(max_capability_steps=2),
    ...     task_state=None, current_success_probability=Probability("0.5"),
    ... )
    >>> str(run.total_spend)
    '$0.00'
    """
    # The only check here, because `total_spend` is derived by subtraction and
    # the subtraction has to happen before `RunState` can see the result.
    # Everything else — bounds, the ledger identity, the step count, the
    # status, the consumed identifiers, the opaque state — is enforced by
    # `RunState.__post_init__`, which no caller can skip.
    for label, amount in (
        ("initial_budget", initial_budget),
        ("remaining_budget", remaining_budget),
    ):
        _exactly(amount, Money, f"{label} (total_spend is derived from it)")

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
        # Exact `str`, not "string-like": a str subclass is a perfectly good
        # place to keep a list, and the identifier is retained in the record.
        _exactly(consumed_id, str, "each consumed candidate identifier")
    return tuple(sorted(set(consumed_candidate_ids)))


def _checked_count(value: int) -> int:
    if type(value) is not int:
        # Exact, which is also what excludes bool: `True` is an `int` by
        # inheritance and would otherwise pass as a count of one.
        raise TypeError(
            f"capability_step_count must be exactly a whole number, got "
            f"{type(value).__name__}."
        )
    if value < 0:
        raise ValueError(
            f"capability_step_count cannot be negative, got {value}."
        )
    return value
