# TASK-002 — Real inference via OpenRouter

**Status:** Specified, all decisions resolved — **NOT AUTHORIZED for implementation**
**Authorization:** None. Its decisions are settled; the work itself still requires explicit authorization from the human product owner.
**Traces to:** [`PREREQ-001`](../docs/PREREQ-001_PRODUCT_DEFINITION.md) §5.1–5.2
**Bounded by:** [`ARCHITECTURE.md`](../docs/ARCHITECTURE.md) §3.1
**Replaces backlog entry:** `BL-01`
**Depends on:** TASK-001 complete and merged

**Predates the product pivot.** Written under the previous product definition
(inference-expenditure allocation). Preserved as a **proposed specification and
historical record** under [`PREREQ-001`](../docs/PREREQ-001_PRODUCT_DEFINITION.md)
§2.3; its technical decisions are unaltered. **Its place in the dependency chain
is not automatically authorized** under the new direction — see
[`BACKLOG.md`](BACKLOG.md) and [`ARCHITECTURE.md`](../docs/ARCHITECTURE.md) §4a.

---

## 1. Purpose

Make the money real.

TASK-001 proved the economic reasoning against a simulator. Every figure it
decided with was declared, and every dollar it spent was imaginary. This task
replaces the simulator with **actual inference bought from actual providers**,
so that a run's reported spend is money that genuinely left an account.

This is the task that turns a demonstration into a product. Until it lands,
every number Radhanite reports is a number somebody typed.

## 2. Scope

Replace `radhanite.execution.ScriptedSimulator` with an execution path that
calls OpenRouter, and reconcile what that costs with what the economic loop
assumed it would.

Radhanite **selects a capability tier and a spend ceiling**. OpenRouter routes,
executes and bills. Per `ARCHITECTURE.md §3.1`, Radhanite must not reimplement
model routing, provider fallback, provider-specific clients, or inference
billing.

## 3. The problem this task actually has to solve

The loop as built assumes something OpenRouter will not give it.

**A strategy's cost is declared before the purchase.** `Strategy.initial_cost`
is a fixed figure, the ledger is charged that amount *before* execution, and
§2.5's rule weighs that same figure. Real inference costs are known **after**
the call, from tokens consumed.

So the loop needs two quantities where it currently has one:

- an **estimated cost**, available before the decision, which §2.5 weighs;
- an **actual cost**, known afterwards, which the ledger must reconcile.

Everything difficult about this task follows from that gap:

- What happens when actual exceeds estimated, and the budget ceiling would be
  breached? The ceiling is criterion 12 of TASK-001 and cannot simply be
  relaxed.
- Does an overrun invalidate the decision that authorized it, and if so, what
  does the run record say?
- Is a spend ceiling passed to the provider, so the overrun cannot happen?

Nothing here is decided. See §6.

## 4. Out of scope

| Excluded | Note |
|---|---|
| Privy | Wallets and permissions are TASK-003. |
| Arc / USDC, x402 | Paying for inference in a token is TASK-004. Inference here is billed to an OpenRouter account by conventional means. |
| Model routing, provider fallback | OpenRouter's job. `ARCHITECTURE.md §3.1`. |
| Learned or measured success probabilities | Still `BL-06`. Probabilities remain declared constants even though real outcomes are now observable. Measuring them is a separate authorized task or nothing. |
| Production UI | Still excluded. |
| Real repository execution | `BL-07`. The model is called; its output is not run against a codebase. |

That fifth row deserves emphasis: **this task makes the spend real, not the
work**. What a strategy does with a model, and how "the tests pass" is actually
checked, is `BL-07` and `BL-08`.

## 5. Acceptance criteria

1. A run buys inference from OpenRouter and reports what it actually cost.
2. Estimated cost is available before the decision; actual cost is known after,
   and both appear in the run record.
