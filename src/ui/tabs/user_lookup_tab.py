"""User lookup tab functionality"""

import streamlit as st

from core.security import security_validator
from ui.components import display_search_form
from ui.error_handler import UIErrorHandler


def user_lookup_tab():
    """Handle user lookup tab"""
    st.header("User Profile Lookup")

    col1, col2 = st.columns([1, 3])

    with col1:
        _render_search_section()

    with col2:
        _render_user_details_section()


def _render_search_section():
    """Render the search form and handle search logic"""
    search_type, search_value, search_button = display_search_form()

    if search_button and search_value:
        if not security_validator.validate_search_query(search_value):
            st.error("Invalid search query. Please check your input.")
            return

        _perform_user_search(search_type, search_value)


def _perform_user_search(search_type: str, search_value: str):
    """Perform user search and update session state"""
    try:
        user = st.session_state.user_service.get_user(
            search_type.lower().replace(" ", "_"), search_value
        )
        if user:
            st.session_state.selected_user = user
            _clear_previous_report_details()
            st.success(f"User found: {user['username']}")
        else:
            st.info("User not found")
    except Exception as e:
        st.info("User not found")


def _clear_previous_report_details():
    """Clear previous report details from session state"""
    if "selected_report_details" in st.session_state:
        del st.session_state.selected_report_details


def _render_user_details_section():
    """Render user details if a user is selected"""
    if "selected_user" in st.session_state:
        UIErrorHandler.handle_service_call(
            lambda: show_user_details(st.session_state.selected_user)
        )


def show_user_details(user):
    """Show complete user details with profile, activities, and moderation tools"""
    from ui.components import (
        display_ban_form,
        display_message_form,
        display_moderation_actions,
        display_user_profile,
    )

    display_user_profile(user)

    if "selected_report_details" in st.session_state:
        show_report_details(st.session_state.selected_report_details)

    show_user_activities_and_messages(user)
    show_moderation_section(user["id"])


def show_report_details(report_details):
    """Show report information"""
    st.subheader("Report Information")
    st.metric("Total Reports", report_details["report_count"])

    if report_details["reporters"]:
        st.write("**Reported by:**")
        for i, reporter in enumerate(report_details["reporters"], 1):
            st.write(f"{i}. {reporter}")
    st.divider()


def show_user_activities_and_messages(user):
    """Show recent messages in an organized format"""
    st.subheader("Recent Messages")
    
    if not _has_recent_messages(user):
        st.info("No recent messages found.")
        return
    
    for i, msg in enumerate(user["recent_messages"]):
        _render_message_item(msg, i)


def _has_recent_messages(user) -> bool:
    """Check if user has recent messages"""
    return "recent_messages" in user and user["recent_messages"]


def _render_message_item(msg: dict, index: int):
    """Render individual message item"""
    message_preview = _create_message_preview(msg.get("content", ""))
    title = f"{msg['timestamp']} - Chat {msg['chat_id']} - {message_preview}"

    with st.expander(title, expanded=False):
        col1, col2 = st.columns([2, 1])

        with col1:
            _render_message_details(msg)

        with col2:
            _render_message_flags(msg)


def _create_message_preview(content: str, max_length: int = 60) -> str:
    """Create a preview of the message content"""
    if len(content) > max_length:
        return content[:max_length] + "..."
    return content


def _render_message_details(msg: dict):
    """Render message details in the main column"""
    st.write(f"**Timestamp:** {msg['timestamp']}")
    st.write(f"**Chat ID:** {msg['chat_id']}")
    st.write("**Message:**")
    st.code(msg.get("content", "No content"), language=None)


def _render_message_flags(msg: dict):
    """Render message flags in the side column"""
    if msg.get("flagged"):
        st.warning("⚠️ Flagged")


def show_moderation_section(user_id):
    """Show moderation actions and forms"""
    from ui.components import (
        display_ban_form,
        display_message_form,
        display_moderation_actions,
    )

    display_moderation_actions(user_id)

    if st.session_state.get("show_message_form", False):
        display_message_form(user_id, st.session_state.moderation_service)

    if st.session_state.get("show_ban_form", False):
        display_ban_form(user_id, st.session_state.moderation_service)
