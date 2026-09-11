# PR-028 — A new benchmark, and an engine that did not move

**Pull request:** #28
**Authority:** product-direction decision by the human product owner, recorded per `AI_BUILD_GOVERNANCE.md` §3
**Author:** Claude Code, under human product owner authorization

---

## 1. Purpose of this PR

The benchmark changed. **The engine did not.**

Radhanite's demonstration is now **autonomous revenue opportunity pursuit** — an
agent pursuing a deal it could win, deciding what evidence and judgement are
worth buying. Supplier onboarding was the previous framing and is preserved as
such.

**Documentation only.** No runtime code, no tests, no dependencies, no APIs.
476 tests, unchanged.

## 2. What changed

| File | |
|---|---|
| `docs/PREREQ-001_PRODUCT_DEFINITION.md` | §6 rewritten; §6.3a preserves the previous benchmark |
| `docs/ARCHITECTURE.md` | The task sequence, and The Graph's role as evidence |
| `README.md`, `site/index.html` | The headline benchmark |
| `tasks/TASK-008` … `TASK-014` | **Six new task files** |
| `tasks/TASK-011_..._THE_GRAPH.md` | **Renamed** from TASK-008; content unchanged |
| `tasks/BACKLOG.md` | The task sequence as an index |
| `tasks/TASK-006`, `TASK-007` | **Two sentences each** — the passing mentions of the old benchmark |
| `docs/reviews/PR-028_...`, `docs/pr_explanations/PR-028_...`, `docs/reviews/README.md` | The review prompt, this document, the index row |

## 3. Why the change was needed

Supplier diligence made the economic question unavoidable. Revenue pursuit makes
the **failure visible**.

A $50,000 contract and a $250 budget look like permission to buy everything
available — and an agent that does has made no economic decision at all. The new
benchmark is built so that **poor execution strategy destroys margin even when
the opportunity is large**, which is the thing nobody currently measures.

Unused budget becomes **retained margin** rather than an awkward result to
explain. §4.2's rule — budget is permission to spend, not a target — stops being
a caveat and becomes the point.

## 4. How this worked before

`PREREQ-001` §6 named supplier onboarding. Three integration tasks existed, in a
priority order, with no generic boundary between the engine and them.

## 5. How it works after

### The benchmark

```
Opportunity        a $50,000 crypto-native infrastructure contract
Operating budget   $250
Available          research, onchain intelligence, specialist analysis,
                   independent review — each priced, each optional
Question           what should it spend next, if anything?
```

### The layers, and who decides

> **Circle tells the agent what it can buy and how to pay. The Graph and Hedera
> are things it can buy. Radhanite decides what is worth buying.**

Marketplace services — Tavily-backed research, BlockRun analysis — are
**candidates**, discovered and evaluated. **None is a mandatory step.** A run
that rejects all of them is a correct run.

The Graph returns **evidence**, not a probability. It reaches TASK-009, which
interprets it; the economic rule never sees it. Hedera supplies **one** paid
second opinion — not a second marketplace — and being a second opinion earns it
no preference.

### The task sequence

| | Task | Layer |
|---|---|---|
| 006 | Capability selection | **Engine** — implemented |
| 007 | Run loop | **Engine** |
| 008 | Capability acquisition | **Boundary** — descriptors become candidates |
| 009 | Revenue opportunity state | **Benchmark reasoning** |
| 010–012 | Circle, The Graph, Hedera | **Adapters** |
| 013–014 | Benchmark, presentation | **Assembly** |

**TASK-008 is the new load-bearing boundary.** Acquisition knows who is selling;
the decision does not. That asymmetry is what lets adapters be provider-specific
while §2.1 stays neutral.

**TASK-009 is where the benchmark lives, and the only place it may.** Putting
opportunity reasoning into the engine would make Radhanite a sales tool with an
economic layer attached, rather than an economic layer with a sales benchmark on
top.

## 6. What goes into the system

Nothing. No runtime changed.

## 7. What the system decides

Nothing new. **TASK-006's economic rule and TASK-007's runtime semantics are
untouched** — verified: neither file's behavioural content changed, and
`radhanite/` and `tests/` are identical to `main`.

## 8. What comes out

A repository whose roadmap matches what is being built, with the engine and the
benchmark visibly separated.

## 9. How it can fail

**By letting the benchmark into the engine.** The pressure is real: a sales
benchmark wants the selector to know it is pursuing revenue. Every such concept
is confined to TASK-009 and the adapters, and TASK-006 §3 now excludes
benchmark-specific rules by name rather than by naming one vertical.

**By presenting sponsors as a workflow.** A demo that always calls the same
services in the same order is wiring. `PREREQ-001` §6.3 forbids it, and TASK-013
requires four scenarios with different orders from the same engine — including
one that abandons cheaply.

## 10. Tests run and their results

```
$ python3.12 -m unittest discover -q
Ran 476 tests in 0.13s
OK
```

