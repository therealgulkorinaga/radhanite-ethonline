"""The ranking, its three tie-breaks, and the order-independence they buy.

TASK-006 §2.4 fixes the ranking; §2.5 fixes when the answer is STOP instead.
Nothing here executes a capability, evaluates a task state, or advances a run.
"""

import doctest
import itertools
import unittest

from radhanite import eligibility as eligibility_module
from radhanite import selection as selection_module
from radhanite.capability import Candidate
from radhanite.eligibility import Assessment, Ineligibility, assess
from radhanite.money import Money
from radhanite.probability import Probability
from radhanite.selection import Selection, SelectionOutcome, select_capability

# current 0.50, task value $20.00 — so IEV = (p - 0.50) x $20.00
#
#   id          cost     p        IEV      NEV
#   a-cheap     $0.10    0.525    $0.50    $0.40
#   b-middle    $1.00    0.65     $3.00    $2.00   <- best net value
#   c-dear      $4.00    0.75     $5.00    $1.00   <- best gross value
CHEAP = Candidate("a-cheap", Money("0.10"), Probability("0.525"))
MIDDLE = Candidate("b-middle", Money("1.00"), Probability("0.65"))
DEAR = Candidate("c-dear", Money("4.00"), Probability("0.75"))


STATE = {
    "current_success_probability": Probability("0.50"),
    "task_value": Money("20.00"),
    "remaining_budget": Money("10.00"),
    "consumed_candidate_ids": (),
    "capability_step_count": 0,
    "max_capability_steps": 4,
}


def assessed(candidates, **state_overrides) -> tuple[Assessment, ...]:
    """Run eligibility, as a caller would, BEFORE ranking is asked anything."""
    state = {**STATE, **state_overrides}
    return tuple(assess(candidate=c, **state) for c in candidates)


def a_selection(candidates=None, assessments=None, **overrides) -> Selection:
    state = {k: v for k, v in overrides.items() if k in STATE}
    unknown = set(overrides) - set(STATE)
    assert not unknown, f"unexpected override(s): {unknown}"

    if assessments is None:
        if candidates is None:
            candidates = [CHEAP, MIDDLE, DEAR]
        assessments = assessed(candidates, **state)

    return select_capability(assessments=assessments, **{**STATE, **state})


class RankingTests(unittest.TestCase):
    def test_the_best_net_value_wins(self) -> None:
        s = a_selection()
        self.assertIs(s.outcome, SelectionOutcome.SELECTED)
        self.assertEqual(s.selected.candidate.candidate_id, "b-middle")
        self.assertEqual(s.selected.net_expected_value, Money("2.00"))

    def test_the_winner_is_neither_the_cheapest_nor_the_most_valuable(self) -> None:
        # A rule that picked the cheapest, or the largest gross gain, would pass
        # a test that only checked "something was selected".
        s = a_selection()
        costs = {a.candidate.candidate_id: a.candidate.cost for a in s.assessments}
        gross = {
            a.candidate.candidate_id: a.incremental_expected_value
            for a in s.assessments
        }
        self.assertNotEqual(min(costs, key=costs.get), "b-middle")
        self.assertNotEqual(max(gross, key=gross.get), "b-middle")

    def test_a_single_eligible_candidate_wins_by_default(self) -> None:
        s = a_selection(candidates=[MIDDLE])
        self.assertEqual(s.selected.candidate.candidate_id, "b-middle")

    def test_every_candidate_is_assessed_not_only_the_winner(self) -> None:
        # TASK-006 §8: a record showing only what was bought cannot answer why
        # the alternatives were not.
        s = a_selection()
        self.assertEqual(len(s.assessments), 3)
        self.assertEqual(len(s.eligible), 3)
        self.assertEqual(s.rejected, ())


