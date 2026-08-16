"""
config.py
Shared constants: backend URL, auth storage path, email regex, validator metadata.
"""

import os
import re

# ----------------------------------------------------------------------
# Backend
# ----------------------------------------------------------------------
# NOTE: demo mode (api.py) does not use this — it simulates everything
# locally. This is kept only for when you swap in the real backend later.
DEFAULT_BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
    )

# ----------------------------------------------------------------------
# Auth
# ----------------------------------------------------------------------
USERS_DB_PATH = os.path.join(os.path.dirname(__file__), "users.json")
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9.-]+$")
MIN_PASSWORD_LENGTH = 8

# ----------------------------------------------------------------------
# Validators (matches the 6 validators in the architecture diagram)
# ----------------------------------------------------------------------
VALIDATOR_META = {
    "syntax":        {"label": "Syntax",             "icon": "🧩", "color": "#4C6EF5"},
    "formatting":    {"label": "Formatting",          "icon": "🧹", "color": "#12B886"},
    "security":      {"label": "Security",            "icon": "🔒", "color": "#E64980"},
    "configuration": {"label": "Configuration",       "icon": "⚙️", "color": "#F76707"},
    "best_practice": {"label": "Best Practice",       "icon": "✅", "color": "#20C997"},
    "optimization":  {"label": "Cost Optimization",   "icon": "💰", "color": "#FAB005"},
}