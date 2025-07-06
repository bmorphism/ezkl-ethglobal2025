# Makefile for the Agentic Proof-Chaining Framework

# --- Primary Commands ---

.PHONY: all
all: install

# Install all dependencies
.PHONY: install
install:
	@echo "Installing Node.js and Python dependencies..."
	@npm install
	@pip3 install -r requirements.txt
	@echo "Installation complete."

# Conduct the end-to-end performance
.PHONY: conduct
conduct:
	@./conduct.sh

# --- Deployment Commands ---

# Deploy the maximal framework to Sepolia testnet
.PHONY: deploy-sepolia
deploy-sepolia:
	@echo "Deploying the maximal framework to Sepolia..."
	@npx hardhat run scripts/deploy_maximal_framework.js --network sepolia

# Deploy the simple verifier to the local devnet
.PHONY: deploy-devnet
deploy-devnet:
	@echo "Deploying the simple verifier to the local devnet..."
	@npx hardhat run scripts/deploy_devnet.js --network localhost

# --- Cleanup ---

.PHONY: clean
clean:
	@echo "Cleaning up build artifacts..."
	@rm -rf cache artifacts
	@rm -f kzg.srs
	@rm -f ezkl_workspace/rwkv_simple/proof.json
	@echo "Cleanup complete."

# --- Help ---

.PHONY: help
help:
	@echo "Available commands:"
	@echo "  install         - Install all project dependencies"
	@echo "  conduct         - Run the end-to-end proof-of-resonance demo"
	@echo "  deploy-sepolia  - Deploy the maximal framework to the Sepolia testnet"
	@echo "  deploy-devnet   - Deploy the simple verifier to a local devnet"
	@echo "  clean           - Remove all build artifacts and generated files"
