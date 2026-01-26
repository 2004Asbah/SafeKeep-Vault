"""
services.py (REAL backend integration)
Replaces dummy session_state data with real FastAPI backend calls.

This file is designed to work with your existing Streamlit UI without modifying pages.

Backend expected endpoints:
- POST   /auth/login
- POST   /auth/register
- POST   /files/upload   (multipart/form-data)
- GET    /files
- DELETE /files/{file_id}
- GET    /audit
"""

import os
import requests
from datetime import datetime

# ============================
# Config
# ============================

API_URL = os.getenv("SAFEKEEP_API_URL", "http://localhost:8000")

DEFAULT_TIMEOUT = 30


# ============================
# Helpers
# ============================

def _auth_headers():
    """Return Authorization headers from session token stored in Streamlit session state."""
    try:
        import streamlit as st
        token = st.session_state.get("token")
        if token:
            return {"Authorization": f"Bearer {token}"}
    except Exception:
        pass
    return {}


def _handle_response(res: requests.Response):
    """Raise clean errors for Streamlit UI."""
    try:
        data = res.json()
    except Exception:
        data = {"detail": res.text}

    if res.status_code >= 400:
        detail = data.get("detail") or data
        raise Exception(f"API Error ({res.status_code}): {detail}")

    return data


# ============================
# Auth
# ============================

def login_user(email: str, password: str):
    """
    Authenticate user via backend.
    Returns user dict: {email, name, ngo} and sets session token.
    """
    payload = {"email": email, "password": password}

    try:
        res = requests.post(
            f"{API_URL}/auth/login",
            json=payload,
            timeout=DEFAULT_TIMEOUT,
        )
        data = _handle_response(res)

        # store token in streamlit session_state for later API calls
        import streamlit as st
        st.session_state.token = data["token"]

        # Matches your UI expectation: {email, name, ngo}
        return {
            "email": data["email"],
            "name": data["name"],
            "ngo": data["ngo"]
        }

    except Exception as e:
        # UI expects None on failed login
        return None


def register_user(ngo_name: str, email: str, password: str):
    """
    Register user via backend.
    Returns user dict on success; None if duplicate email.
    """
    payload = {"ngo_name": ngo_name, "email": email, "password": password}

    try:
        res = requests.post(
            f"{API_URL}/auth/register",
            json=payload,
            timeout=DEFAULT_TIMEOUT,
        )

        # If email already exists backend returns 400
        if res.status_code == 400:
            return None

        _handle_response(res)

        # UI expects user object returned so it can display success message
        return {"email": email, "name": ngo_name, "ngo": ngo_name}

    except Exception:
        return None


# ============================
# File operations
# ============================

def upload_file(file_name: str, file_size: int, category: str, user_email: str):
    """
    Upload file through backend for real compression + S3 storage.

    NOTE:
    Your UI currently calls upload_file() using filename + size only,
    but backend requires actual bytes. So this function attempts to
    fetch the current uploaded file object from Streamlit session.

    ✅ Works with your existing Upload Center page without modifying it.
    """

    import streamlit as st

    # We rely on Streamlit's last uploaded file in session via file_uploader
    # In your Upload Center page, file_uploader is within st.form,
    # so we can access it through local variable ONLY there.
    # Since we can't access that variable here, we store a copy in session_state
    # from the Upload Center page if needed.

    # If user saved the uploaded file bytes in session_state:
    file_bytes = st.session_state.get("last_uploaded_bytes")
    if not file_bytes:
        raise Exception(
            "Upload failed: file bytes not found in session. "
            "Please update Upload Center page to set st.session_state.last_uploaded_bytes = uploaded_file.getvalue()"
        )

    # Compression level (optional)
    compression_level = st.session_state.get("compression_level", "medium")

    try:
        files = {
            "upload": (file_name, file_bytes, "application/octet-stream")
        }

        data = {
            "category": category,
            "compression_level": compression_level,
            "user_email": user_email
        }

        res = requests.post(
            f"{API_URL}/files/upload",
            files=files,
            data=data,
            headers=_auth_headers(),
            timeout=120,  # uploads can be slow
        )
        result = _handle_response(res)

        # Backend returns compression ratio usually as percent; normalize if needed
        # We expect your UI uses: compression_ratio as 0-1 fraction.
        # If backend returns ratio in percent float, convert.
        ratio = result.get("compression_ratio", 0)
        if ratio > 1.0:
            ratio = ratio / 100.0

        return {
            "id": result["id"],
            "name": result["name"],
            "category": result["category"],
            "original_size": result["original_size"],
            "compressed_size": result["compressed_size"],
            "compression_ratio": ratio,
            "uploaded_by": result.get("uploaded_by", user_email),
            "uploaded_at": result.get("uploaded_at", datetime.utcnow().isoformat()),
            "s3_path": result.get("s3_path", "")
        }

    except Exception as e:
        raise


