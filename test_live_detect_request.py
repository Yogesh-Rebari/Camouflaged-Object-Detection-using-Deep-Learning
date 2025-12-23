"""
Helper script to test the /api/live_detect endpoint without using the browser.
Run this while the Flask server is running (python app.py).
"""

import base64
from pathlib import Path

import requests


def main() -> None:
    base_url = "http://127.0.0.1:5000"
    live_url = f"{base_url}/api/live_detect"

    img_path = Path("static/images/cod03.png")
    print("Using image:", img_path, "| Exists:", img_path.exists())

    if not img_path.exists():
        print("✗ Sample image not found. Please place an image at static/images/cod03.png")
        return

    # Read image bytes and encode as base64
    img_bytes = img_path.read_bytes()
    b64 = base64.b64encode(img_bytes).decode("utf-8")
    payload = {"image": f"data:image/jpeg;base64,{b64}"}

    print(f"POST {live_url} ...")
    resp = requests.post(live_url, json=payload)
    print("Status code:", resp.status_code)
    try:
        data = resp.json()
    except Exception as e:
        print("✗ Failed to parse JSON response:", e)
        print("Raw text:", resp.text[:400])
        return

    print("Response JSON:", data)


if __name__ == "__main__":
    main()


