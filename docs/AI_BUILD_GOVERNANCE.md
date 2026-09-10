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
(OpenRouter, Arc/USDC, Hedera, x402, The Graph, and the deprioritized Privy).
Anticipating them in code is a
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

### 2.2 External dependencies

> **A task may introduce an external dependency only where its own
> specification says so.**

TASK-001 §1 requires the implementation to have **no external dependencies**,
and that requirement was enforced strictly — PR #3 was rejected for adding a
test runner and a build backend. That constraint belongs to TASK-001 and does
not bind the project permanently.

The integrations that follow cannot be built without dependencies. A task may
introduce them, subject to all four of:

1. the dependency is **necessary** for the integration that task authorizes;
2. it is **named or justified in that task's specification**, not decided during
   implementation;
3. the **minimum practical set** is used;
4. it is **disclosed in the pull request explanation**.

**This is not general authorization to add dependencies.** A dependency that
seems useful, or that would make something more convenient, is not covered. If
one is needed and the task specification does not name it, the specification is
wrong and the product owner amends it — the implementing agent does not decide
the question by installing something.

Each integration task enumerates its own. TASK-002 authorizes what OpenRouter
requires and nothing else; TASK-003 what Privy requires; TASK-005 what Arc
requires; TASK-004 what the verified x402 tooling requires.

## 3. Change-authorization rule

> **Every committed change must map to an authorized task, a prerequisite, a
> governance amendment, a documented review correction, or — narrowly, and
> under §3.2 — public communication material.**

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
- a **correction** commit references the review finding it resolves;
- a **communication** commit references §3.2, the narrowest authority, and is
  bound by every constraint stated there.

### 3.1 Referencing a review finding

A correction commit must be traceable to the specific finding that caused it.
The record lives in the commit history; no separate issue tracker is used.

Each finding in a review is given a stable identifier:

```
<REVIEWER>-PR<pr number>-<finding number>
```

for example `CODEX-PR003-01`, numbered in the order the review lists them. The
identifier is assigned when the review is recorded and never reused.

The commit that resolves it takes this form:

```
Correction: <what was wrong, in one line>

Codex review finding CODEX-PR003-01 on PR #3.
<what changed, and why it resolves the finding>

Authority: documented review correction
```

The finding's full history is then recoverable with a single command:

```
git log --grep=CODEX-PR003
```

One finding, one identifier, one or more commits referencing it. A correction
that names no finding is not a correction — it is an unauthorized change.

A committed change that can be traced to none of these four authorities should
not exist. If work turns out to be unauthorized, it is removed rather than
retroactively justified.

Commits follow the hackathon requirements in
[`HACKATHON_RULES.md`](HACKATHON_RULES.md): frequent, meaningful, and small
enough to review.

### 3.2 Public communication material

> **A fifth authority, and the narrowest one: material whose purpose is to
> describe this repository to people outside it.**

A progress page, a demonstration write-up, or a submission summary is none of
the four things above. It implements no task, establishes no prerequisite,
amends no governance, and corrects no finding — it only *describes*. Before this
amendment such material had no authority it could honestly claim, and §3 covers
"all committed repository content", so it could not be committed at all.

Material committed under this authority must satisfy **all** of the following.

1. **Every factual claim is true of a named commit**, and the material states
   which commit and on what date. A reader who finds the repository has moved on
   must be able to see that the material is the stale side.
2. **[`ARCHITECTURE.md`](ARCHITECTURE.md) §6 applies in full**, and items 8
   through 12 with particular force. Simulated values are not USDC, declared
   fixtures are not measurements, testnet value is not production value, a payee
   is not inferred, and no claim is made about work Radhanite has not done.
3. **It introduces no product, architecture, or implementation decision.** It
   describes documents that already exist. Where it and an authoritative
   document disagree, the authoritative document is right and the material is a
   defect.
4. **Describing an integration does not authorize it.** Unauthorized work named
   in such material must be visibly marked as unauthorized, in the material
   itself and not only in a document the reader will not open.
5. **Staleness is a defect, and correcting it is a §3.2 commit.** When a change
   invalidates a claim, the same pull request corrects the claim or its
   provenance line.

**What this authority does not permit.** It is not a route for shipping code,
configuration, or dependencies under a documentation heading. Where such
material needs a build step, a framework, or a runtime, that need is its own
task and gets one. Static files and the minimum configuration required to serve
them are the whole of it.

