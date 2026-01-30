import streamlit as st
from components import (
    load_custom_css, page_header, require_auth,
    sidebar_navigation, format_datetime, set_glass_background
)
from services import create_user, list_org_users
import pandas as pd

st.set_page_config(
    page_title="User Management - Safekeep NGO Vault",
    page_icon="👥",
    layout="wide"
)

set_glass_background()
load_custom_css()

require_auth()
sidebar_navigation()

# Page header
page_header("👥 User Management", "Manage your organization's staff and access")

# Check Access
if st.session_state.user.get('role') != 'admin':
    st.error("⛔ Access Denied: This area is restricted to Organization Administrators.")
    st.stop()

# Two column layout
left, right = st.columns([1, 2])

with left:
    st.markdown("### ➕ Add New Staff")
    st.caption("Create an account for a team member. They will benefit from your organization's storage.")

    with st.form("create_user_form"):
        name = st.text_input("Full Name", placeholder="John Doe")
        email = st.text_input("Email Address", placeholder="john@ngo.org")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        confirm_pass = st.text_input("Confirm Password", type="password", placeholder="••••••••")

        submit = st.form_submit_button("Create User", width="stretch", type="primary")

        if submit:
            if not name or not email or not password:
                st.error("⚠️ Please fill in all fields")
            elif password != confirm_pass:
                st.error("🔒 Passwords do not match")
            else:
                success, msg = create_user(st.session_state.user, email, password, name)
                if success:
                    st.success(f"✅ {msg}")
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")

with right:
    st.markdown("### 📋 Organization Members")

    users = list_org_users(st.session_state.user)

    if users:
        for u in users:
            with st.container():
                c1, c2, c3 = st.columns([2, 2, 1])
                with c1:
                    role_badge = "👑 Admin" if u.get('role') == 'admin' else "👤 Staff"
                    st.markdown(f"**{u['name']}**")
                    st.caption(f"{role_badge} • Joined {format_datetime(u['created_at'])}")
                with c2:
                    st.markdown(f"`{u['email']}`")
                with c3:
                    if u['email'] == st.session_state.user['email']:
                        st.caption("You")
                    else:
                        st.caption("Active")
                st.markdown("---")
    else:
        st.info("No users found")

    st.info("💡 Note: Standard staff users can upload and view files but cannot access audit logs or manage other users.")
