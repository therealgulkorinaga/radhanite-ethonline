# AI Build Governance

**Status:** Binding on all contributors, human and AI
**Owner:** Human product owner

Radhanite is built primarily by AI agents. This document defines who may do
what, and how work is authorized, reviewed, and merged. It exists so that the
repository's history is a record of deliberate decisions rather than of
accumulated agent output.

---

## 1. Roles

### 1.1 Human product owner
The only role with authority to:

- define and change the product definition,
- authorize a task for implementation,
- expand or reduce scope,
- **merge any work into the main branch.**

No AI agent may merge. No AI agent may authorize its own work.

### 1.2 Claude Code — implementation agent
Builds **only** tasks that have been explicitly authorized by the product owner
in a task file under `tasks/`.

Claude Code may not:

- implement anything outside the authorized task's stated scope,
- implement anything from `tasks/BACKLOG.md`,
- add dependencies or integrations that the authorized task does not name,
- merge its own work,
- decide that scope should be expanded because it seems useful.

When Claude Code believes the task specification is wrong, incomplete, or
harmful, it says so plainly and waits for the product owner's decision. It does
not fix the specification by building something different.

### 1.3 Codex — independent review agent
Reviews implementations **against the specification**, independently of the
agent that wrote them.

Codex's review answers:

1. Does the implementation do what the authorized task specifies?
2. Does it do anything the task does **not** authorize?
3. Does it violate the boundaries in [`ARCHITECTURE.md`](ARCHITECTURE.md)?
4. Are its claims about behavior actually true?

Codex reviews; it does not merge, and it does not silently rewrite scope either.

### 1.4 Separation of duties
Implementation, review, and merge are three distinct roles held by three
distinct parties. This separation is the core control and is not optional for
convenience or speed.

## 2. The authorization rule

> **Future scope must not be silently implemented.**

If a capability is not described in a currently authorized task file, it must
not appear in the repository — not as code, not as a dependency, not as a
configuration stub, not as an abstraction "ready for later."

This applies with full force to the integrations named in `ARCHITECTURE.md`
(OpenRouter, Privy, Arc/USDC, Hedera, x402). Anticipating them in code is a
violation even when no external call is made.

Backlog entries are **not** authorization. `tasks/BACKLOG.md` records ideas that
have been deliberately *not* approved.

### 2.1 Narrow adjacent-document consistency exception

There is exactly one exception to the rule above, and it is deliberately narrow.

When an explicitly authorized product or architecture decision would otherwise
leave another repository document **materially inaccurate, contradictory, or
misleading**, the implementation agent may make the minimum necessary
adjacent-document correction.

**This does not create general authority to edit out-of-scope documentation.**

Any such adjacent-document edit must:

- be **strictly necessary** to preserve repository consistency or to avoid
  misrepresentation;
- be **minimal**;
- be **explicitly disclosed** in the implementation report, naming the file and
  the reason;
- introduce **no new product, architecture, or implementation decision**.

The test is not "would this document be better?" — it is "would leaving this
document untouched make the repository contradict itself or state something
untrue?" Only the second justifies the edit.

If there is any doubt, **stop and ask the human product owner.**

## 3. Change-authorization rule

> **Every committed change must map to an authorized task, a prerequisite, a
> governance amendment, or a documented review correction.**

This rule covers **all committed repository content**, not only code:

- source code and tests,
- documentation,
- preserved prompt records,
- PR explanation files,
- configuration and any other committed artifact.

Each commit message states which authority it derives from:

- a **task** commit references the authorized task (for example, `TASK-001`);
- a **prerequisite** commit references the prerequisite it establishes or
  changes (for example, `PREREQ-001`);
- a **governance** commit references the governance amendment it applies, which
  the human product owner must have authorized;
- a **correction** commit references the review finding it resolves.

A committed change that can be traced to none of these four authorities should
not exist. If work turns out to be unauthorized, it is removed rather than
retroactively justified.

Commits follow the hackathon requirements in
[`HACKATHON_RULES.md`](HACKATHON_RULES.md): frequent, meaningful, and small
enough to review.

## 4. Pull request readiness and the explanation artifact

> **Changes must be explained in plain English, in a committed document, before
> a pull request is eligible for review.**

A pull request is **ready for review** only when both of the following are
present. These are the required PR artifacts.

### 4.1 Authority mapping

Every change in the pull request maps to an authorized task, prerequisite,
governance amendment, or documented review correction, per §3, and the mapping
is stated in the pull request.

### 4.2 A committed explanation file

The pull request includes a committed, non-technical explanation file under
`docs/pr_explanations/`:

```
docs/pr_explanations/PR-001_TASK-001_EXPLANATION.md
```

The PR number, the authority it implements, and the `_EXPLANATION` suffix.

