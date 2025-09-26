"""Database connection and session management"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()


class DatabaseService:
    """Handles database connections and session management"""

    def __init__(self):
        db_host = os.getenv("DB_HOST", "34.76.230.176")
        db_user = os.getenv("DB_USER", "boyan")
        db_password = os.getenv("DB_PASSWORD", "00000000")
        db_name = os.getenv("DB_NAME", "jointlyProd")
        db_port = os.getenv("DB_PORT", "3306")

        DATABASE_URL = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

        self.engine = create_engine(DATABASE_URL)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def get_session(self):
        """Get database session context manager"""
        return self.SessionLocal()
