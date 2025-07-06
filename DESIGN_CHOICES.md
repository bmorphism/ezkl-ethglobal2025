# Architectural Design Choices

This document records the key architectural decisions made during the development of the Agentic Proof-Chaining Framework.

## 1. Choice of EZKL for ZKML

**Decision:** Use EZKL as the primary library for generating zero-knowledge proofs of machine learning models.

**Rationale:**

- **Accessibility:** EZKL provides a high-level CLI and Python API that abstracts away much of the complexity of circuit design. This was crucial for rapid prototyping in a hackathon environment.
- **ONNX Compatibility:** Its native support for the ONNX format allows for a clean separation between the machine learning and cryptography domains. Data scientists can work in familiar frameworks (like PyTorch) and export their models without needing to be ZK experts.
- **Solidity Export:** The ability to export a Solidity verifier contract directly from the compiled circuit is a key feature that enables the on-chain verification that is central to this project.

**Trade-offs:**

- EZKL is a high-level tool, which means we have less granular control over the circuit design compared to writing circuits directly in a language like Circom or Halo2. This can lead to less optimized circuits, but the development speed trade-off was deemed acceptable.

## 2. Multi-Contract vs. Monolithic Architecture

**Decision:** Implement separate verifier contracts for each neural architecture (RWKV, Mamba, xLSTM) and separate contracts for coordination (`AgentRegistry`, `ProofChainOrchestrator`).

**Rationale:**

- **Modularity and Upgradability:** A multi-contract architecture allows for each component to be upgraded independently. If a more efficient verifier for the Mamba architecture is developed, it can be deployed without affecting the other verifiers.
- **Gas Efficiency:** Deploying separate, smaller contracts is generally more gas-efficient than deploying a single, massive monolithic contract.
- **Clarity of Purpose:** Each contract has a single, well-defined responsibility, which makes the system easier to understand, audit, and extend.

**Trade-offs:**

- This approach introduces some complexity in the form of inter-contract communication. However, this is managed by the `ProofChainOrchestrator`, which acts as a central hub.

## 3. On-Chain vs. Off-Chain Logic

**Decision:** Keep the on-chain logic strictly limited to verification and coordination. All heavy computation (model inference, proof generation) is performed off-chain.

**Rationale:**

- **Cost and Scalability:** Performing ML inference or ZK proof generation on-chain would be prohibitively expensive and slow. The blockchain is used as a trust layer, not a computation layer.
- **Flexibility:** Off-chain agents can be written in any language and can leverage specialized hardware (like GPUs) for performance. The on-chain contracts only need to verify the results.

**Trade-offs:**

- This architecture requires a robust bridge between the off-chain and on-chain worlds. The `resonate.js` and deployment scripts serve this purpose, but in a full production system, a more sophisticated relayer or oracle system might be needed.