#### Purpose

The explanation exists so that the human product owner, reviewers, hackathon
judges, and future contributors can understand the change **without reading
source code**. Radhanite is built by AI agents at speed; a repository whose
changes are only legible to whoever has just read the diff is not reviewable by
anyone else.

#### Required contents

The explanation file must cover all of the following. This is the **single**
checklist for a pull request — there is no separate summary requirement
elsewhere.

1. the purpose of the PR;
2. what changed;
3. why the change was needed;
4. how the relevant system worked **before**;
5. how it works **after**;
6. important inputs, data, or state entering the system;
7. the decisions the system makes;
8. outputs or state changes;
9. failure modes;
10. tests run, and their results;
11. assumptions made;
12. known limitations;
13. functionality explicitly left out of scope;
14. anything deferred to future tasks;
15. a short closing section titled **"How to explain this to a judge"**.

#### Writing standard

The explanation is written **for a non-technical reader**. Technical terms may
be used only where genuinely necessary, and each must be explained immediately
in ordinary English. An explanation that requires the reader to already
understand the implementation has failed at its only job.

An explanation that hides a limitation is worse than no explanation. If tests
fail, or a piece was stubbed, or an assumption is load-bearing, it is stated
outright — item 10 records results honestly, including failures.

### 4.3 Status: explanatory artifact, not a source of truth

**The PR explanation is not authoritative.** The committed product definitions,
architecture documents, task specifications, code, and tests remain the only
sources of truth.

Consequently:

- **Codex reviews the implementation against those authoritative materials**,
  independently of the PR explanation.
- **Codex must not treat the PR explanation as evidence that the implementation
  is correct.** A confident, well-written explanation of behavior that the code
  does not exhibit is a defect to be caught, not a reason to approve.
- Where the explanation and the code disagree, the code is what shipped, and the
  explanation is wrong.

## 5. Prompt preservation

> **Meaningful AI prompts that cause substantive repository changes are
> preserved.**

When a prompt drives a real change to the repository, that prompt is recorded in
`prompts/`. This makes the project's provenance auditable: a reader can see not
only what the code does, but what instruction produced it.

Trivial prompts are not preserved — the point is signal, not a transcript. The
convention is described in [`prompts/README.md`](../prompts/README.md).

## 6. Working agreement for AI agents

Applies to every AI agent operating in this repository.

1. **Do the authorized task. All of it. Only it.**
2. **Do not expand scope**, even when expansion is obviously useful. Propose it
   instead; the product owner decides.
3. **Do not narrow scope silently.** If part of a task cannot be completed, do
   the rest and say exactly what was left undone and why.
4. **Ask only when it matters.** Make ordinary judgment calls; escalate only
   when different readings produce materially different work.
5. **State assumptions explicitly** rather than encoding them invisibly.
6. **Report honestly.** Never describe unverified work as verified.
7. **Never merge.**

## 7. Review readiness and review outcomes

### 7.1 Review readiness

A pull request is **not eligible for Codex review** until the required PR
artifacts in §4 are present — including the committed plain-English explanation
file. Codex review begins only once these readiness requirements are satisfied.

**A missing required artifact is a review-readiness failure, not a substantive
review outcome.** It is not a rejection, and it is not recorded as one: the
review has not started. The pull request is returned for completion, and review
begins when it is ready.

### 7.2 Substantive outcomes

Once a review has begun, it concludes with exactly one of:

- **Approved** — matches the specification, no unauthorized scope. Product owner
  may merge.
- **Approved with corrections** — merge after specific, named corrections; each
  correction is committed with a reference to the finding.
- **Rejected** — the work departs from the specification or crosses an
  architecture boundary. It is fixed or removed; it is not merged with a note.

Unauthorized scope found in review is removed, not merged and deferred.

### 7.3 Review records

> **Every review is recorded in `docs/reviews/` — the prompt and the findings
> both.**

A review that leaves no trace cannot be shown to have happened. Each reviewed
pull request gets one committed record, `docs/reviews/PR-<NNN>_CODEX_REVIEW.md`,
holding the prompt the reviewer was given, the findings it returned verbatim,
the outcome, and the correction commits that resolved each finding.

The prompt is committed **before the review is run**. A prompt recorded
afterwards can be quietly reshaped to fit the answer it received.

Findings are never summarized, softened, or deleted. A finding that was disputed
is kept, together with the reasoning that disputed it.

The record is a transcript, not a source of truth. A reviewer can be wrong, and
the record preserves what it said rather than endorsing it. See
[`docs/reviews/README.md`](reviews/README.md).

## 8. Amending this document

This document may be changed only by the human product owner. No AI agent may
relax its own constraints, and an agent asked to edit this file states plainly
that the change originated from the product owner.
