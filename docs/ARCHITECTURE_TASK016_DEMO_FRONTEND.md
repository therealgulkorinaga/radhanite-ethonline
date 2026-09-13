# TASK-016 architecture note — demo frontend

**Implementation agent: Manus.**

TASK-016 is a presentation layer over existing Radhanite contracts. It does not become a second economic engine.

```text
backend-shaped runtime data
        ↓
site/demo-data.js fixture boundary
        ↓
static dashboard / trace / architecture views
```

The current repository has no authorized browser API for live TASK-006/TASK-009 state. Therefore the frontend uses a deterministic fixture that mirrors the shape of the runtime result without claiming it is a runtime observation. The fixture contains the $50,000 opportunity, $250 budget, 8% → 14% declared probability transition, three candidate statuses, the selected Circle/Arc capability, exact 0.001 USDC / 1,000-atomic-unit fixture amount, a clearly labelled fixture reference, positive service evidence, and the next economic stop.

TASK-006 remains authoritative for eligibility, ranking, exact cost, expected value, and selected capability. TASK-007 remains authoritative for selected-only execution and committed spend. TASK-009 remains authoritative for evidence and probability/state transitions. The frontend only formats and renders those backend-shaped fields; it does not calculate or mutate them.

The Arc execution card is deliberately labelled **FIXTURE MODE** and says that no wallet call, signature, payment, or settlement occurred. No reference is presented as live settlement evidence. The future live badge must be derived from actual backend evidence and must never fall back silently to fixture mode.

The Graph and Hedera slots are visible to communicate the intended provider-neutral architecture, but both are marked **Coming next / Not connected in this build**. This task does not implement either integration, and does not alter TASK-015 payment semantics.

**Implementation agent: Manus.**
