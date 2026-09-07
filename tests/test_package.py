"""The package imports and is wired up correctly.

This is deliberately minimal. Its job is to prove that the test command works
and that `src/` is on the import path, so that later tests have somewhere to
stand.
"""

import radhanite


def test_package_declares_a_version() -> None:
    assert isinstance(radhanite.__version__, str)
    assert radhanite.__version__


def test_package_docstring_describes_the_product() -> None:
    assert radhanite.__doc__ is not None
    assert "economic control layer" in radhanite.__doc__
