#!/usr/bin/env python3
"""
Simple test to validate existing EZKL artifacts
Checks that our production models and files are correctly structured
"""

import json
import os
from pathlib import Path

class EZKLArtifactValidator:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.workspace_dir = self.base_dir / "simple_ezkl_workspace"
        self.models = ["rwkv_simple", "mamba_simple", "xlstm_simple"]
        
    def validate_json_file(self, file_path, expected_keys=None):
        """Validate that a JSON file is properly formatted"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            if expected_keys:
                missing_keys = [key for key in expected_keys if key not in data]
                if missing_keys:
                    return False, f"Missing keys: {missing_keys}"
            
            return True, f"Valid JSON with {len(data)} top-level keys"
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {e}"
        except Exception as e:
            return False, f"Error reading file: {e}"
    
    def check_model_structure(self, model_name):
        """Check the structure and validity of a model directory"""
        print(f"\n🔍 Validating {model_name}:")
        
        model_dir = self.workspace_dir / model_name
        if not model_dir.exists():
            print(f"  ❌ Directory not found: {model_dir}")
            return False
        
        success = True
        
        # Check ONNX model
        onnx_file = model_dir / "model.onnx"
        if onnx_file.exists():
            size = onnx_file.stat().st_size
            print(f"  ✅ ONNX model: {size:,} bytes")
        else:
            print(f"  ❌ ONNX model missing")
            success = False
        
        # Check input.json
        input_file = model_dir / "input.json"
        if input_file.exists():
            valid, msg = self.validate_json_file(input_file)
            if valid:
                print(f"  ✅ Input JSON: {msg}")
            else:
                print(f"  ❌ Input JSON: {msg}")
                success = False
        else:
            print(f"  ❌ Input JSON missing")
            success = False
        
        # Check settings.json
        settings_file = model_dir / "settings.json"
        if settings_file.exists():
            valid, msg = self.validate_json_file(settings_file, ["run_args"])
            if valid:
                print(f"  ✅ Settings JSON: {msg}")
                
                # Try to read specific settings
                try:
                    with open(settings_file, 'r') as f:
                        settings = json.load(f)
                    
                    if "run_args" in settings:
                        run_args = settings["run_args"]
                        print(f"    📊 Tolerance: {run_args.get('tolerance', 'default')}")
                        print(f"    📊 Input scale: {run_args.get('input_scale', 'default')}")
                        print(f"    📊 Param scale: {run_args.get('param_scale', 'default')}")
                    
                    if "run_args" in settings and "num_inner_cols" in settings["run_args"]:
                        print(f"    📊 Inner columns: {settings['run_args']['num_inner_cols']}")
                    
                    if "num_rows" in settings:
                        print(f"    📊 Number of rows: {settings['num_rows']:,}")
                    
                    if "version" in settings:
                        print(f"    📊 EZKL version: {settings['version']}")
                        
                except Exception as e:
                    print(f"    ⚠️  Could not read settings details: {e}")
                    
            else:
                print(f"  ❌ Settings JSON: {msg}")
                success = False
        else:
            print(f"  ❌ Settings JSON missing")
            success = False
        
        # Check for optional circuit file (RWKV has one)
        circuit_file = model_dir / "circuit.ezkl"
        if circuit_file.exists():
            size = circuit_file.stat().st_size
            print(f"  ✅ Circuit file: {size:,} bytes (pre-compiled)")
        else:
            print(f"  ℹ️  No pre-compiled circuit (will be generated)")
        
        return success
    
    def validate_deployment_addresses(self):
        """Check that we have valid deployment addresses"""
        print(f"\n🌐 Checking deployment configuration:")
        
        sepolia_file = self.base_dir / "sepolia-addresses.json"
        if sepolia_file.exists():
            valid, msg = self.validate_json_file(sepolia_file)
            if valid:
                print(f"  ✅ Sepolia addresses: {msg}")
                
                # Show actual addresses
                try:
                    with open(sepolia_file, 'r') as f:
                        addresses = json.load(f)
                    
                    for contract_name, address in addresses.items():
                        print(f"    🔗 {contract_name}: {address}")
                        
                except Exception as e:
                    print(f"    ⚠️  Could not read addresses: {e}")
            else:
                print(f"  ❌ Sepolia addresses: {msg}")
                return False
        else:
            print(f"  ❌ Sepolia addresses missing")
            return False
        
        return True
    
    def run_validation(self):
        """Run complete validation of EZKL artifacts"""
        print("🔬 EZKL Artifact Validation")
        print("=" * 40)
        
        # Check workspace directory
        if not self.workspace_dir.exists():
            print(f"❌ Workspace directory not found: {self.workspace_dir}")
            return False
        
        print(f"✅ Workspace found: {self.workspace_dir}")
        
        # Validate each model
        all_valid = True
        valid_models = 0
        
        for model_name in self.models:
            if self.check_model_structure(model_name):
                valid_models += 1
            else:
                all_valid = False
        
        # Check deployment configuration
        deployment_valid = self.validate_deployment_addresses()
        
        # Summary
        print(f"\n📊 Validation Results:")
        print(f"  ✅ Valid models: {valid_models}/{len(self.models)}")
        print(f"  ✅ Deployment config: {'Yes' if deployment_valid else 'No'}")
        
        if all_valid and deployment_valid:
            print(f"\n🎉 All EZKL artifacts are valid!")
            print(f"🚀 Ready for proof generation and blockchain integration!")
            
            print(f"\n💡 What you can do next:")
            print(f"  1. Install EZKL CLI: pip install ezkl")
            print(f"  2. Generate proofs: cd simple_ezkl_workspace/rwkv_simple && ezkl prove ...")
            print(f"  3. Submit to deployed contracts on Sepolia testnet")
            return True
        else:
            print(f"\n⚠️  Some artifacts are invalid - check the issues above")
            return False

def main():
    """Validate existing EZKL artifacts"""
    validator = EZKLArtifactValidator()
    validator.run_validation()

if __name__ == "__main__":
    main()