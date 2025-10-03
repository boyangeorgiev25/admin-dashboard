import os
from typing import Dict, List

import requests
from dotenv import load_dotenv

from core.security import AuditLogger, audit_log
from utils.error_handler import ErrorHandler
from utils.exceptions import ValidationError

load_dotenv()


class ConvertKitService:
    def __init__(self):
        self.api_key = os.getenv("CONVERTKIT_API_KEY", "")
        self.api_secret = os.getenv("CONVERTKIT_API_SECRET", "")
        self.sequence_id = os.getenv("CONVERTKIT_SEQUENCE_ID", "")

    @ErrorHandler.handle_database_error
    def add_subscriber(self, email: str, first_name: str = "Added from dashboard", language: str = None) -> bool:
        if not self.api_key:
            raise ValidationError("ConvertKit API key not configured")

        if not email or "@" not in email:
            raise ValidationError("Valid email is required")

        try:
            data = {
                "first_name": first_name,
                "email": email,
                "api_key": self.api_key
            }

            if language:
                data["fields"] = {"language": language}

            response = requests.post(
                f"https://api.kit.com/v3/sequences/{self.sequence_id}/subscribe",
                json=data,
                timeout=10
            )

            if response.status_code == 200:
                AuditLogger.log_action(
                    "CONVERTKIT_SUBSCRIBER_ADDED",
                    {"email": email, "language": language, "response": "success"}
                )
                return True
            else:
                AuditLogger.log_action(
                    "CONVERTKIT_ERROR",
                    {"email": email, "status_code": response.status_code, "response": response.text[:200]}
                )
                raise ValidationError(f"ConvertKit API error: {response.status_code} - {response.text[:100]}")

        except requests.RequestException as e:
            AuditLogger.log_action(
                "CONVERTKIT_REQUEST_ERROR",
                {"email": email, "error": str(e)}
            )
            raise ValidationError(f"Request failed: {str(e)}")

    @ErrorHandler.handle_database_error
    def get_subscriber_by_email(self, email: str) -> Dict:
        if not self.api_secret:
            raise ValidationError("ConvertKit API secret not configured")

        if not email or "@" not in email:
            raise ValidationError("Valid email is required")

        try:
            params = {
                "api_secret": self.api_secret,
                "email_address": email
            }

            response = requests.get(
                "https://api.convertkit.com/v3/subscribers",
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("subscribers"):
                    return data["subscribers"][0]

            return None

        except requests.RequestException as e:
            return None

    @ErrorHandler.handle_database_error
    def update_subscriber_language(self, subscriber_id: str, language: str) -> bool:
        if not self.api_secret:
            raise ValidationError("ConvertKit API secret not configured")

        if not subscriber_id or not language:
            raise ValidationError("Subscriber ID and language are required")

        try:
            url = f"https://api.convertkit.com/v3/subscribers/{subscriber_id}"

            payload = {
                "api_secret": self.api_secret,
                "fields": {
                    "language": language
                }
            }

            response = requests.put(url, json=payload, timeout=10)

            if response.status_code == 200:
                AuditLogger.log_action(
                    "CONVERTKIT_LANGUAGE_UPDATED",
                    {"subscriber_id": subscriber_id, "language": language}
                )
                return True

            return False

        except requests.RequestException as e:
            return False

    @audit_log("BULK_SYNC_CONVERTKIT")
    def bulk_sync_users(self, users: List[Dict]) -> Dict:
        synced = 0
        failed = 0

        for user in users:
            try:
                email = user.get("email")
                language = user.get("language")

                if email and "privaterelay" not in email:
                    subscriber = self.get_subscriber_by_email(email)

                    if subscriber:
                        subscriber_id = subscriber.get("id")
                        if self.update_subscriber_language(subscriber_id, language):
                            synced += 1
                        else:
                            failed += 1
                    else:
                        if self.add_subscriber(email, user.get("name", "User"), language):
                            synced += 1
                        else:
                            failed += 1

            except Exception as e:
                failed += 1

        AuditLogger.log_action(
            "CONVERTKIT_BULK_SYNC_COMPLETE",
            {"synced": synced, "failed": failed}
        )

        return {"synced": synced, "failed": failed}
