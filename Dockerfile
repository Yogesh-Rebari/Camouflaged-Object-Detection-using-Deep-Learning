# CPU Dockerfile for YOLOv8 Flask app
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . /app

# Upgrade pip
RUN pip install --upgrade pip

# Install CPU PyTorch - adjust version if required
RUN pip install "torch==2.9.1+cpu" --index-url https://download.pytorch.org/whl/cpu

# Install rest of requirements
RUN pip install -r requirements.txt

# Create uploads dir
RUN mkdir -p /app/static/uploads

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production
EXPOSE 5000

CMD ["python", "app.py"]