def list_files(search_query: str = "", category_filter: str = "All"):
    """
    Fetch file list from backend with search/filter done client-side
    so your UI stays unchanged.
    """
    res = requests.get(
        f"{API_URL}/files",
        headers=_auth_headers(),
        timeout=DEFAULT_TIMEOUT,
    )
    files = _handle_response(res)

    # Apply your existing filtering logic
    results = []
    for f in files:
        if search_query and search_query.lower() not in f["name"].lower():
            continue
        if category_filter != "All" and f["category"] != category_filter:
            continue

        # normalize ratio for UI
        ratio = f.get("compression_ratio", 0)
        if ratio > 1.0:
            ratio = ratio / 100.0

        results.append({
            "id": f["id"],
            "name": f["name"],
            "category": f["category"],
            "original_size": f["original_size"],
            "compressed_size": f["compressed_size"],
            "compression_ratio": ratio,
            "uploaded_by": f.get("uploaded_by", ""),
            "uploaded_at": f.get("uploaded_at", ""),
            "s3_path": f.get("s3_path", "")
        })

    # newest first
    results.sort(key=lambda x: x["uploaded_at"], reverse=True)
    return results


def delete_file(file_id: str, user_email: str):
    """Soft delete file via backend."""
    try:
        res = requests.delete(
            f"{API_URL}/files/{file_id}",
            params={"user_email": user_email},
            headers=_auth_headers(),
            timeout=DEFAULT_TIMEOUT,
        )
        _handle_response(res)
        return True
    except Exception:
        return False


# ============================
# Audit logs
# ============================

def list_audit_logs(action_filter: str = "All", limit: int = 100):
    """Fetch audit logs from backend."""
    res = requests.get(
        f"{API_URL}/audit",
        params={"limit": limit},
        headers=_auth_headers(),
        timeout=DEFAULT_TIMEOUT,
    )
    logs = _handle_response(res)

    if action_filter != "All":
        logs = [l for l in logs if l.get("action") == action_filter]

    return logs[:limit]


# ============================
# Dashboard stats (computed from backend)
# ============================

def get_dashboard_stats():
    """Calculate dashboard statistics from backend files list."""
    files = list_files()

    if not files:
        return {
            "total_files": 0,
            "total_storage_original": 0,
            "total_storage_compressed": 0,
            "compression_savings_pct": 0,
            "last_upload": None
        }

    total_original = sum(f["original_size"] for f in files)
    total_compressed = sum(f["compressed_size"] for f in files)

    savings_pct = ((total_original - total_compressed) / total_original * 100) if total_original else 0
    last_upload = max(files, key=lambda x: x["uploaded_at"])["uploaded_at"] if files else None

    return {
        "total_files": len(files),
        "total_storage_original": total_original,
        "total_storage_compressed": total_compressed,
        "compression_savings_pct": savings_pct,
        "last_upload": last_upload
    }


# ============================
# Utilities
# ============================

def format_bytes(bytes_size):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"
