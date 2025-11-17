from flask import Flask
import logging
import os

from .config import Config

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config())

    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    numeric_level = getattr(logging, log_level, logging.INFO)

    logging.basicConfig(level=numeric_level)

    app.logger.setLevel(numeric_level)
    app.logger.info(f"Log level set to {log_level}")

    # Lazy imports to avoid circular deps during app init
    from .routes.health import bp as health_bp
    from .routes.loans import bp as loans_bp
    from .routes.stats import bp as stats_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(loans_bp, url_prefix="/api")
    app.register_blueprint(stats_bp, url_prefix="/api")

    return app
