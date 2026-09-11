"""The state a capability run carries, and the snapshots that audit it.

TASK-007 §3. This is the state model only — no execution, no transitions, no
classification, no loop.
"""

import dataclasses
import doctest
import unittest
from decimal import Decimal
from enum import Enum
from types import MappingProxyType

from radhanite import runstate as runstate_module
from radhanite.money import Money
from radhanite.policy import RunPolicy
from radhanite.probability import Probability
from radhanite.runstate import RunSnapshot, RunState, RunStatus, TransitionRecord, begin_run
from radhanite.selection import Selection, SelectionOutcome


def a_selection() -> Selection:
    """A real STOP decision, so a transition test cannot pass for the wrong reason."""
    return Selection(
        outcome=SelectionOutcome.STOP,
        reason="no candidates were offered",
        selected=None,
        assessments=(),
        current_success_probability=Probability("0.20"),
        task_value=Money("50000.00"),
        remaining_budget=Money("250.00"),
        consumed_candidate_ids=(),
        capability_step_count=0,
        max_capability_steps=4,
    )


class ArbitraryObject:
    """A mutable object a caller keeps hold of.

    Before `CODEX-PR030-02` this was stored by reference. It is now refused:
    TASK-007 may not interpret opaque state, and may not alias it either.
    """

    def __init__(self, marker="baseline"):
        self.marker = marker


def a_run(**overrides) -> RunState:
    arguments = {
        "task_value": Money("50000.00"),
        "initial_budget": Money("250.00"),
        "remaining_budget": Money("250.00"),
        "policy": RunPolicy(max_capability_steps=4),
        "task_state": {"marker": "baseline"},
        "current_success_probability": Probability("0.20"),
    }
    arguments.update(overrides)
    return begin_run(**arguments)


class InitialisationTests(unittest.TestCase):
    def test_a_fresh_run_has_spent_nothing(self) -> None:
        run = a_run()
        self.assertEqual(run.total_spend, Money("0.00"))
        self.assertEqual(run.remaining_budget, Money("250.00"))
        self.assertEqual(run.capability_step_count, 0)
        self.assertEqual(run.consumed_candidate_ids, ())
        self.assertEqual(run.history, ())
        self.assertIs(run.status, RunStatus.RUNNING)

    def test_baseline_spend_initialises_the_ledger(self) -> None:
        # §3.2: remaining_budget may already be lower on entry.
        run = a_run(remaining_budget=Money("180.00"))
        self.assertEqual(run.total_spend, Money("70.00"))

    def test_nothing_remaining_means_everything_spent(self) -> None:
        run = a_run(remaining_budget=Money("0.00"))
        self.assertEqual(run.total_spend, Money("250.00"))

    def test_the_ledger_balances(self) -> None:
        for remaining in ("250.00", "180.00", "0.01", "0.00"):
            run = a_run(remaining_budget=Money(remaining))
            self.assertEqual(
                run.total_spend + run.remaining_budget, run.initial_budget
            )

    def test_more_remaining_than_the_budget_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            a_run(remaining_budget=Money("250.01"))

    def test_a_negative_remaining_budget_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            a_run(remaining_budget=Money("-0.01"))

    def test_a_negative_initial_budget_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            a_run(initial_budget=Money("-1.00"), remaining_budget=Money("-1.00"))

    def test_money_must_be_money(self) -> None:
        for field in ("task_value", "initial_budget", "remaining_budget"):
            with self.assertRaises(TypeError):
                a_run(**{field: Decimal("10.00")})

    def test_the_probability_must_be_a_probability(self) -> None:
        with self.assertRaises(TypeError):
            a_run(current_success_probability=Decimal("0.20"))

    def test_the_policy_must_be_a_run_policy(self) -> None:
        with self.assertRaises(TypeError):
            a_run(policy=4)

    def test_no_float_reaches_the_ledger(self) -> None:
        run = a_run(remaining_budget=Money("180.00"))
        for figure in (run.initial_budget, run.remaining_budget, run.total_spend,
                       run.task_value):
            self.assertIsInstance(figure, Money)
            self.assertNotIsInstance(figure, float)

    def test_arguments_are_keyword_only(self) -> None:
        with self.assertRaises(TypeError):
            begin_run(Money("50000.00"), Money("250.00"), Money("250.00"))


class StepCountTests(unittest.TestCase):
    def test_a_run_may_start_part_way_through(self) -> None:
        self.assertEqual(a_run(capability_step_count=2).capability_step_count, 2)

    def test_a_negative_step_count_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            a_run(capability_step_count=-1)

    def test_bool_is_refused_as_a_step_count(self) -> None:
        # True == 1, and a count of "True" is a caller error.
        for wrong in (True, False):
            with self.assertRaises(TypeError):
                a_run(capability_step_count=wrong)

    def test_non_integers_are_refused(self) -> None:
        for wrong in (1.0, Decimal("1"), "1", None):
            with self.assertRaises(TypeError):
                a_run(capability_step_count=wrong)

    def test_the_ceiling_comes_from_the_policy(self) -> None:
        run = a_run(policy=RunPolicy(max_capability_steps=7))
        self.assertEqual(run.max_capability_steps, 7)

    def test_a_zero_step_policy_is_valid_state(self) -> None:
        # PR A models state; it does not classify a terminal condition.
        run = a_run(policy=RunPolicy(max_capability_steps=0))
        self.assertEqual(run.max_capability_steps, 0)
        self.assertIs(run.status, RunStatus.RUNNING)


