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
    global YOLO, YOLO_AVAILABLE, _last_error
    if SKIP_YOLO_IMPORT:
        print("[WARN] SKIP_YOLO_IMPORT is set - skipping YOLO import.")
        return
    try:
        # Patch torch.load for PyTorch 2.6+ compatibility
        import torch
        # Patch torch.load to set weights_only=False by default for YOLO models
        original_torch_load = torch.load
        def patched_torch_load(*args, **kwargs):
            # Only patch if weights_only is not explicitly set
            if 'weights_only' not in kwargs:
                kwargs['weights_only'] = False
            return original_torch_load(*args, **kwargs)
        torch.load = patched_torch_load
        print("[OK] Patched torch.load for PyTorch 2.6+ compatibility (weights_only=False)")

        from ultralytics import YOLO as _YOLO

        YOLO = _YOLO
        YOLO_AVAILABLE = True
        if not callable(YOLO):
            print("[WARN] YOLO class not callable")
            YOLO_AVAILABLE = False
    except Exception as e:
        _last_error = f"YOLO import failed: {e}"
        print(f"[ERROR] {_last_error}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        YOLO = None
        YOLO_AVAILABLE = False


def _import_image_libs() -> None:
    global Image, cv2, np
    if SKIP_IMAGE_IMPORTS:
        print("[WARN] SKIP_IMAGE_IMPORTS is set - skipping Pillow/OpenCV/numpy.")
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
_last_error: Optional[str] = None


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
    global _last_error
    if not YOLO_AVAILABLE or YOLO is None:
        _last_error = "Cannot load model: YOLO not available"
        print(f"[ERROR] {_last_error}")
        return None
    if _model_cache is not None:
        return _model_cache

    models_dir: Path = current_app.config["MODELS_DIR"]
    discovered = _discover_model_paths(models_dir)
    print(f"Searching for model files in: {models_dir}")
    print(f"Discovered models: {discovered}")

    for path in discovered:
        # Resolve path to absolute before checking
        resolved_path = path.resolve() if not path.is_absolute() else path
        if resolved_path.exists():
            try:
                print(f"Attempting to load model from: {resolved_path}")
                _model_cache = YOLO(str(resolved_path))
                print(f"[OK] Model loaded: {resolved_path}")
                return _model_cache
            except Exception as e:
                _last_error = f"Error loading model from {resolved_path}: {e}"
                print(f"[ERROR] {_last_error}")
                import traceback
                print(f"   Traceback: {traceback.format_exc()}")
                _model_cache = None
                continue

    # fallback default
    try:
        print("Loading default yolov8n.pt ...")
        _model_cache = YOLO("yolov8n.pt")
        return _model_cache
    except Exception as e:
        _last_error = f"Error loading default model: {e}"
        print(f"[ERROR] {_last_error}")
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
    if not image_b64 or not image_b64.startswith("data:image"):
        print("[WARN] Invalid base64 image format - must start with 'data:image'")
        return None
    try:
        header, encoded = image_b64.split(",", 1)
        data = base64.b64decode(encoded)
        if np is None or cv2 is None:
            print("[ERROR] Image processing libraries (numpy/cv2) not available for base64 decode.")
            return None
        image_array = np.frombuffer(data, dtype=np.uint8)
        img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        if img is None:
            print("[ERROR] Failed to decode image from base64 data")
            return None
        print(f"[OK] Successfully decoded base64 image: shape={img.shape}")
        return img
    except Exception as e:
        print(f"[ERROR] Base64 decode error: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return None


def get_last_model_error() -> Optional[str]:
    """Return the last model/import error message, if any."""
    return _last_error


