# EMERGENCY TASK-017 — The Graph live evidence capability

**Status:** Timeboxed blocker recorded; no runtime or frontend implementation.

**Implementation agent: Manus.**

## Intended question

> Is there meaningful recent onchain activity supporting this opportunity?

The Graph is an evidence source only. It must not directly change probability, TASK-006 ranking, budget, or final outcome. Any future adapter must keep query/provider metadata outside the TASK-006 Candidate and pass immutable structured evidence to the existing loop.

## Required evidence shape

```json
{
  "source": "the_graph",
  "query_id": "...",
  "metric": "...",
  "value": "...",
  "block_number": "...",
  "timestamp": "...",
  "outcome": "positive|neutral|negative"
}
```

Values must come from a successful live query. No fixture, guessed subgraph schema, or invented metric is acceptable.

## Timeboxed investigation result

The 15-minute investigation stopped without making a live query or changing the frontend. Official The Graph documentation confirms that Subgraph queries require an API key and use a concrete gateway endpoint of the form:

```text
https://gateway.thegraph.com/api/<API_KEY>/subgraphs/id/<SUBGRAPH_ID>
```

The current session has no configured Graph connector, no Graph API key, and no approved subgraph identifier/schema tied to this opportunity. The Graph Explorer search surfaced an Arc Testnet `zk-sendly` subgraph (`nN9Zif8kcoQdvcm62vsPPFUnhoyQiRK4vs5uyirdVDy`) whose page reports it was updated three months ago, has zero signal, and does not expose a verified opportunity-specific metric schema in the available response. It is not a reliable basis for a live commercial signal within this timebox.

## Stop condition

No runtime adapter, query, frontend state, candidate, probability, budget, or TASK-015 payment behavior was changed. The TASK-016 Graph card must remain **Coming next / Not connected in this build**. A future attempt requires Arko to provide or authorize a Graph API key and a current Arc Testnet subgraph/query whose schema exposes a meaningful recent activity metric.

**Implementation agent: Manus.**
