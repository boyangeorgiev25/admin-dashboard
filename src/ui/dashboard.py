"""Main dashboard entry point - optimized"""

import streamlit as st

from config.config import config
from core.auth import require_authentication
from core.security import AuditLogger


config.validate_config()
config.configure_streamlit_security()


def get_service(service_name, service_class):
    """Lazy service initialization"""
    if service_name not in st.session_state:
        st.session_state[service_name] = service_class()
    return st.session_state[service_name]


def init_core_services():
    """Initialize only essential services"""
    if "user_service" not in st.session_state:
        from services.user_service import UserService
        st.session_state.user_service = UserService()
    if "moderation_service" not in st.session_state:
        from services.moderation_service import ModerationService
        st.session_state.moderation_service = ModerationService()


def main():
    """Main dashboard entry point"""
    require_authentication()
    init_core_services()
    AuditLogger.log_action("DASHBOARD_ACCESS", {"page": "main"})

    st.title("Admin Dashboard")

    main_tab1, main_tab2, main_tab3, main_tab4, main_tab5 = st.tabs(
        ["Users", "Moderation", "Analytics", "Settings", "Communications"]
    )

    with main_tab1:
        sub_tab1, sub_tab2 = st.tabs(["Lookup", "Activities"])

        with sub_tab1:
            from ui.tabs.user_lookup_tab import user_lookup_tab
            user_lookup_tab()

        with sub_tab2:
            from ui.tabs.user_activities_tab import user_activities_tab
            user_activities_tab()

    with main_tab2:
        sub_tab1, sub_tab2, sub_tab3, sub_tab4 = st.tabs(
            ["Chats", "Forums", "Reports", "Feedback"]
        )

        with sub_tab1:
            if "chat_moderation_service" not in st.session_state:
                from services.chat_moderation_service import ChatModerationService
                st.session_state.chat_moderation_service = ChatModerationService()
            from ui.tabs.chat_moderation_tab import render as chat_moderation_tab
            chat_moderation_tab()

        with sub_tab2:
            from services.community_forum_service import CommunityForumService
            get_service("community_forum_service", CommunityForumService)
            from ui.tabs.forum_moderation_tab import render as forum_moderation_tab
            forum_moderation_tab()

        with sub_tab3:
            from ui.tabs.reports_tab import reports_tab
            reports_tab()

        with sub_tab4:
            from ui.tabs.feedback_tab import feedback_tab
            feedback_tab()

    with main_tab3:
        from services.analytics_service import AnalyticsService
        get_service("analytics_service", AnalyticsService)
        from ui.tabs.analytics_tab import analytics_tab
        analytics_tab()

    with main_tab4:
        sub_tab1, sub_tab2, sub_tab3 = st.tabs(
            ["Activity Types", "Venues", "Communities"]
        )

        with sub_tab1:
            from services.activity_type_service import ActivityTypeService
            get_service("activity_type_service", ActivityTypeService)
            from ui.tabs.activity_types_tab import activity_types_tab
            activity_types_tab()

        with sub_tab2:
            from services.venue_service import VenueService
            get_service("venue_service", VenueService)
            from ui.tabs.venues_tab import venues_tab
            venues_tab()

        with sub_tab3:
            from services.community_service import CommunityService
            get_service("community_service", CommunityService)
            from ui.tabs.communities_tab import communities_tab
            communities_tab()

    with main_tab5:
        sub_tab1, sub_tab2 = st.tabs(["Notifications", "ConvertKit"])

        with sub_tab1:
            from services.notification_service import NotificationService
            get_service("notification_service", NotificationService)
            from ui.tabs.notifications_tab import notifications_tab
            notifications_tab()

        with sub_tab2:
            from services.convertkit_service import ConvertKitService
            get_service("convertkit_service", ConvertKitService)
            from ui.tabs.convertkit_tab import convertkit_tab
            convertkit_tab()


if __name__ == "__main__":
    main()
