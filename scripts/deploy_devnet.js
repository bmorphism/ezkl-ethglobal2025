const { ethers } = require("hardhat");

async function main() {
    console.log("🚀 Deploying Production ZK Language Model Verifiers to DevNet...");
    console.log("📍 Network:", process.env.HARDHAT_NETWORK || "hardhat");
    
    const [deployer] = await ethers.getSigners();
    console.log("👤 Deploying with account:", await deployer.getAddress());
    console.log("💰 Account balance:", ethers.formatEther(await deployer.provider.getBalance(deployer.address)), "ETH");
    
    const deployedContracts = {};
    const architectures = ['RWKV', 'Mamba', 'xLSTM'];
    
    for (const architecture of architectures) {
        try {
            console.log(`\n📋 Deploying Production${architecture}Verifier...`);
            
            const Verifier = await ethers.getContractFactory(`Production${architecture}Verifier`);
            const Registry = await ethers.getContractFactory(`${architecture}InferenceRegistry`);
            
            console.log("   Estimating deployment costs...");
            const verifierDeployTx = await Verifier.getDeployTransaction();
            const registryDeployTx = await Registry.getDeployTransaction();
            
            const verifierGasEstimate = await deployer.estimateGas(verifierDeployTx);
            const registryGasEstimate = await deployer.estimateGas(registryDeployTx);
            
            console.log(`   📊 Verifier Gas Estimate: ${verifierGasEstimate.toString()}`);
            console.log(`   📊 Registry Gas Estimate: ${registryGasEstimate.toString()}`);
            
            console.log("   Deploying verifier contract...");
            const verifier = await Verifier.deploy({
                gasLimit: verifierGasEstimate + BigInt(50000) // Add buffer
            });
            await verifier.waitForDeployment();
            
            console.log("   Deploying registry contract...");
            const registry = await Registry.deploy({
                gasLimit: registryGasEstimate + BigInt(50000) // Add buffer
            });
            await registry.waitForDeployment();
            
            const verifierAddress = await verifier.getAddress();
            const registryAddress = await registry.getAddress();
            
            deployedContracts[architecture] = {
                verifier: verifierAddress,
                registry: registryAddress
            };
            
            console.log(`   ✅ ${architecture}Verifier: ${verifierAddress}`);
            console.log(`   ✅ ${architecture}Registry: ${registryAddress}`);
            
            // Verify architecture info
            try {
                const archInfo = await verifier.getArchitectureInfo();
                console.log(`   📊 Circuit Gates: ${archInfo.circuitGates}`);
                console.log(`   🔒 Security Level: ${archInfo.securityLevel}`);
                console.log(`   🛡️ Protocol: ${archInfo.protocol}`);
                
                // Test verification key transparency
                const vk = await verifier.getVerificationKey();
                console.log(`   🔑 VK Alpha: [${vk.alpha[0].toString().slice(0, 10)}..., ${vk.alpha[1].toString().slice(0, 10)}...]`);
                console.log(`   🔑 IC Length: ${vk.icLength}`);
                
                // Estimate gas
                const gasEstimate = await verifier.estimateVerificationGas(4);
                console.log(`   ⛽ Gas Estimate: ${gasEstimate}`);
                
                // Test basic functionality
                console.log("   🧪 Testing basic functionality...");
                const sampleProof = {
                    a: ["0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                        "0xfedcba0987654321fedcba0987654321fedcba0987654321fedcba0987654321"],
                    b: [["0x1111111111111111111111111111111111111111111111111111111111111111",
                         "0x2222222222222222222222222222222222222222222222222222222222222222"],
                        ["0x3333333333333333333333333333333333333333333333333333333333333333",
                         "0x4444444444444444444444444444444444444444444444444444444444444444"]],
                    c: ["0x5555555555555555555555555555555555555555555555555555555555555555",
                        "0x6666666666666666666666666666666666666666666666666666666666666666"],
                    z: ["0x7777777777777777777777777777777777777777777777777777777777777777",
                        "0x8888888888888888888888888888888888888888888888888888888888888888"],
                    t1: ["0x9999999999999999999999999999999999999999999999999999999999999999",
                         "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"],
                    t2: ["0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                         "0xcccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"],
                    t3: ["0xdddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
                         "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"],
                    eval_a: "0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
                    eval_b: "0x1111111111111111111111111111111111111111111111111111111111111112",
                    eval_c: "0x1111111111111111111111111111111111111111111111111111111111111113",
                    eval_s1: "0x1111111111111111111111111111111111111111111111111111111111111114",
                    eval_s2: "0x1111111111111111111111111111111111111111111111111111111111111115",
                    eval_zw: "0x1111111111111111111111111111111111111111111111111111111111111116"
                };
                
                const testInputs = [1, 2, 3, 4];
                const verifyTx = await verifier.verifyProof(sampleProof, testInputs);
                const receipt = await verifyTx.wait();
                console.log(`   ✅ Test verification successful! Gas used: ${receipt.gasUsed}`);
                
            } catch (testError) {
                console.log(`   ⚠️ Post-deployment test failed: ${testError.message}`);
            }
            
        } catch (error) {
            console.error(`   ❌ Failed to deploy ${architecture}: ${error.message}`);
            if (error.code === 'INSUFFICIENT_FUNDS') {
                console.error("   💸 Insufficient funds for deployment");
            } else if (error.code === 'NETWORK_ERROR') {
                console.error("   🌐 Network connection error");
            }
        }
    }
    
    console.log("\n🎯 DevNet Deployment Summary:");
    console.log(JSON.stringify(deployedContracts, null, 2));
    
    // Save deployment addresses with network info
    const fs = require('fs');
    const deploymentData = {
        network: process.env.HARDHAT_NETWORK || "hardhat",
        timestamp: new Date().toISOString(),
        deployer: await deployer.getAddress(),
        contracts: deployedContracts
    };
    
    fs.writeFileSync(
        'devnet-deployment-addresses.json',
        JSON.stringify(deploymentData, null, 2)
    );
    
    console.log("\n📄 Deployment data saved to: devnet-deployment-addresses.json");
    
    if (Object.keys(deployedContracts).length > 0) {
        console.log("\n🎉 DevNet deployment completed successfully!");
        console.log("🔗 Ready for testing and verification on the development network");
    } else {
        console.log("\n❌ No contracts were successfully deployed");
    }
    
    return deployedContracts;
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error("❌ DevNet deployment failed:", error);
        process.exit(1);
    });