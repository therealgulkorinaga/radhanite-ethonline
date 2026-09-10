# PR-024 — A page that describes the project, and the rule that lets it exist

**Pull request:** #24
**Authority:** governance amendment (`AI_BUILD_GOVERNANCE.md` §3.2), authorized by the human product owner
**Author:** Claude Code, under human product owner authorization

---

## 1. Purpose of this PR

Two things, and the second is why the first is allowed.

**A public progress page** for ETHOnline, at `site/index.html`, deployable to
Vercel with no build step.

**A new authority in the governance**, §3.2, covering material whose only job is
to describe this repository to people outside it. Without it the page could not
honestly be committed at all.

**No product code changed.** 423 tests, unchanged.

## 2. What changed

| File | What it is |
|---|---|
| `docs/AI_BUILD_GOVERNANCE.md` | **§3.2** — the new authority, and its constraints |
| `site/index.html` | The page. One file, no build, no dependencies |
| `site/README.md` | What the page may say, and how to deploy it |
| `vercel.json` | Points Vercel at `site/`, no build command |
| `README.md` | One line for `site/` in the repository layout |
| `docs/reviews/PR-024_CODEX_REVIEW.md` | The review prompt, **committed before the review runs** |
| `docs/reviews/README.md` | Its row in the review index |
| `docs/pr_explanations/PR-024_...md` | This document |

Eight files. No `.py` file. **No dependency** — the project still has none, and
the page has none either.

## 3. Why the change was needed

The page was asked for. The rule had to come first.

`§3` says every committed change maps to **an authorized task, a prerequisite, a
governance amendment, or a documented review correction** — and it says so about
*"all committed repository content, not only code"*, naming configuration and
"any other committed artifact" explicitly.

A progress page is none of those four. It implements no task, establishes no
prerequisite, corrects no finding. Under the rule as written, it could not be
committed — and the wrong response would have been to file it under
"documentation" and hope nobody checked.

So the gap gets named and closed, narrowly, in the same pull request as the
thing that revealed it.

## 4. How this worked before

There was no public-facing material in the repository at all, and no authority
under which any could be added.

## 5. How it works after

### The rule

**§3.2** admits a fifth authority and immediately constrains it. Material
committed under it must:

1. be **true of a named commit**, and say which one and when;
2. satisfy **`ARCHITECTURE.md` §6 in full** — simulated values are not USDC,
   declared fixtures are not measurements, testnet value is not production
   value, no claim about work Radhanite has not done;
3. **introduce no product or architecture decision** — where it disagrees with
   an authoritative document, it is the defect;
4. **authorize nothing by describing it** — unauthorized work must be visibly
   marked as unauthorized *in the material itself*;
5. treat **staleness as a defect**, corrected in the same pull request as the
   change that caused it.

And it is explicitly **not** a route for shipping code, dependencies or a build
step under a documentation heading. Static files and the minimum configuration
to serve them, and nothing else.

### The page

Eight cards, scrolled, one idea each:

| | |
|---|---|
| — | Rails answer *how* a machine pays. We answer *whether it should* |
| 01 | Every purchase is one sum — 50¢ buys 50%→80% on a $20 outcome, **$5.50 net** |
| 02 | Six conditions, three of which aren't about money |
| 03 | **A run that buys nothing is a correct run** |
| 04 | What the engine does today |
| 05 | What doesn't exist |
| 06 | Built by agents that can't approve themselves |
| 07 | Where it's going, and the three tracks — all marked *not authorized* |

Cards 04 and 05 face each other deliberately. The project's strongest claim to a
judge is not the feature list; it is that the feature list is followed
immediately by an equally long list of what is missing.

## 6. What goes into the system

Nothing. The page is static, takes no input, stores nothing, and calls nothing
except Google Fonts for two typefaces.

## 7. What the system decides

Nothing. §3.2 says so outright: material under this authority describes
decisions, it does not make them.

## 8. What comes out

A page at `site/index.html`, and a deployable repository. Every figure on it —
423 tests, 23 merged pull requests, 47 review findings, zero dependencies — was
read from the repository rather than remembered, and the page names the commit
it read them from.

## 9. How it can fail

**By going stale.** The figures describe a commit. The repository will move.
That is the failure mode this page is most exposed to, and the reason it carries
a visible provenance line rather than an undated claim: a reader who checks can
see which side is behind.

**By overclaiming.** A page written for judges is exactly where a project
describes what it wishes it had built. Every integration on it is marked *not
authorized*; the probabilities are labelled declared fixtures; and there is no
sentence implying that any value has moved on any chain, because none has.

## 10. Tests run and their results

```
$ python3.12 -m unittest discover -q
Ran 423 tests in 0.14s
OK
```

**423 passing, unchanged.** Nothing here could affect them; the suite was run to
confirm the repository is green.

The page itself has no tests, and that is worth stating plainly rather than
leaving as an omission. Its correctness is the accuracy of its claims, which is
checked by reading them against the repository — the review prompt in
`docs/reviews/PR-024_CODEX_REVIEW.md` asks a reviewer to do exactly that,
figure by figure.

## 11. Assumptions made

- **The product owner authorizes §3.2 by merging this.** The amendment is
  written here because the page needs it; the authority to add it is theirs, and
  merging is how it is given.
- **Vercel is the target.** `vercel.json` sets `outputDirectory` to `site` with
  no build command, so an import needs no dashboard configuration.
- **The page is a description, not a source of truth.** It is committed under
  the authority that says so.

## 12. Known limitations

- **The page duplicates facts that live elsewhere**, which is what makes
  staleness possible. §3.2 requires correcting it alongside the change that
  invalidates it, but nothing enforces that automatically.
- **No test asserts the page's figures match the repository.** That could be
  built; it is not built here, and this PR does not pretend otherwise.
- **The amendment widens what may be committed.** Narrowly and with five
  conditions, but it is still a widening, and it is the reviewer's job to say
  whether the conditions are tight enough.

## 13. Explicitly out of scope

No product code, no tests, no dependency, no build step, no framework. No
integration became authorized — the page names three and marks all three
unauthorized. No task changed status. `TASK-006`'s remaining work is untouched.

## 14. Deferred to future tasks

The remaining steps of TASK-006. Whether the page's figures should be checked by
a test rather than by a reader is a real question and is not answered here.

## 15. How to explain this to a judge

> We wanted a page describing the project. Our own rules said every committed
> file has to trace back to an authorized piece of work — and a landing page
> doesn't.
>
> So rather than file it under "documentation" and look away, we wrote the rule
> that covers it, and made that rule strict: anything we publish about ourselves
> has to be true of a specific commit, has to say which one, and has to mark
> unauthorized work as unauthorized on the page itself.
>
> Then we wrote the page under that rule. The section listing what we haven't
> built is exactly as long as the one listing what we have.
