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


class OpaqueState:
    """Something TASK-007 must transport without understanding."""

    def __init__(self, marker="baseline"):
        self.marker = marker


def a_run(**overrides) -> RunState:
    arguments = {
        "task_value": Money("50000.00"),
        "initial_budget": Money("250.00"),
        "remaining_budget": Money("250.00"),
        "policy": RunPolicy(max_capability_steps=4),
        "task_state": OpaqueState(),
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
    def test_it_is_stored_exactly_as_given(self) -> None:
        state = OpaqueState("evidence-so-far")
        run = a_run(task_state=state)
        self.assertIs(run.task_state, state)

    def test_any_object_is_accepted(self) -> None:
        for state in (None, 42, "text", {"k": "v"}, [1, 2], OpaqueState()):
            self.assertIs(a_run(task_state=state).task_state, state)

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

        run = a_run(task_state=Explodes())
        run.snapshot()


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
        self.assertIs(s.task_state, run.task_state)
        self.assertIs(s.status, run.status)

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
