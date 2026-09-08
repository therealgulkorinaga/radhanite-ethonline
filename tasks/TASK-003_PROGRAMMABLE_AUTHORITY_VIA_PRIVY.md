# TASK-003 — Programmable authority over the agent, via Privy

**Status:** Specified — **NOT AUTHORIZED**
**Authorization:** None. This document does not permit implementation.
**Traces to:** [`PREREQ-001`](../docs/PREREQ-001_PRODUCT_DEFINITION.md) §2.2, §4.2
**Bounded by:** [`ARCHITECTURE.md`](../docs/ARCHITECTURE.md) §3.2
**Replaces backlog entry:** `BL-02`
**Depends on:** TASK-002 complete and merged

---

## 1. Purpose

To put the agent under **authority it cannot grant itself**.

The valuable thing here is not that Privy can make a wallet. Any keypair makes a
wallet. It is that authority over an autonomous agent becomes **programmable**:
granted from outside, enforced outside, changed or revoked outside, and beyond
the agent's reach to widen.

## 2. The circularity this closes

Radhanite answers one question: **is this purchase worth the money?** That is a
judgement it makes about its own spending.

Nothing yet answers the other: **is this agent permitted to make it?**

Today the budget ceiling holds because the code respects it. TASK-001 criterion
12 is enforced by a ledger Radhanite owns, inside a process Radhanite controls,
against a budget Radhanite was handed. Every part of that is the agent marking
its own homework. If the escalation rule were wrong, or the ledger had a bug, or
some later change quietly raised a limit, nothing outside would notice.

An agent that decides its own limits has the same circularity as an agent that
sets its own budget. The economics cannot fix it, because the economics are the
thing being checked.

**This is the same principle the repository already runs on.** `AI_BUILD_GOVERNANCE.md`
§1.1 says the implementing agent may not authorize its own work, and §1.4
separates who decides from who acts. Programmable authority is that rule applied
to money instead of code: a human grants scope, the agent operates freely inside
it, and the agent cannot widen it.

## 3. Scope

An authority layer over the agent's spending, expressed and enforced outside
Radhanite:

- **Granted externally.** A person or system defines what the agent may spend,
  and on what terms.
- **Enforced externally.** A spend outside that authority is refused by the
  wallet, not by Radhanite's own check.
- **Revocable and adjustable** without changing or redeploying Radhanite.
- **Not self-expandable.** The agent can spend within its authority and cannot
  enlarge it.
- **Auditable.** What the agent was permitted to do, at the time it acted, is
  recoverable afterwards.

Radhanite must **not** implement custody, key management, or authentication
(`ARCHITECTURE.md §3.2`). It holds authority; it does not issue it.

### 3.1 The shape this must take

Most Privy material describes a browser flow: a person logs in and a wallet is
made for them. **That is the wrong shape.** Radhanite is a backend process that
spends while nobody is watching — no user, no login, no browser.

What this needs is a wallet the agent signs with from a server, under a policy
set by someone else. Whether Privy's server-side product provides that, and how
its policy controls actually work, is the first thing to establish — §7.1.

### 3.2 Where the money lives

The wallet holds **USDC on Arc**, so that the agent's authority, its balance, and
what it pays are all denominated in the same unit as its budget. This is where
TASK-003 and the Circle integration meet: Privy supplies the wallet and the
authority over it; Arc is the chain it operates on.

## 4. What this makes possible that nothing else does

**Two independent judgements, which can disagree.** Radhanite says a purchase is
economically justified. The authority layer says whether it is permitted. When
they disagree, the refusal comes from outside the agent — and that refusal is the
demonstration. A successful payment proves plumbing. A payment the agent wanted
to make and was **not allowed** to make proves the control is real.

**Authority that changes while the agent runs.** A limit tightened mid-run takes
effect without touching the agent. Radhanite has no path for this today: its
budget is fixed when a run starts.

**A bounded blast radius.** If the escalation rule is wrong, the loss is capped
by something the rule cannot reach.

## 5. Out of scope

| Excluded | Note |
|---|---|
| Custody, key management, authentication | Privy's job. `ARCHITECTURE.md §3.2`. |
| Any browser flow, login screen, or user-facing wallet UI | Still a production UI, still excluded. |
| Payment protocol or settlement | TASK-004/005. This task establishes authority, not rails. |
| Multi-task budget allocation | `BL-09`. |
| Human approval per spend | A spend needing a human is not autonomous. Authority is granted in advance, not asked for each time. |

That last row draws the line: this is *authority*, not *supervision*. The point
is that the agent acts alone, inside bounds it did not set.

## 6. Acceptance criteria

1. The agent holds a wallet it controls from a backend process, with no human
   interaction at spend time.
2. **A spend Radhanite decides to make is refused by the authority layer**,
   demonstrated by a test — the refusal coming from outside Radhanite's own
   logic.
3. **The agent cannot widen its own authority.** Demonstrated by attempting it.
4. Authority can be changed or revoked without modifying or redeploying
   Radhanite, and the change takes effect.
5. The run record shows the authority in force when each spend was attempted.
6. A refusal by the authority layer is an outcome the loop handles, not a crash.
7. No secret appears in the repository, a run record, or a log.
8. The existing suite still runs deterministically without network access.
9. Nothing in §5 appears.
10. Repository tests pass.

Criteria 2 and 3 are the task. A limit Radhanite enforces on itself is the same
ceiling counted twice; a limit the agent could raise is not a limit.

## 7. Open decisions — product owner input required

1. **What Privy's server-side product actually offers** an agent with no user,
   and what its policy controls can express. Everything below depends on this.
2. **What authority is worth expressing** — per transaction, per period, per
   recipient, per asset, or some combination.
3. **What the loop does when the economics say buy and authority says no.** This
   is a new outcome. TASK-001's loop has no path for a decision it is not
   allowed to act on, and it is not obvious whether that ends the run, or the
   strategy, or neither.
4. **How per-run budget relates to a persistent wallet.** Each run builds a
   ledger from its task's budget and discards it; a wallet keeps its balance
   between runs, and one task can spend what the next needed. Allocating across
   tasks is `BL-09` and is not authorized.

## 8. Review notes

- Confirm no browser, login, or user-facing flow appears.
- Confirm the refusal in criterion 2 genuinely originates outside Radhanite —
  a check Radhanite performs on itself does not satisfy it.
- Confirm criterion 3 by attempting to widen authority from inside the agent.
- Confirm authority changes take effect without redeploying.
- Confirm no credential reaches the repository, a record, or a log.
- Assess whether the authority layer is doing real work or is decoration over a
  limit Radhanite already enforces. If it is the latter, say so.
