from typing import Dict, List, Optional

from dotenv import load_dotenv
from sqlalchemy import desc

from core.models import ActivityType, Place
from core.security import AuditLogger, audit_log
from services.database_service import DatabaseService
from utils.error_handler import ErrorHandler
from utils.exceptions import ValidationError

load_dotenv()


class VenueService:
    def __init__(self):
        self.db_service = DatabaseService()

    def get_db_session(self):
        return self.db_service.get_session()

    @ErrorHandler.handle_database_error
    def get_all_venues(self) -> List[Dict]:
        with self.get_db_session() as db:
            venues = db.query(Place).order_by(desc(Place.id)).all()

            result = []
            for venue in venues:
                activity_type = db.query(ActivityType).filter(ActivityType.id == venue.subtype_id).first()

                result.append({
                    "id": venue.id,
                    "name": venue.name,
                    "subtype_id": venue.subtype_id,
                    "subtype_name": activity_type.subtype if activity_type else "Unknown",
                    "keywords": venue.keywords,
                    "address": venue.address,
                    "img_url": venue.img_url,
                    "url": venue.url,
                    "location": venue.location
                })

            return result

    @ErrorHandler.handle_database_error
    def get_activity_types(self) -> List[Dict]:
        with self.get_db_session() as db:
            types = db.query(ActivityType).order_by(ActivityType.subtype).all()

            return [
                {
                    "id": t.id,
                    "type": t.type,
                    "subtype": t.subtype,
                    "emoji": t.emoji
                }
                for t in types
            ]

    @audit_log("ADD_VENUE")
    @ErrorHandler.handle_database_error
    def add_venue(self, name: str, subtype_id: int, keywords: str, address: str,
                  img_url: str, url: str, location: str) -> bool:
        if not name or not address or not location:
            raise ValidationError("Name, address, and location are required")

        with self.get_db_session() as db:
            new_venue = Place(
                name=name,
                subtype_id=subtype_id,
                keywords=keywords,
                address=address,
                img_url=img_url,
                url=url,
                location=location
            )

            db.add(new_venue)
            db.commit()

            AuditLogger.log_action(
                "VENUE_ADDED",
                {"venue_name": name, "address": address}
            )

            return True

    @audit_log("UPDATE_VENUE")
    @ErrorHandler.handle_database_error
    def update_venue(self, venue_id: int, name: str, subtype_id: int, keywords: str,
                     address: str, img_url: str, url: str, location: str) -> bool:
        if not name or not address or not location:
            raise ValidationError("Name, address, and location are required")

        with self.get_db_session() as db:
            venue = db.query(Place).filter(Place.id == venue_id).first()

            if not venue:
                raise ValidationError(f"Venue {venue_id} not found")

            venue.name = name
            venue.subtype_id = subtype_id
            venue.keywords = keywords
            venue.address = address
            venue.img_url = img_url
            venue.url = url
            venue.location = location

            db.commit()

            AuditLogger.log_action(
                "VENUE_UPDATED",
                {"venue_id": venue_id, "venue_name": name}
            )

            return True

    @audit_log("DELETE_VENUE")
    @ErrorHandler.handle_database_error
    def delete_venue(self, venue_id: int) -> bool:
        with self.get_db_session() as db:
            venue = db.query(Place).filter(Place.id == venue_id).first()

            if not venue:
                raise ValidationError(f"Venue {venue_id} not found")

            venue_name = venue.name
            db.delete(venue)
            db.commit()

            AuditLogger.log_action(
                "VENUE_DELETED",
                {"venue_id": venue_id, "venue_name": venue_name}
            )

            return True
