import streamlit as st


def render():
    st.header("Chat Moderation")

    service = st.session_state.chat_moderation_service

    try:
        stats = service.get_chat_stats()

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Chats", f"{stats['total_chats']:,}")
        with col2:
            st.metric("Activity Chats", f"{stats['total_activity_chats']:,}")
        with col3:
            st.metric("Direct Messages", f"{stats['total_individual_chats']:,}")
        with col4:
            st.metric("Total Messages", f"{stats['total_messages']:,}")

    except Exception as e:
        st.error(f"Error loading stats: {str(e)}")

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(
        ["Activity Chats", "Direct Messages", "Search"]
    )

    with tab1:
        render_activity_chats(service)

    with tab2:
        render_individual_chats(service)

    with tab3:
        render_message_search(service)


def render_activity_chats(service):
    st.subheader("Activity Group Chats")

    search_col, limit_col = st.columns([3, 1])
    with search_col:
        search = st.text_input(
            "Search activity chats",
            placeholder="Search by activity name, message, or sender...",
            key="activity_search",
        )
    with limit_col:
        limit = st.number_input("Limit", min_value=10, max_value=200, value=50, step=10, key="activity_limit")

    try:
        chats = service.get_activity_chats(limit=limit, search=search if search else None)

        if not chats:
            st.info("No activity chats found")
            return

        st.write(f"**Found {len(chats)} chats**")

        for chat in chats:
            with st.expander(
                f"🏃 {chat['activity_name'] or 'Unknown Activity'} - {chat['member_count']} members - {chat['message_count']} messages"
            ):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.write(f"**Activity ID:** {chat['activity_id']}")
                    st.write(f"**Chat ID:** {chat['id']}")
                    st.write(f"**City:** {chat['activity_city'] or 'N/A'}")
                    st.write(f"**Last Sender:** {chat['last_sender_name']}")
                    st.write(f"**Last Message:** {chat['last_message'] or 'No messages'}")
                    st.write(f"**Last Active:** {chat['last_timestamp']}")

                with col2:
                    if st.button(f"View Messages", key=f"view_activity_{chat['id']}"):
                        st.session_state[f"show_messages_{chat['id']}"] = True

                if st.session_state.get(f"show_messages_{chat['id']}", False):
                    st.markdown("---")
                    st.write("**💬 Chat Messages:**")
                    try:
                        messages = service.get_chat_messages(chat['id'], chat_type="activity")
                        if messages:
                            for msg in messages[-20:]:
                                deleted_badge = "🗑️ " if msg.get('is_deleted') else ""
                                edited_badge = "✏️ " if msg.get('is_edited') else ""
                                st.text(
                                    f"{deleted_badge}{edited_badge}[{msg['timestamp']}] {msg['sender_name']}: {msg['content'][:100]}"
                                )
                        else:
                            st.info("No messages in this chat")
                    except Exception as e:
                        st.error(f"Error loading messages: {str(e)}")

    except Exception as e:
        st.error(f"Error loading activity chats: {str(e)}")


