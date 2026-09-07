"""The package imports, and the runtime is the one the specification requires.

These tests are deliberately minimal. Their job is to prove the test command
works and that the package can be imported, so that later tests have somewhere
to stand.
"""

import sys
import unittest

import radhanite


class PackageTests(unittest.TestCase):
    def test_declares_a_version(self) -> None:
        self.assertIsInstance(radhanite.__version__, str)
        self.assertTrue(radhanite.__version__)

    def test_docstring_describes_the_product(self) -> None:
        self.assertIsNotNone(radhanite.__doc__)
        self.assertIn("economic control layer", radhanite.__doc__)


class RuntimeTests(unittest.TestCase):
    def test_runs_on_python_3_12(self) -> None:
        # TASK-001 §6.4 specifies Python 3.12. The `requires-python` field in
        # pyproject.toml is installation metadata only: it does not constrain
        # running the tests directly from the source tree, so on its own it
        # enforces nothing. The constraint is applied here, where it bites.
        self.assertEqual(
            sys.version_info[:2],
            (3, 12),
            f"TASK-001 §6.4 requires Python 3.12; running {sys.version.split()[0]}",
        )
