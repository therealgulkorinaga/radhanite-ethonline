#!/usr/bin/env node
/**
 * TASK-010 Arc Testnet x402 buyer helper.
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
const DEFAULT_GATEWAY_WALLET = "0x0077777d7EBA4688BDeF3E311b846F25870A19B9";

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
  if (!/^\d+(?:\.\d{1,6})?$/.test(text)) {
    throw new Error(`invalid USDC amount ${text}`);
  }
  const [whole, fraction = ""] = text.split(".");
  return BigInt(whole) * 1_000_000n + BigInt(fraction.padEnd(6, "0") || "0");
}

function atomicToUsdc(value) {
  const atomic = BigInt(value);
  const whole = atomic / 1_000_000n;
  const fraction = String(atomic % 1_000_000n).padStart(6, "0");
  return `${whole}.${fraction}`;
}

function normalizeTypedData(params) {
  const domain = {
    ...params.domain,
    chainId: String(params.domain.chainId),
  };
  const types = {
    EIP712Domain: [
      { name: "name", type: "string" },
      { name: "version", type: "string" },
      { name: "chainId", type: "uint256" },
      { name: "verifyingContract", type: "address" },
    ],
    ...params.types,
  };
  return JSON.stringify({
    types,
    domain,
    primaryType: params.primaryType,
    message: params.message,
  });
}

async function getOrCreateWallet(circle, requestedAddress) {
  if (requestedAddress) return requestedAddress;

  const listed = await circle.listWallets({ pageSize: 50 });
  const wallets = listed.data?.wallets ?? [];
  const existing = wallets.find(
    (wallet) => wallet.blockchain === ARC_CHAIN && wallet.accountType === "EOA",
  );
  if (existing?.address) return existing.address;

  let walletSetId = process.env.CIRCLE_WALLET_SET_ID;
  if (!walletSetId) {
    const createdSet = await circle.createWalletSet({
      name: "Radhanite Arc Testnet",
      idempotencyKey: randomUUID(),
    });
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
  return wallet.address;
}

async function getGatewayBalance(walletAddress) {
  const response = await fetch("https://gateway-api-testnet.circle.com/v1/balances", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      token: "USDC",
      sources: [{ domain: 26, depositor: walletAddress }],
    }),
  });
  if (!response.ok) {
    throw new Error(`Gateway balance request failed: ${response.status}`);
  }
  const result = await response.json();
  const balance = result.balances?.find(({ domain }) => domain === 26)?.balance ?? "0";
  return usdcToAtomic(String(balance));
}

async function waitForCircleTransaction(circle, transactionId) {
  const terminalStates = new Set(["COMPLETE", "CONFIRMED", "FAILED", "DENIED", "CANCELLED"]);
  while (true) {
    const response = await circle.getTransaction({ id: transactionId });
    const state = response.data?.transaction?.state;
    if (state && terminalStates.has(state)) {
      if (state !== "COMPLETE" && state !== "CONFIRMED") {
        throw new Error(`Circle Wallet transaction ended in state: ${state}`);
      }
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
    contractAddress: process.env.Radhanite_ARC_USDC ?? "0x3600000000000000000000000000000000000000",
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
    abiParameters: [process.env.Radhanite_ARC_USDC ?? "0x3600000000000000000000000000000000000000", String(depositAtomic)],
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

async function main() {
  const url = requiredArgOrEnv("--url", "Radhanite_ARC_RESOURCE");
  const method = arg("--method", "GET").toUpperCase();
  const maxAmount = requiredArgOrEnv("--amount", "Radhanite_ARC_MAX_AMOUNT");
  const expectedNetwork = arg("--network", ARC_NETWORK);
  const expectedAsset = arg("--asset");
  const gatewayWallet = arg("--gateway-wallet", DEFAULT_GATEWAY_WALLET);
  if (expectedNetwork !== ARC_NETWORK) throw new Error("Arc helper only accepts eip155:5042002.");
  if (!expectedAsset) throw new Error("--asset is required.");
  if (method !== "GET") throw new Error("The Arc demo helper currently supports GET only.");

  const apiKey = requiredEnv("CIRCLE_API_KEY");
  const entitySecret = requiredEnv("CIRCLE_ENTITY_SECRET");
  const circle = initiateDeveloperControlledWalletsClient({ apiKey, entitySecret });
  const walletAddress = await getOrCreateWallet(
    circle,
    arg("--wallet-address", process.env.CIRCLE_ARC_WALLET_ADDRESS),
  );
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

  const response = await fetch(url, { method });
  if (response.status !== 402) {
    throw new Error(`Arc seller must return 402 before payment; got HTTP ${response.status}.`);
  }
  const paymentRequiredHeader = response.headers.get("PAYMENT-REQUIRED");
  if (!paymentRequiredHeader) throw new Error("Arc seller omitted PAYMENT-REQUIRED.");
  const paymentRequired = JSON.parse(Buffer.from(paymentRequiredHeader, "base64").toString("utf8"));
  if (!paymentRequired.resource) throw new Error("Arc seller omitted x402 resource metadata.");
  const accepts = (paymentRequired.accepts ?? []).filter(
    (requirement) =>
      requirement.network === ARC_NETWORK &&
      requirement.asset.toLowerCase() === expectedAsset.toLowerCase() &&
      requirement.scheme === "exact" &&
      requirement.extra?.name === "GatewayWalletBatched" &&
      BigInt(requirement.amount) <= usdcToAtomic(maxAmount),
  );
  if (accepts.length !== 1) throw new Error("Arc seller did not expose exactly one authorized Arc Gateway offer.");
  const selected = accepts[0];
  if (BigInt(selected.amount) > gatewayBalance) {
    throw new Error("Gateway balance is below the exact selected Arc payment amount.");
  }
  const batchScheme = new BatchEvmScheme(signer);
  const paymentPayload = await batchScheme.createPaymentPayload(paymentRequired.x402Version, selected);
  const paid = await fetch(url, {
    method,
    headers: {
      "PAYMENT-SIGNATURE": Buffer.from(JSON.stringify({
        ...paymentPayload,
        accepted: selected,
        resource: paymentRequired.resource,
      })).toString("base64"),
    },
  });
  const bodyText = await paid.text();
  if (!paid.ok) throw new Error(`Arc x402 seller rejected payment with HTTP ${paid.status}: ${bodyText.slice(0, 200)}`);

  let settle = {};
  const settleHeader = paid.headers.get("PAYMENT-RESPONSE");
  if (settleHeader) settle = JSON.parse(Buffer.from(settleHeader, "base64").toString("utf8"));
  const authorization = paymentPayload.payload?.authorization ?? {};
  const paymentReference = settle.transaction ?? settle.txHash ?? authorization.nonce ?? null;
  if (!paymentReference) throw new Error("Arc payment returned no transaction or authorization reference.");

  jsonLine({
    status: "settled",
    network: ARC_NETWORK,
    asset: expectedAsset,
    amount: atomicToUsdc(selected.amount),
    wallet_address: walletAddress,
    payment_reference: paymentReference,
    response_status: paid.status,
    result: bodyText ? JSON.parse(bodyText) : null,
  });
}

main().catch((error) => {
  jsonLine({ error: error instanceof Error ? error.message : String(error) });
  process.exitCode = 1;
});
