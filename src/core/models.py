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
    subtype_id = Column(Integer, ForeignKey('activity_types.id'), index=True, nullable=True)
    subtype_code = Column(Integer, nullable=True)
    intent = Column(Integer, index=True, nullable=True)
    date = Column(DateTime, nullable=True, index=True)
    place_id = Column(Integer, nullable=True)
    place = Column(String(100), nullable=True)
    city = Column(String(100))
    location = Column(String(100), nullable=True)
    participants_min = Column(Integer, nullable=True)
    participants_max = Column(Integer, nullable=True)
    min_age = Column(Integer, nullable=True)
    max_age = Column(Integer, nullable=True)
    allowed_genders = Column(Integer, nullable=True)
    img_url = Column(String(200), nullable=True)
    question1 = Column(String(150), nullable=True)
    question2 = Column(String(150), nullable=True)
    question3 = Column(String(150), nullable=True)
    is_full = Column(Boolean, default=False)
    is_reported = Column(Boolean, default=False)
    shuffle_key = Column(Float, nullable=True)
    created_at = Column(DateTime, nullable=True)
    nl = Column(Boolean, nullable=True)
    en = Column(Boolean, nullable=True)
    fr = Column(Boolean, nullable=True)
    schedule_date_deadline = Column(DateTime, nullable=True)
    check_in_sent = Column(Boolean, nullable=True)
    asked_review = Column(Boolean, nullable=True)
    is_partner_event = Column(Boolean, nullable=True)


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


class Place(Base):
    __tablename__ = "places"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(60))
    subtype_id = Column(Integer, ForeignKey('activity_types.id'), index=True)
    keywords = Column(String(150))
    address = Column(String(150))
    img_url = Column(String(150))
    url = Column(String(150))
    location = Column(String(100))


class ActivityType(Base):
    __tablename__ = "activity_types"
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(50), nullable=False)
    subtype = Column(String(50), nullable=False, unique=True)
    subtype_nl = Column(String(50), nullable=False, unique=True)
    subtype_fr = Column(String(50), nullable=False, unique=True)
    subtype_code = Column(Integer, unique=True, nullable=False)
    img_url = Column(String(250), nullable=True)
    emoji = Column(String(10), nullable=False)


class Community(Base):
    __tablename__ = 'communities'
    id = Column(Integer, primary_key=True)
    name = Column(String(40))
    description = Column(String(300))
    img_url = Column(String(150))
    location = Column(String(100))
    is_starter = Column(Boolean)


class ActivityJoiner(Base):
    __tablename__ = 'activity_joiners'
    activity_id = Column(Integer, ForeignKey('activities.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    answer1 = Column(String(250), nullable=True)
    answer2 = Column(String(250), nullable=True)
    answer3 = Column(String(250), nullable=True)
    intro = Column(String(250), nullable=True)


class ChatMeta(Base):
    __tablename__ = 'chat_meta'
    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, ForeignKey('activities.id'), index=True, nullable=True)
    last_sender_name = Column(String(100), nullable=True)
    last_message = Column(Text, nullable=True)
    last_timestamp = Column(Integer, nullable=True)
    activity_name = Column(String(50), nullable=True)
    activity_subtype_id = Column(Integer, ForeignKey('activity_types.id'), nullable=True)


class ChatUserActivity(Base):
    __tablename__ = 'chat_user_activity'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    chat_id = Column(Integer, ForeignKey('chat_meta.id'))
    last_activity = Column(Integer, nullable=True)
    active = Column(Boolean, default=True)


class IndChats(Base):
    __tablename__ = 'ind_chats'
    id = Column(Integer, primary_key=True)
    activity_name = Column(String(100), nullable=True)
    activity_id = Column(Integer, nullable=True)
    activity_owner_id = Column(Integer, ForeignKey('users.id'))
    last_sender_name = Column(String(100), nullable=True)
    last_message = Column(Text, nullable=True)
    last_timestamp = Column(Integer, nullable=True)
    receiver_id = Column(Integer, ForeignKey('users.id'))


class IndChatMembers(Base):
    __tablename__ = 'ind_chat_membership'
    id = Column(Integer, primary_key=True)
    ind_chat_id = Column(Integer, ForeignKey('ind_chats.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    last_activity = Column(Integer, nullable=True)
    active = Column(Boolean, default=True)


class MessageReaction(Base):
    __tablename__ = 'message_reactions'
    id = Column(Integer, primary_key=True, index=True)
    emoji_id = Column(Integer, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    message_id = Column(Integer, ForeignKey('messages.id'), index=True)


class IndMessageReaction(Base):
    __tablename__ = 'ind_message_reactions'
    id = Column(Integer, primary_key=True, index=True)
    emoji_id = Column(Integer, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    ind_message_id = Column(Integer, ForeignKey('ind_messages.id'), index=True)


class CommunityThread(Base):
    __tablename__ = 'community_threads'
    id = Column(Integer, primary_key=True)
    community_id = Column(Integer, ForeignKey('communities.id'))
    created_at = Column(DateTime)
    last_updated = Column(DateTime)
    owner_id = Column(Integer, ForeignKey('users.id'))
    body = Column(Text)
    title = Column(String(250))
    is_reported = Column(Boolean, default=False)


class CommunityThreadReply(Base):
    __tablename__ = 'community_thread_replies'
    id = Column(Integer, primary_key=True)
    thread_id = Column(Integer, ForeignKey('community_threads.id'), index=True)
    created_at = Column(DateTime)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    body = Column(Text)
    parent_id = Column(Integer, ForeignKey('community_thread_replies.id'), nullable=True)
    is_reported = Column(Boolean, default=False)


class CommunityMembership(Base):
    __tablename__ = 'community_membership'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    community_id = Column(Integer, ForeignKey('communities.id'), primary_key=True)
    last_visited = Column(DateTime)


class CommunityThreadUpvote(Base):
    __tablename__ = 'community_thread_upvotes'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    thread_id = Column(Integer, ForeignKey('community_threads.id'))


class CommunityThreadReplyUpvote(Base):
    __tablename__ = 'community_thread_reply_upvotes'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    reply_id = Column(Integer, ForeignKey('community_thread_replies.id'))
