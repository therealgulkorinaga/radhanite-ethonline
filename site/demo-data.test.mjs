// Implementation agent: Manus.
import test from "node:test";
import assert from "node:assert/strict";
import {
  costBasisLabel,
  fixture,
  formatAtomic,
  formatCapabilityCost,
  formatMoney,
  formatNetExpectedValue,
  formatPercent,
  formatUsdc,
  modeLabel,
  renderableState,
} from "./demo-data.js";

test("live mode is explicit and cannot be claimed without evidence", () => {
  assert.equal(modeLabel(fixture.mode), "LIVE · THE GRAPH");
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

test("the selected capability is the one the economics actually rank first", () => {
  const selected = fixture.capabilities.filter((capability) => capability.selected);
  assert.equal(selected.length, 1);
  assert.equal(selected[0].id, "graph-onchain-liquidity-001");
  assert.equal(selected[0].status, "BUY");
  // Selection must follow net expected value, not presentation preference.
  const best = [...fixture.capabilities].sort(
    (a, b) => Number(b.netExpectedValue) - Number(a.netExpectedValue),
  )[0];
  assert.equal(selected[0].id, best.id);
});

test("net expected value equals uplift times task value minus cost", () => {
  const value = Number(fixture.opportunity.value);
  const before = Number(fixture.opportunity.probabilityBefore);
  for (const capability of fixture.capabilities) {
    const incremental = (Number(capability.expectedProbability) - before) * value;
    assert.equal(incremental.toFixed(2), Number(capability.incrementalExpectedValue).toFixed(2));
    assert.equal(
      (incremental - Number(capability.cost)).toFixed(3),
      Number(capability.netExpectedValue).toFixed(3),
    );
  }
});

test("only the integration that actually ran is marked live", () => {
  assert.equal(fixture.capabilities.find((capability) => capability.provider === "The Graph").live, true);
  assert.equal(fixture.capabilities.find((capability) => capability.provider === "Circle / Arc").live, false);
  assert.equal(fixture.capabilities.find((capability) => capability.provider === "Hedera").live, false);
});

test("a benchmark price is never rendered as a settled USDC amount", () => {
  const graph = fixture.capabilities.find((capability) => capability.provider === "The Graph");
  assert.equal(graph.costBasis, "benchmark");
  assert.equal(formatCapabilityCost(graph), "$0.40");
  assert.equal(costBasisLabel(graph), "Benchmark price");
  assert.ok(!formatCapabilityCost(graph).includes("USDC"));
  const arc = fixture.capabilities.find((capability) => capability.provider === "Circle / Arc");
  assert.equal(formatCapabilityCost(arc), "0.001 USDC");
});

test("net expected value keeps a third decimal only when it carries information", () => {
  assert.equal(formatNetExpectedValue("4499.60"), "$4,499.60");
  assert.equal(formatNetExpectedValue("2999.999"), "$2,999.999");
  assert.equal(formatNetExpectedValue("999.60"), "$999.60");
});

test("the trace reads as the real sequence the engine ran", () => {
  const titles = fixture.trace.map(([, title]) => title);
  assert.ok(titles.includes("The Graph selected"));
  assert.ok(titles.includes("Live Graph query executed"));
  assert.ok(titles.includes("Live evidence returned"));
  assert.ok(titles.includes("TASK-009 state updated"));
  assert.ok(titles.includes("Next TASK-006 decision"));
});

test("no Arc settlement or payment reference is asserted anywhere", () => {
  const serialized = JSON.stringify(fixture);
  assert.ok(!serialized.includes("fixture-ref-arc-001"));
  assert.ok(!/committedAmount/.test(serialized));
  const arc = fixture.capabilities.find((capability) => capability.provider === "Circle / Arc");
  assert.equal(arc.selected, false);
});

test("execution records the live query and labels its price basis", () => {
  assert.equal(fixture.execution.liveEvidence, true);
  assert.equal(fixture.execution.provider, "The Graph");
  assert.equal(fixture.execution.block, "25969369");
  assert.equal(fixture.execution.evaluatedPrice, "0.40");
  assert.match(fixture.execution.priceLabel, /not an amount charged by The Graph/);
  assert.equal(fixture.evidence.outcomeKey, "positive_market_signal");
  assert.equal(fixture.evidence.serviceResult, "Live onchain liquidity and volume snapshot");
  // The facts must be the ones the live query actually returned.
  assert.ok(fixture.evidence.facts.some((fact) => fact.includes("72,855")));
  assert.ok(fixture.evidence.facts.some((fact) => fact.includes("149,631,676")));
  assert.ok(fixture.evidence.facts.some((fact) => fact.includes("25,969,369")));
});

test("trace includes the probability transition and next stop decision", () => {
  assert.ok(fixture.trace.some(([, title]) => title === "TASK-009 state updated"));
  assert.ok(fixture.trace.some(([, title, detail]) => title === "Next TASK-006 decision" && detail.includes("STOP")));
  assert.equal(fixture.opportunity.probabilityBefore, "0.08");
  assert.equal(fixture.opportunity.probabilityAfter, "0.14");
  // The declared expectation and the engine's actual output are different
  // numbers, and the UI must never quietly show the nicer one.
  assert.equal(fixture.opportunity.probabilityExpected, "0.17");
  assert.notEqual(fixture.opportunity.probabilityExpected, fixture.opportunity.probabilityAfter);
});

console.log("TASK-016 frontend fixture tests passed");