The reason for the constraint is the obvious one. A page written for an
audience is where a project is most tempted to describe what it wishes it had
built, and this repository has spent more effort than anything else on not doing
that.

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

### 4.4 Attribution

> **The pull request description must name every party that contributed and the
> role each held.**

Radhanite is built by AI agents under human authorization, and `§1.4` separates
implementation, review and merge into three distinct parties. A pull request
that does not say which party did what leaves that separation unverifiable by
anyone reading it.

At minimum, name:

- the **human product owner**, who authorized the work and holds merge authority;
- the **implementation agent**, and what it authored;
- the **review agent**, and — as a pointer to the review record per `§7.4`, never
  as a restated outcome — its review status.

Name the review agent **even when it has not reviewed the pull request**. An
absent row reads as there being no reviewer at all, which is a stronger and less
honest claim than an empty one.

This is a requirement, not a courtesy. It is written down because it was carried
by habit for six pull requests instead, and habit failed: PR #7 — a pull request
whose own purpose was fixing a stale claim about the review agent — shipped with
the review agent omitted from it entirely. Nothing required the attribution, so
restructuring the description silently dropped it.

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

### 7.4 Recording a review is one step, not several

> **A review is recorded everywhere at once, or it is not recorded.**

Recording a review has three parts, and they are a single action:

1. the review record in `docs/reviews/PR-<NNN>_CODEX_REVIEW.md` — prompt,
   findings verbatim, outcome, corrections;
2. its row in `docs/reviews/README.md`;
3. **every claim about review status in the pull request itself.**

None may be left for later. A review recorded in two of the three places has
produced a repository that contradicts itself, which is worse than one that had
not been reviewed at all — a reader cannot tell which statement to believe.

#### Why this rule exists

It was written after the failure it prevents. Pull request #6 was reviewed
twice, rejected twice, and ten findings were corrected — while its own
description still read *"Codex: has not yet reviewed"* throughout. The record in
`docs/reviews/` was accurate; the pull request was months of process away from
it, and a reader would have seen the false claim first.

That was the fourth instance of the same defect: a change made in one place and
a claim about it left stale in another. Two were caught by review
(`CODEX-PR003-04`, `CODEX-PR006-09`), one by the implementing agent, and one by
the product owner reading the pull request.

#### Prefer pointing over repeating

The durable fix for a claim that goes stale is to stop making it twice. Where a
pull request needs to state review status, prefer a reference to the review
record over a restatement of its contents. A summary that must be kept in step
is a summary that will eventually fall out of step.

Where a pull request and a review record disagree, **the review record is
correct**, on the same reasoning as §4.3: the record is the primary artifact and
the description is a convenience.

### 7.5 Corrections are reviewed too

> **A pull request whose findings have been corrected is not finished. The
> corrections are themselves reviewed before merge.**

A review examines the code as it stood when the review ran. Corrections written
afterwards have been examined by nobody but the agent that wrote them — the same
agent whose work the review just faulted.

#### Why this rule exists

Because corrections are where the defects have been:

- **PR #3.** The second pass found `CODEX-PR003-04`: stale counts introduced *by*
  a correction, in the same document the correction had just edited.
- **PR #6.** The second pass found `CODEX-PR006-03` only half fixed — negation
  still bypassed the exact context, and the context itself was a mutable object
  any caller could strip — plus three findings the first pass had not reached.

In both cases the implementing agent had reported the findings as resolved, in
good faith, and was wrong.

#### How the cycle ends

Reviewing corrections produces corrections, so the loop needs a floor:

1. A review returning **no findings** ends it. The pull request is ready.
2. The **human product owner may merge at any point** — `§1.1` is unconditional
   and this rule does not qualify it.

Where the product owner merges with corrections unreviewed, that is recorded in
the review record, naming the commits that went in unexamined. The decision is
theirs; the record simply does not pretend otherwise.

#### Scope

This applies to corrections of substance — code, tests, and claims about
behaviour. A correction that only fixes a typo does not restart the cycle. If it
is unclear which kind a correction is, it is the reviewable kind.

## 8. Amending this document

This document may be changed only by the human product owner. No AI agent may
relax its own constraints, and an agent asked to edit this file states plainly
that the change originated from the product owner.
