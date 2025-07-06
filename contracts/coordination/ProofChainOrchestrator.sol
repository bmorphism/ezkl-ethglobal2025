// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract ProofChainOrchestrator {
    enum OperadType {
        SEQUENTIAL,
        PARALLEL,
        HIERARCHICAL,
        PIPELINE,
        TREE,
        DAG
    }

    struct OperadSpecification {
        OperadType operadType;
        address[] participantAgents;
        uint8[] requiredArchitectures;
        bytes32[] taskDecomposition;
        uint256[] qualityThresholds;
        uint256[] costBudgets;
        uint256 totalDeadline;
        bytes32 expectedFinalOutput;
        mapping(uint => uint[]) dependencies;
    }

    struct ExecutionState {
        bytes32 operadId;
        OperadSpecification spec;
        mapping(uint => bytes32) stepReceipts;
        mapping(uint => bool) stepCompleted;
        uint256 currentStep;
        uint256 totalStepsCompleted;
        bool isCompleted;
        bytes32 finalReceipt;
        uint256 totalCost;
        uint256 totalQuality;
    }

    mapping(bytes32 => ExecutionState) public operadExecutions;
    mapping(address => bytes32[]) public agentOperads;

    event OperadInitiated(
        bytes32 indexed operadId,
        OperadType operadType,
        address[] participants,
        uint256 totalBudget
    );

    event OperadStepCompleted(
        bytes32 indexed operadId,
        uint256 indexed stepNumber,
        address indexed completingAgent,
        bytes32 stepReceipt,
        uint256 stepCost,
        uint256 stepQuality
    );

    event OperadCompleted(
        bytes32 indexed operadId,
        bytes32 finalReceipt,
        uint256 totalCost,
        uint256 averageQuality,
        uint256 executionTime
    );
}
