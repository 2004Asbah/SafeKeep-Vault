import streamlit as st
from components import (
    load_custom_css, page_header, require_auth, 
    sidebar_navigation, format_datetime, set_glass_background
)
from services import list_audit_logs
import pandas as pd

st.set_page_config(
    page_title="Audit Logs - Safekeep NGO Vault",
    page_icon="📜",
    layout="wide"
)

set_glass_background()  # Add this line
load_custom_css()

require_auth()
sidebar_navigation()

# Page header
page_header("📜 Audit Logs", "Complete activity trail for compliance and security")

# Check Access
if st.session_state.user.get('role') != 'admin':
    st.error("⛔ Access Denied: This area is restricted to Organization Administrators.")
    st.stop()

# Filter bar
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.markdown("**Filter & Export**")

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
col_info1, col_info2, col_info3 = st.columns(3)

with col_info1:
    st.info("🔒 **All actions are logged** for security and compliance")

with col_info2:
    st.info("⏱️ **Real-time tracking** of all file operations")

with col_info3:
    st.info("📊 **Exportable** for external audit reviews")

st.markdown("<br>", unsafe_allow_html=True)

# Display logs
if logs:
    # Create DataFrame for better display
    log_data = []
    
    for log in logs:
        # Determine status badge
        if log['status'] == 'Success':
            status_badge = '<span class="status-success">✅ Success</span>'
        elif log['status'] == 'Failed':
            status_badge = '<span class="status-failed">❌ Failed</span>'
        else:
            status_badge = '<span class="status-pending">⏳ Pending</span>'
        
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
            'IP Address': log.get('ip', 'N/A')
        })
    
    df = pd.DataFrame(log_data)
    
    # Display as HTML table for better formatting
    st.markdown("### 📋 Activity Log")
    
    for idx, log in enumerate(logs):
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])
            
            # Determine status and icon
            if log['status'] == 'Success':
                status_icon = "✅"
                status_color = "#10b981"
            elif log['status'] == 'Failed':
                status_icon = "❌"
                status_color = "#ef4444"
            else:
                status_icon = "⏳"
                status_color = "#f59e0b"
            
            action_icons = {
                'LOGIN': '🔓',
                'LOGIN_FAILED': '🔒',
                'UPLOAD': '⬆️',
                'DELETE': '🗑️',
                'DOWNLOAD': '⬇️',
                'REGISTER': '📝'
            }
            action_icon = action_icons.get(log['action'], 'ℹ️')
            
            with col1:
                st.caption("Timestamp")
                st.markdown(f"**{format_datetime(log['timestamp'])}**")
            
            with col2:
                st.caption("User")
                st.markdown(f"👤 **{log['user']}**")
            
            with col3:
                st.caption("Action")
                st.markdown(f"{action_icon} **{log['action']}**")
            
            with col4:
                st.caption("Target")
                st.markdown(f"**{log['target']}**")
            
            with col5:
                st.caption("Status")
                st.markdown(f"""
                    <span style="color: {status_color}; font-weight: bold;">
                        {status_icon} {log['status']}
                    </span>
                """, unsafe_allow_html=True)
            
            # Show IP in a subtle way
            st.caption(f"🌐 IP: {log.get('ip', 'N/A')}")
            
            st.markdown("---")
    
    # Export functionality
    st.markdown("### 📤 Export Logs")
    
    col_exp1, col_exp2 = st.columns([1, 3])
    
    with col_exp1:
        export_format = st.radio(
            "Export Format",
            options=["CSV", "JSON"],
            horizontal=True
        )
    
    with col_exp2:
        if export_format == "CSV":
            # Create clean CSV data
            csv_data = []
            for log in logs:
                csv_data.append({
                    'Timestamp': log['timestamp'],
                    'User': log['user'],
                    'Action': log['action'],
                    'Target': log['target'],
                    'Status': log['status'],
                    'IP Address': log.get('ip', 'N/A')
                })
            
            csv_df = pd.DataFrame(csv_data)
            csv_string = csv_df.to_csv(index=False)
            
            st.download_button(
                label="⬇️ Download CSV",
                data=csv_string,
                file_name=f"audit_logs_{action_filter.lower()}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            import json
            json_string = json.dumps(logs, indent=2)
            
            st.download_button(
                label="⬇️ Download JSON",
                data=json_string,
                file_name=f"audit_logs_{action_filter.lower()}.json",
                mime="application/json",
                use_container_width=True
            )

else:
    empty_state("No audit logs found", "📭")

# Statistics
st.markdown("---")
st.markdown("### 📊 Log Statistics")

if logs:
    col1, col2, col3, col4 = st.columns(4)
    
    # Count by action
    action_counts = {}
    status_counts = {}
    
    for log in logs:
        action = log['action']
        status = log['status']
        
        action_counts[action] = action_counts.get(action, 0) + 1
        status_counts[status] = status_counts.get(status, 0) + 1
    
    with col1:
        st.metric("Total Entries", len(logs))
    
    with col2:
        st.metric("Successful", status_counts.get('Success', 0))
    
    with col3:
        st.metric("Failed", status_counts.get('Failed', 0))
    
    with col4:
        most_common_action = max(action_counts.items(), key=lambda x: x[1])
        st.metric("Most Common", f"{most_common_action[0]}")
    
    # Action breakdown
    st.markdown("#### Action Breakdown")
    
    action_cols = st.columns(len(action_counts))
    
    for idx, (action, count) in enumerate(action_counts.items()):
        with action_cols[idx]:
            action_icons = {
                'LOGIN': '🔓',
                'LOGIN_FAILED': '🔒',
                'UPLOAD': '⬆️',
                'DELETE': '🗑️',
                'DOWNLOAD': '⬇️',
                'REGISTER': '📝'
            }
            icon = action_icons.get(action, 'ℹ️')
            st.metric(f"{icon} {action}", count)

# Compliance note
st.markdown("---")
st.info("""
    **🔐 Compliance Note:** All audit logs are retained for 90 days minimum and stored securely. 
    Logs are immutable and tamper-proof. For extended retention requirements, please export logs regularly.
""")

# Security best practices
with st.expander("🛡️ Security & Compliance Best Practices"):
    st.markdown("""
        **Audit Log Best Practices:**
        
        1. **Regular Reviews:** Review audit logs weekly for unusual activity
        2. **Export for Records:** Download and archive logs monthly
        3. **Anomaly Detection:** Watch for failed login attempts or unauthorized access
        4. **Compliance:** Maintain logs for regulatory requirements (90 days minimum)
        5. **Incident Response:** Use logs to investigate security incidents
        
        **What's Logged:**
        - All user authentication attempts (success and failures)
        - File uploads, downloads, and deletions
        - Administrative actions
        - System events
        
        **Security Features:**
        - Immutable log entries (cannot be modified or deleted)
        - Timestamp verification
        - IP address tracking
        - User attribution for all actions
    """)