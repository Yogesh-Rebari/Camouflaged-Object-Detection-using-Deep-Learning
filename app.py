"""
Minimal Flask application to serve the YOLOv8 frontend pages.
- Routes:
  - /                -> index
  - /model_info      -> model.html
  - /predict         -> placeholder page
  - /performance     -> placeholder page
"""
from datetime import datetime
import uuid
import os
import io
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename

# Try to import ultralytics YOLO. The project may not have it installed yet.
try:
    from ultralytics import YOLO
except Exception:
    YOLO = None

from PIL import Image
import cv2
import numpy as np

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB upload limit
app.secret_key = 'dev_secret_for_flash_messages'

# Model configuration
MODELS_DIR = os.path.join(app.root_path, 'models')
MODEL_PATHS = [
    os.path.join(MODELS_DIR, 'model.pt'),           # Primary model file
    os.path.join(MODELS_DIR, 'custom_yolov8.pt'),  # Custom model
    os.path.join(MODELS_DIR, 'best.pt'),            # Best checkpoint
    os.path.join(MODELS_DIR, 'last.pt'),            # Last checkpoint
    'yolov8n.pt'  # Fallback to default pre-trained model
]

# Ensure directories exist
Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)
Path(MODELS_DIR).mkdir(parents=True, exist_ok=True)

# Global model cache (loaded once at startup)
_model_cache = None


def load_model():
    """
    Load YOLOv8 model with caching. Tries custom model first, then falls back to default.
    Returns the model instance or None if YOLO is not available.
    """
    global _model_cache
    
    if YOLO is None:
        return None
    
    # Return cached model if already loaded
    if _model_cache is not None:
        return _model_cache
    
    # Try to load custom model from models directory
    for model_path in MODEL_PATHS:
        if os.path.exists(model_path):
            try:
                print(f"Loading model from: {model_path}")
                _model_cache = YOLO(model_path)
                print(f"Model loaded successfully!")
                return _model_cache
            except Exception as e:
                print(f"Error loading model from {model_path}: {e}")
                continue
    
    # If no custom model found, try to download default
    try:
        print("No custom model found. Loading default YOLOv8n model...")
        _model_cache = YOLO('yolov8n.pt')
        print("Default model loaded successfully!")
        return _model_cache
    except Exception as e:
        print(f"Error loading default model: {e}")
        return None


@app.context_processor
def inject_globals():
    """Injects common template variables."""
    return {"current_year": datetime.now().year}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/model_info")
def model_info():
    return render_template("model.html")


@app.route("/predict", methods=["GET", "POST"])
def predict():
    # Show form on GET, handle uploads on POST
    if request.method == 'GET':
        return render_template('predict.html')

    # POST: handle uploaded image
    if 'image' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['image']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    # Save uploaded file to uploads folder (use secure filename and avoid collisions)
    original_name = secure_filename(file.filename)
    unique_suffix = uuid.uuid4().hex[:8]
    filename = f"{unique_suffix}_{original_name}"
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(save_path)

    # Run YOLOv8 model if available
    annotated_path = None
    model = load_model()
    
    if model is None:
        if YOLO is None:
            flash('YOLO (ultralytics) library is not installed. Please install it: pip install ultralytics')
        else:
            flash('Failed to load model. Please check MODEL_SETUP_GUIDE.md for instructions.')
    else:
        try:
            # Run prediction with the loaded model
            results = model(save_path, imgsz=640)

            # results[0].plot() returns an OpenCV BGR image (numpy array)
            annotated = results[0].plot()

            # Convert BGR (OpenCV) to RGB and save via PIL
            annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
            im_pil = Image.fromarray(annotated_rgb)

            annotated_filename = f"annotated_{uuid.uuid4().hex[:8]}_{original_name}"
            annotated_path = os.path.join(app.config['UPLOAD_FOLDER'], annotated_filename)
            im_pil.save(annotated_path)
            
            # Optional: Get detection statistics
            num_detections = len(results[0].boxes) if results[0].boxes is not None else 0
            if num_detections > 0:
                flash(f'Detection successful! Found {num_detections} object(s).')
        except Exception as e:
            flash(f'Error running model: {str(e)}')
            print(f"Prediction error: {e}")

    return render_template('predict.html', uploaded_image=filename, annotated_image=(os.path.basename(annotated_path) if annotated_path else None))


@app.route("/performance")
def performance():
    return render_template("performance.html")


if __name__ == "__main__":
    # Load model at startup
    print("=" * 50)
    print("Initializing YOLOv8 Model...")
    print("=" * 50)
    model = load_model()
    if model:
        print("✓ Model ready for inference!")
    else:
        print("⚠ Warning: Model not loaded. Check MODEL_SETUP_GUIDE.md")
    print("=" * 50)
    print("\nStarting Flask server...")
    print("Open http://127.0.0.1:5000 in your browser\n")
    
    # For local dev convenience
    app.run(host="127.0.0.1", port=5000, debug=True)