class TieBreakTests(unittest.TestCase):
    """§2.4, levels two and three."""

    def test_equal_net_value_goes_to_the_lower_cost(self) -> None:
        # cheaper: $1.00, IEV $3.00, net $2.00
        # dearer:  $2.00, IEV $4.00, net $2.00
        cheaper = Candidate("z-cheaper", Money("1.00"), Probability("0.65"))
        dearer = Candidate("a-dearer", Money("2.00"), Probability("0.70"))
        s = a_selection(candidates=[dearer, cheaper])
        # The tie must be real, or this tests nothing about level two.
        self.assertEqual(
            {a.net_expected_value for a in s.assessments}, {Money("2.00")}
        )
        self.assertNotEqual(cheaper.cost, dearer.cost)
        self.assertEqual(s.selected.candidate.candidate_id, "z-cheaper")

    def test_the_cost_tie_break_is_not_the_identifier_tie_break(self) -> None:
        # The cheaper candidate here sorts LAST alphabetically, so a rule that
        # skipped level two would pick the other one.
        cheaper = Candidate("z-cheaper", Money("1.00"), Probability("0.65"))
        dearer = Candidate("a-dearer", Money("2.00"), Probability("0.70"))
        s = a_selection(candidates=[cheaper, dearer])
        self.assertEqual(s.selected.candidate.candidate_id, "z-cheaper")

    def test_equal_net_value_and_cost_goes_to_the_smaller_identifier(self) -> None:
        first = Candidate("a-first", Money("1.00"), Probability("0.65"))
        second = Candidate("b-second", Money("1.00"), Probability("0.65"))
        for offer in ([first, second], [second, first]):
            s = a_selection(candidates=offer)
            self.assertEqual(s.selected.candidate.candidate_id, "a-first")

    def test_the_identifier_tie_break_carries_no_economic_meaning(self) -> None:
        # It exists only to make the order total. A candidate must not win on
        # its name while another has a better net value.
        early_name = Candidate("a-worse", Money("1.00"), Probability("0.60"))
        late_name = Candidate("z-better", Money("1.00"), Probability("0.65"))
        s = a_selection(candidates=[early_name, late_name])
        self.assertEqual(s.selected.candidate.candidate_id, "z-better")


class NeitherUpliftNorCheapnessRoutingTests(unittest.TestCase):
    """The test that makes "highest uplift" and "cheapest" impossible to ship.

    A has the largest probability uplift.
    B has the lowest cost.
    C has neither — and the highest net expected value.

    C must win.
    """

    # current 0.50, task value $20.00
    #   A  cost $8.00  p 0.95  uplift 0.45  IEV $9.00  NET $1.00
    #   B  cost $0.10  p 0.53  uplift 0.03  IEV $0.60  NET $0.50
    #   C  cost $2.00  p 0.80  uplift 0.30  IEV $6.00  NET $4.00  <- wins
    A_BIGGEST_UPLIFT = Candidate("a-uplift", Money("8.00"), Probability("0.95"))
    B_LOWEST_COST = Candidate("b-cheapest", Money("0.10"), Probability("0.53"))
    C_BEST_NET = Candidate("c-best-net", Money("2.00"), Probability("0.80"))

    def _selection(self, order):
        return a_selection(candidates=list(order), remaining_budget=Money("20.00"))

    def test_the_premises_hold_before_the_conclusion_is_tested(self) -> None:
        # If A were not the largest uplift, or B not the cheapest, the
        # conclusion below would prove nothing.
        s = self._selection(
            [self.A_BIGGEST_UPLIFT, self.B_LOWEST_COST, self.C_BEST_NET]
        )
        by_id = {a.candidate.candidate_id: a for a in s.assessments}
        self.assertEqual(len(s.eligible), 3)

        uplifts = {
            i: a.candidate.success_probability for i, a in by_id.items()
        }
        costs = {i: a.candidate.cost for i, a in by_id.items()}
        nets = {i: a.net_expected_value for i, a in by_id.items()}

        self.assertEqual(max(uplifts, key=uplifts.get), "a-uplift")
        self.assertEqual(min(costs, key=costs.get), "b-cheapest")
        self.assertEqual(max(nets, key=nets.get), "c-best-net")

    def test_the_highest_net_value_wins_not_the_biggest_uplift(self) -> None:
        s = self._selection(
            [self.A_BIGGEST_UPLIFT, self.B_LOWEST_COST, self.C_BEST_NET]
        )
        self.assertEqual(s.selected.candidate.candidate_id, "c-best-net")
        self.assertEqual(s.selected.net_expected_value, Money("4.00"))

    def test_it_wins_from_every_input_order(self) -> None:
        for order in itertools.permutations(
            [self.A_BIGGEST_UPLIFT, self.B_LOWEST_COST, self.C_BEST_NET]
        ):
            with self.subTest(order=[c.candidate_id for c in order]):
                self.assertEqual(
                    self._selection(order).selected.candidate.candidate_id,
                    "c-best-net",
                )


