#!/usr/bin/env python3
"""
Simple EZKL-Compatible Models
Creates simplified neural network models that work with EZKL constraints
"""

import torch
import torch.nn as nn
import numpy as np
import json

class SimpleLinearModel(nn.Module):
    """Very simple linear model that EZKL can handle"""
    
    def __init__(self, input_size: int = 10, hidden_size: int = 32, output_size: int = 69):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.linear2 = nn.Linear(hidden_size, output_size)
        
    def forward(self, x):
        x = self.linear1(x)
        x = self.relu(x)
        x = self.linear2(x)
        return x

class SimpleRNNModel(nn.Module):
    """Simple RNN that mimics our architectures"""
    
    def __init__(self, vocab_size: int = 69, hidden_size: int = 32, seq_len: int = 10):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, hidden_size)
        self.rnn = nn.RNN(hidden_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, vocab_size)
        
    def forward(self, x):
        # x shape: (batch, seq_len)
        embedded = self.embedding(x)  # (batch, seq_len, hidden)
        output, _ = self.rnn(embedded)  # (batch, seq_len, hidden)
        # Take last timestep
        last_output = output[:, -1, :]  # (batch, hidden)
        logits = self.fc(last_output)  # (batch, vocab_size)
        return logits

def create_simple_models():
    """Create simplified models for each architecture"""
    
    models = {
        'rwkv_simple': SimpleLinearModel(input_size=10, hidden_size=16, output_size=69),
        'mamba_simple': SimpleLinearModel(input_size=10, hidden_size=24, output_size=69),
        'xlstm_simple': SimpleLinearModel(input_size=10, hidden_size=20, output_size=69),
    }
    
    # Also create token-based models
    token_models = {
        'rwkv_tokens': SimpleRNNModel(vocab_size=69, hidden_size=16, seq_len=5),
        'mamba_tokens': SimpleRNNModel(vocab_size=69, hidden_size=24, seq_len=5),
        'xlstm_tokens': SimpleRNNModel(vocab_size=69, hidden_size=20, seq_len=5),
    }
    
    return models, token_models

def export_onnx_models():
    """Export simplified models to ONNX"""
    
    print("🚀 Creating Simplified EZKL-Compatible Models")
    print("=" * 50)
    
    models, token_models = create_simple_models()
    
    results = {}
    
    # Export continuous input models
    for name, model in models.items():
        print(f"\n📦 Exporting {name}...")
        
        model.eval()
        
        # Create dummy input
        dummy_input = torch.randn(1, 10)
        
        try:
            output_path = f"{name}.onnx"
            torch.onnx.export(
                model,
                dummy_input,
                output_path,
                export_params=True,
                opset_version=11,
                do_constant_folding=True,
                input_names=['input'],
                output_names=['output'],
                dynamic_axes={
                    'input': {0: 'batch_size'},
                    'output': {0: 'batch_size'}
                }
            )
            
            print(f"✅ Exported to {output_path}")
            
            # Test the model
            with torch.no_grad():
                output = model(dummy_input)
                print(f"   Model output shape: {output.shape}")
                print(f"   Sample output: {output[0, :5].tolist()}")
            
            results[name] = {
                'path': output_path,
                'input_shape': list(dummy_input.shape),
                'output_shape': list(output.shape),
                'success': True
            }
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
            results[name] = {'success': False, 'error': str(e)}
    
    # Export token-based models
    for name, model in token_models.items():
        print(f"\n📦 Exporting {name}...")
        
        model.eval()
        
        # Create dummy token input
        dummy_input = torch.randint(0, 69, (1, 5), dtype=torch.long)
        
        try:
            output_path = f"{name}.onnx"
            torch.onnx.export(
                model,
                dummy_input,
                output_path,
                export_params=True,
                opset_version=11,
                do_constant_folding=True,
                input_names=['tokens'],
                output_names=['logits'],
                dynamic_axes={
                    'tokens': {0: 'batch_size'},
                    'logits': {0: 'batch_size'}
                }
            )
            
            print(f"✅ Exported to {output_path}")
            
            # Test the model
            with torch.no_grad():
                output = model(dummy_input)
                print(f"   Model output shape: {output.shape}")
                print(f"   Sample logits: {output[0, :5].tolist()}")
            
            results[name] = {
                'path': output_path,
                'input_shape': list(dummy_input.shape),
                'output_shape': list(output.shape),
                'success': True
            }
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
            results[name] = {'success': False, 'error': str(e)}
    
    # Save export results
    with open('simple_onnx_export_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    successful_exports = [name for name, data in results.items() if data.get('success', False)]
    print(f"\n🎯 Summary: {len(successful_exports)}/{len(results)} models exported successfully")
    
    return results

def create_sample_inputs():
    """Create sample input files for EZKL"""
    
    print("\n📝 Creating Sample Input Files")
    print("-" * 30)
    
    # For continuous models
    continuous_models = ['rwkv_simple', 'mamba_simple', 'xlstm_simple']
    for model_name in continuous_models:
        input_data = np.random.randn(1, 10).astype(np.float32)
        
        input_json = {
            "input_data": [input_data.tolist()]
        }
        
        filename = f"{model_name}_input.json"
        with open(filename, 'w') as f:
            json.dump(input_json, f, indent=2)
        
        print(f"📄 Created {filename}")
    
    # For token models
    token_models = ['rwkv_tokens', 'mamba_tokens', 'xlstm_tokens']
    for model_name in token_models:
        # Create token sequence representing "plurigrid is"
        # Simple encoding: p=15, l=11, u=20, r=17, i=8, g=6, r=17, i=8, d=3, space=62, i=8, s=18
        token_data = np.array([[15, 11, 20, 17, 8]], dtype=np.float32)  # First 5 tokens
        
        input_json = {
            "input_data": [token_data.tolist()]
        }
        
        filename = f"{model_name}_input.json"
        with open(filename, 'w') as f:
            json.dump(input_json, f, indent=2)
        
        print(f"📄 Created {filename}")
    
    print("✅ All input files created")

if __name__ == "__main__":
    # Export models
    results = export_onnx_models()
    
    # Create input files
    create_sample_inputs()
    
    print("\n🎉 Simple EZKL models ready for proof generation!")