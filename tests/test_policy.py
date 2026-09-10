"""Run policy: a run states, explicitly, how many capabilities it may buy.

TASK-006 §2.5 C makes the step ceiling a termination safeguard and §2.2a makes
it authoritative run policy rather than a sixth user input. §5 forbids a default
that would make it optional, and forbids a literal ceiling in the selection
logic.
"""

import unittest
from decimal import Decimal

from radhanite.money import Money
from radhanite.policy import RunPolicy
from radhanite.probability import Probability


class RunPolicyTests(unittest.TestCase):
    def test_carries_the_ceiling(self) -> None:
        self.assertEqual(RunPolicy(max_capability_steps=4).max_capability_steps, 4)

    def test_the_ceiling_is_required(self) -> None:
        # A default would make a safety limit optional — TASK-006 §5.
        with self.assertRaises(TypeError):
            RunPolicy()

    def test_one_is_the_smallest_usable_policy(self) -> None:
        # §7: at least one step is needed for the two-tier scenarios to reproduce.
        self.assertEqual(RunPolicy(max_capability_steps=1).max_capability_steps, 1)

    def test_zero_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            RunPolicy(max_capability_steps=0)

    def test_negative_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            RunPolicy(max_capability_steps=-1)

    def test_bool_is_refused(self) -> None:
        # True == 1 in Python, and a policy of "True steps" is a caller error.
        for wrong in (True, False):
            with self.assertRaises(TypeError):
                RunPolicy(max_capability_steps=wrong)

    def test_non_integers_are_refused(self) -> None:
        for wrong in (4.0, Decimal("4"), "4", None, Money("4.00")):
            with self.assertRaises(TypeError):
                RunPolicy(max_capability_steps=wrong)


class ImmutabilityTests(unittest.TestCase):
    def test_ordinary_assignment_is_refused(self) -> None:
        policy = RunPolicy(max_capability_steps=4)
        with self.assertRaises(Exception):
            policy.max_capability_steps = 99

    def test_rehydration_is_refused(self) -> None:
        with self.assertRaises(TypeError):
            RunPolicy(max_capability_steps=4).__setstate__({"max_capability_steps": 99})

    def test_there_is_no_instance_dictionary(self) -> None:
        self.assertFalse(hasattr(RunPolicy(max_capability_steps=4), "__dict__"))


class ItReachesTheDecisionTests(unittest.TestCase):
    """The policy must be the source of the ceiling, not a decoration."""

    def test_the_policy_value_reaches_eligibility(self) -> None:
        from radhanite.capability import Candidate
        from radhanite.eligibility import Ineligibility, assess

        policy = RunPolicy(max_capability_steps=2)
        candidate = Candidate("c-1", Money("0.50"), Probability("0.80"))
        at_ceiling = assess(
            candidate=candidate,
            current_success_probability=Probability("0.50"),
            task_value=Money("20.00"),
            remaining_budget=Money("10.00"),
            capability_step_count=2,
            max_capability_steps=policy.max_capability_steps,
        )
        self.assertIn(Ineligibility.STEP_CEILING, at_ceiling.failed_conditions)

        below = assess(
            candidate=candidate,
            current_success_probability=Probability("0.50"),
            task_value=Money("20.00"),
            remaining_budget=Money("10.00"),
            capability_step_count=1,
            max_capability_steps=policy.max_capability_steps,
        )
        self.assertTrue(below.eligible)


class NoUniversalCeilingTests(unittest.TestCase):
    """TASK-006 §5: no default that makes the policy optional, and no literal
    ceiling in the logic. The demonstration's four is a setting, not a constant.

    Checked behaviourally rather than by scanning text: a doctest that calls a
    function with `max_capability_steps=4` is a call site, which is exactly what
    a caller is supposed to do, and a text scan that flagged it would be
    measuring the wrong thing.
    """

    def _parameter(self, function):
        import inspect

        return inspect.signature(function).parameters["max_capability_steps"]

    def test_eligibility_has_no_default_ceiling(self) -> None:
        import inspect

        from radhanite.eligibility import assess

        self.assertIs(self._parameter(assess).default, inspect.Parameter.empty)

    def test_selection_has_no_default_ceiling(self) -> None:
        import inspect

        from radhanite.selection import select_capability

        self.assertIs(
            self._parameter(select_capability).default, inspect.Parameter.empty
        )

    def test_the_policy_itself_has_no_default(self) -> None:
        import dataclasses

        fields = {f.name: f for f in dataclasses.fields(RunPolicy)}
        field = fields["max_capability_steps"]
        self.assertIs(field.default, dataclasses.MISSING)
        self.assertIs(field.default_factory, dataclasses.MISSING)

    def test_no_module_level_ceiling_constant_exists(self) -> None:
        # A named constant is the other way a universal ceiling arrives.
        import pathlib
        import re

        import radhanite

        root = pathlib.Path(radhanite.__file__).parent
        offenders = []
        for path in sorted(root.glob("*.py")):
            for n, line in enumerate(path.read_text().splitlines(), 1):
                if re.match(r"^[A-Z_]*(MAX_|CEILING|STEPS)[A-Z_]*\s*(:.*)?=", line):
                    offenders.append(f"{path.name}:{n}: {line.strip()}")
        self.assertEqual(offenders, [], "a universal ceiling constant exists")


if __name__ == "__main__":
    unittest.main()