class NoMutationTests(unittest.TestCase):
    """Ranking answers a question. It changes nothing."""

    def test_the_candidates_are_unchanged(self) -> None:
        before = [(c.candidate_id, c.cost, c.success_probability)
                  for c in (CHEAP, MIDDLE, DEAR)]
        a_selection()
        after = [(c.candidate_id, c.cost, c.success_probability)
                 for c in (CHEAP, MIDDLE, DEAR)]
        self.assertEqual(before, after)

    def test_the_assessments_are_unchanged_by_ranking(self) -> None:
        s = a_selection()
        snapshot = [
            (a.candidate.candidate_id, a.net_expected_value,
             a.incremental_expected_value, a.failed_conditions)
            for a in s.assessments
        ]
        # Reading the winner and the partitions must not disturb anything.
        _ = s.selected, s.eligible, s.rejected, s.reason
        self.assertEqual(
            [(a.candidate.candidate_id, a.net_expected_value,
              a.incremental_expected_value, a.failed_conditions)
             for a in s.assessments],
            snapshot,
        )

    def test_the_selected_candidate_is_not_consumed(self) -> None:
        # §2.7: consuming an identifier belongs to the run loop.
        s = a_selection(consumed_candidate_ids=["x-other"])
        self.assertEqual(s.consumed_candidate_ids, ("x-other",))
        self.assertNotIn(s.selected.candidate.candidate_id, s.consumed_candidate_ids)

    def test_the_step_count_is_not_advanced(self) -> None:
        s = a_selection(capability_step_count=2)
        self.assertEqual(s.capability_step_count, 2)
        for assessment in s.assessments:
            self.assertEqual(assessment.capability_step_count, 2)

    def test_the_callers_consumed_collection_is_not_written_to(self) -> None:
        consumed = ["x-other"]
        a_selection(consumed_candidate_ids=consumed)
        self.assertEqual(consumed, ["x-other"])

    def test_selecting_twice_from_the_same_state_gives_the_same_answer(self) -> None:
        first, second = a_selection(), a_selection()
        self.assertEqual(
            first.selected.candidate.candidate_id,
            second.selected.candidate.candidate_id,
        )
        self.assertEqual(first.consumed_candidate_ids, second.consumed_candidate_ids)
        self.assertEqual(first.capability_step_count, second.capability_step_count)


class ExactArithmeticTests(unittest.TestCase):
    def test_no_float_reaches_any_figure(self) -> None:
        s = a_selection()
        for assessment in s.assessments:
            for figure in (
                assessment.incremental_expected_value,
                assessment.net_expected_value,
                assessment.candidate.cost,
            ):
                self.assertIsInstance(figure, Money)
                self.assertNotIsInstance(figure, float)

    def test_a_tie_that_binary_floating_point_would_miss(self) -> None:
        # 0.1 + 0.2 != 0.3 in binary floating point. These two candidates tie
        # exactly in decimal, so level two decides; under float they would not
        # tie and the dearer might win.
        first = Candidate("a-tenths", Money("0.30"), Probability("0.53"))
        second = Candidate("b-thirds", Money("0.10"), Probability("0.52"))
        s = a_selection(candidates=[first, second], task_value=Money("20.00"))
        self.assertEqual(
            {a.net_expected_value for a in s.assessments}, {Money("0.30")}
        )
        self.assertEqual(s.selected.candidate.candidate_id, "b-thirds")


class OrderIndependenceTests(unittest.TestCase):
    """§2.4 — the ranking is total, so the offer order cannot matter."""

    def test_every_permutation_selects_the_same_candidate(self) -> None:
        for offer in itertools.permutations([CHEAP, MIDDLE, DEAR]):
            with self.subTest(order=[c.candidate_id for c in offer]):
                s = a_selection(candidates=list(offer))
                self.assertEqual(s.selected.candidate.candidate_id, "b-middle")

    def test_every_permutation_of_a_full_tie_selects_the_same_candidate(self) -> None:
        # The hardest case for order-dependence: all three tie on net value, two
        # of them tie on cost as well.
        tied = [
            Candidate("a-first", Money("1.00"), Probability("0.65")),
            Candidate("b-second", Money("1.00"), Probability("0.65")),
            Candidate("c-cheaper", Money("0.50"), Probability("0.625")),
        ]
        for offer in itertools.permutations(tied):
            with self.subTest(order=[c.candidate_id for c in offer]):
                s = a_selection(candidates=list(offer))
                self.assertEqual(
                    {a.net_expected_value for a in s.assessments}, {Money("2.00")}
                )
                self.assertEqual(s.selected.candidate.candidate_id, "c-cheaper")

    def test_the_assessments_follow_the_offer_order(self) -> None:
        # Selection is order-independent; the record is not, and must reproduce
        # the offer as given.
        s = a_selection(candidates=[DEAR, CHEAP, MIDDLE])
        self.assertEqual(
            [a.candidate.candidate_id for a in s.assessments],
            ["c-dear", "a-cheap", "b-middle"],
        )


