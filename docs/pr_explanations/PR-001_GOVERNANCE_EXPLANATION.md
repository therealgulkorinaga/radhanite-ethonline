# PR-001 — Repository governance and planning scaffolding

**Pull request:** #1
**Authority:** governance amendment, plus the PREREQ-001 prerequisite and the
TASK-001 task specification
**Author:** Claude Code, under human product owner authorization

---

## 1. Purpose of this PR

To agree the rules and the plan before any product is built.

This pull request adds no working software. It defines what Radhanite is, what
it is allowed to do, how AI agents are permitted to build it, and what the first
piece of work will be. Everything here is a written decision, not a program.

## 2. What changed

The repository went from completely empty to eleven documents:

| File | What it is |
|---|---|
| `README.md` | An overview of the project for a first-time reader |
| `LICENSE` | The MIT licence, making the project open source |
| `docs/PREREQ-001_PRODUCT_DEFINITION.md` | What Radhanite is and why it exists |
| `docs/ARCHITECTURE.md` | What Radhanite builds itself, and what it must never rebuild |
| `docs/HACKATHON_RULES.md` | The ETHOnline competition rules we build under |
| `docs/AI_BUILD_GOVERNANCE.md` | The rules controlling how AI agents may build here |
| `docs/pr_explanations/README.md` | How to write documents like this one |
| `tasks/TASK-001_...md` | The first and only authorized piece of work |
| `tasks/BACKLOG.md` | Ideas deliberately **not** approved yet |
| `prompts/README.md` | How AI instructions are preserved for the record |
| `docs/pr_explanations/PR-001_...md` | This document |

## 3. Why the change was needed

Radhanite is built mostly by AI agents, which can produce a great deal of change
very quickly. Without rules agreed in advance, three things go wrong: work drifts
beyond what was actually asked for, nobody can tell afterwards which changes were
deliberate, and the project quietly becomes something no one chose.

Writing the constraints down first makes each of those visible instead of
invisible.

## 4. How this worked before

It did not. The repository was empty. There were no rules, no product
definition, and no agreed first task.

## 5. How it works after

There is still **no working software**, and nothing in this pull request runs.

What exists now is a set of agreements:

- Radhanite's purpose is fixed in writing.
- The boundaries of what it will and will not build are fixed.
- One task — and only one — is approved to be built next.
- Every future change must be traceable to something that was authorized.
- Every future pull request must carry a plain-English explanation like this one.

## 6. What goes into the system

No system exists yet, so nothing goes into anything today.

The documents do fix what will go in, once TASK-001 is built. A user will give
Radhanite five things:

- **the task** — the work to be done;
- **the budget** — the most it may spend;
- **the task value** — what getting it done is worth to the user;
- **the constraints** — what it must not do along the way;
- **the success condition** — an objective test of whether it worked.

The budget and the task value are deliberately separate. A budget alone only
answers "can I afford this?". Value is what lets the system answer "is this worth
buying?".

## 7. What the system decides

Nothing yet — there is no system running.

The decision Radhanite will make, once built, is written down and settled. After
each attempt it chooses one of three things: the work succeeded, or spending more
is worth it, or spending more is not worth it and it should stop.

The rule for "is spending more worth it?" is:

> Work out how much the extra spend would improve the chance of success, and what
> that improvement is worth. Spend the money only if that value is greater than
> the cost — and only if the budget can cover it.

Deciding to **stop** is treated as a correct answer, not a failure. An agent that
refuses to keep spending on work that is not worth it has done its job.

## 8. What comes out

Nothing comes out today; there is no program to produce output.

Once TASK-001 is built, each run will produce a record — in plain data form — of
what was asked, what was attempted, what each attempt cost, what was decided, why
it was decided, and what the final result was.

## 9. How it can fail

Because this pull request is documentation, the failure modes are about the rules
rather than about software crashing:

- **The rules could be ignored.** They rely on a human reviewing and merging, and
  on a second AI reviewer checking the work independently.
- **Scope could creep in quietly.** An agent could build something that was never
  approved because it seemed useful. The governance document treats this as a
  violation, and the reviewer is told to look for it specifically.
- **The documents could drift out of step with each other** as decisions change.
  There is a narrow, disclosed rule for correcting a document that an authorized
  decision has made inaccurate.
- **The written plan could simply be wrong.** Nothing here has been tested against
  reality yet, because there is nothing to test.

## 10. Tests run, and their results

**No tests were run, because no tests exist and there is no code to test.**

What was checked instead: that every document is internally consistent, that
cross-references between documents point at sections that actually exist, and
that the repository contains no product code. The last was confirmed
mechanically — the repository contains no files other than documentation and the
licence.

## 11. Assumptions made

- That the human product owner is the sole authority for approving work and
  merging it, and that no AI agent may do either.
- That the copyright holder named in the licence is the repository owner.
- That the first task is best proved with a simulated version of the work, so the
  economic decisions can be judged on their own.
- That competition details not yet confirmed — deadlines, prize tracks — should be
  left blank rather than guessed. They are marked as unconfirmed.

## 12. Known limitations

- Nothing here has been validated by building anything.
- Four decisions inside TASK-001 were made on paper and have never been exercised:
  the escalation rule, the choice of programming language, how run records are
  stored, and how money is represented.
- The governance depends on people and agents actually following it. It is not
  enforced by any tooling.

## 13. Functionality explicitly left out of scope

No product code of any kind was written. Specifically absent, and deliberately so:

- any connection to real AI models or to OpenRouter;
- any wallet, login, or permission system;
- any cryptocurrency, payment, or blockchain component;
- any user interface;
- any machine learning or self-improving behaviour.

None of these is approved, and the documents record them as unapproved so that
their absence is a decision rather than an oversight.

## 14. Deferred to future tasks

- Building TASK-001 itself.
- Connecting Radhanite to real AI models.
- Making the budget real money rather than a number.
- Letting Radhanite learn from its own history instead of using fixed assumptions.
- Anything listed in `tasks/BACKLOG.md`, all of which is marked unauthorized.

## 15. How to explain this to a judge

Radhanite is an economic control layer for AI agents. Instead of giving an AI a
prompt and hoping the result was worth the money, you give it a job, a budget,
what success is worth to you, the rules it must follow, and an objective test of
whether it worked. Radhanite then decides how much intelligence to buy, whether
buying more is justified, and — crucially — when to stop paying.

This pull request contains no software. It is the project's constitution: what
Radhanite is, what it will never build itself, what the first piece of work is,
and the rules the AI agents building it must obey.

That is deliberate, and it is the honest answer to the obvious question. This
project is built largely by AI. Anyone can generate a great deal of code quickly.
What is harder, and what this repository is set up to demonstrate, is that every
single change can be traced to a decision a human actually made — and that the
work stops at the boundary of what was approved.

The first real test of that is TASK-001, which proves the economics work before
any money or any real model is involved.

---

**This document explains; it does not govern.** The product definition, the
architecture document, the task specification, and — once it exists — the code and
its tests are the authoritative record. Where this explanation and the repository
disagree, the repository is correct.
