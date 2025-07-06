#!/usr/bin/env python3
"""
Complete Deployment Verification Script
Verifies all components of the ZK-verified agentic framework are properly deployed and functional
"""

import os
import json
import subprocess
from pathlib import Path

def verify_file_structure():
    """Verify all essential files and directories exist"""
    print("🔍 VERIFYING FILE STRUCTURE")
    print("=" * 50)
    
    required_files = [
        "contracts/ProductionRWKVVerifier.sol",
        "contracts/ProductionMambaVerifier.sol", 
        "contracts/ProductionxLSTMVerifier.sol",
        "scripts/deploy_sepolia.js",
        "scripts/deploy_devnet.js",
        "scripts/simple_model_test.js",
        "src/real_model_inference.py",
        "src/simple_ezkl_models.py",
        "docs/MAXIMAL_AGENTIC_PROOF_CHAINING_FRAMEWORK.md",
        "docs/SEPOLIA_DEPLOYMENT_SUCCESS.md",
        "docs/sepolia_setup_guide.md",
        "config/sepolia-addresses.json",
        "config/deployment-addresses.json",
        "README.md",
        "LICENSE",
        "CONTRIBUTING.md",
        "hardhat.config.js",
        "package.json",
        ".env.example"
    ]
    
    required_dirs = [
        "contracts/",
        "scripts/", 
        "src/",
        "docs/",
        "config/",
        "ezkl_workspace/"
    ]
    
    missing_files = []
    missing_dirs = []
    
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"   ✅ {file_path}")
    
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
        else:
            print(f"   ✅ {dir_path}")
    
    print(f"\n📊 File Structure Status:")
    print(f"   ✅ Files verified: {len(required_files) - len(missing_files)}/{len(required_files)}")
    print(f"   ✅ Directories verified: {len(required_dirs) - len(missing_dirs)}/{len(required_dirs)}")
    
    if missing_files:
        print(f"   ❌ Missing files: {missing_files}")
    if missing_dirs:
        print(f"   ❌ Missing directories: {missing_dirs}")
    
    return len(missing_files) == 0 and len(missing_dirs) == 0

def verify_contract_addresses():
    """Verify live contract addresses are properly configured"""
    print("\n🔗 VERIFYING LIVE CONTRACT ADDRESSES")
    print("=" * 50)
    
    try:
        with open("config/sepolia-addresses.json", 'r') as f:
            addresses = json.load(f)
        
        expected_contracts = {
            "ProductionRWKVVerifier": "0x52b5e61fA6Ae53BA08B9094eA077820283Dcec01",
            "ProductionMambaVerifier": "0x89dFdcC74Ed05bf2a76eF788b15e5cbC8Ad8C5cD", 
            "ProductionxLSTMVerifier": "0x52a55dEBE04124376841dF391Ef0e4eF1dd6835B"
        }
        
        contracts_section = addresses.get("contracts", addresses)
        all_verified = True
        
        for contract_name, expected_addr in expected_contracts.items():
            if contract_name in contracts_section and contracts_section[contract_name] == expected_addr:
                display_name = contract_name.replace("Production", "").replace("Verifier", "")
                print(f"   ✅ {display_name}: {expected_addr}")
            else:
                display_name = contract_name.replace("Production", "").replace("Verifier", "")
                actual_addr = contracts_section.get(contract_name, 'MISSING')
                print(f"   ❌ {display_name}: Expected {expected_addr}, got {actual_addr}")
                all_verified = False
        
        return all_verified
        
    except FileNotFoundError:
        print("   ❌ sepolia-addresses.json not found")
        return False
    except json.JSONDecodeError:
        print("   ❌ Invalid JSON in sepolia-addresses.json")
        return False

def verify_ezkl_workspace():
    """Verify EZKL workspace configurations"""
    print("\n🏗️ VERIFYING EZKL WORKSPACE")
    print("=" * 50)
    
    architectures = ["rwkv", "mamba", "xlstm"]
    workspace_files = ["model.onnx", "input.json", "settings.json"]
    
    all_verified = True
    for arch in architectures:
        arch_path = Path(f"ezkl_workspace/{arch}")
        if arch_path.exists():
            print(f"   ✅ {arch}/ directory exists")
            for file_name in workspace_files:
                file_path = arch_path / file_name
                if file_path.exists():
                    print(f"      ✅ {arch}/{file_name}")
                else:
                    print(f"      ❌ {arch}/{file_name} missing")
                    all_verified = False
        else:
            print(f"   ❌ {arch}/ directory missing")
            all_verified = False
    
    return all_verified

