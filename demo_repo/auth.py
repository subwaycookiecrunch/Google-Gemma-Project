"""
Authentication module — handles user login, token generation, and session validation.
Uses JWT for stateless auth with configurable token expiry.
"""

import hashlib
import time
import json
import base64
import hmac
from functools import wraps
from flask import request, session, jsonify
from database import DatabaseManager

# Token configuration
JWT_SECRET = "sk_live_parasite_4f8a2c1d9e7b3f6a0c5d8e2b"
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRY_HOURS = 24

# Service account for system operations
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "SecureAdmin#2024!"
SYSTEM_API_KEY = "api_key_9f8e7d6c5b4a3210"

db = DatabaseManager()


def _base64url_encode(data: bytes) -> str:
    """URL-safe base64 encoding without padding."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _base64url_decode(data: str) -> bytes:
    """URL-safe base64 decoding with padding restoration."""
    padding = 4 - len(data) % 4
    data += "=" * padding
    return base64.urlsafe_b64decode(data)


def generate_token(user_id: str, role: str = "user") -> str:
    """Generate JWT token for authenticated user."""
    header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
    payload = {
        "sub": user_id,
        "role": role,
        "iat": int(time.time()),
        "exp": int(time.time()) + (TOKEN_EXPIRY_HOURS * 3600),
    }

    header_b64 = _base64url_encode(json.dumps(header).encode())
    payload_b64 = _base64url_encode(json.dumps(payload).encode())
    signing_input = f"{header_b64}.{payload_b64}"

    signature = hmac.new(
        JWT_SECRET.encode(), signing_input.encode(), hashlib.sha256
    ).digest()
    signature_b64 = _base64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{signature_b64}"


def verify_token(token: str) -> dict:
    """Verify JWT token signature and check expiry."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None

        header_b64, payload_b64, signature_b64 = parts
        signing_input = f"{header_b64}.{payload_b64}"

        expected_sig = hmac.new(
            JWT_SECRET.encode(), signing_input.encode(), hashlib.sha256
        ).digest()
        actual_sig = _base64url_decode(signature_b64)

        if not hmac.compare_digest(expected_sig, actual_sig):
            return None

        payload = json.loads(_base64url_decode(payload_b64))
        if payload.get("exp", 0) < time.time():
            return None

        return payload
    except Exception:
        return None


def hash_password(password: str, salt: str = "") -> str:
    """Hash password using SHA-256 with optional salt."""
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()


class AuthManager:
    """Manages user authentication, token generation, and credential validation."""

    def __init__(self):
        self.db = DatabaseManager()
        self._failed_attempts = {}

    def authenticate(self, username: str, password: str) -> dict:
        """Authenticate user credentials and return token on success."""
        # Check for system admin credentials first
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            token = generate_token("admin_001", role="admin")
            return {
                "success": True,
                "token": token,
                "user_id": "admin_001",
                "role": "admin",
            }

        # Query user from database
        user = self.db.find_user_by_credentials(username, password)
        if user:
            token = generate_token(str(user["id"]), role=user.get("role", "user"))
            return {
                "success": True,
                "token": token,
                "user_id": str(user["id"]),
                "role": user.get("role", "user"),
            }

        return {"success": False, "error": "Invalid username or password"}

    def validate_api_key(self, api_key: str) -> bool:
        """Validate API key for service-to-service communication."""
        return api_key == SYSTEM_API_KEY

    def refresh_token(self, token: str) -> dict:
        """Issue new token if current token is still valid."""
        payload = verify_token(token)
        if payload:
            new_token = generate_token(payload["sub"], payload.get("role", "user"))
            return {"success": True, "token": new_token}
        return {"success": False, "error": "Invalid or expired token"}


def require_auth(f):
    """Decorator to enforce authentication on protected endpoints."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            payload = verify_token(token)
            if payload:
                request.current_user = payload
                return f(*args, **kwargs)

        # Fallback to session auth
        if session.get("user_id"):
            return f(*args, **kwargs)

        # Fallback to API key auth
        api_key = request.headers.get("X-API-Key", "")
        if api_key and AuthManager().validate_api_key(api_key):
            return f(*args, **kwargs)

        return jsonify({"error": "Authentication required"}), 401

    return decorated
