#!/usr/bin/env node
/**
 * TASK-015 Arc Testnet x402 buyer helper.
 *
 * **Implementation agent: Manus.**
 *
 * The helper deliberately uses the lower-level BatchEvmScheme because the
 * pinned GatewayClient requires a raw private key. Circle signs the EIP-712
 * authorization through a pre-provisioned Developer-Controlled Wallet ID.
 * Wallet creation, funding, approval, and Gateway deposit are setup actions
 * and are intentionally not performed here.
 */

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
const AUTHORIZATION_FIELDS = ["from", "to", "value", "validAfter", "validBefore", "nonce"];
const AUTHORIZATION_TYPES = [
  { name: "from", type: "address" },
  { name: "to", type: "address" },
  { name: "value", type: "uint256" },
  { name: "validAfter", type: "uint256" },
  { name: "validBefore", type: "uint256" },
  { name: "nonce", type: "bytes32" },
];
const EIP712_DOMAIN_TYPES = [
  { name: "name", type: "string" },
  { name: "version", type: "string" },
  { name: "chainId", type: "uint256" },
  { name: "verifyingContract", type: "address" },
];

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

function normalizeSignature(value) {
  if (typeof value !== "string" || !/^0x[0-9a-fA-F]{130}$/.test(value)) {
    throw new Error("Circle returned an invalid EIP-712 signature.");
  }
  return value;
}

function jsonBigIntReplacer(_key, value) {
  return typeof value === "bigint" ? value.toString() : value;
}

function typedDataJson(params) {
  return JSON.stringify({
    types: {
      EIP712Domain: EIP712_DOMAIN_TYPES,
      ...params.types,
    },
    domain: params.domain,
    primaryType: params.primaryType,
    message: params.message,
  }, jsonBigIntReplacer);
}

function errorText(error) {
  return [
    error?.message,
    error?.response?.data?.message,
    error?.response?.data?.error,
  ].filter((value) => typeof value === "string").join(" ");
}

function isCircleTypedDataValidationRejection(error) {
  const detail = errorText(error);
  return detail.includes("there is extra data provided in the message (0 < 4)")
    && detail.includes("Failed during the validation for typed data");
}

function signingFailureEnvelope(error, circleSigningAttempted, paymentSubmitted) {
  const knownPreSignRejection = isCircleTypedDataValidationRejection(error);
  const preSign = knownPreSignRejection || (!circleSigningAttempted && !paymentSubmitted);
  return {
    phase: preSign ? "pre_sign" : "post_submit",
    status: "error",
    signing_started: preSign ? false : circleSigningAttempted,
    payment_submitted: paymentSubmitted,
    commitment_status: preSign ? "not_committed" : "unresolved",
    error: errorText(error) || String(error),
  };
}

function validateTypedData(params, selected, walletAddress) {
  if (params.primaryType !== "TransferWithAuthorization") {
    throw new Error("Circle signing refused: wrong EIP-712 primaryType.");
  }
  const domain = params.domain ?? {};
  if (domain.name !== X402_BATCHING_NAME || domain.version !== X402_BATCHING_VERSION) {
    throw new Error("Circle signing refused: wrong GatewayWalletBatched EIP-712 domain.");
  }
  if (Number(domain.chainId) !== 5042002) {
    throw new Error("Circle signing refused: wrong Arc EVM chain ID.");
  }
  if (normalizeEvmAddress(domain.verifyingContract, "EIP-712 verifying contract") !== DEFAULT_GATEWAY_WALLET.toLowerCase()) {
    throw new Error("Circle signing refused: wrong GatewayWallet verifying contract.");
  }
  const actualTypes = params.types?.TransferWithAuthorization;
  if (JSON.stringify(actualTypes) !== JSON.stringify(AUTHORIZATION_TYPES)) {
    throw new Error("Circle signing refused: wrong TransferWithAuthorization field schema.");
  }
  const message = params.message ?? {};
  if (JSON.stringify(Object.keys(message).sort()) !== JSON.stringify(AUTHORIZATION_FIELDS.sort())) {
    throw new Error("Circle signing refused: wrong authorization fields.");
  }
  if (normalizeEvmAddress(message.from, "authorization.from") !== walletAddress.toLowerCase()) {
    throw new Error("Circle signing refused: authorization.from does not match wallet address.");
  }
  normalizeEvmAddress(message.to, "authorization.to");
  if (BigInt(message.value) !== BigInt(selected.amount)) {
    throw new Error("Circle signing refused: authorization.value does not match exact quote.");
  }
  if (!/^\d+$/.test(String(message.validAfter)) || !/^\d+$/.test(String(message.validBefore))) {
    throw new Error("Circle signing refused: authorization validity bounds are invalid.");
  }
  if (BigInt(message.validBefore) <= BigInt(message.validAfter)) {
    throw new Error("Circle signing refused: authorization validity window is invalid.");
  }
  if (typeof message.nonce !== "string" || !/^0x[0-9a-fA-F]{64}$/.test(message.nonce)) {
    throw new Error("Circle signing refused: authorization.nonce is invalid.");
  }
}

