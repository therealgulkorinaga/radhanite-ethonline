"""Radhanite — an economic control layer for autonomous AI agents.

**Partially implemented.** Radhanite is built one authorized task at a time.
See tasks/TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md for the current scope.

Implemented so far:

- ``radhanite.money.Money`` — exact US dollar amounts
- ``radhanite.probability.Probability`` — an exact probability of success
- ``radhanite.task.Task`` — the five inputs a task is defined by
- ``radhanite.escalation.decide`` — the escalate-or-stop rule, TASK-001 §2.5

Not yet implemented: strategy fixtures, strategy selection, execution, outcome
evaluation, the loop that drives them, and the run record.

Intended behaviour, once complete: Radhanite is given a task, a budget, a task
value, constraints and a measurable success condition. It selects an execution
strategy, allocates expenditure across attempts, evaluates the outcome against
the success condition, and decides whether buying more intelligence is
economically justified.

See docs/PREREQ-001_PRODUCT_DEFINITION.md for the product definition.
"""

from radhanite.escalation import Decision, EscalationDecision, FailedCondition, decide
from radhanite.money import CURRENCY, Money
from radhanite.probability import Probability
from radhanite.task import Task

__version__ = "0.1.0"

__all__ = [
    "CURRENCY",
    "Decision",
    "EscalationDecision",
    "FailedCondition",
    "Money",
    "Probability",
    "Task",
    "__version__",
    "decide",
]
