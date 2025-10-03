import os
from datetime import datetime
from typing import Dict, List

import requests
from dotenv import load_dotenv
from sqlalchemy import func, text

from core.models import DeletedUser, Feedback, User, UserReport
from core.security import AuditLogger, audit_log, security_validator
from services.database_service import DatabaseService
from utils.error_handler import ErrorHandler
from utils.exceptions import DashboardException, DatabaseError, ValidationError

load_dotenv()


class ModerationService:
    def __init__(self, api_base_url: str = None, use_direct_db: bool = True):
        self.api_base_url = api_base_url or "http://127.0.0.1:8000"
        self.session = requests.Session()
        self.use_direct_db = use_direct_db

        if use_direct_db:
            self.db_service = DatabaseService()

    def get_db_session(self):
        return self.db_service.get_session()

    @audit_log("SEND_ADMIN_MESSAGE")
    @ErrorHandler.handle_database_error
    def send_message(self, user_id: str, subject: str, message: str,
                     action_type: str = None, action_text: str = None,
                     action_data: dict = None) -> bool:
        if not security_validator.validate_user_id(user_id):
            raise ValidationError("Invalid user ID format")
        if not security_validator.validate_message_content(message):
            raise ValidationError("Invalid message content")

        message = security_validator.sanitize_input(message)

        if self.use_direct_db:
            import time
            import json

            from core.models import IndMessage

            with self.get_db_session() as db:
                new_message = IndMessage(
                    content=message,
                    timestamp=int(time.time()),
                    sender_id=1,
                    ind_chat_id=int(user_id),
                    action_type=action_type if action_type else "direct_message",
                    action_text=action_text if action_text else "Dashboard message",
                    action_data=json.dumps(action_data) if action_data else None
                )

                AuditLogger.log_action(
                    "MESSAGE_SENT",
                    {"recipient_id": user_id, "message_length": len(message), "has_action": bool(action_type)},
                )

                db.add(new_message)
                db.commit()
                return True
        else:
            try:
                response = self.session.post(
                    f"{self.api_base_url}/api/moderation/message",
                    json={
                        "sender_id": 1,
                        "user_id": user_id,
                        "subject": subject,
                        "message": message,
                        "timestamp": datetime.now().isoformat(),
                    },
                )
                if response.status_code != 200:
                    raise DashboardException(
                        f"API request failed with status {response.status_code}"
                    )
                return True
            except requests.RequestException as e:
                raise DashboardException(f"API request failed: {str(e)}")

    @audit_log("PERMANENT_BAN_USER")
    @ErrorHandler.handle_database_error
    def permanent_ban(self, user_id: str, reason: str) -> bool:
        if not security_validator.validate_user_id(user_id):
            raise ValidationError("Invalid user ID format")
        if not reason or len(reason) > 1000:
            raise ValidationError(
                "Ban reason is required and must be under 1000 characters"
            )

        reason = security_validator.sanitize_input(reason)

        if self.use_direct_db:
            with self.get_db_session() as db:
                user = db.query(User).filter(User.id == int(user_id)).first()
                if not user:
                    raise ValidationError(f"User {user_id} not found")

                AuditLogger.log_action(
                    "USER_BANNED",
                    {
                        "banned_user_id": user.id,
                        "banned_username": user.name,
                        "ban_reason": reason[:100],
                    },
                )

                deleted_user = DeletedUser(
                    user_id=user.id,
                    name=user.name,
                    email=user.email,
                    phone=user.phone,
                    reason=reason,
                )
                db.add(deleted_user)
                db.delete(user)
                db.commit()
                return True
        else:
            try:
                response = self.session.post(
                    f"{self.api_base_url}/api/moderation/permanent_ban",
                    json={
                        "user_id": user_id,
                        "reason": reason,
                        "timestamp": datetime.now().isoformat(),
                    },
                )
                if response.status_code != 200:
                    raise DashboardException(
                        f"Ban API request failed with status {response.status_code}"
                    )
                return True
            except requests.RequestException as e:
                raise DashboardException(f"Ban API request failed: {str(e)}")

    @ErrorHandler.handle_database_error
    def get_pending_reports(self) -> List[Dict]:
        if self.use_direct_db:
            with self.get_db_session() as db:
                report_data = (
                    db.query(
                        UserReport.reported_id,
                        func.count(UserReport.id).label("report_count"),
                        User.name.label("reported_name"),
                    )
                    .outerjoin(User, UserReport.reported_id == User.id)
                    .group_by(UserReport.reported_id, User.name)
                    .having(func.count(UserReport.id) > 1)
                    .order_by(func.count(UserReport.id).desc())
                    .all()
                )

                result = []
                for reported_id, count, reported_name in report_data:
                    reporters_query = (
                        db.query(User.name)
                        .join(UserReport, UserReport.reporter_id == User.id)
                        .filter(UserReport.reported_id == reported_id)
                        .all()
                    )

                    reporter_names = [r.name for r in reporters_query if r.name]

                    result.append(
                        {
                            "id": f"rep_{reported_id}",
                            "reported_user": reported_name or f"User {reported_id}",
                            "reported_user_id": str(reported_id),
                            "description": f"User has been reported {count} times by different users",
                            "report_count": int(count),
                            "reporters": reporter_names,
                        }
                    )

                return result
        else:
            try:
                response = self.session.get(f"{self.api_base_url}/api/reports/pending")
                if response.status_code == 200:
                    return response.json()
                return []
            except requests.RequestException as e:
                raise DashboardException(f"Reports API request failed: {str(e)}")

    @ErrorHandler.handle_database_error
    def get_sent_feedback(self) -> List[Dict]:
        """Get all feedback/messages sent to users from database"""
        if self.use_direct_db:
            with self.get_db_session() as db:
                try:
                    columns_result = db.execute(text("DESCRIBE feedback"))
                    columns = [row[0] for row in columns_result.fetchall()]

                    timestamp_fields = []
                    for field in [
                        "created_at",
                        "timestamp",
                        "date_created",
                        "updated_at",
                        "created",
                    ]:
                        if field in columns:
                            timestamp_fields.append(field)

                    if timestamp_fields:
                        coalesce_clause = f"COALESCE({', '.join(timestamp_fields)}, NOW()) as feedback_date"
                    else:
                        coalesce_clause = "NOW() as feedback_date"

                    result = db.execute(
                        text(
                            f"""
                        SELECT *, {coalesce_clause}
                        FROM feedback 
                        ORDER BY 
                            CASE 
                                WHEN rating IS NULL OR rating = 0 THEN 2 
                                ELSE 1 
                            END,
                            rating ASC,
                            id DESC 
                        LIMIT 100
                    """
                        )
                    )
                except Exception as e:
                    result = db.execute(
                        text(
                            """
                        SELECT *, NOW() as feedback_date
                        FROM feedback 
                        ORDER BY 
                            CASE 
                                WHEN rating IS NULL OR rating = 0 THEN 2 
                                ELSE 1 
                            END,
                            rating ASC,
                            id DESC 
                        LIMIT 100
                    """
                        )
                    )
                rows = result.fetchall()

                feedback_list = []
                for row in rows:
                    row_dict = dict(row._mapping)
                    user_id = row_dict.get("user_id")

                    user = db.query(User).filter(User.id == user_id).first()
                    user_name = user.name if user and user.name else f"User {user_id}"

                    rating = row_dict.get("rating", 0)

                    feedback_date = row_dict.get("feedback_date")

                    feedback_list.append(
                        {
                            "id": row_dict.get("id"),
                            "user_id": user_id,
                            "user_name": user_name,
                            "message": row_dict.get("feedback", "No feedback"),
                            "rating": row_dict.get("rating", "No rating"),
                            "timestamp": feedback_date,
                            "status": "Feedback",
                            "read_status": True,
                        }
                    )

                return feedback_list
        else:
            try:
                response = self.session.get(
                    f"{self.api_base_url}/api/moderation/feedback"
                )
                if response.status_code == 200:
                    return response.json()
                return []
            except requests.RequestException as e:
                raise DashboardException(f"Feedback API request failed: {str(e)}")
