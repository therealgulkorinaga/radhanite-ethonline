"""Capability descriptors become provider-neutral candidates, and nothing else.

TASK-008 is the boundary between external capability sources and TASK-006's
`Candidate`. It normalizes. It selects nothing, executes nothing, pays nothing,
and updates no task state.
"""

import doctest
import unittest
from decimal import Decimal

from radhanite import acquisition as acquisition_module
from radhanite.acquisition import (
    CapabilityCatalog,
    CapabilityDescriptor,
    acquire,
    normalize,
)
from radhanite.capability import Candidate
from radhanite.money import Money
from radhanite.probability import Probability


def a_descriptor(**overrides) -> CapabilityDescriptor:
    fields = {
        "descriptor_id": "second-opinion-001",
        "name": "Independent second opinion",
        "cost": Money("0.50"),
        "source_reference": "opaque-handle-abc",
    }
    fields.update(overrides)
    return CapabilityDescriptor(**fields)


def an_offer(**overrides):
    return [(a_descriptor(**overrides), Probability("0.80"))]


class DescriptorTests(unittest.TestCase):
    def test_carries_its_fields(self) -> None:
        d = a_descriptor()
        self.assertEqual(d.descriptor_id, "second-opinion-001")
        self.assertEqual(d.name, "Independent second opinion")
        self.assertEqual(d.cost, Money("0.50"))
        self.assertEqual(d.source_reference, "opaque-handle-abc")

    def test_needs_an_identifier(self) -> None:
        for empty in ("", "   "):
            with self.assertRaises(ValueError):
                a_descriptor(descriptor_id=empty)

    def test_needs_a_name(self) -> None:
        with self.assertRaises(ValueError):
            a_descriptor(name="  ")

    def test_is_immutable(self) -> None:
        d = a_descriptor()
        with self.assertRaises(Exception):
            d.cost = Money("9.99")
        with self.assertRaises(TypeError):
            d.__setstate__({"cost": Money("9.99")})
        self.assertFalse(hasattr(d, "__dict__"))


class KnownPriceTests(unittest.TestCase):
    """The non-negotiable invariant: the price is known before purchase."""

    def test_a_zero_cost_descriptor_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            a_descriptor(cost=Money("0.00"))

    def test_a_negative_cost_descriptor_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            a_descriptor(cost=Money("-0.01"))

    def test_an_unquoted_cost_cannot_enter_the_candidate_set(self) -> None:
        # There is no representation for "unknown". A source that cannot quote
        # cannot construct a descriptor at all.
        for unquoted in (None, "unknown", "", Decimal("0.50"), 0.5):
            with self.assertRaises(TypeError):
                a_descriptor(cost=unquoted)

    def test_the_refusal_explains_the_invariant(self) -> None:
        with self.assertRaises(ValueError) as raised:
            a_descriptor(cost=Money("0.00"))
        self.assertIn("known before purchase", str(raised.exception))


