#!/usr/bin/env python3
"""
Test script for AI Detection App
Verifies all components work correctly
"""

import sys
import os

print("=" * 60)
print("AI Detection App - Component Test")
print("=" * 60)

# Test 1: Check engine file
print("\n[1/5] Checking for .engine files...")
import glob
engine_files = glob.glob('**/*.engine', recursive=True)
if engine_files:
    print(f"✓ Found engine file: {engine_files[0]}")
else:
    print("✗ No .engine file found")

# Test 2: Check imports
print("\n[2/5] Checking required imports...")
try:
    import cv2
    print(f"✓ OpenCV version: {cv2.__version__}")
except ImportError:
    print("✗ OpenCV not found - install with: pip3 install opencv-python")

try:
    import numpy as np
    print(f"✓ NumPy version: {np.__version__}")
except ImportError:
    print("✗ NumPy not found - install with: pip3 install numpy")

try:
    from PySide6 import QtCore
    print(f"✓ PySide6 version: {QtCore.__version__}")
except ImportError:
    print("✗ PySide6 not found - install with: pip3 install PySide6")

try:
    import tensorrt as trt
    print(f"✓ TensorRT available")
except ImportError:
    print("⚠ TensorRT not available (optional for testing)")

try:
    import pycuda.driver as cuda
    print(f"✓ PyCUDA available")
except ImportError:
    print("⚠ PyCUDA not available (optional for testing)")

# Test 3: Check cameras
print("\n[3/5] Checking camera availability...")
try:
    import cv2
    for cam_idx in [0, 2]:
        cap = cv2.VideoCapture(cam_idx)
        if cap.isOpened():
            print(f"✓ Camera {cam_idx} available")
            cap.release()
        else:
            print(f"⚠ Camera {cam_idx} not available")
except Exception as e:
    print(f"✗ Camera check failed: {e}")

# Test 4: Check Relay_b.py
print("\n[4/5] Checking Relay module...")
if os.path.exists('Relay_b.py') and os.path.getsize('Relay_b.py') > 0:
    try:
        from Relay_b import Relay
        print("✓ Relay_b.py loaded successfully")
    except Exception as e:
        print(f"⚠ Relay_b.py exists but has issues: {e}")
        print("  The app will use dummy relay mode")
else:
    print("⚠ Relay_b.py is empty or missing")
    print("  The app will use dummy relay mode")

# Test 5: Verify app can be imported
print("\n[5/5] Checking main application...")
try:
    # Just check if it can be imported/parsed
    with open('ai_detection_app.py', 'r') as f:
        content = f.read()
        if 'class DetectionApp' in content:
            print("✓ Main application file structure OK")
        else:
            print("✗ Main application file missing DetectionApp class")
except Exception as e:
    print(f"✗ Error reading application: {e}")

print("\n" + "=" * 60)
print("Test Summary")
print("=" * 60)
print("\nTo run the application:")
print("  python3 ai_detection_app.py")
print("\nThe app will auto-detect the engine file and use dummy relay mode")
print("if Relay_b.py is not available.")
print("\nNote: Without TensorRT, object detection will not work but the")
print("      camera feeds and GUI will still function.")
print("=" * 60)
