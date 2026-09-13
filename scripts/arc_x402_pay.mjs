#!/usr/bin/env node
/**
 * TASK-015 Arc Testnet x402 buyer helper.
 *
 * **Implementation agent: Manus.**
 *
 * Uses Circle's official Developer-Controlled Wallet SDK to sign the
 * GatewayWalletBatched EIP-3009 authorization and Circle's official x402
 * batching SDK to perform the 402 challenge/retry. No secret is printed.
 */

import { randomUUID } from "node:crypto";
import { initiateDeveloperControlledWalletsClient } from "@circle-fin/developer-controlled-wallets";
import { BatchEvmScheme } from "@circle-fin/x402-batching/client";

const ARC_NETWORK = "eip155:5042002";
const ARC_CHAIN = "ARC-TESTNET";
const ARC_GATEWAY_DOMAIN = 26;
const ARC_USDC = "0x3600000000000000000000000000000000000000";
const DEFAULT_GATEWAY_WALLET = "0x0077777d7EBA4688BDeF3E311b846F25870A19B9";
const X402_VERSION = 2;
const X402_SCHEME = "exact";
const X402_BATCHING_NAME = "GatewayWalletBatched";
const X402_BATCHING_VERSION = "1";

function arg(name, fallback = undefined) {
  const index = process.argv.indexOf(name);
  return index >= 0 ? process.argv[index + 1] ?? fallback : fallback;
}

function requiredEnv(name) {
  const value = process.env[name];
  if (!value) throw new Error(`missing required environment variable ${name}`);
  return value;
}

function requiredArgOrEnv(option, envName) {
  return arg(option) ?? requiredEnv(envName);
}

function jsonLine(value) {
  process.stdout.write(`${JSON.stringify(value)}\n`);
}

function usdcToAtomic(value) {
  const text = String(value);
  if (!/^\d+(?:\.\d{1,6})?$/.test(text)) throw new Error(`invalid USDC amount ${text}`);
  const [whole, fraction = ""] = text.split(".");
  const atomic = BigInt(whole) * 1_000_000n + BigInt(fraction.padEnd(6, "0") || "0");
  if (atomic <= 0n) throw new Error("USDC amount must be positive");
  return atomic;
}

function atomicToUsdc(value) {
  const atomic = BigInt(value);
  if (atomic <= 0n) throw new Error("atomic USDC amount must be positive");
  const whole = atomic / 1_000_000n;
  const fraction = String(atomic % 1_000_000n).padStart(6, "0");
  return `${whole}.${fraction}`;
}

function normalizeEvmAddress(value, label) {
  if (typeof value !== "string" || !/^0x[0-9a-fA-F]{40}$/.test(value)) {
    throw new Error(`${label} must have a 0x prefix and exactly 40 hexadecimal characters`);
  }
  return value.toLowerCase();
}

function normalizeTypedData(params) {
  const domain = { ...params.domain, chainId: String(params.domain.chainId) };
  const types = {
    EIP712Domain: [
      { name: "name", type: "string" },
      { name: "version", type: "string" },
      { name: "chainId", type: "uint256" },
      { name: "verifyingContract", type: "address" },
    ],
    ...params.types,
  };
  return JSON.stringify({ types, domain, primaryType: params.primaryType, message: params.message });
}

async function getOrCreateWallet(circle, requestedAddress) {
  if (requestedAddress) return normalizeEvmAddress(requestedAddress, "Arc wallet address");
  const listed = await circle.listWallets({ pageSize: 50 });
  const wallets = listed.data?.wallets ?? [];
  const existing = wallets.find(
    (wallet) => wallet.blockchain === ARC_CHAIN && wallet.accountType === "EOA",
  );
  if (existing?.address) return normalizeEvmAddress(existing.address, "Circle Arc wallet address");

  let walletSetId = process.env.CIRCLE_WALLET_SET_ID;
  if (!walletSetId) {
    const createdSet = await circle.createWalletSet({ name: "Radhanite Arc Testnet", idempotencyKey: randomUUID() });
    walletSetId = createdSet.data?.walletSet?.id;
  }
  if (!walletSetId) throw new Error("Circle did not return a wallet-set id.");
  const created = await circle.createWallets({
    walletSetId,
    blockchains: [ARC_CHAIN],
    count: 1,
    accountType: "EOA",
    idempotencyKey: randomUUID(),
  });
  const wallet = created.data?.wallets?.[0];
  if (!wallet?.address) throw new Error("Circle did not return the created Arc wallet address.");
  return normalizeEvmAddress(wallet.address, "created Circle Arc wallet address");
}

async function getGatewayBalance(walletAddress) {
  const response = await fetch("https://gateway-api-testnet.circle.com/v1/balances", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token: "USDC", sources: [{ domain: ARC_GATEWAY_DOMAIN, depositor: walletAddress }] }),
  });
  if (!response.ok) throw new Error(`Gateway balance request failed: ${response.status}`);
  const result = await response.json();
  const balance = result.balances?.find(({ domain }) => domain === ARC_GATEWAY_DOMAIN)?.balance ?? "0";
  return usdcToAtomic(String(balance));
}

