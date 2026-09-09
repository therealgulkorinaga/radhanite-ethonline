"""A candidate carries three declared figures, and an offer must be decidable.

TASK-006 §2.2 fixes the candidate to exactly three fields and refuses duplicate
identifiers at the boundary; §2.5 A refuses a zero cost, as a termination
safeguard rather than an economic preference.

Nothing here tests an economic rule, because this step of TASK-006 contains
none.
"""

import doctest
import unittest
from decimal import Decimal

from radhanite import capability as capability_module
from radhanite.capability import Candidate, validate_candidates
from radhanite.money import Money
from radhanite.probability import Probability


def a_candidate(**overrides) -> Candidate:
    fields = {
        "candidate_id": "second-opinion-001",
        "cost": Money("0.50"),
        "success_probability": Probability("0.80"),
    }
    fields.update(overrides)
    return Candidate(**fields)


class CandidateTests(unittest.TestCase):
    def test_carries_its_declared_figures(self) -> None:
        c = a_candidate()
        self.assertEqual(c.candidate_id, "second-opinion-001")
        self.assertEqual(c.cost, Money("0.50"))
        self.assertEqual(c.success_probability, Probability("0.80"))

    def test_reads_as_its_identifier(self) -> None:
        self.assertEqual(str(a_candidate()), "second-opinion-001")

    def test_has_exactly_the_three_fields_task_006_allows(self) -> None:
        # TASK-006 §2.2: "Nothing else may enter the decision." A fourth field
        # is how a provider-shaped concept arrives in a provider-neutral model.
        self.assertEqual(
            Candidate.__dataclass_fields__.keys(),
            {"candidate_id", "cost", "success_probability"},
        )

    def test_needs_an_identifier(self) -> None:
        for empty in ("", "   ", "\t"):
            with self.assertRaises(ValueError):
                a_candidate(candidate_id=empty)

    def test_refuses_an_identifier_that_is_not_a_string(self) -> None:
        with self.assertRaises(TypeError):
            a_candidate(candidate_id=1)

    def test_refuses_a_padded_identifier(self) -> None:
        # "a " and "a" would read as one candidate in a run record while being
        # two under the single-use rule, so one could be consumed while the
        # other stayed on offer.
        for padded in (" second-opinion-001", "second-opinion-001 "):
            with self.assertRaises(ValueError):
                a_candidate(candidate_id=padded)


class PositiveCostInvariantTests(unittest.TestCase):
    """TASK-006 §2.5 A, criterion 18."""

    def test_refuses_a_zero_cost(self) -> None:
        with self.assertRaises(ValueError):
            a_candidate(cost=Money("0.00"))

    def test_refuses_a_negative_cost(self) -> None:
        with self.assertRaises(ValueError):
            a_candidate(cost=Money("-0.01"))

    def test_the_smallest_positive_cost_is_allowed(self) -> None:
        self.assertEqual(a_candidate(cost=Money("0.01")).cost, Money("0.01"))

    def test_the_refusal_says_why(self) -> None:
        # The invariant is a termination safeguard, and a message that reads as
        # an economic preference would invite someone to relax it.
        with self.assertRaises(ValueError) as raised:
            a_candidate(cost=Money("0.00"))
        self.assertIn("not a purchasable capability", str(raised.exception))


class FieldTypeTests(unittest.TestCase):
    def test_cost_must_be_money(self) -> None:
        for wrong in (Decimal("0.50"), 0.5, "0.50"):
            with self.assertRaises(TypeError):
                a_candidate(cost=wrong)

    def test_probability_must_be_a_probability(self) -> None:
        for wrong in (Decimal("0.80"), 0.8, "0.80"):
            with self.assertRaises(TypeError):
                a_candidate(success_probability=wrong)


class NoEconomicJudgementTests(unittest.TestCase):
    """A candidate is constructed knowing only itself."""

    def test_a_hopeless_candidate_is_permitted(self) -> None:
        # Whether an offer beats the task's current probability is a question
        # about a decision, not about the offer. Rejecting it here would make an
        # ordinary economic situation into an invalid object — the mistake
        # CODEX-PR006-04 caught in TASK-001.
        self.assertEqual(
            a_candidate(success_probability=Probability("0")).success_probability,
            Probability("0"),
        )

    def test_a_certain_candidate_is_permitted(self) -> None:
        self.assertEqual(
            a_candidate(success_probability=Probability("1")).success_probability,
            Probability("1"),
        )

    def test_an_expensive_candidate_is_permitted(self) -> None:
        # Affordability is checked against a budget the candidate cannot see.
        self.assertEqual(a_candidate(cost=Money("9999.99")).cost, Money("9999.99"))


class ImmutabilityTests(unittest.TestCase):
    def test_ordinary_assignment_is_refused(self) -> None:
        c = a_candidate()
        with self.assertRaises(Exception):
            c.cost = Money("0.01")

    def test_rehydration_is_refused(self) -> None:
        c = a_candidate()
        with self.assertRaises(TypeError):
            c.__setstate__({"cost": Money("0.01")})

    def test_there_is_no_instance_dictionary_to_write_through(self) -> None:
        self.assertFalse(hasattr(a_candidate(), "__dict__"))


