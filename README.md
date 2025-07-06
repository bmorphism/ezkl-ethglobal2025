# Agentic Proof-Chaining Framework

This repository contains the smart contracts, agent code, and documentation for a comprehensive, multi-agent proof-chaining framework using EZKL.

## Overview

This project enables verifiable, trustless collaboration between autonomous AI agents through the use of zero-knowledge proofs. It includes:

*   **Solidity Contracts:** Verifiers for RWKV, Mamba, and xLSTM models.
*   **Agent Implementations:** Python scripts for generating proofs.
*   **Deployment Scripts:** Hardhat scripts for deploying to testnets.
*   **Documentation:** Detailed specifications and guides.

## Getting Started

1.  **Install Dependencies:**
    ```bash
    npm install
    pip install -r requirements.txt
    ```

2.  **Configure Environment:**
    *   Create a `.env` file and populate it with your Sepolia RPC URL and private key.

3.  **Deploy Contracts:**
    ```bash
    npx hardhat run scripts/deploy_sepolia.js --network sepolia
    ```

## Directory Structure

*   `contracts/`: Solidity source code.
*   `scripts/`: Deployment and testing scripts.
*   `src/`: Python source code for agents.
*   `ezkl_workspace/`: EZKL models and inputs.
*   `config/`: Deployment addresses and configuration.
*   `docs/`: Project documentation.