class NormalizationTests(unittest.TestCase):
    def test_produces_a_candidate(self) -> None:
        c = normalize(a_descriptor(), expected_post_action_success_probability=Probability("0.80"))
        self.assertIsInstance(c, Candidate)

    def test_uses_the_descriptors_exact_cost(self) -> None:
        c = normalize(a_descriptor(cost=Money("1.37")),
                      expected_post_action_success_probability=Probability("0.80"))
        self.assertEqual(c.cost, Money("1.37"))

    def test_preserves_the_supplied_probability_exactly(self) -> None:
        for p in ("0.80", "0.005", "0.999999", "1", "0"):
            c = normalize(a_descriptor(),
                          expected_post_action_success_probability=Probability(p))
            self.assertEqual(c.success_probability, Probability(p))

    def test_nothing_passes_through_float(self) -> None:
        c = normalize(a_descriptor(), expected_post_action_success_probability=Probability("0.80"))
        self.assertIsInstance(c.cost, Money)
        self.assertNotIsInstance(c.cost, float)
        self.assertIsInstance(c.success_probability, Probability)

    def test_an_invalid_probability_is_refused(self) -> None:
        for wrong in (Decimal("0.80"), 0.8, "0.80", None):
            with self.assertRaises(TypeError):
                normalize(a_descriptor(), expected_post_action_success_probability=wrong)

    def test_the_descriptor_must_be_a_descriptor(self) -> None:
        with self.assertRaises(TypeError):
            normalize("second-opinion-001",
                      expected_post_action_success_probability=Probability("0.80"))

    def test_the_probability_is_keyword_only(self) -> None:
        with self.assertRaises(TypeError):
            normalize(a_descriptor(), Probability("0.80"))

    def test_identity_is_the_descriptor_identifier(self) -> None:
        c = normalize(a_descriptor(descriptor_id="research-042"),
                      expected_post_action_success_probability=Probability("0.80"))
        self.assertEqual(c.candidate_id, "research-042")

    def test_the_same_input_normalizes_identically(self) -> None:
        first = normalize(a_descriptor(), expected_post_action_success_probability=Probability("0.80"))
        second = normalize(a_descriptor(), expected_post_action_success_probability=Probability("0.80"))
        self.assertEqual(first, second)

    def test_the_descriptor_is_not_mutated(self) -> None:
        d = a_descriptor()
        before = (d.descriptor_id, d.name, d.cost, d.source_reference)
        normalize(d, expected_post_action_success_probability=Probability("0.80"))
        self.assertEqual((d.descriptor_id, d.name, d.cost, d.source_reference), before)


class CandidateStaysProviderNeutralTests(unittest.TestCase):
    """The contamination this task exists to prevent."""

    def test_the_candidate_shape_is_unchanged(self) -> None:
        self.assertEqual(
            set(Candidate.__dataclass_fields__),
            {"candidate_id", "cost", "success_probability"},
        )

    def test_no_source_reference_reaches_the_candidate(self) -> None:
        c = normalize(a_descriptor(source_reference="https://example.invalid/x402/pay"),
                      expected_post_action_success_probability=Probability("0.80"))
        for value in vars(type(c))["__slots__"]:
            self.assertNotIn("source", value)
        self.assertNotIn("example.invalid", repr(c))

    def test_no_name_reaches_the_candidate(self) -> None:
        c = normalize(a_descriptor(name="BlockRun deep analysis via Circle"),
                      expected_post_action_success_probability=Probability("0.80"))
        self.assertNotIn("BlockRun", repr(c))
        self.assertNotIn("Circle", repr(c))

    def test_the_module_names_no_provider(self) -> None:
        # Whole words only. A plain substring scan flags "arc" inside
        # "research", which would push the module towards worse prose to satisfy
        # a test rather than towards neutrality.
        import pathlib
        import re

        text = pathlib.Path(acquisition_module.__file__).read_text().lower()
        for forbidden in ("hedera", "circle", "arc", "tavily", "blockrun",
                          "openrouter", "x402", "wallet", "usdc", "subgraph",
                          "marketplace", "sponsor"):
            self.assertIsNone(
                re.search(rf"\b{forbidden}\b", text),
                f"provider term {forbidden!r} appears in the acquisition module",
            )


