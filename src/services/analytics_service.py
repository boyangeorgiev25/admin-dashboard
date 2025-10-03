"""Analytics and statistics service"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List

from sqlalchemy import and_, func

from core.models import IndMessage, Message, User, UserReport
from services.database_service import DatabaseService
from utils.error_handler import ErrorHandler
from utils.exceptions import DatabaseError


class AnalyticsService:
    """Handles platform analytics and statistics"""

    def __init__(self):
        self.db_service = DatabaseService()

    @st.cache_data(ttl=300)
    @ErrorHandler.handle_database_error
    def get_platform_stats(_self) -> Dict:
        """Get basic platform statistics - cached for 5 minutes"""
        with _self.db_service.get_session() as db:
            total_users = db.query(User).count()
            active_users = (
                db.query(User)
                .filter(User.last_active >= datetime.now() - timedelta(days=30))
                .count()
            )

            today_start = int(
                datetime.now()
                .replace(hour=0, minute=0, second=0, microsecond=0)
                .timestamp()
            )
            messages_today = (
                db.query(Message).filter(Message.timestamp >= today_start).count()
            )
            messages_today += (
                db.query(IndMessage).filter(IndMessage.timestamp >= today_start).count()
            )

            new_reports = db.query(UserReport).count()

            return {
                "total_users": total_users,
                "active_users": active_users,
                "messages_today": messages_today,
                "new_reports": new_reports,
            }

    @ErrorHandler.handle_database_error
    def get_activity_analytics(self) -> List[Dict]:
        """Get real activity analytics data from database"""
        with self.db_service.get_session() as db:
            result = []

            for i in range(90):
                date = datetime.now() - timedelta(days=89 - i)
                day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
                day_end = day_start + timedelta(days=1)

                day_start_ts = int(day_start.timestamp())
                day_end_ts = int(day_end.timestamp())

                active_users = (
                    db.query(User)
                    .filter(
                        and_(User.last_active >= day_start, User.last_active < day_end)
                    )
                    .count()
                )

                new_users = (
                    db.query(User)
                    .filter(
                        and_(User.created_at >= day_start, User.created_at < day_end)
                    )
                    .count()
                )

                messages_count = (
                    db.query(Message)
                    .filter(
                        and_(
                            Message.timestamp >= day_start_ts,
                            Message.timestamp < day_end_ts,
                        )
                    )
                    .count()
                )
                messages_count += (
                    db.query(IndMessage)
                    .filter(
                        and_(
                            IndMessage.timestamp >= day_start_ts,
                            IndMessage.timestamp < day_end_ts,
                        )
                    )
                    .count()
                )

                result.append(
                    {
                        "date": date.strftime("%Y-%m-%d"),
                        "active_users": active_users,
                        "new_users": new_users,
                        "messages": messages_count,
                        "day_name": date.strftime("%A"),
                    }
                )

            return result