class ConsumedIdentifierTests(unittest.TestCase):
    def test_they_are_stored_sorted_and_deduplicated(self) -> None:
        run = a_run(consumed_candidate_ids=["z", "a", "a", "m"])
        self.assertEqual(run.consumed_candidate_ids, ("a", "m", "z"))

    def test_a_set_normalises_to_the_same_deterministic_tuple(self) -> None:
        self.assertEqual(
            a_run(consumed_candidate_ids={"c", "a", "b"}).consumed_candidate_ids,
            ("a", "b", "c"),
        )

    def test_caller_mutation_afterwards_changes_nothing(self) -> None:
        supplied = ["a"]
        run = a_run(consumed_candidate_ids=supplied)
        supplied.append("b")
        self.assertEqual(run.consumed_candidate_ids, ("a",))

    def test_a_bare_string_is_refused(self) -> None:
        # `"a" in "abc"` is a substring test.
        with self.assertRaises(TypeError):
            a_run(consumed_candidate_ids="abc")

    def test_members_must_be_identifiers(self) -> None:
        with self.assertRaises(TypeError):
            a_run(consumed_candidate_ids=[1])

    def test_they_are_independent_of_any_offer(self) -> None:
        # §2.5a: consumed identifiers are run state, not offer state.
        run = a_run(consumed_candidate_ids=["bought-earlier"])
        self.assertIn("bought-earlier", run.consumed_candidate_ids)


class OpaqueTaskStateTests(unittest.TestCase):
    def test_its_value_is_preserved_exactly(self) -> None:
        run = a_run(task_state={"evidence": ["so-far"]})
        self.assertEqual(run.task_state, {"evidence": ("so-far",)})

    def test_immutable_values_and_containers_of_them_are_accepted(self) -> None:
        for state in (None, 42, "text", {"k": "v"}, [1, 2]):
            a_run(task_state=state)

    def test_a_mutable_object_the_caller_keeps_is_refused(self) -> None:
        # CODEX-PR030-02. Accepting it would let the caller rewrite history.
        with self.assertRaises(TypeError):
            a_run(task_state=ArbitraryObject())

    def test_nothing_inspects_it(self) -> None:
        class Explodes:
            def __getattr__(self, name):
                raise AssertionError(f"task_state was inspected: {name}")

            def __len__(self):
                raise AssertionError("task_state was inspected: __len__")

            def __iter__(self):
                raise AssertionError("task_state was inspected: __iter__")

            def __eq__(self, other):
                raise AssertionError("task_state was inspected: __eq__")

            def __hash__(self):
                raise AssertionError("task_state was inspected: __hash__")

        # Refusal is decided from the object's *type*, so even an object that
        # detonates on every read is refused without being read.
        with self.assertRaises(TypeError):
            a_run(task_state=Explodes())


class SnapshotTests(unittest.TestCase):
    def test_it_carries_every_field_except_history(self) -> None:
        expected = {
            "task_value", "initial_budget", "policy", "task_state",
            "current_success_probability", "remaining_budget", "total_spend",
            "consumed_candidate_ids", "capability_step_count", "status",
        }
        self.assertEqual(set(RunSnapshot.__dataclass_fields__), expected)

    def test_it_has_no_history_field(self) -> None:
        self.assertNotIn("history", RunSnapshot.__dataclass_fields__)
        self.assertFalse(hasattr(a_run().snapshot(), "history"))

    def test_the_values_match_the_run(self) -> None:
        run = a_run(remaining_budget=Money("180.00"),
                    consumed_candidate_ids=["a"], capability_step_count=1)
        s = run.snapshot()
        self.assertEqual(s.task_value, run.task_value)
        self.assertEqual(s.initial_budget, run.initial_budget)
        self.assertEqual(s.remaining_budget, run.remaining_budget)
        self.assertEqual(s.total_spend, run.total_spend)
        self.assertEqual(s.consumed_candidate_ids, run.consumed_candidate_ids)
        self.assertEqual(s.capability_step_count, run.capability_step_count)
        self.assertIs(s.policy, run.policy)
        self.assertIs(s.status, run.status)
        # Equal, not identical: a snapshot freezes opaque state on the way in
        # like everything else does, so it holds its own frozen equivalent
        # rather than sharing one object with the run (CODEX-PR030-02).
        self.assertEqual(s.task_state, run.task_state)

    def test_taking_one_does_not_mutate_the_run(self) -> None:
        run = a_run(remaining_budget=Money("180.00"), consumed_candidate_ids=["a"])
        before = (run.remaining_budget, run.total_spend, run.consumed_candidate_ids,
                  run.capability_step_count, run.status, run.history)
        run.snapshot()
        self.assertEqual(
            (run.remaining_budget, run.total_spend, run.consumed_candidate_ids,
             run.capability_step_count, run.status, run.history),
            before,
        )

    def test_it_is_immutable(self) -> None:
        s = a_run().snapshot()
        with self.assertRaises(Exception):
            s.total_spend = Money("1.00")
        with self.assertRaises(TypeError):
            s.__setstate__({"total_spend": Money("1.00")})
        self.assertFalse(hasattr(s, "__dict__"))

    def test_consumed_identifiers_cannot_be_appended_to(self) -> None:
        with self.assertRaises(AttributeError):
            a_run(consumed_candidate_ids=["a"]).snapshot().consumed_candidate_ids.append("b")

    def test_two_snapshots_of_one_run_are_equal(self) -> None:
        run = a_run(task_state=None)
        self.assertEqual(run.snapshot(), run.snapshot())


