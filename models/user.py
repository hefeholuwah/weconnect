from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)

    # Timestamp columns
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships for session tracking
    sessions = relationship("UserSession", back_populates="user")
    daily_usage = relationship("DailyUsage", back_populates="user")


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Null for guest users
    session_start = Column(DateTime(timezone=True), server_default=func.now())  # Start time
    session_end = Column(DateTime(timezone=True), nullable=True)  # End time of the session
    session_duration = Column(Integer)  # Duration in minutes

    # Relationships
    user = relationship("User", back_populates="sessions")


class DailyUsage(Base):
    __tablename__ = "daily_usage"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_time_used = Column(Integer, default=0)  # Total minutes used for the day
    usage_date = Column(DateTime(timezone=True), server_default=func.now())  # Date for usage tracking

    # Relationships
    user = relationship("User", back_populates="daily_usage")
