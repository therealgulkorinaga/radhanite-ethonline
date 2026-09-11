# Builder handover — Claude Code → Manus

**Status:** Current as of `c24e38d` (PR #30 merged), 2026-09-11.
**Purpose:** Let the incoming implementation agent continue without
rediscovering the architecture or reopening settled decisions.

| Role | Who |
|---|---|
| Human product owner, final authority, **sole merge authority** | Arko (`therealgulkorinaga`) |
| Primary implementation agent | **Manus** (replacing Claude Code) |
| Independent review agent | Codex |
| Public implementation and audit trail | GitHub |

> **This document is a summary, not a source of truth.** Where it disagrees with
> `docs/`, `tasks/` or the code, **the repository wins** — flag the discrepancy
> rather than following this file. `AI_BUILD_GOVERNANCE.md` §4.3 says the same
> thing about PR explanations, for the same reason.

---

## 1. Product definition

**Positioning (external, current):** Radhanite is the **economic execution layer
for autonomous revenue agents**.

**Authoritative statement (`PREREQ-001` §1):** "Radhanite is the economic control
layer for autonomous work."

Both are in use and they are not in conflict — the second is the general claim,
the first is how it is being presented for ETHOnline with the revenue benchmark
in front. **`PREREQ-001` §1 is the one to build against**; `site/index.html`
uses its wording.

The distinction that defines the product, from `PREREQ-001` §1.1:

> Payment infrastructure answers **"How can the machine pay?"**
> Radhanite answers **"Should the machine pay, and what is worth buying?"**

**Current benchmark (`PREREQ-001` §6):** autonomous **revenue-opportunity
pursuit** — an agent pursuing a deal it could win, deciding what evidence and
judgement are worth buying on the way. A $50,000 opportunity, a $250 operating
budget, priced optional capabilities. Target output is exactly one of
`PURSUE` / `ABANDON` / `ESCALATE`, reached having spent what the opportunity
justified and no more.

### What Radhanite receives

- the task / opportunity
- its economic value
- an operating budget
- current success probability and state
- purchasable capability candidates

### What Radhanite decides

- whether another capability is worth buying
- which **eligible** capability has the highest economic value
- when to stop spending

### The line that must survive every refactor

> **Budget is permission to spend, not a target to spend.**

A run that buys nothing and stops is a correct run. So is a run that rejects
every marketplace service on offer.

---

## 2. Core economic rule

Authoritative: `TASK-006` §2.3 and §2.4. Reproduced exactly — **do not
paraphrase these in ways that change semantics.**

```
uplift                     = candidate_success_probability - current_success_probability
incremental_expected_value = uplift × task_value
net_expected_value         = incremental_expected_value - candidate_cost
```

### Eligibility — all six must hold

```
candidate_cost > 0
candidate_cost <= remaining_budget
candidate_success_probability > current_success_probability
incremental_expected_value > candidate_cost
candidate_id has not already been consumed in this run
capability_step_count < max_capability_steps
```

- **The strict `>` on value is load-bearing.** A candidate whose incremental
  expected value exactly equals its cost buys nothing and is ineligible. **A
  `>=` here is a defect, not a rounding preference.**
- `<=` on affordability is correct: spending the last of the budget is allowed.
- The **uplift condition is implied** by the other two given a positive cost and
  a non-negative task value. It is stated anyway as an explicit gate. **An
  implementation may not drop it on the grounds that it is redundant.**
- The first four conditions are economic. The last two are **termination
  safeguards** (`TASK-006` §2.5 B and C), as is `candidate_cost > 0` (§2.5 A).
  A run record must keep the distinction: `Ineligibility.is_economic` is
  `False` for all three.
- The step-ceiling condition is run-level, not per-candidate — when it fails it
  fails for every candidate at once, so an implementation may short-circuit to
  STOP, **provided the run record still says why**.

### Ranking among eligible candidates

1. highest **net expected value**
2. then **lower cost**
3. then **lexicographically smaller stable candidate ID**

Three levels give a **total order**, which is what makes selection independent
of the order candidates were offered in. `TASK-006` criterion 14 requires that
to be demonstrated, not asserted.

### Arithmetic

Exact decimal throughout — `Money` and `Probability`. **No float appears
anywhere on an economic path**, and the test suite enforces it.

---

## 3. Completed implementation

On `main` at `c24e38d`. **652 tests pass on Python 3.12. Zero external
dependencies** (`pyproject.toml` pins `>=3.12,<3.13`).

### Foundation — TASK-001 (delivered and merged)

`money.py`, `probability.py`, `_exactness.py`, `_immutable.py`, `task.py`,
`strategy.py`, `escalation.py`, `execution.py`, `evaluation.py`, `run.py`,
`cli.py`, `__main__.py`. The original single-task economic loop. **Unchanged
since TASK-006 began** — treat it as history, not as the current engine.

`_immutable.refuse_rehydration` and the frozen-slotted-dataclass pattern are
used by everything below.

### TASK-006 — generalized capability selection · **IMPLEMENTED, NOT CLOSED**

| File | Public API | Tests |
|---|---|---|
| `radhanite/capability.py` | `Candidate(candidate_id, cost, success_probability)`, `validate_candidates`, `DECLARED_CANDIDATES` | 47 |
| `radhanite/eligibility.py` | `Ineligibility` (enum, `.is_economic`), `Assessment`, `assess(...)` | 68 |
| `radhanite/selection.py` | `SelectionOutcome`, `Selection`, `select_capability(assessments=..., ...)` | 80 |
| `radhanite/policy.py` | `RunPolicy(max_capability_steps: int)` | 18 |

Key invariants:

- `Candidate` has **exactly three fields**. No provider, network, payee, URL or
  metadata field may be added to it.
- `Ineligibility` distinguishes economic refusals (`BUDGET`, `UPLIFT`, `VALUE`)
  from safeguards (`COST_NOT_POSITIVE`, `CONSUMED`, `STEP_CEILING`).
- `Selection` carries **every** assessment, not just the winner — a record
  showing only what was bought cannot answer why the alternatives were not.
- `RunPolicy` takes **no default** and **zero is valid**. A zero-step policy is
  a legitimate run that buys nothing. (An earlier revision refused zero; that
  was an invented product rule, corrected as `CODEX-PR026-02`.)
- The safety stop / economic stop distinction, and **the ceiling outranks every
  economic reason**.

> **Why NOT CLOSED:** criteria 10 and 13 of `TASK-006` §4 need a run loop, which
> §2.2a / §2.7 / §3 place **outside** this task. 20 of 22 criteria are directly
> demonstrated. This is an ownership inconsistency recorded in **§5a**, not a
> gap to be quietly closed in the wrong layer. Do not "finish" TASK-006 by
> satisfying those two somewhere they don't belong.

### TASK-008 — capability acquisition · **PR A IMPLEMENTED**

| File | Public API | Tests |
|---|---|---|
| `radhanite/acquisition.py` | `CapabilityDescriptor(descriptor_id, name, cost, source_reference)`, `normalize(descriptor, *, expected_post_action_success_probability)`, `acquire(offers)`, `CapabilityCatalog` | 51 |

This is **the load-bearing boundary**: descriptors in, three-field candidates
out, provider identity retained on the adapter side and never visible to the
decision. It is what lets adapters be provider-specific while TASK-006 stays
neutral.

- **Identity rule:** the candidate takes the descriptor's identifier unchanged.
  One rule, no derivation, nothing to drift.
- `CapabilityCatalog` validates in its **constructor**, not only in `acquire()`
  (`CODEX-PR029-01`).
- Duplicate identifiers are **refused, not resolved**.
- `source_reference` is opaque to Radhanite — the adapter's own handle.

**Not built:** candidate generation from task state, any provider adapter, any
network call. **Open:** §6.1, candidate identity across iterations.

### TASK-007 — capability run loop · **PR A IMPLEMENTED ONLY**

| File | Public API | Tests |
|---|---|---|
| `radhanite/runstate.py` | `RunStatus`, `RunSnapshot`, `TransitionRecord`, `RunState`, `begin_run(...)` | 125 |

The §3 **state model only**. Key invariants:

- `RunState` has exactly the eleven §3 fields; `RunSnapshot` carries all of them
  **except `history`** — that exclusion is what keeps the audit record
  non-recursive (`CODEX-PR027-02`).
- **Ledger:** `total_spend + remaining_budget == initial_budget`, with
  `0 <= remaining_budget <= initial_budget` and `0 <= total_spend <=
  initial_budget`. `total_spend` is **derived**, never supplied, and **includes
  pre-loop baseline spend**.
- **Every construction is validated** — invariants live in `__post_init__`, not
  in `begin_run()`. There is no safe-factory / unsafe-constructor split.
- **`task_state` is frozen structurally on the way in**, matched by **exact
  type**. Immutable scalars pass through; `dict`/`list`/`tuple`/`set`/
  `frozenset`/`mappingproxy` are rebuilt immutable; cycles raise `ValueError`;
  anything else — subclasses included — raises `TypeError`. **No `Enum` is
  accepted.**
- **`TransitionRecord.execution` must be `None`.** A reserved placeholder; the
  authorized execution result type arrives with PR B.
- Everything the module **retains** is matched by exact type via `_exactly()`.
  Input containers stay on `isinstance` deliberately — read once, rebuilt as a
  tuple, never retained.

**Not built:** execution, the executor interface, execution results,
committed-cost transitions, candidate consumption, step increments, task-state
updates, acquisition calls, terminal classification, retry, **and the loop
itself**.

### Specification-only — written, NOT authorized, NO code

`TASK-002` (OpenRouter), `TASK-003` (Privy — **deprioritized/superseded**),
`TASK-004` (Hedera/x402), `TASK-005` (Arc USDC), `TASK-009`, `TASK-010`,
`TASK-012`, `TASK-013`, `TASK-014`.

### Placeholder — not yet specified

`TASK-011` (The Graph).

> **Nothing in this section may be described as working that is not listed as
> implemented above.** `ARCHITECTURE.md` §6 item 9 makes a false work claim a
> boundary violation.

---

## 4. Current task roadmap

| | Task | Layer | State |
|---|---|---|---|
| 007 | Capability run loop — **remaining runtime work** | Engine | PR A merged; PR B onward outstanding |
| 009 | Revenue opportunity state / updater | Benchmark reasoning | Specified |
| 010 | Circle Marketplace + Arc / x402 / Nanopayments | Adapter | Specified |
| 011 | The Graph onchain intelligence | Adapter | Placeholder |
| 012 | Hedera independent review | Adapter | Specified |
| 013 | End-to-end revenue-agent benchmark | Assembly | Specified |
| 014 | UI / demo / submission hardening | Presentation | Specified |

**The engine does not move because the benchmark did.** TASK-006 and TASK-007
are task-agnostic and were not redesigned when the benchmark became revenue
pursuit. Everything specific to it lives in TASK-009 and the adapters.

`ARCHITECTURE.md` §4a carries this sequence with its rationale, and notes that
the table predates the `PREREQ-001` §2.3 pivot — the ordering after TASK-009 is
a live product decision, not an inheritance.

---

## 5. Sponsor architecture

Three external layers sit **beneath** Radhanite. **None of them decides
anything.** `PREREQ-001` §6.1, `ARCHITECTURE.md` §3.3–§3.5.

### Circle / Arc

- Marketplace and **service discovery**
- **Machine-readable** price and capability source — descriptors and prices
- Payment and execution of the **selected** service, through x402 /
  Nanopayments / the Agent Stack
- **Tavily and BlockRun are candidate capabilities, not mandatory workflow
  steps.** A run that rejects all of them is a correct run.

### The Graph

- Live **onchain commercial intelligence** — protocol activity, chain and
  stablecoin usage, treasury and adoption signals, contract relationships
- Produces **evidence / data**
- **Does not directly alter TASK-006 economics.** Evidence changes task state;
  task state may change a declared probability; the decision rule does not
  change.

### Hedera

- A **paid independent opportunity-review** capability
- Returns a structured **second opinion**
- **Radhanite decides whether it is worth purchasing** — like any other
  candidate, it can be rejected

> Circle tells the agent what it can buy and how to pay. The Graph and Hedera
> are things it can buy. **Radhanite decides what is worth buying.**

**None of these integrations is authorized.** Specification is not permission.

---

## 6. Architecture boundaries

**Non-negotiable unless the human product owner explicitly changes them.**

1. **TASK-006 remains provider-neutral.** Nothing entering the decision carries
   provider, network or payment identity.
2. **`Candidate` stays minimal** — exactly `candidate_id`, `cost`,
   `success_probability`.
3. **Provider metadata does not enter `Candidate`.**
4. **External descriptors and catalogues live outside `Candidate`**, in
   `acquisition.py`, on the adapter side of the TASK-008 boundary.
5. **`task_state` is opaque to TASK-007.** It is stored and passed, never
   interpreted. *Opacity is not aliasing* — it is frozen on the way in
   (`TASK-007` §3.1.1).
6. **Domain reasoning belongs outside the generic run loop** — TASK-009 and the
   adapters, never in `runstate.py`, `selection.py` or `eligibility.py`.
7. **Probabilities are benchmark-declared fixtures for the hackathon**, unless a
   later authorized task explicitly changes this. Describing them as learned,
   measured or inferred is a boundary violation (`ARCHITECTURE.md` §6 item 12).
8. **AI does not silently invent prices.**
9. **Candidate cost must be known before purchase.** Discovery / quoting costs
   nothing and precedes selection; purchase follows it. A source that cannot
   quote is not eligible.
10. **Capability order must not be hard-coded.** No sponsor sequence, no fixed
    pipeline — the order is whatever the economics produce.

### Standing prohibitions (verbatim, product owner)

- Never commit: Privy app secret; authorization key; private key;
  wallet-control secret; production credentials.
- Credentials must come from **environment variables**.
- Do not attempt to automate, bypass, scrape, or defeat the public faucet.
- Add or update `.env.example` with **placeholder names only**.
- **Do not describe simulated USD values as USDC.**
- **Do not claim Arc USDC is being settled on Hedera.** Arc and Hedera are
  separate environments (`ARCHITECTURE.md` §4b).
- **Do not merge your own work.**

`ARCHITECTURE.md` §6 lists twelve boundary violations in full. Read it.

---

## 7. Development and governance workflow

Authoritative: `docs/AI_BUILD_GOVERNANCE.md`.

1. **The human authorizes one narrowly scoped implementation step.** Scope is
   stated explicitly and is not to be widened. Specification is not permission.
2. **The implementation agent:**
   - branches from **fresh `main`**
   - writes focused **tests first** where practical
   - **runs them and confirms the expected failing state** — then records it
   - implements the **minimum** code
   - runs focused tests, then the **full suite**
   - performs **mutation / fault checks** where required
   - writes the **PR explanation** (§4, fifteen sections, committed to
     `docs/pr_explanations/`)
   - commits the **Codex review prompt before the review runs** (§7.3), in the
     same commit as the work
   - opens the PR — and **stops before merge**
3. **Codex reviews independently** for material correctness, against the task
   specs, `ARCHITECTURE.md` and the governance document — never against the PR
   explanation (§4.3).
4. **Corrections are themselves reviewed** (§7.5).
5. **The human alone authorizes and performs the merge** (§1.1).

Review status is recorded in **three places at once** (§7.4): the record in
`docs/reviews/`, the index row in `docs/reviews/README.md`, and the PR body. It
should also be stated **up front** in any report to the product owner, not
buried.

> ⚠️ **`AI_BUILD_GOVERNANCE.md` §1.2 still names "Claude Code" as the
> implementation agent.** This handover does not amend it — §8 reserves
> amendments to the human product owner. **Manus should flag this as the first
> discrepancy and ask for an authorized amendment**, rather than editing it.

---

## 8. Known lessons and traps

Every one of these was a real defect found in review on this repository.

- **`isinstance` is not an immutability guarantee.** A subclass of an immutable
  scalar is not immutable — `class Smuggler(int)` carrying a list satisfies
  `isinstance(x, int)`. Match retained values by **exact type**. Related: a
  `str` subclass **is** a `Sequence`, so a structural rule converted `"abc"` to
  `("a","b","c")` and called it the caller's state.
- **Public constructors must enforce their own invariants, or not be public.**
- **No safe-factory + unsafe-public-constructor pattern.** One safe path and one
  unsafe path is one unsafe path. (`CODEX-PR029-01`, `CODEX-PR030-01`.)
- **Mutable aliases invalidate audit records.** A caller who can still mutate
  what you stored can rewrite what an already-written record appears to say.
- **History and snapshots must stay non-recursive.** History → snapshots is
  permitted; snapshot → history is forbidden. Watch for recursion arriving
  through a loosely typed field, not only through a type.
- **Stale `__pycache__` previously invalidated mutation results** — two
  mutations falsely reported as "survived", and a genuine false pass hidden
  inside the suite. **Run mutations with `PYTHONDONTWRITEBYTECODE=1` and clear
  `__pycache__` between runs.**
- **Tests must distinguish plausible wrong implementations, not merely exercise
  happy paths.** Mutation testing is how that gets checked; a surviving mutant
  usually means a weak test, not safe code.
- **Avoid vacuous assertions.** Ones caught here: an algebraically identical sum
  comparison; an assertion about a docstring's contents; a caller-mutation test
  that passed whatever the code did; a type test that raised for the wrong
  reason and looked like it passed.
- **A source scan is not a behavioural test.** A ceiling guard "proved" by
  grepping the source was defeated by `min(value, 4)`; it was replaced with
  behavioural tests across several ceilings.
- **Never fabricate a quotation from a specification.** One review finding
  (`CODEX-PR026-04`) was a sentence attributed to a task document that had in
  fact come from a source docstring.
- **Do not invent product rules to fill a gap.** If the specification does not
  say, it is an open question for the product owner, not a default to pick.
- **Match the spec by fixing the environment**, not by shipping a deviation with
  a disclosure. (A version-guard test failed only because the suite had been run
  on Python 3.14.)

---

## 9. Repository commands

**The authoritative full test command**, from the repository root:

```
PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest discover -q
```

**Current state: `Ran 652 tests — OK`**, at `c24e38d` (PR #30 merged).

Focused runs and mutation runs:

```
PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest tests.test_runstate -q
find . -name __pycache__ -type d -exec rm -rf {} +      # before any mutation run
```

Python **3.12 only** — `pyproject.toml` pins `>=3.12,<3.13`, and a version-guard
test enforces it. **Zero external dependencies**; adding one requires explicit
authorization (`AI_BUILD_GOVERNANCE.md` §2.2).

---

## 10. Next expected task boundary

**Not authorized. Stated only so the shape of the next step is known.**

The next expected boundary is **TASK-007 PR B — the capability executor
interface and execution transitions**: the executor boundary, an authorized
execution result type (which is what `TransitionRecord.execution` is reserved
for), committed-cost accounting, candidate consumption, and the step-count
increment. `TASK-007` §7 and §3.4 describe the shape; §5.2 describes the
executor boundary.

After that, `TASK-007` still needs terminal classification (§6.1 precedence,
§6.2 classification) and the loop itself before TASK-009 becomes reachable.

> **Manus must not begin this, or any other task, until the human product owner
> issues an explicit narrowly scoped authorization.**

---

## 11. Files to read first, in order

1. `docs/BUILDER_HANDOVER_MANUS.md` — this file
2. `docs/PREREQ-001_PRODUCT_DEFINITION.md` — what the product is; §1, §4a, §5,
   §6, §6.5
3. `docs/ARCHITECTURE.md` — what Radhanite owns and does not; §2.2, §3, §4a,
   §4b, **§6**
4. `tasks/TASK-006_GENERALIZED_CAPABILITY_SELECTION.md` — the economic rule;
   §2.3, §2.4, §2.5, §4, **§5a**
5. `tasks/TASK-007_CAPABILITY_RUN_LOOP.md` — §3, §3.1.1, §3.3, §3.4, §4, §5, §6,
   §7
6. `tasks/TASK-008_CAPABILITY_ACQUISITION.md` — the neutrality boundary
7. `docs/AI_BUILD_GOVERNANCE.md` — §1, §2, §3, §4, §7
8. `tasks/BACKLOG.md` and the `tasks/` index — what is open
9. `docs/reviews/README.md` — every review outcome and correction to date

Then read the code and its tests, in this order:
`capability.py` → `eligibility.py` → `selection.py` → `policy.py` →
`acquisition.py` → `runstate.py`, each with its `tests/test_*.py`.

`docs/pr_explanations/` holds the reasoning behind each merged change. It is
explanatory, **not authoritative** (§4.3).