class NonRecursionTests(unittest.TestCase):
    """§3.3 — history holds snapshots; a snapshot never holds history."""

    def test_a_transition_record_holds_snapshots(self) -> None:
        self.assertIn("before", TransitionRecord.__dataclass_fields__)
        self.assertIn("after", TransitionRecord.__dataclass_fields__)

    def test_no_snapshot_field_can_carry_history(self) -> None:
        for name in RunSnapshot.__dataclass_fields__:
            self.assertNotIn("history", name)
            self.assertNotIn("transition", name)

    def test_walking_a_snapshot_terminates(self) -> None:
        # Structural proof: a snapshot exposes nothing that leads back to a run
        # or a history, so a reader following its fields cannot loop.
        s = a_run().snapshot()
        for name in RunSnapshot.__dataclass_fields__:
            value = getattr(s, name)
            self.assertNotIsInstance(value, (RunState, TransitionRecord))

    def test_the_run_holds_history_and_the_snapshot_does_not(self) -> None:
        run = a_run()
        self.assertIn("history", RunState.__dataclass_fields__)
        self.assertNotIn("history", RunSnapshot.__dataclass_fields__)
        self.assertEqual(run.history, ())


class RunStateShapeTests(unittest.TestCase):
    def test_the_fields_are_exactly_those_the_specification_lists(self) -> None:
        self.assertEqual(
            set(RunState.__dataclass_fields__),
            {
                "task_value", "initial_budget", "policy", "task_state",
                "current_success_probability", "remaining_budget", "total_spend",
                "consumed_candidate_ids", "capability_step_count", "status",
                "history",
            },
        )

    def test_no_provider_or_payment_field_exists(self) -> None:
        for name in set(RunState.__dataclass_fields__) | set(RunSnapshot.__dataclass_fields__):
            for forbidden in ("provider", "network", "chain", "wallet", "payment",
                              "source", "endpoint", "marketplace", "retry"):
                self.assertNotIn(forbidden, name)

    def test_no_execution_result_field_exists_yet(self) -> None:
        for absent in ("execution_result", "committed_cost", "last_result"):
            self.assertNotIn(absent, RunState.__dataclass_fields__)

    def test_the_run_is_immutable(self) -> None:
        run = a_run()
        with self.assertRaises(Exception):
            run.total_spend = Money("1.00")
        self.assertFalse(hasattr(run, "__dict__"))

    def test_the_module_names_no_provider(self) -> None:
        import pathlib
        import re

        text = pathlib.Path(runstate_module.__file__).read_text().lower()
        for forbidden in ("hedera", "circle", "arc", "tavily", "blockrun",
                          "openrouter", "x402", "wallet", "usdc", "marketplace"):
            self.assertIsNone(re.search(rf"\b{forbidden}\b", text))


class NothingElseTests(unittest.TestCase):
    def test_no_execution_selection_or_classification(self) -> None:
        exported = set(vars(runstate_module))
        for absent in ("execute", "select", "select_capability", "assess",
                       "acquire", "classify", "terminate", "advance", "step"):
            self.assertNotIn(absent, exported)

    def test_the_run_offers_no_transition_methods(self) -> None:
        for absent in ("advance", "consume", "commit", "execute", "increment",
                       "with_execution", "next_state"):
            self.assertFalse(hasattr(RunState, absent), absent)


class DoctestTests(unittest.TestCase):
    def test_module_doctests_pass(self) -> None:
        results = doctest.testmod(runstate_module, verbose=False)
        self.assertEqual(results.failed, 0)
        self.assertGreater(results.attempted, 0)


if __name__ == "__main__":
    unittest.main()


# ── CODEX-PR030-01 ─────────────────────────────────────────────────────────

