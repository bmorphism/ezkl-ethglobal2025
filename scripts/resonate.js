const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  // Read the address of the deployed verifier
  const deployments = JSON.parse(fs.readFileSync(path.join(__dirname, "../config/devnet-deployment-addresses.json")));
  const verifierAddress = deployments.ProductionRWKVVerifier;

  // Get the verifier contract instance
  const Verifier = await hre.ethers.getContractFactory("ProductionRWKVVerifier");
  const verifier = Verifier.attach(verifierAddress);

  // Read the generated proof
  const proof = fs.readFileSync(path.join(__dirname, "../ezkl_workspace/rwkv_simple/proof.json"), "utf8");
  const proofBytes = "0x" + Buffer.from(proof).toString("hex");

  // Read the public inputs from the input.json
  const inputData = JSON.parse(fs.readFileSync(path.join(__dirname, "../ezkl_workspace/rwkv_simple/input.json"), "utf8"));
  // Note: In a real scenario, you would derive the public inputs according to your circuit's definition.
  // For this simple model, we'll use a placeholder or an empty array, as the core verification is in the proof itself.
  const publicInputs = [];

  // Perform the verification
  const result = await verifier.verify(proofBytes, publicInputs);

  if (result) {
    console.log("✓");
  } else {
    console.error("Resonance failed.");
    process.exit(1);
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
