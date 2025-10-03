from datetime import datetime
from typing import Dict, List, Optional

from dotenv import load_dotenv
from sqlalchemy import desc, or_

from core.models import (
    Community,
    CommunityMembership,
    CommunityThread,
    CommunityThreadReply,
    CommunityThreadReplyUpvote,
    CommunityThreadUpvote,
    User,
)
from core.security import AuditLogger, audit_log
from services.database_service import DatabaseService
from utils.error_handler import ErrorHandler
from utils.exceptions import ValidationError

load_dotenv()


class CommunityForumService:
    def __init__(self):
        self.db_service = DatabaseService()

    def get_db_session(self):
        return self.db_service.get_session()

    @ErrorHandler.handle_database_error
    def get_forum_stats(self) -> Dict:
        with self.get_db_session() as db:
            total_communities = db.query(Community).count()
            total_threads = db.query(CommunityThread).count()
            total_replies = db.query(CommunityThreadReply).count()
            reported_threads = (
                db.query(CommunityThread)
                .filter(CommunityThread.is_reported == True)
                .count()
            )
            reported_replies = (
                db.query(CommunityThreadReply)
                .filter(CommunityThreadReply.is_reported == True)
                .count()
            )
            total_members = db.query(CommunityMembership).count()

            return {
                "total_communities": total_communities,
                "total_threads": total_threads,
                "total_replies": total_replies,
                "total_posts": total_threads + total_replies,
                "reported_threads": reported_threads,
                "reported_replies": reported_replies,
                "total_reported": reported_threads + reported_replies,
                "total_members": total_members,
            }

    @ErrorHandler.handle_database_error
    def get_threads(
        self,
        limit: int = 50,
        offset: int = 0,
        community_id: Optional[int] = None,
        search: Optional[str] = None,
        reported_only: bool = False,
    ) -> List[Dict]:
        with self.get_db_session() as db:
            query = db.query(CommunityThread)

            if community_id:
                query = query.filter(CommunityThread.community_id == community_id)

            if reported_only:
                query = query.filter(CommunityThread.is_reported == True)

            if search:
                query = query.filter(
                    or_(
                        CommunityThread.title.ilike(f"%{search}%"),
                        CommunityThread.body.ilike(f"%{search}%"),
                    )
                )

            threads = (
                query.order_by(desc(CommunityThread.last_updated))
                .limit(limit)
                .offset(offset)
                .all()
            )

            result = []
            for thread in threads:
                owner = db.query(User).filter(User.id == thread.owner_id).first()
                community = (
                    db.query(Community)
                    .filter(Community.id == thread.community_id)
                    .first()
                )

                reply_count = (
                    db.query(CommunityThreadReply)
                    .filter(CommunityThreadReply.thread_id == thread.id)
                    .count()
                )

                upvote_count = (
                    db.query(CommunityThreadUpvote)
                    .filter(CommunityThreadUpvote.thread_id == thread.id)
                    .count()
                )

                result.append(
                    {
                        "id": thread.id,
                        "title": thread.title,
                        "body": thread.body[:200] + "..."
                        if len(thread.body) > 200
                        else thread.body,
                        "body_full": thread.body,
                        "community_id": thread.community_id,
                        "community_name": community.name if community else "Unknown",
                        "owner_id": thread.owner_id,
                        "owner_name": owner.name if owner else "Unknown",
                        "created_at": thread.created_at,
                        "last_updated": thread.last_updated,
                        "is_reported": thread.is_reported,
                        "reply_count": reply_count,
                        "upvote_count": upvote_count,
                    }
                )

            return result

    @ErrorHandler.handle_database_error
    def get_thread_replies(self, thread_id: int) -> List[Dict]:
        with self.get_db_session() as db:
            replies = (
                db.query(CommunityThreadReply)
                .filter(CommunityThreadReply.thread_id == thread_id)
                .order_by(CommunityThreadReply.created_at.asc())
                .all()
            )

            result = []
            for reply in replies:
                owner = db.query(User).filter(User.id == reply.owner_id).first()

                upvote_count = (
                    db.query(CommunityThreadReplyUpvote)
                    .filter(CommunityThreadReplyUpvote.reply_id == reply.id)
                    .count()
                )

                parent_author = None
                if reply.parent_id:
                    parent_reply = (
                        db.query(CommunityThreadReply)
                        .filter(CommunityThreadReply.id == reply.parent_id)
                        .first()
                    )
                    if parent_reply and parent_reply.owner_id:
                        parent_user = (
                            db.query(User)
                            .filter(User.id == parent_reply.owner_id)
                            .first()
                        )
                        parent_author = parent_user.name if parent_user else "Unknown"

                result.append(
                    {
                        "id": reply.id,
                        "body": reply.body,
                        "owner_id": reply.owner_id,
                        "owner_name": owner.name if owner else "Unknown",
                        "created_at": reply.created_at,
                        "parent_id": reply.parent_id,
                        "parent_author": parent_author,
                        "is_reported": reply.is_reported,
                        "upvote_count": upvote_count,
                    }
                )

            return result

    @ErrorHandler.handle_database_error
    def get_reported_content(self) -> Dict:
        with self.get_db_session() as db:
            reported_threads = (
                db.query(CommunityThread)
                .filter(CommunityThread.is_reported == True)
                .order_by(desc(CommunityThread.last_updated))
                .all()
            )

            reported_replies = (
                db.query(CommunityThreadReply)
                .filter(CommunityThreadReply.is_reported == True)
                .order_by(desc(CommunityThreadReply.created_at))
                .all()
            )

            threads = []
            for thread in reported_threads:
                owner = db.query(User).filter(User.id == thread.owner_id).first()
                community = (
                    db.query(Community)
                    .filter(Community.id == thread.community_id)
                    .first()
                )

                threads.append(
                    {
                        "type": "thread",
                        "id": thread.id,
                        "title": thread.title,
                        "body": thread.body[:200] + "..."
                        if len(thread.body) > 200
                        else thread.body,
                        "community_name": community.name if community else "Unknown",
                        "owner_name": owner.name if owner else "Unknown",
                        "created_at": thread.created_at,
                    }
                )

            replies = []
            for reply in reported_replies:
                owner = db.query(User).filter(User.id == reply.owner_id).first()
                thread = (
                    db.query(CommunityThread)
                    .filter(CommunityThread.id == reply.thread_id)
                    .first()
                )

                replies.append(
                    {
                        "type": "reply",
                        "id": reply.id,
                        "body": reply.body,
                        "thread_title": thread.title if thread else "Unknown",
                        "owner_name": owner.name if owner else "Unknown",
                        "created_at": reply.created_at,
                    }
                )

            return {"threads": threads, "replies": replies}

    @ErrorHandler.handle_database_error
    def search_forum_content(self, keyword: str, limit: int = 50) -> List[Dict]:
        if not keyword or len(keyword) < 2:
            raise ValidationError("Search keyword must be at least 2 characters")

        with self.get_db_session() as db:
            threads = (
                db.query(CommunityThread)
                .filter(
                    or_(
                        CommunityThread.title.ilike(f"%{keyword}%"),
                        CommunityThread.body.ilike(f"%{keyword}%"),
                    )
                )
                .order_by(desc(CommunityThread.last_updated))
                .limit(limit // 2)
                .all()
            )

            replies = (
                db.query(CommunityThreadReply)
                .filter(CommunityThreadReply.body.ilike(f"%{keyword}%"))
                .order_by(desc(CommunityThreadReply.created_at))
                .limit(limit // 2)
                .all()
            )

            result = []

            for thread in threads:
                owner = db.query(User).filter(User.id == thread.owner_id).first()
                community = (
                    db.query(Community)
                    .filter(Community.id == thread.community_id)
                    .first()
                )

                result.append(
                    {
                        "type": "thread",
                        "id": thread.id,
                        "title": thread.title,
                        "body": thread.body,
                        "community_name": community.name if community else "Unknown",
                        "owner_name": owner.name if owner else "Unknown",
                        "created_at": thread.created_at,
                        "is_reported": thread.is_reported,
                    }
                )

            for reply in replies:
                owner = db.query(User).filter(User.id == reply.owner_id).first()
                thread = (
                    db.query(CommunityThread)
                    .filter(CommunityThread.id == reply.thread_id)
                    .first()
                )

                result.append(
                    {
                        "type": "reply",
                        "id": reply.id,
                        "body": reply.body,
                        "thread_title": thread.title if thread else "Unknown",
                        "owner_name": owner.name if owner else "Unknown",
                        "created_at": reply.created_at,
                        "is_reported": reply.is_reported,
                    }
                )

            result.sort(key=lambda x: x["created_at"] or datetime.min, reverse=True)
            return result[:limit]

    @audit_log("DELETE_THREAD")
    @ErrorHandler.handle_database_error
    def delete_thread(self, thread_id: int, reason: str) -> bool:
        if not reason or len(reason) < 5:
            raise ValidationError("Deletion reason must be at least 5 characters")

        with self.get_db_session() as db:
            thread = (
                db.query(CommunityThread)
                .filter(CommunityThread.id == thread_id)
                .first()
            )

            if not thread:
                raise ValidationError(f"Thread {thread_id} not found")

            thread_title = thread.title

            db.query(CommunityThreadReplyUpvote).filter(
                CommunityThreadReplyUpvote.reply_id.in_(
                    db.query(CommunityThreadReply.id).filter(
                        CommunityThreadReply.thread_id == thread_id
                    )
                )
            ).delete(synchronize_session=False)

            db.query(CommunityThreadReply).filter(
                CommunityThreadReply.thread_id == thread_id
            ).delete()

            db.query(CommunityThreadUpvote).filter(
                CommunityThreadUpvote.thread_id == thread_id
            ).delete()

            db.delete(thread)
            db.commit()

            AuditLogger.log_action(
                "THREAD_DELETED",
                {"thread_id": thread_id, "title": thread_title, "reason": reason[:100]},
            )

            return True

    @audit_log("DELETE_REPLY")
    @ErrorHandler.handle_database_error
    def delete_reply(self, reply_id: int, reason: str) -> bool:
        if not reason or len(reason) < 5:
            raise ValidationError("Deletion reason must be at least 5 characters")

        with self.get_db_session() as db:
            reply = (
                db.query(CommunityThreadReply)
                .filter(CommunityThreadReply.id == reply_id)
                .first()
            )

            if not reply:
                raise ValidationError(f"Reply {reply_id} not found")

            db.query(CommunityThreadReplyUpvote).filter(
                CommunityThreadReplyUpvote.reply_id == reply_id
            ).delete()

            db.delete(reply)
            db.commit()

            AuditLogger.log_action(
                "REPLY_DELETED", {"reply_id": reply_id, "reason": reason[:100]}
            )

            return True

    @ErrorHandler.handle_database_error
    def get_community_members(self, community_id: int) -> List[Dict]:
        with self.get_db_session() as db:
            memberships = (
                db.query(CommunityMembership)
                .filter(CommunityMembership.community_id == community_id)
                .all()
            )

            result = []
            for membership in memberships:
                user = db.query(User).filter(User.id == membership.user_id).first()
                if user:
                    result.append(
                        {
                            "user_id": user.id,
                            "username": user.name,
                            "email": user.email,
                            "last_visited": membership.last_visited,
                        }
                    )

            return result

    @ErrorHandler.handle_database_error
    def get_user_activity_in_communities(self, user_id: int) -> Dict:
        with self.get_db_session() as db:
            threads = (
                db.query(CommunityThread)
                .filter(CommunityThread.owner_id == user_id)
                .all()
            )

            replies = (
                db.query(CommunityThreadReply)
                .filter(CommunityThreadReply.owner_id == user_id)
                .all()
            )

            return {
                "total_threads": len(threads),
                "total_replies": len(replies),
                "threads": [
                    {"id": t.id, "title": t.title, "created_at": t.created_at}
                    for t in threads[:10]
                ],
                "replies": [
                    {"id": r.id, "body": r.body[:100], "created_at": r.created_at}
                    for r in replies[:10]
                ],
            }
