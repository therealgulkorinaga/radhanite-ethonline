# PR #41 — TASK-017: The Graph live evidence capability

**Implementation agent: Manus.**

## Result

This is a narrow blocker-only PR. The 15-minute live-query attempt did **not** produce a reliable live The Graph metric, so no runtime adapter, frontend change, candidate, probability, budget, or payment behavior was added.

## Exact blocker

The official Graph query path requires both:

1. A Graph API key, kept server-side and supplied through an environment variable.
2. A concrete current subgraph ID and schema exposing a commercially meaningful recent activity metric for the opportunity.

The current session has neither a configured Graph connector/API key nor an approved opportunity-specific Arc Testnet subgraph/query. Graph Explorer surfaced an Arc Testnet `zk-sendly` subgraph with ID `nN9Zif8kcoQdvcm62vsPPFUnhoyQiRK4vs5uyirdVDy`; its page reported zero signal, an update three months earlier, and no verified opportunity metric schema in the fetched response. It was not reliable evidence for this demo.

The official query shape is:

```text
https://gateway.thegraph.com/api/<API_KEY>/subgraphs/id/<SUBGRAPH_ID>
```

No request was sent because the required authenticated endpoint and verified metric were unavailable. No API key was printed, stored, or requested from the user during the timebox.

## Product boundary preserved

The Graph remains an evidence provider only:

```text
The Graph = live onchain facts
Radhanite = decides whether a capability is worth buying and what to do with returned evidence
```

The TASK-016 frontend Graph card remains **Coming next / Not connected in this build**. Circle/Arc fixture/live status is unchanged.

## Files changed

- `tasks/TASK-017_GRAPH_LIVE_EVIDENCE.md`
- `prompts/016_emergency-task-017-graph-live-evidence.md`

No runtime or frontend files changed.

## Human setup required for a future attempt

Arko must provide or authorize a Graph API key and a current Arc Testnet subgraph/query with a documented metric schema. Once available, the smallest live query should normalize to the authorized evidence shape and remain outside TASK-006 selection logic.

**Implementation agent: Manus.**
