# ETHOnline Rules and Constraints

**Status:** Binding on all work in this repository
**Event:** ETHOnline 2026

These are the competition constraints Radhanite is built under. They are
recorded here so that every contributor — human or AI — builds in compliance
without having to re-derive the rules.

---

## 1. The rules

### 1.1 The project starts from scratch
No pre-existing codebase, no work carried over from before the hackathon. The
repository's history begins at the hackathon and shows the project being built.

**How we comply:** this repository was initialized empty. Its first commit is
governance and planning scaffolding, not inherited product code.

### 1.2 Version control is required
All work is tracked in git.

**How we comply:** every change to the repository lands as a commit. Nothing is
delivered outside version control.

### 1.3 Commits must be frequent and meaningful
Progress must be visible in the history.

**How we comply:** each authorized unit of work is committed when it is coherent
and self-describing. Commit messages explain what changed and why, in plain
English, and reference the authorized task they belong to.

### 1.4 Avoid a tiny number of huge commits
A history of two enormous commits does not demonstrate that the project was
built during the event.

**How we comply:** work is broken into small, reviewable commits. A commit that
mixes unrelated concerns is split. Large one-shot dumps of generated code are
treated as a process failure, not a shortcut.

### 1.5 The repository must remain public
Visibility must not be restricted at any point.

**How we comply:** the repository is public. No secrets, credentials, or private
data are ever committed — the repository being public is assumed at all times.

### 1.6 The project must be open source
The work must be released under an open source license.

**How we comply:** the repository is licensed under the MIT License, an
OSI-approved licence, from its first push. All code and documentation in the
repository is written with public release in mind.

## 2. Practical consequences for AI-assisted building

These rules interact directly with how AI agents are used here.

| Rule | Consequence for AI-built work |
|---|---|
| From scratch | No importing generated scaffolding from prior projects. |
| Frequent meaningful commits | AI output is committed in reviewable increments, not in one large drop. |
| Avoid huge commits | An agent that produces a large change must have it split before merge. |
| Public repository | Nothing sensitive is ever placed in prompts, code, or docs. |
| Open source | All AI-produced content must be licensable and safe to publish. |

The governance process that enforces this is in
[`AI_BUILD_GOVERNANCE.md`](AI_BUILD_GOVERNANCE.md).

## 3. Unverified event details

The following are intentionally left blank rather than guessed. They must be
filled in by the human product owner from the official ETHOnline sources:

- Submission deadline: _TBD_
- Required submission artifacts: _TBD_
- Prize tracks being targeted: _TBD_
- Track-specific technical requirements: _TBD_

Nothing in this repository should assume a value for these until confirmed.
