"""
UI Components for the Admin Dashboard

This module contains reusable UI components and helper functions
for the Streamlit admin dashboard interface.
"""

from typing import Dict, List, Optional

import pandas as pd
import streamlit as st


def display_user_profile(user: Dict) -> None:
    """Display user profile information in a structured layout"""
    st.subheader(f"Profile: {user['username']}")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("User ID", user["id"])
        st.metric("Account Status", user["status"])
        st.metric("Join Date", user["created_at"])

    with col2:
        st.metric("Total Messages", user["message_count"])
        st.metric("Reports Against", user["report_count"])
        st.write("**Email:**")
        st.caption(user["email"])

    with col3:
        st.metric("Last Active", user["last_active"])


def display_user_activities(activities: List[Dict]) -> None:
    """Display user activities in a table format"""
    if activities:
        df = pd.DataFrame(activities)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No activities found.")


def display_user_messages(messages: List[Dict]) -> None:
    """Display user messages in expandable sections"""
    if messages:
        for msg in messages:
            preview = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            with st.expander(f"Message from {msg['timestamp']} - {msg['activity']}: {preview}", expanded=False):
                st.write(msg["content"])
                if msg.get("flagged"):
                    st.warning("⚠️ This message has been flagged")
    else:
        st.info("No recent messages found.")


def display_search_form() -> tuple:
    """Display user search form and return search parameters"""
    st.subheader("Search User")
    search_type = st.selectbox("Search by:", ["User ID", "Username"])
    search_value = st.text_input(
        f"Enter {search_type}:", placeholder=f"Type {search_type.lower()} here..."
    )
    search_button = st.button("Search", type="primary")
    st.caption("💡 If no results appear, try clicking Search again")

    return search_type, search_value, search_button


def display_moderation_actions(user_id: str) -> None:
    """Display moderation action buttons"""
    st.subheader("Moderation Actions")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Send Message", type="secondary"):
            st.session_state.show_message_form = True
            st.session_state.message_user_id = user_id

    with col2:
        if st.button("🚫 Permanent Ban", type="secondary"):
            st.session_state.show_ban_form = True
            st.session_state.ban_user_id = user_id


def display_message_form(user_id: str, moderation_service) -> None:
    """Display direct message form with action button support"""
    st.subheader("Send Direct Message")
    with st.form("direct_message_form"):
        message = st.text_area("Message:", max_chars=1000)

        st.subheader("Action Button (Optional)")
        add_action = st.checkbox("Add action button to message")

        action_type = None
        action_text = None
        action_data = None

        if add_action:
            action_type = st.selectbox("Action Type", ["navigation", "url", "none"])

            if action_type != "none":
                action_text = st.text_input("Button Text", max_chars=70, placeholder="View Details")

                if action_type == "navigation":
                    screen = st.selectbox("Target Screen", ["Browse", "Profile", "Activities", "Communities", "Thread"])
                    thread_id = st.number_input("Thread ID (if applicable)", min_value=0, value=0)

                    if thread_id > 0:
                        action_data = {"screen": screen, "params": {"threadId": thread_id}}
                    else:
                        action_data = {"screen": screen}

                elif action_type == "url":
                    url = st.text_input("URL", placeholder="https://...")
                    if url:
                        action_data = {"url": url}

        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Send Message", type="primary"):
                if not message:
                    st.error("Please enter a message")
                else:
                    success = moderation_service.send_message(
                        user_id, "", message, action_type, action_text, action_data
                    )
                    if success:
                        st.success("Message sent successfully!")
                        st.session_state.show_message_form = False
                        st.rerun()
                    else:
                        st.error("Failed to send message")

        with col2:
            if st.form_submit_button("Cancel"):
                st.session_state.show_message_form = False
                st.rerun()


def display_ban_form(user_id: str, moderation_service) -> None:
    """Display permanent ban form"""
    with st.form("perm_ban_form"):
        st.subheader("⚠️ PERMANENT BAN")
        st.warning("This action cannot be undone!")
        reason = st.text_area("Reason for permanent ban:", max_chars=500)
        confirm = st.checkbox("I confirm this permanent ban")

        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Apply Permanent Ban", type="primary"):
                if confirm and reason:
                    success = moderation_service.permanent_ban(user_id, reason)
                    if success:
                        st.success("User permanently banned")
                        st.session_state.show_ban_form = False
                        st.rerun()
                    else:
                        st.error("Failed to apply ban")
                else:
                    st.error("Please confirm the action and provide a reason")

        with col2:
            if st.form_submit_button("Cancel"):
                st.session_state.show_ban_form = False
                st.rerun()


def display_stats_metrics(stats: Dict) -> None:
    """Display platform statistics as metrics"""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Active Users (30d)", f"{stats.get('active_users', 0):,}")
    with col2:
        st.metric("Total Users", f"{stats.get('total_users', 0):,}")
    with col3:
        st.metric("Messages Today", f"{stats.get('messages_today', 0):,}")
    with col4:
        st.metric("Reports", f"{stats.get('new_reports', 0):,}")


def display_error_message(message: str, error_type: str = "error") -> None:
    """Display formatted error message"""
    if error_type == "warning":
        st.warning(f"{message}")
    elif error_type == "info":
        st.info(f"ℹ{message}")
    else:
        st.error(f"{message}")


def display_success_message(message: str) -> None:
    """Display formatted success message"""
    st.success(f"{message}")
