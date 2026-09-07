# PR-003 — The empty workshop

**Pull request:** #3
**Authority:** TASK-001 (authorized task)
**Author:** Claude Code, under human product owner authorization

---

## 1. Purpose of this PR

To set up the workshop before building anything in it.

This is the first pull request containing actual software rather than documents.
It contains no part of Radhanite itself. What it adds is the bench the rest of
the work will be built on: a place for code to live, and a command that checks
whether the code works.

## 2. What changed

Four new files:

| File | What it is |
|---|---|
| `pyproject.toml` | The project's identity card — its name, version, and which version of Python it needs |
| `src/radhanite/__init__.py` | The empty container the real code will go into |
| `tests/test_package.py` | Two checks that confirm the setup works |
| `.gitignore` | A list of files that should never be saved into the project's history |

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
whether they all passed. Today it finds two checks and both pass.

Those two checks are deliberately not empty. One confirms the project can
actually be loaded and knows its own version number. The other confirms the
project's written description of itself is present and says what it should. A
test that always passes regardless of the state of the code proves nothing, and
would have been worse than having no test.

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
  them behave differently. The project refuses any version outside 3.12, so this
  fails loudly rather than silently.
- **The checks could be meaningless.** A test that passes no matter what is
  worse than useless, because it creates false confidence. Both tests here were
  written to fail if the setup is genuinely broken.
- **The setup could work on this machine only.** It has not been run anywhere
  else, so that is an open risk rather than a solved problem.

## 10. Tests run, and their results

The full test command was run, and everything passed:

```
$ python --version
Python 3.12.13

$ python -m pytest -q
..                                                          [100%]
2 passed in 0.01s
```

Both tests are new in this pull request. There were no tests before it.

## 11. Assumptions made

- That "Python 3.12" in the specification means the project should both target
  and be tested on 3.12, rather than merely tolerate it. The project is pinned
  to 3.12 and refuses later versions, and 3.12 was installed on the build
  machine for this purpose.
- That tests should run without an installation step, so that a reviewer or
  judge can check the work with one command.
- That the standard Python testing tool is the right choice, rather than
  something written by hand.

## 12. Known limitations

- Nothing in this pull request does anything useful on its own.
- The exact versions of the testing tools are not pinned, so a future install
  could pick up newer ones and behave differently.
- The setup has only ever been run on one machine.

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

Radhanite's first task is finished only when the project's own tests pass, so
the very first thing built was the ability to run tests and see the result.
There are two of them and they both pass, and neither is the kind of test that
passes no matter what.

The reason to do this separately, rather than folding it into the first real
piece of code, is that it keeps blame clear. When something breaks later, it
will be obvious whether the workshop or the work is at fault.

---

**This document explains; it does not govern.** The product definition,
architecture document, task specification, and the code and its tests are the
authoritative record. Where this explanation and the repository disagree, the
repository is correct.
