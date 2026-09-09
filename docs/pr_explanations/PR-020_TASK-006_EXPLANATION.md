# PR-020 — TASK-006 is authorized

**Pull request:** #20
**Authority:** authorization of TASK-006 by the human product owner
**Author:** Claude Code, under human product owner authorization

---

## 1. Purpose of this PR

To record one decision: **the human product owner has authorized TASK-006.**

Work in this repository becomes buildable only when the product owner says so,
and that decision is worth exactly as much as the record of it. This pull
request is that record.

**It contains no code**, and it changes nothing about what TASK-006 says. It
changes what may now be done about it.

## 2. What changed

| File | What it is |
|---|---|
| `tasks/TASK-006_...md` | Its status header — the only edit to the specification |
| `tasks/BACKLOG.md` | `BL-13` becomes the file's one authorized entry |
| `docs/ARCHITECTURE.md` | Two places that said the work was not authorized |
| `README.md` | The repository-status row for capability acquisition |
| `docs/pr_explanations/PR-020_...md` | This document |

Five files. No `.py` file, no dependency, no configuration. The test count is
unchanged at 242.

## 3. Why the change was needed

This repository draws a hard line between **describing** work and **permitting**
it. A task file states what would be built; only the product owner decides that
it may be. The rule exists because an AI agent that can authorize its own work
has no meaningful supervision at all.

TASK-006 was written, then reviewed, then had its three blocking questions
answered — and through all of that it stayed marked *not authorized*, which was
accurate. The product owner has now authorized it, so the documents must say so.
A repository whose files still say "not authorized" while work proceeds is
lying, in the direction that matters most.

## 4. How this worked before

Every document said the same thing, consistently: TASK-006 is specified, its
decisions are settled, and **it may not be built**.

## 5. How it works after

TASK-006 reads **AUTHORIZED for implementation**, dated, and attributed to the
product owner. `BL-13` is now the only authorized entry in the backlog.

Three limits are stated in the same breath, because an authorization without
edges is an invitation:

- **It reaches TASK-006 §2 and nothing further.** The selection rule, and that
  alone.
- **TASK-006 §3 is untouched.** No provider discovery, no payment execution, no
  task-state layer, no candidate generation. Those remain separate, unauthorized
  concerns.
- **Every integration is still unauthorized.** TASK-002 through TASK-005 are
  unaffected, and so is the demonstration in `PREREQ-001` §6.

## 6. What goes into the system

Nothing. This is a status change with no runtime, no inputs, and no state.

## 7. What the system decides

Nothing. The only decision here was a human one, already taken.

Worth being precise: **the authorization is the product owner's word, not this
file.** The commit records it so that anyone reading the repository later can
see when it happened and what it covered. If the record and the decision ever
disagreed, the decision would be the real thing and the record would be a bug.

## 8. What comes out

A repository in which the authorized work and the built work are two different
sets, and both are stated. **TASK-006 is authorized and not implemented**, and
`ARCHITECTURE.md` §2.2.1 still describes what actually runs today.

## 9. How it can fail

The failure mode is an authorization that quietly widens. TASK-006 sits next to
a demonstration involving several external services, and "we authorized
capability selection" could drift into "we authorized buying things."

So the boundaries in §5 are written into the documents rather than left to
memory, and TASK-006's own §3 and §10 already refuse the adjacent work by name.

## 10. Tests run and their results

```
$ python3.12 -m unittest discover -q
Ran 242 tests in 0.10s
OK
```

**242 passing, unchanged.** Nothing here could affect them; the suite was run to
confirm the repository is green before implementation starts against it.

## 11. Assumptions made

- **The authorization is unconditional within TASK-006 §2.** No further sign-off
  is expected before implementation begins.
- **It does not extend to anything TASK-006 excludes.** Where that is
  ambiguous, the narrower reading is taken and the question goes back to the
  product owner.

## 12. Known limitations

- **Authorizing is not building.** No line of TASK-006 exists as code. Anyone
  reading only this pull request should not conclude otherwise.
- **The specification is unreviewed since its decisions were frozen.** Codex
  reviewed the original specification on PR #19; the commit that resolved the
  three decisions has not been independently reviewed.

## 13. Explicitly out of scope

No implementation. No integration, no provider, no payment, no wallet, no
candidate generation, no task-state layer. No change to any other task's
authorization status.

## 14. Deferred to future tasks

Implementation of TASK-006, which begins after this. It is intended to arrive as
a sequence of small pull requests — the candidate model, then eligibility, then
ranking and tie-breaking, then the termination safeguards, then the
demonstration that TASK-001's scenarios still reproduce — each with its own
explanation and its own independent review.

## 15. How to explain this to a judge

> In this project, writing down what to build and being allowed to build it are
> two separate events, and both are in the git history.
>
> We specified how the system should choose between things it could buy. We had
> it independently reviewed. We found three questions it couldn't answer —
> including one where the loop would never terminate — and answered them.
>
> This commit is the moment a human said: *now you may build it.* It's four
> lines and no code, and it's a separate commit on purpose, because the whole
> point is that the AI didn't get to make that call.
