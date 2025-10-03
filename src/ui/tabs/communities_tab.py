import streamlit as st


def communities_tab():
    st.header("Communities")

    tab1, tab2 = st.tabs(["View", "Add"])

    with tab1:
        _view_communities()

    with tab2:
        _add_community()


def _view_communities():
    if st.button("Refresh", key="refresh_communities"):
        st.rerun()

    try:
        communities = st.session_state.community_service.get_all_communities()

        if not communities:
            st.info("No communities found")
            return

        st.write(f"Total: {len(communities)} communities")

        starters = [c for c in communities if c.get('is_starter')]
        regulars = [c for c in communities if not c.get('is_starter')]

        if starters:
            st.subheader("Starter Communities")
            for community in starters:
                _render_community_card(community)

        if regulars:
            st.subheader("Regular Communities")
            for community in regulars:
                _render_community_card(community)

    except Exception as e:
        st.error(f"Error loading communities: {str(e)}")


def _render_community_card(community):
    with st.expander(f"{'⭐' if community['is_starter'] else '📍'} {community['name']}"):
        col1, col2 = st.columns([2, 1])

        with col1:
            st.write(f"**ID:** {community['id']}")
            st.write(f"**Description:** {community['description']}")
            st.write(f"**Location:** {community['location']}")
            st.write(f"**Starter Community:** {'Yes' if community['is_starter'] else 'No'}")

        with col2:
            if community['img_url']:
                try:
                    st.image(community['img_url'], width=150)
                except:
                    st.caption(f"Image: {community['img_url']}")

            if st.button(f"🗑️ Delete", key=f"del_community_{community['id']}"):
                _delete_community(community['id'], community['name'])


def _add_community():
    st.subheader("Add Community")

    with st.form("add_community_form"):
        name = st.text_input("Community Name*", max_chars=40, placeholder="Brussels Expats")

        description = st.text_area("Description*", max_chars=300, placeholder="Connect with expats in Brussels...")

        img_url = st.text_input("Image URL*", max_chars=150, placeholder="https://storage.googleapis.com/...")

        col1, col2 = st.columns(2)

        with col1:
            latitude = st.number_input("Latitude*", format="%.6f", value=50.8503, step=0.0001)

        with col2:
            longitude = st.number_input("Longitude*", format="%.6f", value=4.3517, step=0.0001)

        is_starter = st.checkbox("Starter Community", help="Starter communities are auto-assigned to new users based on location")

        st.info(f"Location will be: POINT({longitude} {latitude})")

        submitted = st.form_submit_button("Add Community")

        if submitted:
            if not name or not description or not img_url:
                st.error("Name, description, and image URL are required")
            else:
                location = f"POINT({longitude} {latitude})"
                _save_community(name, description, img_url, location, is_starter)


def _save_community(name, description, img_url, location, is_starter):
    try:
        success = st.session_state.community_service.add_community(
            name, description, img_url, location, is_starter
        )

        if success:
            st.success(f"✓ Added community: {name}")
            st.balloons()
        else:
            st.error("Failed to add community")

    except Exception as e:
        st.error(f"Error: {str(e)}")


def _delete_community(community_id, community_name):
    try:
        if st.session_state.community_service.delete_community(community_id):
            st.success(f"✓ Deleted community: {community_name}")
            st.rerun()
    except Exception as e:
        st.error(f"Error: {str(e)}")
