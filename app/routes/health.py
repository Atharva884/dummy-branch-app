from flask import Blueprint, jsonify
from sqlalchemy import text
from app.extensions import db
import logging

bp = Blueprint("health", __name__)
logger = logging.getLogger(__name__)

@bp.route("/health", methods=["GET"])
def health_check():
    """
    Full health check including DB connectivity.
    """
    try:
        db.session.execute(text("SELECT 1"))
        db_status = "healthy"
        status_code = 200
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
        status_code = 500

    response = {
        "status": "ok" if db_status == "healthy" else "error",
        "database": db_status
    }

    logger.info("Health check hit: %s", response)
    return jsonify(response), status_code