3. The budget ceiling holds against **actual** spend, not estimated.
4. An overrun — actual exceeding estimated — is detected, recorded, and handled
   by whatever rule §6.1 settles on, rather than silently absorbed.
5. A provider failure (timeout, refusal, rate limit) is an outcome the loop
   handles, not a crash.
6. No API key appears in the repository, in a run record, or in any log.
7. Runs remain reproducible for testing: the real path is exercised against
   OpenRouter, and a recorded or stubbed path keeps the existing suite
   deterministic without network access.
7a. Nothing claims the work was done. No output, record or document states or
    implies that code was fixed or tests passed — §6.5 and `ARCHITECTURE.md §6`
    item 9.
7b. Only the dependencies §6.6 allows appear, and each is disclosed.
8. Every decision remains recomputable from the run record.
9. Nothing in §4 appears.
10. Repository tests pass.

Criterion 7 matters more than it looks. TASK-001's entire value rests on runs
being deterministic. A test suite that needs the network is a test suite that
fails for reasons unrelated to the code.

## 6. Decisions

**All resolved by the human product owner.** The implementing agent does not
reinterpret them.

### 6.1 The overrun rule ✅

**Reserve against a configured maximum cost before the call, and refuse the call
if the provider cannot bound the charge within the remaining budget.**

The ceiling is not relaxed and no overrun is absorbed. Where a bounded maximum
cannot be established, the purchase does not happen — which is a refusal, not a
failure, and is recorded as one.

### 6.2 Where estimates come from ✅

**Published provider pricing, multiplied by declared token assumptions.** The
token assumption is a declared constant attached to a strategy, under the same
rule as its probabilities.

**Never learned from history.** Observing that calls have tended to cost more
than assumed does not change the assumption; that is `BL-06`.

### 6.3 Model mapping ✅

**Fixed, explicit model identifiers**, one for each existing initial and
escalated tier. No dynamic routing, and OpenRouter's own automatic routing is
not the decision engine — Radhanite chooses the tier, and the identifier for
that tier is declared.

### 6.4 Declared probabilities ✅

**They remain fixtures.** Real outcomes are recorded, and the declared figures
are not updated from them. That the two will visibly disagree is expected and is
not a defect: `BL-06` is where that gap is closed, and it is unauthorized.

### 6.5 What may be claimed about success ✅

**A model's output is evidence within a declared scenario, and nothing more.**

This task makes the *spend* real. It does not make the *work* real: no
repository is modified and no test runner executes (`BL-07`). Nothing in the
code, the run record, the demonstration or the explanation may state or imply
that Radhanite fixed code or that tests passed.

The honest form is: **Radhanite executed real inference and then evaluated a
declared scenario.** `ARCHITECTURE.md §6` item 9 makes departing from this a
boundary violation.

### 6.6 Dependencies ✅

This task may introduce **only** what is required to call OpenRouter — in
practice an HTTP client, or the official SDK if one exists and is verified.
Nothing else, and each is disclosed in the pull request explanation, per
`AI_BUILD_GOVERNANCE.md §2.2`.

TASK-001's zero-dependency constraint binds TASK-001. It does not bind this
task, and this task's allowance does not extend to any other.

## 7. Review notes

- Confirm Radhanite selects a tier and ceiling and nothing more; any routing,
  fallback or provider-specific client logic is a §3.1 violation.
- Confirm the ceiling is enforced against actual spend.
- Confirm no credential reaches the repository, a record, or a log.
- Confirm the existing suite still runs deterministically without network
  access.
- Confirm probabilities are still declared and nothing infers them from
  observed outcomes.
- Confirm nothing anywhere claims the work was done. Read the demonstration
  output and the explanation with this specifically in mind: real inference
  producing a plausible answer is not the work having been done.
- Confirm no dependency beyond what §6.6 allows, and that each is disclosed.
- Confirm the two-tier strategy model is unchanged, and that no one-shot or
  parallel workflow has been approximated within it (`ARCHITECTURE.md §2.2`).
