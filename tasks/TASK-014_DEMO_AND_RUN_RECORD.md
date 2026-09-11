# TASK-014 — Demonstration surface and run record

**Status:** Specified — **NOT AUTHORIZED for implementation**
**Authorization:** None. This document specifies the work; it does not permit it.
**Replaces backlog entry:** `BL-10`
**Depends on:** TASK-013

---

## 1. Purpose

The presentation layer for the benchmark: make one run legible to someone who
has not read the code.

## 2. What a run must show

| | |
|---|---|
| Opportunity value | What winning is worth |
| Operating budget | What may be spent |
| Current success probability | Declared, and labelled as declared |
| Available capabilities and prices | Everything on offer, not only what was bought |
| **The decision** | Which candidate won, and the arithmetic behind it |
| Selected capability | What was bought |
| Actual spend | `committed_cost`, which may differ from the quoted price |
| Remaining budget | What is left |
| Updated task state | What changed as a result |
| **Stop reason** | Which of the four terminal states, and why |
| **Retained margin** | Unused budget, presented as a result rather than a shortfall |

## 3. The two things it must not do

**It must not show only what was bought.** TASK-006 §8 requires the rejected
candidates and the reason each lost. A surface that hides them turns an auditable
decision back into an opaque one.

**It must not present declared figures as measured.** Every probability on
screen is a fixture — `ARCHITECTURE.md` §6 item 12.

## 4. Out of scope

Any economic logic. This layer reads a run record and renders it; a display that
computed anything would be a second implementation of the rule.