class DirectConstructionTests(unittest.TestCase):
    """Invariants lived in begin_run(); RunState was publicly constructible.

    One safe path and one unsafe path is one unsafe path.
    """

    def _fields(self, **overrides):
        fields = {
            "task_value": Money("50000.00"),
            "initial_budget": Money("250.00"),
            "policy": RunPolicy(max_capability_steps=4),
            "task_state": None,
            "current_success_probability": Probability("0.20"),
            "remaining_budget": Money("250.00"),
            "total_spend": Money("0.00"),
            "consumed_candidate_ids": (),
            "capability_step_count": 0,
            "status": RunStatus.RUNNING,
            "history": (),
        }
        fields.update(overrides)
        return fields

    def test_a_valid_direct_construction_succeeds(self) -> None:
        run = RunState(**self._fields())
        self.assertEqual(run.total_spend, Money("0.00"))

    def test_an_unbalanced_ledger_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            RunState(**self._fields(
                initial_budget=Money("10.00"),
                remaining_budget=Money("10.00"),
                total_spend=Money("999.00"),
            ))

    def test_spend_exceeding_the_budget_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            RunState(**self._fields(
                initial_budget=Money("10.00"),
                remaining_budget=Money("-989.00"),
                total_spend=Money("999.00"),
            ))

    def test_a_ledger_that_does_not_add_up_is_rejected(self) -> None:
        # Both figures are individually plausible — non-negative and within
        # the budget — and together they are still wrong. Only the identity
        # catches this, which is why the bounds tests do not cover it.
        for remaining, spend in (("100.00", "50.00"), ("100.00", "200.00")):
            with self.assertRaises(ValueError):
                RunState(**self._fields(
                    initial_budget=Money("250.00"),
                    remaining_budget=Money(remaining),
                    total_spend=Money(spend),
                ))

    def test_negative_spend_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            RunState(**self._fields(
                remaining_budget=Money("250.01"), total_spend=Money("-0.01")
            ))

    def test_a_negative_step_count_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            RunState(**self._fields(capability_step_count=-1))

    def test_bool_is_rejected_as_a_step_count(self) -> None:
        with self.assertRaises(TypeError):
            RunState(**self._fields(capability_step_count=True))

    def test_an_invalid_status_is_rejected(self) -> None:
        for wrong in ("running", 0, None):
            with self.assertRaises(TypeError):
                RunState(**self._fields(status=wrong))

    def test_a_mutable_consumed_id_input_is_detached_and_frozen(self) -> None:
        supplied = ["b", "a", "a"]
        run = RunState(**self._fields(consumed_candidate_ids=supplied))
        supplied.append("z")
        self.assertEqual(run.consumed_candidate_ids, ("a", "b"))
        self.assertIsInstance(run.consumed_candidate_ids, tuple)

    def test_a_mutable_history_input_is_detached_and_frozen(self) -> None:
        supplied = []
        run = RunState(**self._fields(history=supplied))
        supplied.append("not-a-transition")
        self.assertEqual(run.history, ())
        self.assertIsInstance(run.history, tuple)

    def test_history_members_must_be_transition_records(self) -> None:
        with self.assertRaises(TypeError):
            RunState(**self._fields(history=["not-a-transition"]))

    def test_begin_run_produces_the_same_validated_state(self) -> None:
        direct = RunState(**self._fields(
            remaining_budget=Money("180.00"), total_spend=Money("70.00")
        ))
        via_begin_run = begin_run(
            task_value=Money("50000.00"), initial_budget=Money("250.00"),
            remaining_budget=Money("180.00"), policy=direct.policy,
            task_state=None, current_success_probability=Probability("0.20"),
        )
        self.assertEqual(direct.total_spend, via_begin_run.total_spend)
        self.assertEqual(direct.remaining_budget, via_begin_run.remaining_budget)
        self.assertEqual(
            direct.consumed_candidate_ids, via_begin_run.consumed_candidate_ids
        )


# ── CODEX-PR030-02 ─────────────────────────────────────────────────────────

class TaskStateIsDetachedTests(unittest.TestCase):
    """Opacity forbids interpreting the state. It does not permit aliasing it."""

    def test_a_mutated_dict_does_not_change_the_stored_state(self) -> None:
        supplied = {"evidence": "none"}
        run = a_run(task_state=supplied)
        supplied["evidence"] = "tampered"
        self.assertEqual(run.task_state["evidence"], "none")

    def test_a_mutated_nested_structure_does_not_change_it(self) -> None:
        supplied = {"evidence": [{"claim": "a"}]}
        run = a_run(task_state=supplied)
        supplied["evidence"][0]["claim"] = "tampered"
        supplied["evidence"].append({"claim": "extra"})
        self.assertEqual(len(run.task_state["evidence"]), 1)
        self.assertEqual(run.task_state["evidence"][0]["claim"], "a")

    def test_an_existing_snapshot_does_not_change(self) -> None:
        supplied = {"evidence": ["a"]}
        run = a_run(task_state=supplied)
        snap = run.snapshot()
        supplied["evidence"].append("b")
        self.assertEqual(len(snap.task_state["evidence"]), 1)

    def test_the_stored_state_cannot_be_mutated_directly(self) -> None:
        run = a_run(task_state={"evidence": ["a"]})
        with self.assertRaises(Exception):
            run.task_state["evidence"] = ["tampered"]
        with self.assertRaises(AttributeError):
            run.task_state["evidence"].append("b")

    def test_a_caller_cannot_inject_a_back_reference_afterwards(self) -> None:
        supplied = {"evidence": []}
        run = a_run(task_state=supplied)
        snap = run.snapshot()
        supplied["self"] = snap          # the caller tries to make it recursive
        supplied["run"] = run
        self.assertNotIn("self", run.task_state)
        self.assertNotIn("run", snap.task_state)

    def test_a_cyclic_opaque_input_is_rejected_deterministically(self) -> None:
        cyclic = {"evidence": []}
        cyclic["evidence"].append(cyclic)
        with self.assertRaises(ValueError):
            a_run(task_state=cyclic)

    def test_immutable_opaque_values_still_work(self) -> None:
        for state in (None, 42, "text", (1, 2), frozenset({"a"}),
                      Money("1.00"), Probability("0.5"), Decimal("1.5")):
            self.assertEqual(a_run(task_state=state).task_state, state)

    def test_containers_are_frozen_deterministically(self) -> None:
        run = a_run(task_state={"list": [1, 2], "set": {3}, "nested": {"k": [4]}})
        self.assertIsInstance(run.task_state["list"], tuple)
        self.assertIsInstance(run.task_state["set"], frozenset)
        self.assertIsInstance(run.task_state["nested"]["k"], tuple)

    def test_an_unfreezable_object_is_refused_rather_than_aliased(self) -> None:
        class Arbitrary:
            def __init__(self):
                self.mutable = []

        with self.assertRaises(TypeError):
            a_run(task_state=Arbitrary())

    def test_nothing_interprets_the_state(self) -> None:
        # Freezing is structural — isinstance checks on container types — and
        # must not read keys, values or attributes for meaning.
        run = a_run(task_state={"opportunity": "x", "evidence": [1]})
        self.assertEqual(set(run.task_state), {"opportunity", "evidence"})


