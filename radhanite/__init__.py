"""Radhanite — an economic control layer for autonomous AI agents.

**Partially implemented.** Radhanite is built one authorized task at a time.
See tasks/TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md for the current scope.

Implemented so far:

- ``radhanite.money.Money`` — exact US dollar amounts
- ``radhanite.probability.Probability`` — an exact probability of success
- ``radhanite.task.Task`` — the five inputs a task is defined by
- ``radhanite.escalation.decide`` — the escalate-or-stop rule, TASK-001 §2.5
- ``radhanite.strategy`` — declared strategy fixtures and deterministic selection
- ``radhanite.execution`` — the scripted simulator standing in for real work
- ``radhanite.evaluation`` — judging an outcome against the success condition
- ``radhanite.run`` — the loop that drives them, and the run record
- ``radhanite.cli`` — a developer entry point: ``python -m radhanite``
- ``radhanite.capability`` — a priced candidate action, and the checks an offer
  must pass before a decision is made over it (TASK-006 §2.2)
- ``radhanite.eligibility`` — whether one candidate may be bought, and what
  buying it would be worth (TASK-006 §2.3)
- ``radhanite.selection`` — choosing one capability from an offer, or stopping
  (TASK-006 §2.4, §2.5)
- ``radhanite.policy`` — the ceiling a run states for itself (TASK-006 §2.2a)
- ``radhanite.acquisition`` — external capabilities become provider-neutral
  candidates (TASK-008)
- ``radhanite.runstate`` — what a capability run carries, and the snapshots
  that audit it (TASK-007 §3)
- ``radhanite.loop`` — provider-neutral candidate sourcing, task-state updating,
  and the generic TASK-007 orchestration loop
- ``radhanite.revenue`` — declared ETHOnline revenue-opportunity state, evidence,
  benchmark initializer, and TASK-007 updater (TASK-009)
- ``radhanite.circle`` — live Circle Discovery normalization and an opt-in
  Circle CLI x402/Gateway executor boundary (TASK-010)

TASK-001 is complete. TASK-006 — choosing among candidate capabilities rather
than escalating through two fixed tiers — is implemented: the candidate model,
eligibility rule, ranking, declared fixtures, and run policy exist, and
TASK-001's scenarios are demonstrated to decide identically under them. TASK-007
PR A and PR B provide the immutable run-state and one-execution foundations;
the final-loop branch adds provider-neutral candidate sourcing, task-state
updating, terminal classification, and repeated orchestration. TASK-009 adds
only the declared revenue-benchmark state and updater fixtures. TASK-010 adds
the Circle Discovery and opt-in x402/Gateway adapter boundary; no credentials
are stored and no payment runs automatically.

Intended behaviour, once complete: Radhanite is given a task, a budget, a task
value, constraints and a measurable success condition. It selects an execution
strategy, allocates expenditure across attempts, evaluates the outcome against
the success condition, and decides whether buying more intelligence is
economically justified.

See docs/PREREQ-001_PRODUCT_DEFINITION.md for the product definition.
"""

from radhanite.acquisition import (
    CapabilityCatalog,
    CapabilityDescriptor,
    acquire,
    normalize,
)
from radhanite.capability import DECLARED_CANDIDATES, Candidate, validate_candidates
from radhanite.capability_execution import (
    CapabilityExecutor,
    ExecutionResult,
    apply_execution,
)
from radhanite.circle import (
    CircleCapabilityCatalog,
    CircleCapabilityExecutor,
    CircleCliPaymentClient,
    CircleDiscoveryError,
    CircleOffer,
    CirclePaymentCommitmentUnresolvedError,
    CirclePaymentMetadataError,
    CirclePaymentReceipt,
    CirclePostAttemptError,
    CirclePreAttemptError,
    catalog_from_circle_response,
    live_circle_discovery,
)
from radhanite.eligibility import Assessment, Ineligibility, assess
from radhanite.escalation import Decision, EscalationDecision, FailedCondition, decide
from radhanite.evaluation import Evaluation, Verdict, evaluate
from radhanite.execution import Attempt, Observation, ScriptedSimulator
from radhanite.money import CURRENCY, Money
from radhanite.policy import RunPolicy
from radhanite.probability import Probability
from radhanite.revenue import (
    BENCHMARK_INITIAL_BUDGET,
    BENCHMARK_INITIAL_PROBABILITY,
    BENCHMARK_OPPORTUNITY_VALUE,
    BENCHMARK_P1_PROBABILITY,
    BENCHMARK_P2_PROBABILITY,
    RevenueOpportunityUpdater,
    benchmark_opportunity,
    initialize_benchmark_run,
    make_evidence,
)
from radhanite.loop import (
    CandidateSource,
    TaskStateUpdate,
    TaskStateUpdater,
    run_capability_loop,
)
from radhanite.run import RunOutcome, RunRecord, Step, run
from radhanite.runstate import (
    RunSnapshot,
    RunState,
    RunStatus,
    TransitionRecord,
    begin_run,
)
from radhanite.selection import Selection, SelectionOutcome, select_capability
from radhanite.strategy import DECLARED_STRATEGIES, Strategy, select
from radhanite.task import Task

__version__ = "0.1.0"

__all__ = [
    "CURRENCY",
    "DECLARED_CANDIDATES",
    "DECLARED_STRATEGIES",
    "Assessment",
    "Attempt",
    "CapabilityCatalog",
    "CapabilityDescriptor",
    "CapabilityExecutor",
    "CircleCapabilityCatalog",
    "CircleCapabilityExecutor",
    "CircleCliPaymentClient",
    "CircleDiscoveryError",
    "CircleOffer",
    "CirclePaymentCommitmentUnresolvedError",
    "CirclePaymentMetadataError",
    "CirclePaymentReceipt",
    "CirclePostAttemptError",
    "CirclePreAttemptError",
    "CandidateSource",
    "Candidate",
    "Decision",
    "EscalationDecision",
    "Evaluation",
    "ExecutionResult",
    "FailedCondition",
    "Ineligibility",
    "Observation",
    "Money",
    "RevenueOpportunityUpdater",
    "Probability",
    "RunOutcome",
    "RunSnapshot",
    "RunState",
    "RunStatus",
    "RunPolicy",
    "RunRecord",
    "Selection",
    "SelectionOutcome",
    "ScriptedSimulator",
    "Step",
    "TransitionRecord",
    "Strategy",
    "Task",
    "TaskStateUpdate",
    "TaskStateUpdater",
    "Verdict",
    "__version__",
    "acquire",
    "benchmark_opportunity",
    "initialize_benchmark_run",
    "make_evidence",
    "apply_execution",
    "begin_run",
    "catalog_from_circle_response",
    "assess",
    "decide",
    "evaluate",
    "normalize",
    "live_circle_discovery",
    "run_capability_loop",
    "run",
    "select",
    "select_capability",
    "validate_candidates",
    "BENCHMARK_INITIAL_BUDGET",
    "BENCHMARK_INITIAL_PROBABILITY",
    "BENCHMARK_OPPORTUNITY_VALUE",
    "BENCHMARK_P1_PROBABILITY",
    "BENCHMARK_P2_PROBABILITY",
]
