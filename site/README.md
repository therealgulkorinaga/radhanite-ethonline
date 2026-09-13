# Radhanite demo frontend

**Implementation agent: Manus.**

This directory contains the TASK-016 desktop-first demo frontend for ETHOnline judges. It presents the Radhanite thesis as an economic control console for autonomous agents:

```text
Task + value + budget
→ candidate capabilities
→ economic evaluation
→ BUY / SKIP
→ Circle / Arc execution
→ evidence
→ updated probability/state
→ next decision / STOP
```

## Run locally

From the repository root:

```bash
python3 -m http.server 4173 --directory site
```

Then open <http://127.0.0.1:4173/>. Opening `site/index.html` directly also works in modern browsers, but an HTTP server is recommended because the UI imports `demo-data.js` as an ES module.

## Routes / views

The single-page demo exposes three hash views:

- `#dashboard` — live demo dashboard with opportunity summary, candidate cards, selected decision, Arc execution, evidence, and state transition.
- `#trace` — chronological decision trace from opportunity creation through the next TASK-006 decision.
- `#how` — architecture diagram and explicit integration status.

## Fixture and live honesty

This build defaults to **FIXTURE** mode. It uses deterministic backend-shaped benchmark data and never performs payment. The visible Arc wallet, x402, Arc Testnet, quote, committed amount, and reference are labelled fixture data and are not settlement evidence.

The frontend contains no live backend endpoint and no payment capability. It does not reproduce TASK-006 calculations in JavaScript. The displayed values are rendered from `demo-data.js`, which is shaped like backend output. A future live view may render actual backend evidence only when an authorized endpoint supplies it; it must then show `LIVE ARC TESTNET` and never silently fall back to fixture mode.

The Graph and Hedera are intentionally displayed as **Coming next / Not connected in this build**. They are not presented as live integrations.

## Visual direction

The design is a restrained economic-control-console aesthetic: deep ink navigation, warm neutral surfaces, mint decision states, amber fixture/setup states, large numeric hierarchy, and compact monospace data. It avoids wallet-first, trading-dashboard, and developer-console patterns.

## Verification

The frontend is intentionally dependency-free. The repository-level Python suite remains the runtime authority. The demo's pure formatting/data module can be imported by a future lightweight browser test harness without changing the Python economic contracts.

**Implementation agent: Manus.**