class IneligibleCandidatesTests(unittest.TestCase):
    def test_an_ineligible_candidate_cannot_win_however_good(self) -> None:
        # Consumed, and would otherwise outrank everything on offer.
        best = Candidate("a-consumed", Money("0.50"), Probability("0.95"))
        s = a_selection(
            candidates=[best, MIDDLE], consumed_candidate_ids={"a-consumed"}
        )
        self.assertEqual(s.selected.candidate.candidate_id, "b-middle")
        rejected = s.rejected[0]
        self.assertEqual(rejected.candidate.candidate_id, "a-consumed")
        self.assertGreater(rejected.net_expected_value, s.selected.net_expected_value)

    def test_rejected_candidates_keep_their_figures(self) -> None:
        s = a_selection(remaining_budget=Money("1.50"))
        dear = next(a for a in s.assessments if a.candidate.candidate_id == "c-dear")
        self.assertIn(Ineligibility.BUDGET, dear.failed_conditions)
        self.assertEqual(dear.incremental_expected_value, Money("5.00"))
        self.assertEqual(dear.net_expected_value, Money("1.00"))

    def test_the_budget_limits_which_candidates_can_win(self) -> None:
        s = a_selection(remaining_budget=Money("0.50"))
        self.assertEqual(s.selected.candidate.candidate_id, "a-cheap")


class StopTests(unittest.TestCase):
    """§2.5 — stopping is a first-class successful behaviour."""

    def test_no_candidates_offered_stops(self) -> None:
        s = a_selection(candidates=[])
        self.assertIs(s.outcome, SelectionOutcome.STOP)
        self.assertTrue(s.stopped)
        self.assertIsNone(s.selected)
        self.assertEqual(s.assessments, ())

    def test_all_ineligible_stops(self) -> None:
        s = a_selection(remaining_budget=Money("0.05"))
        self.assertTrue(s.stopped)
        self.assertEqual(len(s.rejected), 3)

    def test_the_step_ceiling_stops_with_budget_to_spare(self) -> None:
        # Criterion 21, criterion 22.
        s = a_selection(
            remaining_budget=Money("1000000.00"),
            capability_step_count=4,
            max_capability_steps=4,
        )
        self.assertTrue(s.stopped)
        for assessment in s.assessments:
            self.assertEqual(
                assessment.failed_conditions, (Ineligibility.STEP_CEILING,)
            )

    def test_a_stop_is_not_an_exception(self) -> None:
        self.assertIsInstance(a_selection(candidates=[]), Selection)


class ZeroCostOnlyOfferTests(unittest.TestCase):
    """Criterion 18, demonstrated at the selector — CODEX-PR026-03.

    §4 criterion 18: "a set consisting only of zero-cost candidates yields
    STOP". Proving separately that `Candidate` refuses zero, that eligibility
    refuses zero, and that some unrelated all-ineligible set stops, does not
    demonstrate that outcome. This does.

    The malformed candidate is built with `object.__setattr__`, the technique
    `_immutable.py` documents and `tests/test_eligibility.py` already uses to
    exercise the §2.5 A defence in depth.
    """

    def _free_candidate(self, candidate_id: str) -> Candidate:
        candidate = Candidate(candidate_id, Money("0.50"), Probability("0.80"))
        object.__setattr__(candidate, "cost", Money("0.00"))
        return candidate

    def test_an_offer_of_only_zero_cost_candidates_stops(self) -> None:
        offer = [self._free_candidate("a-free"), self._free_candidate("b-free")]
        s = a_selection(candidates=offer)
        self.assertIs(s.outcome, SelectionOutcome.STOP)
        self.assertIsNone(s.selected)
        self.assertEqual(len(s.assessments), 2)
        for assessment in s.assessments:
            self.assertIn(
                Ineligibility.COST_NOT_POSITIVE, assessment.failed_conditions
            )

    def test_it_stops_however_attractive_the_free_candidates_are(self) -> None:
        # Certain success, free: the single most tempting thing that could be
        # offered, and the one that would never terminate.
        candidate = Candidate("a-free", Money("0.50"), Probability("1"))
        object.__setattr__(candidate, "cost", Money("0.00"))
        s = a_selection(candidates=[candidate])
        self.assertTrue(s.stopped)

    def test_a_priced_candidate_alongside_them_still_wins(self) -> None:
        # The stop must come from the zero cost, not from the offer being odd.
        s = a_selection(candidates=[self._free_candidate("a-free"), MIDDLE])
        self.assertEqual(s.selected.candidate.candidate_id, "b-middle")


