# PR-002 — Who Radhanite is for

**Pull request:** #2
**Authority:** PREREQ-001 (prerequisite)
**Author:** Claude Code, under human product owner authorization

---

## 1. Purpose of this PR

To answer a question the product definition never answered: **who is this for?**

The document already said what Radhanite does and why the idea matters. It never
said which people have the problem, which of them would run the thing, or which
of them would pay for it.

## 2. What changed

One new section, `§2.1 Who this is for`, was added to
`docs/PREREQ-001_PRODUCT_DEFINITION.md`. Nothing else in the repository changed.

The section names three roles for the first version, restates the problem those
people actually have, and sketches how the audience widens later.

## 3. Why the change was needed

A product definition that does not name its audience cannot be checked against
reality. "Agents cost too much" is true of everyone and therefore useful to no
one. Naming the buyer forces a sharper claim: someone specific is accountable
for what these agents cost and whether they worked, and right now nothing
connects those two facts for them.

It also protects against a subtle drift. Without a named audience, a project can
gradually redefine itself to suit whatever it happens to have built.

## 4. How this worked before

The product definition described the problem in general terms — spend is
discovered after the fact, escalation is a guess, agents retry until something
external stops them — but attributed it to no one in particular.

## 5. How it works after

The same problem is now attributed to specific people:

- **Users** — engineering teams running autonomous coding agents.
- **Operator** — the person who deploys and supervises those agents day to day:
  an engineering lead, AI platform engineer, or developer-tooling owner.
- **Buyer** — the leader accountable for both agent performance and what the
  agents cost: a CTO, VP Engineering, or Head of AI Platform.

The section also states, plainly, that the problem is **not** that AI is
expensive. Expense is fine when the result is worth it. The real gap is that
nothing decides how much intelligence to buy for a given piece of work, so teams
miss in both directions — paying for premium models where it changes nothing, or
under-spending and getting worse results. Neither miss is visible until the money
is already spent.

## 6. What goes into the system

Nothing changed here. This PR adds no inputs and no behaviour; the five inputs a
task requires are unchanged.

## 7. What the system decides

Nothing changed here. The rule for deciding whether to spend more is untouched.

## 8. What comes out

Nothing changed here. There is still no running software in this repository.

## 9. How it can fail

This is a written description of an audience, so the failure modes are about
being wrong rather than about breaking:

- **The audience could be wrong.** No user has been interviewed. This is a
  stated belief, not a finding.
- **It could quietly become a sales document.** The section was deliberately kept
  short and excludes market sizing, pricing, and go-to-market material, which
  belong nowhere near a product definition.
- **The long-term section could be mistaken for a plan.** It closes by stating
  that it records intended direction, not authorization.

## 10. Tests run, and their results

**No tests were run. There is still no code in this repository to test.**

What was checked instead: that the new section did not renumber any existing
section, because three cross-references elsewhere point at sections by number.
Those numbers were verified unchanged after the edit. It was also confirmed that
no other document contradicts the new section, so no further edits were needed.

## 11. Assumptions made

- That the operator and the buyer are usually different people, and that the
  disconnect between them is a real part of the problem.
- That the same economic problem generalizes beyond software engineering. This
  is a belief about direction, recorded as such.
- That naming an audience is part of defining a product, and does not require a
  separate document to live in.

## 12. Known limitations

- Nothing here is validated by contact with a real team.
- The roles are described by job title, which varies between organizations.
- The long-term expansion is a sketch, not a plan, and nothing has been approved
  on the strength of it.

## 13. Functionality explicitly left out of scope

No code, and no product decisions of any kind. This PR does not change the five
inputs, the way strategies are chosen, the rule for deciding whether to spend
more, the architectural boundaries, or the scope of the first task.

It also deliberately excludes ideal-customer profiles, go-to-market plans, market
sizing, and pricing.

## 14. Deferred to future tasks

- Building TASK-001, which remains the only authorized piece of work.
- Testing any of these audience assumptions against real teams.
- Everything in `tasks/BACKLOG.md`, all of which remains unauthorized.

## 15. How to explain this to a judge

Radhanite decides how much intelligence an AI agent should buy to finish a job,
and when to stop paying. This change answers who that is for.

In the first version it is engineering teams running autonomous coding agents.
One person deploys and supervises those agents; a different person — a CTO or a
VP of Engineering — answers for what they cost and whether they worked. Nothing
today connects those two things, so teams either overpay for premium models that
change nothing, or underpay and get worse results, and they find out only after
the money is gone.

The point worth making is the framing. The problem is not that AI is expensive.
It is that spend cannot be tied to finished work. That is a control problem, and
control problems have solutions.

---

**This document explains; it does not govern.** The product definition,
architecture document, task specification, and — once it exists — the code and its
tests are the authoritative record. Where this explanation and the repository
disagree, the repository is correct.
