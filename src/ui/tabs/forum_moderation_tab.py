import streamlit as st

from services.community_forum_service import CommunityForumService
from services.community_service import CommunityService


def render():
    st.header("Forum Moderation")

    forum_service = CommunityForumService()
    community_service = CommunityService()

    try:
        stats = forum_service.get_forum_stats()

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Posts", f"{stats['total_posts']:,}")
        with col2:
            st.metric("Threads", f"{stats['total_threads']:,}")
        with col3:
            st.metric("Replies", f"{stats['total_replies']:,}")
        with col4:
            reported = stats['total_reported']
            st.metric("Reported", f"{reported:,}")

    except Exception as e:
        st.error(f"Error loading stats: {str(e)}")

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["All Threads", "Reported", "Search", "Members"]
    )

    with tab1:
        render_all_threads(forum_service, community_service)

    with tab2:
        render_reported_content(forum_service)

    with tab3:
        render_search(forum_service)

    with tab4:
        render_members(forum_service, community_service)


def render_all_threads(forum_service: CommunityForumService, community_service: CommunityService):
    st.subheader("All Forum Threads")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search = st.text_input(
            "Search threads",
            placeholder="Search by title or content...",
            key="thread_search",
        )
    with col2:
        try:
            communities = community_service.get_all_communities()
            community_options = ["All Communities"] + [
                f"{c['name']} (ID: {c['id']})" for c in communities
            ]
            selected_community = st.selectbox(
                "Filter by community", community_options, key="community_filter"
            )
        except:
            selected_community = "All Communities"
    with col3:
        limit = st.number_input("Limit", min_value=10, max_value=200, value=50, step=10, key="thread_limit")

    community_id = None
    if selected_community != "All Communities":
        try:
            community_id = int(selected_community.split("ID: ")[1].rstrip(")"))
        except:
            pass

    try:
        threads = forum_service.get_threads(
            limit=limit,
            search=search if search else None,
            community_id=community_id,
        )

        if not threads:
            st.info("No threads found")
            return

        st.write(f"**Found {len(threads)} threads**")

        for thread in threads:
            reported_badge = "🚩 " if thread['is_reported'] else ""
            with st.expander(
                f"{reported_badge}**{thread['title']}** - {thread['community_name']} - {thread['reply_count']} replies, {thread['upvote_count']} upvotes"
            ):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.write(f"**Thread ID:** {thread['id']}")
                    st.write(f"**Community:** {thread['community_name']}")
                    st.write(f"**Author:** {thread['owner_name']} (ID: {thread['owner_id']})")
                    st.write(f"**Created:** {thread['created_at']}")
                    st.write(f"**Last Updated:** {thread['last_updated']}")
                    st.write(f"**Upvotes:** {thread['upvote_count']}")

                    st.markdown("---")
                    st.text_area(
                        "Content",
                        value=thread['body_full'],
                        height=150,
                        key=f"thread_content_{thread['id']}",
                        disabled=True,
                    )

                with col2:
                    if thread['is_reported']:
                        st.error("⚠️ REPORTED")

                    if st.button(f"View Replies ({thread['reply_count']})", key=f"view_replies_{thread['id']}"):
                        st.session_state[f"show_replies_{thread['id']}"] = True

                    st.markdown("---")
                    if st.button("🗑️ Delete Thread", key=f"delete_thread_{thread['id']}"):
                        st.session_state[f"confirm_delete_thread_{thread['id']}"] = True

                if st.session_state.get(f"confirm_delete_thread_{thread['id']}", False):
                    reason = st.text_input(
                        "Reason for deletion (required)",
                        key=f"delete_reason_thread_{thread['id']}",
                    )
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("Confirm Delete", key=f"confirm_delete_btn_{thread['id']}", type="primary"):
                            if reason and len(reason) >= 5:
                                try:
                                    forum_service.delete_thread(thread['id'], reason)
                                    st.success("Thread deleted successfully")
                                    st.session_state[f"confirm_delete_thread_{thread['id']}"] = False
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error deleting thread: {str(e)}")
                            else:
                                st.error("Reason must be at least 5 characters")
                    with col_b:
                        if st.button("Cancel", key=f"cancel_delete_{thread['id']}"):
                            st.session_state[f"confirm_delete_thread_{thread['id']}"] = False

                if st.session_state.get(f"show_replies_{thread['id']}", False):
                    st.markdown("---")
                    st.write("**💬 Replies:**")
                    try:
                        replies = forum_service.get_thread_replies(thread['id'])
                        if replies:
                            for reply in replies:
                                reported_badge_reply = "🚩 " if reply.get('is_reported') else ""
                                parent_info = f" (replying to {reply['parent_author']})" if reply.get('parent_author') else ""

                                with st.container():
                                    st.markdown(f"---")
                                    col_r1, col_r2 = st.columns([3, 1])
                                    with col_r1:
                                        st.write(f"{reported_badge_reply}**{reply['owner_name']}**{parent_info} - {reply['created_at']}")
                                        st.write(reply['body'])
                                        st.caption(f"👍 {reply['upvote_count']} upvotes")
                                    with col_r2:
                                        if st.button("🗑️", key=f"delete_reply_{reply['id']}"):
                                            st.session_state[f"confirm_delete_reply_{reply['id']}"] = True

                                if st.session_state.get(f"confirm_delete_reply_{reply['id']}", False):
                                    reason_r = st.text_input(
                                        "Reason for deletion",
                                        key=f"delete_reason_reply_{reply['id']}",
                                    )
                                    if st.button("Confirm Delete Reply", key=f"confirm_delete_reply_btn_{reply['id']}"):
                                        if reason_r and len(reason_r) >= 5:
                                            try:
                                                forum_service.delete_reply(reply['id'], reason_r)
                                                st.success("Reply deleted")
                                                st.session_state[f"confirm_delete_reply_{reply['id']}"] = False
                                                st.rerun()
                                            except Exception as e:
                                                st.error(f"Error: {str(e)}")
                                        else:
                                            st.error("Reason must be at least 5 characters")
                        else:
                            st.info("No replies yet")
                    except Exception as e:
                        st.error(f"Error loading replies: {str(e)}")

    except Exception as e:
        st.error(f"Error loading threads: {str(e)}")


