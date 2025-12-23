import base64
import io
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from flask import current_app

# Optional heavy deps
YOLO = None
YOLO_AVAILABLE = False
Image = None
cv2 = None
np = None

# Environment flags
SKIP_YOLO_IMPORT = str(os.environ.get("SKIP_YOLO_IMPORT", "")).lower() in ("1", "true", "yes")
SKIP_IMAGE_IMPORTS = (
    str(os.environ.get("SKIP_IMAGE_IMPORTS", "")).lower() in ("1", "true", "yes") or SKIP_YOLO_IMPORT
)


def _import_yolo() -> None:
    global YOLO, YOLO_AVAILABLE
    if SKIP_YOLO_IMPORT:
        print("⚠ SKIP_YOLO_IMPORT is set — skipping YOLO import.")
        return
    try:
        from ultralytics import YOLO as _YOLO

        YOLO = _YOLO
        YOLO_AVAILABLE = True
        if not callable(YOLO):
            print("⚠ YOLO class not callable")
            YOLO_AVAILABLE = False
    except Exception as e:
        print(f"❌ YOLO import failed: {e}")
        YOLO = None
        YOLO_AVAILABLE = False


def _import_image_libs() -> None:
    global Image, cv2, np
    if SKIP_IMAGE_IMPORTS:
        print("⚠ SKIP_IMAGE_IMPORTS is set — skipping Pillow/OpenCV/numpy.")
        return
    try:
        from PIL import Image as _Image
        Image = _Image
    except Exception:
        Image = None
    try:
        import cv2 as _cv2
        cv2 = _cv2
    except Exception:
        cv2 = None
    try:
        import numpy as _np
        np = _np
    except Exception:
        np = None


_import_yolo()
_import_image_libs()

# Model cache
_model_cache: Optional[Any] = None


def _discover_model_paths(models_dir: Path) -> List[Path]:
    candidates: List[Path] = []
    try:
        for fname in os.listdir(models_dir):
            if fname.lower().endswith(".pt"):
                candidates.append(models_dir / fname)
    except Exception:
        pass

    preferred = ["best(1).pt", "best (1).pt", "best.pt", "model.pt", "last.pt", "custom_yolov8.pt"]
    ordered: List[Path] = []

    def norm_name(p: Path) -> str:
        return p.name.strip().lower().replace(" ", "")

    for key in preferred:
        key_norm = key.replace(" ", "").lower()
        for c in list(candidates):
            if norm_name(c) == key_norm:
                ordered.append(c)
                candidates.remove(c)
    ordered.extend(candidates)
    ordered.append(Path("yolov8n.pt"))
    return ordered


def load_model() -> Optional[Any]:
    """Load YOLO model with caching."""
    global _model_cache
    if not YOLO_AVAILABLE or YOLO is None:
        print("❌ Cannot load model: YOLO not available")
        return None
    if _model_cache is not None:
        return _model_cache

    models_dir: Path = current_app.config["MODELS_DIR"]
    discovered = _discover_model_paths(models_dir)
    print(f"Searching for model files in: {models_dir}")
    print(f"Discovered models: {discovered}")

    for path in discovered:
        if path.is_absolute() and path.exists():
            try:
                print(f"Attempting to load model from: {path}")
                _model_cache = YOLO(str(path))
                print(f"✓ Model loaded: {path}")
                return _model_cache
            except Exception as e:
                print(f"❌ Error loading model from {path}: {e}")
                _model_cache = None
                continue

    # fallback default
    try:
        print("Loading default yolov8n.pt ...")
        _model_cache = YOLO("yolov8n.pt")
        return _model_cache
    except Exception as e:
        print(f"❌ Error loading default model: {e}")
        _model_cache = None
        return None


def run_inference_on_path(model: Any, path: str, conf: float = 0.25) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """Run YOLO inference on file path; return detections and annotated path."""
    results = model(path, imgsz=640, conf=conf, verbose=False)
    annotated = results[0].plot(line_width=2)
    annotated_filename = f"annotated_{os.path.basename(path)}"
    annotated_path = current_app.config["UPLOAD_FOLDER"] / annotated_filename

    try:
        if cv2 is not None and Image is not None:
            annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
            im_pil = Image.fromarray(annotated_rgb)
            im_pil.save(annotated_path)
        elif Image is not None:
            Image.fromarray(annotated).save(annotated_path)
        elif cv2 is not None:
            cv2.imwrite(str(annotated_path), annotated)
        else:
            annotated_path = None
    except Exception as e:
        print(f"Could not save annotated image: {e}")
        annotated_path = None

    detections: List[Dict[str, Any]] = []
    boxes = getattr(results[0], "boxes", None)
    if boxes is not None:
        for box in boxes:
            try:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf_val = float(box.conf[0].cpu().numpy())
                cls = int(box.cls[0].cpu().numpy())
                class_name = (
                    results[0].names[cls] if hasattr(results[0], "names") and cls < len(results[0].names) else f"class_{cls}"
                )
                detections.append(
                    {
                        "bbox": [float(x1), float(y1), float(x2), float(y2)],
                        "confidence": conf_val,
                        "class": class_name,
                        "class_id": cls,
                    }
                )
            except Exception as e:
                print(f"Error processing box: {e}")
                continue
    return detections, str(annotated_path) if annotated_path else None


def decode_base64_image(image_b64: str) -> Optional[Any]:
    """Decode data URL base64 image to numpy array (BGR)."""
    if not image_b64.startswith("data:image"):
        return None
    try:
        header, encoded = image_b64.split(",", 1)
        data = base64.b64decode(encoded)
        if np is None or cv2 is None:
            return None
        image_array = np.frombuffer(data, dtype=np.uint8)
        img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print(f"Base64 decode error: {e}")
        return None


