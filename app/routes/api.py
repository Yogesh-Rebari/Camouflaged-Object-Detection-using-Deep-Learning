from flask import Blueprint, jsonify, request

from app.services.model_service import load_model, decode_base64_image
from app.services.model_service import get_last_model_error

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/live_detect", methods=["POST"])
def live_detect():
    print("[INFO] Live detect: Received API request.")
    if not request.is_json:
        print("[ERROR] Live detect: Request not JSON.")
        return jsonify({"success": False, "error": "Request must be JSON"}), 400

    data = request.get_json(silent=True) or {}
    image_b64 = data.get("image")
    if not image_b64:
        print("[ERROR] Live detect: Missing image field.")
        return jsonify({"success": False, "error": "Missing image field"}), 400

    model = load_model()
    if model is None:
        print("[ERROR] Live detect: Model not loaded.")
        return jsonify({"success": False, "error": "Model not loaded"}), 503

    print("[INFO] Live detect: Model loaded, decoding image...")
    img = decode_base64_image(image_b64)
    if img is None:
        print("[ERROR] Live detect: Invalid image data after decode.")
        return jsonify({"success": False, "error": "Invalid image data"}), 400
    
    # Validate image dimensions
    if len(img.shape) != 3 or img.shape[2] != 3:
        print(f"[ERROR] Live detect: Invalid image shape: {img.shape}")
        return jsonify({"success": False, "error": f"Invalid image format: expected 3-channel image, got shape {img.shape}"}), 400
    
    if img.shape[0] < 32 or img.shape[1] < 32:
        print(f"[WARN] Live detect: Image is very small: {img.shape}, may affect detection accuracy")
    
    print(f"[OK] Live detect: Image decoded successfully. Shape: {img.shape}, dtype: {img.dtype}")

    try:
        # Confidence threshold: lower = more detections (but more false positives)
        # Higher = fewer detections (but more accurate)
        # For camouflaged object detection, 0.25-0.3 is usually good
        conf_threshold = float(data.get("confidence", 0.25))
        conf_threshold = max(0.1, min(0.9, conf_threshold))  # Clamp between 0.1 and 0.9
        print(f"[INFO] Running detection with confidence threshold: {conf_threshold}")
        
        # Ensure image is in correct format (BGR for OpenCV, which YOLO expects)
        # The decode_base64_image already returns BGR format from cv2.imdecode
        results = model(img, imgsz=640, conf=conf_threshold, verbose=False)
        
        detections = []
        boxes = getattr(results[0], "boxes", None)
        print(f"[INFO] Found {len(boxes) if boxes is not None else 0} boxes in detection results")
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
                except Exception as box_error:
                    print(f"[WARN] Error processing box: {box_error}")
                    continue

        # Get annotated image from YOLO (this is resized to 640x640)
        annotated = results[0].plot(line_width=3)
        
        # Resize annotated image back to original video frame dimensions
        # This ensures the annotated image matches the video frame exactly
        original_height, original_width = img.shape[:2]
        annotated_resized = None
        
        try:
            from app.services.model_service import cv2, Image
            if cv2 is not None:
                # Resize annotated image to match original frame dimensions
                annotated_resized = cv2.resize(annotated, (original_width, original_height), interpolation=cv2.INTER_LINEAR)
                print(f"[INFO] Resized annotated image from {annotated.shape} to ({original_height}, {original_width})")
            
            # Convert to PIL for base64 encoding
            if annotated_resized is not None and Image is not None:
                annotated_rgb = cv2.cvtColor(annotated_resized, cv2.COLOR_BGR2RGB)
                annotated_pil = Image.fromarray(annotated_rgb)
            elif Image is not None:
                annotated_pil = Image.fromarray(annotated)
            else:
                annotated_pil = None
        except Exception as annotate_error:
            print(f"[WARN] Error creating annotated image: {annotate_error}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            annotated_pil = None

        annotated_base64 = None
        if annotated_pil is not None:
            import base64
            import io

            buffer = io.BytesIO()
            annotated_pil.save(buffer, format="JPEG", quality=90)
            annotated_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
            print(f"[OK] Created base64 annotated image: {len(annotated_base64)} bytes")

        print(f"[OK] Live detect: Detection completed. Detections: {len(detections)}")
        return jsonify(
            {
                "success": True,
                "detections": detections,
                "count": len(detections),
                "annotated_image": f"data:image/jpeg;base64,{annotated_base64}" if annotated_base64 else None,
            }
        )
    except Exception as e:
        print(f"[ERROR] Live detection error: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return jsonify({"success": False, "error": f"Detection failed: {str(e)}"}), 500


@api_bp.route("/status", methods=["GET"])
def status():
    model = load_model()
    last_error = get_last_model_error()
    return jsonify({
        "success": model is not None,
        "model_loaded": model is not None,
        "last_error": last_error,
    })


