# PR-025 — The Graph takes Privy's place on the build path

**Pull request:** #25
**Authority:** product-direction decision by the human product owner, recorded per `AI_BUILD_GOVERNANCE.md` §3
**Author:** Claude Code, under human product owner authorization

---

## 1. Purpose of this PR

To record one decision the product owner made: **Privy comes off the active
integration path, and The Graph takes its place.**

**Documentation only.** No product code changed, no task became authorized, and
`TASK-006`'s logic is untouched — 423 tests, unchanged.

## 2. What changed

| File | What it is |
|---|---|
| `tasks/TASK-003_..._PRIVY.md` | Status changed; a superseded notice with the reasons. **The specification itself is unaltered** |
| `tasks/TASK-007_..._THE_GRAPH.md` | **New.** The placeholder, its premise, and three unresolved decisions |
| `docs/ARCHITECTURE.md` | §3.2 marked deprioritized; new §3.5 for The Graph; the active path in priority order |
| `tasks/BACKLOG.md` | `BL-02` deprioritized, `BL-15` added |
| `README.md` | The integration row |
| `site/index.html` | The Privy card becomes The Graph — required by §3.2 |
| `docs/AI_BUILD_GOVERNANCE.md` | The named-integration set in §2 |
| `docs/reviews/PR-025_CODEX_REVIEW.md` | The review prompt, **committed before the review runs** |
| `docs/reviews/README.md` | Its row in the index |
| `docs/pr_explanations/PR-025_...md` | This document |

Ten files. **No `.py` file. No dependency.**

## 3. Why the change was needed

The product owner's reasoning, recorded rather than left in a conversation:

1. **Circle Agent Wallets and Arc now cover the wallet and payment layer** for
   the current build. What Privy was to provide is largely provided by an
   environment already on the path.
2. **Privy would add overlap, not a distinct economic capability.** A second
   route to the same wallet-and-permissions layer is not a second thing
   Radhanite could decide to buy.
3. **Wallet authorization is not what Radhanite is differentiated on.** The
   product is deciding *whether a purchase is worth making*. Spending a
   hackathon on the part nobody is competing over is the expensive choice.

There is a shape to the replacement worth naming. Privy would have given
Radhanite an **authority it holds**. The Graph gives it a **capability it can
buy** — which is what the product definition now describes, and what the other
two integrations on the path already are.

## 4. How this worked before

Privy was the second of four integrations, with a specification and a place in
the dependency chain. The Graph appeared nowhere.

## 5. How it works after

The active path, in priority order:

| | Integration | What it contributes |
|---|---|---|
| 1 | **Hedera / x402** | A paid independent-judgement capability |
| 2 | **Circle / Arc** | The marketplace and payment environment, and research |
| 3 | **The Graph** | A paid onchain-information capability |

**Privy is not on it.** Its task is marked
`DEPRIORITIZED / SUPERSEDED FOR CURRENT ETHONLINE BUILD`, and nothing below that
notice was rewritten.

### What The Graph is, and is not

**It is not part of the decision engine.** It is one capability among the
candidates. A Graph-backed purchase would return structured onchain evidence —
wallet, protocol or entity activity — which changes what the task knows, and
therefore what the next decision is measured against.

Buying information is a purchase like any other. It has a price, it may improve
the odds, and it is not exempt from *worth more than it costs* because it
happens to be data rather than judgement.

### The line that must not move

> **The Graph must not influence ranking merely because it is The Graph.**

`TASK-006` §2.1 keeps provider and network identity outside the selection logic,
and this PR **does not touch TASK-006 at all** — verified: the file is unchanged
in the diff, as are `radhanite/` and `tests/`.

TASK-007 §3 restates the prohibition in the specific terms that would be
tempting here: no field or branch naming a provider, no tie-break a provider
earns by identity, and **no "trusted source" concept**, which is provider
preference wearing a hat. If onchain evidence deserves to win, it wins on price
and effect through `net_expected_value`, like everything else.

## 6. What goes into the system

Nothing. No runtime, no input, no state.

## 7. What the system decides

Nothing. This records a decision the product owner made; it makes none.

## 8. What comes out

A repository whose roadmap says what is actually planned, and a public page that
no longer advertises an integration that is not being built.

## 9. How it can fail

**By deleting history.** Deprioritizing work is not discovering it was wrong,
and a repository that quietly erases superseded plans cannot be trusted about
the ones it keeps. TASK-003's specification is preserved whole, and the
architecture keeps its argument — an agent enforcing its own spending limits is
circular — because that argument is still correct and is still unbuilt.

**By letting the new integration into the engine.** The failure mode for an
information provider is that "authoritative data" becomes a reason to rank it
higher. That is the one thing §2.1 forbids, and TASK-007 §3 says so in the terms
someone would actually reach for.

## 10. Tests run and their results

```
$ python3.12 -m unittest discover -q
Ran 423 tests in 0.13s
OK
```

**423 passing, unchanged.** No test could have been affected; the suite was run
to confirm the repository is green, and to confirm the claim that nothing in
`radhanite/` or `tests/` was touched.

## 11. Assumptions made

- **The decision is the product owner's and is final.** It was given directly.
  This PR records it and does not argue it.
- **Circle/Arc genuinely covers the wallet layer for this build.** That is the
  product owner's assessment; nothing here verifies it independently, and no
  Circle integration exists to check it against.

## 12. Known limitations

- **TASK-007 is a placeholder, not a specification.** It states a premise and
  three unresolved decisions. Nothing could be built from it as written, and it
  does not pretend otherwise.
- **One of those three has no owner.** §6.3 — turning returned evidence into a
  changed success probability — belongs to the task-state layer, and **no
  authorized task owns that layer.** Until one does, this integration cannot
  produce a working loop by itself.
- **§6.2 may not be satisfiable as stated.** The economic rule needs a strictly
  positive price *before* the purchase. Query pricing knowable only afterwards
  does not meet `TASK-006` §2.3, and that is a real constraint on what a Graph
  capability can look like.

## 13. Explicitly out of scope

No Graph API call, subgraph, query, key or client library. No Hedera, Circle or
Privy implementation. No payment logic, candidate discovery, or run-loop
behaviour. No change to `TASK-006`. No task changed authorization status —
TASK-007 arrives unauthorized, and everything else keeps the status it had.

## 14. Deferred to future tasks

Specifying TASK-007 properly, which needs §6.1–§6.3 answered first. The
remaining `TASK-006` deliverables are untouched and unaffected.

## 15. How to explain this to a judge

> We dropped an integration. Not because it was bad — because it overlapped with
> one we were already doing, and because it strengthened the part of the product
> nobody is competing on.
>
> What replaced it is a better fit for what we actually are: The Graph is
> something the agent can **buy**, not an authority it has to **hold**. Onchain
> evidence has a price and might improve your odds, so it goes through the same
> sum as everything else.
>
> The rule we did not relax: the engine is not allowed to know who is selling.
> The Graph gets no preference for being The Graph. If its evidence is worth
> buying, it wins on price and effect like anything else would.
>
> And the old plan is still in the repository, unedited, with the reason it was
> set aside. Deprioritizing something is not the same as deciding it was wrong.
