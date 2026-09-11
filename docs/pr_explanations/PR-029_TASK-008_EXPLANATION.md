# PR-029 — The socket the integrations plug into

**Pull request:** #29
**Authorized task:** TASK-008, PR A
**Author:** Claude Code, under human product owner authorization

---

## 1. Purpose of this PR

One boundary: **turn a capability that is actually for sale into something the
economic rule can judge.**

It selects nothing, executes nothing, pays nothing, and updates no task state.

The point of doing this before any integration is that Circle, The Graph and
Hedera would otherwise each invent their own idea of what a capability is, and
we would discover the mismatch while wiring the third one.

## 2. What changed

| File | |
|---|---|
| `radhanite/acquisition.py` | **New.** The whole boundary |
| `tests/test_acquisition.py` | **New.** 38 tests |
| `radhanite/__init__.py` | Exports |
| `tasks/TASK-008_CAPABILITY_ACQUISITION.md` | Status, and what PR A delivered |
| `docs/reviews/PR-029_...`, `docs/pr_explanations/PR-029_...`, `docs/reviews/README.md` | Review prompt, this document, the index row |

**No dependency.** The project still has none.

## 3. Why the change was needed

TASK-006's `Candidate` is three fields and must stay that way — the moment it
knows who is selling, selection stops being economic. But an adapter has to know
how to invoke the thing it bought.

Both are true, so they need two types and a mapping between them. That is this.

## 4. How this worked before

Nothing bridged them. The declared fixtures were candidates already, which works
for a test and answers nothing about a real source.

## 5. How it works after

### Two types, deliberately

**`CapabilityDescriptor`** — what the source says: an identifier, a name, an
exact price, and an opaque reference the adapter will use to invoke it. Four
fields, because that is the fewest that lets an adapter recover its own handle
after selection without this layer understanding what the handle means.

**`Candidate`** — unchanged, still exactly identifier, cost, probability.

**The asymmetry is the whole design.** Acquisition knows who is selling; the
decision does not. A test asserts `Candidate`'s shape is untouched, and others
assert the name and the source reference never appear in it.

### The known-price invariant

> A capability may enter the candidate set only when its exact cost is known
> **before purchase.**

There is deliberately **no representation for an unknown price**. A source that
cannot quote cannot construct a descriptor at all — not a placeholder, not a
zero, not `None`. The refusal says why, because the next person to hit it will
be tempted to add an estimate.

That matters because the rule this feeds is `value > cost`, and a comparison
against a price nobody has yet is not a comparison.

### Identity

The candidate takes the descriptor's identifier, unchanged. One rule, nothing to
derive, nothing to drift.

A capability offered again after the state changes arrives as a **new
descriptor with a new identifier from its source** — which is what makes it a
new candidate under TASK-006 §2.5a, and why this layer needs no notion of
capability type.

### Recovering what was bought

`CapabilityCatalog` holds the pairs and answers `descriptor_for(candidate_id)`.
An unknown identifier raises `KeyError` rather than returning something
plausible: a selection can only be executed against the catalogue it came from.

## 6. What goes into the system

Descriptors from some source, each with a declared expected post-action
probability. **Probabilities are supplied, never computed** — nothing here
estimates, learns, or infers one, least of all from who is selling.

## 7. What the system decides

**Nothing.** It refuses malformed input and translates well-formed input.

Tests assert the module exports nothing named for selecting, executing or
paying, that neither function takes task state or budget, and that the source
contains no HTTP or socket call.

## 8. What comes out

A `CapabilityCatalog`: candidates in offer order for TASK-006, and the mapping
back for whoever executes the winner.

## 9. How it can fail

Every failure is a refusal at construction: a blank or padded identifier, a
missing name, a cost that is not exact money, a non-positive cost, a probability
that is not a `Probability`, an unordered offer, a malformed pair, or two
capabilities sharing an identifier.

The failure mode that matters most is not an exception — it is `Candidate`
quietly acquiring a fourth field. Three tests guard that specifically.

## 10. Tests run and their results

**Before** — written first, run against the code as it stood:

```
ImportError: cannot import name 'acquisition' from 'radhanite'
Ran 477 tests — FAILED (errors=1)
```

An import failure proves absence, not that each assertion discriminates. The
mutations below establish that.

**After:**

```
$ python3.12 -m unittest discover -q
Ran 514 tests in 0.14s
OK
```

**476 existing, unchanged, plus 38 new.**

### Deliberate faults, all caught

Bytecode writing disabled throughout.

| Fault introduced | Result |
|---|---|
| Replace the descriptor's cost with a default | **2 failures** |
| Allow a zero cost | **3 failures** |
| Alter the supplied probability | **2 failures** |
| Allow duplicate identifiers | **1 failure** |
| Break the candidate → descriptor lookup | **1 failure, 1 error** |
| Put the source reference into the candidate ID | **4 failures** |
| Store a mutable list as the catalogue's entries | **1 failure** |

**The last one initially survived, and the reason was a weak test.** It checked
that mutating the *caller's* list after the call changed nothing — which passes
whatever the code does, because `acquire` builds its own list either way. The
real exposure is the catalogue's own field being a list anyone holding it could
append to. A test now asserts it is a tuple, and the mutation fails.

**One test was corrected during implementation.** A scan for provider names
flagged `arc` inside **research**. Renaming the content to satisfy the scan
would have made the module worse; the scan now matches whole words, and gained
`marketplace` and `sponsor` while it was being fixed.

## 11. Assumptions made

- **Descriptors come from somewhere.** Generating them from task state is not
  this PR.
- **`source_reference` is opaque.** A string this layer stores and never reads.
- **Probabilities are benchmark-declared**, per TASK-008 §4.

## 12. Known limitations

- **Nothing produces descriptors yet.** `acquire` has no production caller until
  an adapter exists — worth naming, since code without a caller is normally a
  smell.
- **TASK-008 §6.1 is still unresolved**: what makes two offers "the same
  capability" across iterations. The identity rule sidesteps it by deferring to
  the source, which is correct for now and not an answer.
- **`source_reference` being a bare string** may prove too thin for some adapter.
  Widening it is a specification change, not an implementation detail.

## 13. Explicitly out of scope

Every provider — Circle, Arc, x402, Nanopayments, Agent Wallets, Tavily,
BlockRun, The Graph, Hedera, OpenRouter. Live discovery, HTTP, adapters, revenue
reasoning, probability estimation, ranking, eligibility, execution, task-state
updates, run-loop orchestration, payment. No bounded-price mechanism.

**No change to TASK-006 or TASK-007 behaviour**, to `Money`, `Probability`,
`Candidate`, `Assessment` or `Selection` — verified: every existing module is
byte-identical to `main` apart from `__init__.py`'s exports.

## 14. Deferred to future tasks

TASK-009 through TASK-014. TASK-008 §6.1.

## 15. How to explain this to a judge

> Before wiring up three different capability providers, we built the shape they
> all have to fit.
>
> There are two types on purpose. One knows what the thing actually is — its
> name, where it came from, how to call it. The other has three fields and is
> all the pricing engine ever sees: an identifier, a price, and how much better
> your odds get.
>
> The engine is not allowed to know who is selling. That is the whole claim, and
> this is where it is enforced — there is a test that reads our own source code
> and fails if a supplier's name appears in it.
>
> One rule is stricter than it looks: **a capability cannot be offered unless its
> exact price is already known.** Not estimated, not discovered by buying it.
> There is no way to represent an unknown price, which is deliberate — you cannot
> decide whether something is worth £5 if nobody will tell you it costs £5.
