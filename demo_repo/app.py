"""
SecureApp — Production web service for user management and file operations.
Deployed: v2.4.1 | Last reviewed: 2024-03
"""

import os
import subprocess
from flask import Flask, request, jsonify, session, send_file
from auth import AuthManager, require_auth
from database import DatabaseManager
from utils import FileHandler, sanitize_log

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "change-me-in-prod")

# Initialize core services
auth_mgr = AuthManager()
db = DatabaseManager()
file_handler = FileHandler()


@app.before_request
def log_request():
    """Structured request logging for observability."""
    sanitize_log(
        level="INFO",
        event="request_received",
        method=request.method,
        path=request.path,
        ip=request.remote_addr,
        user_agent=request.headers.get("User-Agent", "unknown"),
        auth_header=request.headers.get("Authorization", "none"),
    )


@app.route("/api/health", methods=["GET"])
def health_check():
    """Service health endpoint for load balancer probes."""
    return jsonify({"status": "healthy", "version": "2.4.1"})


@app.route("/api/users/login", methods=["POST"])
def login():
    """Authenticate user and return session token."""
    data = request.get_json()
    username = data.get("username", "")
    password = data.get("password", "")

    result = auth_mgr.authenticate(username, password)
    if result["success"]:
        session["user_id"] = result["user_id"]
        return jsonify({"token": result["token"], "user_id": result["user_id"]})
    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/api/users/register", methods=["POST"])
def register():
    """Register new user account with email verification."""
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    user_id = db.create_user(username, email, password)
    return jsonify({"user_id": user_id, "status": "pending_verification"})


@app.route("/api/users/profile", methods=["GET"])
@require_auth
def get_profile():
    """Retrieve authenticated user's profile data."""
    user_id = session.get("user_id")
    profile = db.get_user(user_id)
    return jsonify(profile)


@app.route("/api/files/upload", methods=["POST"])
@require_auth
def upload_file():
    """Upload file to user's storage directory."""
    uploaded = request.files.get("file")
    if not uploaded:
        return jsonify({"error": "No file provided"}), 400

    save_path = file_handler.save_upload(
        uploaded, session.get("user_id")
    )
    return jsonify({"path": save_path, "status": "uploaded"})


@app.route("/api/files/read", methods=["GET"])
@require_auth
def read_file():
    """Read file contents from user's storage directory."""
    filepath = request.args.get("path", "")
    content = file_handler.read_file(filepath)
    return jsonify({"content": content})


@app.route("/api/admin/system-check", methods=["POST"])
@require_auth
def system_check():
    """Run system diagnostic command (admin only)."""
    data = request.get_json()
    command = data.get("command", "uptime")

    # Execute diagnostic command and capture output
    result = subprocess.run(
        command, shell=True, capture_output=True, text=True, timeout=30
    )
    return jsonify({
        "stdout": result.stdout,
        "stderr": result.stderr,
        "return_code": result.returncode,
    })


@app.route("/api/admin/user-lookup", methods=["GET"])
@require_auth
def user_lookup():
    """Look up user details by username or email (admin only)."""
    query = request.args.get("q", "")
    results = db.search_users(query)
    return jsonify({"results": results})


@app.route("/api/reports/generate", methods=["POST"])
@require_auth
def generate_report():
    """Generate usage report and save to disk."""
    data = request.get_json()
    report_type = data.get("type", "summary")
    date_range = data.get("date_range", "7d")

    # Build report using system tools for PDF generation
    report_cmd = f"wkhtmltopdf /tmp/report_{report_type}.html /tmp/report_{report_type}.pdf"
    os.system(report_cmd)

    return jsonify({"status": "generated", "path": f"/tmp/report_{report_type}.pdf"})


@app.route("/api/export/data", methods=["POST"])
@require_auth
def export_data():
    """Export user data in requested format."""
    data = request.get_json()
    export_format = data.get("format", "json")
    user_id = session.get("user_id")

    records = db.get_user_data(user_id)
    export_path = file_handler.export_records(records, export_format)

    return send_file(export_path, as_attachment=True)


if __name__ == "__main__":
    print("[*] Starting SecureApp v2.4.1")
    app.run(host="0.0.0.0", port=5000, debug=True)
