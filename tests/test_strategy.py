"""Strategy fixtures are declared constants, and selection is deterministic.

TASK-001 §2.2 requires selection by fixed, inspectable rules producing an
identical result on identical input, and criterion 13 requires the costs and
probabilities to be static declared constants with no runtime estimation.
"""

import doctest
import unittest
from decimal import Decimal

from radhanite import strategy as strategy_module
from radhanite.money import Money
from radhanite.probability import Probability
from radhanite.strategy import DECLARED_STRATEGIES, Strategy, select


def a_strategy(**overrides) -> Strategy:
    fields = {
        "name": "Progressive Escalation",
        "initial_cost": Money("0.10"),
        "initial_success_probability": Probability("0.55"),
        "escalation_cost": Money("0.40"),
        "escalated_success_probability": Probability("0.85"),
    }
    fields.update(overrides)
    return Strategy(**fields)


class StrategyTests(unittest.TestCase):
    def test_carries_its_declared_figures(self) -> None:
        s = a_strategy()
        self.assertEqual(s.initial_cost, Money("0.10"))
        self.assertEqual(s.initial_success_probability, Probability("0.55"))
        self.assertEqual(s.escalation_cost, Money("0.40"))
        self.assertEqual(s.escalated_success_probability, Probability("0.85"))

    def test_needs_a_name(self) -> None:
        with self.assertRaises(ValueError):
            a_strategy(name="   ")

    def test_refuses_negative_costs(self) -> None:
        with self.assertRaises(ValueError):
            a_strategy(initial_cost=Money("-0.01"))
        with self.assertRaises(ValueError):
            a_strategy(escalation_cost=Money("-0.01"))

    def test_costs_must_be_money_and_chances_must_be_probabilities(self) -> None:
        with self.assertRaises(TypeError):
            a_strategy(initial_cost="0.10")
        with self.assertRaises(TypeError):
            a_strategy(initial_success_probability=Decimal("0.55"))

    def test_free_attempts_are_allowed(self) -> None:
        self.assertEqual(a_strategy(initial_cost=Money("0")).initial_cost, Money("0"))

    def test_a_worthless_escalation_is_permitted(self) -> None:
        # An escalation that does not improve the chance of success, or makes it
        # worse, is an economic situation rather than an invalid one. TASK-001
        # §2.5 answers it with Stop, and that outcome must stay reachable.
        # Rejecting it here would repeat CODEX-PR006-04.
        useless = a_strategy(escalated_success_probability=Probability("0.55"))
        self.assertEqual(useless.escalated_success_probability, Probability("0.55"))
        worse = a_strategy(escalated_success_probability=Probability("0.30"))
        self.assertEqual(worse.escalated_success_probability, Probability("0.30"))

    def test_a_strategy_cannot_be_changed_after_creation(self) -> None:
        with self.assertRaises(Exception):
            a_strategy().initial_cost = Money("999.00")


class DeclaredConstantsTests(unittest.TestCase):
    """Criterion 13: static declared constants, never estimated at runtime."""

    def test_a_declared_strategy_cannot_be_mutated_through_its_dict(self) -> None:
        # A frozen dataclass blocks attribute assignment but, without slots,
        # leaves the instance dictionary writable — so the catalogue could be
        # rewritten from outside despite the guarantee.
        strategy = DECLARED_STRATEGIES[0]
        with self.assertRaises(AttributeError):
            strategy.__dict__["initial_cost"] = Money("9.00")
        with self.assertRaises(AttributeError):
            strategy.initial_cost.__dict__["amount"] = 9
        self.assertEqual(DECLARED_STRATEGIES[0].initial_cost, Money("0.02"))

    def test_the_fixtures_hold_exactly_the_declared_figures(self) -> None:
        # Written out longhand on purpose. If anything ever computes these
        # rather than declaring them, this test is what notices.
        expected = {
            "Direct Attempt": ("0.02", "0.35", "0.08", "0.55"),
            "Progressive Escalation": ("0.10", "0.55", "0.40", "0.85"),
            "Exhaustive Attempt": ("0.50", "0.75", "1.50", "0.92"),
        }
        self.assertEqual(len(DECLARED_STRATEGIES), len(expected))
        for s in DECLARED_STRATEGIES:
            with self.subTest(strategy=s.name):
                self.assertIn(s.name, expected)
                cost, chance, esc_cost, esc_chance = expected[s.name]
                self.assertEqual(s.initial_cost, Money(cost))
                self.assertEqual(s.initial_success_probability, Probability(chance))
                self.assertEqual(s.escalation_cost, Money(esc_cost))
                self.assertEqual(
                    s.escalated_success_probability, Probability(esc_chance)
                )

    def test_every_declared_figure_is_a_literal_in_the_source(self) -> None:
        """Criterion 13 forbids computing these, not merely getting them right.

        Comparing values cannot tell a declared 0.35 from a computed
        0.30 + 0.05 — both compare equal. So this reads the source itself and
        requires every figure inside DECLARED_STRATEGIES to be a literal
        constant handed straight to Money or Probability, with no arithmetic,
        no name lookup, and no call in between.
        """
        import ast
        import pathlib

        source = pathlib.Path(strategy_module.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)

        declaration = None
        for node in ast.walk(tree):
            if isinstance(node, ast.AnnAssign) and getattr(
                node.target, "id", None
            ) == "DECLARED_STRATEGIES":
                declaration = node.value
            elif isinstance(node, ast.Assign) and any(
                getattr(t, "id", None) == "DECLARED_STRATEGIES" for t in node.targets
            ):
                declaration = node.value
        self.assertIsNotNone(declaration, "DECLARED_STRATEGIES not found in source")

        checked = 0
        for call in (n for n in ast.walk(declaration) if isinstance(n, ast.Call)):
            callee = getattr(call.func, "id", None)
            if callee not in {"Money", "Probability"}:
                continue
            for argument in call.args:
                self.assertIsInstance(
                    argument,
                    ast.Constant,
                    f"{callee}(...) in DECLARED_STRATEGIES is built from "
                    f"{ast.dump(argument)}, not a literal constant",
                )
                self.assertIsInstance(argument.value, str)
                checked += 1

        # Three strategies x two costs and two probabilities.
        self.assertEqual(checked, 12)

    def test_the_figures_do_not_change_between_reads(self) -> None:
        first = tuple(DECLARED_STRATEGIES)
        second = tuple(DECLARED_STRATEGIES)
        self.assertEqual(first, second)

    def test_the_catalogue_cannot_be_appended_to(self) -> None:
        with self.assertRaises(AttributeError):
            DECLARED_STRATEGIES.append(a_strategy())

    def test_names_are_unique(self) -> None:
        # Run records refer to a strategy by name; duplicates would make a
        # record ambiguous about what was actually attempted.
        names = [s.name for s in DECLARED_STRATEGIES]
        self.assertEqual(len(names), len(set(names)))


