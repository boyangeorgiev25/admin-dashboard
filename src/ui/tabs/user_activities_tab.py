import streamlit as st

from core.security import security_validator
from ui.error_handler import UIErrorHandler


def user_activities_tab():
    st.header("User Activities & Messages")

    col1, col2 = st.columns([1, 3])

    with col1:
        _render_search_section()

    with col2:
        _render_user_activities_section()


def _render_search_section():
    st.subheader("Search User")
    search_type = st.selectbox("Search by:", ["User ID", "Username"], key="user_activities_search_type")
    search_value = st.text_input(
        f"Enter {search_type}:", placeholder=f"Type {search_type.lower()} here...", key="user_activities_search_value"
    )
    search_button = st.button("Search", type="primary", key="user_activities_search_button")

    if search_button and search_value:
        if not security_validator.validate_search_query(search_value):
            st.error("Invalid search query. Please check your input.")
            return

        _perform_user_search(search_type, search_value)


def _perform_user_search(search_type: str, search_value: str):
    try:
        user = st.session_state.user_service.get_user(
            search_type.lower().replace(" ", "_"), search_value
        )
        if user:
            st.session_state.selected_user_activities = user
            st.success(f"User found: {user['username']}")
        else:
            st.info("User not found")
    except Exception as e:
        st.info("User not found")


def _render_user_activities_section():
    if "selected_user_activities" in st.session_state:
        UIErrorHandler.handle_service_call(
            lambda: show_user_activities(st.session_state.selected_user_activities)
        )


def show_user_activities(user):
    st.subheader(f"Activities for {user['username']}")

    activities = st.session_state.user_service.get_user_activities(user['id'])

    if not activities:
        st.info("No activities found for this user.")
        return

    activity_messages = st.session_state.user_service.get_user_activity_messages(user['id'])

    st.metric("Total Activities", len(activities))
    st.divider()

    for activity in activities:
        _render_activity_card(activity, user['id'], activity_messages)


def _render_activity_card(activity, user_id, activity_messages):
    status_emoji = "👑" if activity['is_owner'] else "👤"
    status_text = activity['status']

    with st.expander(
        f"{status_emoji} {activity['name']} - {activity['date']} ({status_text})",
        expanded=False
    ):
        col1, col2 = st.columns([2, 1])

        with col1:
            st.write(f"**Description:** {activity['description']}")
            st.write(f"**Date:** {activity['date']}")
            st.write(f"**City:** {activity['city']}")
            if activity.get('location'):
                st.write(f"**Location:** {activity['location']}")
            if activity.get('place'):
                st.write(f"**Venue:** {activity['place']}")

        with col2:
            st.write(f"**Status:** {status_text}")
            if activity['is_full']:
                st.warning("⚠️ Full")
            if activity.get('participants_min') and activity.get('participants_max'):
                st.write(f"**Participants:** {activity['participants_min']}-{activity['participants_max']}")
            if activity.get('min_age') and activity.get('max_age'):
                st.write(f"**Age Range:** {activity['min_age']}-{activity['max_age']}")

        if activity.get('question1') or activity.get('question2') or activity.get('question3'):
            st.write("---")
            st.write("**Joining Questions:**")
            if activity.get('question1'):
                st.write(f"1. {activity['question1']}")
            if activity.get('question2'):
                st.write(f"2. {activity['question2']}")
            if activity.get('question3'):
                st.write(f"3. {activity['question3']}")

        messages = activity_messages.get(activity['activity_id'], [])
        if messages:
            st.write("---")
            st.write(f"**Recent Messages ({len(messages)}):**")
            for msg in messages:
                _render_message_preview(msg)
        else:
            st.write("---")
            st.info("No messages in this activity")


def _render_message_preview(msg):
    message_preview = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']

    flags = []
    if msg.get('is_deleted'):
        flags.append("🗑️ Deleted")
    if msg.get('is_edited'):
        flags.append("✏️ Edited")

    flag_text = " ".join(flags)

    st.text(f"{msg['timestamp']} {flag_text}")
    st.code(message_preview, language=None)
