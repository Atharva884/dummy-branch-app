from flask import Flask
import logging
import os

from .config import Config
from app.extensions import db
from app.json_logger import JsonFormatter


def setup_logging():
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.handlers = [handler]

    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    root.setLevel(log_level)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    # Init DB
    db.init_app(app)

    # Structured JSON logging
    setup_logging()
    app.logger.info("Application started with JSON logging")

    # Register blueprints
    from .routes.health import bp as health_bp
    from .routes.loans import bp as loans_bp
    from .routes.stats import bp as stats_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(loans_bp, url_prefix="/api")
    app.register_blueprint(stats_bp, url_prefix="/api")

    return app
