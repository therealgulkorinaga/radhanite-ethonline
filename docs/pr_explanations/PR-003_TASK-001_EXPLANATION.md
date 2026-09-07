# PR-003 — The empty workshop

**Pull request:** #3
**Authority:** TASK-001 (authorized task)
**Author:** Claude Code, under human product owner authorization

---

> **A note on numbering.** Files and finding identifiers in this repository are
> named for the **GitHub pull request number**, never for a position in the build
> plan. TASK-001 was planned as twelve build steps, and its first step happened
> to land as pull request #3 — a coincidence, not a scheme. Governance pull
> requests #4 and #5 then landed in between, so from that point the two
> numberings diverge: the second build step is pull request **#6**, not #4.
>
> GitHub pull request numbers are permanent, assigned at creation and shared with
> the issue counter, so they cannot be reassigned. When the build plan and the
> record disagreed, the plan moved. Reading the pull request numbers as build
> steps will mislead you; read them as what they are.

## 1. Purpose of this PR

To set up the workshop before building anything in it.

This is the first pull request containing actual software rather than documents.
It contains no part of Radhanite itself. What it adds is the bench the rest of
the work will be built on: a place for code to live, and a command that checks
whether the code works.

## 2. What changed

Six new files:

| File | What it is |
|---|---|
| `pyproject.toml` | The project's identity card — its name, version, and which version of Python it needs |
| `radhanite/__init__.py` | The empty container the real code will go into |
| `tests/test_package.py` | Three checks that confirm the setup works |
| `tests/__init__.py` | Lets the test command find the tests with no configuration |
| `.gitignore` | A list of files that should never be saved into the project's history |
| `docs/pr_explanations/PR-003_...md` | This document |

This pull request was revised after an independent review rejected its first
version. Three problems were found and fixed; the record is in
`docs/reviews/PR-003_CODEX_REVIEW.md`.

## 3. Why the change was needed

TASK-001 is only finished when **the repository's tests pass**. That sentence is
meaningless until there is a way to run tests at all.

This is also the honest order to work in. If the workshop is assembled at the
same time as the first real component, and something breaks, there is no way to
tell which of the two is at fault.

## 4. How this worked before

The repository contained only documents. There was no code, no way to run
anything, and no way to check whether anything worked.

## 5. How it works after

There is now a single command that runs every check in the project and reports
whether they all passed. Today it finds three checks and all three pass.

Those three checks are deliberately not empty. One confirms the project can
actually be loaded and knows its own version number. The second confirms the
project's written description of itself is present and says what it should. The
third refuses to run on the wrong version of Python. A test that always passes
regardless of the state of the code proves nothing, and would have been worse
than having no test.

**The project uses nothing but Python itself.** No outside software is needed to
run it or to check it, because the task specification requires that and makes no
exception for testing tools. This is why the checks are written against Python's
own built-in testing facility rather than the more common third-party one, and
why there is nothing to install before running them.

The `.gitignore` file deserves one note. Building software produces disposable
by-products — temporary files, a private copy of Python and its add-ons. These
should never be saved into the project's permanent record, and this file lists
them so they are skipped. It does **not** exclude the plain-English explanation
documents; those are meant to be public and are committed deliberately.

## 6. What goes into the system

Nothing. There is no system yet, and nothing to feed it.

## 7. What the system decides

Nothing. No part of Radhanite's economic reasoning exists in this pull request.

## 8. What comes out

Only the result of running the checks: a count of how many passed and how many
failed.

## 9. How it can fail

- **The checks could be run with the wrong version of Python**, which could make
  them behave differently. One of the three checks fails outright on any version
  other than 3.12, so this is loud rather than silent. This was verified by
  running the tests on a newer Python and confirming they fail.
- **The checks could be meaningless.** A test that passes no matter what is
  worse than useless, because it creates false confidence. All three tests
  here were written to fail if the setup is genuinely broken.
- **The setup could work on this machine only.** It has not been run anywhere
  else, so that is an open risk rather than a solved problem.

## 10. Tests run, and their results

The full test command was run on Python 3.12, and everything passed:

```
$ python --version
Python 3.12.13

$ python -m unittest discover
...
Ran 3 tests in 0.000s
OK
```

Two further checks were run, because an earlier version of this document made
claims that turned out to be false:

**That nothing needs installing.** The tests were run with a completely bare
Python 3.12 that has no extra software at all. All three passed.

```
$ python3.12 -c "import pytest"
ModuleNotFoundError: No module named 'pytest'

$ python3.12 -m unittest discover
Ran 3 tests in 0.000s
OK
```

**That the wrong version of Python is actually refused.** The tests were run on
Python 3.14 and failed, as they should.

```
$ python3 -m unittest discover
TASK-001 §6.4 requires Python 3.12; running 3.14.3
FAILED (failures=1)
```

All three tests are new in this pull request. There were no tests before it.

## 11. Assumptions made

- That "no external dependencies" in the task specification means exactly that,
  including testing and packaging tools. An earlier version of this pull request
  assumed testing tools were exempt; a reviewer disagreed, and the specification
  does not say they are.
- That "Python 3.12" means the project should refuse to run on anything else,
  rather than merely stating a preference.
- That a reviewer or judge should be able to check the work with one command and
  no setup.

## 12. Known limitations

- Nothing in this pull request does anything useful on its own.
- The setup has only ever been run on one machine, on macOS.
- Python's built-in testing facility is less convenient than the common
  third-party alternative. That cost was accepted in order to depend on nothing.
- The version check enforces 3.12 when the tests are run. It cannot stop someone
  importing the package under a different version without running them.

## 13. Functionality explicitly left out of scope

All of Radhanite. No task, no budget, no strategies, no decisions, no run
records. Also absent, as required by TASK-001 §3: any connection to real AI
models, any wallet or payment component, any user interface, and any form of
machine learning.

## 14. Deferred to future tasks

The rest of TASK-001, which will arrive as a sequence of small pull requests:
the way money is represented, the five things a task is made of, the rule for
deciding whether to spend more, the strategies, the simulator, the loop itself,
the run record, and a command to run one task end to end.

## 15. How to explain this to a judge

This pull request is the empty workbench.

It was rejected on its first review and fixed. That is worth saying out loud,
because it is the process working rather than failing.

Radhanite's first task is finished only when the project's own tests pass, so
the very first thing built was the ability to run tests and see the result.
There are three of them and they all pass, and none is the kind of test that
passes no matter what.

The reason to do this separately, rather than folding it into the first real
piece of code, is that it keeps blame clear. When something breaks later, it
will be obvious whether the workshop or the work is at fault.

The project also depends on no outside software whatsoever — only Python itself.
That was not a preference; the specification demanded it, a reviewer noticed it
had been broken, and it was corrected.

---

**This document explains; it does not govern.** The product definition,
architecture document, task specification, and the code and its tests are the
authoritative record. Where this explanation and the repository disagree, the
repository is correct.
