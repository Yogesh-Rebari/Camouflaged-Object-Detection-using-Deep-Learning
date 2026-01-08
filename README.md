# Camouflaged Military Object Detection (YOLOv8)

Modern Flask-based web app for image upload and live webcam detection using a custom YOLOv8 model. Includes LandingLens-inspired UI, prioritized model loading (`best (1).pt`), and API endpoints for live detection.

![Architecture](static/images/system%20archihtecture.png)

## Project Highlights
- YOLOv8 custom model with prioritized load order (`models/best (1).pt` → fallback `yolov8n.pt`).
- Live detection via `/api/live_detect` (base64 frames) with annotated frame return.
- Upload workflow with extension/mimetype checks and 16 MB limit.
- Clean structure with blueprints and service layer:
  - `app/` (factory, routes, services)
  - `templates/`, `static/`
  - `models/` (place `best (1).pt`)
- LandingLens-inspired frontend (minimal, light theme).

## Repository Structure
```
.
├─ app/
│  ├─ __init__.py          # app factory, config load, blueprints
│  ├─ routes/
│  │  ├─ web.py            # HTML routes (/ , /model_info, /performance, /predict)
│  │  └─ api.py            # JSON API (/api/live_detect, /api/status)
│  └─ services/
│     └─ model_service.py  # YOLO load, inference, base64 decode
├─ static/
│  ├─ css/, js/, images/   # assets and provided diagrams/figures
│  └─ uploads/             # runtime annotated outputs
├─ templates/              # Jinja2 templates
├─ models/                 # place best (1).pt here
├─ app.py                  # entrypoint (uses create_app)
├─ config.py               # Dev/Prod configs (env-driven)
├─ requirements.txt
└─ tests/ (suggested)      # add pytest-based API checks
```

## Quickstart (Local)

**📖 For detailed step-by-step instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md)**

Quick start:

1) **Python env**
```bash
python -m venv venv
venv\Scripts\activate   # on Windows
# or: source venv/bin/activate
```

2) **Install dependencies**
```bash
pip install -r requirements.txt
pip install ultralytics   # if not pinned in requirements.txt
```

3) **Add your model**
- Place `best (1).pt` in `models/`.

4) **Run**
```bash
python app.py
# Visit: http://127.0.0.1:5000/predict
```

## API
- `POST /api/live_detect`
  - Body (JSON): `{ "image": "data:image/jpeg;base64,...." }`
  - Response: `{ success, detections, count, annotated_image }`
- `GET /api/status`
  - Returns `{ model_loaded: bool }`

## Security & Safety
- `SECRET_KEY` and limits from env (`config.py`); defaults provided for dev.
- Upload hardening: extension & mimetype checks; 16 MB cap.
- Model caching avoids reload on each request.

## Model & Pipeline Visuals

Architecture (YOLOv8 Backbone/Neck/Head):
![YOLOv8 Architecture](static/images/Image01.png)

Dataset examples:
![Dataset Samples](static/images/Image02.png)
![More Samples](static/images/Image03.png)
![Additional Samples](static/images/Image04.png)

System flow:
![System Flow](static/images/system%20archihtecture.png)

Confusion matrix:
![Confusion Matrix](static/images/Comfusion%20matrix.png)

Confidence curve:
![Confidence Curve](static/images/Confidence%20curve.png)

Precision-Recall curve:
![Precision Recall Curve](static/images/precision%20recall%20curve.png)

Precision-Confidence matrix:
![Precision Confidence Matrix](static/images/presision%20confidence%20matrix.png)

## Testing (suggested)
- Convert existing helper scripts into pytest tests:
  - `/predict` upload success
  - `/api/live_detect` JSON success with sample base64
  - Error cases: missing file, bad mimetype, missing image field


### Production Checklist:
- ✅ `wsgi.py` created for production servers
- ✅ `gunicorn` added to requirements.txt
- ✅ Security headers configured
- ✅ Error handling for production
- ✅ Environment-based configuration
- ✅ Logging configured

**📖 Full deployment guide:** [DEPLOYMENT.md](DEPLOYMENT.md)

## Team & Contributions

Below are the core contributors to this project along with their primary roles and a short list of contributions. The images displayed are for visual reference.

<p align="center">
  <img src="static/images/Osama.png" alt="Osama Mikrani" width="160" style="margin:8px; border-radius:8px; box-shadow:0 2px 6px rgba(0,0,0,0.12);">
  <img src="static/images/Raghu.png" alt="Raghu G R" width="160" style="margin:8px; border-radius:8px; box-shadow:0 2px 6px rgba(0,0,0,0.12);">
  <img src="static/images/Yogesh.png" alt="Yogesh Rebari" width="160" style="margin:8px; border-radius:8px; box-shadow:0 2px 6px rgba(0,0,0,0.12);">
</p>

### Osama Mikrani — Lead Backend & Deployment Engineer
- Role: Backend engineer and deployment lead
- Contributions:
  - Implemented the Flask application factory and blueprint structure
  - Built the model service (loading, caching, inference helpers)
  - Added production entrypoints (`wsgi.py`, `Procfile`) and deployment guidance
  - Wrote the model discovery and fallback logic

### Pavan U — Data & Augmentation Engineer
- Role: Dataset engineer and augmentation specialist
- Contributions:
  - Curated and preprocessed the training/validation datasets
  - Designed augmentation pipelines and data formatting for YOLOv8
  - Assisted with label quality checks and dataset splits for robust evaluation

### Raghu G R — Model Architect & Evaluation Lead
- Role: Model architecture and evaluation
- Contributions:
  - Selected and tuned the YOLOv8 variant for this task
  - Performed model fine-tuning, hyperparameter selection, and evaluation
  - Produced the performance artifacts (confusion matrices, PR curves) shown in the repo

### Yogesh Rebari — Frontend & Integration Engineer
- Role: Frontend developer and integration lead
- Contributions:
  - Implemented the UI templates, upload flow, and the live-detection client
  - Integrated the frontend with the inference API and improved UX for results
  - Wrote documentation and setup guides for local and cloud deployment

If you want me to include short links to each contributor's GitHub profile or a short contact line, tell me which handles to add and I will update the README accordingly.