**Unchanged.** This PR contains no code; the suite was run to confirm the file
rename and the documentation edits disturbed nothing.

## 11. Assumptions made

- **The decision is the product owner's and is final.** Recorded, not argued.
- **The engine genuinely did not need to move.** TASK-006 and TASK-007 were
  written task-agnostic, and the pivot tested that: nothing in either required
  redesign.

## 12. Known limitations

- **TASK-008 through TASK-014 are specifications, several thin.** 010, 012, 013
  and 014 state purpose and boundaries; none could be built from as written.
- **Two unresolved decisions remain**, in TASK-008 §6.1 and TASK-009 §7 —
  candidate identity across iterations, and how evidence becomes a probability.
  The second has moved from "nobody owns it" to "TASK-009 owns it and has not
  answered it", which is progress but not an answer. **TASK-008 §6.2 is now
  resolved** — see §14a.
- **`PREREQ-001` now carries three framings** — software engineering (§6.4),
  supplier onboarding (§6.3a), revenue pursuit (§6). §6.6 tabulates which is
  implemented and which is current. That is honest, and it is also a document
  accumulating history.

## 13. Explicitly out of scope

No runtime code, tests, dependencies or APIs. No implementation of TASK-008 or
beyond. No change to TASK-006's economics or TASK-007's semantics. No
integration authorized. **No immutable review record or historical PR
explanation was edited** — where they describe supplier onboarding, they
describe what was true when written.

## 14. Deferred to future tasks

All of TASK-008 through TASK-014, and the three unresolved decisions in §12.

## 14a. Corrections after review

Two material contradictions the first version left standing, both now closed.

### The completion contract was still the supplier one

`PREREQ-001` §6.5 is **current** benchmark definition, and it still required
`APPROVE` | `ESCALATE` | `REJECT` over evidence categories carrying
`resolved` | `unresolved` | `not_found`. The benchmark had changed; its success
condition had not.

The current contract now uses **`PURSUE` / `ABANDON` / `ESCALATE`**, defined
narrowly, with **nine machine-checkable clauses**: one terminal outcome from the
closed set, every required state field accounted for, every material unresolved
question explicitly represented, the probability represented per the fixture
contract, spend within the operating budget, no execution past the step ceiling,
no consumed ID reused, a deterministic terminal reason, and a record sufficient
to audit why Radhanite stopped.

**These are benchmark outcomes, not predictions.** `PURSUE` does not assert the
deal will be won. Radhanite does not forecast sales outcomes and no document may
say it does.

The old contract is preserved in §6.5 as **historical**, attached to the framing
in §6.3a. Its *shape* survived — a closed outcome set, explicit representation of
the unknown, spend inside the ceiling — because the shape was right and only the
vocabulary was supplier-specific.

The contract is also now explicit that it **is not the economic rule**: three of
its clauses restate constraints TASK-006 and TASK-007 already enforce, and it
checks a completed run rather than deciding anything.

### Pricing before purchase — resolved, not accommodated

TASK-008 §6.2 had suggested a source might not know its price before execution,
which would break TASK-006 §2.3. **TASK-006 was not weakened.**

> **A capability may enter the candidate set only when its exact cost is known
> before purchase.**

The confusion was between two different acts, now separated explicitly:

| | When | Costs money? |
|---|---|---|
| **Discovery / quote** | Before economic selection | **No** |
| **Purchase / execution** | Only after selection | Yes |

Reading a price is not buying anything, and **no payment is made merely to
discover a price** — a source charging for its quote would make the decision
itself cost money, which is a different product.

**Circle satisfies this today.** Discovery responses expose payment terms before
purchase, including the required amount and invocation metadata; TASK-008
normalizes that quoted amount into the candidate cost.

A source that genuinely cannot quote is **not eligible** — not offered, not
approximated, not given a placeholder. It becomes eligible only if a future
authorized task introduces a deterministic pre-purchase quote or a bounded-price
mechanism, and **that mechanism is not designed here.**

### Not done deliberately

`PREREQ-001` still carries three framings. The authorization was explicit that a
broad structural rewrite is **not** part of this correction, and the statuses are
unambiguous, so the document keeps its history for a later cleanup task.

## 15. How to explain this to a judge

> We changed what we're demonstrating and didn't change the engine.
>
> The demo is now an agent chasing a $50,000 contract on a $250 budget. It can
> buy research, onchain intelligence, a specialist second opinion — all priced.
> The interesting failure is that a big opportunity makes people spend badly, and
> spending badly destroys the margin you were chasing.
>
> What matters for the architecture is what *didn't* move. The part that decides
> whether something is worth buying doesn't know it's pursuing revenue, and
> can't — everything about deals lives in one layer above it. We proved that by
> changing the benchmark and touching two sentences in the engine.
>
> And the sponsors sit underneath. Circle says what's for sale and handles
> payment; The Graph and Hedera are things you can buy. We decide what's worth
> buying — including deciding to buy nothing.
