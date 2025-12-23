# Troubleshooting Guide

## Common Issues and Solutions

### Issue 1: "YOLO (ultralytics) library is not installed"

**Symptoms:**
- Error message: "YOLO (ultralytics) library is not installed. Please install it: pip install ultralytics"
- Model detection not working

**Solutions:**

1. **Install ultralytics:**
   ```bash
   pip install ultralytics
   ```
   
   Or if that doesn't work:
   ```bash
   pip install --user ultralytics
   python -m pip install ultralytics
   ```

2. **Verify installation:**
   ```bash
   python -c "from ultralytics import YOLO; print('YOLO installed successfully')"
   ```

3. **Check Python environment:**
   - Make sure you're using the same Python interpreter for both installation and running Flask
   - Check which Python is being used: `python --version`
   - Check pip location: `python -m pip --version`

4. **Restart Flask server:**
   - After installing, you MUST restart the Flask server
   - Stop the server (Ctrl+C) and run `python app.py` again

### Issue 2: "Failed to load model"

**Symptoms:**
- Error: "Failed to load model. Please ensure best (1).pt or model.pt exists in the models/ directory"

**Solutions:**

1. **Check model file location:**
   - Primary model file should be at: `models/best (1).pt`
   - (Optional fallback) `models/model.pt`
   - Verify file exists: Check the `models/` folder

2. **Check file permissions:**
   - Ensure the model file is readable
   - On Windows, check file properties

3. **Check console output:**
   - Look at the Flask server console when it starts
   - It will show which model files were found/not found

4. **Model file naming:**
   - Supported names (in priority order):
     - `models/best (1).pt` (recommended)
     - `models/model.pt` (optional fallback)
     - `models/custom_yolov8.pt`
     - `models/best.pt`
     - `models/last.pt`

### Issue 3: Detection not working / No detections

**Symptoms:**
- Image uploads but no bounding boxes appear
- "No objects detected" message

**Solutions:**

1. **Check confidence threshold:**
   - Current threshold: 0.25 (25%)
   - Lower threshold = more detections (but more false positives)
   - Higher threshold = fewer detections (but more accurate)

2. **Check image quality:**
   - Ensure image is clear and not too dark/blurry
   - Try with different images

3. **Check model classes:**
   - The model is trained for camouflaged military soldier detection
   - It may not detect other objects well

4. **Check server console:**
   - Look for error messages in the Flask server output
   - Check if model loaded successfully at startup

### Issue 4: Live camera detection not working

**Symptoms:**
- Camera doesn't start
- "Unable to access camera" error

**Solutions:**

1. **Browser permissions:**
   - Grant camera permissions in browser settings
   - Chrome: Settings > Privacy > Site Settings > Camera
   - Firefox: Settings > Privacy & Security > Permissions > Camera

2. **HTTPS requirement:**
   - Some browsers require HTTPS for camera access
   - For local development, use `http://localhost:5000` (should work)
   - For production, use HTTPS

3. **Camera already in use:**
   - Close other applications using the camera
   - Restart browser if needed

4. **Check browser console:**
   - Open browser DevTools (F12)
   - Check Console tab for JavaScript errors

### Issue 5: Flask server won't start

**Solutions:**

1. **Check port availability:**
   - Port 5000 might be in use
   - Change port in `app.py`: `app.run(host="127.0.0.1", port=5001)`

2. **Check Python version:**
   - Requires Python 3.7+
   - Check: `python --version`

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Issue 6: Model loads but predictions fail

**Solutions:**

1. **Check image format:**
   - Supported: JPG, PNG, WEBP
   - Try converting image to JPG

2. **Check image size:**
   - Very large images may cause memory issues
   - Model automatically resizes to 640x640

3. **Check server logs:**
   - Look for specific error messages
   - Check if PIL/OpenCV are installed

## Quick Diagnostic Commands

```bash
# Check Python version
python --version

# Check if ultralytics is installed
python -c "from ultralytics import YOLO; print('OK')"

# Check if model file exists
python -c "import os; print('Model exists:', os.path.exists('models/model.pt'))"

# Check all dependencies
python check_imports.py

# List files in models directory
dir models  # Windows
ls models   # Linux/Mac
```

## Getting Help

1. **Check server console output** - Most errors are logged there
2. **Check browser console** (F12) - For frontend errors
3. **Verify all files are in place:**
   - `models/model.pt` exists
   - `app.py` is in root directory
   - All template files are in `templates/` folder

## Installation Checklist

- [ ] Python 3.7+ installed
- [ ] Flask installed: `pip install Flask`
- [ ] ultralytics installed: `pip install ultralytics`
- [ ] Model file placed in `models/model.pt`
- [ ] Flask server restarted after installation
- [ ] Browser camera permissions granted
