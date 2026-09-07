# Codex review — PR-003

**Pull request:** [#3](https://github.com/therealgulkorinaga/radhanite-ethonline/pull/3) — project skeleton and a working test command (TASK-001)
**Reviewer:** Codex (independent review agent, `AI_BUILD_GOVERNANCE.md` §1.3)
**Reviewed against:** `tasks/TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md`, `docs/PREREQ-001_PRODUCT_DEFINITION.md`, `docs/ARCHITECTURE.md`
**Date issued:** 2026-09-07
**Outcome:** **Rejected** — TASK-001 §1's no-external-dependencies requirement was departed from by `pytest` and `hatchling`.
**Commit reviewed:** `887e9f6`

---

## 1. Prompt issued

Recorded verbatim, before the review was run.

```text
You are the independent review agent for the Radhanite repository, per
docs/AI_BUILD_GOVERNANCE.md §1.3.

Review pull request #3:
https://github.com/therealgulkorinaga/radhanite-ethonline/pull/3

Review the implementation against these authoritative documents ONLY:
  - tasks/TASK-001_DETERMINISTIC_ECONOMIC_LOOP.md
  - docs/PREREQ-001_PRODUCT_DEFINITION.md
  - docs/ARCHITECTURE.md

Do NOT treat docs/pr_explanations/PR-003_TASK-001_EXPLANATION.md as evidence
that the implementation is correct. Per §4.3 the explanation is not
authoritative. A confident, well-written explanation of behaviour that the code
does not actually exhibit is a defect to catch, not a reason to approve.

Answer these specifically:

1. Does the PR do what it claims, and ONLY that?

2. Does it contain anything TASK-001 §3 excludes? That list is: OpenRouter,
   real model APIs, Privy, Arc/USDC, Hedera, x402, production UI, machine
   learning, contextual bandits, reinforcement learning, any database, and
   learned or inferred probabilities. Check dependencies and configuration,
   not just source files.

3. Does it violate any boundary in ARCHITECTURE.md §6, including item 7
   (abstractions whose only justification is a future unauthorized task)?

4. Is Python pinned to 3.12, as TASK-001 §6.4 requires?

5. Are the two tests in tests/test_package.py real tests, or do they pass
   regardless of the state of the code?

6. Does every commit map to an authorized task, prerequisite, governance
   amendment, or documented review correction, per §3?

7. Is there any claim in a commit message, docstring, or code comment that the
   code does not actually support?

FORMAT OF YOUR FINDINGS

Number every finding you raise, in this exact form, per §3.1:

    CODEX-PR003-01
    CODEX-PR003-02
    ...

For each finding give: the identifier, the file and line it concerns, what is
wrong, and which specification or boundary it departs from. These identifiers
will be referenced by the commits that fix them, so number them in the order you
list them and do not reuse a number.

If you find nothing, say so explicitly and raise no findings.

CONCLUDE

End with exactly ONE outcome, per §7.2:
  - Approved
  - Approved with corrections  (list the finding identifiers to be fixed)
  - Rejected  (state which specification or boundary was departed from)
```

## 2. Findings returned

Recorded verbatim, as returned. Not summarized, softened, or filtered.

> Reviewed PR #3 at `887e9f6` against the three specified authoritative documents.
>
> 1. The implementation is limited to project scaffolding and tests, but several claims overstate what it currently provides.
> 2. None of the technologies expressly excluded by TASK-001 §3 appear in the source, configuration, or declared dependencies.
> 3. No ARCHITECTURE.md §6 integration boundary or speculative future abstraction appears.
> 4. Python 3.12 is declared through `requires-python = ">=3.12,<3.13"`, but the documented test command does not enforce that constraint.
> 5. Both tests are real, although narrow. Removing `__version__` failed the first test; removing the required product wording failed the second.
> 6. All three commits explicitly identify TASK-001 as their authority.
> 7. Unsupported behavioral claims exist, as detailed below.
>
> `CODEX-PR003-01`
>
> File and line: `pyproject.toml:9-14`
>
> The PR adds two third-party dependencies: pytest as an optional development dependency and hatchling as a build dependency. TASK-001 §1 requires the implementation to have "no external dependencies" and provides no exception for development or build tooling. Neither package is among the specific exclusions in §3, but both still depart from the broader requirement in §1.
>
> `CODEX-PR003-02`
>
> File and line: `src/radhanite/__init__.py:3-6`
>
> The package docstring states in the present tense that Radhanite accepts task inputs, selects a strategy, allocates expenditure, evaluates outcomes, and decides whether further expenditure is justified. The package exports only `__version__`; none of that behavior exists in this PR. This is an unsupported behavioral claim concerning the pipeline defined by TASK-001 §2. The text should be explicitly framed as the intended product behavior until the implementation exists.
>
> `CODEX-PR003-03`
>
> File and line: `docs/pr_explanations/PR-003_TASK-001_EXPLANATION.md:45-46,75-77,101-108`
>
> The explanation claims that the project refuses Python versions outside 3.12 and that a reviewer can run the tests with one command and no installation step. Neither claim holds for the documented `python -m pytest -q` workflow:
>
> - The unchanged tests passed under Python 3.13 and Python 3.14 because `requires-python` is package-installation metadata; it does not constrain direct source-tree test execution.
> - A clean Python 3.12 environment failed with `No module named pytest`, so an installation step or pre-existing pytest installation is required.
>
> This overstates compliance with TASK-001 §6.4 and violates the review requirement that claims about behavior be supported by the implementation.
>
> Rejected — TASK-001 §1's no-external-dependencies requirement is departed from by `pytest` and `hatchling`.

## 3. Outcome

**Rejected.**

Per §7.2, rejected work is fixed or removed — it is not merged with a note. All
three findings were accepted without dispute and corrected. None was disputed.

Finding `CODEX-PR003-01` turned on a genuine ambiguity in the specification the
implementing agent had itself written: TASK-001 §1 says "no external
dependencies" with no exemption for tooling. The implementing agent had assumed
testing and build tools were exempt. The specification does not say that, so the
dependencies were removed rather than the specification reinterpreted.

## 4. Corrections

| Finding | Correction commit | What changed |
|---|---|---|
| `CODEX-PR003-01` | `01817a9` | Removed `pytest` and `hatchling`. Tests rewritten against the standard library's `unittest`; `[build-system]` and all dependencies dropped from `pyproject.toml`; package moved from `src/radhanite/` to `radhanite/`, the src layout existing only to force an install step that no longer happens. |
| `CODEX-PR003-02` | `f554191` | Docstring reframed as intended behaviour, opening with an explicit statement that none of it is implemented and that the package exports only its version. |
| `CODEX-PR003-03` | `024e60e` | Both false claims made true rather than deleted. A third test asserts the runtime is 3.12, verified to FAIL on 3.14; with `pytest` gone, no install step remains, verified on a bare 3.12 interpreter that cannot import pytest. |

The full history of any finding is recoverable with:

```
git log --grep=CODEX-PR003
```

### Verification after correction

```
$ python --version
Python 3.12.13
$ python -m unittest discover
...
Ran 3 tests in 0.000s
OK
```

Wrong runtime is now refused:

```
$ python3 --version
Python 3.14.3
$ python3 -m unittest discover
TASK-001 §6.4 requires Python 3.12; running 3.14.3
FAILED (failures=1)
```

No install step, on an interpreter with nothing installed:

```
$ python3.12 -c "import pytest"
ModuleNotFoundError: No module named 'pytest'
$ python3.12 -m unittest discover
Ran 3 tests in 0.000s
OK
```
