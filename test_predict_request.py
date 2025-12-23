"""
Small helper script to test the /predict endpoint using a local sample image.
Run this while the Flask server is running (python app.py).
"""

import os
from pathlib import Path

import requests


def main() -> None:
    base_url = "http://127.0.0.1:5000"
    predict_url = f"{base_url}/predict"

    # Use an existing sample image from the project
    img_path = Path("static/images/cod03.png")
    print("Using image:", img_path, "| Exists:", img_path.exists())

    if not img_path.exists():
        print("✗ Sample image not found. Please place an image at static/images/cod03.png")
        return

    with img_path.open("rb") as f:
        files = {"image": (img_path.name, f, "image/png")}
        print(f"POST {predict_url} ...")
        resp = requests.post(predict_url, files=files, allow_redirects=True)

    print("Status code:", resp.status_code)
    # Show a small snippet of the returned HTML to see flash messages
    text = resp.text
    marker = "Failed to load model"
    if marker in text:
        print("✗ Response contains error message: 'Failed to load model'")
    else:
        print("✓ No 'Failed to load model' message found in response.")

    # Optionally show the first 400 characters for debugging
    print("\n--- Response preview (first 400 chars) ---")
    print(text[:400])


if __name__ == "__main__":
    main()


