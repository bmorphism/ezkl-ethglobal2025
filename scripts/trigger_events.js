const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("Triggering on-chain event on Sepolia testnet...");

  // Get the wallet from the private key
  const privateKey = process.env.PRIVATE_KEY;
  if (!privateKey) {
    throw new Error("Please set your PRIVATE_KEY in a .env file");
  }
  const wallet = new hre.ethers.Wallet(privateKey, hre.ethers.provider);

  // Get the verifier contract instance
  const deployments = JSON.parse(fs.readFileSync(path.join(__dirname, "../config/sepolia-addresses.json")));
  const verifierAddress = deployments.contracts.ProductionRWKVVerifier;
  const Verifier = await hre.ethers.getContractFactory("ProductionRWKVVerifier");
  const verifier = Verifier.attach(verifierAddress).connect(wallet);

  // Simulate a proof and public inputs
  const proof = {
    a: ["0x0", "0x0"],
    b: [["0x0", "0x0"], ["0x0", "0x0"]],
    c: ["0x0", "0x0"],
    z: ["0x0", "0x0"],
    t1: ["0x0", "0x0"],
    t2: ["0x0", "0x0"],
    t3: ["0x0", "0x0"],
    eval_a: "0x0",
    eval_b: "0x0",
    eval_c: "0x0",
    eval_s1: "0x0",
    eval_s2: "0x0",
    eval_zw: "0x0",
  };
  const publicInputs = ["0x0", "0x0", "0x0", "0x0"];
  const prompt = "What is the meaning of life?";
  const continuation = "42";

  // Trigger the on-chain event
  try {
    const [architecture, circuitGates, securityLevel, protocol] = await verifier.getArchitectureInfo();
    console.log("\n✅ Successfully connected to the on-chain contract!");
    console.log("Architecture:", architecture);
    console.log("Circuit Gates:", circuitGates.toString());
    console.log("Security Level:", securityLevel.toString());
    console.log("Protocol:", protocol);
  } catch (error) {
    console.error("\n❌ Failed to connect to the on-chain contract.");
    console.error(error);
    process.exit(1);
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});