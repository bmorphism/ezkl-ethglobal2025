// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "./ProductionRWKVVerifier.sol";
import "./ProductionMambaVerifier.sol";
import "./ProductionxLSTMVerifier.sol";

/**
 * @title AgenticOrchestrator
 * @dev Multi-agent coordination and proof-chaining orchestrator
 * Enables complex multi-step reasoning workflows across different neural architectures
 */
contract AgenticOrchestrator {
    // Neural architecture verifiers
    ProductionRWKVVerifier public immutable rwkvVerifier;
    ProductionMambaVerifier public immutable mambaVerifier;
    ProductionxLSTMVerifier public immutable xlstmVerifier;
    
    // Chain ID for receipt generation
    bytes32 private immutable chainId;
    
    // Proof chain management
    struct ProofChain {
        bytes32 chainId;
        address initiator;
        uint256 stepCount;
        uint256 createdAt;
        bool isActive;
        mapping(uint256 => ProofStep) steps;
    }
    
    struct ProofStep {
        Architecture architecture;
        bytes32 proofHash;
        bytes32 previousHash;
        uint256[] publicInputs;
        uint256 timestamp;
        address verifier;
        bool verified;
    }
    
    struct AgentCapability {
        address agent;
        Architecture[] supportedArchitectures;
        uint256 reputationScore;
        uint256 totalVerifications;
        uint256 successfulVerifications;
        bool isActive;
    }
    
    struct DelegationTask {
        bytes32 taskId;
        address requester;
        address assignee;
        Architecture requiredArchitecture;
        bytes32 inputHash;
        bytes32 expectedOutputHash;
        uint256 deadline;
        uint256 stake;
        TaskStatus status;
    }
    
    enum Architecture { RWKV, Mamba, xLSTM }
    enum TaskStatus { Pending, InProgress, Completed, Failed, Disputed }
    
    // State variables
    mapping(bytes32 => ProofChain) public proofChains;
    mapping(address => AgentCapability) public agentCapabilities;
    mapping(bytes32 => DelegationTask) public delegationTasks;
    mapping(address => mapping(Architecture => uint256)) public agentSpecialization;
    
    // Counters
    uint256 public totalChains;
    uint256 public totalAgents;
    uint256 public totalTasks;
    
    // Events
    event ProofChainInitiated(bytes32 indexed chainId, address indexed initiator);
    event ProofStepAdded(bytes32 indexed chainId, uint256 stepIndex, Architecture architecture);
    event ProofChainCompleted(bytes32 indexed chainId, uint256 totalSteps);
    event AgentRegistered(address indexed agent, Architecture[] architectures);
    event TaskDelegated(bytes32 indexed taskId, address indexed requester, address indexed assignee);
    event TaskCompleted(bytes32 indexed taskId, bool successful);
    event ReputationUpdated(address indexed agent, uint256 newScore);
    
    constructor(
        address _rwkvVerifier,
        address _mambaVerifier,
        address _xlstmVerifier
    ) {
        rwkvVerifier = ProductionRWKVVerifier(_rwkvVerifier);
        mambaVerifier = ProductionMambaVerifier(_mambaVerifier);
        xlstmVerifier = ProductionxLSTMVerifier(_xlstmVerifier);
        chainId = keccak256(abi.encodePacked(block.chainid, address(this)));
    }
    
    /**
     * @dev Initialize a new proof chain for multi-step reasoning
     */
    function initiateProofChain() external returns (bytes32) {
        bytes32 newChainId = keccak256(abi.encodePacked(
            chainId,
            msg.sender,
            block.timestamp,
            totalChains
        ));
        
        ProofChain storage chain = proofChains[newChainId];
        chain.chainId = newChainId;
        chain.initiator = msg.sender;
        chain.stepCount = 0;
        chain.createdAt = block.timestamp;
        chain.isActive = true;
        
        totalChains++;
        
        emit ProofChainInitiated(newChainId, msg.sender);
        return newChainId;
    }
    
    /**
     * @dev Add a proof step to an existing chain
     */
    function addProofStep(
        bytes32 _chainId,
        Architecture _architecture,
        bytes calldata _proof,
        uint256[] calldata _publicInputs
    ) external returns (bool) {
        ProofChain storage chain = proofChains[_chainId];
        require(chain.isActive, "Chain not active");
        require(chain.initiator == msg.sender || isAuthorizedAgent(msg.sender, _architecture), "Unauthorized");
        
        // Verify the proof using appropriate verifier
        bool verified = _verifyProof(_architecture, _proof, _publicInputs);
        require(verified, "Proof verification failed");
        
        // Create proof step
        bytes32 proofHash = keccak256(_proof);
        bytes32 previousHash = chain.stepCount > 0 
            ? chain.steps[chain.stepCount - 1].proofHash 
            : bytes32(0);
        
        ProofStep storage step = chain.steps[chain.stepCount];
        step.architecture = _architecture;
        step.proofHash = proofHash;
        step.previousHash = previousHash;
        step.publicInputs = _publicInputs;
        step.timestamp = block.timestamp;
        step.verifier = _getVerifierAddress(_architecture);
        step.verified = true;
        
        chain.stepCount++;
        
        // Update agent reputation if applicable
        if (msg.sender != chain.initiator) {
            _updateAgentReputation(msg.sender, true);
        }
        
        emit ProofStepAdded(_chainId, chain.stepCount - 1, _architecture);
        return true;
    }
    
    /**
     * @dev Complete a proof chain
     */
    function completeProofChain(bytes32 _chainId) external {
        ProofChain storage chain = proofChains[_chainId];
        require(chain.initiator == msg.sender, "Only initiator can complete");
        require(chain.isActive, "Chain not active");
        require(chain.stepCount > 0, "No steps in chain");
        
        chain.isActive = false;
        
        emit ProofChainCompleted(_chainId, chain.stepCount);
    }
    
    /**
     * @dev Register an agent with capabilities
     */
    function registerAgent(Architecture[] calldata _architectures) external {
        require(_architectures.length > 0, "Must specify at least one architecture");
        
        AgentCapability storage capability = agentCapabilities[msg.sender];
        capability.agent = msg.sender;
        capability.supportedArchitectures = _architectures;
        capability.reputationScore = 100; // Starting reputation
        capability.totalVerifications = 0;
        capability.successfulVerifications = 0;
        capability.isActive = true;
        
        // Initialize specialization scores
        for (uint i = 0; i < _architectures.length; i++) {
            agentSpecialization[msg.sender][_architectures[i]] = 50; // Starting specialization
        }
        
        totalAgents++;
        
        emit AgentRegistered(msg.sender, _architectures);
    }
    
    /**
     * @dev Delegate a task to another agent
     */
    function delegateTask(
        address _assignee,
        Architecture _architecture,
        bytes32 _inputHash,
        bytes32 _expectedOutputHash,
        uint256 _deadline
    ) external payable returns (bytes32) {
        require(isAuthorizedAgent(_assignee, _architecture), "Agent not authorized");
        require(_deadline > block.timestamp, "Invalid deadline");
        require(msg.value > 0, "Stake required");
        
        bytes32 taskId = keccak256(abi.encodePacked(
            msg.sender,
            _assignee,
            _architecture,
            _inputHash,
            block.timestamp,
            totalTasks
        ));
        
        DelegationTask storage task = delegationTasks[taskId];
        task.taskId = taskId;
        task.requester = msg.sender;
        task.assignee = _assignee;
        task.requiredArchitecture = _architecture;
        task.inputHash = _inputHash;
        task.expectedOutputHash = _expectedOutputHash;
        task.deadline = _deadline;
        task.stake = msg.value;
        task.status = TaskStatus.Pending;
        
        totalTasks++;
        
        emit TaskDelegated(taskId, msg.sender, _assignee);
        return taskId;
    }
    
    /**
     * @dev Complete a delegated task
     */
    function completeTask(
        bytes32 _taskId,
        bytes calldata _proof,
        uint256[] calldata _publicInputs
    ) external {
        DelegationTask storage task = delegationTasks[_taskId];
        require(task.assignee == msg.sender, "Only assignee can complete");
        require(task.status == TaskStatus.Pending, "Task not pending");
        require(block.timestamp <= task.deadline, "Task expired");
        
        // Verify the proof
        bool verified = _verifyProof(task.requiredArchitecture, _proof, _publicInputs);
        
        if (verified) {
            task.status = TaskStatus.Completed;
            
            // Pay the assignee
            payable(task.assignee).transfer(task.stake);
            
            // Update reputation
            _updateAgentReputation(task.assignee, true);
            
            emit TaskCompleted(_taskId, true);
        } else {
            task.status = TaskStatus.Failed;
            
            // Refund the requester
            payable(task.requester).transfer(task.stake);
            
            // Penalize reputation
            _updateAgentReputation(task.assignee, false);
            
            emit TaskCompleted(_taskId, false);
        }
    }
    
    /**
     * @dev Get proof chain information
     */
    function getProofChain(bytes32 _chainId) external view returns (
        bytes32 proofChainId,
        address initiator,
        uint256 stepCount,
        uint256 createdAt,
        bool isActive
    ) {
        ProofChain storage chain = proofChains[_chainId];
        return (
            chain.chainId,
            chain.initiator,
            chain.stepCount,
            chain.createdAt,
            chain.isActive
        );
    }
    
    /**
     * @dev Get proof step information
     */
    function getProofStep(bytes32 _chainId, uint256 _stepIndex) external view returns (
        Architecture architecture,
        bytes32 proofHash,
        bytes32 previousHash,
        uint256[] memory publicInputs,
        uint256 timestamp,
        address verifier,
        bool verified
    ) {
        ProofStep storage step = proofChains[_chainId].steps[_stepIndex];
        return (
            step.architecture,
            step.proofHash,
            step.previousHash,
            step.publicInputs,
            step.timestamp,
            step.verifier,
            step.verified
        );
    }
    
    /**
     * @dev Get agent capability information
     */
    function getAgentCapability(address _agent) external view returns (
        Architecture[] memory supportedArchitectures,
        uint256 reputationScore,
        uint256 totalVerifications,
        uint256 successfulVerifications,
        bool isActive
    ) {
        AgentCapability storage capability = agentCapabilities[_agent];
        return (
            capability.supportedArchitectures,
            capability.reputationScore,
            capability.totalVerifications,
            capability.successfulVerifications,
            capability.isActive
        );
    }
    
    /**
     * @dev Check if agent is authorized for architecture
     */
    function isAuthorizedAgent(address _agent, Architecture _architecture) public view returns (bool) {
        AgentCapability storage capability = agentCapabilities[_agent];
        if (!capability.isActive) return false;
        
        for (uint i = 0; i < capability.supportedArchitectures.length; i++) {
            if (capability.supportedArchitectures[i] == _architecture) {
                return agentSpecialization[_agent][_architecture] >= 25; // Minimum specialization
            }
        }
        return false;
    }
    
    /**
     * @dev Verify proof using appropriate architecture verifier
     */
    function _verifyProof(
        Architecture _architecture,
        bytes calldata _proof,
        uint256[] calldata _publicInputs
    ) internal returns (bool) {
        if (_architecture == Architecture.RWKV) {
            ProductionRWKVVerifier.Proof memory rwkvProof = _parseRWKVProof(_proof);
            return rwkvVerifier.verifyProof(rwkvProof, _publicInputs);
        } else if (_architecture == Architecture.Mamba) {
            ProductionMambaVerifier.Proof memory mambaProof = _parseMambaProof(_proof);
            return mambaVerifier.verifyProof(mambaProof, _publicInputs);
        } else if (_architecture == Architecture.xLSTM) {
            ProductionxLSTMVerifier.Proof memory xlstmProof = _parseXLSTMProof(_proof);
            return xlstmVerifier.verifyProof(xlstmProof, _publicInputs);
        }
        return false;
    }
    
    /**
     * @dev Parse proof bytes into RWKV proof format
     */
    function _parseRWKVProof(bytes calldata _proof) internal pure returns (ProductionRWKVVerifier.Proof memory) {
        // This is a simplified proof parser - in production this would properly decode
        // the EZKL proof format into the expected struct
        require(_proof.length >= 416, "Proof too short"); // 13 * 32 bytes minimum
        
        ProductionRWKVVerifier.Proof memory proof;
        
        // Parse proof components (simplified - in production would use proper deserialization)
        uint256 offset = 0;
        
        // a: [2]uint256
        proof.a[0] = abi.decode(_proof[offset:offset+32], (uint256));
        offset += 32;
        proof.a[1] = abi.decode(_proof[offset:offset+32], (uint256));
        offset += 32;
        
        // b: [2][2]uint256 
        proof.b[0][0] = abi.decode(_proof[offset:offset+32], (uint256));
        offset += 32;
        proof.b[0][1] = abi.decode(_proof[offset:offset+32], (uint256));
        offset += 32;
        proof.b[1][0] = abi.decode(_proof[offset:offset+32], (uint256));
        offset += 32;
        proof.b[1][1] = abi.decode(_proof[offset:offset+32], (uint256));
        offset += 32;
        
        // c: [2]uint256
        proof.c[0] = abi.decode(_proof[offset:offset+32], (uint256));
        offset += 32;
        proof.c[1] = abi.decode(_proof[offset:offset+32], (uint256));
        offset += 32;
        
        // Remaining fields with fallback values
        if (_proof.length >= offset + 32) {
            proof.z[0] = abi.decode(_proof[offset:offset+32], (uint256));
            offset += 32;
        }
        if (_proof.length >= offset + 32) {
            proof.z[1] = abi.decode(_proof[offset:offset+32], (uint256));
            offset += 32;
        }
        
        // Set remaining fields to mock values for demonstration
        proof.t1[0] = 0x1111111111111111111111111111111111111111111111111111111111111111;
        proof.t1[1] = 0x2222222222222222222222222222222222222222222222222222222222222222;
        proof.t2[0] = 0x3333333333333333333333333333333333333333333333333333333333333333;
        proof.t2[1] = 0x4444444444444444444444444444444444444444444444444444444444444444;
        proof.t3[0] = 0x5555555555555555555555555555555555555555555555555555555555555555;
        proof.t3[1] = 0x6666666666666666666666666666666666666666666666666666666666666666;
        proof.eval_a = 0x7777777777777777777777777777777777777777777777777777777777777777;
        proof.eval_b = 0x8888888888888888888888888888888888888888888888888888888888888888;
        proof.eval_c = 0x9999999999999999999999999999999999999999999999999999999999999999;
        proof.eval_s1 = 0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa;
        proof.eval_s2 = 0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb;
        proof.eval_zw = 0xcccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc;
        
        return proof;
    }
    
    /**
     * @dev Parse proof bytes into Mamba proof format
     */
    function _parseMambaProof(bytes calldata _proof) internal pure returns (ProductionMambaVerifier.Proof memory) {
        require(_proof.length >= 416, "Proof too short");
        
        ProductionMambaVerifier.Proof memory proof;
        uint256 offset = 0;
        
        // Parse same structure but return as Mamba proof type
        proof.a[0] = abi.decode(_proof[offset:offset+32], (uint256));
        offset += 32;
        proof.a[1] = abi.decode(_proof[offset:offset+32], (uint256));
        offset += 32;
        
        proof.b[0][0] = abi.decode(_proof[offset:offset+32], (uint256));
        offset += 32;
        proof.b[0][1] = abi.decode(_proof[offset:offset+32], (uint256));
        offset += 32;
        proof.b[1][0] = abi.decode(_proof[offset:offset+32], (uint256));
        offset += 32;
        proof.b[1][1] = abi.decode(_proof[offset:offset+32], (uint256));
        offset += 32;
        
        proof.c[0] = abi.decode(_proof[offset:offset+32], (uint256));
        offset += 32;
        proof.c[1] = abi.decode(_proof[offset:offset+32], (uint256));
        offset += 32;
        
        if (_proof.length >= offset + 32) {
            proof.z[0] = abi.decode(_proof[offset:offset+32], (uint256));
            offset += 32;
        }
        if (_proof.length >= offset + 32) {
            proof.z[1] = abi.decode(_proof[offset:offset+32], (uint256));
            offset += 32;
        }
        
        // Set remaining fields to mock values
        proof.t1[0] = 0x1111111111111111111111111111111111111111111111111111111111111111;
        proof.t1[1] = 0x2222222222222222222222222222222222222222222222222222222222222222;
        proof.t2[0] = 0x3333333333333333333333333333333333333333333333333333333333333333;
        proof.t2[1] = 0x4444444444444444444444444444444444444444444444444444444444444444;
        proof.t3[0] = 0x5555555555555555555555555555555555555555555555555555555555555555;
        proof.t3[1] = 0x6666666666666666666666666666666666666666666666666666666666666666;
        proof.eval_a = 0x7777777777777777777777777777777777777777777777777777777777777777;
        proof.eval_b = 0x8888888888888888888888888888888888888888888888888888888888888888;
        proof.eval_c = 0x9999999999999999999999999999999999999999999999999999999999999999;
        proof.eval_s1 = 0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa;
        proof.eval_s2 = 0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb;
        proof.eval_zw = 0xcccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc;
        
        return proof;
    }
    
    /**
     * @dev Parse proof bytes into xLSTM proof format
     */
    function _parseXLSTMProof(bytes calldata _proof) internal pure returns (ProductionxLSTMVerifier.Proof memory) {
        require(_proof.length >= 416, "Proof too short");
        
        ProductionxLSTMVerifier.Proof memory proof;
        uint256 offset = 0;
        
        // Parse same structure but return as xLSTM proof type
        proof.a[0] = abi.decode(_proof[offset:offset+32], (uint256));
        offset += 32;
        proof.a[1] = abi.decode(_proof[offset:offset+32], (uint256));
        offset += 32;
        
        proof.b[0][0] = abi.decode(_proof[offset:offset+32], (uint256));
        offset += 32;
        proof.b[0][1] = abi.decode(_proof[offset:offset+32], (uint256));
        offset += 32;
        proof.b[1][0] = abi.decode(_proof[offset:offset+32], (uint256));
        offset += 32;
        proof.b[1][1] = abi.decode(_proof[offset:offset+32], (uint256));
        offset += 32;
        
        proof.c[0] = abi.decode(_proof[offset:offset+32], (uint256));
        offset += 32;
        proof.c[1] = abi.decode(_proof[offset:offset+32], (uint256));
        offset += 32;
        
        if (_proof.length >= offset + 32) {
            proof.z[0] = abi.decode(_proof[offset:offset+32], (uint256));
            offset += 32;
        }
        if (_proof.length >= offset + 32) {
            proof.z[1] = abi.decode(_proof[offset:offset+32], (uint256));
            offset += 32;
        }
        
        // Set remaining fields to mock values
        proof.t1[0] = 0x1111111111111111111111111111111111111111111111111111111111111111;
        proof.t1[1] = 0x2222222222222222222222222222222222222222222222222222222222222222;
        proof.t2[0] = 0x3333333333333333333333333333333333333333333333333333333333333333;
        proof.t2[1] = 0x4444444444444444444444444444444444444444444444444444444444444444;
        proof.t3[0] = 0x5555555555555555555555555555555555555555555555555555555555555555;
        proof.t3[1] = 0x6666666666666666666666666666666666666666666666666666666666666666;
        proof.eval_a = 0x7777777777777777777777777777777777777777777777777777777777777777;
        proof.eval_b = 0x8888888888888888888888888888888888888888888888888888888888888888;
        proof.eval_c = 0x9999999999999999999999999999999999999999999999999999999999999999;
        proof.eval_s1 = 0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa;
        proof.eval_s2 = 0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb;
        proof.eval_zw = 0xcccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc;
        
        return proof;
    }
    
    /**
     * @dev Get verifier contract address for architecture
     */
    function _getVerifierAddress(Architecture _architecture) internal view returns (address) {
        if (_architecture == Architecture.RWKV) {
            return address(rwkvVerifier);
        } else if (_architecture == Architecture.Mamba) {
            return address(mambaVerifier);
        } else if (_architecture == Architecture.xLSTM) {
            return address(xlstmVerifier);
        }
        return address(0);
    }
    
    /**
     * @dev Update agent reputation based on performance
     */
    function _updateAgentReputation(address _agent, bool _successful) internal {
        AgentCapability storage capability = agentCapabilities[_agent];
        capability.totalVerifications++;
        
        if (_successful) {
            capability.successfulVerifications++;
            if (capability.reputationScore < 1000) {
                capability.reputationScore += 1;
            }
        } else {
            if (capability.reputationScore > 0) {
                capability.reputationScore -= 2;
            }
        }
        
        emit ReputationUpdated(_agent, capability.reputationScore);
    }
    
    /**
     * @dev Emergency pause function (owner only)
     */
    function pause() external {
        // Implementation would include owner checks and pause functionality
        // Simplified for this example
    }
}