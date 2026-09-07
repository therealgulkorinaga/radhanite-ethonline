"""Radhanite — an economic control layer for autonomous AI agents.

**Partially implemented.** Radhanite is built one authorized task at a time.
See tasks/TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md for the current scope.

Implemented so far:

- ``radhanite.money.Money`` — exact US dollar amounts
- ``radhanite.task.Task`` — the five inputs a task is defined by

Not yet implemented: strategy selection, execution, outcome evaluation, the
escalate-or-stop decision, and the run record.

Intended behaviour, once complete: Radhanite is given a task, a budget, a task
value, constraints and a measurable success condition. It selects an execution
strategy, allocates expenditure across attempts, evaluates the outcome against
the success condition, and decides whether buying more intelligence is
economically justified.

See docs/PREREQ-001_PRODUCT_DEFINITION.md for the product definition.
"""

from radhanite.money import CURRENCY, Money
from radhanite.task import Task

__version__ = "0.1.0"

__all__ = ["CURRENCY", "Money", "Task", "__version__"]
