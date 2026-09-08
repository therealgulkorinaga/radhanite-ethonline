"""The developer-facing entry point runs a task end to end and writes a record.

TASK-001 §5 deliverable 5.
"""

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from radhanite.cli import SCENARIOS, TASK, main
from radhanite.money import Money


class EndToEndTests(unittest.TestCase):
    def test_running_every_scenario_writes_a_record_for_each(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with redirect_stdout(io.StringIO()):
                code = main([directory])
            self.assertEqual(code, 0)
            written = sorted(Path(directory).glob("run-*.json"))
            self.assertEqual(len(written), len(SCENARIOS))

    def test_each_record_is_readable_json_with_an_outcome(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with redirect_stdout(io.StringIO()):
                main([directory])
            for path in sorted(Path(directory).glob("run-*.json")):
                with self.subTest(record=path.name):
                    data = json.loads(path.read_text(encoding="utf-8"))
                    self.assertIn(data["outcome"], {"succeeded", "stopped"})
                    self.assertEqual(data["task"]["description"], TASK.description)
                    self.assertTrue(data["steps"])

    def test_the_scenarios_show_success_and_stopping(self) -> None:
        # A demonstration that only ever succeeded would hide the product's
        # actual claim: that it stops when spending more is not worth it.
        with tempfile.TemporaryDirectory() as directory:
            with redirect_stdout(io.StringIO()):
                main([directory])
            outcomes = {
                json.loads(p.read_text(encoding="utf-8"))["outcome"]
                for p in Path(directory).glob("run-*.json")
            }
        self.assertEqual(outcomes, {"succeeded", "stopped"})

    def test_no_scenario_ever_exceeds_the_budget(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with redirect_stdout(io.StringIO()):
                main([directory])
            for path in Path(directory).glob("run-*.json"):
                with self.subTest(record=path.name):
                    data = json.loads(path.read_text(encoding="utf-8"))
                    self.assertLessEqual(
                        Money(data["spent"]), Money(data["task"]["budget"])
                    )

    def test_it_prints_what_it_did(self) -> None:
        buffer = io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            with redirect_stdout(buffer):
                main([directory])
        printed = buffer.getvalue()
        for expected in (TASK.description, "SUCCEEDED", "STOPPED", "unspent"):
            with self.subTest(expected=expected):
                self.assertIn(expected, printed)

    def test_a_stopped_run_leaves_money_unspent(self) -> None:
        # The claim the whole product rests on.
        with tempfile.TemporaryDirectory() as directory:
            with redirect_stdout(io.StringIO()):
                main([directory])
            stopped = [
                json.loads(p.read_text(encoding="utf-8"))
                for p in Path(directory).glob("run-*.json")
                if json.loads(p.read_text(encoding="utf-8"))["outcome"] == "stopped"
            ]
        self.assertTrue(stopped)
        for data in stopped:
            with self.subTest(reason=data["reason"][:40]):
                self.assertTrue(Money(data["remaining"]).is_positive)
