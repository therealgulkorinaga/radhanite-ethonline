# TASK-006 — Generalized capability selection

**Status:** Specified — **NOT AUTHORIZED**
**Authorization:** None. This document specifies the work; it does not permit implementation.
**Traces to:** [`PREREQ-001`](../docs/PREREQ-001_PRODUCT_DEFINITION.md) §4a, §5.1
**Bounded by:** [`ARCHITECTURE.md`](../docs/ARCHITECTURE.md) §2.2.2, §2.2.3
**Replaces backlog entry:** `BL-13`
**Depends on:** TASK-001 complete and merged — it is

---

## 1. Purpose

Replace the assumption that a strategy is **one attempt and one escalation**
with a model in which a decision point offers **zero or more candidate
capabilities**, and the economic rule chooses among them.

```
current task state
  → zero or more candidate capabilities
  → deterministic economic selection
  → execute the selected capability, or STOP
```

A **candidate capability** is a priced action that may improve the probability
of completing the task.

This is a change to the economic policy, not a refactor. `ARCHITECTURE.md`
§2.2.3 requires it to be an authorized task of its own precisely so that it
cannot arrive inside a provider integration, and this document is that task.

**TASK-001 is not rewritten.** It remains the historical specification of the
delivered two-tier kernel. §7 below states exactly how its behaviour survives
under this model, and criterion 14 requires that to be demonstrated rather than
assumed.

## 2. Scope — the authorized model

### 2.1 The core model is provider-neutral

The decision takes a set of candidates and returns one of them, or STOP. It
knows a candidate's **identity, price and claimed effect**, and nothing else.

The following must **not** appear anywhere in the core candidate model or the
selection rule — not as a field, an enum, a branch, a name, or a comment
justifying future shape:

> Hedera · Circle · Arc · Tavily · BlockRun · OpenRouter · x402 · any wallet or
> payment concept

A capability bought over x402 on Hedera and one computed locally are
indistinguishable to the rule. That is the point: the economics decide on price
and effect, and a provider that could influence selection by being that provider
would make the layer something other than an economic one.

Encoding any of the above is a boundary violation under `ARCHITECTURE.md` §6
items 1–7.

### 2.2 Minimum candidate fields

Three fields, and the rule uses only these three:

| Field | Meaning |
|---|---|
| **stable capability ID** | Identifies the candidate. Stable across runs, unique within one decision |
| **cost** | The price of taking this action, as exact `Money` |
| **expected post-action success probability** | The declared probability of task success *after* this action, as `Probability` |

**Nothing else may enter the decision.** Descriptive or provider metadata may
exist, but only outside the core decision logic or inside a field the rule does
not read. If a proposed field would change which candidate is selected, it is
not metadata and it needs its own authorization.

**Do not overdesign this.** A fourth field added "for later" is `ARCHITECTURE.md`
§6 item 7.

**Duplicate IDs are refused at the boundary**, not resolved. The tie-break in
§2.4 terminates on ID, so two candidates sharing one would leave selection
undefined. This mirrors TASK-001's refusal of unordered strategy collections:
an input that cannot produce a deterministic answer is rejected rather than
processed into one.

### 2.2a Inputs the decision receives, beyond the candidates

A decision is not made from the candidate set alone. Four further inputs enter
it, and **none of them is a candidate**:

| Input | Where it comes from |
|---|---|
| `current_success_probability` | The **current task state**, established by the baseline execution and evaluation layer |
| `remaining_budget` | The run's ledger, already net of everything spent so far — including the baseline |
| `capability_step_count` | The run: how many capabilities have been purchased so far |
| `max_capability_steps` | **Run policy** — see §2.5 |

`task_value` is a task input under `PREREQ-001` §4.3 and is unchanged.

**`current_success_probability` is not a user input**, and it is **not**
represented as a zero-cost candidate. It is a fact about the task as it now
stands, supplied to the decision:

```
user task
  → baseline execution / evaluation
  → current task state
  → TASK-006 capability selection
```

**How that baseline state is produced is outside TASK-006.** Nothing in this
task specifies, authorizes, or constrains the execution and evaluation layer
that produces it, and no part of the implementation may reach into it. It is an
input at the boundary, exactly as the candidate set is.

