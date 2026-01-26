import streamlit as st
from services import login_user, register_user
from components import load_custom_css, trust_badges, set_glass_background

import time

st.set_page_config(
    page_title="Safekeep NGO Vault",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Set animated gradient background
set_glass_background()

# Load custom CSS
load_custom_css()

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None

# Redirect to dashboard if already authenticated
if st.session_state.authenticated:
    st.switch_page("pages/1_Dashboard.py")

# Hero Section with Glass Effect
st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">💎 Safekeep NGO Vault</h1>
        <p class="hero-subtitle">Secure • Encrypted • Compliant</p>
        <p class="hero-description">Enterprise-grade file storage with auto-compression for NGOs</p>
    </div>
""", unsafe_allow_html=True)

trust_badges()

# Center the login form
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Glass login container
    st.markdown("""
        <div style="
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(20px);
            border-radius: 24px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            padding: 2rem;
            margin: 1rem 0;
        ">
    """, unsafe_allow_html=True)
    
    # Toggle between login modes
    tab1, tab2, tab3 = st.tabs(["🔒 Admin Portal", "👤 Staff Portal", "🏢 Register NGO"])
    
    # --- ADMIN LOGIN ---
    with tab1:
        st.markdown("### Admin Access")
        st.caption("Manage NGO settings, users, and audit logs")
        with st.form("admin_login_form"):
            email = st.text_input("Admin Email", placeholder="admin@ngo.org")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            
            submit = st.form_submit_button("Login as Admin", use_container_width=True, type="primary")
            
            if submit:
                user = login_user(email, password)
                if user:
                    if user.get('role') == 'admin':
                        st.session_state.authenticated = True
                        st.session_state.user = user
                        st.success(f"✨ Welcome back, {user['name']}!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("⛔ This portal is for Admins only. Please use Staff Portal.")
                else:
                    st.error("❌ Invalid credentials")

    # --- STAFF LOGIN ---
    with tab2:
        st.markdown("### Staff Access")
        st.caption("Upload files and view vault")
        with st.form("staff_login_form"):
            email = st.text_input("Staff Email", placeholder="staff@ngo.org")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            
            submit = st.form_submit_button("Login as Staff", use_container_width=True, type="primary")
            
            if submit:
                user = login_user(email, password)
                if user:
                    if user.get('role') == 'user':
                        st.session_state.authenticated = True
                        st.session_state.user = user
                        st.success(f"👋 Welcome back, {user['name']}!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.warning("⚠️ You are an Admin. Redirecting...")
                        st.session_state.authenticated = True
                        st.session_state.user = user
                        time.sleep(1)
                        st.rerun()
                else:
                    st.error("❌ Invalid credentials")

    # --- REGISTER NGO ---
    with tab3:
        st.markdown("### Register Organization")
        st.caption("Create a new secure vault for your NGO")
        with st.form("register_form"):
            ngo_name = st.text_input("NGO Name", placeholder="Global Relief Foundation")
            reg_email = st.text_input("Admin Email", placeholder="contact@ngo.org")
            reg_password = st.text_input("Password", type="password", placeholder="••••••••")
            reg_confirm = st.text_input("Confirm Password", type="password", placeholder="••••••••")
            
            register_btn = st.form_submit_button("Create NGO Account", use_container_width=True, type="primary")
            
            if register_btn:
                if not ngo_name or not reg_email or not reg_password:
                    st.error("⚠️ Please fill in all fields")
                elif reg_password != reg_confirm:
                    st.error("🔒 Passwords do not match")
                else:
                    user = register_user(ngo_name, reg_email, reg_password)
                    if user:
                        st.success(f"✅ Organization '{ngo_name}' created!")
                        st.info("📧 Please login via Admin Portal")
                    else:
                        st.error("📧 Email already exists")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Features section with glass cards
st.markdown("---")
st.markdown("### 💡 Why Choose Safekeep?")

feat1, feat2, feat3 = st.columns(3)

with feat1:
    st.markdown("""
        <div class="feature-card">
            <h3>🗜️ Smart Compression</h3>
            <p>Reduce file sizes by 40-70% without quality loss</p>
        </div>
    """, unsafe_allow_html=True)

with feat2:
    st.markdown("""
        <div class="feature-card">
            <h3>🔐 Zero-Knowledge</h3>
            <p>Your data is encrypted before it leaves your device</p>
        </div>
    """, unsafe_allow_html=True)

with feat3:
    st.markdown("""
        <div class="feature-card">
            <h3>📊 Full Compliance</h3>
            <p>GDPR, HIPAA, and NGO compliance built-in</p>
        </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; padding: 2em 0; color: rgba(255,255,255,0.7);">
        <p>Built for NGOs • Powered by AWS • Secured with AES-256</p>
        <p style="font-size: 0.8em; margin-top: 1em;">© 2024 Safekeep Vault. All rights reserved.</p>
    </div>
""", unsafe_allow_html=True)