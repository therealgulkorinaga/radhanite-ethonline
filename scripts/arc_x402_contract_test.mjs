#!/usr/bin/env node
/**
 * TASK-015 mocked Node contract tests; no Circle or seller calls are made.
 * **Implementation agent: Manus.**
 */

import assert from "node:assert/strict";
import { BatchEvmScheme } from "@circle-fin/x402-batching/client";
import { typedDataJson, validateTypedData } from "./arc_x402_pay.mjs";

const walletId = "wallet-id-for-test";
const walletAddress = "0x1111111111111111111111111111111111111111";
const requirements = {
  scheme: "exact",
  network: "eip155:5042002",
  asset: "0x3600000000000000000000000000000000000000",
  amount: "1000",
  payTo: "0x2222222222222222222222222222222222222222",
  maxTimeoutSeconds: 60,
  extra: {
    name: "GatewayWalletBatched",
    version: "1",
    verifyingContract: "0x0077777d7EBA4688BDeF3E311b846F25870A19B9",
  },
};
const authorizationTypes = {
  TransferWithAuthorization: [
    { name: "from", type: "address" },
    { name: "to", type: "address" },
    { name: "value", type: "uint256" },
    { name: "validAfter", type: "uint256" },
    { name: "validBefore", type: "uint256" },
    { name: "nonce", type: "bytes32" },
  ],
};
const selected = { amount: requirements.amount };
const circleCalls = [];
const signer = {
  address: walletAddress,
  async signTypedData(params) {
    validateTypedData(params, selected, walletAddress);
    const data = typedDataJson(params);
    circleCalls.push({ walletId, data, memo: "TASK-015 mocked signer" });
    return "0x" + "ab".repeat(65);
  },
};

const payload = await new BatchEvmScheme(signer).createPaymentPayload(2, requirements);
assert.equal(payload.x402Version, 2);
assert.equal(payload.payload.authorization.from.toLowerCase(), walletAddress);
assert.equal(circleCalls.length, 1);
assert.equal(circleCalls[0].walletId, walletId);
const typed = JSON.parse(circleCalls[0].data);
assert.equal(typed.primaryType, "TransferWithAuthorization");
assert.equal(typed.domain.chainId, 5042002);
assert.equal(typed.domain.name, "GatewayWalletBatched");
assert.equal(typed.domain.version, "1");
assert.equal(typed.domain.verifyingContract.toLowerCase(), requirements.extra.verifyingContract.toLowerCase());
assert.deepEqual(typed.types, authorizationTypes);

const beforeMismatch = circleCalls.length;
assert.throws(() => validateTypedData({
  ...typed,
  domain: { ...typed.domain, chainId: 8453 },
}, selected, walletAddress), /wrong Arc EVM chain ID/);
assert.equal(circleCalls.length, beforeMismatch);

assert.throws(() => validateTypedData({
  ...typed,
  message: { ...typed.message, from: "0x3333333333333333333333333333333333333333" },
}, selected, walletAddress), /does not match wallet address/);
assert.equal(circleCalls.length, beforeMismatch);

console.log(JSON.stringify({
  status: "passed",
  circle_signTypedData_wallet_id: circleCalls[0].walletId,
  x402_signer_address: signer.address,
  exact_payload_created: true,
  mismatch_rejected_before_circle_signing: true,
}));