**`max_capability_steps` is not a sixth user input** under `PREREQ-001` §4, and
must not become one here. It is authoritative run policy supplied to the run;
where it is configured is not settled by TASK-006 and does not need to be for
the rule to be implementable.

### 2.3 The economic rule is preserved

Unchanged from TASK-001 §2.5, applied per candidate:

```
incremental_expected_value =
    (candidate_success_probability - current_success_probability) × task_value
```

A candidate is **eligible** only when **all six** hold:

```
candidate_cost > 0
candidate_cost <= remaining_budget
candidate_success_probability > current_success_probability
incremental_expected_value > candidate_cost
candidate_id has not already been consumed in this run
capability_step_count < max_capability_steps
```

Otherwise it is **ineligible**. Ineligibility is an ordinary outcome, not an
error.

The first four are economic. The last two are the termination safeguards in
§2.5, and they are stated here as eligibility conditions because that is what
they are: a consumed candidate and an exhausted step budget make every affected
candidate unbuyable. The sixth is run-level rather than per-candidate — when it
fails, it fails for every candidate at once — so an implementation may
short-circuit to STOP without evaluating any candidate, provided the run record
still says why.

**`candidate_cost > 0` is new**, and it is a termination safeguard rather than
an economic one. See §2.5 A. A zero-cost or local action is **not a purchasable
candidate** and must not be represented as one.

**On the uplift condition.** Given the positive-cost invariant and a
non-negative `task_value`, it is implied by the incremental-value condition:
eligibility requires `incremental_expected_value > candidate_cost > 0`, and a
positive incremental value with a non-negative task value requires a positive
uplift. It is stated anyway, as an explicit gate — it makes the intent checkable
at review, and it holds the invariant if those constraints are ever revisited.
An implementation may not drop it on the grounds that it is redundant.

**The strict `>` on value is load-bearing**, exactly as in TASK-001. A candidate
whose incremental expected value exactly equals its cost buys nothing and is
ineligible. A `>=` here is a defect, not a rounding preference.

### 2.4 Selection among eligible candidates

For every eligible candidate:

```
net_expected_value = incremental_expected_value - candidate_cost
```

**Select the candidate with the highest net expected value.** Ties are broken
deterministically, in this order:

| | Rule |
|---|---|
| 1 | Higher `net_expected_value` wins |
| 2 | If exactly equal — **lower cost** wins |
| 3 | If cost is also exactly equal — **lexicographically smaller stable ID** wins |

This ranking is **authoritative for TASK-006**.

Rule 2 is not arbitrary. Because `incremental_expected_value = net + cost`, two
candidates with equal net expected value differ only in how much budget they
consume to deliver it, and the cheaper one leaves more budget for whatever comes
next. Rule 3 exists only to make the order total; it carries no economic
meaning and must never be described as though it did.

**The ranking is total, so input order cannot affect the result.** A candidate
set is not a policy the way TASK-001's declared catalogue order was — a change
that must be stated explicitly rather than discovered. Criterion 15 requires it
to be demonstrated.

### 2.5 Terminal conditions

**STOP** — and the run terminates, reporting honestly — when any of:

- the **task success condition is already satisfied**;
- **`capability_step_count >= max_capability_steps`**; or
- **no candidate is eligible**, including the case of zero candidates offered.

The success condition is evaluated **before** selection is considered, never
after. This is the ordering TASK-001 arrived at through `CODEX-PR013-06`: the
economic rule answers "is more worth buying?", which is not a question to ask
about a task that is already done.

Stopping remains a **first-class successful behaviour**, per `PREREQ-001` §5.4.
An implementation that treats "no eligible candidate" as a failure, an
exception, or an empty result to be worked around has misread the product.

#### Termination is guaranteed by three safeguards, not by the budget

**Budget depletion alone is not an adequate termination proof.** A free
candidate with any positive uplift would be eligible, be selected, and — since
probabilities are declared fixtures — be eligible again on identical terms,
forever, without ever exceeding the budget. Three safeguards close that, and all
three are mandatory.

**A. Positive-cost invariant.** Every candidate participating in economic
selection must have `candidate_cost > 0`. Zero-cost and local actions sit
**outside the paid-capability selector** and must not be represented as
purchasable candidates. With this in force, every purchase strictly decreases
the remaining budget.

