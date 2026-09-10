# site/

The public ETHOnline progress page. **Communication material, not product code.**

Committed under [`AI_BUILD_GOVERNANCE.md`](../docs/AI_BUILD_GOVERNANCE.md) §3.2,
which is the only authority that permits it and which constrains what it may
say.

```
site/index.html    the page — one file, no build step, no dependencies
vercel.json        at the repository root; points Vercel here
```

## Deploying

The page is a single static HTML file. It needs no build, no framework, and no
install step.

**Vercel.** Import the repository. `vercel.json` at the repository root already
sets `outputDirectory` to `site` with no build command, so the defaults are
correct and nothing needs configuring in the dashboard. If the project was
created before that file existed, set **Root Directory** to `site` and
**Framework Preset** to *Other* instead.

**Anything else.** Serve `site/` as a static directory, or open
`site/index.html` in a browser. Both work; there is nothing to compile.

The only network requests the page makes are to Google Fonts. Everything else —
styles, layout, the small script that tracks the scroll position — ships inside
the file.

## What this page may and may not say

§3.2 is narrow on purpose, because a landing page is exactly where a project
starts overclaiming.

- Every claim about what exists must be **true of a named commit**, and the page
  states which one. A page whose figures have drifted from the repository is a
  defect in the page.
- [`ARCHITECTURE.md`](../docs/ARCHITECTURE.md) §6 applies here **in full** —
  items 8 through 12 especially. Simulated figures are not USDC, declared
  fixtures are not measurements, testnet value is not production value, and
  nothing may imply Radhanite has done work it has not done.
- It **introduces no product or architecture decision.** It describes documents
  that already exist and has no authority of its own.
- Naming an integration here **authorizes nothing.** Every integration on the
  page is marked *not authorized*, which is the truth and must stay the truth.

## Keeping it honest

The figures come from the repository and go stale as the repository moves. When
they do, correct them in the same pull request as the change that invalidated
them, or correct the provenance line so a reader can see the page is behind.

Leaving a stale claim standing is the failure this project has spent the most
effort avoiding — see `AI_BUILD_GOVERNANCE.md` §7.4 for what it cost the last
few times.
