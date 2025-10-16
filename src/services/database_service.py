"""Database connection and session management"""

import os
from contextlib import contextmanager

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

load_dotenv()


class DatabaseService:
    """Handles database connections and session management"""

    def __init__(self):
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_name = os.getenv("DB_NAME")
        instance_connection_name = os.getenv("INSTANCE_CONNECTION_NAME")

        if not all([db_user, db_password, db_name]):
            raise ValueError("Missing required database configuration. Check your .env file.")

        if instance_connection_name:
            from google.cloud.sql.connector import Connector
            connector = Connector()

            def getconn():
                return connector.connect(
                    instance_connection_name,
                    "pymysql",
                    user=db_user,
                    password=db_password,
                    db=db_name,
                    timeout=30,
                    enable_iam_auth=False,
                )

            self.engine = create_engine(
                "mysql+pymysql://",
                creator=getconn,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=1800,
                echo=False,
            )
        else:
            db_host = os.getenv("DB_HOST", "127.0.0.1")
            db_port = os.getenv("DB_PORT", "3306")
            DATABASE_URL = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

            self.engine = create_engine(
                DATABASE_URL,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                pool_recycle=3600,
                connect_args={
                    'connect_timeout': 10,
                    'connection_timeout': 10
                }
            )
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    @contextmanager
    def get_session(self):
        """Get database session with proper context manager support"""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()
