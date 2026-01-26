"""
Reusable UI Components - Glassmorphism Version
"""
import streamlit as st
from datetime import datetime
import base64
from pathlib import Path


# ---------------- GLASS BACKGROUND ----------------
def set_glass_background():
    """
    Set animated gradient background (no image needed)
    """
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #f5576c, #ffd89b) !important;
            background-size: 400% 400% !important;
            animation: gradient 15s ease infinite !important;
        }
        
        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        </style>
        """,
        unsafe_allow_html=True
    )


# ---------------- CSS ----------------
def load_custom_css():
    """Load custom glassmorphism CSS"""
    try:
        with open('styles.css', 'r') as f:
            css_content = f.read()
            st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("CSS file not found. Using fallback styles.")


# ---------------- TRUST BADGES ----------------
def trust_badges():
    """Display glass trust badges"""
    st.markdown("""
        <div class="trust-badges">
            <span class="badge">🔒 End-to-End Encrypted</span>
            <span class="badge">🛡️ Military Grade Security</span>
            <span class="badge">✅ GDPR Compliant</span>
        </div>
    """, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = ""):
    """Standard glass page header"""
    st.markdown(f"""
        <div class="page-header">
            <h1>{title}</h1>
            {f'<p class="page-subtitle">{subtitle}</p>' if subtitle else ''}
        </div>
    """, unsafe_allow_html=True)
    trust_badges()
    st.markdown('<hr style="border-color: rgba(255,255,255,0.2);">', unsafe_allow_html=True)


# ---------------- METRICS ----------------
def metric_card(label: str, value: str, delta: str = None, icon: str = "📊"):
    """Display a glass metric card"""
    delta_html = f'<p class="metric-delta">{delta}</p>' if delta else ''
    
    return f"""
        <div class="metric-card">
            <div class="metric-icon">{icon}</div>
            <div class="metric-content">
                <p class="metric-label">{label}</p>
                <p class="metric-value">{value}</p>
                {delta_html}
            </div>
        </div>
    """


# ---------------- AUTH ----------------
def require_auth():
    """Redirect to login if not authenticated"""
    if not st.session_state.get('authenticated', False):
        st.warning("🔐 Please login to access this page")
        st.stop()


# ---------------- GLASS SIDEBAR ----------------
def sidebar_navigation():
    """Display glass sidebar navigation"""
    with st.sidebar:
        st.markdown("""
            <div style="text-align: center; margin-bottom: 2rem;">
                <h2 style="font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem;">🔒 Safekeep</h2>
                <p style="font-size: 0.875rem; opacity: 0.8;">NGO Secure Vault</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.get('authenticated', False):
            user = st.session_state.get("user", {})

            name = user.get("name", "User")
            email = user.get("email", "")

            st.markdown(f"""
                <div class="user-info">
                    <p><strong>{name}</strong></p>
                    <p class="user-email">{email}</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<hr style="border-color: rgba(255,255,255,0.2); margin: 1.5rem 0;">', unsafe_allow_html=True)
            
            # Navigation with icons
            nav_cols = st.columns(2)
            with nav_cols[0]:
                if st.button("📊 Dashboard", use_container_width=True):
                    st.switch_page("pages/1_Dashboard.py")
                if st.button("📁 Vault", use_container_width=True):
                    st.switch_page("pages/3_Vault_Explorer.py")
            with nav_cols[1]:
                if st.button("⬆️ Upload", use_container_width=True):
                    st.switch_page("pages/2_Upload_Center.py")
                if st.button("📜 Logs", use_container_width=True):
                    st.switch_page("pages/4_Audit_Logs.py")
            
            st.markdown('<hr style="border-color: rgba(255,255,255,0.2); margin: 1.5rem 0;">', unsafe_allow_html=True)
            
            if st.button("🚪 Logout", use_container_width=True, type="primary"):
                st.session_state.authenticated = False
                st.session_state.user = None
                st.switch_page("app.py")


# ---------------- FORMATTERS ----------------
def format_datetime(iso_string: str):
    """Format ISO datetime string to readable format"""
    try:
        dt = datetime.fromisoformat(iso_string)
        return dt.strftime("%b %d, %Y %I:%M %p")
    except:
        return iso_string


def format_date(iso_string: str):
    """Format ISO datetime string to date only"""
    try:
        dt = datetime.fromisoformat(iso_string)
        return dt.strftime("%b %d, %Y")
    except:
        return iso_string


def empty_state(message: str, icon: str = "💎"):
    """Display glass empty state"""
    st.markdown(f"""
        <div class="empty-state">
            <div class="empty-icon">{icon}</div>
            <p class="empty-message">{message}</p>
        </div>
    """, unsafe_allow_html=True)