class SafetyStopTests(unittest.TestCase):
    """§8 — a safety stop must not read as a verdict on value."""

    def test_a_step_ceiling_stop_carries_no_economic_judgement(self) -> None:
        s = a_selection(capability_step_count=4, max_capability_steps=4)
        self.assertTrue(s.stopped_without_economic_judgement)
        self.assertIn("safety stop", s.reason)

    def test_a_budget_stop_does_carry_one(self) -> None:
        s = a_selection(remaining_budget=Money("0.05"))
        self.assertFalse(s.stopped_without_economic_judgement)
        self.assertNotIn("safety stop", s.reason)

    def test_an_all_consumed_stop_is_a_safety_stop(self) -> None:
        s = a_selection(
            consumed_candidate_ids={"a-cheap", "b-middle", "c-dear"}
        )
        self.assertTrue(s.stopped_without_economic_judgement)

    def test_an_empty_offer_is_not_a_safety_stop(self) -> None:
        # Nothing was refused, so there is no refusal to characterize.
        s = a_selection(candidates=[])
        self.assertTrue(s.stopped)
        self.assertFalse(s.stopped_without_economic_judgement)

    def test_a_selection_is_not_a_stop_of_any_kind(self) -> None:
        self.assertFalse(a_selection().stopped_without_economic_judgement)

    def test_a_mixed_stop_is_not_a_safety_stop(self) -> None:
        # One candidate refused ONLY by a safeguard, another ONLY on economics.
        # A real verdict was reached on at least one, so the stop is not a
        # safety stop — "all refusals were safeguards", never "any of them was".
        safeguard_only = MIDDLE  # affordable and worth buying, but consumed
        economic_only = Candidate("d-breakeven", Money("1.00"), Probability("0.55"))
        s = a_selection(
            candidates=[safeguard_only, economic_only],
            consumed_candidate_ids={"b-middle"},
        )
        self.assertTrue(s.stopped)

        by_id = {a.candidate.candidate_id: a for a in s.assessments}
        self.assertEqual(
            by_id["b-middle"].failed_conditions, (Ineligibility.CONSUMED,)
        )
        self.assertTrue(by_id["b-middle"].refused_without_economic_judgement)
        self.assertEqual(
            by_id["d-breakeven"].failed_conditions, (Ineligibility.VALUE,)
        )
        self.assertFalse(by_id["d-breakeven"].refused_without_economic_judgement)

        self.assertFalse(s.stopped_without_economic_judgement)
        self.assertNotIn("safety stop", s.reason)


class RecordTests(unittest.TestCase):
    """§8 — the decision must be recomputable from what it recorded."""

    def test_the_decision_level_inputs_are_carried(self) -> None:
        s = a_selection(consumed_candidate_ids=["z", "a"], capability_step_count=2)
        self.assertEqual(s.current_success_probability, Probability("0.50"))
        self.assertEqual(s.task_value, Money("20.00"))
        self.assertEqual(s.remaining_budget, Money("10.00"))
        self.assertEqual(s.consumed_candidate_ids, ("a", "z"))
        self.assertEqual(s.capability_step_count, 2)
        self.assertEqual(s.max_capability_steps, 4)

    def test_inputs_survive_an_empty_offer(self) -> None:
        # With no assessments to read them from, the selection must carry them.
        s = a_selection(candidates=[], capability_step_count=3)
        self.assertEqual(s.remaining_budget, Money("10.00"))
        self.assertEqual(s.capability_step_count, 3)
        self.assertEqual(s.consumed_candidate_ids, ())

    def test_the_reason_names_the_winner_and_its_value(self) -> None:
        reason = a_selection().reason
        self.assertIn("b-middle", reason)
        self.assertIn("$2.00", reason)

    def test_the_reason_says_when_nothing_was_offered(self) -> None:
        self.assertIn("no capability was offered", a_selection(candidates=[]).reason)

    def test_eligible_and_rejected_partition_the_assessments(self) -> None:
        s = a_selection(remaining_budget=Money("1.50"))
        self.assertEqual(len(s.eligible) + len(s.rejected), len(s.assessments))


