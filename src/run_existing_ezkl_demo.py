#!/usr/bin/env python3
"""
EZKL Demo using existing production models
Demonstrates proof generation with pre-built RWKV, Mamba, and xLSTM models
"""

import os
import json
import subprocess
import sys
from pathlib import Path

class ProductionEZKLDemo:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.workspace_dir = self.base_dir / "simple_ezkl_workspace"
        self.models = ["rwkv_simple", "mamba_simple", "xlstm_simple"]
        
    def check_ezkl_installation(self):
        """Verify EZKL is installed and accessible"""
        try:
            result = subprocess.run(["ezkl", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ EZKL found: {result.stdout.strip()}")
                return True
            else:
                print(f"❌ EZKL not working: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ EZKL not found: {e}")
            return False
            
    def verify_models_exist(self):
        """Check that all required model files exist"""
        print(f"\n🔍 Verifying existing models...")
        
        for model_name in self.models:
            model_dir = self.workspace_dir / model_name
            required_files = ["model.onnx", "input.json", "settings.json"]
            
            print(f"\n📂 Checking {model_name}:")
            
            if not model_dir.exists():
                print(f"❌ Directory missing: {model_dir}")
                return False
                
            for file_name in required_files:
                file_path = model_dir / file_name
                if file_path.exists():
                    size = file_path.stat().st_size
                    print(f"  ✅ {file_name} ({size:,} bytes)")
                else:
                    print(f"  ❌ Missing: {file_name}")
                    return False
                    
        print(f"\n✅ All model files verified!")
        return True
        
    def generate_proof_for_model(self, model_name):
        """Generate a ZK proof for a specific model"""
        print(f"\n🔬 Generating proof for {model_name}...")
        
        model_dir = self.workspace_dir / model_name
        
        # Change to model directory
        original_cwd = os.getcwd()
        os.chdir(model_dir)
        
        try:
            # For RWKV, we might already have a circuit
            circuit_file = "circuit.ezkl"
            if not Path(circuit_file).exists():
                print(f"  🏗️  Compiling circuit...")
                result = subprocess.run([
                    "ezkl", "compile-circuit",
                    "-M", "model.onnx",
                    "-S", "settings.json",
                    "--compiled-circuit", circuit_file
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode != 0:
                    print(f"  ❌ Circuit compilation failed: {result.stderr}")
                    return False
                print(f"  ✅ Circuit compiled successfully")
            else:
                print(f"  ✅ Using existing circuit")
            
            # Setup ceremony (generate proving key)
            pk_file = "pk.key"
            vk_file = "vk.key"
            
            if not Path(pk_file).exists():
                print(f"  🔑 Setting up ceremony...")
                result = subprocess.run([
                    "ezkl", "setup",
                    "-M", "model.onnx",
                    "-S", "settings.json",
                    "--vk-path", vk_file,
                    "--pk-path", pk_file
                ], capture_output=True, text=True, timeout=120)
                
                if result.returncode != 0:
                    print(f"  ❌ Setup failed: {result.stderr}")
                    return False
                print(f"  ✅ Ceremony setup complete")
            else:
                print(f"  ✅ Using existing keys")
            
            # Generate witness
            witness_file = "witness.json"
            print(f"  🧮 Generating witness...")
            result = subprocess.run([
                "ezkl", "gen-witness",
                "-M", "model.onnx",
                "-I", "input.json",
                "-O", witness_file,
                "-S", "settings.json"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                print(f"  ❌ Witness generation failed: {result.stderr}")
                return False
            print(f"  ✅ Witness generated")
            
            # Generate proof
            proof_file = "proof.json"
            print(f"  🔐 Generating ZK proof...")
            result = subprocess.run([
                "ezkl", "prove",
                "-M", "model.onnx",
                "-W", witness_file,
                "-S", "settings.json",
                "--pk-path", pk_file,
                "--proof-path", proof_file
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                print(f"  ❌ Proof generation failed: {result.stderr}")
                return False
            
            # Verify proof
            print(f"  ✅ Verifying proof...")
            result = subprocess.run([
                "ezkl", "verify",
                "-S", "settings.json",
                "--proof-path", proof_file,
                "--vk-path", vk_file
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                print(f"  ❌ Proof verification failed: {result.stderr}")
                return False
            
            # Get proof size
            proof_size = Path(proof_file).stat().st_size
            print(f"  ✅ Proof verified successfully! ({proof_size:,} bytes)")
            
            return True
            
        except subprocess.TimeoutExpired:
            print(f"  ❌ Operation timed out")
            return False
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False
        finally:
            os.chdir(original_cwd)
    
    def run_demo(self):
        """Run the complete EZKL demo"""
        print("🎯 Production EZKL Demo Pipeline")
        print("=" * 50)
        
        # Check EZKL installation
        if not self.check_ezkl_installation():
            return False
            
        # Verify models exist
        if not self.verify_models_exist():
            return False
            
        # Test proof generation for each model
        success_count = 0
        
        for model_name in self.models:
            if self.generate_proof_for_model(model_name):
                success_count += 1
            else:
                print(f"❌ Failed to generate proof for {model_name}")
        
        print(f"\n📊 Demo Results:")
        print(f"  ✅ Successful proofs: {success_count}/{len(self.models)}")
        print(f"  📈 Success rate: {(success_count/len(self.models)*100):.1f}%")
        
        if success_count == len(self.models):
            print(f"\n🎉 All models successfully generated and verified ZK proofs!")
            print(f"🚀 Ready for blockchain deployment!")
            return True
        else:
            print(f"\n⚠️  Some models failed - check EZKL setup")
            return False

def main():
    """Run EZKL demo with existing production models"""
    demo = ProductionEZKLDemo()
    success = demo.run_demo()
    
    if success:
        print(f"\n🎯 Next Steps:")
        print(f"  1. Deploy verifier contracts (already done on Sepolia!)")
        print(f"  2. Submit proofs to smart contracts")
        print(f"  3. Build agentic proof-chaining workflows")
    else:
        print(f"\n🔧 Troubleshooting:")
        print(f"  1. Check EZKL installation: ezkl --version")
        print(f"  2. Verify model files are not corrupted")
        print(f"  3. Check system memory (proofs require significant RAM)")

if __name__ == "__main__":
    main()