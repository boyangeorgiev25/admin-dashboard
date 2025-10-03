import streamlit as st


def convertkit_tab():
    st.header("ConvertKit Email Management")

    st.markdown("Sync users with ConvertKit email list and manage language preferences")

    if not st.session_state.convertkit_service.api_key:
        st.warning("⚠️ ConvertKit API credentials not configured in .env file")
        return

    tab1, tab2 = st.tabs(["Add Subscriber", "Sync Users"])

    with tab1:
        _add_subscriber()

    with tab2:
        _sync_users()


def _add_subscriber():
    st.subheader("Add Single Subscriber")

    with st.form("add_subscriber_form"):
        email = st.text_input("Email*", placeholder="user@example.com")
        first_name = st.text_input("First Name", placeholder="John", value="Added from dashboard")
        language = st.selectbox("Language", ["nl", "en", "fr"], index=0)

        submitted = st.form_submit_button("Add to ConvertKit")

        if submitted:
            if not email or "@" not in email:
                st.error("Valid email is required")
            else:
                _add_single_subscriber(email, first_name, language)


def _add_single_subscriber(email, first_name, language):
    try:
        success = st.session_state.convertkit_service.add_subscriber(
            email, first_name, language
        )

        if success:
            st.success(f"✓ Added {email} to ConvertKit")
        else:
            st.error("Failed to add subscriber")

    except Exception as e:
        st.error(f"Error: {str(e)}")


def _sync_users():
    st.subheader("Bulk Sync Users to ConvertKit")

    st.info("This will sync registered users with ConvertKit, updating language preferences")

    col1, col2 = st.columns(2)

    with col1:
        language_filter = st.multiselect("Filter by language", ["nl", "en", "fr"], default=["nl", "en", "fr"])

    with col2:
        limit = st.number_input("Max users to sync", min_value=1, max_value=1000, value=50)

    if st.button("Preview Users", key="preview_convertkit_users"):
        _preview_sync_users(language_filter, limit)

    if st.button("🚀 Start Sync", type="primary", key="start_convertkit_sync"):
        _sync_users_to_convertkit(language_filter, limit)


def _preview_sync_users(language_filter, limit):
    try:
        from services.user_service import UserService
        from core.models import User

        user_service = UserService()

        with user_service.db_service.get_session() as db:
            query = db.query(User).filter(
                User.reg_complete == True,
                User.language.in_(language_filter)
            ).limit(limit)

            users = query.all()

            st.write(f"**Found {len(users)} users to sync**")

            preview = []
            for user in users[:10]:
                preview.append({
                    "ID": user.id,
                    "Name": user.name or "N/A",
                    "Email": user.email or "N/A",
                    "Language": user.language or "N/A"
                })

            if preview:
                st.table(preview)

                if len(users) > 10:
                    st.caption(f"Showing first 10 of {len(users)} users")

    except Exception as e:
        st.error(f"Error: {str(e)}")


def _sync_users_to_convertkit(language_filter, limit):
    try:
        from services.user_service import UserService
        from core.models import User

        user_service = UserService()

        with user_service.db_service.get_session() as db:
            query = db.query(User).filter(
                User.reg_complete == True,
                User.language.in_(language_filter)
            ).limit(limit)

            users = query.all()

            user_list = [
                {
                    "email": u.email,
                    "name": u.name,
                    "language": u.language
                }
                for u in users if u.email
            ]

        with st.spinner(f"Syncing {len(user_list)} users..."):
            result = st.session_state.convertkit_service.bulk_sync_users(user_list)

        st.success(f"✓ Synced {result['synced']} users successfully")

        if result['failed'] > 0:
            st.warning(f"⚠ {result['failed']} users failed to sync")

    except Exception as e:
        st.error(f"Error: {str(e)}")
