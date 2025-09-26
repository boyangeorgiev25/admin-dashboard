from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import desc

from core.models import IndMessage, Message, User, UserReport
from core.security import AuditLogger
from services.database_service import DatabaseService
from utils.error_handler import ErrorHandler
from utils.exceptions import DatabaseError, UserNotFoundError, ValidationError

# Constants
MAX_RECENT_MESSAGES = 10
MESSAGE_CONTENT_PREVIEW_LENGTH = 10000
VALID_SEARCH_TYPES = ["user_id", "username"]


class UserService:
    def __init__(self):
        self.db_service = DatabaseService()

    def get_user(self, search_type: str, search_value: str) -> Optional[Dict]:
        self._validate_search_params(search_type, search_value)

        AuditLogger.log_action(
            "USER_SEARCH", {"search_type": search_type, "search_value": search_value}
        )

        with self.db_service.get_session() as db:
            user = self._find_user(db, search_type, search_value)
            if not user:
                raise UserNotFoundError(
                    f"No user found with {search_type.replace('_', ' ')}: '{search_value}'"
                )

            report_count = self._get_report_count(db, user.id)
            total_messages = self._get_total_message_count(db, user.id)
            recent_messages = self._get_recent_messages(db, user.id)

            return self._build_user_dict(
                user, report_count, total_messages, recent_messages
            )

    @ErrorHandler.handle_database_error
    def get_user_from_report(self, reported_user_id):
        if not reported_user_id:
            raise ValidationError("User ID is required for report lookup")

        try:
            user_id = int(reported_user_id)
        except ValueError:
            raise ValidationError(
                f"Invalid user ID '{reported_user_id}' in report: must be a valid integer"
            )

        with self.db_service.get_session() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise UserNotFoundError(str(user_id))

            report_count = self._get_report_count(db, user.id)
            total_messages = self._get_total_message_count(db, user.id)
            recent_messages = self._get_recent_messages(db, user.id)

            return self._build_user_dict(
                user, report_count, total_messages, recent_messages
            )

    def get_user_activities(self, user_id: str) -> List[Dict]:
        return []

    def _validate_search_params(self, search_type: str, search_value: str):
        """Validate search parameters"""
        if not search_type or not search_value:
            raise ValidationError("Search type and value are required")

        if search_type not in VALID_SEARCH_TYPES:
            raise ValidationError(
                f"Invalid search type '{search_type}'. Must be one of: {', '.join(VALID_SEARCH_TYPES)}"
            )

    def _find_user(self, db, search_type: str, search_value: str):
        """Find user by search type and value"""
        if search_type == "user_id":
            return self._find_user_by_id(db, search_value)
        elif search_type == "username":
            return self._find_user_by_username(db, search_value)
        return None

    def _find_user_by_id(self, db, user_id_str: str):
        """Find user by ID"""
        try:
            user_id = int(user_id_str)
        except ValueError:
            raise ValidationError(
                f"Invalid user ID '{user_id_str}': must be a valid integer"
            )
        return db.query(User).filter(User.id == user_id).first()

    def _find_user_by_username(self, db, username: str):
        """Find user by username"""
        return db.query(User).filter(User.name == username).first()

    def _get_report_count(self, db, user_id: int) -> int:
        return db.query(UserReport).filter(UserReport.reported_id == user_id).count()

    def _get_total_message_count(self, db, user_id: int) -> int:
        ind_count = db.query(IndMessage).filter(IndMessage.sender_id == user_id).count()
        reg_count = db.query(Message).filter(Message.sender_id == user_id).count()
        return ind_count + reg_count

    def _get_recent_messages(self, db, user_id: int) -> List[Dict]:
        try:
            ind_messages = (
                db.query(IndMessage)
                .filter(IndMessage.sender_id == user_id)
                .order_by(desc(IndMessage.timestamp))
                .limit(MAX_RECENT_MESSAGES)
                .all()
            )

            regular_messages = (
                db.query(Message)
                .filter(Message.sender_id == user_id)
                .order_by(desc(Message.timestamp))
                .limit(MAX_RECENT_MESSAGES)
                .all()
            )
        except Exception as e:
            return []

        all_messages = []

        try:
            for msg in ind_messages:
                all_messages.append(
                    {
                        "content": self._format_message_content(
                            getattr(msg, "content", None)
                        ),
                        "timestamp": self._format_timestamp(
                            getattr(msg, "timestamp", None)
                        ),
                        "chat_id": f"IND-{getattr(msg, 'ind_chat_id', 'unknown')}",
                        "timestamp_raw": getattr(msg, "timestamp", 0) or 0,
                    }
                )

            for msg in regular_messages:
                all_messages.append(
                    {
                        "content": self._format_message_content(
                            getattr(msg, "content", None)
                        ),
                        "timestamp": self._format_timestamp(
                            getattr(msg, "timestamp", None)
                        ),
                        "chat_id": f"MSG-{getattr(msg, 'id', 'unknown')}",
                        "timestamp_raw": getattr(msg, "timestamp", 0) or 0,
                    }
                )
        except Exception as e:
            pass

        all_messages.sort(key=lambda x: x["timestamp_raw"], reverse=True)
        messages_list = all_messages[:MAX_RECENT_MESSAGES]

        for msg in messages_list:
            del msg["timestamp_raw"]

        return messages_list

    def _format_message_content(self, content: str) -> str:
        """Format message content for display"""
        return content if content else "No content"

    def _format_timestamp(self, timestamp) -> str:
        """Format timestamp for display"""
        if timestamp:
            return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        return "Unknown"

    def _build_user_dict(
        self, user, report_count: int, message_count: int, recent_messages: List[Dict]
    ) -> Dict:
        return {
            "id": user.id,
            "username": user.name or f"User {user.id}",
            "email": user.email or "Unknown",
            "status": "active",
            "created_at": (
                user.created_at.strftime("%Y-%m-%d") if user.created_at else "Unknown"
            ),
            "last_active": (
                user.last_active.strftime("%Y-%m-%d %H:%M:%S")
                if user.last_active
                else "Unknown"
            ),
            "message_count": message_count,
            "report_count": report_count,
            "recent_messages": recent_messages,
        }
