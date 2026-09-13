/**
 * TASK-016 frontend data, carrying the TASK-011 live Graph run.
 *
 * **Implementation agents: Manus (TASK-016), Claude Code (TASK-011 update).**
 *
 * The UI renders this backend-shaped data; it does not reproduce TASK-006
 * calculations.
 *
 * Two different claims live in this file and the UI must never blur them:
 *
 * - `live: true` and `liveEvidence: true` mean **the query actually ran** and
 *   the facts below came back from The Graph's decentralized network. They are
 *   real.
 * - `costBasis: "benchmark"` means the price is the figure **Radhanite
 *   evaluated** for the capability. It is not an amount The Graph charged. The
 *   query ran under a Subgraph Studio Free plan, which billed 0 GRT.
 *
 * Circle/Arc remains a visible candidate. Its own live smoke attempt became
 * unresolved after submission and no authoritative committed amount or payment
 * reference was ever preserved, so nothing here asserts an Arc settlement.
 */

export const fixture = {
  mode: "live",
  liveDataSource: {
    provider: "The Graph",
    network: "Decentralized Network gateway",
    subgraphId: "5zvR82QoaXYFyDEKLZ9t6v9adgnptxYpKpSbxtgVENFV",
    block: "25969369",
    note: "Query served by the decentralized network. Facts below are real.",
  },
  opportunity: {
    title: "Crypto infrastructure contract",
    value: "50000.00",
    budget: "250.00",
    remainingBudget: "249.60",
    probabilityBefore: "0.08",
    probabilityAfter: "0.14",
    stage: "Live onchain evidence acquired · next decision ready",
    finalState: "ECONOMIC STOP",
    questionResolved: "market_signal",
  },
  capabilities: [
    {
      id: "graph-onchain-liquidity-001",
      name: "Onchain liquidity and volume snapshot",
      provider: "The Graph",
      network: "Decentralized Network",
      cost: "0.40",
      costBasis: "benchmark",
      expectedProbability: "0.17",
      incrementalExpectedValue: "4500.00",
      netExpectedValue: "4499.60",
      status: "BUY",
      selected: true,
      reason:
        "Highest net expected value of the priced candidates. The query ran and returned live onchain facts.",
      live: true,
    },
    {
      id: "arc-demo-x402",
      name: "Premium market quote",
      provider: "Circle / Arc",
      network: "Arc Testnet · fixture execution",
      cost: "0.001",
      costBasis: "usdc",
      expectedProbability: "0.14",
      incrementalExpectedValue: "3000.00",
      netExpectedValue: "2999.999",
      status: "SKIP",
      selected: false,
      reason:
        "Positive expected value, but below the selected capability. Not bought in this run.",
      live: false,
    },
    {
      id: "hedera-commercial-fit",
      name: "Commercial-fit signal",
      provider: "Hedera",
      network: "Not connected in this build",
      cost: "0.40",
      costBasis: "benchmark",
      expectedProbability: "0.10",
      incrementalExpectedValue: "1000.00",
      netExpectedValue: "999.60",
      status: "INELIGIBLE",
      selected: false,
      reason: "Coming next · no live Hedera adapter is connected.",
      live: false,
    },
  ],
  execution: {
    provider: "The Graph",
    transport: "GraphQL over HTTPS · decentralized network gateway",
    network: "Decentralized Network",
    subgraphId: "5zvR82QoaXYFyDEKLZ9t6v9adgnptxYpKpSbxtgVENFV",
    block: "25969369",
    evaluatedPrice: "0.40",
    priceLabel: "Benchmark capability price · not an amount charged by The Graph",
    status: "Live query served",
    liveEvidence: true,
  },
  evidence: {
    outcome: "positive",
    outcomeKey: "positive_market_signal",
    serviceResult: "Live onchain liquidity and volume snapshot",
    facts: [
      "poolCount 72,855",
      "txCount 149,631,676",
      "totalVolumeUSD 1,917,152,732,933.20",
      "indexed at block 25,969,369",
    ],
  },
  trace: [
    ["01", "Opportunity created", "value=$50,000 · budget=$250 · p=8%", "complete"],
    ["02", "Candidates generated", "3 priced capabilities · provider metadata retained outside selection", "complete"],
    ["03", "Economic evaluation", "TASK-006 compares exact cost, probability, value, and remaining budget", "complete"],
    ["04", "Capability selected", "Onchain liquidity snapshot · BUY · net expected value $4,499.60", "complete"],
    ["05", "The Graph execution", "Live query served by the decentralized network gateway at block 25,969,369", "live"],
    ["06", "Service result", "positive_market_signal · live onchain facts returned", "complete"],
    ["07", "Evidence recorded", "Immutable evidence passed to TASK-009", "complete"],
    ["08", "TASK-009 update", "p=8% → 14% · market_signal resolved", "complete"],
    ["09", "Next TASK-006 decision", "No remaining economically justified action · ECONOMIC STOP", "stop"],
  ],
};

export function formatMoney(value, digits = 2) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(Number(value));
}

export function formatUsdc(value) {
  return `${Number(value).toFixed(3)} USDC`;
}

export function formatPercent(value) {
  return `${(Number(value) * 100).toFixed(0)}%`;
}

export function formatAtomic(value) {
  return `${new Intl.NumberFormat("en-US").format(Number(value))} atomic units`;
}

/**
 * How a candidate's price is rendered, and what the figure actually is.
 *
 * A benchmark price is what Radhanite evaluated, not what a provider charged.
 * Rendering it in the same units as a settled USDC amount is how a demo starts
 * implying a payment nobody made.
 */
export function formatCapabilityCost(capability) {
  return capability.costBasis === "usdc"
    ? formatUsdc(capability.cost)
    : formatMoney(capability.cost, 2);
}

export function costBasisLabel(capability) {
  return capability.costBasis === "usdc" ? "Exact quote" : "Benchmark price";
}

export function modeLabel(mode) {
  return mode === "live" ? "LIVE · THE GRAPH" : "FIXTURE";
}

export function renderableState(data = fixture) {
  return {
    ...data,
    mode: data.mode === "live" && data.execution?.liveEvidence ? "live" : "fixture",
  };
}
