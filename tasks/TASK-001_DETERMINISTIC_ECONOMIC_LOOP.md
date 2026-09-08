# TASK-001 — Deterministic Economic Loop

**Status:** **Implemented and merged.** All seventeen acceptance criteria met; 242 tests pass on Python 3.12.
**Delivered by:** PR #3, #6, #9, #11, #12, #13. Independently reviewed across 13 passes, which raised 43 findings, all corrected. The final round of corrections was merged without a further review.
**Authorization:** Authorized by the human product owner
**Traces to:** [`PREREQ-001`](../docs/PREREQ-001_PRODUCT_DEFINITION.md) §5
**Bounded by:** [`ARCHITECTURE.md`](../docs/ARCHITECTURE.md)

---

## 1. Purpose

Build the smallest complete, honest version of Radhanite's economic decision
loop, end to end, with **no external dependencies and no real inference**.

The point of this task is to prove that the economic reasoning — allocate,
attempt, evaluate, escalate or stop — works and can be inspected. It is not to
demonstrate intelligence. Execution is simulated precisely so that the economic
decisions can be tested deterministically and reviewed on their own merits.

If this loop is not correct and auditable, no integration built on top of it can
be trusted.

## 2. Scope — the authorized pipeline

TASK-001 covers exactly this pipeline and nothing else:

```
task
  → deterministic strategy selection
  → simulated execution
  → outcome evaluation
  → economic escalation/stop decision
  → run record
```

### 2.1 Task
A task is accepted with the five inputs from PREREQ-001 §4: the work to be done,
a budget, a task value, constraints, and a measurable success condition.

```
task + budget + task_value + constraints + success condition
```

`budget` and `task_value` are separate quantities and neither is derived from
the other.

### 2.2 Deterministic strategy selection
Given the task and the state of the run so far, select an execution strategy by
**fixed, inspectable rules**. Given identical inputs, selection must produce an
identical result every time.

Each strategy is a **declared fixture** — a fixed set of constants stating its
costs and its success probabilities. For example:

```
Strategy:                       Progressive Escalation
Initial success probability:    0.55
Escalated success probability:  0.85
Initial cost:                   $0.10
Escalation cost:                $0.40
```

**These constants must not be estimated, learned, inferred, or updated from run
history.** They are test fixtures and declared benchmark assumptions, used purely
to prove the economic mechanism works. They are not measurements, and no
document or output may present them as measured performance.

The future product will learn these values from benchmark history. That is
`BL-06` in [`BACKLOG.md`](BACKLOG.md) and is **unauthorized future scope**.

### 2.3 Simulated execution
Execute the selected strategy against a **simulator**, not a model. The
simulator produces an outcome and a cost. It must be deterministic and
controllable, so that success, failure, and partial-progress scenarios can each
be exercised on demand in tests.

The simulator stands in for the eventual inference layer. It is a test fixture
for the economics, not a model of intelligence, and must not pretend to be one.

### 2.4 Outcome evaluation
Compare the outcome against the task's measurable success condition and produce
an objective verdict. Evaluation reports what happened. It does not interpret,
soften, or infer partial success that the condition does not define.

### 2.5 Economic escalation/stop decision
From the verdict, the spend so far, and the remaining budget, decide exactly one
of:

- **Succeeded** — the success condition is met. Stop and report success.
- **Escalate** — further expenditure is economically justified. Continue, with
  an allocation for the next attempt.
- **Stop** — further expenditure is not economically justified, or the budget
  cannot cover another attempt. Terminate and report the task incomplete.

#### The escalation rule

**Decided by the human product owner. This is the rule; it is not open to
reinterpretation by the implementing agent.**

> Escalate if the expected incremental value of the next action is greater than
> its incremental cost, and the action fits within the remaining budget.

First calculate the incremental expected value of the escalation under
consideration:

```
incremental_expected_value =
    (post_escalation_success_probability - current_success_probability) × task_value
```

Then **escalate if and only if both** conditions hold:

```
remaining_budget >= escalation_cost

incremental_expected_value > escalation_cost
```

Otherwise, **stop**.

#### Worked example

```
task_value                              = $20.00
current_success_probability             = 0.50
post_escalation_success_probability     = 0.80
escalation_cost                         = $0.50

incremental_expected_value = (0.80 - 0.50) × $20.00 = $6.00

remaining_budget >= $0.50                 → satisfied
$6.00 > $0.50                             → satisfied

Decision: ESCALATE
```

Spend $0.50 to gain $6.00 of expected value. This is the first genuine
Radhanite economic decision, and this example should be reproducible by the
implementation as a test.

#### Properties of the rule that must be preserved

These follow from the rule as stated and must survive implementation:

- **The test is marginal, not cumulative.** It compares the *next* purchase
  against the *gain from that purchase*. Spend already incurred does not appear
  in either condition. Sunk cost must not influence the decision — an
  implementation that factors in total spend to date has changed the rule.
- **Ties do not escalate.** The value condition is a strict `>`. When the
  incremental expected value exactly equals the escalation cost, the decision is
  Stop.
- **No expected improvement means Stop.** If
  `post_escalation_success_probability` is not greater than
  `current_success_probability`, `incremental_expected_value` is zero or
  negative and the condition fails. This is how the loop terminates when no
  better strategy is available, and it requires no special case.
- **The budget ceiling is enforced structurally.** The first condition is
  checked against the cost of the escalation being considered, so the ceiling
  cannot be breached by a decision that passes the rule.
- **Budget and value never substitute for each other.** `budget` appears only in
  the first condition; `task_value` only in the second. An implementation that
  uses one in place of the other has destroyed the economic model.
- **All quantities are recorded.** `remaining_budget`, `escalation_cost`, both
  probabilities, `task_value`, and the computed `incremental_expected_value` are
  written into the run record for every escalate-or-stop decision, along with
  which condition failed when the decision was Stop. A decision that cannot be
  recomputed from the run record does not satisfy §2.6.

Requirements:

- The budget is a hard ceiling. The loop must never exceed it.
- Stopping is a correct, successful outcome of the system, not an error.
- Every decision must record **why** it was made, in terms a human can read.

### 2.6 Run record
Every run produces an inspectable record: the inputs, each attempt, the strategy
chosen and why, the cost incurred, the evaluation verdict, the decision taken
and why, and the final outcome with total spend.

The run record is held in memory during execution and written as a **JSON file
per completed run**, for example:

```
runs/run-001.json
```

containing the task inputs, the strategy chosen and why, spend, every decision
with its reason and quantities, and the final outcome. No database.

The run record is a deliverable of equal weight to the loop itself. PREREQ-001
§8 requires that every economic decision can be inspected and explained after
the fact; the run record is how that requirement is met.

## 3. Out of scope — explicitly not authorized

None of the following may be implemented, imported, stubbed, configured, or
prepared for in TASK-001:

| Excluded | Note |
|---|---|
| OpenRouter | No client, no routing, no config, no dependency. |
| Real model APIs | No provider calls of any kind. No network calls to any model. |
| Privy | No wallets, custody, keys, auth, or permission system. |
| Arc / USDC | No tokens, transfers, balances, or settlement. Budget is an internal number. |
| Hedera | No ledger, no account, no dependency. |
| x402 | No payment protocol, no metered or payable endpoint. |
| Production UI | No product UI. A minimal developer-facing entry point is acceptable. |
| Machine learning | No learned components of any kind. |
| Contextual bandits | Not authorized. Selection is deterministic rules only. |
| Reinforcement learning | Not authorized. No policy learning, no reward optimization. |
| Database / persistent store | Run records are JSON files. No database, no ORM, no migrations. |
| Learned or inferred probabilities | Strategy probabilities are static declared constants (§2.2). |

**Selection and escalation in TASK-001 are deterministic rules.** Any adaptive,
probabilistic, or learned decision-making is a separate future task and is not
authorized here. See [`BACKLOG.md`](BACKLOG.md).

## 4. Acceptance criteria

TASK-001 is complete when all of the following hold:

1. A task with all five inputs — including `task_value` — can be submitted and
   run end to end, with `task_value` not derived from `budget`.
2. Strategy selection is deterministic: identical inputs produce an identical
   selection, demonstrated by a test.
3. Simulated execution can be driven to produce success, failure, and
   partial-progress outcomes on demand.
4. Evaluation produces an objective verdict against the stated success
   condition.
5. The escalate-or-stop decision implements the rule in §2.5 exactly — the
   `incremental_expected_value` calculation and both conditions, in the stated
   form — and nothing else influences it.
6. The worked example in §2.5 reproduces exactly: $20.00 value, 0.50 → 0.80,
   $0.50 cost, yielding $6.00 incremental expected value and an ESCALATE
   decision. Demonstrated by a test.
7. The loop escalates when both conditions hold.
8. The loop stops when the value condition fails, **without** exhausting the
   budget, and reports the task incomplete and honestly.
9. The loop stops when the budget condition fails.
10. The equality boundary is correct: when `incremental_expected_value` exactly
    equals `escalation_cost`, the decision is Stop. Demonstrated by a test.
11. The no-improvement case is correct: when the next strategy offers no
    probability gain, the decision is Stop, with no special-case code path.