class OfferValidationTests(unittest.TestCase):
    def test_returns_the_candidates_in_order(self) -> None:
        a, b = a_candidate(candidate_id="a"), a_candidate(candidate_id="b")
        self.assertEqual(validate_candidates([a, b]), (a, b))
        self.assertEqual(validate_candidates([b, a]), (b, a))

    def test_an_empty_offer_is_valid(self) -> None:
        # Zero candidates is an ordinary decision input — TASK-006 criterion 1
        # makes it STOP, which is a decision this step does not make.
        self.assertEqual(validate_candidates([]), ())

    def test_the_result_is_a_tuple_the_caller_cannot_change(self) -> None:
        offered = [a_candidate(candidate_id="a")]
        frozen = validate_candidates(offered)
        offered.append(a_candidate(candidate_id="b"))
        self.assertEqual(len(frozen), 1)

    def test_a_tuple_is_accepted(self) -> None:
        a = a_candidate(candidate_id="a")
        self.assertEqual(validate_candidates((a,)), (a,))

    def test_an_unordered_collection_is_refused(self) -> None:
        # Selection is order-independent, but the run record is not: a record
        # whose candidate list reorders between identical runs is not
        # reproducible.
        a, b = a_candidate(candidate_id="a"), a_candidate(candidate_id="b")
        with self.assertRaises(TypeError):
            validate_candidates({a, b})

    def test_a_generator_is_refused(self) -> None:
        with self.assertRaises(TypeError):
            validate_candidates(c for c in [a_candidate()])

    def test_a_string_is_refused(self) -> None:
        # A str is a Sequence, and would otherwise be iterated into characters.
        with self.assertRaises(TypeError):
            validate_candidates("second-opinion-001")

    def test_members_must_be_candidates(self) -> None:
        with self.assertRaises(TypeError):
            validate_candidates([a_candidate(), "not a candidate"])

    def test_the_member_refusal_names_the_position(self) -> None:
        with self.assertRaises(TypeError) as raised:
            validate_candidates([a_candidate(), object()])
        self.assertIn("[1]", str(raised.exception))


class DuplicateIdentifierTests(unittest.TestCase):
    """TASK-006 §2.2 — refused at the boundary, never resolved."""

    def test_duplicate_identifiers_are_refused(self) -> None:
        a = a_candidate(candidate_id="a", cost=Money("0.10"))
        also_a = a_candidate(candidate_id="a", cost=Money("0.90"))
        with self.assertRaises(ValueError):
            validate_candidates([a, also_a])

    def test_identical_candidates_are_still_a_duplicate(self) -> None:
        a = a_candidate(candidate_id="a")
        with self.assertRaises(ValueError):
            validate_candidates([a, a])

    def test_the_refusal_names_both_positions(self) -> None:
        a = a_candidate(candidate_id="a")
        b = a_candidate(candidate_id="b")
        with self.assertRaises(ValueError) as raised:
            validate_candidates([a, b, a])
        message = str(raised.exception)
        self.assertIn("positions 0 and 2", message)
        self.assertIn("'a'", message)

    def test_identifiers_differing_only_in_case_are_distinct(self) -> None:
        # Not a normalization rule: the tie-break in §2.4 is lexicographic on
        # the identifier as given, and folding case here would quietly change
        # which candidate wins.
        upper = a_candidate(candidate_id="A")
        lower = a_candidate(candidate_id="a")
        self.assertEqual(len(validate_candidates([upper, lower])), 2)


class DeterminismTests(unittest.TestCase):
    def test_validation_accumulates_no_state(self) -> None:
        a = a_candidate(candidate_id="a")
        first = validate_candidates([a])
        second = validate_candidates([a])
        self.assertEqual(first, second)

    def test_a_candidate_consumed_in_one_offer_is_not_barred_from_another(self) -> None:
        # Single-use is a property of a run, not of this module — TASK-006
        # §2.5a is enforced where the run's consumed set lives, and validation
        # must not quietly acquire memory of what it has seen.
        a = a_candidate(candidate_id="a")
        validate_candidates([a])
        self.assertEqual(validate_candidates([a]), (a,))


class NoAnticipationTests(unittest.TestCase):
    """This step of TASK-006 carries the model, and no economic rule."""

    def test_the_module_imports_no_decision_logic(self) -> None:
        imported = set(vars(capability_module))
        for absent in ("decide", "select", "evaluate", "run", "Strategy"):
            self.assertNotIn(absent, imported)

    def test_no_provider_or_payment_concept_appears(self) -> None:
        # TASK-006 §2.1. The rule must not be able to tell who is selling.
        import pathlib

        text = pathlib.Path(capability_module.__file__).read_text().lower()
        for forbidden in (
            "hedera",
            "circle",
            "tavily",
            "blockrun",
            "openrouter",
            "x402",
            "wallet",
            "usdc",
        ):
            self.assertNotIn(forbidden, text)


class DoctestTests(unittest.TestCase):
    def test_module_doctests_pass(self) -> None:
        results = doctest.testmod(capability_module, verbose=False)
        self.assertEqual(results.failed, 0)
        self.assertGreater(results.attempted, 0)


if __name__ == "__main__":
    unittest.main()
