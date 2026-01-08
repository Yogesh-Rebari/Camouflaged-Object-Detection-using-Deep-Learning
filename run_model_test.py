"""Quick test script to load the YOLO model and run an inference.

Usage (PowerShell):
    .\.venv\Scripts\Activate.ps1
    python run_model_test.py

The script will:
- create the Flask app and push an application context
- import app.services.model_service and call load_model()
- search `static/uploads` for a sample image and run inference
- print detections and where the annotated image was saved
"""
from pathlib import Path
import sys

from app import create_app

app = create_app()

with app.app_context():
    try:
        from app.services import model_service
    except Exception as e:
        print("Could not import model_service:", e)
        sys.exit(1)

    model = model_service.load_model()
    if model is None:
        print("Model could not be loaded. Ensure ultralytics is installed and the model file exists in the 'models' directory.")
        sys.exit(2)

    uploads_dir: Path = app.config['UPLOAD_FOLDER']
    uploads_dir.mkdir(parents=True, exist_ok=True)

    # pick first image in uploads
    sample = None
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.webp"):
        matches = list(uploads_dir.glob(ext))
        if matches:
            sample = matches[0]
            break

    if sample is None:
        print(f"No sample images found in {uploads_dir}. Please place an image there or upload via the web UI and retry.")
        sys.exit(3)

    print(f"Running inference on: {sample}")
    detections, annotated_path = model_service.run_inference_on_path(model, str(sample), conf=0.25)

    print("Detections:")
    for d in detections:
        print(d)

    print("Annotated image saved to:", annotated_path)