async function waitForCircleTransaction(circle, transactionId) {
  const terminalStates = new Set(["COMPLETE", "CONFIRMED", "FAILED", "DENIED", "CANCELLED"]);
  while (true) {
    const response = await circle.getTransaction({ id: transactionId });
    const state = response.data?.transaction?.state;
    if (state && terminalStates.has(state)) {
      if (state !== "COMPLETE" && state !== "CONFIRMED") throw new Error(`Circle Wallet transaction ended in state: ${state}`);
      return;
    }
    await new Promise((resolve) => setTimeout(resolve, 3000));
  }
}

async function ensureGatewayBalance(circle, walletAddress, depositAmount, gatewayWallet) {
  const depositAtomic = usdcToAtomic(depositAmount);
  const current = await getGatewayBalance(walletAddress);
  if (current >= depositAtomic) return current;
  const approval = await circle.createContractExecutionTransaction({
    walletAddress,
    blockchain: ARC_CHAIN,
    contractAddress: ARC_USDC,
    abiFunctionSignature: "approve(address,uint256)",
    abiParameters: [gatewayWallet, String(depositAtomic)],
    fee: { type: "level", config: { feeLevel: "MEDIUM" } },
  });
  const approvalId = approval.data?.id;
  if (!approvalId) throw new Error("Circle USDC approval was not created.");
  await waitForCircleTransaction(circle, approvalId);
  const deposit = await circle.createContractExecutionTransaction({
    walletAddress,
    blockchain: ARC_CHAIN,
    contractAddress: gatewayWallet,
    abiFunctionSignature: "deposit(address,uint256)",
    abiParameters: [ARC_USDC, String(depositAtomic)],
    fee: { type: "level", config: { feeLevel: "MEDIUM" } },
  });
  const depositId = deposit.data?.id;
  if (!depositId) throw new Error("Circle Gateway deposit was not created.");
  await waitForCircleTransaction(circle, depositId);
  for (let attempt = 0; attempt < 40; attempt += 1) {
    const available = await getGatewayBalance(walletAddress);
    if (available >= depositAtomic) return available;
    await new Promise((resolve) => setTimeout(resolve, 3000));
  }
  throw new Error("Gateway balance did not become available after deposit.");
}

function parsePaymentRequired(header) {
  let paymentRequired;
  try {
    paymentRequired = JSON.parse(Buffer.from(header, "base64").toString("utf8"));
  } catch (error) {
    throw new Error(`PAYMENT-REQUIRED is not valid base64 JSON: ${error.message}`);
  }
  if (paymentRequired.x402Version !== X402_VERSION) throw new Error(`Arc seller must return x402Version ${X402_VERSION}.`);
  if (!paymentRequired.resource || !Array.isArray(paymentRequired.accepts)) throw new Error("Arc seller omitted x402 resource or accepts metadata.");
  return paymentRequired;
}

function selectAuthorizedRequirement(paymentRequired, expectedAsset, expectedAmount) {
  const expectedAssetNormalized = normalizeEvmAddress(expectedAsset, "expected Arc asset");
  const expectedAmountAtomic = usdcToAtomic(expectedAmount);
  const acceptable = paymentRequired.accepts.filter((requirement) => {
    if (!requirement || typeof requirement !== "object") return false;
    if (requirement.network !== ARC_NETWORK || requirement.scheme !== X402_SCHEME) return false;
    if (normalizeEvmAddress(requirement.asset, "seller payment asset") !== expectedAssetNormalized) return false;
    if (requirement.extra?.name !== X402_BATCHING_NAME || requirement.extra?.version !== X402_BATCHING_VERSION) return false;
    if (normalizeEvmAddress(requirement.extra?.verifyingContract, "seller verifying contract") !== DEFAULT_GATEWAY_WALLET.toLowerCase()) return false;
    if (!/^\d+$/.test(String(requirement.amount)) || BigInt(requirement.amount) <= 0n) return false;
    if (BigInt(requirement.amount) !== expectedAmountAtomic) return false;
    if (!Number.isInteger(requirement.maxTimeoutSeconds) || requirement.maxTimeoutSeconds <= 0) return false;
    try { normalizeEvmAddress(requirement.payTo, "seller payTo address"); } catch { return false; }
    return true;
  });
  if (acceptable.length !== 1) throw new Error("Arc seller did not expose exactly one authorized Arc Gateway requirement.");
  return acceptable[0];
}

