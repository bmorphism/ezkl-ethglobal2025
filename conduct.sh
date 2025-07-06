#!/bin/bash

# The Conductor's Baton

# --- Animation Functions ---
function setup_stage() {
    clear
    echo "The Conductor's Score"
    echo "---------------------"
    echo
    echo "Instruments tuning..."
    sleep 1
}

function conduct_step() {
    local step_name=$1
    local pid=$2
    
    echo -n "  [ ] $step_name"
    while ps -p $pid > /dev/null; do
        echo -n "."
        sleep 0.1
    done
    echo -e "\r  [✓] $step_name"
}

# --- The Performance ---

setup_stage

# Create a temporary file to store the PID of the background process
BG_PID_FILE=$(mktemp)

# The performance is conducted silently in the background.
{
    set -e
    
    # Source environment for non-interactive shell
    source ~/.nvm/nvm.sh
    source ~/.profile
    source ~/.bashrc

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
    echo $! > $BG_PID_FILE
    sleep 5
    npx hardhat run scripts/deploy_devnet.js --network localhost > /dev/null 2>&1

} &> /dev/null &

PERFORMANCE_PID=$!

# --- Visual Conduction ---
conduct_step "Composing the melody (model creation)..." $PERFORMANCE_PID
conduct_step "Scoring the arrangement (circuit compile)..." $PERFORMANCE_PID
conduct_step "Tuning the instruments (SRS setup)..." $PERFORMANCE_PID
conduct_step "Generating the performance (proof)..." $PERFORMANCE_PID
conduct_step "Verifying the resonance (on-chain)..." $PERFORMANCE_PID

wait $PERFORMANCE_PID
EXIT_CODE=$?

# --- The Finale ---
if [ $EXIT_CODE -eq 0 ]; then
    npx hardhat run scripts/resonate.js --network localhost
    echo
    echo "---------------------"
    echo "Performance complete."
else
    echo
    echo "---------------------"
    echo "The performance was flawed. The conductor has stopped the orchestra."
    exit 1
fi

# --- Cleanup ---
NODE_PID=$(cat $BG_PID_FILE)
kill $NODE_PID
rm $BG_PID_FILE
rm kzg.srs
