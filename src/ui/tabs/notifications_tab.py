import streamlit as st
import json
from ui.error_handler import UIErrorHandler


def notifications_tab():
    st.header("Bulk Notifications")

    st.markdown("Send push notifications to filtered users")

    st.subheader("Notification Content")

    title = st.text_input("Title*", max_chars=100, placeholder="New update available")
    body = st.text_area("Message*", max_chars=500, placeholder="Check out the new features...")

    st.subheader("Navigation (Optional)")
    screen = st.selectbox("Target Screen", ["None", "Browse", "Profile", "Activities", "Communities", "Chat"])

    st.subheader("User Filters")
    col1, col2 = st.columns(2)

    with col1:
        language = st.multiselect("Language", ["nl", "en", "fr"], default=["nl", "en", "fr"])
        reg_complete = st.checkbox("Only registered users", value=True)

    with col2:
        min_user_id = st.number_input("Min User ID (optional)", min_value=0, value=0)
        max_user_id = st.number_input("Max User ID (optional)", min_value=0, value=0)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📊 Preview Recipients", type="secondary", use_container_width=True):
            if not title or not body:
                st.error("Title and message are required")
            else:
                _preview_recipients(title, body, screen, language, reg_complete, min_user_id, max_user_id)

    with col2:
        if st.button("🚀 Send to All", type="primary", use_container_width=True):
            if not title or not body:
                st.error("Title and message are required")
            else:
                filters = {
                    "language": language,
                    "reg_complete": reg_complete,
                    "min_user_id": min_user_id if min_user_id > 0 else None,
                    "max_user_id": max_user_id if max_user_id > 0 else None
                }
                _send_notifications(title, body, screen, filters)


def _preview_recipients(title, body, screen, language, reg_complete, min_user_id, max_user_id):
    try:
        filters = {
            "language": language,
            "reg_complete": reg_complete,
            "min_user_id": min_user_id if min_user_id > 0 else None,
            "max_user_id": max_user_id if max_user_id > 0 else None
        }

        recipient_count = st.session_state.notification_service.get_recipient_count(filters)

        st.success(f"✓ Found {recipient_count} users matching filters")

        st.subheader("Preview")
        st.info(f"**{title}**\n\n{body}")

        if screen != "None":
            st.caption(f"→ Opens: {screen}")

    except Exception as e:
        st.error(f"Error: {str(e)}")


def _send_notifications(title, body, screen, filters):
    try:
        data = {"screen": screen} if screen != "None" else {}

        result = st.session_state.notification_service.send_bulk_notification(
            title, body, data, filters
        )

        st.success(f"✓ Sent {result['sent']} notifications successfully")

        if result['failed'] > 0:
            st.warning(f"⚠ {result['failed']} notifications failed")

    except Exception as e:
        st.error(f"Failed to send notifications: {str(e)}")


def _send_test_notifications(title, body, screen, filters):
    try:
        data = {"screen": screen} if screen != "None" else {}
        filters['limit'] = 5

        result = st.session_state.notification_service.send_bulk_notification(
            title, body, data, filters
        )

        st.success(f"✓ Test sent to {result['sent']} users")

    except Exception as e:
        st.error(f"Failed to send test: {str(e)}")
