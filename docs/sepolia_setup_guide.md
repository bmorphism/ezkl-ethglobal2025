# Sepolia Testnet Setup Guide

## 🚀 Quick Start Deployment

### Step 1: Get Sepolia ETH

```bash
# Visit any of these faucets to get free Sepolia ETH:
# 1. https://sepoliafaucet.com/ (recommended)
# 2. https://faucet.sepolia.dev/
# 3. https://www.alchemy.com/faucets/ethereum-sepolia

# You'll need:
# - MetaMask or similar wallet
# - At least 0.01 ETH for deployment (usually get 0.1-0.5 ETH from faucets)
```

### Step 2: Set Up Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your details:
# PRIVATE_KEY=your_wallet_private_key (without 0x)
# SEPOLIA_URL=https://eth-sepolia.g.alchemy.com/v2/your_api_key
# ETHERSCAN_API_KEY=your_etherscan_api_key (optional, for verification)
```

### Step 3: Deploy to Sepolia

```bash
# Install dependencies if not already done
npm install

# Compile contracts
npx hardhat compile

# Deploy to Sepolia testnet
npx hardhat run deploy_sepolia.js --network sepolia
```

## 🔧 Detailed Setup Instructions

### A. Wallet Setup

1. **Export Private Key** from MetaMask:
   - Open MetaMask → Account Details → Export Private Key
   - **⚠️ SECURITY WARNING**: Never share this key or use it for mainnet funds!

2. **Get Testnet ETH**:
   - Visit https://sepoliafaucet.com/
   - Connect your wallet or enter your address
   - Request 0.5 ETH (usually takes 1-2 minutes)

### B. RPC Provider Setup

**Option 1: Alchemy (Recommended)**

```bash
# 1. Sign up at https://alchemy.com/
# 2. Create new app → Ethereum → Sepolia
# 3. Copy the HTTP URL
SEPOLIA_URL=https://eth-sepolia.g.alchemy.com/v2/YOUR_API_KEY
```

**Option 2: Infura**

```bash
# 1. Sign up at https://infura.io/
# 2. Create new project → Ethereum
# 3. Use Sepolia endpoint
SEPOLIA_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID
```

**Option 3: Public RPC (No signup required)**

```bash
SEPOLIA_URL=https://rpc.sepolia.org
```

### C. Etherscan Setup (Optional but Recommended)

1. Sign up at https://etherscan.io/apis
2. Generate free API key
3. Add to .env:

```bash
ETHERSCAN_API_KEY=YOUR_API_KEY
```

## 📋 Environment Variables Checklist

Create `.env` file with these variables:

```bash
# ✅ Required for deployment
PRIVATE_KEY=your_private_key_here

# ✅ Required for Sepolia connection
SEPOLIA_URL=your_rpc_url_here

# 🔍 Optional for contract verification
ETHERSCAN_API_KEY=your_etherscan_key

# 📊 Optional for gas reporting
REPORT_GAS=true
```

## 🎯 Pre-Deployment Checklist

- [ ] Wallet has at least 0.01 ETH on Sepolia
- [ ] `.env` file created with correct values
- [ ] Dependencies installed (`npm install`)
- [ ] Contracts compiled (`npx hardhat compile`)
- [ ] Network connectivity confirmed

## ⚡ One-Command Deployment

Once setup is complete:

```bash
npx hardhat run deploy_sepolia.js --network sepolia
```

Expected output:

```
🚀 Starting Sepolia Testnet Deployment
=====================================
📡 Network: sepolia
🔗 Chain ID: 11155111
👤 Deployer: 0x...
💰 Balance: 0.5 ETH

🏗️ Deploying Contracts
======================

📝 Deploying ProductionRWKVVerifier...
✅ ProductionRWKVVerifier deployed!
   📍 Address: 0x...
   ⛽ Gas used: 2,156,789
   💸 Cost: 0.00043 ETH
   🔗 Tx hash: 0x...

[Similar output for Mamba and xLSTM verifiers]

🎉 ALL CONTRACTS DEPLOYED SUCCESSFULLY!

📍 Contract Addresses:
ProductionRWKVVerifier: 0x...
ProductionMambaVerifier: 0x...
ProductionxLSTMVerifier: 0x...
```

## 🔍 Post-Deployment Verification

Verify contracts on Etherscan (optional but recommended):

```bash
# Commands will be provided by deployment script
npx hardhat verify --network sepolia 0xCONTRACT_ADDRESS
```

## 📊 Expected Costs

- **Deployment**: ~0.001-0.003 ETH total (~$2-6 USD)
- **Each Verification**: ~0.0001 ETH (~$0.20 USD)
- **Total Monthly Testing**: <0.01 ETH (<$20 USD)

## 🆘 Troubleshooting

### Common Issues:

**❌ "Insufficient funds"**

```
Solution: Get more ETH from faucet
Minimum needed: 0.01 ETH
```

**❌ "Invalid nonce"**

```
Solution: Reset MetaMask account or wait for network sync
```

**❌ "Network not found"**

```
Solution: Check SEPOLIA_URL in .env file
Test with: curl -X POST $SEPOLIA_URL -H "Content-Type: application/json" -d '{"method":"eth_blockNumber","params":[],"id":1,"jsonrpc":"2.0"}'
```

**❌ "Contract size too large"**

```
This shouldn't happen with our contracts (~12.5KB each)
If it does, optimization is already enabled in hardhat.config.js
```

## 🎯 Success Indicators

✅ All 3 contracts deployed successfully  
✅ Gas usage ~2M per contract  
✅ Total cost under 0.003 ETH  
✅ Contracts show up on Sepolia Etherscan  
✅ Ready for testing phase

Your contracts will be live on Ethereum Sepolia testnet and publicly accessible!
