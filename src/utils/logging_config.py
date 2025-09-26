"""Logging configuration for the admin dashboard"""

import json
import logging
import logging.handlers
import os
from datetime import datetime
from typing import Optional


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if hasattr(record, "user"):
            log_entry["user"] = record.user
        if hasattr(record, "action"):
            log_entry["action"] = record.action
        if hasattr(record, "error_code"):
            log_entry["error_code"] = record.error_code
        if hasattr(record, "details"):
            log_entry["details"] = record.details

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, ensure_ascii=False)


class DashboardLogger:
    """Centralized logging configuration for the dashboard"""

    def __init__(self, log_level: str = "INFO", log_dir: str = "logs"):
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.log_dir = log_dir
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Setup logging configuration"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)

        root_logger.handlers.clear()

        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

        app_log_file = os.path.join(self.log_dir, "dashboard.log")
        app_handler = logging.handlers.RotatingFileHandler(
            app_log_file, maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
        )
        app_handler.setLevel(logging.DEBUG)
        app_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(app_handler)

        security_log_file = os.path.join(self.log_dir, "security_audit.log")
        security_handler = logging.FileHandler(security_log_file)
        security_handler.setLevel(logging.INFO)
        security_handler.setFormatter(JSONFormatter())

        security_logger = logging.getLogger("security")
        security_logger.addHandler(security_handler)
        security_logger.setLevel(logging.INFO)
        security_logger.propagate = False

        error_log_file = os.path.join(self.log_dir, "errors.log")
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file, maxBytes=5 * 1024 * 1024, backupCount=3  # 5MB
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(error_handler)

        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

        logging.info("Logging system initialized")

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Get a logger instance with the given name"""
        return logging.getLogger(name)

    @staticmethod
    def get_security_logger() -> logging.Logger:
        """Get the security audit logger"""
        return logging.getLogger("security")

    @staticmethod
    def log_user_action(user: str, action: str, details: Optional[dict] = None) -> None:
        """Log user action to security audit log"""
        security_logger = logging.getLogger("security")
        security_logger.info(
            f"User action: {action}",
            extra={"user": user, "action": action, "details": details or {}},
        )

    @staticmethod
    def log_security_event(
        event_type: str,
        message: str,
        details: Optional[dict] = None,
        user: Optional[str] = None,
    ) -> None:
        """Log security event to security audit log"""
        security_logger = logging.getLogger("security")
        security_logger.warning(
            f"Security event - {event_type}: {message}",
            extra={
                "user": user or "unknown",
                "action": event_type,
                "details": details or {},
            },
        )


def setup_logging(log_level: str = None, log_dir: str = None) -> DashboardLogger:
    """Setup logging system with environment-based configuration"""
    log_level = log_level or os.getenv("LOG_LEVEL", "INFO")
    log_dir = log_dir or os.getenv("LOG_DIR", "logs")

    return DashboardLogger(log_level=log_level, log_dir=log_dir)


dashboard_logger = None


def get_logger(name: str = __name__) -> logging.Logger:
    """Get logger instance, initializing logging system if needed"""
    global dashboard_logger
    if dashboard_logger is None:
        dashboard_logger = setup_logging()
    return dashboard_logger.get_logger(name)
