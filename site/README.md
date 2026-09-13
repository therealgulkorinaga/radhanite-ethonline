# Radhanite demo frontend

**Implementation agents: Manus (TASK-016), Claude Code (TASK-011 update).**

This directory contains the TASK-016 desktop-first demo frontend for ETHOnline judges. It presents the Radhanite thesis as an economic control console for autonomous agents:

```text
Task + value + budget
→ candidate capabilities
→ economic evaluation
→ BUY / SKIP
→ execution of the selected capability
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

- `#dashboard` — demo dashboard with opportunity summary, candidate cards, selected decision, execution of the selected capability, evidence, and state transition.
- `#trace` — chronological decision trace from opportunity creation through the next TASK-006 decision.
- `#how` — architecture diagram and explicit integration status.

## Live data, benchmark prices, and what is not claimed

Two different claims appear on this screen, and the UI keeps them apart on purpose.

**LIVE DATA SOURCE — The Graph.** The selected capability's query really ran, against The Graph's decentralized network gateway. The facts on the dashboard came back from that query:

| Fact | Value |
|---|---|
| `poolCount` | 72,855 |
| `txCount` | 149,631,676 |
| `totalVolumeUSD` | 1,917,152,732,933.20 |
| Indexed block | 25,969,369 |

Reproduce it with `RADHANITE_GRAPH_API_KEY=... python3 -m radhanite.graph_smoke` from the repository root.

**BENCHMARK CAPABILITY PRICE — $0.40.** This is the price *Radhanite evaluated* for the capability inside the economic decision. **The Graph did not charge it.** The query ran under a Subgraph Studio Free plan and billed 0 GRT. The onchain facts are live; the price is a benchmark fixture, exactly like the declared probabilities. `demo-data.js` marks this with `costBasis: "benchmark"`, and a benchmark price is never rendered in USDC.

**Circle / Arc is visible but not selected, and not settled.** The adapter is implemented and the Arc Testnet smoke ran, but it became unresolved after submission and no authoritative committed amount or payment reference was preserved. This build asserts **no Arc settlement**, and a test enforces that no payment reference appears in the data at all. Arc is shown as a priced candidate the economics ranked second — at $2,999.999 net expected value against The Graph's $4,499.60.

**Hedera** remains **Coming next / Not connected in this build**.

The selected capability is not a presentation choice. The Graph is selected because it carries the highest net expected value of the priced candidates, and `demo-data.test.mjs` asserts both that the selected candidate is the net-EV maximum and that every candidate's arithmetic satisfies `net = (p_after − p_before) × value − cost`. TASK-006 economics were not modified to produce this narrative.

The frontend contains no live backend endpoint and no payment capability. It does not reproduce TASK-006 calculations in JavaScript; the displayed values are rendered from `demo-data.js`, which is shaped like backend output. `renderableState` still refuses to report live mode unless `execution.liveEvidence` is true, so the badge can never be claimed without evidence.

## Visual direction

The design is a restrained economic-control-console aesthetic: deep ink navigation, warm neutral surfaces, mint decision states, amber fixture/setup states, large numeric hierarchy, and compact monospace data. It avoids wallet-first, trading-dashboard, and developer-console patterns.

## Verification

The frontend is intentionally dependency-free. The repository-level Python suite remains the runtime authority. The demo's pure formatting/data module can be imported by a future lightweight browser test harness without changing the Python economic contracts.

**Implementation agents: Manus, Claude Code.**
