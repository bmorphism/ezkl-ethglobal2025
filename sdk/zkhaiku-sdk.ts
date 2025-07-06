/**
 * ZK Haiku NanoGPT SDK - Production Ready Integration Library
 * 
 * Provides seamless integration with deployed ZK verifier contracts
 * for RWKV, Mamba, and xLSTM architectures on Ethereum Sepolia
 */

import { ethers } from 'ethers';

export interface ZKProofData {
    proof: string;
    publicInputs: string[];
    modelType: 'rwkv' | 'mamba' | 'xlstm';
    generatedText?: string;
    metadata?: {
        provingTime: number;
        gasEstimate: number;
        qualityScore?: number;
    };
}

export interface VerificationResult {
    verified: boolean;
    transactionHash: string;
    gasUsed: number;
    blockNumber: number;
    timestamp: number;
    cost: string; // in ETH
}

export interface NetworkConfig {
    rpcUrl: string;
    chainId: number;
    contracts: {
        rwkv: string;
        mamba: string;
        xlstm: string;
    };
}

// Production contract addresses on Sepolia
export const SEPOLIA_CONFIG: NetworkConfig = {
    rpcUrl: 'https://sepolia.infura.io/v3/YOUR_KEY',
    chainId: 11155111,
    contracts: {
        rwkv: '0x52b5e61fA6Ae53BA08B9094eA077820283Dcec01',
        mamba: '0x89dFdcC74Ed05bf2a76eF788b15e5cbC8Ad8C5cD',
        xlstm: '0x52a55dEBE04124376841dF391Ef0e4eF1dd6835B'
    }
};

export class ZKHaikuSDK {
    private provider: ethers.Provider;
    private signer?: ethers.Signer;
    private contracts: { [key: string]: ethers.Contract };
    private config: NetworkConfig;

    constructor(config: NetworkConfig, signerOrProvider: ethers.Signer | ethers.Provider) {
        this.config = config;
        
        if ('provider' in signerOrProvider) {
            this.signer = signerOrProvider;
            this.provider = signerOrProvider.provider!;
        } else {
            this.provider = signerOrProvider;
        }

        // Initialize contract instances
        const verifierABI = [
            "function verifyProof(bytes memory proof, uint256[] memory publicInputs) public view returns (bool)",
            "function submitAndVerify(bytes memory proof, uint256[] memory publicInputs) public returns (bool)",
            "event ProofVerified(address indexed submitter, bool result, uint256 gasUsed)"
        ];

        this.contracts = {
            rwkv: new ethers.Contract(config.contracts.rwkv, verifierABI, signerOrProvider),
            mamba: new ethers.Contract(config.contracts.mamba, verifierABI, signerOrProvider),
            xlstm: new ethers.Contract(config.contracts.xlstm, verifierABI, signerOrProvider)
        };
    }

    /**
     * Verify a ZK proof without submitting to blockchain (view function)
     */
    async verifyProof(proofData: ZKProofData): Promise<boolean> {
        const contract = this.contracts[proofData.modelType];
        if (!contract) {
            throw new Error(`Unsupported model type: ${proofData.modelType}`);
        }

        try {
            const result = await contract.verifyProof(
                proofData.proof,
                proofData.publicInputs
            );
            return result;
        } catch (error) {
            console.error('Proof verification failed:', error);
            return false;
        }
    }

    /**
     * Submit and verify proof on-chain (transaction)
     */
    async submitAndVerify(proofData: ZKProofData): Promise<VerificationResult> {
        if (!this.signer) {
            throw new Error('Signer required for transaction submission');
        }

        const contract = this.contracts[proofData.modelType];
        if (!contract) {
            throw new Error(`Unsupported model type: ${proofData.modelType}`);
        }

        try {
            // Estimate gas first
            const gasEstimate = await contract.submitAndVerify.estimateGas(
                proofData.proof,
                proofData.publicInputs
            );

            // Submit transaction
            const tx = await contract.submitAndVerify(
                proofData.proof,
                proofData.publicInputs,
                { gasLimit: gasEstimate.add(10000) } // Add buffer
            );

            // Wait for confirmation
            const receipt = await tx.wait();
            
            // Parse verification result from events
            const verificationEvent = receipt.events?.find(
                e => e.event === 'ProofVerified'
            );
            
            const verified = verificationEvent?.args?.result || false;
            const gasUsed = receipt.gasUsed.toNumber();
            const cost = ethers.utils.formatEther(receipt.gasUsed.mul(tx.gasPrice || 0));

            return {
                verified,
                transactionHash: receipt.transactionHash,
                gasUsed,
                blockNumber: receipt.blockNumber,
                timestamp: Math.floor(Date.now() / 1000),
                cost
            };

        } catch (error) {
            console.error('Transaction submission failed:', error);
            throw error;
        }
    }