class SiblingRecordConstructionTests(unittest.TestCase):
    """CODEX-PR030-01 applied to the module's other two public records.

    `RunSnapshot` and `TransitionRecord` are exported and constructible too,
    and a snapshot is the object an auditor actually reads — leaving either of
    them unvalidated would put the same hole one field further out.
    """

    def test_a_snapshot_freezes_its_own_opaque_state(self) -> None:
        supplied = {"evidence": ["a"]}
        snap = a_run(task_state=None).snapshot()
        rebuilt = RunSnapshot(**{
            **{name: getattr(snap, name) for name in RunSnapshot.__dataclass_fields__},
            "task_state": supplied,
        })
        supplied["evidence"].append("b")
        self.assertEqual(len(rebuilt.task_state["evidence"]), 1)

    def test_a_snapshot_rejects_an_incoherent_ledger(self) -> None:
        snap = a_run().snapshot()
        fields = {name: getattr(snap, name) for name in RunSnapshot.__dataclass_fields__}
        with self.assertRaises(ValueError):
            RunSnapshot(**{**fields, "total_spend": Money("40.00")})

    def test_a_transition_must_hold_snapshots_not_runs(self) -> None:
        run = a_run()
        snap = run.snapshot()
        # A genuine Selection, so the only thing wrong with each record below
        # is the field under test.
        TransitionRecord(before=snap, selection=a_selection(), after=snap)
        with self.assertRaises(TypeError):
            TransitionRecord(before=run, selection=a_selection(), after=snap)
        with self.assertRaises(TypeError):
            TransitionRecord(before=snap, selection=a_selection(), after=run)

    def test_a_transition_must_hold_a_selection(self) -> None:
        snap = a_run().snapshot()
        with self.assertRaises(TypeError):
            TransitionRecord(before=snap, selection="chose-something", after=snap)


class RecursiveWalkTests(unittest.TestCase):
    """§3.3 proved by walking, not by reading field names."""

    def _reachable(self, value, seen=None):
        seen = seen if seen is not None else set()
        if id(value) in seen:
            return
        seen.add(id(value))
        yield value
        if isinstance(value, (RunState, RunSnapshot, TransitionRecord)):
            for name in value.__dataclass_fields__:
                yield from self._reachable(getattr(value, name), seen)
        elif isinstance(value, (tuple, list, frozenset, set)):
            for item in value:
                yield from self._reachable(item, seen)
        elif hasattr(value, "items"):
            for key, item in value.items():
                yield from self._reachable(key, seen)
                yield from self._reachable(item, seen)

    def test_nothing_run_shaped_is_reachable_from_a_snapshot(self) -> None:
        supplied = {"evidence": [{"deep": ["deeper"]}]}
        run = a_run(task_state=supplied)
        snap = run.snapshot()
        for value in self._reachable(snap):
            if value is snap:
                continue
            self.assertNotIsInstance(value, (RunState, RunSnapshot, TransitionRecord))

    def test_a_caller_cannot_make_a_snapshot_reach_itself(self) -> None:
        supplied = {"evidence": []}
        run = a_run(task_state=supplied)
        snap = run.snapshot()
        supplied["loop"] = snap
        reachable = list(self._reachable(snap))
        self.assertEqual(sum(1 for v in reachable if v is snap), 1)


# ── CODEX-PR030-01, remaining: the execution escape hatch ──────────────────

class ExecutionPlaceholderTests(unittest.TestCase):
    """`execution` accepted anything, which reopened every hole beside it.

    A mutable payload is a live alias inside history; a `RunState` payload puts
    history inside history. PR A implements no execution and no caller needs a
    payload, so the smallest safe contract is that there isn't one yet.
    """

    def _transition(self, **overrides):
        snap = a_run().snapshot()
        fields = {"before": snap, "selection": a_selection(), "after": snap}
        fields.update(overrides)
        return TransitionRecord(**fields)

    def test_none_is_accepted(self) -> None:
        self.assertIsNone(self._transition().execution)
        self.assertIsNone(self._transition(execution=None).execution)

    def test_a_mutable_payload_is_rejected(self) -> None:
        for payload in ([], {}, {"cost": "0.40"}, ["committed"], set(), bytearray()):
            with self.assertRaises(ValueError):
                self._transition(execution=payload)

    def test_a_run_state_as_execution_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self._transition(execution=a_run())

    def test_a_snapshot_as_execution_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self._transition(execution=a_run().snapshot())

    def test_a_transition_as_execution_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self._transition(execution=self._transition())

    def test_even_an_immutable_payload_is_rejected(self) -> None:
        # Not "freeze whatever arrives" — PR A has no authorized execution
        # result type at all, and inventing one here would be PR B's schema
        # arriving early under a different name.
        for payload in ("committed", 1, Money("0.40"), ("committed",)):
            with self.assertRaises(ValueError):
                self._transition(execution=payload)

    def test_caller_mutation_cannot_reach_an_existing_history_record(self) -> None:
        payload = {"committed_cost": "0.40"}
        with self.assertRaises(ValueError):
            self._transition(execution=payload)
        payload["committed_cost"] = "999.00"
        # Nothing retained it, so there is nothing for the mutation to reach.
        run = a_run(consumed_candidate_ids=["x"])
        run = RunState(**{
            **{n: getattr(run, n) for n in RunState.__dataclass_fields__},
            "history": (self._transition(),),
        })
        self.assertIsNone(run.history[0].execution)


# ── CODEX-PR030-02, remaining: isinstance trusted subclasses ───────────────

class _IntWithBaggage(int):
    def __init__(self, *_):
        self.baggage = []


class _StrWithBaggage(str):
    def __init__(self, *_):
        self.baggage = []


class _FloatWithBaggage(float):
    def __init__(self, *_):
        self.baggage = []


