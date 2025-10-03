import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Security configuration for admin dashboard"""

    # Database settings (from .env)
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
    DB_PORT = os.getenv("DB_PORT", "3306")

    # Security settings
    SECRET_KEY = os.getenv("SECRET_KEY")
    SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", "1800"))

    # Authentication
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH")

    # Environment
    ENVIRONMENT = os.getenv("ENVIRON", "development")

    # Geocoding defaults
    DEFAULT_LOCATION = os.getenv("DEFAULT_LOCATION", "POINT(4.19297 51.2603666)")

    @classmethod
    def validate_config(cls):
        """Validate critical configuration"""
        missing = []

        if not cls.DB_PASSWORD:
            missing.append("DB_PASSWORD")
        if not cls.SECRET_KEY:
            missing.append("SECRET_KEY")
        if not cls.ADMIN_PASSWORD_HASH:
            missing.append("ADMIN_PASSWORD_HASH")

        if missing:
            st.error(f"Missing required environment variables: {', '.join(missing)}")
            st.error("Please create a .env file with all required variables.")
            st.stop()

    @classmethod
    def get_database_url(cls):
        """Get secure database connection URL"""
        return f"mysql+mysqlconnector://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"

    @classmethod
    def is_production(cls):
        """Check if running in production"""
        return cls.ENVIRONMENT.lower() == "production"

    @classmethod
    def configure_streamlit_security(cls):
        """Configure Streamlit security settings with full screen layout"""
        if cls.is_production():
            # Production security headers
            st.set_page_config(
                page_title="Admin Dashboard",
                page_icon="⚡",
                layout="wide",
                initial_sidebar_state="collapsed",
                menu_items={"Get Help": None, "Report a bug": None, "About": None},
            )
        else:
            st.set_page_config(
                page_title="Admin Dashboard [DEV]",
                page_icon="⚡",
                layout="wide",
                initial_sidebar_state="collapsed",
            )

        st.markdown(
            """
        <style>
        .main .block-container {
            padding: 1rem;
            max-width: 100%;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            background-color: #f0f2f6;
            border-radius: 4px 4px 0px 0px;
            padding: 10px;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #ffffff;
            border-bottom: 2px solid #007acc;
        }
        
        .stDataFrame {
            width: 100%;
        }
        
        .stForm {
            border: 1px solid #e9ecef;
            border-radius: 0.5rem;
            padding: 1rem;
            background-color: #f8f9fa;
        }
        
        header[data-testid="stHeader"] {
            display: none;
        }
        
        footer {
            display: none;
        }
        
        .stButton > button {
            border-radius: 0.5rem;
            border: 1px solid #dee2e6;
            transition: all 0.2s;
        }
        
        .stButton > button:hover {
            background-color: #f8f9fa;
            border-color: #007acc;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )


config = Config()