class CatalogTests(unittest.TestCase):
    def test_acquire_returns_a_catalog_of_candidates(self) -> None:
        catalog = acquire(an_offer())
        self.assertIsInstance(catalog, CapabilityCatalog)
        self.assertEqual(len(catalog.candidates), 1)
        self.assertIsInstance(catalog.candidates[0], Candidate)

    def test_an_empty_offer_is_valid(self) -> None:
        self.assertEqual(acquire([]).candidates, ())

    def test_the_descriptor_is_recoverable_from_the_selected_candidate_id(self) -> None:
        catalog = acquire(an_offer())
        selected = catalog.candidates[0]
        recovered = catalog.descriptor_for(selected.candidate_id)
        self.assertEqual(recovered.source_reference, "opaque-handle-abc")
        self.assertEqual(recovered.name, "Independent second opinion")

    def test_lookup_of_an_unknown_candidate_id_fails_deterministically(self) -> None:
        catalog = acquire(an_offer())
        for unknown in ("nope", "", "SECOND-OPINION-001"):
            with self.assertRaises(KeyError):
                catalog.descriptor_for(unknown)

    def test_duplicate_identifiers_in_one_offer_are_refused(self) -> None:
        twin = (a_descriptor(cost=Money("9.99")), Probability("0.90"))
        with self.assertRaises(ValueError):
            acquire(an_offer() + [twin])

    def test_the_offer_must_be_an_ordered_sequence(self) -> None:
        with self.assertRaises(TypeError):
            acquire({(a_descriptor(), Probability("0.80"))})

    def test_candidates_follow_the_offer_order(self) -> None:
        offer = [
            (a_descriptor(descriptor_id="b"), Probability("0.70")),
            (a_descriptor(descriptor_id="a"), Probability("0.80")),
        ]
        self.assertEqual([c.candidate_id for c in acquire(offer).candidates], ["b", "a"])

    def test_caller_mutation_cannot_change_the_catalog(self) -> None:
        offer = an_offer()
        catalog = acquire(offer)
        offer.append((a_descriptor(descriptor_id="late"), Probability("0.9")))
        self.assertEqual(len(catalog.candidates), 1)

    def test_the_catalog_is_immutable(self) -> None:
        catalog = acquire(an_offer())
        with self.assertRaises(Exception):
            catalog.entries = ()
        with self.assertRaises(AttributeError):
            catalog.candidates.append(None)

    def test_the_stored_entries_are_a_tuple_not_a_list(self) -> None:
        # A frozen dataclass stops the field being reassigned; it does not stop
        # a list inside it being appended to by anyone holding the catalogue.
        catalog = acquire(an_offer())
        self.assertIsInstance(catalog.entries, tuple)
        with self.assertRaises(AttributeError):
            catalog.entries.append(None)

    def test_acquiring_twice_is_deterministic(self) -> None:
        self.assertEqual(acquire(an_offer()).candidates, acquire(an_offer()).candidates)


