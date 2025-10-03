from datetime import datetime
from typing import Dict, List, Optional

from dotenv import load_dotenv
from sqlalchemy import desc, or_

from core.models import (
    Activity,
    ChatMeta,
    ChatUserActivity,
    IndChats,
    IndChatMembers,
    IndMessage,
    Message,
    User,
)
from core.security import AuditLogger, audit_log
from services.database_service import DatabaseService
from utils.error_handler import ErrorHandler
from utils.exceptions import ValidationError

load_dotenv()


class ChatModerationService:
    def __init__(self):
        self.db_service = DatabaseService()

    def get_db_session(self):
        return self.db_service.get_session()

    def get_activity_chats(
        self, limit: int = 50, offset: int = 0, search: str = None
    ) -> List[Dict]:
        import streamlit as st

        cache_key = f"activity_chats_{limit}_{offset}_{search or 'all'}"
        cache_time_key = f"{cache_key}_time"

        if cache_key in st.session_state:
            cached_time = st.session_state.get(cache_time_key, 0)
            if (datetime.now().timestamp() - cached_time) < 300:
                return st.session_state[cache_key]

        try:
            with self.get_db_session() as db:
                query = db.query(ChatMeta).options()

                if search:
                    query = query.filter(
                        or_(
                            ChatMeta.activity_name.ilike(f"%{search}%"),
                            ChatMeta.last_message.ilike(f"%{search}%"),
                            ChatMeta.last_sender_name.ilike(f"%{search}%"),
                        )
                    )

                chats = (
                    query.order_by(desc(ChatMeta.last_timestamp))
                    .limit(limit)
                    .offset(offset)
                    .all()
                )

                result = []
                for chat in chats:
                    activity = None
                    if chat.activity_id:
                        activity = (
                            db.query(Activity)
                            .filter(Activity.id == chat.activity_id)
                            .first()
                        )

                    member_count = (
                        db.query(ChatUserActivity)
                        .filter(ChatUserActivity.chat_id == chat.id, ChatUserActivity.active == True)
                        .count()
                    )

                    message_count = (
                        db.query(Message).filter(Message.chat_id == chat.id).count()
                    )

                    result.append(
                        {
                            "id": chat.id,
                            "activity_id": chat.activity_id,
                            "activity_name": chat.activity_name,
                            "activity_city": activity.city if activity else None,
                            "last_sender_name": chat.last_sender_name,
                            "last_message": (
                                chat.last_message[:100] + "..."
                                if chat.last_message and len(chat.last_message) > 100
                                else chat.last_message
                            ),
                            "last_timestamp": datetime.fromtimestamp(chat.last_timestamp)
                            if chat.last_timestamp
                            else None,
                            "member_count": member_count,
                            "message_count": message_count,
                        }
                    )

                st.session_state[cache_key] = result
                st.session_state[cache_time_key] = datetime.now().timestamp()
                return result
        except Exception:
            if cache_key in st.session_state:
                return st.session_state[cache_key]
            return []

    @ErrorHandler.handle_database_error
    def get_individual_chats(
        self, limit: int = 50, offset: int = 0, search: str = None
    ) -> List[Dict]:
        with self.get_db_session() as db:
            query = db.query(IndChats)

            if search:
                query = query.filter(
                    or_(
                        IndChats.activity_name.ilike(f"%{search}%"),
                        IndChats.last_message.ilike(f"%{search}%"),
                        IndChats.last_sender_name.ilike(f"%{search}%"),
                    )
                )

            chats = (
                query.order_by(desc(IndChats.last_timestamp))
                .limit(limit)
                .offset(offset)
                .all()
            )

            result = []
            for chat in chats:
                owner = (
                    db.query(User)
                    .filter(User.id == chat.activity_owner_id)
                    .first()
                )
                receiver = (
                    db.query(User).filter(User.id == chat.receiver_id).first()
                )

                message_count = (
                    db.query(IndMessage)
                    .filter(IndMessage.ind_chat_id == chat.id)
                    .count()
                )

                result.append(
                    {
                        "id": chat.id,
                        "activity_name": chat.activity_name,
                        "owner_id": chat.activity_owner_id,
                        "owner_name": owner.name if owner else "Unknown",
                        "receiver_id": chat.receiver_id,
                        "receiver_name": receiver.name if receiver else "Unknown",
                        "last_sender_name": chat.last_sender_name,
                        "last_message": (
                            chat.last_message[:100] + "..."
                            if chat.last_message and len(chat.last_message) > 100
                            else chat.last_message
                        ),
                        "last_timestamp": datetime.fromtimestamp(chat.last_timestamp)
                        if chat.last_timestamp
                        else None,
                        "message_count": message_count,
                    }
                )

            return result

    @ErrorHandler.handle_database_error
    def get_chat_messages(self, chat_id: int, chat_type: str = "activity") -> List[Dict]:
        with self.get_db_session() as db:
            if chat_type == "activity":
                messages = (
                    db.query(Message)
                    .filter(Message.chat_id == chat_id)
                    .order_by(Message.timestamp.asc())
                    .all()
                )

                result = []
                for msg in messages:
                    user = db.query(User).filter(User.id == msg.sender_id).first()
                    result.append(
                        {
                            "id": msg.id,
                            "sender_id": msg.sender_id,
                            "sender_name": user.name if user else "Unknown",
                            "content": msg.content,
                            "timestamp": datetime.fromtimestamp(msg.timestamp)
                            if msg.timestamp
                            else None,
                            "is_deleted": msg.is_deleted,
                            "is_edited": msg.is_edited,
                            "action_type": msg.action_type,
                        }
                    )
                return result

            else:
                messages = (
                    db.query(IndMessage)
                    .filter(IndMessage.ind_chat_id == chat_id)
                    .order_by(IndMessage.timestamp.asc())
                    .all()
                )

                result = []
                for msg in messages:
                    user = db.query(User).filter(User.id == msg.sender_id).first()
                    result.append(
                        {
                            "id": msg.id,
                            "sender_id": msg.sender_id,
                            "sender_name": user.name if user else "Unknown",
                            "content": msg.content,
                            "timestamp": datetime.fromtimestamp(msg.timestamp)
                            if msg.timestamp
                            else None,
                            "action_type": msg.action_type,
                            "image_url": msg.image_url,
                        }
                    )
                return result

    @ErrorHandler.handle_database_error
    def search_messages(self, keyword: str, limit: int = 100) -> List[Dict]:
        if not keyword or len(keyword) < 2:
            raise ValidationError("Search keyword must be at least 2 characters")

        with self.get_db_session() as db:
            activity_messages = (
                db.query(Message)
                .filter(Message.content.ilike(f"%{keyword}%"))
                .order_by(desc(Message.timestamp))
                .limit(limit // 2)
                .all()
            )

            ind_messages = (
                db.query(IndMessage)
                .filter(IndMessage.content.ilike(f"%{keyword}%"))
                .order_by(desc(IndMessage.timestamp))
                .limit(limit // 2)
                .all()
            )

            result = []

            for msg in activity_messages:
                user = db.query(User).filter(User.id == msg.sender_id).first()
                chat = db.query(ChatMeta).filter(ChatMeta.id == msg.chat_id).first()

                result.append(
                    {
                        "type": "activity",
                        "message_id": msg.id,
                        "chat_id": msg.chat_id,
                        "chat_name": chat.activity_name if chat else "Unknown",
                        "sender_id": msg.sender_id,
                        "sender_name": user.name if user else "Unknown",
                        "content": msg.content,
                        "timestamp": datetime.fromtimestamp(msg.timestamp)
                        if msg.timestamp
                        else None,
                    }
                )

            for msg in ind_messages:
                user = db.query(User).filter(User.id == msg.sender_id).first()
                chat = (
                    db.query(IndChats)
                    .filter(IndChats.id == msg.ind_chat_id)
                    .first()
                )

                result.append(
                    {
                        "type": "individual",
                        "message_id": msg.id,
                        "chat_id": msg.ind_chat_id,
                        "chat_name": chat.activity_name if chat else "Direct Message",
                        "sender_id": msg.sender_id,
                        "sender_name": user.name if user else "Unknown",
                        "content": msg.content,
                        "timestamp": datetime.fromtimestamp(msg.timestamp)
                        if msg.timestamp
                        else None,
                    }
                )

            result.sort(key=lambda x: x["timestamp"] or datetime.min, reverse=True)
            return result[:limit]

    @audit_log("FLAG_MESSAGE")
    @ErrorHandler.handle_database_error
    def flag_message(
        self, message_id: int, chat_type: str, reason: str
    ) -> bool:
        if not reason or len(reason) < 5:
            raise ValidationError("Flag reason must be at least 5 characters")

        with self.get_db_session() as db:
            if chat_type == "activity":
                message = (
                    db.query(Message).filter(Message.id == message_id).first()
                )
                if message:
                    message.is_deleted = True
                    db.commit()
            else:
                pass

            AuditLogger.log_action(
                "MESSAGE_FLAGGED",
                {
                    "message_id": message_id,
                    "chat_type": chat_type,
                    "reason": reason[:100],
                },
            )

            return True

    def get_chat_stats(self) -> Dict:
        import streamlit as st

        cache_key = "chat_stats_cache"
        cache_time_key = "chat_stats_cache_time"

        if cache_key in st.session_state:
            cached_time = st.session_state.get(cache_time_key, 0)
            if (datetime.now().timestamp() - cached_time) < 300:
                return st.session_state[cache_key]

        try:
            with self.get_db_session() as db:
                total_activity_chats = db.query(ChatMeta).count()
                total_individual_chats = db.query(IndChats).count()
                total_messages = db.query(Message).count()
                total_ind_messages = db.query(IndMessage).count()

                stats = {
                    "total_activity_chats": total_activity_chats,
                    "total_individual_chats": total_individual_chats,
                    "total_activity_messages": total_messages,
                    "total_individual_messages": total_ind_messages,
                    "total_chats": total_activity_chats + total_individual_chats,
                    "total_messages": total_messages + total_ind_messages,
                }

                st.session_state[cache_key] = stats
                st.session_state[cache_time_key] = datetime.now().timestamp()
                return stats
        except Exception as e:
            if cache_key in st.session_state:
                return st.session_state[cache_key]

            return {
                "total_activity_chats": 0,
                "total_individual_chats": 0,
                "total_activity_messages": 0,
                "total_individual_messages": 0,
                "total_chats": 0,
                "total_messages": 0,
            }
