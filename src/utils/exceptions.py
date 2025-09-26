"""Custom exceptions for the admin dashboard"""

from typing import Optional


class DashboardException(Exception):
    """Base exception for dashboard-related errors"""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[dict] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "DASHBOARD_ERROR"
        self.details = details or {}


class AuthenticationError(DashboardException):
    """Raised when authentication fails"""

    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, error_code="AUTH_ERROR", **kwargs)


class AuthorizationError(DashboardException):
    """Raised when authorization fails"""

    def __init__(self, message: str = "Access denied", **kwargs):
        super().__init__(message, error_code="AUTHZ_ERROR", **kwargs)


class ValidationError(DashboardException):
    """Raised when input validation fails"""

    def __init__(
        self, message: str = "Validation failed", field: Optional[str] = None, **kwargs
    ):
        details = kwargs.get("details", {})
        if field:
            details["field"] = field
        super().__init__(
            message, error_code="VALIDATION_ERROR", details=details, **kwargs
        )


class DatabaseError(DashboardException):
    """Raised when database operations fail"""

    def __init__(self, message: str = "Database operation failed", **kwargs):
        super().__init__(message, error_code="DB_ERROR", **kwargs)


class ConfigurationError(DashboardException):
    """Raised when configuration is invalid"""

    def __init__(self, message: str = "Configuration error", **kwargs):
        super().__init__(message, error_code="CONFIG_ERROR", **kwargs)


class SecurityError(DashboardException):
    """Raised when security violations are detected"""

    def __init__(self, message: str = "Security violation detected", **kwargs):
        super().__init__(message, error_code="SECURITY_ERROR", **kwargs)


class UserNotFoundError(DashboardException):
    """Raised when a user is not found"""

    def __init__(self, user_id: Optional[str] = None, **kwargs):
        message = f"User not found: {user_id}" if user_id else "User not found"
        details = kwargs.get("details", {})
        if user_id:
            details["user_id"] = user_id
        super().__init__(
            message, error_code="USER_NOT_FOUND", details=details, **kwargs
        )
