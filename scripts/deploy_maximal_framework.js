const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("Deploying the Maximal Agentic Proof-Chaining Framework...");

  // Deploy Verifiers
  const rwkvVerifier = await hre.ethers.deployContract(
    "ProductionRWKVVerifier",
  );
  await rwkvVerifier.waitForDeployment();
  console.log(`  -> ProductionRWKVVerifier deployed to ${rwkvVerifier.target}`);

  const mambaVerifier = await hre.ethers.deployContract(
    "ProductionMambaVerifier",
  );
  await mambaVerifier.waitForDeployment();
  console.log(
    `  -> ProductionMambaVerifier deployed to ${mambaVerifier.target}`,
  );

  const xlstmVerifier = await hre.ethers.deployContract(
    "ProductionxLSTMVerifier",
  );
  await xlstmVerifier.waitForDeployment();
  console.log(
    `  -> ProductionxLSTMVerifier deployed to ${xlstmVerifier.target}`,
  );

  // Deploy Coordination Contracts
  const agentRegistry = await hre.ethers.deployContract("AgentRegistry");
  await agentRegistry.waitForDeployment();
  console.log(`  -> AgentRegistry deployed to ${agentRegistry.target}`);

  const proofChainOrchestrator = await hre.ethers.deployContract(
    "ProofChainOrchestrator",
  );
  await proofChainOrchestrator.waitForDeployment();
  console.log(
    `  -> ProofChainOrchestrator deployed to ${proofChainOrchestrator.target}`,
  );

  // Save the addresses
  const addresses = {
    ProductionRWKVVerifier: rwkvVerifier.target,
    ProductionMambaVerifier: mambaVerifier.target,
    ProductionxLSTMVerifier: xlstmVerifier.target,
    AgentRegistry: agentRegistry.target,
    ProofChainOrchestrator: proofChainOrchestrator.target,
  };

  fs.writeFileSync(
    path.join(__dirname, "../config/maximal-deployment-addresses.json"),
    JSON.stringify(addresses, null, 2),
  );

  console.log(
    "\nMaximal framework deployment complete. Addresses saved to config/maximal-deployment-addresses.json",
  );
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
