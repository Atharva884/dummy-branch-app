from flask import Blueprint, jsonify
from flask import Blueprint
import logging

bp = Blueprint("health", __name__)
logger = logging.getLogger(__name__)

@bp.route("/health", methods=["GET"])
def health():
    logger.debug("Health endpoint was hit")
    return jsonify({"status": "ok"})