class DirectCatalogConstructionTests(unittest.TestCase):
    """CODEX-PR029-01 — one validated path, not two paths of differing safety.

    `acquire()` enforced the invariants; the public constructor enforced
    nothing, so a caller could build a catalogue whose lookup returned a
    descriptor inconsistent with its candidate. A type with one safe route and
    one unsafe route has an unsafe route.
    """

    def _pair(self, identifier="a", cost=Money("0.10")):
        descriptor = a_descriptor(descriptor_id=identifier, cost=cost)
        candidate = normalize(
            descriptor, expected_post_action_success_probability=Probability("0.80")
        )
        return candidate, descriptor

    def test_a_valid_direct_construction_is_accepted(self) -> None:
        catalog = CapabilityCatalog(entries=[self._pair()])
        self.assertEqual(len(catalog.candidates), 1)
        self.assertEqual(catalog.descriptor_for("a").descriptor_id, "a")

    def test_entries_are_frozen_even_when_a_list_is_passed(self) -> None:
        catalog = CapabilityCatalog(entries=[self._pair()])
        self.assertIsInstance(catalog.entries, tuple)
        with self.assertRaises(AttributeError):
            catalog.entries.append(None)

    def test_mutating_the_original_list_afterwards_changes_nothing(self) -> None:
        supplied = [self._pair("a")]
        catalog = CapabilityCatalog(entries=supplied)
        supplied.append(self._pair("b"))
        self.assertEqual(len(catalog.candidates), 1)
        with self.assertRaises(KeyError):
            catalog.descriptor_for("b")

    def test_duplicate_candidate_ids_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            CapabilityCatalog(entries=[self._pair("a"), self._pair("a")])

    def test_the_duplicate_refusal_names_both_positions(self) -> None:
        with self.assertRaises(ValueError) as raised:
            CapabilityCatalog(
                entries=[self._pair("a"), self._pair("b"), self._pair("a")]
            )
        self.assertIn("positions 0 and 2", str(raised.exception))

    def test_an_identifier_mismatch_is_rejected(self) -> None:
        candidate, descriptor = self._pair("a")
        other = a_descriptor(descriptor_id="different", cost=candidate.cost)
        with self.assertRaises(ValueError):
            CapabilityCatalog(entries=[(candidate, other)])

    def test_a_cost_mismatch_is_rejected(self) -> None:
        candidate, _ = self._pair("a", Money("0.10"))
        dearer = a_descriptor(descriptor_id="a", cost=Money("9.99"))
        with self.assertRaises(ValueError):
            CapabilityCatalog(entries=[(candidate, dearer)])

    def test_a_malformed_entry_is_rejected(self) -> None:
        candidate, descriptor = self._pair()
        for malformed in (
            [candidate],
            [(candidate,)],
            [(candidate, descriptor, descriptor)],
            [(descriptor, candidate)],
            ["not-a-pair"],
            [(None, None)],
        ):
            with self.subTest(entries=malformed):
                with self.assertRaises((TypeError, ValueError)):
                    CapabilityCatalog(entries=malformed)

    def test_an_unordered_collection_of_entries_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            CapabilityCatalog(entries={self._pair()})

    def test_an_empty_catalog_is_valid(self) -> None:
        self.assertEqual(CapabilityCatalog(entries=[]).candidates, ())

    def test_lookup_can_never_contradict_its_candidate(self) -> None:
        # The property the invariants exist to guarantee.
        catalog = CapabilityCatalog(entries=[self._pair("a"), self._pair("b", Money("2.00"))])
        for candidate in catalog.candidates:
            descriptor = catalog.descriptor_for(candidate.candidate_id)
            self.assertEqual(candidate.candidate_id, descriptor.descriptor_id)
            self.assertEqual(candidate.cost, descriptor.cost)

    def test_unknown_lookup_still_fails_deterministically(self) -> None:
        catalog = CapabilityCatalog(entries=[self._pair("a")])
        with self.assertRaises(KeyError):
            catalog.descriptor_for("b")

    def test_acquire_still_behaves_exactly_as_before(self) -> None:
        catalog = acquire(an_offer())
        self.assertEqual(len(catalog.candidates), 1)
        self.assertEqual(
            catalog.descriptor_for("second-opinion-001").source_reference,
            "opaque-handle-abc",
        )
        self.assertIsInstance(catalog.entries, tuple)


class DoesNothingElseTests(unittest.TestCase):
    def test_it_selects_nothing(self) -> None:
        exported = set(vars(acquisition_module))
        for absent in ("select", "select_capability", "assess", "rank", "decide"):
            self.assertNotIn(absent, exported)

    def test_it_executes_and_pays_nothing(self) -> None:
        exported = set(vars(acquisition_module))
        for absent in ("execute", "invoke", "pay", "settle", "charge", "request"):
            self.assertNotIn(absent, exported)

    def test_it_updates_no_task_state(self) -> None:
        import inspect

        for fn in (normalize, acquire):
            parameters = set(inspect.signature(fn).parameters)
            for absent in ("task_state", "state", "run", "budget", "task_value"):
                self.assertNotIn(absent, parameters)

    def test_it_makes_no_network_call(self) -> None:
        import pathlib

        text = pathlib.Path(acquisition_module.__file__).read_text()
        for forbidden in ("http", "urllib", "requests", "socket", "import json"):
            self.assertNotIn(forbidden, text)


class DoctestTests(unittest.TestCase):
    def test_module_doctests_pass(self) -> None:
        results = doctest.testmod(acquisition_module, verbose=False)
        self.assertEqual(results.failed, 0)
        self.assertGreater(results.attempted, 0)


if __name__ == "__main__":
    unittest.main()