class _BytesWithBaggage(bytes):
    def __init__(self, *_):
        self.baggage = []


class _DecimalWithBaggage(Decimal):
    def __init__(self, *_):
        self.baggage = []


class _MutableValued(Enum):
    LEDGER = ["entry"]


class _WithExtraAttribute(Enum):
    A = "a"

    def __init__(self, _value):
        self.baggage = []


class ExactTypeFreezeTests(unittest.TestCase):
    """`isinstance` trusts subclasses, and a subclass can carry a mutable payload.

    `_IntWithBaggage(1)` passes `isinstance(x, int)` and is stored unchanged —
    along with the list hanging off it, which the caller still owns.
    """

    def test_a_scalar_subclass_carrying_a_mutable_payload_is_rejected(self) -> None:
        for smuggler in (_IntWithBaggage(1), _StrWithBaggage("x"),
                         _FloatWithBaggage(1.5), _BytesWithBaggage(b"x"),
                         _DecimalWithBaggage("1.5")):
            with self.assertRaises(TypeError):
                a_run(task_state=smuggler)

    def test_a_scalar_subclass_is_rejected_inside_a_container_too(self) -> None:
        with self.assertRaises(TypeError):
            a_run(task_state={"evidence": [_IntWithBaggage(1)]})

    def test_an_enum_member_with_a_mutable_value_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            a_run(task_state=_MutableValued.LEDGER)

    def test_an_enum_member_with_a_mutable_attribute_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            a_run(task_state=_WithExtraAttribute.A)

    def test_no_enum_member_is_blanket_accepted(self) -> None:
        # Including this module's own, which is safe — the rule is "no arbitrary
        # Enum", and narrowing it to specific authorized types is PR B's call.
        with self.assertRaises(TypeError):
            a_run(task_state=RunStatus.RUNNING)

    def test_exact_builtin_scalars_are_still_accepted(self) -> None:
        for value in (None, True, False, 0, 42, -1, 1.5, 2j, "text", b"bytes",
                      Decimal("1.5")):
            self.assertEqual(a_run(task_state=value).task_state, value)

    def test_exact_project_value_types_are_still_accepted(self) -> None:
        for value in (Money("1.00"), Probability("0.5"),
                      RunPolicy(max_capability_steps=3)):
            self.assertEqual(a_run(task_state=value).task_state, value)

    def test_a_project_value_subclass_is_not_trusted(self) -> None:
        class _MoneyWithBaggage(Money):
            pass

        with self.assertRaises(TypeError):
            a_run(task_state=_MoneyWithBaggage("1.00"))

    def test_nested_ordinary_containers_still_freeze(self) -> None:
        run = a_run(task_state={"a": [1, {"b": {2}}], "c": (3,), "d": frozenset({4})})
        self.assertIsInstance(run.task_state["a"], tuple)
        self.assertIsInstance(run.task_state["a"][1]["b"], frozenset)
        self.assertIsInstance(run.task_state["c"], tuple)
        self.assertIsInstance(run.task_state["d"], frozenset)

    def test_a_string_subclass_is_not_silently_split_into_characters(self) -> None:
        # A str subclass is a Sequence. Converting it would turn "abc" into
        # ("a", "b", "c") and call that a faithful record.
        with self.assertRaises(TypeError):
            a_run(task_state=_StrWithBaggage("abc"))

    def test_cyclic_input_still_fails_deterministically(self) -> None:
        cyclic = {"evidence": []}
        cyclic["evidence"].append(cyclic)
        for _ in range(3):
            with self.assertRaises(ValueError):
                a_run(task_state=cyclic)

    def test_a_frozen_state_can_be_refrozen(self) -> None:
        # `snapshot()` re-runs the freeze over already-frozen state, so the
        # exact-type rule has to admit its own output.
        run = a_run(task_state={"a": [1], "b": {2}, "c": "s"})
        self.assertEqual(run.snapshot().task_state, run.task_state)


