# PR-014 — Writing down what comes next, and why it is harder than wiring

**Pull request:** #14
**Authority:** governance amendment, at the product owner's direction
**Author:** Claude Code, under human product owner authorization

---

## 1. Purpose of this PR

To write down the plan for everything after the first piece of work: making the
spending real, giving the agent a wallet, and letting it pay for what it buys.

**Nothing here authorizes any of that.** These are specifications. Building them
still needs a separate decision from the product owner.

## 2. What changed

| File | What it is |
|---|---|
| `tasks/TASK-002_..._OPENROUTER.md` | Real inference, so the money actually leaves an account |
| `tasks/TASK-003_..._PRIVY.md` | Authority over the agent that it cannot grant itself |
| `tasks/TASK-004_..._HEDERA_AND_X402.md` | The agent paying for its own purchases |
| `docs/ARCHITECTURE.md` | The plan, and a payments direction that was missing |
| `tasks/BACKLOG.md` | Those items now point at their specifications |
| `docs/PREREQ-001_PRODUCT_DEFINITION.md` | Why this matters now |
| `docs/pr_explanations/PR-014_...md` | This document |
| `docs/reviews/PR-014_CODEX_REVIEW.md` | The review prompt, committed before the review |
| `docs/reviews/README.md` | Its row added to the index of reviews |

Nine files. No code, and no change to the test count, which stays at 242 on the
main branch.

## 3. Why the change was needed

The first piece of work proves the reasoning is sound, and spends imaginary
money doing it. Everything that makes it a real product was described only as
four lines in a list of ideas nobody had thought through.

More importantly: the reason any of this matters has changed, and the documents
did not say so.

## 4. How this worked before

Four one-line entries in a backlog, each marked "not approved". No sense of
order, no sense of what any of them would actually involve, and nothing saying
which parts of the existing design would have to change.

## 5. How it works after

### The plan

Three pieces of work, in the order their dependencies force:

1. **Real inference.** Buy the work from an actual provider. The money in a
   record becomes money that actually left an account.
2. **Authority it cannot grant itself.** The agent gets a wallet, and — the part
   that matters — someone outside decides what it may spend. A spend beyond that
   is refused by the wallet, not by Radhanite's own check, and the agent cannot
   raise its own limit.
3. **Paying for itself.** The agent settles its own purchases, on a public
   ledger, with no human in the transaction.

### The part worth reading

Each specification names an assumption in the existing system that reality
breaks. These are the difficult parts, and they are design questions rather than
plumbing:

**Prices are decided in advance, and real ones are not.** Today each way of
working has a fixed price, and the budget is charged that amount before the work
happens. Real AI costs are known *afterwards*, once you see how much was used.
So the system needs two figures where it has one: a guess to decide with, and a
real number to settle against. And then a rule for what happens when the real
number is bigger and the budget would be broken — which is a question about what
a budget *means*, not a coding detail.

**Payments can fail, and decisions currently cannot.** The loop assumes that
deciding to spend and having spent are the same event. With real money they come
apart: a payment can be declined, time out, or arrive late. "Decided to buy",
"paid", and "got what was paid for" become three different states, and the
system has never had to tell them apart.

**A budget belongs to one job; a wallet does not.** Each run gets a fresh
allowance and throws it away afterwards. A wallet keeps its balance between jobs,
so one job can spend what the next one needed. Nothing currently thinks about
that at all.

**Every limit the system has, it set for itself.** This is the one that cannot be
fixed from inside. The spending ceiling holds because the code chooses to respect
it — the ledger belongs to the system, runs inside it, and checks a budget the
system was handed. If the rule that decides spending were wrong, nothing outside
would notice. An agent that decides its own limits is marking its own homework,
and no amount of better arithmetic fixes that.

The answer is authority granted from outside: a person decides what the agent may
spend, the wallet refuses anything beyond it, and the agent cannot widen what it
was given. Which is exactly the rule this project already runs on for code — the
AI may not approve its own work — applied to money.

That matters twice over once there is more than one agent. **Ten agents each
perfectly respecting a $2 budget is $20 of exposure nobody agreed to.** Every one
of them is individually correct; the total is unbounded, and no agent can see the
others. That is not a limit a better-written agent could impose on itself — it is
a kind of limit self-imposed ceilings cannot express. Running several agents is
recorded as a future idea and is not approved; the point here is that it is the
clearest argument for granting authority from outside rather than trusting each
agent to police itself.

