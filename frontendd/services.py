"""
Backend service layer - mocked for now, ready to be replaced with real AWS/DB calls
"""
import streamlit as st
from datetime import datetime
import time
import random
from data import (
    get_users, save_users, 
    get_files, save_files, 
    get_audit_logs, save_audit_logs,
    save_file_content, get_file_content, delete_file_content
)

def login_user(email: str, password: str):
    """Authenticate user - mocked"""
    users = get_users()
    user = users.get(email)
    if user and user['password'] == password:
        add_audit_log(email, user['ngo'], "LOGIN", "System", "Success")
        return {
            'email': email,
            'name': user['name'],
            'ngo': user['ngo'],
            'role': user.get('role', 'user')
        }
    add_audit_log(email, "Unknown", "LOGIN_FAILED", "System", "Failed")
    return None

def register_user(ngo_name: str, email: str, password: str):
    """Register new NGO (Admin) - mocked"""
    users = get_users()
    if email in users:
        return None
    
    users[email] = {
        'name': ngo_name + " Admin",
        'ngo': ngo_name,
        'password': password,
        'role': 'admin',
        'created_at': datetime.now().isoformat()
    }
    save_users(users)
    add_audit_log(email, ngo_name, "REGISTER_NGO", "System", "Success")
    return {
        'email': email,
        'name': ngo_name + " Admin",
        'ngo': ngo_name,
        'role': 'admin'
    }

def create_user(admin_user: dict, email: str, password: str, name: str):
    """Create a new staff user for the NGO (Admin only)"""
    if admin_user.get('role') != 'admin':
        return False, "Unauthorized"
        
    users = get_users()
    if email in users:
        return False, "Email already exists"
        
    users[email] = {
        'name': name,
        'ngo': admin_user['ngo'],
        'password': password,
        'role': 'user',
        'created_at': datetime.now().isoformat()
    }
    save_users(users)
    add_audit_log(admin_user['email'], admin_user['ngo'], "CREATE_USER", email, "Success")
    return True, "User created successfully"

def list_org_users(admin_user: dict):
    """List all users for the organization"""
    if admin_user.get('role') != 'admin':
        return []
        
    users = get_users()
    org_users = []
    for email, u in users.items():
        if u['ngo'] == admin_user['ngo']:
            u_copy = u.copy()
            u_copy['email'] = email
            org_users.append(u_copy)
    return org_users

def upload_file(file_name: str, file_size: int, category: str, user: dict, file_bytes: bytes = None):
    """
    Simulate file upload with compression
    Returns: dict with upload details including compression stats
    """
    files = get_files()
    
    # Simulate compression (random 40-70% savings)
    compression_ratio = random.uniform(0.4, 0.7)
    compressed_size = int(file_size * (1 - compression_ratio))
    
    file_id = f"file_{len(files) + 1}_{int(time.time())}"
    
    file_record = {
        'id': file_id,
        'name': file_name,
        'category': category,
        'original_size': file_size,
        'compressed_size': compressed_size,
        'compression_ratio': compression_ratio,
        'uploaded_by': user['email'],
        'ngo': user['ngo'] if isinstance(user, dict) else 'Unknown', # Handle case where user might be just email string in legacy calls, though we updated it
        'uploaded_at': datetime.now().isoformat(),
        's3_path': f"s3://safekeep-vault/{category.lower()}/{file_id}",
        'status': 'active'
    }
    

    files[file_id] = file_record
    save_files(files)

    # Store actual bytes if provided (Mock S3)
    if file_bytes:
        save_file_content(file_id, file_bytes)
        
    add_audit_log(user['email'], user['ngo'], "UPLOAD", file_name, "Success")
    
    return file_record

def list_files(user: dict, search_query: str = "", category_filter: str = "All"):
    """List all files filtered by tenant (NGO)"""
    files = get_files()
    results = []
    
    for file_id, file_data in files.items():
        if file_data['status'] != 'active':
            continue
            
        # Tenant Isolation
        if file_data.get('ngo') != user['ngo']:
            continue
        
        # Apply filters
        if search_query and search_query.lower() not in file_data['name'].lower():
            continue
        
        if category_filter != "All" and file_data['category'] != category_filter:
            continue
        
        results.append(file_data)
    
    # Sort by upload date (newest first)
    results.sort(key=lambda x: x['uploaded_at'], reverse=True)
    return results


def delete_file(file_id: str, user: dict):
    """Soft delete a file"""
    files = get_files()
    if file_id in files:
        # Tenant check
        if files[file_id].get('ngo') != user['ngo']:
            return False
            
        files[file_id]['status'] = 'deleted'
        files[file_id]['deleted_at'] = datetime.now().isoformat()
        files[file_id]['deleted_by'] = user['email']
        save_files(files)
        
        # Clean up content
        delete_file_content(file_id)
            
        add_audit_log(user['email'], user['ngo'], "DELETE", files[file_id]['name'], "Success")
        return True
    return False

def list_audit_logs(user: dict, action_filter: str = "All", limit: int = 100):
    """List audit logs filtered by tenant (NGO)"""
    logs = get_audit_logs()
    
    if action_filter != "All":
        logs = [log for log in logs if log['action'] == action_filter and log.get('ngo') == user['ngo']]
    else:
        logs = [log for log in logs if log.get('ngo') == user['ngo']]
    
    return logs[:limit]

def add_audit_log(user_email: str, ngo: str, action: str, target: str, status: str):
    """Add new audit log entry"""
    logs = get_audit_logs()
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'user': user_email,
        'ngo': ngo,
        'action': action,
        'target': target,
        'status': status,
        'ip': f"192.168.{random.randint(1,255)}.{random.randint(1,255)}"  # Mock IP
    }
    
    logs.insert(0, log_entry)  # Add to beginning
    
    # Keep only last 1000 logs
    if len(logs) > 1000:
        logs.pop()
        
    save_audit_logs(logs)

def get_dashboard_stats(user: dict):
    """Calculate dashboard statistics for specific tenant"""
    files = list_files(user)
    
    if not files:
        return {
            'total_files': 0,
            'total_storage_original': 0,
            'total_storage_compressed': 0,
            'compression_savings_pct': 0,
            'last_upload': None
        }
    
    total_original = sum(f['original_size'] for f in files)
    total_compressed = sum(f['compressed_size'] for f in files)
    savings_pct = ((total_original - total_compressed) / total_original * 100) if total_original > 0 else 0
    
    # Get most recent upload
    files_sorted = sorted(files, key=lambda x: x['uploaded_at'], reverse=True)
    last_upload = files_sorted[0]['uploaded_at'] if files_sorted else None
    
    return {
        'total_files': len(files),
        'total_storage_original': total_original,
        'total_storage_compressed': total_compressed,
        'compression_savings_pct': savings_pct,
        'last_upload': last_upload
    }

def format_bytes(bytes_size):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"