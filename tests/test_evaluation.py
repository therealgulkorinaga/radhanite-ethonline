"""Evaluation compares, and refuses to soften.

TASK-001 §2.4: evaluation compares the outcome against the task's measurable
success condition, and does not interpret, soften, or infer partial success the
condition does not define.
"""

import doctest
import unittest

from radhanite import evaluation as evaluation_module
from radhanite.evaluation import Evaluation, Verdict, evaluate
from radhanite.execution import Attempt, Observation, ScriptedSimulator
from radhanite.strategy import DECLARED_STRATEGIES

CHEAP = DECLARED_STRATEGIES[0]
CONDITION = "tests pass"


def an_attempt(*satisfied: str, note: str = "something happened") -> Attempt:
    return ScriptedSimulator(
        [Observation(satisfied=satisfied, note=note)]
    ).execute(CHEAP, escalated=False)


class TheComparisonIsRealTests(unittest.TestCase):
    """The verdict comes from the condition, not from the attempt's own label.

    An earlier version derived the verdict from a SUCCESS/FAILURE label supplied
    by the simulator, so one attempt counted as success against *any* condition —
    including one it plainly had not met. These tests exist so that cannot
    return.
    """

    def test_the_same_attempt_judges_differently_against_different_conditions(self) -> None:
        attempt = an_attempt("tests pass", note="the suite went green")
        self.assertIs(evaluate(attempt, "tests pass").verdict, Verdict.MET)
        self.assertIs(evaluate(attempt, "issue #184 closed").verdict, Verdict.NOT_MET)
        self.assertIs(evaluate(attempt, "2 + 2 == 5").verdict, Verdict.NOT_MET)

    def test_the_note_is_never_consulted(self) -> None:
        # An attempt that describes itself as a triumph but achieved nothing is
        # still a failure. Prose must not decide anything.
        attempt = an_attempt(note="complete and total success!")
        self.assertIs(evaluate(attempt, CONDITION).verdict, Verdict.NOT_MET)

    def test_achieving_the_condition_under_another_name_does_not_count(self) -> None:
        # No synonym matching, no fuzzy comparison. Inventing either would be
        # exactly the interpretation §2.4 forbids.
        attempt = an_attempt("the tests pass")
        self.assertIs(evaluate(attempt, "tests pass").verdict, Verdict.NOT_MET)

    def test_the_evidence_is_recorded_alongside_the_verdict(self) -> None:
        result = evaluate(an_attempt("code compiles", "linter clean"), CONDITION)
        self.assertEqual(result.satisfied, frozenset({"code compiles", "linter clean"}))


class VerdictTests(unittest.TestCase):
    def test_satisfying_the_condition_meets_it(self) -> None:
        result = evaluate(an_attempt(CONDITION), CONDITION)
        self.assertIs(result.verdict, Verdict.MET)
        self.assertTrue(result.succeeded)

    def test_achieving_nothing_does_not(self) -> None:
        result = evaluate(an_attempt(), CONDITION)
        self.assertIs(result.verdict, Verdict.NOT_MET)
        self.assertFalse(result.succeeded)

    def test_the_condition_may_be_one_of_several_achieved(self) -> None:
        result = evaluate(an_attempt("code compiles", CONDITION), CONDITION)
        self.assertIs(result.verdict, Verdict.MET)


class PartialProgressIsNotSuccessTests(unittest.TestCase):
    """The most dangerous mistake available in this system.

    Softening progress into success would tell the escalation rule the task was
    finished, stop the spending, and report an outcome that never happened.
    """

    def test_achieving_something_else_is_not_meeting_the_condition(self) -> None:
        result = evaluate(an_attempt("code compiles"), CONDITION)
        self.assertIs(result.verdict, Verdict.NOT_MET)
        self.assertFalse(result.succeeded)

    def test_achieving_almost_everything_is_still_not_meeting_it(self) -> None:
        result = evaluate(
            an_attempt("code compiles", "linter clean", "types check"), CONDITION
        )
        self.assertIs(result.verdict, Verdict.NOT_MET)

    def test_progress_and_total_failure_are_distinguishable_in_the_record(self) -> None:
        # Both are NOT MET, but a run record must not lose which happened.
        progress = evaluate(an_attempt("code compiles"), CONDITION)
        nothing = evaluate(an_attempt(), CONDITION)
        self.assertEqual(progress.verdict, nothing.verdict)
        self.assertNotEqual(progress.satisfied, nothing.satisfied)
        self.assertNotEqual(progress.reason, nothing.reason)

    def test_there_is_no_third_verdict(self) -> None:
        self.assertEqual({v.name for v in Verdict}, {"MET", "NOT_MET"})


class RefusalTests(unittest.TestCase):
    def test_no_condition_means_no_judgement(self) -> None:
        # PREREQ-001 §4.5: if success cannot be measured, Radhanite cannot make
        # economic decisions about the task.
        for missing in ("", "   "):
            with self.subTest(condition=missing), self.assertRaises(ValueError):
                evaluate(an_attempt(CONDITION), missing)

    def test_something_other_than_an_attempt_is_refused(self) -> None:
        with self.assertRaises(TypeError):
            evaluate(Observation(satisfied=(), note="x"), CONDITION)


class WhitespaceTests(unittest.TestCase):
    def test_surrounding_whitespace_does_not_change_the_answer(self) -> None:
        self.assertIs(
            evaluate(an_attempt(" tests pass "), "  tests pass  ").verdict,
            Verdict.MET,
        )

    def test_the_trimmed_condition_is_what_gets_recorded(self) -> None:
        self.assertEqual(
            evaluate(an_attempt(CONDITION), "  tests pass  ").success_condition,
            "tests pass",
        )


class EvaluationRecordTests(unittest.TestCase):
    def test_ordinary_assignment_and_rehydration_are_refused(self) -> None:
        # Bounded, not absolute: object.__setattr__ and ctypes remain open by
        # design. radhanite/_immutable.py states exactly what is and is not
        # prevented.
        result = evaluate(an_attempt(CONDITION), CONDITION)
        with self.assertRaises(Exception):
            result.verdict = Verdict.NOT_MET
        with self.assertRaises(AttributeError):
            result.__dict__["verdict"] = Verdict.NOT_MET
        with self.assertRaises(TypeError):
            result.__setstate__({"verdict": Verdict.NOT_MET})

    def test_the_reason_names_the_condition_and_what_happened(self) -> None:
        for satisfied in ((CONDITION,), ("code compiles",), ()):
            with self.subTest(satisfied=satisfied):
                reason = evaluate(an_attempt(*satisfied), CONDITION).reason
                self.assertIn(CONDITION, reason)
                self.assertTrue(reason.startswith(("Met:", "Not met:")))


def load_tests(loader, tests, ignore):
    tests.addTests(
        doctest.DocTestSuite(evaluation_module, optionflags=doctest.ELLIPSIS)
    )
    return tests
