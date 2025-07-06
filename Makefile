# Makefile for the Agentic Proof-Chaining Framework
# A self-documenting Makefile. Use 'make help' to see available commands.

.DEFAULT_GOAL := help

# --- Primary Commands ---

## Install all project dependencies
.PHONY: install
install:
	@echo "🎵 Installing Node.js and Python dependencies..."
	@npm install --quiet
	@pip3 install -r requirements.txt --quiet
	@echo "✅ Installation complete."

## Conduct the end-to-end performance
.PHONY: conduct
conduct:
	@./conduct.sh

# --- Deployment Commands ---

## Deploy the maximal framework to the Sepolia testnet
.PHONY: deploy-sepolia
deploy-sepolia:
	@echo "🎼 Deploying the maximal framework to Sepolia..."
	@npx hardhat run scripts/deploy_maximal_framework.js --network sepolia

## Deploy the simple verifier to a local devnet
.PHONY: deploy-devnet
deploy-devnet:
	@echo "🎻 Deploying the simple verifier to the local devnet..."
	@npx hardhat run scripts/deploy_devnet.js --network localhost

# --- Cleanup ---

## Remove all build artifacts and generated files
.PHONY: clean
clean:
	@echo "🧹 Cleaning up build artifacts..."
	@rm -rf cache artifacts
	@rm -f kzg.srs
	@rm -f ezkl_workspace/rwkv_simple/proof.json
	@echo "✅ Cleanup complete."

# --- Help ---

## Display this help message
.PHONY: help
help:
	@echo "🎶 Agentic Proof-Chaining Framework - Conductor's Makefile"
	@echo "-----------------------------------------------------------"
	@echo "Usage: make [command]"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'