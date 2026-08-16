"""
auth.py
Lightweight local authentication: salted SHA-256 password hashing, users
stored in a local JSON file, email format enforced via regex.
"""

import json
import hashlib
import secrets
import os
from datetime import datetime

import streamlit as st

from config import USERS_DB_PATH, EMAIL_REGEX, MIN_PASSWORD_LENGTH


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email.strip()))


def load_users() -> dict:
    if not os.path.exists(USERS_DB_PATH):
        return {}
    try:
        with open(USERS_DB_PATH, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_users(users: dict) -> None:
    with open(USERS_DB_PATH, "w") as f:
        json.dump(users, f, indent=2)


def hash_password(password: str, salt: str | None = None) -> tuple[str,str]:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return digest, salt


def signup_user(name: str, email: str, password: str, confirm: str):
    """Returns (success: bool, message: str)."""
    email = email.strip().lower()

    if not name.strip():
        return False, "Name is required."
    if not is_valid_email(email):
        return False, "Please enter a valid email address."
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
    if password != confirm:
        return False, "Passwords do not match."

    users = load_users()
    if email in users:
        return False, "An account with this email already exists."

    digest, salt = hash_password(password)
    users[email] = {
        "name": name.strip(),
        "password_hash": digest,
        "salt": salt,
        "created_at": datetime.utcnow().isoformat(),
    }
    save_users(users)
    return True, "Account created successfully. Please log in."


def login_user(email: str, password: str):
    """Returns (success: bool, message: str). On success, sets session state."""
    email = email.strip().lower()

    if not is_valid_email(email):
        return False, "Please enter a valid email address."

    users = load_users()
    record = users.get(email)
    if not record:
        return False, "No account found with this email."

    digest, _ = hash_password(password, record["salt"])
    if digest != record["password_hash"]:
        return False, "Incorrect password."

    st.session_state.authenticated = True
    st.session_state.current_user = {"email": email, "name": record["name"]}
    return True, "Logged in."


def logout_user():
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.session_state.validation_results = None
    st.session_state.recommendations = []
    st.session_state.reviewed_tf = None
    st.session_state.original_tf = None