def render_individual_chats(service):
    st.subheader("Individual Direct Messages")

    search_col, limit_col = st.columns([3, 1])
    with search_col:
        search = st.text_input(
            "Search direct messages",
            placeholder="Search by activity name, message, or sender...",
            key="dm_search",
        )
    with limit_col:
        limit = st.number_input("Limit", min_value=10, max_value=200, value=50, step=10, key="dm_limit")

    try:
        chats = service.get_individual_chats(limit=limit, search=search if search else None)

        if not chats:
            st.info("No direct messages found")
            return

        st.write(f"**Found {len(chats)} chats**")

        for chat in chats:
            with st.expander(
                f"💬 {chat['owner_name']} ↔️ {chat['receiver_name']} - {chat['message_count']} messages"
            ):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.write(f"**Chat ID:** {chat['id']}")
                    st.write(f"**Activity:** {chat['activity_name'] or 'N/A'}")
                    st.write(f"**Owner:** {chat['owner_name']} (ID: {chat['owner_id']})")
                    st.write(f"**Receiver:** {chat['receiver_name']} (ID: {chat['receiver_id']})")
                    st.write(f"**Last Sender:** {chat['last_sender_name']}")
                    st.write(f"**Last Message:** {chat['last_message'] or 'No messages'}")
                    st.write(f"**Last Active:** {chat['last_timestamp']}")

                with col2:
                    if st.button(f"View Messages", key=f"view_dm_{chat['id']}"):
                        st.session_state[f"show_dm_messages_{chat['id']}"] = True

                if st.session_state.get(f"show_dm_messages_{chat['id']}", False):
                    st.markdown("---")
                    st.write("**💬 Chat Messages:**")
                    try:
                        messages = service.get_chat_messages(chat['id'], chat_type="individual")
                        if messages:
                            for msg in messages[-20:]:
                                image_badge = "🖼️ " if msg.get('image_url') else ""
                                st.text(
                                    f"{image_badge}[{msg['timestamp']}] {msg['sender_name']}: {msg['content'][:100]}"
                                )
                        else:
                            st.info("No messages in this chat")
                    except Exception as e:
                        st.error(f"Error loading messages: {str(e)}")

    except Exception as e:
        st.error(f"Error loading direct messages: {str(e)}")


def render_message_search(service):
    st.subheader("Search All Messages")

    col1, col2 = st.columns([3, 1])
    with col1:
        keyword = st.text_input(
            "Search keyword",
            placeholder="Enter keyword to search in all messages (min 2 characters)...",
            key="message_search",
        )
    with col2:
        limit = st.number_input("Max results", min_value=20, max_value=500, value=100, step=20, key="search_limit")

    if st.button("🔍 Search Messages", type="primary"):
        if not keyword or len(keyword) < 2:
            st.error("Search keyword must be at least 2 characters")
            return

        try:
            with st.spinner("Searching messages..."):
                results = service.search_messages(keyword, limit=limit)

            if not results:
                st.info(f"No messages found containing '{keyword}'")
                return

            st.success(f"Found {len(results)} messages")

            for result in results:
                chat_type_icon = "🏃" if result['type'] == "activity" else "💬"
                with st.expander(
                    f"{chat_type_icon} [{result['timestamp']}] {result['sender_name']} in {result['chat_name']}"
                ):
                    st.write(f"**Type:** {result['type'].title()}")
                    st.write(f"**Chat ID:** {result['chat_id']}")
                    st.write(f"**Message ID:** {result['message_id']}")
                    st.write(f"**Sender:** {result['sender_name']} (ID: {result['sender_id']})")
                    st.write(f"**Time:** {result['timestamp']}")
                    st.text_area(
                        "Content",
                        value=result['content'],
                        height=100,
                        key=f"msg_content_{result['message_id']}_{result['type']}",
                        disabled=True,
                    )

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(
                            "🚩 Flag as Inappropriate",
                            key=f"flag_{result['message_id']}_{result['type']}",
                        ):
                            st.session_state[f"flag_reason_{result['message_id']}_{result['type']}"] = True

                    if st.session_state.get(f"flag_reason_{result['message_id']}_{result['type']}", False):
                        reason = st.text_input(
                            "Reason for flagging",
                            key=f"reason_input_{result['message_id']}_{result['type']}",
                        )
                        if st.button(
                            "Confirm Flag",
                            key=f"confirm_flag_{result['message_id']}_{result['type']}",
                        ):
                            try:
                                service.flag_message(
                                    result['message_id'], result['type'], reason
                                )
                                st.success("Message flagged successfully")
                                st.session_state[f"flag_reason_{result['message_id']}_{result['type']}"] = False
                            except Exception as e:
                                st.error(f"Error flagging message: {str(e)}")

        except Exception as e:
            st.error(f"Error searching messages: {str(e)}")
