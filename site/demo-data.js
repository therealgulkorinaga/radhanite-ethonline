/**
 * TASK-016 deterministic frontend fixture.
 *
 * **Implementation agent: Manus.**
 *
 * The UI renders this backend-shaped data; it does not reproduce TASK-006
 * calculations. Fixture references are explicitly non-settlement placeholders.
 */

export const fixture = {
  mode: "fixture",
  opportunity: {
    title: "Crypto infrastructure contract",
    value: "50000.00",
    budget: "250.00",
    remainingBudget: "249.999",
    probabilityBefore: "0.08",
    probabilityAfter: "0.14",
    stage: "Evidence acquired · next decision ready",
    finalState: "ECONOMIC STOP",
    questionResolved: "market_signal",
  },
  capabilities: [
    {
      id: "arc-demo-x402",
      name: "Premium market quote",
      provider: "Circle / Arc",
      network: "Arc Testnet",
      cost: "0.001",
      expectedProbability: "0.14",
      incrementalExpectedValue: "3000.00",
      netExpectedValue: "2999.999",
      status: "BUY",
      selected: true,
      reason: "Positive market-signal evidence clears the economic gate.",
      live: false,
    },
    {
      id: "graph-prospect-signal",
      name: "Prospect intelligence",
      provider: "The Graph",
      network: "Not connected in this build",
      cost: "0.75",
      expectedProbability: "0.09",
      incrementalExpectedValue: "499.25",
      netExpectedValue: "499.25",
      status: "SKIP",
      selected: false,
      reason: "Coming next · no live Graph adapter is connected.",
      live: false,
    },
    {
      id: "hedera-commercial-fit",
      name: "Commercial-fit signal",
      provider: "Hedera",
      network: "Not connected in this build",
      cost: "0.40",
      expectedProbability: "0.10",
      incrementalExpectedValue: "999.60",
      netExpectedValue: "999.60",
      status: "INELIGIBLE",
      selected: false,
      reason: "Coming next · no live Hedera adapter is connected.",
      live: false,
    },
  ],
  execution: {
    wallet: "Circle Developer-Controlled Wallet EOA",
    protocol: "x402 exact",
    network: "Arc Testnet",
    quote: "0.001",
    amountAtomic: "1000",
    committedAmount: "0.001",
    reference: "fixture-ref-arc-001",
    referenceLabel: "Fixture reference · not settlement evidence",
    status: "Fixture execution complete",
    liveEvidence: false,
  },
  evidence: {
    outcome: "positive",
    outcomeKey: "positive_market_signal",
    serviceResult: "Circle Arc Testnet x402 demo result",
    facts: [
      "Validated service result retained",
      "Exact committed testnet-USDC: 0.001",
      "TASK-009 market_signal resolved",
    ],
  },
  trace: [
    ["01", "Opportunity created", "value=$50,000 · budget=$250 · p=8%", "complete"],
    ["02", "Candidates generated", "3 priced capabilities · provider metadata retained outside selection", "complete"],
    ["03", "Economic evaluation", "TASK-006 compares exact cost, probability, value, and remaining budget", "complete"],
    ["04", "Capability selected", "Premium market quote · BUY · net expected value $2,999.999", "complete"],
    ["05", "Circle / Arc execution", "Fixture mode · wallet path and x402 fields rendered, no payment performed", "fixture"],
    ["06", "Service result", "positive_market_signal · validated demo result", "complete"],
    ["07", "Evidence recorded", "Immutable evidence passed to TASK-009", "complete"],
    ["08", "TASK-009 update", "p=8% → 14% · market_signal resolved", "complete"],
    ["09", "Next TASK-006 decision", "No remaining economically justified fixture action · STOP", "stop"],
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

export function modeLabel(mode) {
  return mode === "live" ? "LIVE ARC TESTNET" : "FIXTURE";
}

export function renderableState(data = fixture) {
  return {
    ...data,
    mode: data.mode === "live" && data.execution?.liveEvidence ? "live" : "fixture",
  };
}