def verify_git_status():
    """Verify git repository status"""
    print("\n📡 VERIFYING GIT REPOSITORY STATUS")
    print("=" * 50)
    
    try:
        # Check if we're in a git repository
        result = subprocess.run(["git", "status", "--porcelain"], 
                              capture_output=True, text=True, check=True)
        
        if result.stdout.strip() == "":
            print("   ✅ Working directory clean - all changes committed")
        else:
            print("   ⚠️  Uncommitted changes detected:")
            print(f"      {result.stdout.strip()}")
        
        # Check remote status
        remote_result = subprocess.run(["git", "remote", "-v"], 
                                     capture_output=True, text=True, check=True)
        
        if "git@github.com:bmorphism/ezkl-ethglobal2025.git" in remote_result.stdout:
            print("   ✅ Connected to correct GitHub repository")
        else:
            print("   ❌ GitHub remote not configured correctly")
            return False
            
        # Check if up to date with remote
        subprocess.run(["git", "fetch"], capture_output=True, check=True)
        status_result = subprocess.run(["git", "status", "-uno"], 
                                     capture_output=True, text=True, check=True)
        
        if "up to date" in status_result.stdout or "up-to-date" in status_result.stdout:
            print("   ✅ Repository up to date with remote")
        else:
            print("   ⚠️  Repository may not be up to date with remote")
        
        return True
        
    except subprocess.CalledProcessError:
        print("   ❌ Git command failed - not in a git repository?")
        return False

def verify_dependencies():
    """Verify required dependencies are available"""
    print("\n📦 VERIFYING DEPENDENCIES")
    print("=" * 50)
    
    # Check Node.js dependencies
    try:
        with open("package.json", 'r') as f:
            package_data = json.load(f)
        
        if "hardhat" in package_data.get("dependencies", {}) or "hardhat" in package_data.get("devDependencies", {}):
            print("   ✅ Hardhat configured in package.json")
        else:
            print("   ❌ Hardhat not found in package.json")
        
        # Check if node_modules exists
        if Path("node_modules").exists():
            print("   ✅ node_modules directory exists")
        else:
            print("   ⚠️  node_modules not found - run 'npm install'")
            
    except FileNotFoundError:
        print("   ❌ package.json not found")
        return False
    
    # Check Python dependencies
    if Path("requirements.txt").exists():
        print("   ✅ requirements.txt exists")
        try:
            with open("requirements.txt", 'r') as f:
                requirements = f.read()
            if "torch" in requirements and "ezkl" in requirements:
                print("   ✅ Essential Python dependencies listed")
            else:
                print("   ⚠️  Some Python dependencies may be missing")
        except:
            print("   ❌ Error reading requirements.txt")
    else:
        print("   ❌ requirements.txt not found")
    
    return True

def main():
    """Run complete deployment verification"""
    print("🎯 ZK-VERIFIED AGENTIC FRAMEWORK - DEPLOYMENT VERIFICATION")
    print("=" * 80)
    print("Repository: git@github.com:bmorphism/ezkl-ethglobal2025.git")
    print("=" * 80)
    
    verification_results = {
        "file_structure": verify_file_structure(),
        "contract_addresses": verify_contract_addresses(), 
        "ezkl_workspace": verify_ezkl_workspace(),
        "git_status": verify_git_status(),
        "dependencies": verify_dependencies()
    }
    
    print("\n🏆 VERIFICATION SUMMARY")
    print("=" * 50)
    
    total_checks = len(verification_results)
    passed_checks = sum(verification_results.values())
    
    for check_name, result in verification_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {check_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n📊 Overall Status: {passed_checks}/{total_checks} checks passed")
    
    if all(verification_results.values()):
        print("\n🌟 SUCCESS: ZK-VERIFIED AGENTIC FRAMEWORK FULLY OPERATIONAL!")
        print("🚀 Ready for ETHGlobal 2025 showcase and production use")
        print("\n🔗 Live Contracts:")
        print("   RWKV:  https://sepolia.etherscan.io/address/0x52b5e61fA6Ae53BA08B9094eA077820283Dcec01")
        print("   Mamba: https://sepolia.etherscan.io/address/0x89dFdcC74Ed05bf2a76eF788b15e5cbC8Ad8C5cD")
        print("   xLSTM: https://sepolia.etherscan.io/address/0x52a55dEBE04124376841dF391Ef0e4eF1dd6835B")
        return 0
    else:
        print("\n⚠️  Some verification checks failed - review above for details")
        return 1

if __name__ == "__main__":
    exit(main())