async function verifyWalletIdentity(circle, walletId, walletAddress) {
  const response = await circle.getWallet({ id: walletId });
  const wallet = response.data?.wallet;
  if (!wallet) throw new Error("Arc wallet ID does not resolve to a Circle wallet.");
  if (normalizeEvmAddress(wallet.address, "Circle wallet address") !== walletAddress.toLowerCase()) {
    throw new Error("wallet ID/address mismatch");
  }
  if (wallet.blockchain !== ARC_CHAIN) throw new Error("Circle wallet is not on ARC-TESTNET.");
  if (wallet.accountType && wallet.accountType !== "EOA") throw new Error("Circle wallet is not an EOA.");
  return wallet;
}

async function getGatewayAvailableBalance(walletAddress) {
  const response = await fetch("https://gateway-api-testnet.circle.com/v1/balances", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token: "USDC", sources: [{ domain: ARC_GATEWAY_DOMAIN, depositor: walletAddress }] }),
  });
  const result = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(`Gateway balance check failed: ${result.message ?? response.status}`);
  const row = result.balances?.find(({ domain }) => domain === ARC_GATEWAY_DOMAIN);
  if (!row) throw new Error("Gateway balance missing; complete the Arc Gateway deposit setup.");
  const available = row.available ?? row.balance;
  if (available === undefined) throw new Error("Gateway balance response omitted available balance.");
  return usdcToAtomic(String(available));
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

function parseJsonServiceBody(bodyText) {
  try {
    return JSON.parse(bodyText);
  } catch (error) {
    throw new Error(`Arc seller returned non-JSON service result: ${error.message}`);
  }
}

function validateSettlement(settle, selected, walletAddress) {
  if (settle.success !== true) throw new Error("Arc Gateway did not report successful payment acceptance.");
  if (settle.network !== ARC_NETWORK) throw new Error("Arc Gateway response returned a non-Arc network.");
  if (typeof settle.transaction !== "string" || !settle.transaction.trim()) {
    throw new Error("Arc Gateway response omitted its transaction/payment reference.");
  }
  if (settle.amount !== undefined && String(settle.amount) !== String(selected.amount)) {
    throw new Error("Arc Gateway response amount does not match the exact authorized amount.");
  }
  if (settle.walletAddress !== undefined && normalizeEvmAddress(settle.walletAddress, "Arc Gateway wallet address") !== walletAddress.toLowerCase()) {
    throw new Error("Arc Gateway response wallet does not match the configured signer.");
  }
}

function validateServiceResult(serviceResult, responseStatus) {
  if (!serviceResult || typeof serviceResult !== "object" || Array.isArray(serviceResult)) {
    throw new Error("Arc seller returned no structured service result.");
  }
  if (responseStatus >= 200 && responseStatus < 300) {
    if (serviceResult.capability !== "arc-demo-quote") throw new Error("Arc seller returned an unrecognized demo capability result.");
    if (serviceResult.result !== "Circle Arc Testnet x402 demo result") throw new Error("Arc seller returned an unrecognized demo service result.");
    if (!["positive_market_signal", "neutral", "negative"].includes(serviceResult.outcome)) {
      throw new Error("Arc seller returned no supported demo service outcome.");
    }
    return serviceResult.outcome;
  }
  if (typeof serviceResult.error !== "string" || !serviceResult.error.trim()) {
    throw new Error("Arc seller returned no structured service failure result.");
  }
  return "service_failure";
}

function committedFailureEnvelope(committed, reason) {
  return {
    phase: "post_submit",
    status: "error",
    commitment_status: "committed",
    ...committed,
    service_outcome: "service_failure",
    service_result: { error: reason },
    error: reason,
  };
}