class TransitiveImmutabilityAuditTests(unittest.TestCase):
    """One walk over everything reachable, rather than a rule per field."""

    _SAFE_LEAVES = (
        type(None), bool, int, float, complex, str, bytes, Decimal,
        Money, Probability, RunPolicy, RunStatus, SelectionOutcome,
    )
    _MUTABLE = (list, dict, set, bytearray)

    def _audit(self, value, seen=None, path="root"):
        """Yield (path, complaint) for everything reachable that is not safe."""
        seen = set() if seen is None else seen
        if id(value) in seen:
            yield path, f"cycle back to a {type(value).__name__}"
            return
        seen = seen | {id(value)}

        if isinstance(value, self._MUTABLE):
            yield path, f"mutable {type(value).__name__}"
            return
        if type(value) in self._SAFE_LEAVES:
            return
        if hasattr(value, "__dict__"):
            yield path, f"{type(value).__name__} carries a mutable __dict__"
            return

        if hasattr(value, "__dataclass_fields__"):
            for name in value.__dataclass_fields__:
                yield from self._audit(getattr(value, name), seen, f"{path}.{name}")
        elif isinstance(value, (tuple, frozenset)):
            for index, item in enumerate(value):
                yield from self._audit(item, seen, f"{path}[{index}]")
        elif isinstance(value, MappingProxyType):
            for key, item in value.items():
                yield from self._audit(key, seen, f"{path}.key({key!r})")
                yield from self._audit(item, seen, f"{path}[{key!r}]")
        else:
            yield path, f"unaudited {type(value).__name__}"

    def _run_with_history(self):
        run = a_run(task_state={"evidence": [{"claim": "a"}], "n": {1, 2}})
        snap = run.snapshot()
        record = TransitionRecord(before=snap, selection=a_selection(), after=snap)
        return RunState(**{
            **{n: getattr(run, n) for n in RunState.__dataclass_fields__},
            "history": (record,),
        })

    def test_nothing_mutable_is_reachable_from_a_run(self) -> None:
        self.assertEqual(list(self._audit(self._run_with_history())), [])

    def test_nothing_mutable_is_reachable_from_a_snapshot(self) -> None:
        self.assertEqual(list(self._audit(self._run_with_history().snapshot())), [])

    def test_no_run_state_is_reachable_from_history(self) -> None:
        run = self._run_with_history()
        for value in self._everything(run.history):
            self.assertNotIsInstance(value, RunState)

    def test_no_cycle_is_reachable(self) -> None:
        run = self._run_with_history()
        complaints = [c for _, c in self._audit(run) if "cycle" in c]
        self.assertEqual(complaints, [])

    def test_no_mutable_execution_payload_is_reachable(self) -> None:
        run = self._run_with_history()
        for record in run.history:
            self.assertIsNone(record.execution)
        self.assertEqual(
            [p for p, _ in self._audit(run) if ".execution" in p], []
        )

    def test_the_shapes_the_audit_forbids_cannot_be_constructed(self) -> None:
        # The walk proves a *valid* run is clean. This proves the invalid ones
        # never get built, which is the half a walk over good data cannot show.
        snap = a_run().snapshot()
        with self.assertRaises(ValueError):
            TransitionRecord(before=snap, selection=a_selection(), after=snap,
                             execution={"committed": ["0.40"]})
        with self.assertRaises(ValueError):
            TransitionRecord(before=snap, selection=a_selection(), after=snap,
                             execution=a_run())
        with self.assertRaises(TypeError):
            a_run(task_state={"smuggled": _IntWithBaggage(1)})

    def test_the_audit_would_catch_an_unvalidated_record(self) -> None:
        # Built behind the constructor's back, so the walk is tested against the
        # defect itself rather than against the guard that now prevents it.
        snap = a_run().snapshot()
        smuggled = TransitionRecord.__new__(TransitionRecord)
        for name, value in (("before", snap), ("selection", a_selection()),
                            ("after", snap), ("execution", {"live": ["alias"]})):
            object.__setattr__(smuggled, name, value)
        complaints = list(self._audit(smuggled))
        self.assertTrue(complaints)
        self.assertTrue(any(".execution" in path for path, _ in complaints))

    def test_the_audit_catches_what_it_claims_to(self) -> None:
        # The walker is a test fixture, so it needs its own proof: point it at
        # things that ARE unsafe and confirm it complains.
        mutable = ["live"]
        self.assertTrue(list(self._audit(mutable)))
        self.assertTrue(list(self._audit({"k": mutable})))
        self.assertTrue(list(self._audit((1, mutable))))
        self.assertTrue(list(self._audit(_IntWithBaggage(1))))
        cyclic = []
        cyclic.append(cyclic)
        self.assertTrue(list(self._audit((cyclic,))))

    def _everything(self, value, seen=None):
        seen = set() if seen is None else seen
        if id(value) in seen:
            return
        seen.add(id(value))
        yield value
        if hasattr(value, "__dataclass_fields__"):
            for name in value.__dataclass_fields__:
                yield from self._everything(getattr(value, name), seen)
        elif isinstance(value, (tuple, list, frozenset, set)):
            for item in value:
                yield from self._everything(item, seen)
        elif hasattr(value, "items"):
            for key, item in value.items():
                yield from self._everything(key, seen)
                yield from self._everything(item, seen)


# ── CODEX-PR030-01, remaining: subclasses smuggled into audit records ──────

@dataclasses.dataclass(frozen=True)
class _SnapshotWithBaggage(RunSnapshot):
    baggage: list = dataclasses.field(default_factory=list)


@dataclasses.dataclass(frozen=True)
class _TransitionWithBaggage(TransitionRecord):
    baggage: list = dataclasses.field(default_factory=list)


@dataclasses.dataclass(frozen=True)
class _SelectionWithBaggage(Selection):
    baggage: list = dataclasses.field(default_factory=list)


@dataclasses.dataclass(frozen=True)
class _MoneyWithBaggage(Money):
    baggage: list = dataclasses.field(default_factory=list)


class _StrIdentifier(str):
    """A candidate identifier that is also a place to keep mutable state."""

    def __init__(self, *_):
        self.baggage = []


