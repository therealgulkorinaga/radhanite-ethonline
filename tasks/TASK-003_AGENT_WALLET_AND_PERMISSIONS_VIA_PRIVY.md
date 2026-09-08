# TASK-003 — Agent wallet and spending permissions via Privy

**Status:** Specified — **NOT AUTHORIZED**
**Authorization:** None. This document does not permit implementation.
**Traces to:** [`PREREQ-001`](../docs/PREREQ-001_PRODUCT_DEFINITION.md) §4.2
**Bounded by:** [`ARCHITECTURE.md`](../docs/ARCHITECTURE.md) §3.2
**Replaces backlog entry:** `BL-02`
**Depends on:** TASK-002 complete and merged

---

## 1. Purpose

Give the agent a wallet it controls, and a permission model saying what it may
spend from that wallet without asking anyone.

TASK-001 and TASK-002 give Radhanite a budget. A budget is a number Radhanite
agrees to respect. This task makes it **an account the agent can actually draw
on**, with limits enforced outside Radhanite's own good behaviour.

That distinction is the whole point. Today the budget ceiling holds because the
code checks it. An agent with a wallet needs the ceiling to hold even if the
code is wrong.

## 2. Scope

A **server-side wallet**, created and controlled programmatically, with a
permission model governing what the agent may spend.

Radhanite must **not** implement custody, key management, or authentication
(`ARCHITECTURE.md §3.2`).

### 2.1 The shape this must take

Most Privy material describes a browser flow: a person logs in, and a wallet is
created for that person. **That is the wrong shape.** Radhanite is a backend
process that spends while nobody is watching. There is no user, no login, no
browser.

What this task needs is a wallet the agent holds and signs with, from a server,
with no human in the loop at spend time. Whether Privy's server-side wallet
product provides that, and how, is the first thing to establish — see §6.1.

### 2.2 What "permissions" means here

A spending permission is a limit the agent cannot exceed **even if Radhanite's
own logic fails**. Candidates: a per-task ceiling, a per-period ceiling, an
allowlist of what may be paid.

This is the second enforcement of the same ceiling, deliberately. TASK-001
criterion 12 enforces it in code; this enforces it in the wallet. A budget that
depends only on the spender respecting it is not a budget.

## 3. The problem this task actually has to solve

**Radhanite's budget is per-run; a wallet is not.**

Every run creates a fresh ledger from `task.budget` and discards it. A wallet
persists, is shared across runs, and can be drained by one task to the detriment
of the next. Nothing in Radhanite currently reasons about that — allocating
across several tasks is `BL-09`, and it is not authorized.

So this task has to answer: what does a per-run budget mean when the money comes
from a shared, persistent account? Options include funding a run from the wallet
up to its budget, or enforcing both a per-run and a wallet-level ceiling.
Nothing here is decided. See §6.

## 4. Out of scope

| Excluded | Note |
|---|---|
| Custody, key management, authentication | Privy's job. `ARCHITECTURE.md §3.2`. |
| Any browser flow, login screen, or user-facing wallet UI | Still a production UI, still excluded. |
| Token accounting, transfers, settlement | TASK-004. This task establishes the wallet and its limits, not payments over a rail. |
| Multi-task budget allocation | `BL-09`. One task at a time. |
| Human approval flows | A spend that needs a human is not autonomous. Out of scope unless a later task says otherwise. |

## 5. Acceptance criteria

1. A wallet exists, is controlled programmatically from a backend process, and
   requires no human interaction to sign or spend.
2. A spending permission is configured and **enforced outside Radhanite's own
   logic**, demonstrated by a test in which Radhanite attempts to exceed it and
   is refused.
3. The relationship between per-run budget and wallet balance is defined and
   enforced, per §6.2.
4. No secret appears in the repository, a run record, or a log.
5. A run record shows which wallet paid and under what permission.
6. The existing suite still runs deterministically without network access.
7. Nothing in §4 appears.
8. Repository tests pass.

Criterion 2 is the one that matters. A permission Radhanite enforces on itself
is not a permission; it is the same ceiling counted twice.

## 6. Open decisions — product owner input required

1. **Whether Privy is the right tool for this shape**, and what its server-side
   wallet product actually offers a backend agent with no user. If it is
   fundamentally a human-onboarding product, a plain keypair plus a signing
   library may serve better — and the honest answer might be that Privy earns
   its place only where a human *is* involved.
2. **What a per-run budget means against a persistent wallet.** §3.
3. **Which permissions are worth enforcing** — per task, per period, per
   recipient, or some combination.
4. **What happens when a permission refuses a spend Radhanite decided to make.**
   This is a new outcome: the economic rule said buy, and the wallet said no.
   TASK-001's loop has no path for it.

## 7. Review notes

- Confirm no browser, login, or user-facing flow appears.
- Confirm the permission is enforced outside Radhanite's logic, by attempting to
  breach it.
- Confirm no credential reaches the repository, a record, or a log.
- Confirm the per-run/wallet relationship is enforced, not merely described.
- Assess honestly whether Privy is doing real work here or is present because it
  is a sponsor. Say so either way.