**B. Single-use candidate IDs.** A `candidate_id` that has already been consumed
in this run is ineligible — §2.5a.

**C. Hard capability-step ceiling.** Every run carries `max_capability_steps`
and `capability_step_count`. When the count reaches the maximum, TASK-006
returns STOP and **no further external capability may be purchased**.

**C is deterministic and independent of the remaining budget.** It holds even if
the budget is untouched, even if every candidate is a bargain, and even if A and
B were somehow defeated. It is a safety constraint, not an economic one, and it
must never be described as an economic decision in a run record.

**`max_capability_steps` is authoritative run policy, not a product constant.**
The ETHOnline demonstration is intended to configure it to **4**. That figure is
a demo configuration value and **must not be hard-coded** as a universal
constant, a default buried in the rule, or a magic number in the selection
logic.

### 2.5a Single-use candidates, repeatable capability types

**A candidate offer is single-use.** Once a candidate with a given
`candidate_id` has been executed, that exact candidate is ineligible for the
remainder of the run.

**A capability *type* may be purchased again after the task state changes.** The
constraint is on the offer, not on the kind of thing offered.

Illustratively — and these identifiers are shapes, not a naming scheme this task
imposes — a candidate `second-opinion-001` may execute once. Once new evidence
has changed the task state, a *different* candidate such as
`second-opinion-002` may be generated and considered on its own merits. The same
applies to several targeted research calls.

This keeps two things true at once. Buying two independent second opinions is a
reasonable thing for a run to do, so the model does not forbid it. And no single
offer can be bought twice on identical terms, which is what B in §2.5 needs.

The rule enforces this by ID and by nothing else. **It has no notion of a
capability "type", "class", or "family"**, and must not acquire one — that would
be a fourth field in §2.2 and a provider-shaped concept in a provider-neutral
model. Whether two candidates are the same kind of thing is a question for
whatever generates candidates, which is outside this task.

### 2.6 Budget invariants

All preserved from TASK-001 and `PREREQ-001` §4.2, unchanged:

1. **Budget is a hard ceiling.** It may never be exceeded on any path.
2. **Task value is distinct from budget**, and is never derived from it.
3. **Selection may never require spend beyond the remaining budget** — the
   first eligibility condition is checked against the candidate actually being
   considered.
4. **Unused budget remains unused.** There is no mechanism that consumes it.
5. **Budget is permission to spend, not a target to spend.** A run that stops
   with most of the budget unspent has not underperformed.
6. **Termination does not depend on the budget.** The ceiling bounds spend; it
   is the safeguards in §2.5 that bound the number of decisions. A run may — and
   under a step ceiling routinely will — terminate with budget remaining.

### 2.7 The iterative loop, and what TASK-006 is not

**TASK-006 performs one selection, against one candidate set, for one current
task state.** It is a decision, not a loop.

After the selected capability executes:

1. its `candidate_id` becomes **consumed**;
2. `capability_step_count` increases by one;
3. the **task state is re-evaluated**, producing a new
   `current_success_probability`;
4. a **new candidate set may be generated** for that new state;
5. TASK-006 may run again against it.

**TASK-006 implements none of steps 1 through 4 as behaviour of its own.** It
does not execute capabilities, does not evaluate task state, and does not
generate candidates. It consumes the results of those as inputs and returns a
selection or STOP.

| Concern | Owner |
|---|---|
| Deciding **what to buy** | **TASK-006** |
| Executing the purchase | A separate task — §10 |
| Re-evaluating the task state | A separate task, outside this one — §2.2a |
| Generating the candidate set | A separate task — §3 |
| Tracking consumed IDs and the step count across a run | The run loop, which supplies them as inputs |

This distinction is the whole reason the rule can stay provider-neutral. A
selector that also executed, evaluated, or discovered would need to know what
kind of thing it was buying, and §2.1 forbids exactly that.

## 3. Out of scope — explicitly not authorized

None of the following is part of TASK-006, and none may appear in its
implementation:

- **The baseline execution and evaluation layer** that establishes the current
  task state — §2.2a. TASK-006 receives `current_success_probability`; it does
  not produce it, and this task authorizes none of that work.