async function main() {
  const url = requiredArgOrEnv("--url", "RADHANITE_ARC_RESOURCE");
  const expectedPrice = requiredArgOrEnv("--amount", "RADHANITE_ARC_PRICE");
  const method = arg("--method", "GET").toUpperCase();
  const expectedNetwork = arg("--network", ARC_NETWORK);
  const expectedAsset = arg("--asset", ARC_USDC);
  const gatewayWallet = arg("--gateway-wallet", DEFAULT_GATEWAY_WALLET);
  const walletId = requiredArgOrEnv("--wallet-id", "CIRCLE_ARC_WALLET_ID");
  const walletAddress = normalizeEvmAddress(requiredArgOrEnv("--wallet-address", "CIRCLE_ARC_WALLET_ADDRESS"), "CIRCLE_ARC_WALLET_ADDRESS");
  if (expectedNetwork !== ARC_NETWORK) throw new Error("Arc helper only accepts eip155:5042002.");
  if (normalizeEvmAddress(expectedAsset, "Arc asset") !== ARC_USDC.toLowerCase()) throw new Error("Arc helper only accepts the Arc Testnet USDC asset.");
  if (normalizeEvmAddress(gatewayWallet, "Arc GatewayWallet") !== DEFAULT_GATEWAY_WALLET.toLowerCase()) throw new Error("Arc helper only accepts the Arc Testnet GatewayWallet.");
  if (method !== "GET") throw new Error("The Arc demo helper currently supports GET only.");
  const expectedAmountAtomic = usdcToAtomic(expectedPrice);

  const apiKey = requiredEnv("CIRCLE_API_KEY");
  const entitySecret = requiredEnv("CIRCLE_ENTITY_SECRET");
  const circle = initiateDeveloperControlledWalletsClient({ apiKey, entitySecret });
  await verifyWalletIdentity(circle, walletId, walletAddress);
  const gatewayAvailable = await getGatewayAvailableBalance(walletAddress);
  if (gatewayAvailable < expectedAmountAtomic) throw new Error("insufficient Gateway balance; complete the Arc Gateway deposit setup");

  let circleSigningAttempted = false;
  let paymentSubmitted = false;
  try {
    const response = await fetch(url, { method });
    if (response.status !== 402) throw new Error(`Arc seller must return 402 before payment; got HTTP ${response.status}.`);
    const paymentRequiredHeader = response.headers.get("PAYMENT-REQUIRED");
    if (!paymentRequiredHeader) throw new Error("Arc seller omitted PAYMENT-REQUIRED.");
    const paymentRequired = parsePaymentRequired(paymentRequiredHeader);
    const selected = selectAuthorizedRequirement(paymentRequired, expectedAsset, expectedPrice);
    const signer = {
      address: walletAddress,
      signTypedData: async (params) => {
        validateTypedData(params, selected, walletAddress);
        let signed;
        try {
          signed = await circle.signTypedData({
            walletId,
            data: typedDataJson(params),
            memo: "Radhanite Arc x402 capability payment",
          });
        } catch (error) {
          // A known Circle schema rejection proves no signature was returned.
          // Ambiguous provider failures remain unresolved by design.
          if (!isCircleTypedDataValidationRejection(error)) circleSigningAttempted = true;
          throw error;
        }
        circleSigningAttempted = true;
        return normalizeSignature(signed.data?.signature);
      },
    };
    const batchScheme = new BatchEvmScheme(signer);
    const paymentPayload = await batchScheme.createPaymentPayload(X402_VERSION, selected);
    paymentSubmitted = true;
    const paid = await fetch(url, {
      method,
      headers: {
        "PAYMENT-SIGNATURE": Buffer.from(JSON.stringify({ ...paymentPayload, accepted: selected, resource: paymentRequired.resource })).toString("base64"),
      },
    });
    const settleHeader = paid.headers.get("PAYMENT-RESPONSE");
    if (!settleHeader) throw new Error("Arc seller omitted PAYMENT-RESPONSE after signed payment.");
    let settle;
    try { settle = JSON.parse(Buffer.from(settleHeader, "base64").toString("utf8")); } catch (error) { throw new Error(`PAYMENT-RESPONSE is not valid base64 JSON: ${error.message}`); }
    validateSettlement(settle, selected, walletAddress);
    const committed = {
      settlement_status: "gateway_accepted",
      network: ARC_NETWORK,
      asset: expectedAsset,
      amount: atomicToUsdc(selected.amount),
      amount_atomic: String(selected.amount),
      wallet_id: walletId,
      wallet_address: walletAddress,
      gateway_available: atomicToUsdc(gatewayAvailable),
      payment_reference: settle.transaction,
      response_status: paid.status,
    };
    try {
      const bodyText = await paid.text();
      const serviceResult = parseJsonServiceBody(bodyText);
      const serviceOutcome = validateServiceResult(serviceResult, paid.status);
      jsonLine({
        phase: "complete",
        status: "gateway_accepted",
        commitment_status: "committed",
        ...committed,
        service_outcome: serviceOutcome,
        service_result: serviceResult,
      });
    } catch (error) {
      const reason = error instanceof Error ? error.message : String(error);
      jsonLine(committedFailureEnvelope(committed, reason));
      process.exitCode = 1;
    }
  } catch (error) {
    jsonLine(signingFailureEnvelope(error, circleSigningAttempted, paymentSubmitted));
    process.exitCode = 1;
  }
}

if (process.argv[1] && import.meta.url === new URL(process.argv[1], "file:").href) {
  main().catch((error) => {
    jsonLine({
      phase: "pre_sign",
      status: "error",
      signing_started: false,
      payment_submitted: false,
      commitment_status: "not_committed",
      error: error instanceof Error ? error.message : String(error),
    });
    process.exitCode = 1;
  });
}

export {
  normalizeEvmAddress,
  selectAuthorizedRequirement,
  typedDataJson,
  validateServiceResult,
  validateSettlement,
  committedFailureEnvelope,
  validateTypedData,
  isCircleTypedDataValidationRejection,
  signingFailureEnvelope,
};
