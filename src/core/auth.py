import logging
import os
import secrets
import time
from typing import Dict, Optional

import bcrypt
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class AuthManager:
    """Simple authentication manager for the dashboard"""

    def __init__(self):
       
        self.users = {}

        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_password_hash = os.getenv("ADMIN_PASSWORD_HASH")

        if admin_password_hash:
            self.users[admin_username] = {
                "password_hash": admin_password_hash,
                "role": "admin",
                "last_login": None,
                "failed_attempts": 0,
                "locked_until": None,
            }

        brecht_username = os.getenv("BRECHT_USERNAME", "brecht")
        brecht_password_hash = os.getenv("BRECHT_PASSWORD_HASH")

        if brecht_password_hash:
            self.users[brecht_username] = {
                "password_hash": brecht_password_hash,
                "role": "admin",
                "last_login": None,
                "failed_attempts": 0,
                "locked_until": None,
            }

        if not self.users:
            logger.warning("No admin users configured. Using default credentials.")
            default_hash = self._hash_password("admin123!")
            self.users["admin"] = {
                "password_hash": default_hash,
                "role": "admin",
                "last_login": None,
                "failed_attempts": 0,
                "locked_until": None,
            }

        logger.info(f"Initialized authentication for {len(self.users)} admin users")
        self.session_timeout = int(
            os.getenv("SESSION_TIMEOUT", "1800")
        ) 
        self.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(32))

    def _hash_password(self, password: str) -> str:
        """Hash password with bcrypt"""
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def _verify_password(self, password: str, hash: str) -> bool:
        """Verify password against bcrypt hash"""
        return bcrypt.checkpw(password.encode("utf-8"), hash.encode("utf-8"))

    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate user credentials"""
        if not username or not password:
            return False

        user = self.users.get(username)
        if not user:
            logger.warning(f"Authentication attempt with unknown username: {username}")
            time.sleep(1)  
            return False

        if self._is_account_locked(user):
            logger.warning(f"Authentication attempt on locked account: {username}")
            return False

        if not self._verify_password(password, user["password_hash"]):
            logger.warning(f"Failed authentication attempt for user: {username}")
            user["failed_attempts"] += 1

            if user["failed_attempts"] >= 5:
                user["locked_until"] = time.time() + (15 * 60)  
                logger.warning(f"Account locked due to repeated failures: {username}")

            time.sleep(1)  
            return False

        user["failed_attempts"] = 0
        user["locked_until"] = None
        user["last_login"] = time.time()

        session_token = secrets.token_hex(32)
        st.session_state.authenticated = True
        st.session_state.username = username
        st.session_state.user_role = user["role"]
        st.session_state.login_time = time.time()
        st.session_state.session_token = session_token

        logger.info(f"Successful authentication for user: {username}")
        return True

    def _is_account_locked(self, user: Dict) -> bool:
        """Check if account is locked due to failed attempts"""
        if user.get("locked_until"):
            if time.time() < user["locked_until"]:
                return True
            else:
                user["locked_until"] = None
                user["failed_attempts"] = 0
        return False

    def is_authenticated(self) -> bool:
        """Check if user is authenticated and session is valid"""
        if not st.session_state.get("authenticated", False):
            return False

        login_time = st.session_state.get("login_time", 0)
        if time.time() - login_time > self.session_timeout:
            self.logout()
            return False

        return True

    def logout(self):
        """Clear authentication session"""
        username = st.session_state.get("username", "unknown")
        logger.info(f"User logged out: {username}")

        for key in ["authenticated", "username", "user_role", "login_time"]:
            if key in st.session_state:
                del st.session_state[key]

    def require_auth(self):
        """Decorator/middleware to require authentication"""
        if not self.is_authenticated():
            self.show_login_form()
            st.stop()

    def show_login_form(self):
        """Display login form"""
        st.title("🛡️ Platform Moderation Dashboard - Login")

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            with st.form("login_form"):
                st.subheader("Please log in to continue")

                username = st.text_input("Username")
                password = st.text_input("Password", type="password")

                if st.form_submit_button("Login", type="primary"):
                    if self.authenticate(username, password):
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")


# Global auth manager instance
auth_manager = AuthManager()


def require_authentication():
    """Convenience function to require authentication"""
    auth_manager.require_auth()


def is_authenticated() -> bool:
    """Check if user is authenticated"""
    return auth_manager.is_authenticated()


def get_current_user() -> Optional[str]:
    """Get current authenticated user"""
    if is_authenticated():
        return st.session_state.get("username")
    return None


def logout():
    """Logout current user"""
    auth_manager.logout()