- **Task evidence or state transitions** beyond what is required to supply the
  current success probability to a decision.
- **Candidate generation** — deciding what to offer for a given task state.
- **Sponsor integrations** of any kind.
- **Provider discovery** — finding, listing, or querying available capabilities.
- **Any notion of capability type, class, or family** — §2.5a.
- **Payment execution** and **wallet logic**.
- **Real marketplace pricing.** Costs remain declared.
- **Learned performance estimates** — `BL-05`, `BL-06`.
- **Supplier-diligence rules** and anything specific to that vertical.
- **Demo or any user interface** — `BL-10`.

Also unchanged: real repository execution (`BL-07`) and a live test-suite
success signal (`BL-08`) remain unauthorized.

## 4. Acceptance criteria

1. **Zero candidates offered** → STOP. Not an error, not an exception.
2. **One eligible candidate** → it is selected.
3. **One candidate, ineligible because `cost > remaining_budget`** → STOP.
4. **One candidate, ineligible because of zero uplift** — its probability equals
   the current probability → STOP.
5. **One candidate, ineligible because `incremental_expected_value == cost`** →
   STOP. Demonstrated by a test that fails on `>=`.
6. **Multiple eligible candidates** → exactly one is selected.
7. **Highest net expected value wins**, demonstrated where it is *not* also the
   cheapest and *not* the highest incremental value.
8. **Equal net expected value → lower cost wins.**
9. **Equal net expected value and equal cost → lexicographically smaller stable
   ID wins.**
10. **Task already successful** → STOP, with no candidate evaluated.
11. **No eligible candidate among several** → STOP.
12. **Exact money semantics preserved.** All arithmetic through `Money`,
    `Probability` and the exact decimal context. No float appears anywhere in
    the decision.
13. **Total spend can never exceed the budget**, on every path including
    boundary cases where cost exactly equals the remaining budget.
14. **TASK-001's two-tier behaviour remains representable**, per §7, and
    produces identical decisions on the existing scenarios. Demonstrated by
    test rather than argued.
15. **Provider or network identity does not affect selection.** Demonstrated by
    a test in which the candidate set is permuted and the same candidate is
    selected, and by one in which candidates differing only in metadata rank
    identically.
16. **Duplicate stable IDs within one decision are refused**, per §2.2.
17. **Every decision is inspectable after the fact** — the figures in §8 are
    recorded for every candidate considered, not only the winner.
18. **A zero-cost candidate is rejected.** `cost == 0` is ineligible however
    attractive its uplift, and a set consisting only of zero-cost candidates
    yields STOP.
19. **A consumed candidate is rejected.** A `candidate_id` already executed in
    this run is ineligible when offered again, even if it would otherwise win
    outright.
20. **The same capability type may reappear under a new candidate ID after the
    state changes.** A run executes `second-opinion-001`, the task state
    changes, `second-opinion-002` is offered, and it is evaluated on its merits
    and may be selected. The rule must reach this outcome **without** any notion
    of type — by ID alone.
21. **`capability_step_count >= max_capability_steps` → STOP**, with no
    capability purchased, even where budget remains and eligible-looking
    candidates are on offer.
22. **Termination does not depend solely on budget depletion.** Demonstrated by
    a run that terminates on the step ceiling with budget remaining, and by a
    test that the positive-cost invariant holds so that every purchase strictly
    reduces the remaining budget.

## 5. Deliverables

1. The generalized selection rule implementing §2.3–§2.5, in Python 3.12.
2. A candidate model carrying exactly the three fields in §2.2.
3. A test suite covering §4.
4. Declared candidate fixtures sufficient to exercise the rule, in the same
   spirit as TASK-001's `DECLARED_STRATEGIES` and under the same honesty
   constraint in §9.
5. A demonstration that TASK-001's scenarios reproduce, per §7.
6. A way for the run to supply `max_capability_steps` as policy, with **no
   default that makes it optional** and no literal in the selection logic.

`capability_step_count` and the set of consumed candidate IDs are **inputs** to
a decision, per §2.7. Whatever loop drives the run maintains them; TASK-006
reads them. A selector that keeps its own mutable state across decisions has
taken on the loop's job.

