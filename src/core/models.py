import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True, index=True)
    phone = Column(String(25), nullable=True, index=True)
    birthdate = Column(String(25), nullable=True)
    city = Column(String(100), nullable=True)
    location = Column(String(50), nullable=True)
    intro = Column(String(200), nullable=True)
    lifephase = Column(String(50), nullable=True)
    img_url1 = Column(String(150), nullable=True)
    password = Column(String(100), nullable=True)
    notif_token = Column(String(100), nullable=True)
    gender = Column(String(30), nullable=True)
    reg_complete = Column(Boolean)
    language = Column(String(4), nullable=True)
    phone_verified = Column(Boolean)
    has_unreads = Column(Boolean)
    last_active = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=True)
    hosted = Column(Integer, nullable=True)
    hosted_success = Column(Integer, nullable=True)
    hosted_perc = Column(Float, nullable=True)
    joined = Column(Integer, nullable=True)
    joined_success = Column(Integer, nullable=True)
    joined_perc = Column(Float, nullable=True)
    is_ambassador = Column(Boolean)


class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(60))
    description = Column(String(350))
    owner_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime, nullable=True)
    city = Column(String(100))
    is_full = Column(Boolean)
    is_reported = Column(Boolean)


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    chat_id = Column(Integer)
    content = Column(Text)
    timestamp = Column(Integer)
    action_type = Column(String(50), nullable=True)
    action_text = Column(String(70), nullable=True)
    is_deleted = Column(Boolean, default=False)
    is_edited = Column(Boolean, default=False)


class UserReport(Base):
    __tablename__ = "reported_users"
    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id"))
    reported_id = Column(Integer)


class DeletedUser(Base):
    __tablename__ = "deleted_users"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    name = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)
    phone = Column(String(25), nullable=True)
    reason = Column(String(250), nullable=True)


class IndMessage(Base):
    __tablename__ = "ind_messages"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    timestamp = Column(Integer)
    sender_id = Column(Integer, ForeignKey("users.id"))
    ind_chat_id = Column(Integer, nullable=False)
    image_url = Column(String(250), nullable=True)
    image_width = Column(Integer, nullable=True)
    image_height = Column(Integer, nullable=True)
    action_type = Column(String(50), nullable=True)
    action_text = Column(String(70), nullable=True)
    action_data = Column(Text, nullable=True)


class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=True)
    status = Column(String(50), nullable=True)
    read_status = Column(Boolean, default=False)
