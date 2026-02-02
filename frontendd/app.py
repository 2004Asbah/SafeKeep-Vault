import time
import streamlit as st
from services import login_user, register_user
from components import setup_page_styling

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Safekeep NGO Vault",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize Styling (matches the updated minimal dark theme)
setup_page_styling()

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None

if st.session_state.authenticated:
    st.switch_page("pages/1_Dashboard.py")

# -----------------------------------------------------------------------------
# MAIN LAYOUT
# -----------------------------------------------------------------------------
# Using columns to create the balanced 2-column layout
# Left: Brand & Value | Right: Auth Card

# Spacer at top to center vertically (approx)
st.markdown("<br><br>", unsafe_allow_html=True)

col_left, col_mid, col_right = st.columns([10, 1, 8])

# --- LEFT COLUMN: BRANDING ---
with col_left:
    st.markdown("<br>", unsafe_allow_html=True)

    # Logo Area
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 1.5rem; margin-bottom: 1rem;">
            <span style="font-size: 3.5rem;">💎</span>
            <h1 class="hero-title">Safekeep NGO Vault</h1>
        </div>
        <p style="font-size: 1.1rem; opacity: 0.8; margin-bottom: 2.5rem;">Secure • Encrypted • Compliant</p>

        <h3 style="font-weight: 500; font-size: 1.25rem; margin-bottom: 1rem; opacity: 0.9;">
            The most secure enterprise-grade file storage solution designed specifically for NGOs.
        </h3>
    """, unsafe_allow_html=True)

    # Feature List (Minimal icons)
    features = [
        ("✨", "Zero-Knowledge Encryption"),
        ("⚡", "Smart Compression"),
        ("🛡️", "GDPR & HIPAA Compliant")
    ]

    for icon, text in features:
        st.markdown(f"""
            <div class="feature-item">
                <span class="feature-icon">{icon}</span>
                <span>{text}</span>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Pill Badges
    st.markdown("""
        <div style="display: flex; align-items: center; padding-top: 1rem;">
            <div class="badge-pill">
                🔒 End-to-End Encrypted
            </div>
            <div class="badge-pill">
                🛡️ Military Grade
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- RIGHT COLUMN: AUTH CARD ---
with col_right:
    st.markdown('<div class="login-card">', unsafe_allow_html=True)

    # Context Tabs
    tab1, tab2, tab3 = st.tabs(["🔒 Admin", "👤 Staff", "📝 Register"])

    # --- ADMIN ---
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.form("admin_login"):
            email = st.text_input("Admin Email", placeholder="admin@ngo.org")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("Login")

            if submit:
                user = login_user(email, password)
                if user and user.get('role') == 'admin':
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.rerun()
                elif user:
                    st.error("Please utilize the Staff Portal.")
                else:
                    st.error("Invalid credentials")

    # --- STAFF ---
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.form("staff_login"):
            email = st.text_input("Staff Email", placeholder="staff@ngo.org")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("Login")

            if submit:
                user = login_user(email, password)
                if user and user.get('role') == 'user':
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.rerun()
                elif user:
                    st.warning("Admin account detected. Redirecting...")
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid credentials")

    # --- REGISTER ---
    with tab3:
        st.markdown(
            "<p style='margin-bottom: 1rem;'>Create Organization</p>",
            unsafe_allow_html=True
        )
        with st.form("register"):
            name = st.text_input("NGO Name", placeholder="Organization Name")
            email = st.text_input("Admin Email", placeholder="admin@org.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")

            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("Create Account")

            if submit:
                if not name or not email or not password:
                    st.error("All fields are required")
                else:
                    user = register_user(name, email, password)
                    if user:
                        st.success("Account created! Please login.")
                    else:
                        st.error("Email already exists")

    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
    <div class="footer-text">
        © 2024 Safekeep Vault • Powered by AWS • Secured with AES-256
    </div>
""", unsafe_allow_html=True)