class OfferValidationTests(unittest.TestCase):
    """§2.2's boundary checks, applied to the supplied assessments."""

    def test_duplicate_identifiers_are_refused(self) -> None:
        twin = Candidate("a-cheap", Money("2.00"), Probability("0.90"))
        with self.assertRaises(ValueError):
            a_selection(assessments=assessed([CHEAP, twin]))

    def test_an_unordered_collection_of_assessments_is_refused(self) -> None:
        with self.assertRaises(TypeError):
            a_selection(assessments=set(assessed([CHEAP, MIDDLE])))

    def test_the_collection_must_hold_assessments(self) -> None:
        with self.assertRaises(TypeError):
            a_selection(assessments=[assessed([CHEAP])[0], CHEAP])

    def test_caller_mutation_afterwards_cannot_change_the_record(self) -> None:
        supplied = list(assessed([CHEAP, MIDDLE]))
        s = a_selection(assessments=supplied)
        supplied.append(assessed([DEAR])[0])
        self.assertEqual(len(s.assessments), 2)


class ScopeTests(unittest.TestCase):
    def test_nothing_is_executed_evaluated_or_advanced(self) -> None:
        # §2.7: the step count and consumed set are inputs, never state kept.
        exported = set(vars(selection_module))
        for absent in ("execute", "evaluate", "generate", "advance", "consume"):
            self.assertNotIn(absent, exported)

    def test_the_selector_keeps_no_memory_between_decisions(self) -> None:
        first = a_selection()
        second = a_selection()
        self.assertEqual(first.reason, second.reason)
        self.assertEqual(
            first.selected.candidate.candidate_id,
            second.selected.candidate.candidate_id,
        )

    def test_selecting_a_candidate_does_not_consume_it(self) -> None:
        # Advancing the run is the loop's job, and the loop does not exist yet.
        s = a_selection()
        self.assertEqual(s.consumed_candidate_ids, ())
        self.assertEqual(s.capability_step_count, 0)

    def test_the_success_condition_is_never_consulted(self) -> None:
        # §2.5's other terminal condition is answered before selection, by a
        # layer this module is not told about.
        import inspect

        parameters = set(inspect.signature(select_capability).parameters)
        for absent in ("success_condition", "evaluation", "verdict", "task"):
            self.assertNotIn(absent, parameters)

    def test_no_provider_or_payment_concept_appears(self) -> None:
        import pathlib

        text = pathlib.Path(selection_module.__file__).read_text().lower()
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


