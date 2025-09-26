"""UI-specific error handling for Streamlit components"""

import logging
from functools import wraps
from typing import Any, Callable, Optional

import streamlit as st

from utils.exceptions import (
    DashboardException,
    DatabaseError,
    SecurityError,
    UserNotFoundError,
    ValidationError,
)

logger = logging.getLogger(__name__)


class UIErrorHandler:
    """Handles errors in Streamlit UI components with user-friendly messages"""

    @staticmethod
    def handle_service_call(
        func: Callable,
        success_message: Optional[str] = None,
        default_return: Any = None,
        show_errors: bool = True,
    ) -> Any:
        """
        Handle service calls with appropriate UI error messages

        Args:
            func: Service function to call
            success_message: Message to show on success (optional)
            default_return: Value to return on error
            show_errors: Whether to display error messages in UI
        """
        try:
            result = func()
            if success_message and result is not None:
                st.success(success_message)
            return result

        except ValidationError as e:
            if show_errors:
                st.error(f"Input Error: {e.message}")
            logger.warning(f"Validation error: {e.message}")
            return default_return

        except UserNotFoundError as e:
            if show_errors:
                st.warning(e.message)
            logger.info(f"User lookup - {e.message}")
            return default_return

        except SecurityError as e:
            if show_errors:
                st.error("Security violation detected. Please check your input.")
            logger.warning(f"Security error: {e.message}")
            return default_return

        except DatabaseError as e:
            if show_errors:
                st.error("Database error occurred. Please try again later.")
            logger.error(f"Database error: {e.message}")
            return default_return

        except DashboardException as e:
            if show_errors:
                st.error(f"Service Error: {e.message}")
            logger.error(f"Dashboard error: {e.message}")
            return default_return

        except Exception as e:
            if show_errors:
                st.error("An unexpected error occurred. Please try again.")
            logger.error(f"Unexpected error: {str(e)}")
            return default_return

    @staticmethod
    def safe_service_call(show_errors: bool = True, default_return: Any = None):
        """Decorator for handling service calls in UI components"""

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                return UIErrorHandler.handle_service_call(
                    lambda: func(*args, **kwargs),
                    show_errors=show_errors,
                    default_return=default_return,
                )

            return wrapper

        return decorator

    @staticmethod
    def display_error_details(error: Exception, show_details: bool = False) -> None:
        """Display error with optional technical details"""
        if isinstance(error, ValidationError):
            st.error(f"Input Error: {error.message}")
            if show_details and error.details:
                st.expander("Details", expanded=False).json(error.details)

        elif isinstance(error, UserNotFoundError):
            st.warning(error.message)

        elif isinstance(error, SecurityError):
            st.error(f"Security Error: {error.message}")

        elif isinstance(error, DatabaseError):
            st.error("Database Error: Unable to access data. Please try again later.")
            if show_details:
                st.expander("Technical Details", expanded=False).error(str(error))

        elif isinstance(error, DashboardException):
            st.error(f"Service Error: {error.message}")
            if show_details and error.details:
                st.expander("Details", expanded=False).json(error.details)

        else:
            st.error("Unexpected Error: Something went wrong. Please try again.")
            if show_details:
                st.expander("Technical Details", expanded=False).error(str(error))

    @staticmethod
    def with_error_boundary(component_name: str = "Component"):
        """Decorator that wraps UI components with error boundaries"""

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error in {component_name}: {str(e)}")
                    st.error(
                        f"Error loading {component_name.lower()}. Please refresh the page."
                    )
                    if st.checkbox(f"Show {component_name} error details"):
                        st.exception(e)

            return wrapper

        return decorator

    @staticmethod
    def show_loading_with_error_handling(
        func: Callable, message: str = "Loading..."
    ) -> Any:
        """Show loading spinner while executing function with error handling"""
        with st.spinner(message):
            return UIErrorHandler.handle_service_call(func)