Dependencies: **none.** TASK-006 is pure economic policy and needs nothing
external. `AI_BUILD_GOVERNANCE.md` §2.2 permits a task to name dependencies it
requires; this one requires none, and adding any would need the specification
amended first.

## 6. Decisions

### 6.1 The ranking rule ✅
Resolved. Highest net expected value, then lower cost, then lexicographically
smaller stable ID — §2.4, authoritative.

### 6.2 Minimum candidate fields ✅
Resolved. Exactly three — §2.2. Provider metadata is opaque to the rule.

### 6.3 Provider neutrality ✅
Resolved. No provider, network, or payment concept in the core model — §2.1.

### 6.4 Probabilities remain declared ✅
Resolved — §9. TASK-006 adds no learning and no runtime estimation.

### 6.5 Execution mechanism ✅
Resolved: out of scope — §10. Selection and execution are separate concerns and
separate tasks.

### 6.6 The starting current success probability ✅

Resolved. **`current_success_probability` is an input to TASK-006**, supplied by
the current task state — §2.2a.

It is **not** a user input, and it is **not** modelled as a zero-cost candidate.
Selection runs against a task state that has already been established:

```
user task → baseline execution / evaluation → current task state → TASK-006
```

How the baseline is produced is outside this task and is not authorized by it.

### 6.7 Whether a capability may be selected more than once ✅

Resolved. **A candidate offer is single-use; a capability type is repeatable
after the task state changes** — §2.5a.

A `candidate_id` executed in this run is ineligible thereafter. A different
candidate representing a similar capability may be generated for the new state
and considered on its own merits. The rule enforces this by ID and acquires no
notion of type.

### 6.8 What guarantees the loop terminates ✅

Resolved. **Three mandatory safeguards, none of which is the budget** — §2.5.

**A.** Every candidate must cost more than zero, so every purchase strictly
reduces the remaining budget. **B.** A consumed `candidate_id` is ineligible.
**C.** A hard `max_capability_steps` ceiling returns STOP regardless of budget.

C alone is sufficient, and is deliberately independent of the other two: it
holds even if a defect in A or B lets a candidate repeat. The demonstration
configures the ceiling to **4**; that is run policy, not a product constant, and
must not be hard-coded.

## 7. Backward compatibility with TASK-001

TASK-001's scenarios must remain representable, and this is how.

| TASK-001 | TASK-006 |
|---|---|
| The **initial attempt** — its cost, and its `initial_success_probability` | **Not a candidate.** It is the baseline: after it runs, its declared probability *is* the `current_success_probability` the decision compares against |
| The **escalation option** — `escalation_cost`, `escalated_success_probability` | **One candidate capability**, with those two values and a stable ID |
| The escalate-or-stop decision | The same rule, over a candidate set of size one |

With exactly one candidate, §2.4's ranking is vacuous and §2.3's eligibility
test is TASK-001 §2.5's rule with the redundant uplift gate added. **The
decisions should therefore be identical.**

**"Should" is doing real work in that sentence, and criterion 14 is what turns
it into a fact.** The claim rests on an argument from `Money` non-negativity
(§2.3), and an argument is not a demonstration. The existing TASK-001 scenarios
must be run through the new rule and produce the same outcomes, or this
compatibility claim is withdrawn rather than qualified.

Two things this table does **not** say. The initial attempt is not modelled as a
zero-cost candidate — it has a cost, and it is charged before the decision, so
the `remaining_budget` TASK-006 sees is already net of it. And the mapping is a
statement about behaviour, not about types: nothing here requires the
implementation to keep the `Strategy` shape.

### One narrowing, stated plainly

The positive-cost invariant in §2.5 A makes compatibility **near-total rather
than total**, and the gap is worth naming rather than glossing.

TASK-001's `Strategy` validation rejects a *negative* escalation cost but
permits a **zero** one. Such a strategy could exist under the old model and
cannot be represented as a candidate under this one.

In practice nothing is lost. All three declared TASK-001 fixtures have positive
escalation costs, so every scenario the repository actually contains reproduces.
And a zero-cost escalation was already inert economically: eligibility needed
`incremental_expected_value > 0`, so it was selected whenever it improved the
odds at all — which is precisely the non-terminating case §2.5 exists to
exclude.

