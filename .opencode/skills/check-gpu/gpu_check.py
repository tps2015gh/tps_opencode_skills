#!/usr/bin/env python3
"""Check GPU availability for OCR/AI tasks"""

import os
import sys
import io

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 50)
print("GPU Check for OCR/AI")
print("=" * 50)

# Check NVIDIA GPU
try:
    import subprocess
    result = subprocess.run(['nvidia-smi', '-L'], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"\n✅ NVIDIA GPU Found:")
        print(f"   {result.stdout.strip()}")
        
        # Get GPU info
        result2 = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total,memory.free,driver_version', '--format=csv,noheader'], 
                                capture_output=True, text=True)
        if result2.returncode == 0:
            lines = result2.stdout.strip().split('\n')
            for line in lines:
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 4:
                    print(f"\n📊 GPU Details:")
                    print(f"   Name: {parts[0]}")
                    print(f"   Memory: {parts[1]}")
                    print(f"   Free: {parts[2]}")
                    print(f"   Driver: {parts[3]}")
    else:
        print("\n❌ nvidia-smi not available")
except FileNotFoundError:
    print("\n❌ NVIDIA GPU not found (nvidia-smi not in PATH)")

# Check CUDA
print("\n" + "=" * 50)
print("CUDA Check")
print("=" * 50)

try:
    import torch
    print(f"\n✅ PyTorch installed")
    print(f"   Version: {torch.__version__}")
    print(f"   CUDA Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"   CUDA Version: {torch.version.cuda}")
        print(f"   GPU Count: {torch.cuda.device_count()}")
        print(f"   Current GPU: {torch.cuda.get_device_name(0)}")
except ImportError:
    print("\n⚠️ PyTorch not installed")
    print("   Install with: pip install torch")

# Check EasyOCR GPU support
print("\n" + "=" * 50)
print("OCR GPU Support")
print("=" * 50)

try:
    import easyocr
    print("\n✅ EasyOCR installed")
    
    # Try to detect GPU
    print("\nTo use GPU with EasyOCR, use: easyocr.Reader(['th'], gpu=True)")
    print("To use CPU (slower), use: easyocr.Reader(['th'], gpu=False)")
except ImportError:
    print("\n⚠️ EasyOCR not installed")

# Recommendations
print("\n" + "=" * 50)
print("Recommendations")
print("=" * 50)

recommendations = []

try:
    import torch
    if torch.cuda.is_available():
        recommendations.append("✅ Use GPU for OCR: easyocr.Reader(['th'], gpu=True)")
        recommendations.append("✅ Use GPU for PyTorch models")
    else:
        recommendations.append("⚠️ CUDA not available - use CPU mode")
except:
    pass

if not recommendations:
    recommendations.append("Install PyTorch with CUDA: pip install torch --index-url https://download.pytorch.org/whl/cu118")

for rec in recommendations:
    print(f"   {rec}")

print("\n" + "=" * 50)
