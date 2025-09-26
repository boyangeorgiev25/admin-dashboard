import html
import logging
import re
from datetime import datetime
from functools import wraps
from typing import Any, Optional

import bleach
import streamlit as st

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("admin_audit.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class SecurityValidator:
    """Enterprise-grade security validation for admin dashboard"""

    def __init__(self):
        self.allowed_tags = ["b", "i", "u", "em", "strong", "p", "br"]
        self.allowed_attributes = {}

    def sanitize_html(self, text: str) -> str:
        """Remove potentially dangerous HTML content"""
        if not text:
            return ""
        return bleach.clean(
            text, tags=self.allowed_tags, attributes=self.allowed_attributes, strip=True
        )

    def sanitize_input(self, text: str) -> str:
        """Sanitize user input by escaping HTML and removing dangerous characters"""
        if not text:
            return ""

        # HTML escape
        text = html.escape(text)

        # Remove null bytes and control characters except newlines and tabs
        text = re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]", "", text)

        return text.strip()

    def validate_user_id(self, user_id: str) -> bool:
        """Validate user ID format - must be numeric"""
        if not user_id:
            return False
        try:
            int(user_id)
            return 1 <= int(user_id) <= 999999999  # Reasonable range
        except ValueError:
            return False

    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        if not email:
            return False
        if len(email) > 254:  # RFC limit
            return False
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    def validate_username(self, username: str) -> bool:
        """Validate username format"""
        if not username:
            return False
        return len(username) <= 100 and len(username) >= 1

    def validate_search_query(self, query: str) -> bool:
        """Validate search query to prevent SQL injection"""
        if not query:
            return False

        # Block dangerous SQL patterns
        dangerous_patterns = [
            r"(union|select|drop|delete|insert|update|create|alter|exec|execute)\s",
            r"[;<>|&$`]",
            r"--",
            r"/\*",
            r"\*/",
            r"xp_",
            r"sp_",
            r"0x[0-9a-f]+",
        ]

        query_lower = query.lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                logger.warning(
                    f"SECURITY: Blocked potentially dangerous search query from {st.session_state.get('username', 'unknown')}: {query}"
                )
                return False

        return len(query) <= 200

    def validate_message_content(self, content: str) -> bool:
        """Validate admin message content"""
        if not content:
            return False

        if len(content) > 5000:
            return False

        # Check for script injection
        script_patterns = [
            r"<script",
            r"javascript:",
            r"vbscript:",
            r"onload=",
            r"onerror=",
            r"onclick=",
        ]

        content_lower = content.lower()
        for pattern in script_patterns:
            if pattern in content_lower:
                logger.warning(
                    f"SECURITY: Blocked message with script content from {st.session_state.get('username', 'unknown')}"
                )
                return False

        return True


class AuditLogger:
    """Comprehensive audit logging for admin actions"""

    @staticmethod
    def log_action(action: str, details: dict = None, success: bool = True):
        """Log admin action with full context"""
        username = st.session_state.get("username", "unknown")
        user_role = st.session_state.get("user_role", "unknown")
        timestamp = datetime.now().isoformat()

        log_data = {
            "timestamp": timestamp,
            "username": username,
            "role": user_role,
            "action": action,
            "success": success,
            "details": details or {},
        }

        if success:
            logger.info(
                f"AUDIT SUCCESS: {username} ({user_role}) - {action} | {details}"
            )
        else:
            logger.warning(
                f"AUDIT FAILURE: {username} ({user_role}) - {action} | {details}"
            )


def audit_log(action: str):
    """Decorator to automatically log admin actions"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            username = st.session_state.get("username", "unknown")
            try:
                result = func(*args, **kwargs)
                AuditLogger.log_action(
                    action, {"function": func.__name__}, success=True
                )
                return result
            except Exception as e:
                AuditLogger.log_action(
                    action, {"function": func.__name__, "error": str(e)}, success=False
                )
                raise

        return wrapper

    return decorator


# Role-based access removed per user request


def sanitize_display_data(data: dict) -> dict:
    """Sanitize data before displaying in UI"""
    validator = SecurityValidator()
    sanitized = {}

    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = validator.sanitize_input(value)
        else:
            sanitized[key] = value

    return sanitized


# Global instances
security_validator = SecurityValidator()
audit_logger = AuditLogger()
