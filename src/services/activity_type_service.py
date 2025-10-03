from typing import Dict, List

from dotenv import load_dotenv

from core.models import ActivityType
from core.security import AuditLogger, audit_log
from services.database_service import DatabaseService
from utils.error_handler import ErrorHandler
from utils.exceptions import ValidationError

load_dotenv()


class ActivityTypeService:
    def __init__(self):
        self.db_service = DatabaseService()

    def get_db_session(self):
        return self.db_service.get_session()

    @ErrorHandler.handle_database_error
    def get_all_activity_types(self) -> List[Dict]:
        with self.get_db_session() as db:
            types = db.query(ActivityType).order_by(ActivityType.type, ActivityType.subtype).all()

            return [
                {
                    "id": t.id,
                    "type": t.type,
                    "subtype": t.subtype,
                    "subtype_nl": t.subtype_nl,
                    "subtype_fr": t.subtype_fr,
                    "subtype_code": t.subtype_code,
                    "img_url": t.img_url,
                    "emoji": t.emoji
                }
                for t in types
            ]

    @audit_log("ADD_ACTIVITY_TYPE")
    @ErrorHandler.handle_database_error
    def add_activity_type(self, type_name: str, subtype: str, subtype_nl: str,
                          subtype_fr: str, subtype_code: int, img_url: str, emoji: str) -> bool:
        if not type_name or not subtype or not subtype_nl or not subtype_fr:
            raise ValidationError("Type, subtype (EN, NL, FR) are required")

        if not emoji:
            raise ValidationError("Emoji is required")

        with self.get_db_session() as db:
            existing = db.query(ActivityType).filter(
                (ActivityType.subtype == subtype) |
                (ActivityType.subtype_nl == subtype_nl) |
                (ActivityType.subtype_fr == subtype_fr) |
                (ActivityType.subtype_code == subtype_code)
            ).first()

            if existing:
                raise ValidationError("Activity type with this name or code already exists")

            new_type = ActivityType(
                type=type_name,
                subtype=subtype,
                subtype_nl=subtype_nl,
                subtype_fr=subtype_fr,
                subtype_code=subtype_code,
                img_url=img_url,
                emoji=emoji
            )

            db.add(new_type)
            db.commit()

            AuditLogger.log_action(
                "ACTIVITY_TYPE_ADDED",
                {"type": type_name, "subtype": subtype, "code": subtype_code}
            )

            return True

    @audit_log("UPDATE_ACTIVITY_TYPE")
    @ErrorHandler.handle_database_error
    def update_activity_type(self, type_id: int, type_name: str, subtype: str,
                             subtype_nl: str, subtype_fr: str, subtype_code: int,
                             img_url: str, emoji: str) -> bool:
        if not type_name or not subtype or not subtype_nl or not subtype_fr:
            raise ValidationError("Type, subtype (EN, NL, FR) are required")

        with self.get_db_session() as db:
            activity_type = db.query(ActivityType).filter(ActivityType.id == type_id).first()

            if not activity_type:
                raise ValidationError(f"Activity type {type_id} not found")

            activity_type.type = type_name
            activity_type.subtype = subtype
            activity_type.subtype_nl = subtype_nl
            activity_type.subtype_fr = subtype_fr
            activity_type.subtype_code = subtype_code
            activity_type.img_url = img_url
            activity_type.emoji = emoji

            db.commit()

            AuditLogger.log_action(
                "ACTIVITY_TYPE_UPDATED",
                {"type_id": type_id, "type": type_name, "subtype": subtype}
            )

            return True

    @audit_log("DELETE_ACTIVITY_TYPE")
    @ErrorHandler.handle_database_error
    def delete_activity_type(self, type_id: int) -> bool:
        with self.get_db_session() as db:
            activity_type = db.query(ActivityType).filter(ActivityType.id == type_id).first()

            if not activity_type:
                raise ValidationError(f"Activity type {type_id} not found")

            type_name = activity_type.subtype
            db.delete(activity_type)
            db.commit()

            AuditLogger.log_action(
                "ACTIVITY_TYPE_DELETED",
                {"type_id": type_id, "subtype": type_name}
            )

            return True
