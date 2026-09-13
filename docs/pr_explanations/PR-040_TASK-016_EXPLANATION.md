# PR #40 — TASK-016: Radhanite demo frontend

**Implementation agent: Manus.**

## Summary

This PR adds a polished, desktop-first Radhanite demo frontend for ETHOnline judges. It makes the full thesis legible within thirty seconds:

```text
Task + value + budget
→ candidates
→ economic evaluation
→ BUY / SKIP
→ Circle / Arc execution
→ evidence
→ updated probability/state
→ next decision / STOP
```

## Frontend stack and run command

The frontend is a dependency-free static site built with semantic HTML, CSS, and browser ES modules. No new framework, package, wallet integration, or backend endpoint was introduced.

```bash
python3 -m http.server 4173 --directory site
```

Open `http://127.0.0.1:4173/`.

## Views

- `#dashboard` — live demo dashboard with $50,000 opportunity value, $249.999 fixture remaining budget, 8% → 14% probability transition, three candidate cards, selected Arc decision, exact fixture amount, evidence, and next decision.
- `#trace` — nine chronological events with expandable details: opportunity, candidates, economic evaluation, selected capability, Arc execution, service result, evidence, TASK-009 update, and next TASK-006 stop.
- `#how` — architecture diagram and integration honesty status.

## Backend authority

The frontend renders deterministic backend-shaped fixture data and does not reproduce TASK-006 calculations in JavaScript. Provider identity is visual metadata only. No selection, ranking, expected-value, accounting, or TASK-009 logic changed.

## Fixture/live boundary

The default state is visibly labelled **FIXTURE**. It explicitly says that no wallet, signature, payment, or settlement occurred. The Arc card shows:

- Circle Developer-Controlled Wallet EOA
- x402 exact
- Arc Testnet
- 0.001 USDC / 1,000 atomic units
- deterministic fixture committed amount
- `fixture-ref-arc-001`, labelled **Fixture reference · not settlement evidence**
- Fixture execution complete

The Graph and Hedera are visible as **Coming next / Not connected in this build** and are not represented as live integrations.

## Screenshot-ready states

1. **Economic Decision:** dashboard default view with opportunity, budget, probability, candidate cards, BUY/SKIP/INELIGIBLE statuses, and selected net expected value.
2. **Circle/Arc Execution:** dashboard execution and evidence cards with exact fixture quote, amount, reference boundary, wallet model, x402, Arc Testnet, and positive demo result.
3. **Decision Trace:** `#trace` with probability progression, fixture spend, evidence, and final `ECONOMIC STOP`.

## Tests and verification

- TASK-016 frontend fixture tests: **5 passing** (`node --test site/demo-data.test.mjs`)
- Node syntax checks: passed
- Static structure check: passed
- Existing Python suite: **784 passing**
- Browser preview verified dashboard, `#trace`, and `#how`
- No live Arc smoke, wallet call, signature, or payment was run

## Changed files

- `site/index.html`
- `site/demo-data.js`
- `site/demo-data.test.mjs`
- `site/README.md`
- `tasks/TASK-016_DEMO_FRONTEND.md`
- `docs/ARCHITECTURE_TASK016_DEMO_FRONTEND.md`
- `prompts/015_task-016-demo-frontend.md`

**Implementation agent: Manus.**
