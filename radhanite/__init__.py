"""Radhanite — an economic control layer for autonomous AI agents.

**None of the behaviour described below is implemented yet.** This package
currently exports only its version number. What follows is what Radhanite is
intended to do once TASK-001 is built, not what it does today.

Intended behaviour: Radhanite is given a task, a budget, a task value,
constraints and a measurable success condition. It selects an execution
strategy, allocates expenditure across attempts, evaluates the outcome against
the success condition, and decides whether buying more intelligence is
economically justified.

See docs/PREREQ-001_PRODUCT_DEFINITION.md for the product definition and
tasks/TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md for the scope of this build.
"""

__version__ = "0.1.0"

__all__ = ["__version__"]
