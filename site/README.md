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

**Expected 17%, actual 14%.** The selected candidate declared an expected post-action probability of `0.17`. TASK-009 interpreted the returned evidence and assigned `0.14`. The dashboard shows both, and the state transition shows the engine's actual output rather than the expectation.

**BENCHMARK CAPABILITY PRICE — $0.40.** This is the price *Radhanite evaluated* for the capability inside the economic decision. **The Graph did not charge it.** The query ran under a Subgraph Studio Free plan and billed 0 GRT. The onchain facts are live; the price is a benchmark fixture, exactly like the declared probabilities. `demo-data.js` marks this with `costBasis: "benchmark"`, and a benchmark price is never rendered in USDC.

**LIVE x402 EXECUTION — Circle / Arc.** One authorized smoke, one attempt, no retry, run at commit `c93759d`. Every figure below is copied verbatim from the preserved record `runs/arc_testnet_live_smoke_20260913T153540Z.json`, and a test fails if the UI drifts from it:

| Field | Value |
|---|---|
| Exact quote | 0.001 testnet-USDC |
| Exact committed amount | 0.001000 testnet-USDC |
| Payment reference | `5255d5c3-23f8-4131-aded-084edf821bcd` |
| Settlement status | `gateway_accepted` |
| Service result | HTTP 200 · Circle Arc Testnet x402 demo result |
| TASK-009 in that run | 8% → 14% · `economic_stop` |

**On-chain finality is not asserted.** That reference is Circle Gateway acceptance, not a transaction hash.

**Arc ran as its own run, and is still not the selected capability.** Arc was the only candidate offered to that run, so TASK-006 selected it there. It is not a second purchase inside the run the dashboard narrates. In the run shown, Arc is ranked second — $2,999.999 net expected value against The Graph's $4,499.60 — so the live payment succeeding did **not** make it the selected buy.

**Hedera** remains **Coming next / Not connected in this build**.

The screen therefore communicates three things: The Graph — LIVE onchain evidence; Circle / Arc — LIVE x402 execution; Radhanite — decides which capability is economically worth buying.

The selected capability is not a presentation choice. The Graph is selected because it carries the highest net expected value of the priced candidates, and `demo-data.test.mjs` asserts both that the selected candidate is the net-EV maximum and that every candidate's arithmetic satisfies `net = (p_after − p_before) × value − cost`. TASK-006 economics were not modified to produce this narrative.

The frontend contains no live backend endpoint and no payment capability. It does not reproduce TASK-006 calculations in JavaScript; the displayed values are rendered from `demo-data.js`, which is shaped like backend output. `renderableState` still refuses to report live mode unless `execution.liveEvidence` is true, so the badge can never be claimed without evidence.

## Visual direction

The design is a restrained economic-control-console aesthetic: deep ink navigation, warm neutral surfaces, mint decision states, amber fixture/setup states, large numeric hierarchy, and compact monospace data. It avoids wallet-first, trading-dashboard, and developer-console patterns.

## Verification

The frontend is intentionally dependency-free. The repository-level Python suite remains the runtime authority. The demo's pure formatting/data module can be imported by a future lightweight browser test harness without changing the Python economic contracts.

**Implementation agents: Manus, Claude Code.**
