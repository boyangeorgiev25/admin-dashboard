"""Tests for security module"""
import pytest
from unittest.mock import patch, MagicMock
from security import SecurityValidator, AuditLogger


class TestSecurityValidator:
    """Test cases for SecurityValidator class"""

    def setup_method(self):
        """Setup test fixtures"""
        self.validator = SecurityValidator()

    def test_validate_user_id_valid(self):
        """Test valid user ID validation"""
        assert self.validator.validate_user_id("12345") is True
        assert self.validator.validate_user_id("1") is True

    def test_validate_user_id_invalid(self):
        """Test invalid user ID validation"""
        assert self.validator.validate_user_id("") is False
        assert self.validator.validate_user_id("abc") is False
        assert self.validator.validate_user_id("12.34") is False
        assert self.validator.validate_user_id("0") is False
        assert self.validator.validate_user_id("9999999999") is False

    def test_validate_email_valid(self):
        """Test valid email validation"""
        assert self.validator.validate_email("test@example.com") is True
        assert self.validator.validate_email("user.name@domain.co.uk") is True

    def test_validate_email_invalid(self):
        """Test invalid email validation"""
        assert self.validator.validate_email("") is False
        assert self.validator.validate_email("invalid-email") is False
        assert self.validator.validate_email("@domain.com") is False
        assert self.validator.validate_email("user@") is False
        assert self.validator.validate_email("a" * 255 + "@domain.com") is False

    def test_validate_search_query_valid(self):
        """Test valid search query validation"""
        assert self.validator.validate_search_query("john_doe") is True
        assert self.validator.validate_search_query("user123") is True
        assert self.validator.validate_search_query("test@email.com") is True

    def test_validate_search_query_invalid(self):
        """Test invalid search query validation"""
        assert self.validator.validate_search_query("") is False
        assert self.validator.validate_search_query("DROP TABLE users") is False
        assert self.validator.validate_search_query("SELECT * FROM users") is False
        assert self.validator.validate_search_query("user; DELETE FROM") is False
        assert self.validator.validate_search_query("a" * 201) is False

    def test_sanitize_input(self):
        """Test input sanitization"""
        assert self.validator.sanitize_input("<script>alert('xss')</script>") == "&lt;script&gt;alert('xss')&lt;/script&gt;"
        assert self.validator.sanitize_input("normal text") == "normal text"
        assert self.validator.sanitize_input("") == ""

    def test_validate_message_content_valid(self):
        """Test valid message content validation"""
        assert self.validator.validate_message_content("Hello, this is a message") is True
        assert self.validator.validate_message_content("A" * 1000) is True

    def test_validate_message_content_invalid(self):
        """Test invalid message content validation"""
        assert self.validator.validate_message_content("") is False
        assert self.validator.validate_message_content("A" * 5001) is False
        assert self.validator.validate_message_content("<script>alert('xss')</script>") is False


class TestAuditLogger:
    """Test cases for AuditLogger class"""

    @patch('security.logger')
    @patch('streamlit.session_state', {'username': 'test_admin', 'user_role': 'admin'})
    def test_log_action_success(self, mock_logger):
        """Test successful action logging"""
        AuditLogger.log_action('TEST_ACTION', {'key': 'value'}, success=True)
        mock_logger.info.assert_called_once()

    @patch('security.logger')
    @patch('streamlit.session_state', {'username': 'test_admin', 'user_role': 'admin'})
    def test_log_action_failure(self, mock_logger):
        """Test failed action logging"""
        AuditLogger.log_action('TEST_ACTION', {'key': 'value'}, success=False)
        mock_logger.warning.assert_called_once()

    @patch('security.logger')
    @patch('streamlit.session_state', {})
    def test_log_action_unknown_user(self, mock_logger):
        """Test logging with unknown user"""
        AuditLogger.log_action('TEST_ACTION')
        assert mock_logger.info.called or mock_logger.warning.called