import os
from pathlib import Path


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_secret_for_flash_messages")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    MODELS_DIR = Path(__file__).resolve().parent / "models"
    UPLOAD_FOLDER = Path(__file__).resolve().parent / "static" / "uploads"
    DEBUG = False


class DevConfig(BaseConfig):
    DEBUG = True


class ProdConfig(BaseConfig):
    DEBUG = False


