from typing import Dict, List

from dotenv import load_dotenv
from sqlalchemy import desc

from core.models import Community
from core.security import AuditLogger, audit_log
from services.database_service import DatabaseService
from utils.error_handler import ErrorHandler
from utils.exceptions import ValidationError

load_dotenv()


class CommunityService:
    def __init__(self):
        self.db_service = DatabaseService()

    def get_db_session(self):
        return self.db_service.get_session()

    @ErrorHandler.handle_database_error
    def get_all_communities(self) -> List[Dict]:
        with self.get_db_session() as db:
            communities = db.query(Community).order_by(desc(Community.id)).all()

            return [
                {
                    "id": c.id,
                    "name": c.name,
                    "description": c.description,
                    "img_url": c.img_url,
                    "location": c.location,
                    "is_starter": c.is_starter
                }
                for c in communities
            ]

    @audit_log("ADD_COMMUNITY")
    @ErrorHandler.handle_database_error
    def add_community(self, name: str, description: str, img_url: str,
                      location: str, is_starter: bool) -> bool:
        if not name or not description or not location:
            raise ValidationError("Name, description, and location are required")

        with self.get_db_session() as db:
            from sqlalchemy import text

            result = db.execute(
                text("""
                    INSERT INTO communities (name, description, img_url, location, is_starter)
                    VALUES (:name, :description, :img_url, ST_GeomFromText(:location, 4326), :is_starter)
                """),
                {
                    "name": name,
                    "description": description,
                    "img_url": img_url,
                    "location": location,
                    "is_starter": is_starter
                }
            )
            db.commit()

            AuditLogger.log_action(
                "COMMUNITY_ADDED",
                {"name": name, "is_starter": is_starter}
            )

            return True

    @audit_log("UPDATE_COMMUNITY")
    @ErrorHandler.handle_database_error
    def update_community(self, community_id: int, name: str, description: str,
                         img_url: str, location: str, is_starter: bool) -> bool:
        if not name or not description or not location:
            raise ValidationError("Name, description, and location are required")

        with self.get_db_session() as db:
            community = db.query(Community).filter(Community.id == community_id).first()

            if not community:
                raise ValidationError(f"Community {community_id} not found")

            community.name = name
            community.description = description
            community.img_url = img_url
            community.location = location
            community.is_starter = is_starter

            db.commit()

            AuditLogger.log_action(
                "COMMUNITY_UPDATED",
                {"community_id": community_id, "name": name}
            )

            return True

    @audit_log("DELETE_COMMUNITY")
    @ErrorHandler.handle_database_error
    def delete_community(self, community_id: int) -> bool:
        with self.get_db_session() as db:
            from sqlalchemy import text

            community = db.query(Community).filter(Community.id == community_id).first()

            if not community:
                raise ValidationError(f"Community {community_id} not found")

            community_name = community.name

            db.execute(text("DELETE FROM community_membership WHERE community_id = :community_id"), {"community_id": community_id})

            db.delete(community)
            db.commit()

            AuditLogger.log_action(
                "COMMUNITY_DELETED",
                {"community_id": community_id, "name": community_name}
            )

            return True
