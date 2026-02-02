# pylint: disable=invalid-name
import streamlit as st
from components import (
    load_custom_css, page_header, require_auth,
    sidebar_navigation, format_datetime, metric_card
)
from services import list_audit_logs
import pandas as pd

st.set_page_config(
    page_title="Audit Logs - Safekeep NGO Vault",
    page_icon="📜",
    layout="wide"
)

load_custom_css()
require_auth()
sidebar_navigation()

# Page header
page_header("Audit Logs", "Complete activity trail for compliance and security")

# Check Access
if st.session_state.user.get('role') != 'admin':
    st.error("⛔ Access Denied: This area is restricted to Organization Administrators.")
    st.stop()

# Filter bar
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.markdown("### Filter & Search")

with col2:
    action_filter = st.selectbox(
        "Action Type",
        options=["All", "LOGIN", "UPLOAD", "DELETE", "DOWNLOAD", "LOGIN_FAILED"]
    )

with col3:
    limit = st.selectbox(
        "Show entries",
        options=[25, 50, 100, 500],
        index=1
    )

# Get filtered logs
logs = list_audit_logs(st.session_state.user, action_filter, limit)

st.markdown("---")

# Display log count
st.markdown(f"**{len(logs)}** log entries found")

# Info box
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(metric_card("Total Logs", str(len(logs))), unsafe_allow_html=True)
with c2:
    failed = len([l for l in logs if l['status'] == 'Failed'])
    color = "text-red-500" if failed > 0 else "text-green-500"
    st.markdown(metric_card("Failed Actions", str(failed)), unsafe_allow_html=True)
with c3:
    unique_users = len(set(l['user'] for l in logs))
    st.markdown(metric_card("Active Users", str(unique_users)), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Display logs
if logs:
    # Create DataFrame for better display
    log_data = []

    for log in logs:
        # Determine status badge
        if log['status'] == 'Success':
            status_badge = '✅ Success'
        elif log['status'] == 'Failed':
            status_badge = '❌ Failed'
        else:
            status_badge = '⏳ Pending'

        # Determine action icon
        action_icons = {
            'LOGIN': '🔓',
            'LOGIN_FAILED': '🔒',
            'UPLOAD': '⬆️',
            'DELETE': '🗑️',
            'DOWNLOAD': '⬇️',
            'REGISTER': '📝'
        }
        action_icon = action_icons.get(log['action'], 'ℹ️')

        log_data.append({
            'Timestamp': format_datetime(log['timestamp']),
            'User': log['user'],
            'Action': f"{action_icon} {log['action']}",
            'Target': log['target'],
            'Status': status_badge,
            'IP Address': log.get('ip_address', '127.0.0.1')
        })

    df = pd.DataFrame(log_data)

    # Styled Table
    st.dataframe(
        df,
        column_config={
            "Timestamp": st.column_config.DatetimeColumn("Time", format="D MMM, HH:mm"),
            "User": st.column_config.TextColumn("User"),
            "Action": st.column_config.TextColumn("Action"),
            "Target": st.column_config.TextColumn("Details"),
            "Status": st.column_config.TextColumn("Status"),
            "IP Address": st.column_config.TextColumn("IP Source"),
        },
        width="stretch",
        hide_index=True
    )

    # Export
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📥 Export Audit Log (CSV)", width="content"):
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="audit_logs.csv",
            mime="text/csv"
        )

else:
    st.info("No audit logs found matching criteria.")
