import logging
from functools import wraps
from typing import Any, Callable, Optional, Type, Union

import requests.exceptions as requests_errors
from sqlalchemy.exc import SQLAlchemyError

from utils.exceptions import (
    DashboardException,
    DatabaseError,
    SecurityError,
    UserNotFoundError,
    ValidationError,
)

logger = logging.getLogger(__name__)


class ErrorHandler:
    """Standardized error handling for dashboard services"""

    @staticmethod
    def handle_database_error(func: Callable) -> Callable:
        """Decorator for handling database-related errors"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except SQLAlchemyError as e:
                logger.error(f"Database error in {func.__name__}: {str(e)}")
                raise DatabaseError(
                    f"Database operation failed in {func.__name__}",
                    details={"original_error": str(e)},
                )
            except (ValidationError, UserNotFoundError, SecurityError):
                raise
            except Exception as e:
                logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
                raise DashboardException(
                    f"Unexpected error in {func.__name__}",
                    details={"original_error": str(e)},
                )

        return wrapper

    @staticmethod
    def handle_api_error(func: Callable) -> Callable:
        """Decorator for handling API-related errors"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except requests_errors.RequestException as e:
                logger.error(f"API error in {func.__name__}: {str(e)}")
                raise DashboardException(
                    f"API request failed in {func.__name__}",
                    details={"original_error": str(e)},
                )
            except Exception as e:
                logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
                raise DashboardException(
                    f"Unexpected error in {func.__name__}",
                    details={"original_error": str(e)},
                )

        return wrapper

    @staticmethod
    def handle_validation_error(func: Callable) -> Callable:
        """Decorator for handling validation errors"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValidationError:
                raise  
            except Exception as e:
                logger.error(f"Validation error in {func.__name__}: {str(e)}")
                raise ValidationError(
                    f"Validation failed in {func.__name__}",
                    details={"original_error": str(e)},
                )

        return wrapper

    @staticmethod
    def safe_execute(
        func: Callable,
        default_return: Any = None,
        log_errors: bool = True,
        raise_on_error: bool = False,
        expected_exceptions: tuple = (),
    ) -> Any:
        """
        Safely execute a function with consistent error handling

        Args:
            func: Function to execute
            default_return: Value to return if function fails
            log_errors: Whether to log errors
            raise_on_error: Whether to raise exceptions or return default
            expected_exceptions: Tuple of expected exception types to handle specifically
        """
        try:
            return func()
        except expected_exceptions as e:
            if log_errors:
                logger.warning(f"Expected exception in {func.__name__}: {str(e)}")
            if raise_on_error:
                raise
            return default_return
        except ValidationError as e:
            if log_errors:
                logger.error(f"Validation error in {func.__name__}: {str(e)}")
            if raise_on_error:
                raise
            return default_return
        except DatabaseError as e:
            if log_errors:
                logger.error(f"Database error in {func.__name__}: {str(e)}")
            if raise_on_error:
                raise
            return default_return
        except DashboardException as e:
            if log_errors:
                logger.error(f"Dashboard error in {func.__name__}: {str(e)}")
            if raise_on_error:
                raise
            return default_return
        except Exception as e:
            if log_errors:
                logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            if raise_on_error:
                raise DashboardException(
                    f"Unexpected error in {func.__name__}",
                    details={"original_error": str(e)},
                )
            return default_return

    @staticmethod
    def validate_and_execute(
        validation_func: Callable[[], bool],
        execution_func: Callable,
        validation_error_message: str = "Validation failed",
        default_return: Any = None,
        raise_on_validation_error: bool = True,
    ) -> Any:
        """
        Validate input and execute function with proper error handling
        """
        try:
            if not validation_func():
                if raise_on_validation_error:
                    raise ValidationError(validation_error_message)
                return default_return

            return ErrorHandler.safe_execute(
                execution_func, default_return=default_return, raise_on_error=True
            )
        except ValidationError:
            if raise_on_validation_error:
                raise
            return default_return

    @staticmethod
    def log_and_return_none(error: Exception, operation: str) -> None:
        """Legacy method for backward compatibility - prefer using exceptions"""
        logger.error(f"Error in {operation}: {str(error)}")
        return None

    @staticmethod
    def log_and_return_empty(
        error: Exception, operation: str, return_type: str = "list"
    ) -> Union[list, dict]:
        """Legacy method for backward compatibility - prefer using exceptions"""
        logger.error(f"Error in {operation}: {str(error)}")
        return [] if return_type == "list" else {}

    @staticmethod
    def log_and_return_false(error: Exception, operation: str) -> bool:
        """Legacy method for backward compatibility - prefer using exceptions"""
        logger.error(f"Error in {operation}: {str(error)}")
        return False
