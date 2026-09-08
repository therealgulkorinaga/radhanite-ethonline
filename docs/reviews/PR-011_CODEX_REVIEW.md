# Codex review — PR-011

**Pull request:** [#11](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/11) — strategy fixtures and deterministic selection (TASK-001)
**Reviewer:** Codex (independent review agent, `AI_BUILD_GOVERNANCE.md` §1.3)
**Reviewed against:** `tasks/TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md`, `docs/PREREQ-001_PRODUCT_DEFINITION.md`, `docs/ARCHITECTURE.md`
**Date issued:** 2026-09-08
**Outcome:** **Rejected** — criteria 2 and 13 were not structurally guaranteed, and Money formatting could silently truncate an exact amount. All six findings corrected.
**Commit reviewed:** `a4d10f7`

---

## 1. Prompt issued

Recorded verbatim, before the review was run.

```text
You are the independent review agent for the Radhanite repository, per
docs/AI_BUILD_GOVERNANCE.md §1.3.

Review pull request #11:
https://github.com/therealgulkorinaga/radhanite-ethonline/pull/11

It implements TASK-001 §2.2 — strategy fixtures and deterministic selection —
and addresses acceptance criteria 2 and 13.

Review against these authoritative documents ONLY:
  - tasks/TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md
  - docs/PREREQ-001_PRODUCT_DEFINITION.md
  - docs/ARCHITECTURE.md

Do NOT treat docs/pr_explanations/PR-011_TASK-001_EXPLANATION.md as evidence of
correctness (§4.3).

PART A — determinism and declared constants

1. Criterion 2 requires identical inputs to produce an identical selection.
   Attack that. Is there ANY path by which selection could vary — dict or set
   iteration order, hashing, module import order, mutable default, global
   state, or the ambient decimal context? The tests assert determinism; try to
   break it rather than trusting them.

2. Criterion 13 requires costs and probabilities to be static declared
   constants, never estimated, learned, inferred, or updated from run history.
   Confirm nothing computes them. Confirm DECLARED_STRATEGIES cannot be mutated
   from outside — try, including via the Strategy objects it contains.

PART B — the selection rule itself

3. The rule is "first strategy in declared order whose initial_cost the
   remaining budget can cover", making catalogue order the policy. TASK-001
   §2.2 requires rules that are fixed and inspectable but does not specify
   which rule. Is order-as-policy a legitimate reading, or has the implementing
   agent invented product policy the specification did not authorize? This is
   the question I most want answered.

4. select() does not take the Task, though §2.2 says "given the task and the
   state of the run so far". The PR argues an accepted-and-ignored parameter
   would be speculative scope under ARCHITECTURE §6 item 7. Assess that
   argument — is omitting it a departure from §2.2?

5. select() returns None when nothing is affordable, and raises on a negative
   budget. Are both defensible, or is either an invented rule (CODEX-PR006-04)?

PART C — scope and boundaries

6. Does anything TASK-001 §3 excludes appear? Any dependency, learned
   probability, database, UI, or ML? Check imports and configuration.

7. Strategy permits an escalation that does not improve, or worsens, the chance
   of success. The PR argues §2.5 must answer that with Stop and forbidding it
   would make that outcome unreachable. Is that correct?

8. Money gained __format__ in this PR, which is not obviously part of §2.2. Is
   that justified scope, or should it have been separate? Does it round, raise,
   or lose precision under a changed ambient decimal context — CODEX-PR006-08
   was exactly this class of defect.

PART D — tests and claims

9. Are the tests real? Mutate and confirm failures: reverse the catalogue
   order, change >= to > in the affordability check, change a declared
   probability, make select() return the last match instead of the first, and
   make DECLARED_STRATEGIES a list.

10. Verify every count and factual claim in the explanation independently —
    file count, per-file and total test counts, and the twelve declared
    figures. Stale hand-maintained counts have been findings five times in this
    project (CODEX-PR003-04, CODEX-PR006-09, CODEX-PR009-01 among them).

FORMAT OF YOUR FINDINGS

Number every finding, per §3.1:

    CODEX-PR011-01
    CODEX-PR011-02
    ...

For each: identifier, file and line, what is wrong, and which specification or
boundary it departs from.

If you find nothing, say so explicitly and raise no findings.

CONCLUDE

End with exactly ONE outcome, per §7.2:
  - Approved
  - Approved with corrections  (list the finding identifiers)
  - Rejected  (state which specification or boundary was departed from)
```

## 2. Findings returned

Recorded verbatim, as returned. Not summarized, softened, or filtered.

> Reviewed PR #11 at `a4d10f7`. The baseline suite passes 130 tests on Python 3.12.13.
>
> The order-based policy is a defensible implementation choice. TASK-001 §2.2 authorizes a fixed, inspectable rule without prescribing one, unlike §2.5’s immutable formula. Omitting an unused `Task` parameter also avoids speculative interface surface under ARCHITECTURE §6 item 7. Returning `None`, rejecting negative remaining budget, and permitting non-improving escalations are consistent with TASK-001’s budget and stopping rules.
>
> No dependency, integration, database, UI, ML component, inferred probability, or other excluded scope appears. All four commits have TASK-001 authority mappings.
>
> All requested mutations were detected:
>
> - Reversing the catalogue caused three failures.
> - Changing affordability from `>=` to `>` caused the exact-budget test to error.
> - Changing a declared probability caused its fixture test to fail.
> - Returning the last affordable match caused two failures.
> - Making the catalogue a list caused the immutability test to fail.
>
> Six findings remain.
>
> CODEX-PR011-01
>
> File and line: `radhanite/strategy.py:35`; `radhanite/strategy.py:95`
>
> `DECLARED_STRATEGIES` is a tuple and ordinary field assignment is blocked, but its supposedly frozen objects remain mutable through their instance dictionaries. For example:
>
> ```python
> DECLARED_STRATEGIES[0].__dict__["initial_cost"] = Money("9.00")
> ```
>
> This succeeded and changed selection from `Direct Attempt` to `Progressive Escalation`. Mutating the nested `Money.__dict__` also succeeded. Thus the declared catalogue can be updated externally despite the static-constant guarantee.
>
> This departs from TASK-001 §2.2 and acceptance criterion 13, which require costs and probabilities to remain static declared constants.
>
> CODEX-PR011-02
>
> File and line: `radhanite/strategy.py:120`; `radhanite/strategy.py:145`
>
> `select()` advertises an ordered `Sequence` but performs no runtime validation and silently accepts unordered collections. Passing `set(DECLARED_STRATEGIES)` with the identical budget selected all three different strategies across hash seeds 1–10.
>
> Sets are outside the annotated contract, but accepting one and returning a hash-dependent economic choice leaves determinism unenforced at the public boundary. It should reject unordered catalogues rather than process them.
>
> This departs from TASK-001 §2.2 and acceptance criterion 2’s identical-input determinism requirement.
>
> CODEX-PR011-03
>
> File and line: `radhanite/money.py:151`; `radhanite/money.py:164`
>
> Delegating every specification to string formatting permits precision specifications that silently truncate the rendered amount:
>
> ```python
> format(Money("123.456"), ".2") == "$1"
> format(Money("123.456"), ".4") == "$123"
> ```
>
> `.2f` is rejected as claimed, and alignment remains exact under altered decimal contexts, but string-precision specifications lose genuine monetary information without raising. The new functionality only needs alignment; truncating formats should be refused.
>
> This departs from TASK-001 §6.6’s exact USD representation and PREREQ-001 §8’s requirement that economic decisions remain inspectable.
>
> CODEX-PR011-04
>
> File and line: `tests/test_strategy.py:75`; `docs/pr_explanations/PR-011_TASK-001_EXPLANATION.md:63`
>
> The test and explanation claim that calculating a fixture instead of declaring it would make the test fail. It only compares resulting values. Replacing the literal `0.35` with a runtime calculation of `Decimal("0.30") + Decimal("0.05")` left the test passing.
>
> The implementation currently does declare the values literally, but the claimed enforcement does not exist. This departs from TASK-001 acceptance criterion 13 and §7’s requirement that documentation claims be demonstrated.
>
> CODEX-PR011-05
>
> File and line: `tests/test_strategy.py:171`; `docs/pr_explanations/PR-011_TASK-001_EXPLANATION.md:83`
>
> `test_the_selector_holds_no_state` only checks the function’s parameter names. Adding a module-level selection-history list and appending every budget inside `select()` did not change the signature, and all 24 strategy tests still passed.
>
> The implementation is currently stateless, but the test cannot prove or preserve that property as claimed. This departs from TASK-001 §7’s prohibition on claiming test guarantees that the tests do not demonstrate.
>
> CODEX-PR011-06
>
> File and line: `docs/pr_explanations/PR-011_TASK-001_EXPLANATION.md:16`; `docs/pr_explanations/PR-011_TASK-001_EXPLANATION.md:26`
>
> The inventory again contains stale counts:
>
> - The PR changes eight files, not seven; `docs/reviews/README.md` is omitted.
> - The PR-wide test count increased from 103 to 130, not from 106 to 130.
> - The remaining counts are correct: 24 strategy tests, three added Money tests, 27 new tests overall, and 130 total.
> - All twelve declared economic figures match the source.
>
> This departs from the prompt’s factual-claim requirement and TASK-001 §7’s review-evidence requirement.
>
> Rejected — TASK-001 §2.2 and acceptance criteria 2 and 13 are not structurally guaranteed, and Money formatting can silently truncate exact USD values contrary to TASK-001 §6.6 and PREREQ-001 §8.

## 3. Outcome

**Rejected.** All six findings were accepted without dispute and corrected.

The two questions the prompt raised against the implementing agent's own doubt
were both answered in its favour: order-as-policy is a defensible reading of
§2.2, which authorizes a fixed inspectable rule without prescribing one; and
omitting an unused `Task` parameter avoids speculative interface surface.

The findings that mattered were three guarantees the code appeared to make and
did not:

- **`-01`** — a frozen dataclass without slots leaves the instance dictionary
  writable. The reviewer changed a declared strategy's price from outside and
  altered which strategy was selected. The tuple around the catalogue gave only
  the appearance of safety.
- **`-02`** — a set was accepted as a catalogue and iterated in hash order,
  producing three different strategies from the same budget across hash seeds.
- **`-03`** — `format(Money("123.456"), ".2")` returned `"$1"`, silently.

`-04` and `-05` were tests asserting properties they could not detect. `-06` was
the sixth instance of a stale hand-maintained count.

## 4. Corrections

| Finding | Correction commit | What changed |
|---|---|---|
| `CODEX-PR011-01` | `b463c28` | `slots=True` on every frozen dataclass in the project — Money, Probability, Task, Strategy, EscalationDecision — so no instance dictionary exists to write through. |
| `CODEX-PR011-02` | `b463c28` | Unordered collections refused at the boundary rather than turned into a hash-dependent economic decision. |
| `CODEX-PR011-03` | `b463c28` | Format specs containing a precision refused; alignment and width still supported. |
| `CODEX-PR011-04` | `21683af` | The fixture test now parses the source with `ast` and requires all twelve figures to be literal constants — no arithmetic, no lookups, no calls. The reviewer's exact substitution now fails it. |
| `CODEX-PR011-05` | `21683af` | Statelessness now checked by snapshotting every mutable value the module and the function hold, before and after a series of selections. Verified against both a module-level list and state hung on the function. |
| `CODEX-PR011-06` | `5aad0a8` | Counts corrected to eleven files and 103 → 137. The table now has one row per file so row-count and diff agree. Counts are taken as the final step, after every commit. |

```
git log --grep=CODEX-PR011
```

### Verification after correction

```
$ python -m unittest discover
Ran 137 tests in 0.012s
OK
```

Every reported defect retested:

```
DECLARED_STRATEGIES[0].__dict__["initial_cost"] = ...   -> AttributeError
strategy.initial_cost.__dict__["amount"] = ...          -> AttributeError
select(set(DECLARED_STRATEGIES), Money("2.00"))         -> TypeError
format(Money("123.456"), ".2")                          -> ValueError
Probability(Decimal("0.30") + Decimal("0.05"))          -> ast test fails
module-level history list in select()                   -> state test fails
state hung on select itself                             -> state test fails
```

### A note on the verification method

An early mutation run reported the module-level history list as *undetected*.
That was a stale bytecode cache rather than a passing test — re-run in isolation
with caches cleared, it fails as it should. The first result was wrong. It is
recorded because a verification method that can report a false pass is worth
knowing about, and subsequent mutation checks cleared caches between runs.
