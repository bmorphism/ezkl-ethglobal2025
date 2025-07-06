#!/bin/bash

# The Conductor's Baton

# --- Animation Functions ---
# These functions create the visual performance of the orchestration.

# Clears the screen and sets up the stage
function setup_stage() {
    clear
    echo "The Conductor's Score"
    echo "---------------------"
    echo
    echo "Instruments tuning..."
    sleep 1
}

# Displays a step in the orchestration with a visual cue
function conduct_step() {
    local step_name=$1
    local duration=$2
    
    echo -n "  [ ] $step_name"
    sleep $duration
    echo -e "\r  [✓] $step_name"
}

# --- The Performance ---

setup_stage

# The performance is conducted silently in the background.
# All verbose output is redirected to /dev/null.
{
    set -e # Exit on any error in the background process

    # Movement I: Composition
    python3 src/simple_ezkl_models.py
    
    # Movement II: Scoring
    ezkl gen-settings -M ezkl_workspace/rwkv_simple/model.onnx --settings-path ezkl_workspace/rwkv_simple/settings.json
    ezkl compile-circuit -M ezkl_workspace/rwkv_simple/model.onnx --compiled-circuit ezkl_workspace/rwkv_simple/model.compiled --settings-path ezkl_workspace/rwkv_simple/settings.json
    
    # Movement III: Rehearsal
    ezkl gen-srs --srs-path kzg.srs --logrows 16
    ezkl setup -M ezkl_workspace/rwkv_simple/model.compiled --srs-path kzg.srs --vk-path ezkl_workspace/rwkv_simple/vk.key --pk-path ezkl_workspace/rwkv_simple/pk.key
    
    # Movement IV: The Performance
    ezkl prove -M ezkl_workspace/rwkv_simple/model.compiled --witness ezkl_workspace/rwkv_simple/witness.json -D ezkl_workspace/rwkv_simple/input.json --proof-path ezkl_workspace/rwkv_simple/proof.json --pk-path ezkl_workspace/rwkv_simple/pk.key --srs-path kzg.srs

    # Movement V: The On-Chain Resonance
    npx hardhat node > /dev/null 2>&1 &
    NODE_PID=$!
    sleep 5
    npx hardhat run scripts/deploy_devnet.js --network localhost > /dev/null 2>&1
    
} &> /dev/null

# --- Visual Conduction ---
# This part of the script runs in the foreground, providing the visual performance.

conduct_step "Composing the melody (model creation)..." 0.5
conduct_step "Scoring the arrangement (circuit compile)..." 0.5
conduct_step "Tuning the instruments (SRS setup)..." 1
conduct_step "Generating the performance (proof)..." 1.5
conduct_step "Verifying the resonance (on-chain)..." 2

# --- The Finale ---
# The final confirmation is printed to the screen.

# Restore output for the final confirmation
exec > /dev/tty 2>&1
npx hardhat run scripts/resonate.js --network localhost

# --- Cleanup ---
# The stage is cleared silently.
{
    kill $NODE_PID
    rm kzg.srs
} &> /dev/null

echo
echo "---------------------"
echo "Performance complete."