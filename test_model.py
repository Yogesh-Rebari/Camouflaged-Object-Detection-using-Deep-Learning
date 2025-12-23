"""
Quick test script to verify YOLO installation and model loading.
Run this before starting Flask to diagnose issues.
"""
import sys
import os

print("=" * 70)
print("YOLO Installation & Model Loading Test")
print("=" * 70)
print(f"Python: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")
print()

# Test 1: Import YOLO
print("Test 1: Importing ultralytics...")
try:
    from ultralytics import YOLO
    print("✓ YOLO imported successfully")
    YOLO_AVAILABLE = True
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("   Solution: pip install ultralytics")
    YOLO_AVAILABLE = False
    sys.exit(1)
except Exception as e:
    print(f"❌ Import error: {e}")
    YOLO_AVAILABLE = False
    sys.exit(1)

# Test 2: Check model files
print("\nTest 2: Checking model files...")
MODELS_DIR = os.path.join(os.getcwd(), 'models')
PRIMARY_MODEL = os.path.join(MODELS_DIR, 'best (1).pt')
SECONDARY_MODEL = os.path.join(MODELS_DIR, 'model.pt')

for path in [PRIMARY_MODEL, SECONDARY_MODEL]:
    label = "PRIMARY (best (1).pt)" if path == PRIMARY_MODEL else "SECONDARY (model.pt)"
    if os.path.exists(path):
        print(f"✓ {label} model file found: {path}")
        file_size = os.path.getsize(path) / (1024 * 1024)  # MB
        print(f"  File size: {file_size:.2f} MB")
    else:
        print(f"✗ {label} model file not found: {path}")

if os.path.exists(MODELS_DIR):
    files = os.listdir(MODELS_DIR)
    print(f"\n  Files in models directory: {files}")
else:
    print(f"\n✗ Models directory does not exist: {MODELS_DIR}")

# Test 3: Load model (prefer best (1).pt)
print("\nTest 3: Loading model...")
if YOLO_AVAILABLE:
    try:
        load_path = None
        if os.path.exists(PRIMARY_MODEL):
            load_path = PRIMARY_MODEL
        elif os.path.exists(SECONDARY_MODEL):
            load_path = SECONDARY_MODEL

        if load_path:
            print(f"  Loading from: {load_path}")
            model = YOLO(load_path)
            print("✓ Model loaded successfully!")
            print(f"  Model type: {type(model)}")
            if hasattr(model, 'names'):
                print(f"  Model classes: {len(model.names)}")
        else:
            print("  No local model file found, trying default YOLOv8n...")
            model = YOLO('yolov8n.pt')
            print("✓ Default model loaded successfully!")
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        import traceback
        print(f"  Traceback: {traceback.format_exc()}")
        sys.exit(1)

print("\n" + "=" * 70)
print("✓ All tests passed! You can start Flask server now.")
print("=" * 70)