async function main() {
  const url = requiredArgOrEnv("--url", "Radhanite_ARC_RESOURCE");
  const method = arg("--method", "GET").toUpperCase();
  const maxAmount = requiredArgOrEnv("--amount", "Radhanite_ARC_MAX_AMOUNT");
  const expectedNetwork = arg("--network", ARC_NETWORK);
  const expectedAsset = arg("--asset", ARC_USDC);
  const gatewayWallet = arg("--gateway-wallet", DEFAULT_GATEWAY_WALLET);
  if (expectedNetwork !== ARC_NETWORK) throw new Error("Arc helper only accepts eip155:5042002.");
  if (normalizeEvmAddress(expectedAsset, "Arc asset") !== ARC_USDC.toLowerCase()) throw new Error("Arc helper only accepts the Arc Testnet USDC asset.");
  if (normalizeEvmAddress(gatewayWallet, "Arc GatewayWallet") !== DEFAULT_GATEWAY_WALLET.toLowerCase()) throw new Error("Arc helper only accepts the Arc Testnet GatewayWallet.");
  if (method !== "GET") throw new Error("The Arc demo helper currently supports GET only.");
  const expectedAmountAtomic = usdcToAtomic(maxAmount);

  const apiKey = requiredEnv("CIRCLE_API_KEY");
  const entitySecret = requiredEnv("CIRCLE_ENTITY_SECRET");
  const circle = initiateDeveloperControlledWalletsClient({ apiKey, entitySecret });
  const walletAddress = await getOrCreateWallet(circle, arg("--wallet-address", process.env.CIRCLE_ARC_WALLET_ADDRESS));
  const depositAmount = arg("--deposit-amount", process.env.Radhanite_ARC_DEPOSIT_AMOUNT ?? "1");
  const gatewayBalance = await ensureGatewayBalance(circle, walletAddress, depositAmount, gatewayWallet);

  const signer = {
    address: walletAddress,
    signTypedData: async (params) => {
      const signed = await circle.signTypedData({
        walletAddress,
        blockchain: ARC_CHAIN,
        data: normalizeTypedData(params),
        memo: "Radhanite Arc x402 capability payment",
      });
      const signature = signed.data?.signature;
      if (!signature) throw new Error("Circle returned no typed-data signature.");
      return signature.startsWith("0x") ? signature : `0x${signature}`;
    },
  };

  let paymentSubmitted = false;
  try {
    const response = await fetch(url, { method });
    if (response.status !== 402) throw new Error(`Arc seller must return 402 before payment; got HTTP ${response.status}.`);
    const paymentRequiredHeader = response.headers.get("PAYMENT-REQUIRED");
    if (!paymentRequiredHeader) throw new Error("Arc seller omitted PAYMENT-REQUIRED.");
    const paymentRequired = parsePaymentRequired(paymentRequiredHeader);
    const selected = selectAuthorizedRequirement(paymentRequired, expectedAsset, maxAmount);
    if (expectedAmountAtomic > gatewayBalance) throw new Error("Gateway balance is below the exact selected Arc payment amount.");
    const batchScheme = new BatchEvmScheme(signer);
    const paymentPayload = await batchScheme.createPaymentPayload(paymentRequired.x402Version, selected);
    paymentSubmitted = true;
    const paid = await fetch(url, {
      method,
      headers: {
        "PAYMENT-SIGNATURE": Buffer.from(JSON.stringify({ ...paymentPayload, accepted: selected, resource: paymentRequired.resource })).toString("base64"),
      },
    });
    const bodyText = await paid.text();
    if (!paid.ok) throw new Error(`Arc x402 seller rejected payment with HTTP ${paid.status}: ${bodyText.slice(0, 200)}`);
    const settleHeader = paid.headers.get("PAYMENT-RESPONSE");
    if (!settleHeader) throw new Error("Arc seller omitted PAYMENT-RESPONSE after signed payment.");
    let settle;
    try { settle = JSON.parse(Buffer.from(settleHeader, "base64").toString("utf8")); } catch (error) { throw new Error(`PAYMENT-RESPONSE is not valid base64 JSON: ${error.message}`); }
    if (settle.success !== true) throw new Error("Arc Gateway did not report successful payment acceptance.");
    if (settle.network !== ARC_NETWORK) throw new Error("Arc Gateway response returned a non-Arc network.");
    if (typeof settle.transaction !== "string" || !settle.transaction.trim()) throw new Error("Arc Gateway response omitted its transaction/payment reference.");

    jsonLine({
      status: "gateway_accepted",
      settlement_status: "gateway_accepted",
      network: ARC_NETWORK,
      asset: expectedAsset,
      amount: atomicToUsdc(selected.amount),
      amount_atomic: String(selected.amount),
      wallet_address: walletAddress,
      payment_reference: settle.transaction,
      response_status: paid.status,
      result: bodyText ? JSON.parse(bodyText) : null,
    });
  } catch (error) {
    jsonLine({ error: error instanceof Error ? error.message : String(error), ...(paymentSubmitted ? { commitment_status: "unresolved" } : {}) });
    process.exitCode = 1;
  }
}

main().catch((error) => {
  jsonLine({ error: error instanceof Error ? error.message : String(error) });
  process.exitCode = 1;
});
