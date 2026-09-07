"""The package imports and is wired up correctly.

These tests are deliberately minimal. Their job is to prove the test command
works and that the package can be imported, so that later tests have somewhere
to stand.
"""

import unittest

import radhanite


class PackageTests(unittest.TestCase):
    def test_declares_a_version(self) -> None:
        self.assertIsInstance(radhanite.__version__, str)
        self.assertTrue(radhanite.__version__)

    def test_docstring_describes_the_product(self) -> None:
        self.assertIsNotNone(radhanite.__doc__)
        self.assertIn("economic control layer", radhanite.__doc__)
