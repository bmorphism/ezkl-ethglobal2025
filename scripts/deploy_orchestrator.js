const { ethers } = require("hardhat");
const fs = require('fs');

async function main() {
    console.log("🚀 Deploying Agentic Orchestrator...");
    console.log("=" * 50);
    
    const [deployer] = await ethers.getSigners();
    console.log(`👤 Deployer: ${await deployer.getAddress()}`);
    console.log(`💰 Balance: ${ethers.formatEther(await deployer.provider.getBalance(deployer.address))} ETH`);
    
    // Load existing verifier addresses
    let verifierAddresses;
    try {
        const deploymentData = JSON.parse(fs.readFileSync('fresh-devnet-deployment.json', 'utf8'));
        verifierAddresses = {
            rwkv: deploymentData.contracts.RWKV.verifier,
            mamba: deploymentData.contracts.Mamba.verifier,
            xlstm: deploymentData.contracts.xLSTM.verifier
        };
        console.log("📋 Using existing verifier addresses:");
        console.log(`   RWKV: ${verifierAddresses.rwkv}`);
        console.log(`   Mamba: ${verifierAddresses.mamba}`);
        console.log(`   xLSTM: ${verifierAddresses.xlstm}`);
    } catch (error) {
        console.error("❌ Could not load verifier addresses. Please deploy verifiers first.");
        process.exit(1);
    }
    
    // Deploy AgenticOrchestrator
    console.log("\n🏗️ Deploying AgenticOrchestrator...");
    
    const AgenticOrchestrator = await ethers.getContractFactory("AgenticOrchestrator");
    
    console.log("   📦 Compiling contract...");
    const orchestrator = await AgenticOrchestrator.deploy(
        verifierAddresses.rwkv,
        verifierAddresses.mamba,
        verifierAddresses.xlstm
    );
    
    console.log("   ⏳ Waiting for deployment...");
    await orchestrator.waitForDeployment();
    
    const orchestratorAddress = await orchestrator.getAddress();
    console.log(`   ✅ AgenticOrchestrator deployed at: ${orchestratorAddress}`);
    
    // Get deployment transaction details
    const deployTx = orchestrator.deploymentTransaction();
    const receipt = await deployTx.wait();
    
    console.log(`   ⛽ Gas used: ${receipt.gasUsed}`);
    console.log(`   💰 Deploy cost: ${ethers.formatEther(receipt.gasUsed * deployTx.gasPrice)} ETH`);
    
    // Test basic functionality
    console.log("\n🧪 Testing Basic Functionality...");
    
    try {
        // Test agent registration
        console.log("   📝 Testing agent registration...");
        const registerTx = await orchestrator.registerAgent([0, 1, 2]); // All three architectures
        await registerTx.wait();
        console.log("   ✅ Agent registration successful");
        
        // Test proof chain initiation
        console.log("   🔗 Testing proof chain initiation...");
        const chainTx = await orchestrator.initiateProofChain();
        const chainReceipt = await chainTx.wait();
        
        // Extract chain ID from events
        const chainEvent = chainReceipt.logs.find(log => {
            try {
                const parsed = orchestrator.interface.parseLog(log);
                return parsed.name === 'ProofChainInitiated';
            } catch {
                return false;
            }
        });
        
        if (chainEvent) {
            const parsedEvent = orchestrator.interface.parseLog(chainEvent);
            const chainId = parsedEvent.args.chainId;
            console.log(`   ✅ Proof chain initiated: ${chainId}`);
            
            // Get chain information
            const chainInfo = await orchestrator.getProofChain(chainId);
            console.log(`   📊 Chain info: initiator=${chainInfo.initiator}, steps=${chainInfo.stepCount}`);
        }
        
        // Test agent capability query
        console.log("   🤖 Testing agent capability query...");
        const capability = await orchestrator.getAgentCapability(await deployer.getAddress());
        console.log(`   📊 Agent capability: reputation=${capability.reputationScore}, active=${capability.isActive}`);
        
        console.log("   ✅ All basic tests passed!");
        
    } catch (error) {
        console.log(`   ⚠️ Testing warning: ${error.message}`);
    }
    
    // Save deployment information
    const deploymentInfo = {
        timestamp: new Date().toISOString(),
        network: "hardhat-local",
        deployer: await deployer.getAddress(),
        contracts: {
            AgenticOrchestrator: {
                address: orchestratorAddress,
                gasUsed: receipt.gasUsed.toString(),
                txHash: deployTx.hash
            }
        },
        verifiers: verifierAddresses,
        summary: {
            totalContracts: 1,
            totalGasUsed: receipt.gasUsed.toString(),
            totalCost: ethers.formatEther(receipt.gasUsed * deployTx.gasPrice)
        }
    };
    
    // Write to file
    fs.writeFileSync('orchestrator-deployment.json', JSON.stringify(deploymentInfo, null, 2));
    console.log("\n📄 Deployment info saved to: orchestrator-deployment.json");
    
    // Display integration example
    console.log("\n🔗 Integration Example:");
    console.log("```javascript");
    console.log("// Connect to AgenticOrchestrator");
    console.log(`const orchestrator = await ethers.getContractAt("AgenticOrchestrator", "${orchestratorAddress}");`);
    console.log("");
    console.log("// Register as an agent");
    console.log("await orchestrator.registerAgent([0, 1, 2]); // Support all architectures");
    console.log("");
    console.log("// Start a proof chain");
    console.log("const chainId = await orchestrator.initiateProofChain();");
    console.log("");
    console.log("// Add proof steps");
    console.log("await orchestrator.addProofStep(chainId, 0, proofData, publicInputs);");
    console.log("```");
    
    console.log("\n🎯 Deployment Summary:");
    console.log(`   🏗️ AgenticOrchestrator: ${orchestratorAddress}`);
    console.log(`   ⛽ Total Gas: ${receipt.gasUsed}`);
    console.log(`   💰 Total Cost: ${ethers.formatEther(receipt.gasUsed * deployTx.gasPrice)} ETH`);
    console.log(`   🔗 Connected Verifiers: 3 (RWKV, Mamba, xLSTM)`);
    
    console.log("\n🚀 Multi-Agent Infrastructure Ready!");
    console.log("The orchestrator enables:");
    console.log("  • 🔗 Proof chaining across architectures");
    console.log("  • 🤖 Agent registration and reputation");
    console.log("  • 📋 Task delegation with staking");
    console.log("  • 🏆 Trustless collaboration");
    
    return {
        orchestrator: orchestratorAddress,
        deployer: await deployer.getAddress(),
        gasUsed: receipt.gasUsed.toString()
    };
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error("❌ Deployment failed:", error);
        process.exit(1);
    });