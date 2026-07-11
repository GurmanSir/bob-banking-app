"""
Banking Application — Flask entry point.

Responsibilities:
  - Create the Flask app instance with correct template/static paths.
  - Set the SECRET_KEY for session signing.
  - Register route blueprints.
  - Initialise the SQLite database on startup.
  - Start the development server when run directly.
"""

import os
import sys

from flask import Flask

# ---------------------------------------------------------------------------
# Path resolution — ensure BACKEND/ is on sys.path so that sibling packages
# (models, services, controllers, routes) import correctly when app.py is
# run from *any* working directory.
# ---------------------------------------------------------------------------
_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

_PROJECT_ROOT = os.path.dirname(_BACKEND_DIR)

# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------
app = Flask(
    __name__,
    template_folder=os.path.join(_PROJECT_ROOT, "FRONTEND", "templates"),
    static_folder=os.path.join(_PROJECT_ROOT, "FRONTEND", "static"),
)

app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

# ---------------------------------------------------------------------------
# Register blueprints
# ---------------------------------------------------------------------------
from routes.auth_routes import auth_bp          # noqa: E402
from routes.account_routes import account_bp    # noqa: E402

app.register_blueprint(auth_bp)
app.register_blueprint(account_bp)

# ---------------------------------------------------------------------------
# Initialise database (creates tables + seeds demo data if not present)
# ---------------------------------------------------------------------------
from models.db import init_db   # noqa: E402

with app.app_context():
    init_db()

# ---------------------------------------------------------------------------
# Development server entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
