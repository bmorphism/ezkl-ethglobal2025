# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-07-05

### Added
- Initial project setup with Hardhat and Python.
- Core ZK verifier contracts for RWKV, Mamba, and xLSTM architectures.
- Deployment scripts for Sepolia testnet and local devnet.
- Agent-side Python source for model creation and proof generation.
- EZKL workspace with test models and input data.
- `MAXIMAL_AGENTIC_PROOF_CHAINING_FRAMEWORK.md` as the primary architectural document.
- Sepolia deployment results and setup guides.
- Simple model integration test.
- Silent, end-to-end `conduct.sh` script for proof-of-resonance.
- `AgentRegistry` and `ProofChainOrchestrator` contracts for multi-agent coordination.
- `deploy_maximal_framework.js` script for the full framework.
- `PHILOSOPHY.md`, `spec.txt`, and `ROADMAP.md` to provide deeper project context.
- `LICENSE`, `DESIGN_CHOICES.md`, and `Dockerfile` for governance and reproducibility.

### Changed
- Updated `README.md` to reflect the maximal framework architecture with new diagrams.
- Reorganized contract files into `verifiers` and `coordination` subdirectories.
