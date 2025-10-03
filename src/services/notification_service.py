import json
from typing import Dict, List

import requests
from dotenv import load_dotenv

from core.models import User
from core.security import AuditLogger, audit_log
from services.database_service import DatabaseService
from utils.error_handler import ErrorHandler
from utils.exceptions import ValidationError

load_dotenv()


class NotificationService:
    def __init__(self):
        self.db_service = DatabaseService()

    def get_db_session(self):
        return self.db_service.get_session()

    @ErrorHandler.handle_database_error
    def get_recipient_count(self, filters: Dict) -> int:
        with self.get_db_session() as db:
            query = db.query(User).filter(User.notif_token.isnot(None), User.notif_token != '')

            query = self._apply_filters(query, filters)

            return query.count()

    @audit_log("SEND_BULK_NOTIFICATION")
    @ErrorHandler.handle_database_error
    def send_bulk_notification(self, title: str, body: str, data: Dict, filters: Dict) -> Dict:
        if not title or not body:
            raise ValidationError("Title and body are required")

        with self.get_db_session() as db:
            query = db.query(User).filter(User.notif_token.isnot(None), User.notif_token != '')

            query = self._apply_filters(query, filters)

            if 'limit' in filters and filters['limit']:
                query = query.limit(filters['limit'])

            users = query.all()

            sent = 0
            failed = 0

            for user in users:
                try:
                    if user.notif_token and user.notif_token != '':
                        success = self._send_push_notification(
                            user.notif_token, title, body, data
                        )
                        if success:
                            sent += 1
                        else:
                            failed += 1
                except Exception as e:
                    failed += 1

            AuditLogger.log_action(
                "BULK_NOTIFICATION_SENT",
                {
                    "title": title[:50],
                    "recipients": sent,
                    "failed": failed,
                    "filters": filters
                }
            )

            return {"sent": sent, "failed": failed}

    def _apply_filters(self, query, filters: Dict):
        if filters.get('language'):
            query = query.filter(User.language.in_(filters['language']))

        if filters.get('reg_complete'):
            query = query.filter(User.reg_complete == True)

        if filters.get('min_user_id'):
            query = query.filter(User.id >= filters['min_user_id'])

        if filters.get('max_user_id'):
            query = query.filter(User.id <= filters['max_user_id'])

        return query.order_by(User.id.asc())

    def _send_push_notification(self, token: str, title: str, body: str, data: Dict) -> bool:
        try:
            notification = {
                "to": token,
                "sound": "default",
                "title": title,
                "body": body,
                "data": data,
                "collapse_id": "admin-notification",
                "channelId": "default",
                "priority": "default",
                "android": {
                    "collapseKey": "admin-notification",
                    "category": "CATEGORY_MESSAGE"
                }
            }

            response = requests.post(
                "https://exp.host/--/api/v2/push/send",
                headers={
                    "Accept": "application/json",
                    "Accept-encoding": "gzip, deflate",
                    "Content-Type": "application/json"
                },
                data=json.dumps(notification),
                timeout=10
            )

            return response.status_code == 200
        except Exception:
            return False