Criterion 14 covers the fixtures that exist. **It does not claim that every
strategy TASK-001's types could express remains expressible**, because that is
not true, and a compatibility claim is worth less than the exception it hides.

A step ceiling of at least 1 is also required for the two-tier scenarios to
reproduce, since the escalation is a capability step.

TASK-001 itself is not edited. `ARCHITECTURE.md` §2.2.1 continues to describe
what was delivered.

## 8. Run-record implications

The generalized run record must eventually expose, for every decision:

- the **current success probability** the decision was made against;
- the **remaining budget** at that moment;
- the **capability step count** and the **maximum** in force;
- the **candidate IDs already consumed** in this run;
- **every candidate considered** — not only the selected one;

and for each candidate:

- its **stable ID**;
- its **cost**;
- its **expected post-action success probability**;
- its **incremental expected value**;
- its **net expected value**;
- its **eligibility**, and which of the six conditions in §2.3 failed when
  ineligible — including when it failed as consumed, as zero-cost, or because
  the step ceiling was reached;

and for the decision:

- the **selected candidate, or STOP**, with the reason.

Recording the rejected candidates is the point. `PREREQ-001` §8 criterion 3
requires every economic decision to be inspectable afterwards, and a record
showing only what was bought cannot answer why the alternatives were not.

**A STOP on the step ceiling must be recorded as a safety stop, not an economic
one.** It is the one terminal condition that is not a judgement about value, and
a record that blurs the two would claim the economics rejected something they
never assessed.

**No schema change is implemented by TASK-006.** `docs/RUN_RECORDS.md` documents
the current two-tier record and is not edited by this task. The schema work is
part of implementing TASK-006, under whatever authorization does that.

## 9. Probability truthfulness

Unchanged, and restated because generalization is exactly where it would erode:

> Success probabilities and uplifts are **declared benchmark fixtures**. They are
> not learned, measured, inferred from historical performance, or estimated at
> runtime, and must never be described as though they were.

They remain fixtures unless and until a learning or estimation system is
separately authorized — `BL-05`, `BL-06` — and actually exists. **TASK-006 adds
neither.** Describing them otherwise is a boundary violation under
`ARCHITECTURE.md` §6 item 12.

A candidate set that looks like a market makes it tempting to present its
numbers as market data. They are numbers someone typed.

## 10. Execution boundary

**TASK-006 selects a capability. It does not execute one.**

Execution may later be local, an HTTP call, an x402 purchase, a Circle
Marketplace request, an external model, or another service. **Every one of those
is a separate task and a separate authorization**, and none of them may reach
back into the selection rule.

The economic kernel must not depend on the execution mechanism, must not branch
on it, and must not carry a field that exists to describe it. An implementation
in which the selection rule can tell how a capability would be executed has
already failed §2.1.

## 11. Review notes

When reviewing an implementation of TASK-006, verify specifically:

- The ranking in §2.4 is implemented **exactly**, all three levels, with `>` and
  not `>=` on the value condition — criterion 5.
- Selection is genuinely order-independent — permuting the input changes
  nothing.
- No provider, network, or payment name appears anywhere, including in
  fixtures, comments, and test names.
- The three candidate fields are the only ones the rule reads.
- STOP is reachable and correct on all four routes: already successful, zero
  candidates, all ineligible, and budget exhausted.
- The budget ceiling holds where cost exactly equals the remaining budget.
- TASK-001's scenarios are actually re-run, not merely asserted to be equivalent.
- **No item in §3 appears anywhere**, including in dependencies, configuration,
  comments, or abstractions built "for later."
- All **six** eligibility conditions in §2.3 are implemented, including the two
  that are not economic. Dropping the uplift condition as redundant is a defect.
- `max_capability_steps` is read from run policy. **A literal 4 anywhere in the
  selection logic is a defect**, as is a default that makes the policy optional.
- The step-ceiling STOP is recorded as a safety stop, distinguishable in the run
  record from an economic one — §8.
- Consumption is tracked by ID and by nothing else. **Any notion of capability
  type, class, or family is a defect** — §2.5a, criterion 20.
- Zero-cost candidates are refused rather than quietly ranked last —
  criterion 18.
- The implementation matches what §6.6–§6.8 record as decided, rather than what
  is convenient.