class PrecomputedAssessmentsTests(unittest.TestCase):
    """CODEX-PR023-01 — ranking consumes assessments; it does not produce them."""

    def test_the_caller_supplies_precomputed_assessments(self) -> None:
        supplied = assessed([CHEAP, MIDDLE, DEAR])
        s = select_capability(assessments=supplied, **STATE)
        self.assertEqual(s.assessments, supplied)
        self.assertEqual(s.selected.candidate.candidate_id, "b-middle")

    def test_selection_never_calls_assess(self) -> None:
        # If ranking reaches for the eligibility rule, this explodes.
        supplied = assessed([CHEAP, MIDDLE, DEAR])

        def explode(*args, **kwargs):
            raise AssertionError("selection must not call assess()")

        original = eligibility_module.assess
        patched = [
            m for m in (selection_module, eligibility_module)
            if getattr(m, "assess", None) is original
        ]
        for module in patched:
            module.assess = explode
        try:
            s = select_capability(assessments=supplied, **STATE)
        finally:
            for module in patched:
                module.assess = original

        self.assertEqual(s.selected.candidate.candidate_id, "b-middle")

    def test_the_eligibility_rule_is_not_reachable_from_selection(self) -> None:
        self.assertNotIn("assess", set(vars(selection_module)))

    def test_supplied_assessments_are_unchanged_value_for_value(self) -> None:
        supplied = assessed([CHEAP, MIDDLE, DEAR])
        before = [
            (
                a.candidate.candidate_id,
                a.candidate.cost,
                a.candidate.success_probability,
                a.incremental_expected_value,
                a.net_expected_value,
                a.failed_conditions,
                a.consumed_candidate_ids,
                a.capability_step_count,
                a.max_capability_steps,
                a.reason,
            )
            for a in supplied
        ]
        select_capability(assessments=supplied, **STATE)
        after = [
            (
                a.candidate.candidate_id,
                a.candidate.cost,
                a.candidate.success_probability,
                a.incremental_expected_value,
                a.net_expected_value,
                a.failed_conditions,
                a.consumed_candidate_ids,
                a.capability_step_count,
                a.max_capability_steps,
                a.reason,
            )
            for a in supplied
        ]
        self.assertEqual(before, after)

    def test_the_same_assessment_objects_come_back(self) -> None:
        supplied = assessed([CHEAP, MIDDLE])
        s = select_capability(assessments=supplied, **STATE)
        for original, recorded in zip(supplied, s.assessments):
            self.assertIs(original, recorded)

    def test_supplied_candidates_are_unchanged(self) -> None:
        before = [
            (c.candidate_id, c.cost, c.success_probability)
            for c in (CHEAP, MIDDLE, DEAR)
        ]
        select_capability(assessments=assessed([CHEAP, MIDDLE, DEAR]), **STATE)
        self.assertEqual(
            [(c.candidate_id, c.cost, c.success_probability)
             for c in (CHEAP, MIDDLE, DEAR)],
            before,
        )

    def test_duplicate_ids_are_rejected_without_recomputing_eligibility(self) -> None:
        twin = Candidate("a-cheap", Money("2.00"), Probability("0.90"))
        supplied = assessed([CHEAP, twin])

        def explode(*args, **kwargs):
            raise AssertionError("selection must not call assess()")

        original = eligibility_module.assess
        eligibility_module.assess = explode
        try:
            with self.assertRaises(ValueError):
                select_capability(assessments=supplied, **STATE)
        finally:
            eligibility_module.assess = original

    def test_an_ineligible_supplied_assessment_cannot_win(self) -> None:
        best = Candidate("a-consumed", Money("0.50"), Probability("0.95"))
        supplied = assessed(
            [best, MIDDLE], consumed_candidate_ids={"a-consumed"}
        )
        s = select_capability(
            assessments=supplied,
            **{**STATE, "consumed_candidate_ids": {"a-consumed"}},
        )
        self.assertEqual(s.selected.candidate.candidate_id, "b-middle")
        self.assertGreater(
            supplied[0].net_expected_value, s.selected.net_expected_value
        )

    def test_order_independence_survives_the_refactor(self) -> None:
        for order in itertools.permutations([CHEAP, MIDDLE, DEAR]):
            with self.subTest(order=[c.candidate_id for c in order]):
                s = select_capability(assessments=assessed(order), **STATE)
                self.assertEqual(s.selected.candidate.candidate_id, "b-middle")


class ConsumedIdsSurviveAnEmptyOfferTests(unittest.TestCase):
    """CODEX-PR023-02 — consumed identifiers are run state, not offer state."""

    def test_an_empty_offer_preserves_non_empty_consumed_ids(self) -> None:
        s = a_selection(assessments=[], consumed_candidate_ids=["z-late", "a-early"])
        self.assertTrue(s.stopped)
        self.assertEqual(s.consumed_candidate_ids, ("a-early", "z-late"))

    def test_an_empty_offer_with_nothing_consumed_stays_empty(self) -> None:
        s = a_selection(assessments=[], consumed_candidate_ids=[])
        self.assertEqual(s.consumed_candidate_ids, ())

    def test_consumed_ids_are_not_inferred_from_the_offer(self) -> None:
        # Nothing on offer was consumed, but something else in the run was.
        s = a_selection(consumed_candidate_ids=["x-elsewhere"])
        self.assertEqual(s.consumed_candidate_ids, ("x-elsewhere",))
        self.assertNotIn(
            s.selected.candidate.candidate_id, s.consumed_candidate_ids
        )

    def test_caller_mutation_after_the_call_cannot_change_the_record(self) -> None:
        consumed = ["x-elsewhere"]
        s = a_selection(assessments=[], consumed_candidate_ids=consumed)
        consumed.append("a-cheap")
        self.assertEqual(s.consumed_candidate_ids, ("x-elsewhere",))

    def test_normalization_is_deterministic_on_an_empty_offer(self) -> None:
        for order in (["b", "a", "c"], {"c", "b", "a"}, ("a", "c", "b", "a")):
            s = a_selection(assessments=[], consumed_candidate_ids=order)
            self.assertEqual(s.consumed_candidate_ids, ("a", "b", "c"))