def render_reported_content(forum_service: CommunityForumService):
    st.subheader("Reported Forum Content")

    try:
        reported = forum_service.get_reported_content()

        threads = reported.get('threads', [])
        replies = reported.get('replies', [])

        if not threads and not replies:
            st.success("✅ No reported content!")
            return

        st.warning(f"Found {len(threads)} reported threads and {len(replies)} reported replies")

        if threads:
            st.write("### Reported Threads")
            for thread in threads:
                with st.expander(f"🚩 {thread['title']} - {thread['community_name']}"):
                    st.write(f"**Author:** {thread['owner_name']}")
                    st.write(f"**Created:** {thread['created_at']}")
                    st.write(f"**Content:** {thread['body']}")

                    if st.button(f"🗑️ Delete Thread", key=f"delete_reported_thread_{thread['id']}"):
                        st.session_state[f"confirm_delete_reported_thread_{thread['id']}"] = True

                    if st.session_state.get(f"confirm_delete_reported_thread_{thread['id']}", False):
                        reason = st.text_input(
                            "Deletion reason",
                            key=f"reported_thread_reason_{thread['id']}",
                        )
                        if st.button("Confirm", key=f"confirm_reported_thread_{thread['id']}"):
                            if reason and len(reason) >= 5:
                                try:
                                    forum_service.delete_thread(thread['id'], reason)
                                    st.success("Deleted")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                            else:
                                st.error("Reason must be at least 5 characters")

        if replies:
            st.write("### Reported Replies")
            for reply in replies:
                with st.expander(f"🚩 Reply in '{reply['thread_title']}'"):
                    st.write(f"**Author:** {reply['owner_name']}")
                    st.write(f"**Created:** {reply['created_at']}")
                    st.write(f"**Content:** {reply['body']}")

                    if st.button(f"🗑️ Delete Reply", key=f"delete_reported_reply_{reply['id']}"):
                        st.session_state[f"confirm_delete_reported_reply_{reply['id']}"] = True

                    if st.session_state.get(f"confirm_delete_reported_reply_{reply['id']}", False):
                        reason = st.text_input(
                            "Deletion reason",
                            key=f"reported_reply_reason_{reply['id']}",
                        )
                        if st.button("Confirm", key=f"confirm_reported_reply_{reply['id']}"):
                            if reason and len(reason) >= 5:
                                try:
                                    forum_service.delete_reply(reply['id'], reason)
                                    st.success("Deleted")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                            else:
                                st.error("Reason must be at least 5 characters")

    except Exception as e:
        st.error(f"Error loading reported content: {str(e)}")


def render_search(forum_service: CommunityForumService):
    st.subheader("Search Forum Content")

    col1, col2 = st.columns([3, 1])
    with col1:
        keyword = st.text_input(
            "Search keyword",
            placeholder="Search threads and replies...",
            key="forum_search",
        )
    with col2:
        limit = st.number_input("Max results", min_value=20, max_value=200, value=50, step=10, key="forum_search_limit")

    if st.button("🔍 Search", type="primary"):
        if not keyword or len(keyword) < 2:
            st.error("Search keyword must be at least 2 characters")
            return

        try:
            results = forum_service.search_forum_content(keyword, limit=limit)

            if not results:
                st.info(f"No content found containing '{keyword}'")
                return

            st.success(f"Found {len(results)} results")

            for result in results:
                type_icon = "📝" if result['type'] == "thread" else "💬"
                reported_badge = "🚩 " if result.get('is_reported') else ""

                if result['type'] == "thread":
                    title = f"{type_icon} {reported_badge}{result['title']}"
                else:
                    title = f"{type_icon} {reported_badge}Reply in '{result['thread_title']}'"

                with st.expander(title):
                    st.write(f"**Type:** {result['type'].title()}")
                    st.write(f"**Author:** {result['owner_name']}")

                    if result['type'] == "thread":
                        st.write(f"**Community:** {result['community_name']}")

                    st.write(f"**Created:** {result['created_at']}")

                    st.text_area(
                        "Content",
                        value=result['body'],
                        height=100,
                        key=f"search_result_{result['type']}_{result['id']}",
                        disabled=True,
                    )

        except Exception as e:
            st.error(f"Error searching: {str(e)}")


def render_members(forum_service: CommunityForumService, community_service: CommunityService):
    st.subheader("Community Members")

    try:
        communities = community_service.get_all_communities()
        community_options = [f"{c['name']} (ID: {c['id']})" for c in communities]

        if not community_options:
            st.info("No communities found")
            return

        selected = st.selectbox("Select community", community_options, key="member_community")

        community_id = int(selected.split("ID: ")[1].rstrip(")"))

        members = forum_service.get_community_members(community_id)

        st.metric("Total Members", len(members))

        if members:
            st.write("### Member List")
            for member in members:
                with st.expander(f"👤 {member['username']} (ID: {member['user_id']})"):
                    st.write(f"**Email:** {member['email']}")
                    st.write(f"**Last Visited:** {member['last_visited']}")
        else:
            st.info("No members in this community")

    except Exception as e:
        st.error(f"Error loading members: {str(e)}")