class ExactAuditMemberTests(unittest.TestCase):
    """`isinstance` trusted subclasses of the frozen records themselves.

    A frozen dataclass subclass may add a field holding a list. The reference
    is frozen; the list is not. Accepted as a history member, it becomes
    caller-owned mutable state inside an audit record — the same defect as an
    aliased `task_state`, arriving through the type system instead of past it.
    """

    def _snapshot_fields(self, snap):
        return {n: getattr(snap, n) for n in RunSnapshot.__dataclass_fields__}

    def test_a_transition_subclass_is_refused_as_a_history_member(self) -> None:
        snap = a_run().snapshot()
        smuggler = _TransitionWithBaggage(
            before=snap, selection=a_selection(), after=snap
        )
        run = a_run()
        with self.assertRaises(TypeError):
            RunState(**{
                **{n: getattr(run, n) for n in RunState.__dataclass_fields__},
                "history": (smuggler,),
            })

    def test_a_snapshot_subclass_is_refused_inside_a_transition(self) -> None:
        snap = a_run().snapshot()
        smuggler = _SnapshotWithBaggage(**self._snapshot_fields(snap))
        for position in ("before", "after"):
            fields = {"before": snap, "selection": a_selection(), "after": snap}
            fields[position] = smuggler
            with self.assertRaises(TypeError):
                TransitionRecord(**fields)

    def test_a_selection_subclass_is_refused_inside_a_transition(self) -> None:
        snap = a_run().snapshot()
        real = a_selection()
        smuggler = _SelectionWithBaggage(
            **{n: getattr(real, n) for n in Selection.__dataclass_fields__}
        )
        with self.assertRaises(TypeError):
            TransitionRecord(before=snap, selection=smuggler, after=snap)

    def test_a_money_subclass_is_refused_as_an_amount(self) -> None:
        for field_name in ("task_value", "initial_budget", "remaining_budget"):
            with self.assertRaises(TypeError):
                a_run(**{field_name: _MoneyWithBaggage("1.00")})

    def test_the_exact_types_are_still_accepted(self) -> None:
        # The correction must cost nothing that currently works.
        snap = a_run().snapshot()
        record = TransitionRecord(before=snap, selection=a_selection(), after=snap)
        run = a_run()
        rebuilt = RunState(**{
            **{n: getattr(run, n) for n in RunState.__dataclass_fields__},
            "history": (record,),
        })
        self.assertEqual(rebuilt.history, (record,))
        self.assertIs(type(rebuilt.history[0]), TransitionRecord)

    def test_no_subclass_baggage_is_reachable_from_history(self) -> None:
        # The positive statement behind the three refusals above.
        snap = a_run().snapshot()
        smuggler = _TransitionWithBaggage(
            before=snap, selection=a_selection(), after=snap
        )
        smuggler.baggage.append("mutable")
        run = a_run()
        with self.assertRaises(TypeError):
            RunState(**{
                **{n: getattr(run, n) for n in RunState.__dataclass_fields__},
                "history": (smuggler,),
            })
        self.assertEqual(a_run().history, ())


class ExactConsumedIdentifierTests(unittest.TestCase):
    """`isinstance(x, str)` accepts a str subclass, which can hold state."""

    def test_a_plain_identifier_is_accepted(self) -> None:
        run = a_run(consumed_candidate_ids=["standard-review-001"])
        self.assertEqual(run.consumed_candidate_ids, ("standard-review-001",))
        self.assertIs(type(run.consumed_candidate_ids[0]), str)

    def test_a_stateful_str_subclass_is_refused(self) -> None:
        with self.assertRaises(TypeError):
            a_run(consumed_candidate_ids=[_StrIdentifier("quick-check-001")])

    def test_a_subclass_is_refused_even_alongside_plain_identifiers(self) -> None:
        with self.assertRaises(TypeError):
            a_run(consumed_candidate_ids=["a", _StrIdentifier("b"), "c"])

    def test_mutating_the_subclass_cannot_reach_a_recorded_identifier(self) -> None:
        smuggler = _StrIdentifier("quick-check-001")
        with self.assertRaises(TypeError):
            a_run(consumed_candidate_ids=[smuggler])
        smuggler.baggage.append("tampered")
        # Nothing retained it; the run that does record that identifier records
        # a plain string equal to it and shares nothing with it.
        run = a_run(consumed_candidate_ids=["quick-check-001"])
        self.assertEqual(run.consumed_candidate_ids, ("quick-check-001",))
        self.assertIsNot(run.consumed_candidate_ids[0], smuggler)

    def test_sorting_and_deduplication_are_unchanged(self) -> None:
        self.assertEqual(
            a_run(consumed_candidate_ids=["b", "a", "a", "c"]).consumed_candidate_ids,
            ("a", "b", "c"),
        )
        self.assertEqual(
            a_run(consumed_candidate_ids={"z", "y"}).consumed_candidate_ids,
            ("y", "z"),
        )

    def test_a_bare_string_is_still_refused_as_the_collection(self) -> None:
        with self.assertRaises(TypeError):
            a_run(consumed_candidate_ids="abc")


class SubclassInjectionAuditTests(TransitiveImmutabilityAuditTests):
    """Item 4 — the walker re-run against subclass injection specifically."""

    def test_the_constructors_reject_every_subclass_injection(self) -> None:
        snap = a_run().snapshot()
        real = a_selection()
        with self.assertRaises(TypeError):
            TransitionRecord(
                before=_SnapshotWithBaggage(**self._snapshot_fields(snap)),
                selection=real, after=snap,
            )
        with self.assertRaises(TypeError):
            TransitionRecord(
                before=snap,
                selection=_SelectionWithBaggage(
                    **{n: getattr(real, n) for n in Selection.__dataclass_fields__}
                ),
                after=snap,
            )
        with self.assertRaises(TypeError):
            a_run(consumed_candidate_ids=[_StrIdentifier("x")])

    def test_the_walker_still_catches_a_subclass_built_behind_the_api(self) -> None:
        snap = a_run().snapshot()
        smuggler = _TransitionWithBaggage(
            before=snap, selection=a_selection(), after=snap
        )
        smuggler.baggage.append("mutable")
        complaints = list(self._audit(smuggler))
        self.assertTrue(complaints)

    def test_valid_history_is_still_clean(self) -> None:
        self.assertEqual(list(self._audit(self._run_with_history())), [])

    def _snapshot_fields(self, snap):
        return {n: getattr(snap, n) for n in RunSnapshot.__dataclass_fields__}