12. The budget ceiling is never exceeded under any tested path.
13. Strategy probabilities and costs are static declared constants, with no
    runtime estimation and no updating from prior runs.
14. Every run produces a JSON run record containing the reason for every
    decision, all quantities from §2.5, and, for a Stop, which condition failed.
15. Tests cover, at minimum: the success path, the stop-on-unjustified-spend
    path, the budget-exhaustion path, the equality boundary, the worked example,
    and determinism of selection.
16. No excluded item from §3 appears anywhere in the implementation or its
    dependencies.
17. Repository tests pass.

Criterion 8 deserves emphasis: a run that stops early with budget remaining is a
**pass**, not a failure. Any implementation that treats early stopping as an
error condition does not satisfy this task.

## 5. Deliverables

1. The economic loop implementing §2.1–§2.6, in Python 3.12.
2. A deterministic execution simulator usable as a test fixture, with strategy
   fixtures declaring static costs and success probabilities.
3. A test suite covering acceptance criterion 15.
4. A short plain-English document describing how a run is structured and how to
   read a run record.
5. A developer-facing way to run one task end to end and write its JSON run
   record.

## 6. Decisions

**All open decisions are resolved. Implementation is unblocked.**

Every decision below was made by the human product owner. The implementing agent
does not reinterpret, tune, or "improve" any of them.

### 6.1 The escalation rule ✅

Resolved. Stated in §2.5, with a worked example. Binding as written, including
the strict `>` on the value condition.

### 6.2 `task_value` as a fifth input ✅

Resolved. `task_value` is a **fifth explicit, user-supplied input**. The V1 input
contract is:

```
task + budget + task_value + constraints + success condition
```

- `budget` is the maximum permitted expenditure.
- `task_value` is the user's declared economic value of successful completion.

They remain separate, and `task_value` **must not** be derived from `budget`.
`PREREQ-001` §4 has been updated to make this part of the product definition.

### 6.3 Strategy probabilities ✅

Resolved. Success probabilities and costs are **static declared constants**
attached to deterministic strategy fixtures (§2.2). They must not be estimated,
learned, inferred, or updated from run history in TASK-001.

Adaptive estimation remains **unauthorized future scope** (`BL-05`, `BL-06`).

### 6.4 Language and runtime ✅

Resolved. **Python 3.12.**

Chosen for inspectability, ease of testing, and fit for a deterministic policy
engine. TypeScript is **not** introduced until a frontend is actually needed, and
a frontend is not authorized (`BL-10`).

### 6.5 Run record persistence ✅

Resolved. **In-memory during execution, plus a JSON run record written per
completed run** (for example `runs/run-001.json`).

**No database.** This is enough to prove auditability without inventing
infrastructure.

### 6.6 Budget unit ✅

Resolved. **USD-denominated decimal values** for TASK-001:

```
budget     = 2.00
task_value = 20.00
currency   = "USD"
```

Conceptually this becomes USDC later, when Arc is authorized. **Do not represent
these values as USDC, or name them USDC, before real USDC exists.** Simulated
numbers are not a currency, and labelling them as one would misrepresent the
system. See [`ARCHITECTURE.md`](../docs/ARCHITECTURE.md) §5.

## 7. Review notes for Codex

When reviewing an implementation of TASK-001, verify specifically:

- Selection is genuinely deterministic, with no hidden randomness or ordering
  dependence.
- The escalation rule in §2.5 is implemented **exactly** as stated: both
  conditions, `>=` on budget, strict `>` on value. A `>=` on the value condition
  is a defect, not a rounding preference.
- The decision is marginal. Total spend to date must not appear anywhere in the
  escalate-or-stop computation.
- The equality boundary stops rather than escalates, and a test proves it.
- Success probabilities are static declared constants (§6.3). Any runtime
  estimation, fitting, or cross-run updating is unauthorized scope — reject it.
- Every escalate-or-stop decision in the run record carries all quantities from
  §2.5 and, for a Stop, which condition failed.
- `task_value` is a real input, supplied by the caller and never computed from
  `budget`. The two are used in different conditions and never interchanged.
- The worked example in §2.5 is reproduced by a test and produces ESCALATE.
- Values are USD decimals and are never labelled or described as USDC.
- Run records are JSON files. No database, ORM, or migration machinery appears.
- The implementation is Python 3.12, with no TypeScript and no frontend.
- The budget ceiling holds on every path, including edge cases.
- Early stopping is implemented as a correct outcome, not an exception.
- The run record actually explains decisions, rather than logging that they
  occurred.
- **No item in §3 appears anywhere**, including in dependencies, configuration,
  comments, or abstractions built "for later."
- No behavior is claimed in documentation that the tests do not demonstrate.
