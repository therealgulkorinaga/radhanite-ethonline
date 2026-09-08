# TASK-002 — Real inference via OpenRouter

**Status:** Specified — **NOT AUTHORIZED**
**Authorization:** None. This document does not permit implementation.
**Traces to:** [`PREREQ-001`](../docs/PREREQ-001_PRODUCT_DEFINITION.md) §5.1–5.2
**Bounded by:** [`ARCHITECTURE.md`](../docs/ARCHITECTURE.md) §3.1
**Replaces backlog entry:** `BL-01`
**Depends on:** TASK-001 complete and merged

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
8. Every decision remains recomputable from the run record.
9. Nothing in §4 appears.
10. Repository tests pass.

Criterion 7 matters more than it looks. TASK-001's entire value rests on runs
being deterministic. A test suite that needs the network is a test suite that
fails for reasons unrelated to the code.

## 6. Open decisions — product owner input required

1. **The overrun rule.** What happens when actual cost exceeds estimated and
   the ceiling would break. Options include: pass a hard spend ceiling to the
   provider so it cannot happen; permit the overrun and record a breach; or
   treat the estimate as the charge and absorb the difference. This is a
   product decision about what a budget *means*, not an implementation detail.
2. **Where estimates come from.** Provider pricing multiplied by an expected
   token count is the obvious answer, and the expected token count is another
   declared constant unless something measures it — which would be `BL-06`.
3. **Which models map to which strategies.** The three declared strategies
   become real model choices with real prices. Those prices are facts, not
   fixtures, and will move.
4. **Whether declared probabilities survive contact with reality.** Once real
   outcomes are observable, the declared figures will visibly disagree with
   what happens. TASK-001 forbids updating them. Confirm that still holds.

## 7. Review notes

- Confirm Radhanite selects a tier and ceiling and nothing more; any routing,
  fallback or provider-specific client logic is a §3.1 violation.
- Confirm the ceiling is enforced against actual spend.
- Confirm no credential reaches the repository, a record, or a log.
- Confirm the existing suite still runs deterministically without network
  access.
- Confirm probabilities are still declared and nothing infers them from
  observed outcomes.
