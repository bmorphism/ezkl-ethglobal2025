// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract AgentRegistry {
    struct EnhancedAgentCapabilities {
        uint8[] supportedArchitectures;
        address[] verifierContracts;
        uint256[] computationCosts;
        bytes32 reputationHash;
        uint256 totalComputations;
        uint256 averageQuality;
        uint256 successRate;
        uint256 averageResponseTime;
        uint256 stakedAmount;
        string[] specializations;
        mapping(uint8 => uint256) architectureExpertise;
        mapping(string => bytes32) certifications;
    }

    struct DelegationContract {
        address delegator;
        address delegate;
        bytes32 taskSpecification;
        uint256 maxCost;
        uint256 deadline;
        uint256 qualityThreshold;
        bytes32 expectedOutputCommitment;
        uint256 reputationRequirement;
        uint8 requiredArchitecture;
        bool isCompleted;
        bytes32 completionReceipt;
    }

    mapping(address => EnhancedAgentCapabilities) public agentRegistry;
    mapping(bytes32 => DelegationContract) public delegationContracts;
    mapping(address => mapping(address => uint256)) public trustScores;

    event AgentRegistered(
        address indexed agent,
        uint8[] architectures,
        uint256 initialStake,
        string[] specializations
    );

    event DelegationCreated(
        address indexed delegator,
        address indexed delegate,
        bytes32 indexed taskId,
        uint256 maxCost,
        uint8 architecture
    );

    event DelegationCompleted(
        address indexed delegator,
        address indexed delegate,
        bytes32 indexed taskId,
        bytes32 completionReceipt,
        uint256 actualCost,
        uint256 qualityScore
    );
}
