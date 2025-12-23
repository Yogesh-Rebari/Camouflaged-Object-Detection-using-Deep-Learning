#!/usr/bin/env python
"""
Quick diagnostic script to check YOLO installation
"""
import sys
import os

print("=" * 60)
print("YOLO Installation Diagnostic")
print("=" * 60)
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Working directory: {os.getcwd()}")
print()

# Check YOLO import
print("Checking YOLO import...")
try:
    from ultralytics import YOLO
    print("✓ YOLO imported successfully!")
    print(f"  YOLO class: {YOLO}")
    
    # Try to get version
    try:
        import ultralytics
        version = getattr(ultralytics, '__version__', 'Unknown')
        print(f"  Ultralytics version: {version}")
    except:
        pass
    
    # Check if model file exists
    print("\nChecking model files...")
    model_paths = [
        'models/best (1).pt',
        'models/model.pt',
        'models/custom_yolov8.pt',
        'models/best.pt',
        'models/last.pt'
    ]
    
    for path in model_paths:
        if os.path.exists(path):
            size = os.path.getsize(path) / (1024 * 1024)  # MB
            print(f"  ✓ Found: {path} ({size:.2f} MB)")
        else:
            print(f"  ✗ Not found: {path}")
    
    print("\n✓ All checks passed! YOLO is ready to use.")
    print("  If Flask app still shows error, restart the Flask server.")
    
except ImportError as e:
    print(f"❌ YOLO import failed: {e}")
    print("\nTo install YOLO, run:")
    print("  pip install ultralytics")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    print(f"  Error type: {type(e).__name__}")
    sys.exit(1)

print("=" * 60)

