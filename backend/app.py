"""
AgriScheme Backend — Flask application factory.
Production-ready setup with CORS, compression, security headers, and logging.
"""
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from flask_compress import Compress

from config import FLASK_DEBUG, FLASK_PORT
from db import init_indexes
from routes import api_bp

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------
def create_app():
    app = Flask(__name__)

    # --- CORS ---
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # --- Response compression (gzip) ---
    Compress(app)

    # --- Security headers ---
    @app.after_request
    def _add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Cache-Control"] = "no-store"
        return response

    # --- Register blueprints ---
    app.register_blueprint(api_bp, url_prefix="/api")

    # --- Health-check (root) ---
    @app.route("/", methods=["GET"])
    def health():
        return jsonify({
            "status": "ok",
            "service": "AgriScheme Backend",
            "version": "1.0.0",
        })

    return app

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app = create_app()

    # Initialise DB indexes (non-fatal on failure)
    try:
        init_indexes()
    except Exception as exc:
        logger.warning("Could not initialise indexes: %s", exc)

    app.run(debug=FLASK_DEBUG, host="0.0.0.0", port=FLASK_PORT)
