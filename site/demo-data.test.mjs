// Implementation agent: Manus.
import test from "node:test";
import assert from "node:assert/strict";
import {
  fixture,
  formatAtomic,
  formatMoney,
  formatPercent,
  formatUsdc,
  modeLabel,
  renderableState,
} from "./demo-data.js";

test("fixture mode is explicit and cannot become live without evidence", () => {
  assert.equal(modeLabel(fixture.mode), "FIXTURE");
  assert.equal(renderableState({ ...fixture, mode: "live", execution: { liveEvidence: false } }).mode, "fixture");
  assert.equal(renderableState({ ...fixture, mode: "live", execution: { liveEvidence: true } }).mode, "live");
});

test("exact monetary and atomic formatting is stable", () => {
  assert.equal(formatMoney("50000.00"), "$50,000.00");
  assert.equal(formatMoney("2999.999", 3), "$2,999.999");
  assert.equal(formatUsdc("0.001"), "0.001 USDC");
  assert.equal(formatAtomic("1000"), "1,000 atomic units");
  assert.equal(formatPercent("0.14"), "14%");
});

test("selected capability and skipped integrations are backend-shaped fixture data", () => {
  const selected = fixture.capabilities.filter((capability) => capability.selected);
  assert.equal(selected.length, 1);
  assert.equal(selected[0].id, "arc-demo-x402");
  assert.equal(selected[0].status, "BUY");
  assert.equal(fixture.capabilities.find((capability) => capability.provider === "The Graph").live, false);
  assert.equal(fixture.capabilities.find((capability) => capability.provider === "Hedera").live, false);
});

test("execution and evidence retain exact fixture amount and reference", () => {
  assert.equal(fixture.execution.committedAmount, "0.001");
  assert.equal(fixture.execution.amountAtomic, "1000");
  assert.equal(fixture.execution.reference, "fixture-ref-arc-001");
  assert.match(fixture.execution.referenceLabel, /not settlement evidence/);
  assert.equal(fixture.evidence.outcomeKey, "positive_market_signal");
  assert.equal(fixture.evidence.serviceResult, "Circle Arc Testnet x402 demo result");
});

test("trace includes the probability transition and next stop decision", () => {
  assert.ok(fixture.trace.some(([, title]) => title === "TASK-009 update"));
  assert.ok(fixture.trace.some(([, title, detail]) => title === "Next TASK-006 decision" && detail.includes("STOP")));
  assert.equal(fixture.opportunity.probabilityBefore, "0.08");
  assert.equal(fixture.opportunity.probabilityAfter, "0.14");
});

console.log("TASK-016 frontend fixture tests passed");
