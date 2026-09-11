"""The state a capability run carries, and the snapshots that audit it.

TASK-007 §3. This is the state model only — no execution, no transitions, no
classification, no loop.
"""

import doctest
import unittest
from decimal import Decimal

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
