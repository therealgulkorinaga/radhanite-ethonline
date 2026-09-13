# TASK-016 — Radhanite demo frontend

**Status:** Implemented on branch `task-016-demo-frontend`; pending human merge.

**Implementation agent: Manus.**

## Purpose

Make the Radhanite thesis understandable to an ETHOnline judge within thirty seconds without changing the economic kernel or Arc payment semantics. The demo presents task value, budget, candidate capabilities, economic evaluation, selected-only execution, evidence, the TASK-009 state update, and the next TASK-006 decision.

## Product message

> Radhanite is the economic execution layer for autonomous agents.

The benchmark is a **$50,000 opportunity**, a **$250 agent budget**, and an **8% initial success probability**. The primary safety message is: **budget is permission to spend, not a target to spend**.

## Scope

The frontend has three hash views:

| View | Purpose |
| --- | --- |
| `#dashboard` | Opportunity KPIs, capability cards, selected decision, Circle/Arc execution boundary, evidence, and probability/budget transition. |
| `#trace` | Chronological nine-event run record with expandable event details. |
| `#how` | Architecture diagram and explicit Circle/Arc, The Graph, and Hedera connection status. |

The frontend is a dependency-free static site using HTML, CSS, and browser ES modules. It is runnable with `python3 -m http.server 4173 --directory site` and does not require a build step.

## Authority and honesty boundaries

The UI renders deterministic backend-shaped fixture data from `site/demo-data.js`. It does not reproduce TASK-006 calculations in JavaScript and introduces no provider-selection logic. Provider identity is displayed as metadata only.

The default badge is **FIXTURE**. It explicitly states that no wallet, signature, payment, or settlement occurred. The displayed Arc quote, committed amount, and reference are labelled fixture values and not settlement evidence. A future live view may display **LIVE ARC TESTNET** only when actual backend evidence is present; the current build has no backend endpoint and no payment capability.

The Graph and Hedera are marked **Coming next / Not connected in this build**. They are not represented as live integrations.

## Verification

The lightweight Node test suite covers fixture/live-mode guarding, exact monetary and atomic formatting, selected capability rendering, committed amount/reference rendering, evidence outcome, state transition, and Graph/Hedera non-live status. The repository's Python suite remains unchanged and authoritative.

**Implementation agent: Manus.**
