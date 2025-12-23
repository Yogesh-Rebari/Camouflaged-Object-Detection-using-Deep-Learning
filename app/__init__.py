import os
from flask import Flask
from config import DevConfig, ProdConfig


def create_app() -> Flask:
    """Application factory."""
    app = Flask(__name__, template_folder="../templates", static_folder="../static")

    # Choose config class based on ENV
    env = os.environ.get("FLASK_ENV", "development").lower()
    if env == "production":
        app.config.from_object(ProdConfig)
    else:
        app.config.from_object(DevConfig)

    # Ensure upload/models directories exist
    app.config["UPLOAD_FOLDER"].mkdir(parents=True, exist_ok=True)
    app.config["MODELS_DIR"].mkdir(parents=True, exist_ok=True)

    # Register blueprints
    from app.routes.web import web_bp
    from app.routes.api import api_bp

    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp)

    # Inject common template vars
    from datetime import datetime

    @app.context_processor
    def inject_globals():
        return {"current_year": datetime.now().year}

    return app


