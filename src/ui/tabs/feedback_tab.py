"""Feedback tab functionality"""

import logging

import streamlit as st

from core.security import security_validator


def feedback_tab():
    """Handle feedback tab - shows all feedback from users"""
    st.header("User Feedback")

    # Search functionality
    search_query = st.text_input(
        "Search feedback by user or content:",
        placeholder="Enter search term...",
        help="Search through feedback messages",
    )

    if search_query and not security_validator.validate_search_query(search_query):
        st.error("Invalid search query. Please check your input.")
        return

    try:

        feedback_list = st.session_state.moderation_service.get_sent_feedback()

        if search_query:
            feedback_list = [
                f
                for f in feedback_list
                if search_query.lower() in f.get("user_name", "").lower()
                or search_query.lower() in f.get("message", "").lower()
                or search_query in str(f.get("user_id", ""))
            ]

        if not feedback_list:
            st.info("No feedback found.")
            return

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            feedback_limit = st.selectbox(
                "Show feedback:",
                [10, 20, 50, 100, "All"],
                index=1, 
                help="Select how many feedback items to display",
            )
        with col2:
            sort_option = st.selectbox(
                "Sort by:",
                ["Rating", "Date"],
                index=0, 
                help="Choose how to sort feedback",
            )
        with col3:
            total_available = len(feedback_list)
            st.metric("Available", total_available)

        if sort_option == "Date":
            feedback_list = sorted(
                feedback_list, key=lambda x: x.get("id", 0), reverse=True
            )

        if feedback_limit != "All":
            feedback_list = feedback_list[: int(feedback_limit)]

        st.info(f"Showing {len(feedback_list)} feedback messages")

        for feedback in feedback_list:
            user_name = feedback.get(
                "user_name", f"User {feedback.get('user_id', 'Unknown')}"
            )
            message_preview = (
                feedback.get("message", "")[:60] + "..."
                if len(feedback.get("message", "")) > 60
                else feedback.get("message", "")
            )
            rating = feedback.get("rating", 0)

            if rating and rating > 0:
                rating_stars = "⭐" * int(rating)
                title = f"{rating_stars} {user_name} - {message_preview}"
            else:
                title = f"⚪ {user_name} - {message_preview}"

            with st.expander(title, expanded=False):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.write(f"**From:** {user_name}")
                    st.write(f"**User ID:** {feedback.get('user_id', 'Unknown')}")
                    if feedback.get("rating"):
                        st.write(f"**Rating:** {feedback.get('rating')} ⭐")
                    st.write("**Feedback:**")
                    st.text_area(
                        "Feedback Message",
                        value=feedback.get("message", "No feedback"),
                        height=100,
                        disabled=True,
                        key=f"msg_{feedback.get('id', 'unknown')}",
                        label_visibility="collapsed",
                    )

                with col2:
                    st.info("💬 User Feedback")

                    if st.button(
                        "View User Profile",
                        key=f"profile_{feedback.get('id', 'unknown')}",
                    ):
                        # Load user profile
                        user = st.session_state.user_service.get_user(
                            "user_id", str(feedback.get("user_id", ""))
                        )
                        if user:
                            st.session_state.selected_user = user
                            st.success("User profile loaded - check User Lookup tab")
                        else:
                            st.error("User not found")

    except Exception as e:
        st.error(f"Error loading feedback: {str(e)}")
        logging.error(f"Feedback tab error: {str(e)}", exc_info=True)


def show_feedback_stats():
    """Show feedback statistics"""
    try:
        feedback_list = st.session_state.moderation_service.get_sent_feedback()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Sent", len(feedback_list))

        with col2:
            read_count = sum(1 for f in feedback_list if f.get("read_status"))
            st.metric("Read", read_count)

        with col3:
            unread_count = len(feedback_list) - read_count
            st.metric("Unread", unread_count)

        with col4:
            recent_count = 0
            st.metric("Last 7 Days", recent_count)

    except Exception as e:
        logging.error(f"Feedback stats error: {str(e)}", exc_info=True)
