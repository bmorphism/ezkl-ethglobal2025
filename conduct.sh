#!/bin/bash

# A silent conductor for the proof-of-resonance.

# Exit on any error
set -e

# Suppress all output
exec > /dev/null 2>&1

# 1. The Composition: Create the model and input data
python3 src/simple_ezkl_models.py

# 2. The Score: Generate the EZKL settings
ezkl gen-settings -M ezkl_workspace/rwkv_simple/model.onnx --settings-path ezkl_workspace/rwkv_simple/settings.json

# 3. The Arrangement: Compile the circuit
ezkl compile-circuit -M ezkl_workspace/rwkv_simple/model.onnx --compiled-circuit ezkl_workspace/rwkv_simple/model.compiled --settings-path ezkl_workspace/rwkv_simple/settings.json

# 4. The Tuning: Generate the Structured Reference String
ezkl gen-srs --srs-path kzg.srs --logrows 16

# 5. The Rehearsal: Generate the proving and verification keys
ezkl setup -M ezkl_workspace/rwkv_simple/model.compiled --srs-path kzg.srs --vk-path ezkl_workspace/rwkv_simple/vk.key --pk-path ezkl_workspace/rwkv_simple/pk.key

# 6. The Performance: Generate the proof
ezkl prove -M ezkl_workspace/rwkv_simple/model.compiled --witness ezkl_workspace/rwkv_simple/witness.json -D ezkl_workspace/rwkv_simple/input.json --proof-path ezkl_workspace/rwkv_simple/proof.json --pk-path ezkl_workspace/rwkv_simple/pk.key --srs-path kzg.srs

# 7. The Resonance: Verify the proof on-chain
npx hardhat node > /dev/null 2>&1 &
NODE_PID=$!
sleep 5 # Wait for the node to start
npx hardhat run scripts/deploy_devnet.js --network localhost > /dev/null 2>&1
exec > /dev/tty 2>&1 # Restore output for the final confirmation
npx hardhat run scripts/resonate.js --network localhost

# Cleanup
kill $NODE_PID
rm kzg.srs
