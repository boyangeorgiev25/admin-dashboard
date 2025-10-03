import streamlit as st


def activity_types_tab():
    st.header("Activity Type Management")

    tab1, tab2 = st.tabs(["View Activity Types", "Add Activity Type"])

    with tab1:
        _view_activity_types()

    with tab2:
        _add_activity_type()


def _view_activity_types():
    st.subheader("All Activity Types")

    if st.button("🔄 Refresh", key="refresh_activity_types"):
        st.rerun()

    try:
        types = st.session_state.activity_type_service.get_all_activity_types()

        if not types:
            st.info("No activity types found")
            return

        st.write(f"Total: {len(types)} activity types")

        grouped = {}
        for t in types:
            if t['type'] not in grouped:
                grouped[t['type']] = []
            grouped[t['type']].append(t)

        for category, items in grouped.items():
            st.subheader(f"📁 {category}")

            for item in items:
                with st.expander(f"{item['emoji']} {item['subtype']} (Code: {item['subtype_code']})"):
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.write(f"**ID:** {item['id']}")
                        st.write(f"**English:** {item['subtype']}")
                        st.write(f"**Dutch:** {item['subtype_nl']}")
                        st.write(f"**French:** {item['subtype_fr']}")
                        st.write(f"**Code:** {item['subtype_code']}")
                        st.write(f"**Emoji:** {item['emoji']}")

                        if item['img_url']:
                            st.write(f"**Image:** {item['img_url']}")

                    with col2:
                        if st.button(f"🗑️ Delete", key=f"del_{item['id']}"):
                            _delete_activity_type(item['id'], item['subtype'])

    except Exception as e:
        st.error(f"Error loading activity types: {str(e)}")


def _add_activity_type():
    st.subheader("Add New Activity Type")

    with st.form("add_activity_type_form"):
        category = st.selectbox("Category*", ["Sports", "Culture", "Food", "Social", "Gaming", "Outdoor", "Other"])

        col1, col2 = st.columns(2)

        with col1:
            subtype = st.text_input("English Name*", max_chars=50, placeholder="e.g., Hiking")
            subtype_nl = st.text_input("Dutch Name*", max_chars=50, placeholder="e.g., Wandelen")
            subtype_fr = st.text_input("French Name*", max_chars=50, placeholder="e.g., Randonnée")

        with col2:
            subtype_code = st.number_input("Unique Code*", min_value=1, max_value=9999, value=1000)
            emoji = st.text_input("Emoji*", max_chars=10, placeholder="🏃")
            img_url = st.text_input("Image URL", max_chars=250, placeholder="default/hiking.webp")

        submitted = st.form_submit_button("Add Activity Type")

        if submitted:
            if not subtype or not subtype_nl or not subtype_fr or not emoji:
                st.error("All name fields and emoji are required")
            else:
                _save_activity_type(category, subtype, subtype_nl, subtype_fr, subtype_code, img_url, emoji)


def _save_activity_type(category, subtype, subtype_nl, subtype_fr, subtype_code, img_url, emoji):
    try:
        success = st.session_state.activity_type_service.add_activity_type(
            category, subtype, subtype_nl, subtype_fr, subtype_code, img_url, emoji
        )

        if success:
            st.success(f"✓ Added activity type: {emoji} {subtype}")
            st.balloons()
        else:
            st.error("Failed to add activity type")

    except Exception as e:
        st.error(f"Error: {str(e)}")


def _delete_activity_type(type_id, subtype):
    try:
        if st.session_state.activity_type_service.delete_activity_type(type_id):
            st.success(f"✓ Deleted activity type: {subtype}")
            st.rerun()
    except Exception as e:
        st.error(f"Error: {str(e)}")