class SelectionTests(unittest.TestCase):
    def test_takes_the_first_affordable_in_declared_order(self) -> None:
        self.assertEqual(
            select(DECLARED_STRATEGIES, Money("2.00")).name, "Direct Attempt"
        )

    def test_declared_order_is_the_policy(self) -> None:
        # Reversing the catalogue changes the choice. That is the point: the
        # order is declared data, not a judgement made at runtime.
        reversed_catalogue = tuple(reversed(DECLARED_STRATEGIES))
        self.assertEqual(
            select(reversed_catalogue, Money("2.00")).name, "Exhaustive Attempt"
        )

    def test_skips_what_cannot_be_afforded(self) -> None:
        only_dear = DECLARED_STRATEGIES[1:]
        self.assertEqual(
            select(only_dear, Money("0.20")).name, "Progressive Escalation"
        )

    def test_exactly_affordable_counts_as_affordable(self) -> None:
        self.assertEqual(
            select(DECLARED_STRATEGIES, Money("0.02")).name, "Direct Attempt"
        )

    def test_a_penny_short_is_not(self) -> None:
        self.assertIsNone(select(DECLARED_STRATEGIES, Money("0.01")))

    def test_nothing_affordable_returns_nothing(self) -> None:
        # Not a failure: the budget condition of §2.5 arriving before any
        # attempt is made. The caller is expected to stop.
        self.assertIsNone(select(DECLARED_STRATEGIES, Money("0")))

    def test_an_empty_catalogue_returns_nothing(self) -> None:
        self.assertIsNone(select((), Money("100.00")))

    def test_a_negative_budget_is_a_fault_not_a_choice(self) -> None:
        with self.assertRaises(ValueError):
            select(DECLARED_STRATEGIES, Money("-0.01"))

    def test_an_unordered_catalogue_is_refused(self) -> None:
        # Iterating a set depends on the process hash seed, so the same
        # catalogue and budget could choose differently between runs. Criterion
        # 2 cannot hold for a collection with no order, so it is refused rather
        # than turned into a hash-dependent economic decision.
        with self.assertRaises(TypeError):
            select(set(DECLARED_STRATEGIES), Money("2.00"))
        with self.assertRaises(TypeError):
            select(frozenset(DECLARED_STRATEGIES), Money("2.00"))

    def test_ordered_collections_are_accepted(self) -> None:
        as_list = list(DECLARED_STRATEGIES)
        self.assertEqual(select(as_list, Money("2.00")).name, "Direct Attempt")


class DeterminismTests(unittest.TestCase):
    """Criterion 2: identical inputs produce an identical selection, every time."""

    def test_repeated_selection_is_identical(self) -> None:
        for budget in ("2.00", "0.50", "0.10", "0.02", "0"):
            with self.subTest(budget=budget):
                chosen = {
                    (s.name if (s := select(DECLARED_STRATEGIES, Money(budget))) else None)
                    for _ in range(50)
                }
                self.assertEqual(len(chosen), 1)

    def test_selection_does_not_depend_on_call_order(self) -> None:
        first = select(DECLARED_STRATEGIES, Money("2.00"))
        select(DECLARED_STRATEGIES, Money("0.10"))
        select(DECLARED_STRATEGIES, Money("100.00"))
        again = select(DECLARED_STRATEGIES, Money("2.00"))
        self.assertEqual(first, again)

    def test_the_selector_accumulates_no_state(self) -> None:
        """Checking the signature proves nothing; a history list needs no argument.

        This snapshots every mutable value the module holds, and every attribute
        hung on the function itself, runs a series of selections, and requires
        the snapshot to be unchanged. A selector that remembered anything
        between calls would show up here.
        """
        def snapshot():
            module_state = {
                name: repr(value)
                for name, value in vars(strategy_module).items()
                if not name.startswith("__")
                and isinstance(value, (list, dict, set, bytearray))
            }
            function_state = {
                name: repr(value)
                for name, value in vars(select).items()
                if not name.startswith("__")
            }
            return module_state, function_state

        before = snapshot()
        for budget in ("2.00", "0.10", "0.02", "0", "100.00", "0.50"):
            select(DECLARED_STRATEGIES, Money(budget))
        self.assertEqual(snapshot(), before)

    def test_the_selector_takes_only_what_it_needs(self) -> None:
        import inspect

        self.assertEqual(
            set(inspect.signature(select).parameters),
            {"strategies", "remaining_budget"},
        )


def load_tests(loader, tests, ignore):
    tests.addTests(
        doctest.DocTestSuite(strategy_module, optionflags=doctest.ELLIPSIS)
    )
    return tests
