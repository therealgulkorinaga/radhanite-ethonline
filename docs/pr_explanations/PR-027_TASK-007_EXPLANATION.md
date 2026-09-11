# PR-027 — Specifying the loop that makes the engine run

**Pull request:** #27
**Authority:** product-direction decision — `BL-16` promoted to a task by the human product owner
**Author:** Claude Code, under human product owner authorization

---

## 1. Purpose of this PR

To specify the missing piece: **the loop that asks the decision repeatedly.**

TASK-006 delivered a decision. It decides once, and then nothing happens. This
specifies what keeps the state, acts on each answer, and stops.

**No code. No integration. TASK-006 untouched.** 476 tests, unchanged.

## 2. What changed

| File | What it is |
|---|---|
| `tasks/TASK-007_CAPABILITY_RUN_LOOP.md` | **New.** The specification |
| `tasks/TASK-008_..._THE_GRAPH.md` | **Renamed** from TASK-007. Content unchanged but its number |
| `tasks/BACKLOG.md` | `BL-16` promoted; the renumbering recorded |
| `tasks/TASK-006_...md` | §5a now points at where its two inherited criteria went |
| `tasks/TASK-003_..._PRIVY.md`, `docs/ARCHITECTURE.md` | Links follow the rename |
| `docs/reviews/PR-027_CODEX_REVIEW.md` | Review prompt, **committed before the review** |
| `docs/reviews/README.md`, `docs/pr_explanations/PR-027_...md` | Its row; this document |

## 3. Why the change was needed

Three things now point at the same hole.

TASK-006 §5a records two acceptance criteria it cannot satisfy. `PREREQ-001` §6
describes a demonstration that buys several capabilities in sequence. And
TASK-008 §6.3 needs somewhere for returned evidence to become a new probability.

All three need a loop, and no task owned one.

## 4. How this worked before

`BL-16` was a one-line backlog entry. The kernel had nothing driving it.

## 5. How it works after

### The loop

```
run state → candidate set → eligibility → ranking
          → STOP, or execute exactly one capability
          → commit spend, consume the ID, increment the step count
          → obtain updated state → repeat
```

**One iteration buys at most one capability.** Two would make the step count
meaningless and the safeguards unenforceable.

### The state, and what it deliberately excludes

Eleven fields, including **`task_state`** — opaque, stored and passed but never
read by this task or by the decision. Carrying only a probability would have
made candidate generation, state updating and audit reconstruction impossible: a
probability is a *summary* of a state, not the state.

Excluded because nothing needs them: task text, constraints, provider identity,
per-capability metadata, retry counters.

`remaining_budget` and `total_spend` are both carried although either derives
from the other. **The derivation is the invariant** — a record stating only one
would make it uncheckable afterwards.

The history is a **non-recursive** sequence of transition records. Each holds a
before-snapshot, the complete `Selection`, the execution result, and an
after-snapshot — and **snapshots exclude the history**, so nothing contains
itself. The `Selection` is kept whole, because TASK-006 §8 already requires the
rejected candidates and their reasons.

### Three interfaces, all provider-neutral

**Candidate source** — returns the current offer. Where candidates came from is
not this task's concern and must not become visible to it. The declared fixtures
already satisfy it, which is how the loop can be tested with no integration in
existence.

**Capability executor** — performs the selected capability, returns a structured
result. **No payment or provider fields**, because a provider name here would
reach the decision through the state updater.

**Task-state updater** — turns a result into a new probability and a completion
verdict. **The domain reasoning lives here and emphatically not in the loop.**
It is the same open question as TASK-008 §6.3, and no authorized task owns it.

### Four terminal states, with precedence

`TASK_COMPLETE` · `ECONOMIC_STOP` · `SAFETY_STOP` · `EXECUTION_FAILURE`.

**Already-complete is checked first**, before any candidate. A finished task
terminates `TASK_COMPLETE` even at a zero-step policy, even at the ceiling, even
with eligible candidates on offer. A completed task is not stopped by a ceiling;
it is finished.

The two STOP kinds are **read from**
`Selection.stopped_without_economic_judgement` rather than re-derived. Mixed
failures are recorded as they happened: one economic refusal makes it an
`ECONOMIC_STOP`, and every per-candidate reason survives in the `Selection`.

## 6. What goes into the system

Nothing runs. The specification names what a run would be initialized with:
task value, initial budget, a `RunPolicy`, and a starting task state.

## 7. What the system decides

Nothing new. **The loop makes no economic judgement** — it asks TASK-006 and
acts on the answer. §12 asks a reviewer to confirm no formula, condition,
ranking or threshold moved into it.

## 8. What comes out

An auditable run history: every decision, every candidate considered including
the losers, every state transition, and which of the four terminal states ended
the run.

## 9. How it can fail

**Twelve invariants** are specified, each with a test behind it in §9 of the
task. The ones that matter most: no capability executes unless TASK-006 selected
it; at most one per iteration; nothing executes after a terminal state; and an
execution failure can never appear as successful completion.

The real risk is the loop quietly acquiring economics — a retry threshold, a
preference, a special case. Every one of those would be a rule nobody decided.

## 10. Tests run and their results

```
$ python3.12 -m unittest discover -q
Ran 476 tests in 0.13s
OK
```

**Unchanged.** This PR contains no code; the suite was run to confirm the
repository is green and that the file rename broke nothing.

