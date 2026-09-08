"""Evaluation is objective, and refuses to soften.

TASK-001 §2.4: evaluation reports what happened; it does not interpret, soften,
or infer partial success the condition does not define. The tests that matter
most here are the ones proving partial progress is not treated as success.
"""

import doctest
import unittest

from radhanite import evaluation as evaluation_module
from radhanite.evaluation import Evaluation, Verdict, evaluate
from radhanite.execution import Attempt, Outcome, ScriptedSimulator
from radhanite.money import Money
from radhanite.probability import Probability
from radhanite.strategy import DECLARED_STRATEGIES

CHEAP = DECLARED_STRATEGIES[0]
CONDITION = "tests pass"


def an_attempt(outcome: Outcome) -> Attempt:
    return ScriptedSimulator([outcome]).execute(CHEAP, escalated=False)


class VerdictTests(unittest.TestCase):
    def test_success_meets_the_condition(self) -> None:
        result = evaluate(an_attempt(Outcome.SUCCESS), CONDITION)
        self.assertIs(result.verdict, Verdict.MET)
        self.assertTrue(result.succeeded)

    def test_failure_does_not(self) -> None:
        result = evaluate(an_attempt(Outcome.FAILURE), CONDITION)
        self.assertIs(result.verdict, Verdict.NOT_MET)
        self.assertFalse(result.succeeded)


class PartialProgressIsNotSuccessTests(unittest.TestCase):
    """The most dangerous mistake available in this system.

    Softening partial progress into success would tell the escalation rule the
    task was finished, stop the spending, and report an outcome that never
    happened. §2.4 forbids it explicitly.
    """

    def test_partial_progress_does_not_meet_the_condition(self) -> None:
        result = evaluate(an_attempt(Outcome.PARTIAL_PROGRESS), CONDITION)
        self.assertIs(result.verdict, Verdict.NOT_MET)
        self.assertFalse(result.succeeded)

    def test_partial_progress_is_distinguished_from_outright_failure(self) -> None:
        # Both are "not met", but the record must not lose which happened.
        partial = evaluate(an_attempt(Outcome.PARTIAL_PROGRESS), CONDITION)
        failed = evaluate(an_attempt(Outcome.FAILURE), CONDITION)
        self.assertEqual(partial.verdict, failed.verdict)
        self.assertIs(partial.outcome, Outcome.PARTIAL_PROGRESS)
        self.assertIs(failed.outcome, Outcome.FAILURE)
        self.assertNotEqual(partial.reason, failed.reason)

    def test_there_is_no_third_verdict(self) -> None:
        # A "partly met" verdict is precisely what §2.4 forbids inferring.
        self.assertEqual({v.name for v in Verdict}, {"MET", "NOT_MET"})

    def test_only_success_is_ever_met(self) -> None:
        for outcome in Outcome:
            with self.subTest(outcome=outcome):
                result = evaluate(an_attempt(outcome), CONDITION)
                self.assertEqual(
                    result.succeeded, outcome is Outcome.SUCCESS
                )


class WhatIsJudgedTests(unittest.TestCase):
    def test_the_condition_being_judged_is_recorded(self) -> None:
        result = evaluate(an_attempt(Outcome.SUCCESS), "the build is green")
        self.assertEqual(result.success_condition, "the build is green")
        self.assertIn("the build is green", result.reason)

    def test_surrounding_whitespace_is_trimmed(self) -> None:
        result = evaluate(an_attempt(Outcome.SUCCESS), "  tests pass  ")
        self.assertEqual(result.success_condition, "tests pass")

    def test_the_condition_does_not_change_the_verdict(self) -> None:
        # In TASK-001 the outcome is a controlled input; the condition is what
        # the verdict is reported against, not a second thing to satisfy.
        for condition in ("tests pass", "the build is green", "issue #184 closed"):
            with self.subTest(condition=condition):
                self.assertIs(
                    evaluate(an_attempt(Outcome.SUCCESS), condition).verdict,
                    Verdict.MET,
                )


class RefusalTests(unittest.TestCase):
    def test_no_condition_means_no_judgement(self) -> None:
        # PREREQ-001 §4.5: if success cannot be measured, Radhanite cannot make
        # economic decisions about the task.
        for missing in ("", "   "):
            with self.subTest(condition=missing), self.assertRaises(ValueError):
                evaluate(an_attempt(Outcome.SUCCESS), missing)

    def test_something_other_than_an_attempt_is_refused(self) -> None:
        with self.assertRaises(TypeError):
            evaluate(Outcome.SUCCESS, CONDITION)


class EvaluationRecordTests(unittest.TestCase):
    def test_an_evaluation_cannot_be_changed_after_the_fact(self) -> None:
        result = evaluate(an_attempt(Outcome.SUCCESS), CONDITION)
        with self.assertRaises(Exception):
            result.verdict = Verdict.NOT_MET
        with self.assertRaises(TypeError):
            result.__setstate__({"verdict": Verdict.NOT_MET})

    def test_the_reason_says_what_happened_and_what_was_required(self) -> None:
        for outcome in Outcome:
            with self.subTest(outcome=outcome):
                reason = evaluate(an_attempt(outcome), CONDITION).reason
                self.assertIn(CONDITION, reason)
                self.assertTrue(reason.startswith(("Met:", "Not met:")))


def load_tests(loader, tests, ignore):
    tests.addTests(
        doctest.DocTestSuite(evaluation_module, optionflags=doctest.ELLIPSIS)
    )
    return tests
