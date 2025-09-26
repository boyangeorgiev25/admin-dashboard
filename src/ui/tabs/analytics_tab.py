import pandas as pd
import plotly.express as px
import streamlit as st


@st.cache_data(ttl=60)
def get_cached_stats():
    return st.session_state.analytics_service.get_platform_stats()


@st.cache_data(ttl=300)
def get_cached_analytics():
    return st.session_state.analytics_service.get_activity_analytics()


def analytics_tab():
    st.header("Platform Analytics")

    try:
        col1, col2 = st.columns([3, 1])

        with col2:
            _display_key_metrics()

        with col1:
            _display_analytics_charts()

    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")


def _display_key_metrics():
    st.subheader("Key Metrics")
    with st.spinner("Loading metrics..."):
        stats = get_cached_stats()

    st.metric("Active Users (30d)", f"{stats.get('active_users', 0):,}")
    st.metric("Total Users", f"{stats.get('total_users', 0):,}")
    st.metric("Messages Today", f"{stats.get('messages_today', 0):,}")
    st.metric("Reports", f"{stats.get('new_reports', 0):,}")


def _display_analytics_charts():
    st.subheader("Daily Analytics Trends")
    with st.spinner("Loading chart data..."):
        activity_data = get_cached_analytics()

    if not activity_data:
        st.info("No activity data available")
        return

    df = pd.DataFrame(activity_data)
    chart_tab1, chart_tab2, chart_tab3 = st.tabs(
        ["Active Users", "New Users", "Messages"]
    )

    with chart_tab1:
        _show_active_users_chart(df)
    with chart_tab2:
        _show_new_users_chart(df)
    with chart_tab3:
        _show_messages_chart(df)


def _show_active_users_chart(df):
    if "active_users" not in df.columns:
        return

    fig = px.line(
        df, x="date", y="active_users", title="Daily Active Users (Last 90 Days)"
    )
    fig.update_traces(line_width=2, line_color="#007acc")
    fig.update_layout(height=400, xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    max_active = df["active_users"].max()
    max_date = df.loc[df["active_users"].idxmax(), "date"]
    avg_active = df["active_users"].mean()
    st.info(f"Peak: **{max_active:,}** on {max_date} | Average: **{avg_active:.0f}**")


def _show_new_users_chart(df):
    if "new_users" not in df.columns:
        return

    fig = px.bar(
        df, x="date", y="new_users", title="New User Registrations (Last 90 Days)"
    )
    fig.update_traces(marker_color="#28a745")
    fig.update_layout(height=400, xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    max_new = df["new_users"].max()
    max_date = df.loc[df["new_users"].idxmax(), "date"]
    total_new = df["new_users"].sum()
    st.info(f"Peak: **{max_new:,}** on {max_date} | Total: **{total_new:,}**")


def _show_messages_chart(df):
    if "messages" not in df.columns:
        return

    fig = px.area(
        df, x="date", y="messages", title="Daily Message Volume (Last 90 Days)"
    )
    fig.update_traces(fill="tonexty", line_color="#ffc107")
    fig.update_layout(height=400, xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    max_messages = df["messages"].max()
    max_date = df.loc[df["messages"].idxmax(), "date"]
    total_messages = df["messages"].sum()
    avg_messages = df["messages"].mean()
    st.info(
        f"Peak: **{max_messages:,}** on {max_date} | Total: **{total_messages:,}** | Avg: **{avg_messages:.0f}**"
    )