The specification requires **17 acceptance tests**, listed in its §9.

## 11. Assumptions made

- **The kernel is the right shape to loop around.** It is: eligibility and
  selection already take the state this task would maintain.
- **The declared fixtures satisfy the candidate-source interface**, so the loop
  is testable before any integration exists.

## 12. Known limitations

- **One unresolved product decision**, in §7 of the task: what happens to spend,
  consumption, the step count and retryability when a capability call fails.
  Four options, one recommended, none chosen. Implementation cannot begin
  without it.
- **§5.3's domain reasoning has no owner.** How evidence becomes a probability
  is orchestrated here and defined nowhere.
- **TASK-006 is not made complete by this.** It closes when a TASK-007
  implementation demonstrates criteria 10 and 13 — not because a specification
  promising to exists.

## 13. Explicitly out of scope

No code. No integration — Hedera, Circle/Arc, The Graph, Privy, OpenRouter all
remain unauthorized and untouched. No candidate discovery, provider discovery,
capability-specific logic, payment internals, learned estimation, or
sponsor-specific routing. No change to TASK-006's formula, conditions, ranking
or safeguards.

## 14. Deferred to future tasks

Deciding §7. Then authorizing and implementing TASK-007. Then whoever owns
§5.3's reasoning.

## 14a. Corrections after the Codex review

Five findings, all corrected. Together they changed the state model, the history
structure, the accounting, the terminal states and two acceptance criteria — so
§§2–9 were rewritten rather than patched.

**`-01` — the loop carried a summary, not the state.** It held
`current_success_probability` and nothing else. But candidate generation needs
to know what the task looks like, the state updater needs the previous state,
and audit reconstruction needs both. A probability is a summary of a state, not
a substitute for one. `task_state` is now carried: **opaque**, passed to the
candidate source and the updater, and **never read** by this task or the
decision. Producing and interpreting it is explicitly a separate future task.

**`-02` — the history defined itself.** A history entry contained the complete
post-transition run state, which contains the history. That is circular and
cannot be constructed. It is now a sequence of immutable transition records,
each holding **snapshots that exclude the history**. Rejected-candidate
reasoning survives because the whole `Selection` is still kept.

**`-03` — the accounting contradicted TASK-006.** The invariant
`total_spend + remaining_budget == initial_budget` was asserted alongside a
definition of `total_spend` as loop spend only. TASK-006 §2.2a already defines
`remaining_budget` as net of *everything*, baseline included, so the two could
not both be true. `total_spend` now means all spend from the initial budget, and
initialization must satisfy `total_spend = initial_budget - remaining_budget`.
No separate pre-loop field was added: it is derivable, it duplicates a fact the
first transition already records, and a redundant field can drift. Criterion 12
tests the initialization directly.

**`-04` — a STOP was assumed to be economic.** Criterion 2 said every "no
eligible candidate" outcome was an `ECONOMIC_STOP`. False — a run stopped by the
step ceiling refused nothing on economic grounds. Classification is now derived,
with the mixed case defined, and **already-complete given explicit precedence**
over a zero-step policy, a reached ceiling, and available candidates.

**`-05` — the neutrality criterion claimed too much.** It required candidates
differing only in provider metadata to produce **identical complete runs**.
TASK-006 guarantees no such thing: it guarantees identical *assessments* and
*selection*. Two capabilities priced the same may then do entirely different
things and send the run down different paths. Criterion 20 now asserts what is
actually guaranteed, and §9a states plainly what it does not.

### Execution semantics, now specified

The product owner supplied them following review, and they are stronger than the
four options the earlier draft offered.

The executor returns `committed_cost` — exact `Money`, bounded by the
candidate's declared cost and by the remaining budget. **That figure drives the
accounting, not the declared cost**, and failure does not imply zero spend: a
call that debited then failed committed real money.

Every attempt consumes the ID and records the cost. The paid-step count rises
**only when the committed cost is positive**. Failure terminates the run as
`EXECUTION_FAILURE`, with no retry.

**One claim from the earlier draft was withdrawn.** It said consuming the
candidate ID guaranteed termination on the failure path. It does not — nothing
stops a candidate source regenerating an equivalent capability under a fresh ID.
Termination now rests on §7.3's explicit terminal state, and §7.3 says so.

## 14b. A note on the renumbering

The Graph was TASK-007 and is now **TASK-008** — the number the product owner
originally proposed for it. It was given 007 in PR #25 because 007 was free and
a gap in the sequence seemed worse than a different number; that judgement is
now reversed, since the run loop needed 007. **Nothing about that specification
changed but its number**, and `BACKLOG.md` records the move so a reader
following an old link is not left guessing.

## 15. How to explain this to a judge

> We built an engine that decides whether something is worth buying. It works,
> it's tested, and it decides exactly once — then stops, because nothing asks it
> again.
>
> This specifies the thing that asks repeatedly: keep the budget, remember what
> you already bought, count the purchases, and stop when the engine says stop or
> when you've hit your limit.
>
> The interesting part is what it's forbidden from doing. It makes no economic
> judgements of its own — it can't prefer a supplier, can't retry on a hunch,
> can't decide something was worth it. It asks the engine and does what it says.
>
> And there's one question we refused to answer ourselves: what happens when a
> purchase fails. Four options are written down with a recommendation and a note
> saying a human has to pick before anyone writes code — because that choice is
> economics, and economics isn't the loop's to decide.
