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

### 2.3 The economic rule is preserved

Unchanged from TASK-001 §2.5, applied per candidate:

```
incremental_expected_value =
    (candidate_success_probability - current_success_probability) × task_value
```

A candidate is **economically eligible** only when all three hold:

```
candidate_cost <= remaining_budget
candidate_success_probability > current_success_probability
incremental_expected_value > candidate_cost
```

Otherwise it is **ineligible**. Ineligibility is an ordinary outcome, not an
error.

**On the second condition.** Given that `Money` validation makes cost and task
value non-negative, it is implied by the third: eligibility requires
`incremental_expected_value > candidate_cost >= 0`, and a positive incremental
value with a non-negative task value requires a positive uplift. It is stated
anyway, as an explicit gate — it makes the intent checkable at review, and it
holds the invariant if those non-negativity constraints are ever revisited. An
implementation may not drop it on the grounds that it is redundant.

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

**STOP** — and the run terminates, reporting honestly — when either:

- the **task success condition is already satisfied**; or
- **no candidate is eligible**, including the case of zero candidates offered.

The success condition is evaluated **before** selection is considered, never
after. This is the ordering TASK-001 arrived at through `CODEX-PR013-06`: the
economic rule answers "is more worth buying?", which is not a question to ask
about a task that is already done.

Stopping remains a **first-class successful behaviour**, per `PREREQ-001` §5.4.
An implementation that treats "no eligible candidate" as a failure, an
exception, or an empty result to be worked around has misread the product.

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

## 3. Out of scope — explicitly not authorized

None of the following is part of TASK-006, and none may appear in its
implementation:

- **Task evidence or state transitions** beyond what is required to supply the
  current success probability to a decision.
- **Sponsor integrations** of any kind.
- **Provider discovery** — finding, listing, or querying available capabilities.
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

## 5. Deliverables

1. The generalized selection rule implementing §2.3–§2.5, in Python 3.12.
2. A candidate model carrying exactly the three fields in §2.2.
3. A test suite covering §4.
4. Declared candidate fixtures sufficient to exercise the rule, in the same
   spirit as TASK-001's `DECLARED_STRATEGIES` and under the same honesty
   constraint in §9.
5. A demonstration that TASK-001's scenarios reproduce, per §7.

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

### 6.6 The starting current success probability ⚠️ **UNRESOLVED**

Every eligibility test is relative to `current_success_probability`. At the
first decision of a run, **nothing has been attempted, and this specification
does not say what that value is.**

TASK-001 never faced the question: its escalation compared against the initial
attempt's declared probability, and there was always an initial attempt. Here
the first decision may be a choice among several candidates with no baseline
behind it.

Three shapes are possible — a declared baseline of zero; a baseline declared per
task alongside the other five inputs; or a "do nothing" candidate at zero cost
whose probability is the baseline. They are not equivalent: the third makes the
baseline compete under the ordinary rule, and the second adds a sixth input to
`PREREQ-001` §4.

**This is a product decision for the human product owner.** Implementation
cannot begin without it, because every eligibility outcome depends on it.

### 6.7 Whether a capability may be selected more than once ⚠️ **UNRESOLVED**

After a capability is executed, the current success probability changes and the
decision runs again. **May the same stable ID be offered and selected a second
time?**

Both answers are defensible. Repeat purchase is realistic — buying two
independent second opinions is a real thing to want. Single purchase is simpler
and matches the intuition that a capability, once acquired, is acquired.

The answer determines whether the candidate set is stateful across a run, which
is a structural question and not a detail.

### 6.8 What guarantees the loop terminates ⚠️ **UNRESOLVED**

TASK-001 terminated structurally: two tiers, then the run was over. **This model
has no such bound.**

Termination now rests entirely on the budget: every selected candidate costs
something, so the remaining budget strictly decreases and eligibility eventually
fails. **That argument breaks for a zero-cost candidate.** A candidate costing
nothing with any positive uplift is eligible, is selected, and — if probabilities
are declared fixtures that do not change when it is executed — is eligible again
on identical terms, forever.

Options include forbidding zero-cost candidates, requiring the current
probability to strictly increase after execution, bounding the number of
decisions per run, or accepting zero-cost candidates only once under §6.7.

**This must be settled before implementation.** A specification whose loop can
be shown not to terminate is not ready to build, and criterion 13 does not catch
it: spend stays within budget the whole time it is looping.

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
zero-cost candidate — it has a cost, and it is charged. And the mapping is a
statement about behaviour, not about types: nothing here requires the
implementation to keep the `Strategy` shape.

TASK-001 itself is not edited. `ARCHITECTURE.md` §2.2.1 continues to describe
what was delivered.

## 8. Run-record implications

The generalized run record must eventually expose, for every decision:

- the **current success probability** the decision was made against;
- the **remaining budget** at that moment;
- **every candidate considered** — not only the selected one;

and for each candidate:

- its **stable ID**;
- its **cost**;
- its **expected post-action success probability**;
- its **incremental expected value**;
- its **net expected value**;
- its **eligibility**, and which condition failed when ineligible;

and for the decision:

- the **selected candidate, or STOP**, with the reason.

Recording the rejected candidates is the point. `PREREQ-001` §8 criterion 3
requires every economic decision to be inspectable afterwards, and a record
showing only what was bought cannot answer why the alternatives were not.

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
- The three unresolved decisions in §6.6, §6.7 and §6.8 were resolved by the
  human product owner before implementation began, and the implementation
  matches what was decided rather than what was convenient.
