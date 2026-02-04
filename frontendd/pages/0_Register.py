import streamlit as st
from services import register_user
from components import setup_page_styling

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Register - Safekeep Vault",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

setup_page_styling()

# Check if already authenticated
if st.session_state.get('authenticated'):
    st.switch_page("pages/1_Dashboard.py")

# -----------------------------------------------------------------------------
# REGISTRATION PAGE
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
            Create your organization's secure vault
        </h3>
        <p style="opacity: 0.7; line-height: 1.6;">
            Set up your organization in minutes and start protecting your sensitive files with military-grade encryption.
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

# --- RIGHT COLUMN: REGISTRATION FORM ---
with col_right:
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    
    st.markdown("""
        <h2 style="text-align: center; margin-bottom: 1.5rem; font-size: 1.8rem;">
            📝 Create New Organization
        </h2>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.form("register_form"):
        ngo_name = st.text_input("Organization Name", placeholder="Your NGO Name")
        email = st.text_input("Admin Email Address", placeholder="admin@organization.org")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        
        st.markdown("""
            <p style="font-size: 0.85rem; opacity: 0.6; margin-top: 0.5rem;">
                This will be the administrator account for your organization
            </p>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        submit = st.form_submit_button("Create Account", use_container_width=True, type="primary")
        
        if submit:
            if not ngo_name or not email or not password:
                st.error("All fields are required")
            else:
                user, error = register_user(ngo_name, email, password)
                if user:
                    st.success("✅ Account created successfully! Use the 'Login to Your Account' button below to sign in.")
                else:
                    st.error(error or "Registration failed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Link to Login
    st.markdown("""
        <div style="text-align: center; margin-top: 2rem;">
            <p style="opacity: 0.7;">Already have an account?</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("Login to Your Account", use_container_width=True):
        st.switch_page("pages/0_Login.py")
    
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