    /**
     * Batch verify multiple proofs efficiently
     */
    async batchVerify(proofs: ZKProofData[]): Promise<boolean[]> {
        const promises = proofs.map(proof => this.verifyProof(proof));
        return Promise.all(promises);
    }

    /**
     * Get gas cost estimates for different operations
     */
    async getGasEstimates(modelType: 'rwkv' | 'mamba' | 'xlstm'): Promise<{
        verification: ethers.BigNumber;
        submission: ethers.BigNumber;
        estimatedCostETH: string;
    }> {
        const contract = this.contracts[modelType];
        
        // Sample proof data for estimation
        const sampleProof = "0x" + "00".repeat(2048); // Placeholder
        const sampleInputs = [1, 2, 3]; // Placeholder
        
        try {
            const verificationGas = await contract.verifyProof.estimateGas(sampleProof, sampleInputs);
            const submissionGas = await contract.submitAndVerify.estimateGas(sampleProof, sampleInputs);
            
            const gasPrice = await this.provider.getGasPrice();
            const estimatedCostETH = ethers.utils.formatEther(submissionGas.mul(gasPrice));
            
            return {
                verification: verificationGas,
                submission: submissionGas,
                estimatedCostETH
            };
        } catch (error) {
            console.error('Gas estimation failed:', error);
            throw error;
        }
    }

    /**
     * Monitor verification events in real-time
     */
    async monitorVerifications(
        modelType: 'rwkv' | 'mamba' | 'xlstm',
        callback: (event: any) => void,
        fromBlock: number = 'latest'
    ): Promise<void> {
        const contract = this.contracts[modelType];
        
        contract.on('ProofVerified', (submitter, result, gasUsed, event) => {
            callback({
                submitter,
                result,
                gasUsed: gasUsed.toNumber(),
                transactionHash: event.transactionHash,
                blockNumber: event.blockNumber,
                modelType
            });
        });
    }

    /**
     * Get verification statistics for a model
     */
    async getVerificationStats(
        modelType: 'rwkv' | 'mamba' | 'xlstm',
        fromBlock: number = 0
    ): Promise<{
        totalVerifications: number;
        successfulVerifications: number;
        averageGasUsed: number;
        uniqueUsers: number;
    }> {
        const contract = this.contracts[modelType];
        
        const filter = contract.filters.ProofVerified();
        const events = await contract.queryFilter(filter, fromBlock);
        
        const totalVerifications = events.length;
        const successfulVerifications = events.filter(e => e.args?.result).length;
        const totalGasUsed = events.reduce((sum, e) => sum + (e.args?.gasUsed?.toNumber() || 0), 0);
        const averageGasUsed = totalVerifications > 0 ? totalGasUsed / totalVerifications : 0;
        const uniqueUsers = new Set(events.map(e => e.args?.submitter)).size;
        
        return {
            totalVerifications,
            successfulVerifications,
            averageGasUsed,
            uniqueUsers
        };
    }

    /**
     * Helper method to create ZK proof data from EZKL output
     */
    static createProofData(
        ezklProof: string,
        ezklPublicInputs: number[],
        modelType: 'rwkv' | 'mamba' | 'xlstm',
        metadata?: any
    ): ZKProofData {
        return {
            proof: ezklProof,
            publicInputs: ezklPublicInputs.map(x => x.toString()),
            modelType,
            metadata
        };
    }
}

// Convenience functions for quick integration
export async function quickVerify(
    proof: string,
    publicInputs: string[],
    modelType: 'rwkv' | 'mamba' | 'xlstm',
    rpcUrl?: string
): Promise<boolean> {
    const config = { ...SEPOLIA_CONFIG };
    if (rpcUrl) config.rpcUrl = rpcUrl;
    
    const provider = new ethers.JsonRpcProvider(config.rpcUrl);
    const sdk = new ZKHaikuSDK(config, provider);
    
    return sdk.verifyProof({
        proof,
        publicInputs,
        modelType
    });
}

export async function quickSubmit(
    proof: string,
    publicInputs: string[],
    modelType: 'rwkv' | 'mamba' | 'xlstm',
    privateKey: string,
    rpcUrl?: string
): Promise<VerificationResult> {
    const config = { ...SEPOLIA_CONFIG };
    if (rpcUrl) config.rpcUrl = rpcUrl;
    
    const provider = new ethers.JsonRpcProvider(config.rpcUrl);
    const signer = new ethers.Wallet(privateKey, provider);
    const sdk = new ZKHaikuSDK(config, signer);
    
    return sdk.submitAndVerify({
        proof,
        publicInputs,
        modelType
    });
}

// Export types and constants
export { NetworkConfig, ZKProofData, VerificationResult };
export const SUPPORTED_MODELS = ['rwkv', 'mamba', 'xlstm'] as const;