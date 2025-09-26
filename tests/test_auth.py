"""Tests for authentication module"""
import pytest
from unittest.mock import patch, MagicMock
import time
from auth import AuthManager


class TestAuthManager:
    """Test cases for AuthManager class"""

    def setup_method(self):
        """Setup test fixtures"""
        with patch.dict('os.environ', {
            'ADMIN_USERNAME': 'test_admin',
            'SESSION_TIMEOUT': '1800'
        }):
            self.auth_manager = AuthManager()

    def test_hash_password(self):
        """Test password hashing"""
        password = "test_password"
        hashed = self.auth_manager._hash_password(password)
        assert hashed != password
        assert len(hashed) > 0

    def test_verify_password_correct(self):
        """Test correct password verification"""
        password = "test_password"
        hashed = self.auth_manager._hash_password(password)
        assert self.auth_manager._verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test incorrect password verification"""
        password = "test_password"
        wrong_password = "wrong_password"
        hashed = self.auth_manager._hash_password(password)
        assert self.auth_manager._verify_password(wrong_password, hashed) is False

    @patch('streamlit.session_state', {})
    def test_authenticate_valid_credentials(self):
        """Test authentication with valid credentials"""
        # Mock a user with a known password
        test_password = "test123"
        hashed_password = self.auth_manager._hash_password(test_password)
        self.auth_manager.users["testuser"] = {
            "password_hash": hashed_password,
            "role": "admin",
            "failed_attempts": 0,
            "locked_until": None
        }

        result = self.auth_manager.authenticate("testuser", test_password)
        assert result is True

    @patch('streamlit.session_state', {})
    def test_authenticate_invalid_credentials(self):
        """Test authentication with invalid credentials"""
        result = self.auth_manager.authenticate("nonexistent", "wrongpassword")
        assert result is False

    @patch('streamlit.session_state', {})
    def test_authenticate_empty_credentials(self):
        """Test authentication with empty credentials"""
        assert self.auth_manager.authenticate("", "") is False
        assert self.auth_manager.authenticate("user", "") is False
        assert self.auth_manager.authenticate("", "password") is False

    def test_account_lockout(self):
        """Test account lockout after failed attempts"""
        # Create a test user
        test_password = "test123"
        hashed_password = self.auth_manager._hash_password(test_password)
        self.auth_manager.users["locktest"] = {
            "password_hash": hashed_password,
            "role": "admin",
            "failed_attempts": 0,
            "locked_until": None
        }

        # Simulate 5 failed attempts
        for i in range(5):
            with patch('streamlit.session_state', {}):
                result = self.auth_manager.authenticate("locktest", "wrongpassword")
                assert result is False

        # Check that account is locked
        user = self.auth_manager.users["locktest"]
        assert user["failed_attempts"] == 5
        assert user["locked_until"] is not None

    @patch('streamlit.session_state', {'authenticated': True, 'login_time': time.time()})
    def test_is_authenticated_valid_session(self):
        """Test valid session authentication check"""
        result = self.auth_manager.is_authenticated()
        assert result is True

    @patch('streamlit.session_state', {})
    def test_is_authenticated_no_session(self):
        """Test authentication check with no session"""
        result = self.auth_manager.is_authenticated()
        assert result is False

    @patch('streamlit.session_state', {
        'authenticated': True,
        'login_time': time.time() - 3600  # 1 hour ago
    })
    def test_is_authenticated_expired_session(self):
        """Test authentication check with expired session"""
        result = self.auth_manager.is_authenticated()
        assert result is False

    @patch('streamlit.session_state', {
        'authenticated': True,
        'username': 'testuser',
        'user_role': 'admin',
        'login_time': time.time()
    })
    def test_logout(self):
        """Test logout functionality"""
        import streamlit as st
        self.auth_manager.logout()
        
        # Check that session keys are cleared
        assert 'authenticated' not in st.session_state
        assert 'username' not in st.session_state
        assert 'user_role' not in st.session_state
        assert 'login_time' not in st.session_state