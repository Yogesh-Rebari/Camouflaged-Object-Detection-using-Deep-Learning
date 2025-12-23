import os
import uuid
from pathlib import Path
from typing import Tuple

from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

from app.services.model_service import load_model, run_inference_on_path

web_bp = Blueprint("web", __name__)


def _allowed_file(filename: str, allowed_exts: Tuple[str, ...] = (".jpg", ".jpeg", ".png", ".webp")) -> bool:
    return filename.lower().endswith(allowed_exts)


def _allowed_mimetype(mimetype: str, allowed: Tuple[str, ...] = ("image/jpeg", "image/png", "image/webp")) -> bool:
    return mimetype in allowed


@web_bp.route("/")
def index():
    return render_template("index.html")


@web_bp.route("/model_info")
def model_info():
    return render_template("model.html")


@web_bp.route("/performance")
def performance():
    return render_template("performance.html")


@web_bp.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == "GET":
        return render_template("predict.html")

    if "image" not in request.files:
        flash("No file part")
        return redirect(request.url)

    file = request.files["image"]
    if file.filename == "":
        flash("No selected file")
        return redirect(request.url)

    original_filename = secure_filename(file.filename) or "upload.jpg"
    if not _allowed_file(original_filename):
        flash("Invalid file type. Please upload JPG, JPEG, PNG, or WEBP.")
        return redirect(request.url)

    if not _allowed_mimetype(file.mimetype):
        flash("Invalid file mimetype. Please upload a valid image.")
        return redirect(request.url)

    base, ext = os.path.splitext(original_filename)
    if not ext:
        ext = ".jpg"
    filename = f"{base}_{uuid.uuid4().hex[:6]}{ext}"
    save_path = Path(web_bp.root_path).parent.parent / "static" / "uploads" / filename

    try:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        file.save(save_path)
    except Exception as e:
        flash(f"Error saving file: {e}")
        return redirect(request.url)

    model = load_model()
    if model is None:
        flash("Model not loaded. Ensure ultralytics is installed and best (1).pt is in models/.")
        return redirect(request.url)

    try:
        detections, _ = run_inference_on_path(model, str(save_path), conf=0.25)
        if detections:
            unique = sorted({d["class"] for d in detections})
            flash(f"Detection successful! Found {len(detections)} object(s): {', '.join(unique)}")
        else:
            flash("No objects detected. Try another image or verify the model.")
    except Exception as e:
        flash(f"Error running model: {e}")

    return redirect(url_for("web.predict"))


