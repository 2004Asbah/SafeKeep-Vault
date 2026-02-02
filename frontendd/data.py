"""
Data layer - Persistent JSON storage
"""
import json
import os
from pathlib import Path
# pylint: disable=unused-import
import streamlit as st

DATA_DIR = Path("data")
UPLOADS_DIR = DATA_DIR / "uploads"
USERS_FILE = DATA_DIR / "users.json"
FILES_FILE = DATA_DIR / "files.json"
LOGS_FILE = DATA_DIR / "logs.json"

def init_data():
    """Initialize data directories and files if they don't exist"""
    DATA_DIR.mkdir(exist_ok=True)
    UPLOADS_DIR.mkdir(exist_ok=True)

    if not USERS_FILE.exists():
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f)

    if not FILES_FILE.exists():
        with open(FILES_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f)

    if not LOGS_FILE.exists():
        with open(LOGS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)

# --- USERS ---
def get_users():
    """Get users from JSON"""
    init_data()
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception: # pylint: disable=broad-exception-caught
        return {}

def save_users(users_data):
    """Save users to JSON"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_data, f, indent=2)

# --- FILES METADATA ---
def get_files():
    """Get files metadata from JSON"""
    init_data()
    try:
        with open(FILES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception: # pylint: disable=broad-exception-caught
        return {}

def save_files(files_data):
    """Save files metadata to JSON"""
    with open(FILES_FILE, 'w', encoding='utf-8') as f:
        json.dump(files_data, f, indent=2)

# --- AUDIT LOGS ---
def get_audit_logs():
    """Get audit logs from JSON"""
    init_data()
    try:
        with open(LOGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception: # pylint: disable=broad-exception-caught
        return []

def save_audit_logs(logs_data):
    """Save audit logs to JSON"""
    with open(LOGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs_data, f, indent=2)

# --- FILE CONTENTS (BINARY) ---
def save_file_content(file_id: str, content: bytes):
    """Save binary file content to disk"""
    init_data()
    file_path = UPLOADS_DIR / file_id
    with open(file_path, 'wb') as f:
        f.write(content)

def get_file_content(file_id: str):
    """Get binary file content from disk"""
    init_data()
    file_path = UPLOADS_DIR / file_id
    if file_path.exists():
        with open(file_path, 'rb') as f:
            return f.read()
    return None

def delete_file_content(file_id: str):
    """Delete binary file content from disk"""
    file_path = UPLOADS_DIR / file_id
    if file_path.exists():
        os.remove(file_path)
