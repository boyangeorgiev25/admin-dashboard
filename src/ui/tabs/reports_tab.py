"""Reports tab functionality"""

import streamlit as st

from core.security import security_validator


def reports_tab():
    """Handle reports tab"""
    st.header("User Reports")

  
    search_query = st.text_input(
        "Search by username or user ID:",
        placeholder="Enter search term...",
        help="Search through user reports to find specific users",
    )

   
    if search_query and not security_validator.validate_search_query(search_query):
        st.error("Invalid search query. Please check your input.")
        return

    try:
        reports = st.session_state.moderation_service.get_pending_reports()

        if search_query:
            reports = [
                r
                for r in reports
                if search_query.lower() in r.get("reported_user", "").lower()
                or search_query in str(r.get("reported_user_id", ""))
            ]

        if not reports:
            st.info("No reports found.")
            return

       
        if reports:
            st.info(f"Found {len(reports)} reports")

        for report in reports:
            report_count = report.get("report_count", 1)
            priority = (
                "🔴 HIGH"
                if report_count >= 5
                else "🟡 MEDIUM" if report_count >= 3 else "🟢 LOW"
            )

            with st.expander(
                f"{priority} - {report['reported_user']} (ID: {report['reported_user_id']}) - {report_count} reports",
                expanded=False,
            ):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.write(f"**User:** {report['reported_user']}")
                    st.write(f"**User ID:** {report['reported_user_id']}")
                    st.write(f"**Details:** {report['description']}")

                with col2:
                    if st.button("View User", key=f"view_{report['id']}"):
                        user = st.session_state.user_service.get_user_from_report(
                            report["reported_user_id"]
                        )
                        if user:
                            report_details = {
                                "reporters": report.get("reporters", []),
                                "report_count": report.get("report_count", 0),
                            }
                            st.session_state.selected_user = user
                            st.session_state.selected_report_details = report_details
                            st.success("User loaded")
                            show_compact_user_info(user, report_details)
                        else:
                            st.error("User not found")

    except Exception as e:
        st.error(f"Error loading reports: {str(e)}")


def show_compact_user_info(user, report_details):
    """Display essential user info in reports context"""
    st.subheader(f"User: {user['username']}")

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Last Active:** {user['last_active']}")
        st.write(f"**Email:** {user['email']}")
    with col2:
        st.write(f"**Total Reports:** {report_details['report_count']}")
        st.write(f"**Message Count:** {user['message_count']}")

   
    if report_details["reporters"]:
        st.write("**Reported by:**")
        st.write(", ".join(report_details["reporters"]))

   
    if user.get("recent_messages"):
        st.write("**Recent Messages:**")
        for msg in user["recent_messages"][:3]:
            st.write(
                f"• {msg['timestamp']}: {msg['content'][:50]}{'...' if len(msg['content']) > 50 else ''}"
            )
