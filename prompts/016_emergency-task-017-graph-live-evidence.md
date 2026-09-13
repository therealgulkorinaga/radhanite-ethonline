Yep. With 75 minutes, Graph is worth a real attempt.

I’d give Manus a **single-purpose Graph task** with a hard 15-minute ceiling. The goal is not “integrate The Graph generally”; it is “prove one live onchain signal can become Radhanite evidence.”

Use this:

> **EMERGENCY TASK-017 — THE GRAPH LIVE EVIDENCE CAPABILITY**
>
> Repository:
> `therealgulkorinaga/radhanite-ethonline`
>
> Context:
>
> Circle/Arc is frozen while a separate Codex investigation resolves the unresolved live smoke.
>
> We now need the smallest real The Graph integration that materially strengthens the ETHOnline demo.
>
> Timebox: **15 minutes max**.
>
> Human product owner / final merge authority: Arko.
> Implementation agent: Manus.
> Independent reviewer: Codex only if time permits.
>
> ---
>
> # PRODUCT PURPOSE
>
> The Graph is not an economic decision engine.
>
> It supplies **live onchain commercial evidence** that Radhanite can use in its existing capability loop.
>
> Required product boundary:
>
> `The Graph = live onchain facts`
>
> `Radhanite = decides whether the capability is worth buying and what to do with returned evidence`
>
> Do not let The Graph directly change:
>
> * probability
> * TASK-006 ranking
> * budget
> * final outcome
>
> ---
>
> # IMPLEMENT ONE NARROW QUESTION
>
> Answer exactly one commercially legible question:
>
> **“Is there meaningful recent onchain activity supporting this opportunity?”**
>
> Use the easiest reliable live The Graph source/query available.
>
> Prefer one metric such as:
>
> * recent transaction/activity count
> * recent swap/volume activity
> * liquidity
> * active users/addresses
>
> Pick whichever can be made live fastest and most reliably.
>
> Do not build a generic query engine.
>
> ---
>
> # REQUIRED OUTPUT CONTRACT
>
> Return structured evidence like:
>
> ```json
> {
>   "source": "the_graph",
>   "query_id": "...",
>   "metric": "...",
>   "value": "...",
>   "block_number": "...",
>   "timestamp": "...",
>   "outcome": "positive|neutral|negative"
> }
> ```
>
> `block_number` or `timestamp` may be omitted only if the source truly does not expose one.
>
> Never invent values.
>
> ---
>
> # INTEGRATION INTO RADHANITE
>
> Fit into the existing flow:
>
> `TASK-008 capability`
> → `TASK-006 economic selection`
> → `TASK-007 execution`
> → `The Graph live query`
> → `immutable evidence`
> → `TASK-009`
>
> Keep provider/query metadata outside the TASK-006 Candidate.
>
> TASK-006 should continue to see only:
>
> * candidate ID
> * exact cost
> * declared expected post-action probability
>
> The Graph adapter must not update probability directly.
>
> ---
>
> # COST
>
> Use one exact declared capability cost for the demo.
>
> If no real paid Graph endpoint is required for this integration, keep the cost clearly marked as a benchmark capability price rather than pretending The Graph charged it.
>
> Do not fabricate sponsor billing.
>
> ---
>
> # FRONTEND
>
> If and only if the live Graph query succeeds:
>
> update the TASK-016 Graph card from:
>
> `Not connected`
>
> to:
>
> `LIVE`
>
> and show:
>
> * actual metric
> * actual value
> * source/query label
> * block/timestamp if available
>
> Do not change Circle/Arc fixture/live status.
>
> ---
>
> # TESTS
>
> Minimum:
>
> * successful live-response normalization
> * malformed response rejected
> * missing required metric rejected
> * evidence does not directly modify probability
>
> Avoid heavy test infrastructure.
>
> ---
>
> # STOP CONDITION
>
> If a reliable live Graph query is not working within **15 minutes**, stop.
>
> Report:
>
> * exact blocker
> * whether auth/API key is required
> * whether query/subgraph selection is the blocker
> * whether frontend can remain unchanged
>
> Do not fabricate a successful integration.
>
> ---
>
> # GIT
>
> Create a narrow branch/PR.
>
> Suggested branch:
>
> `task-017-graph-live-evidence`
>
> Do not merge automatically.
>
> ---
>
> # REPORT
>
> Report:
>
> * branch
> * PR
> * head SHA
> * exact Graph endpoint/query used
> * actual returned metric/value
> * whether query is live
> * evidence shape
> * tests
> * whether frontend Graph card can truthfully be marked LIVE
>
> End with:
>
> **Implementation agent: Manus.**

And I’d use this remaining-time allocation:

* 15 min Graph
* 10 min Hedera if Graph works fast
* 15 min frontend/live-state polish
* 20 min video + screenshots
* 15 min submission buffer

If Graph starts asking for account setup, API keys, obscure subgraph IDs, or SDK surgery, abort fast. The value is in getting **one real live signal**, not in architectural completeness.
