"""
Reusable UI Components - Premium Dark Theme
"""
from datetime import datetime
import streamlit as st

# ---------------- THEME SETUP ----------------
def setup_page_styling():
    """Import Custom CSS"""
    try:
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        css_path = os.path.join(current_dir, 'styles.css')
        
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
            st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"CSS file not found at {css_path}")

def load_custom_css():
    """Alias for setup_page_styling"""
    setup_page_styling()

# ---------------- HEADER ELEMENTS ----------------
def trust_badges():
    """Display security badges (used in Login & Header)"""
    st.markdown("""
        <div class="badge-container">
            <span class="badge"><i class="fas fa-lock"></i> End-to-End Encrypted</span>
            <span class="badge"><i class="fas fa-shield-alt"></i> Military Grade Security</span>
            <span class="badge"><i class="fas fa-check-circle"></i> GDPR Compliant</span>
        </div>
    """, unsafe_allow_html=True)

def page_header(title: str, subtitle: str = "", show_logout: bool = False):
    """Standard Page Header with optional logout button"""
    if show_logout:
        col_title, col_logout = st.columns([4, 1])
        
        with col_title:
            st.markdown(f"""
                <div style="margin-bottom: 2rem;">
                    <h1>{title}</h1>
                    <p>{subtitle}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col_logout:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚪 Logout", type="secondary", key="header_logout"):
                st.session_state.authenticated = False
                st.session_state.user = None
                st.switch_page("app.py")
    else:
        st.markdown(f"""
            <div style="margin-bottom: 2rem;">
                <h1>{title}</h1>
                <p>{subtitle}</p>
            </div>
        """, unsafe_allow_html=True)
    
    trust_badges()
    st.markdown("---")

# ---------------- CARDS ----------------
def metric_card(label: str, value: str, sub: str = None):
    """Minimal Dark Metric Card"""
    sub_html = f'<div class="metric-sub">{sub}</div>' if sub else ''
    return f"""
        <div class="metric-container">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {sub_html}
        </div>
    """

def quick_action_card(icon: str, title: str, desc: str):
    """Action Card for Dashboard"""
    return f"""
        <div class="action-card">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem; color: #3b82f6;">{icon}</div>
            <h4>{title}</h4>
            <p class="text-muted" style="font-size: 0.9rem;">{desc}</p>
        </div>
    """

# ---------------- NAVIGATION ----------------
def sidebar_navigation():
    """Dark Sidebar Navigation"""
    with st.sidebar:
        # Prominent header to make sidebar visible
        st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 1rem; 
                        border-radius: 8px; 
                        margin-bottom: 1rem;
                        text-align: center;">
                <h3 style="margin: 0; color: white;">💎 Safekeep</h3>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.8rem; color: rgba(255,255,255,0.9);">
                    Navigation Menu
                </p>
            </div>
        """, unsafe_allow_html=True)

        if st.session_state.get('authenticated', False):
            user = st.session_state.get("user", {})
            st.markdown(f"""
                <div class="sidebar-user">
                    <div style="font-weight: 600;">{user.get('name', 'User')}</div>
                    <div style="font-size: 0.8rem; color: #8b949e;">{user.get('email', '')}</div>
                </div>
            """, unsafe_allow_html=True)

            st.divider()

            if st.button("📊 Dashboard", width="stretch"):
                st.switch_page("pages/1_Dashboard.py")
            if st.button("⬆️ Upload Center", width="stretch"):
                st.switch_page("pages/2_Upload_Center.py")
            if st.button("📁 Vault Explorer", width="stretch"):
                st.switch_page("pages/3_Vault_Explorer.py")
            if st.button("📜 Audit Logs", width="stretch"):
                st.switch_page("pages/4_Audit_Logs.py")
            
            # User Management - Admin only
            if user.get('role') == 'admin':
                if st.button("👥 User Management", width="stretch"):
                    st.switch_page("pages/5_User_Management.py")

            st.divider()

            if st.button("🚪 Logout", width="stretch", key="sidebar_logout"):
                st.session_state.authenticated = False
                st.session_state.user = None
                st.switch_page("app.py")

# ---------------- AUTH CHECK ----------------
def require_auth():
    """Redirect to login if not authenticated"""
    if not st.session_state.get('authenticated', False):
        st.switch_page("app.py")

# ---------------- HELPERS ----------------
def format_datetime(iso_string: str):
    """Format ISO datetime string"""
    try:
        dt = datetime.fromisoformat(iso_string)
        return dt.strftime("%b %d, %Y %I:%M %p")
    except ValueError:
        return iso_string

def empty_state(message: str):
    st.info(message)

# Remove set_glass_background and other glass specific functions
def set_glass_background():
    pass