class StepCeilingPrecedenceTests(unittest.TestCase):
    """CODEX-PR023-03 — the run-level ceiling outranks any economic verdict."""

    AT_CEILING = {"capability_step_count": 4, "max_capability_steps": 4}

    def test_an_attractive_candidate_at_the_ceiling_is_a_safety_stop(self) -> None:
        s = a_selection(candidates=[MIDDLE], **self.AT_CEILING)
        self.assertTrue(s.stopped)
        self.assertTrue(s.stopped_without_economic_judgement)
        self.assertNotIn("worth buying", s.reason)

    def test_a_poor_candidate_at_the_ceiling_is_still_a_safety_stop(self) -> None:
        # Worth exactly its cost — it would fail on economics below the ceiling.
        breakeven = Candidate("d-breakeven", Money("1.00"), Probability("0.55"))
        s = a_selection(candidates=[breakeven], **self.AT_CEILING)
        self.assertTrue(s.stopped_without_economic_judgement)
        self.assertNotIn("worth buying", s.reason)

    def test_unaffordable_and_zero_uplift_at_the_ceiling_is_a_safety_stop(self) -> None:
        flat = Candidate("e-flat", Money("99.00"), Probability("0.50"))
        s = a_selection(
            candidates=[flat], remaining_budget=Money("1.00"), **self.AT_CEILING
        )
        assessment = s.assessments[0]
        self.assertIn(Ineligibility.BUDGET, assessment.failed_conditions)
        self.assertIn(Ineligibility.UPLIFT, assessment.failed_conditions)
        self.assertTrue(s.stopped_without_economic_judgement)

    def test_an_empty_offer_at_the_ceiling_is_a_safety_stop(self) -> None:
        s = a_selection(assessments=[], **self.AT_CEILING)
        self.assertTrue(s.stopped)
        self.assertTrue(s.stopped_without_economic_judgement)

    def test_the_reason_names_the_ceiling_not_the_economics(self) -> None:
        s = a_selection(**self.AT_CEILING)
        self.assertIn("capability step", s.reason)
        self.assertNotIn("worth buying", s.reason)

    def test_economic_failures_are_still_recorded_as_assessment_facts(self) -> None:
        # The ceiling overrides the run-level REASON, not the per-candidate
        # record. Both facts must survive.
        flat = Candidate("e-flat", Money("99.00"), Probability("0.50"))
        s = a_selection(
            candidates=[flat], remaining_budget=Money("1.00"), **self.AT_CEILING
        )
        conditions = s.assessments[0].failed_conditions
        self.assertIn(Ineligibility.BUDGET, conditions)
        self.assertIn(Ineligibility.STEP_CEILING, conditions)

    def test_below_the_ceiling_an_unaffordable_offer_is_an_economic_stop(self) -> None:
        s = a_selection(remaining_budget=Money("0.05"), capability_step_count=3)
        self.assertTrue(s.stopped)
        self.assertFalse(s.stopped_without_economic_judgement)
        self.assertIn("worth buying", s.reason)

    def test_safety_and_economic_stops_stay_distinguishable(self) -> None:
        safety = a_selection(**self.AT_CEILING)
        economic = a_selection(remaining_budget=Money("0.05"))
        self.assertTrue(safety.stopped_without_economic_judgement)
        self.assertFalse(economic.stopped_without_economic_judgement)
        self.assertNotEqual(safety.reason, economic.reason)

    def test_the_ceiling_is_visible_on_the_record(self) -> None:
        s = a_selection(**self.AT_CEILING)
        self.assertTrue(s.ceiling_reached)
        self.assertFalse(a_selection().ceiling_reached)


class ImmutabilityTests(unittest.TestCase):
    def test_ordinary_assignment_is_refused(self) -> None:
        s = a_selection()
        with self.assertRaises(Exception):
            s.reason = "something else"

    def test_rehydration_is_refused(self) -> None:
        with self.assertRaises(TypeError):
            a_selection().__setstate__({"reason": "something else"})

    def test_there_is_no_instance_dictionary(self) -> None:
        self.assertFalse(hasattr(a_selection(), "__dict__"))

    def test_the_assessments_cannot_be_appended_to(self) -> None:
        with self.assertRaises(AttributeError):
            a_selection().assessments.append(None)


class DoctestTests(unittest.TestCase):
    def test_module_doctests_pass(self) -> None:
        results = doctest.testmod(selection_module, verbose=False)
        self.assertEqual(results.failed, 0)
        self.assertGreater(results.attempted, 0)


if __name__ == "__main__":
    unittest.main()
