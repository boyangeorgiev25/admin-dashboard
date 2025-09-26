"""Main dashboard entry point - simplified"""

import streamlit as st

from config.config import config
from core.auth import require_authentication
from core.security import AuditLogger
from services.analytics_service import AnalyticsService
from services.moderation_service import ModerationService
from services.user_service import UserService
from ui.tabs import analytics_tab, feedback_tab, reports_tab, user_lookup_tab


config.validate_config()
config.configure_streamlit_security()


def init_services():
    """Initialize services in session state"""
    if "user_service" not in st.session_state:
        st.session_state.user_service = UserService()
    if "moderation_service" not in st.session_state:
        st.session_state.moderation_service = ModerationService()
    if "analytics_service" not in st.session_state:
        st.session_state.analytics_service = AnalyticsService()


def main():
    """Main dashboard entry point"""
    # Require authentication before accessing dashboard
    require_authentication()

    init_services()

    AuditLogger.log_action("DASHBOARD_ACCESS", {"page": "main"})

    st.title("Platform Moderation Dashboard")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Reports", "Feedback", "User Lookup", "Analytics"]
    )

    with tab1:
        reports_tab()

    with tab2:
        feedback_tab()

    with tab3:
        user_lookup_tab()

    with tab4:
        analytics_tab()


if __name__ == "__main__":
    main()
