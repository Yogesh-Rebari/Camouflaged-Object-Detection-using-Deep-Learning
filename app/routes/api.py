from flask import Blueprint, jsonify, request

from app.services.model_service import load_model, decode_base64_image

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/live_detect", methods=["POST"])
def live_detect():
    if not request.is_json:
        return jsonify({"success": False, "error": "Request must be JSON"}), 400

    data = request.get_json(silent=True) or {}
    image_b64 = data.get("image")
    if not image_b64:
        return jsonify({"success": False, "error": "Missing image field"}), 400

    model = load_model()
    if model is None:
        return jsonify({"success": False, "error": "Model not loaded"}), 503

    img = decode_base64_image(image_b64)
    if img is None:
        return jsonify({"success": False, "error": "Invalid image data"}), 400

    try:
        results = model(img, imgsz=640, conf=0.25, verbose=False)
        detections = []
        boxes = getattr(results[0], "boxes", None)
        if boxes is not None and len(boxes) > 0:
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
                except Exception:
                    continue

        annotated = results[0].plot(line_width=3)
        try:
            from app.services.model_service import cv2, Image  # reuse already-imported refs
            if cv2 is not None and Image is not None:
                annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
                annotated_pil = Image.fromarray(annotated_rgb)
            elif Image is not None:
                annotated_pil = Image.fromarray(annotated)
            else:
                annotated_pil = None
        except Exception:
            annotated_pil = None

        annotated_base64 = None
        if annotated_pil is not None:
            import base64
            import io

            buffer = io.BytesIO()
            annotated_pil.save(buffer, format="JPEG", quality=90)
            annotated_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return jsonify(
            {
                "success": True,
                "detections": detections,
                "count": len(detections),
                "annotated_image": f"data:image/jpeg;base64,{annotated_base64}" if annotated_base64 else None,
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": f"Detection failed: {str(e)}"}), 500


@api_bp.route("/status", methods=["GET"])
def status():
    model = load_model()
    return jsonify({"success": model is not None, "model_loaded": model is not None})


