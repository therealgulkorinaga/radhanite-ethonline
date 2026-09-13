#!/usr/bin/env node
/**
 * Minimal Arc Testnet seller derived from Circle's official x402 batching sample.
 * **Implementation agent: Manus.**
 */

import express from "express";
import { createGatewayMiddleware } from "@circle-fin/x402-batching/server";

const app = express();
const port = Number(process.env.Radhanite_ARC_SELLER_PORT ?? 3000);
const sellerAddress = process.env.CIRCLE_ARC_SELLER_ADDRESS;
if (!sellerAddress) {
  throw new Error("CIRCLE_ARC_SELLER_ADDRESS is required to run the Arc demo seller.");
}

const gateway = createGatewayMiddleware({
  sellerAddress,
  networks: ["eip155:5042002"],
  facilitatorUrl: "https://gateway-api-testnet.circle.com",
});

app.get("/premium/quote", gateway.require("$0.001"), (request, response) => {
  response.json({
    capability: "arc-demo-quote",
    result: "Circle Arc Testnet x402 demo result",
    outcome: "positive_market_signal",
    requestId: request.headers["x-request-id"] ?? null,
  });
});

app.listen(port, "0.0.0.0", () => {
  console.log(`Arc demo seller listening on http://127.0.0.1:${port}/premium/quote`);
});
