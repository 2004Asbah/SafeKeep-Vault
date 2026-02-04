import streamlit as st
from services import login_user
from components import setup_page_styling

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Login - Safekeep Vault",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

setup_page_styling()

# Check if already authenticated
if st.session_state.get('authenticated'):
    st.switch_page("pages/1_Dashboard.py")

# -----------------------------------------------------------------------------
# LOGIN PAGE
# -----------------------------------------------------------------------------

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
            Access your secure vault
        </h3>
        <p style="opacity: 0.7; line-height: 1.6;">
            Login to manage your organization's files with enterprise-grade security and encryption.
        </p>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Feature List
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

# --- RIGHT COLUMN: LOGIN FORM ---
with col_right:
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    
    st.markdown("""
        <h2 style="text-align: center; margin-bottom: 1.5rem; font-size: 1.8rem;">
            🔒 Login to Your Account
        </h2>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        email = st.text_input("Email Address", placeholder="your.email@organization.org")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        submit = st.form_submit_button("Login", use_container_width=True, type="primary")
        
        if submit:
            if not email or not password:
                st.error("Please enter both email and password")
            else:
                user = login_user(email, password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.success("Login successful! Redirecting...")
                    st.rerun()
                else:
                    st.error("Invalid email or password")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Link to Register
    st.markdown("""
        <div style="text-align: center; margin-top: 2rem;">
            <p style="opacity: 0.7;">Don't have an account?</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("Create New Organization", use_container_width=True):
        st.switch_page("pages/0_Register.py")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Back to home
st.markdown("<br>", unsafe_allow_html=True)
if st.button("← Back to Home"):
    st.switch_page("app.py")

# Footer
st.markdown("""
    <div class="footer-text">
        © 2024 Safekeep Vault • Powered by AWS • Secured with AES-256
    </div>
""", unsafe_allow_html=True)
