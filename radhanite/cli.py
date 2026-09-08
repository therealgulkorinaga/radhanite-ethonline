"""Run one task end to end and write its record.

TASK-001 §5 deliverable 5. A developer-facing entry point, not a product
interface — production UI is excluded by §3.

    python -m radhanite

It runs three scenarios against the same task and writes a JSON record for each
into `runs/`. The scenarios are scripted, because execution is simulated (§2.3):
what varies between them is what the work achieves, and what that reveals is how
the economics respond.
"""

from __future__ import annotations

import sys
from pathlib import Path

from radhanite.execution import Observation, ScriptedSimulator
from radhanite.money import Money
from radhanite.run import RunRecord, run
from radhanite.strategy import DECLARED_STRATEGIES
from radhanite.task import Task

__all__ = ["main"]

TASK = Task(
    description="Fix GitHub issue #184",
    budget=Money("2.00"),
    task_value=Money("20.00"),
    success_condition="tests pass",
    constraints=("no dependency changes",),
)

WON = Observation(satisfied=("tests pass",), note="the suite went green")
PARTIAL = Observation(satisfied=("code compiles",), note="it builds, tests still red")
LOST = Observation(satisfied=(), note="nothing worked")

SCENARIOS: tuple[tuple[str, str, list[Observation]], ...] = (
    (
        "cheap win",
        "the first, cheapest attempt does the job",
        [WON],
    ),
    (
        "worth escalating",
        "the cheap attempt falls short, and buying more is justified",
        [LOST, PARTIAL, WON],
    ),
    (
        "not worth finishing",
        "nothing works, and Radhanite stops while money remains",
        [LOST] * 6,
    ),
)


def main(argv: list[str] | None = None) -> int:
    """Run every scenario, print what happened, and write the records."""
    destination = Path(argv[0]) if argv else Path("runs")
    for number, (name, blurb, script) in enumerate(SCENARIOS, start=1):
        record = run(TASK, DECLARED_STRATEGIES, ScriptedSimulator(script))
        path = record.write(destination / f"run-{number:03d}.json")
        print(f"\n{'=' * 72}\n{name} — {blurb}\n{'=' * 72}")
        print(record)
        print(f"  written to {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