### A direction that was missing

The architecture described payments in one direction only: **other machines
paying Radhanite** to use it. The direction that actually matters had no entry
anywhere — **Radhanite's agent paying for what it buys.**

That is the whole point. An agent that can pay for things needs something
deciding whether each purchase is worth making, and that is what this product
is. Both directions are legitimate, they are different features, and they were
being blurred into one line.

### Why now

The product definition explains what was previously assumed: agents are starting
to hold wallets. Once one can pay, "can I afford this?" and "is this worth
buying?" come apart, and a wallet only answers the first. An agent with money and
no answer to the second question is a spending limit with extra steps.

## 6. What goes into the system

Nothing. These are documents.

## 7. What the system decides

Nothing. No behaviour changes.

## 8. What comes out

Nothing.

## 9. How it can fail

- **The plan could be wrong.** None of these three has been attempted, and the
  hard parts are named from reading the code rather than from trying.
- **It could read as more progress than it is.** Writing a specification is not
  building anything, and a repository full of plans is not a product.
- **One of the tools may not fit.** The documented path for the authority
  service is a browser flow with a person logging in, which is the wrong shape
  for something that spends while nobody is watching. Whether its server-side
  product does what is needed is unverified, and two of the three planned pieces
  now depend on it.
- **The authority layer could turn out to be decoration.** If what it enforces
  is the same limit the system already enforces on itself, it adds nothing. The
  specification says to check that and report it either way.
- **The deadline may make the order impossible.** Three pieces of work are
  specified. There is not obviously time for three.

## 10. Tests run, and their results

**No tests were run**, and none changed. This pull request contains no code.

The existing suite is unaffected: 242 tests on the main branch.

What was checked instead: that the new section in the product definition did not
renumber any existing one, since other documents — including review transcripts
that may never be edited — refer to sections by number. Those numbers were
confirmed unchanged.

## 11. Assumptions made

- That specifying all three now is better than specifying one at a time, because
  the hard parts interlock: what a budget means, when money moves, and where it
  lives.
- That naming the three broken assumptions is the useful part. Anyone can list
  integrations; the value is in saying which existing decisions they invalidate.
- That the outbound payment direction was missing rather than implied.

## 12. Known limitations

- Nothing here is authorized, and nothing is built.
- The specifications are written from reading the existing code, not from having
  attempted any of the integrations.
- Details about the specific services — how their tools actually work — are
  deliberately absent, because they have not been verified and guessing would be
  worse than leaving a question open.

## 13. Functionality explicitly left out of scope

All of it. No code, no dependencies, no credentials, no configuration. The
architecture's rule stands: an integration becomes permitted only when the
product owner issues a task saying so, and a specification is not that.

## 14. Deferred to future tasks

Everything described. Also deliberately excluded: budgeting across several jobs
at once, and Radhanite being sold as a paid service — recorded as a separate
idea rather than folded into the one that matters.

## 15. How to explain this to a judge

Radhanite decides whether an AI agent's next purchase is worth the money. So far
it does that with imaginary money, which proves the reasoning but not the
product.

This pull request writes down the three steps to make it real: buy actual work
from an actual provider; give the agent a wallet with limits it cannot exceed;
and let it pay for its own purchases on a public ledger, with nobody in the
loop.

The useful part is not the list. It is that each step names something the current
system assumes that will stop being true. Prices are decided in advance, and real
prices are not. Deciding to spend is treated as the same event as having spent,
and with real payments it is not. A budget belongs to one job, and a wallet does
not.

The fourth is the interesting one. **Every limit this system has, it set for
itself.** It respects its budget because its own code says so. Give it authority
granted from outside — where the wallet refuses a spend the agent wanted to make,
and the agent cannot raise its own limit — and you get two independent judgements
that can disagree. A payment going through proves the plumbing works. A payment
the agent wanted to make and *was not allowed* to make proves the control is
real.

Those are the three places this gets genuinely hard, and they are written down
before any of it is built rather than discovered halfway through.

---

**This document explains; it does not govern.** The product definition,
architecture document, task specifications, and the code and its tests are the
authoritative record. Where this explanation and the repository disagree, the
repository is correct.
