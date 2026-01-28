from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    id          = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email       = Column(String, unique=True, index=True, nullable=False)
    username    = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name   = Column(String)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

class Club(Base):
    __tablename__ = "clubes"
    id             = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name           = Column(String, unique=True, index=True, nullable=False)
    description    = Column(String)
    favorite_genre = Column(String)
    members        = Column(Integer)
    created_date   = Column(DateTime(timezone=True), server_default=func.now())

class Meeting(Base):
    __tablename__ = "meetings"
    id                  = Column(Integer, primary_key=True, index=True, autoincrement=True)
    club_id             = Column(Integer, ForeignKey("clubes.id"), nullable=False)
    # book_id             = Column(String, nullable=True)
    # book_title          = Column(String, nullable=True)
    # scheduled_at        = Column(DateTime(timezone=True), nullable=False)
    # duration            = Column(Integer, nullable=False)
    # location            = Column(String, nullable=True)
    # location_url        = Column(String, nullable=True)
    # description         = Column(String, nullable=True)
    # created_by          = Column(Integer, ForeignKey("users.id"))
    # status              = Column(String, default="upcoming")
    # is_virtual          = Column(Boolean, default=False)
    # virtual_meeting_url = Column(String, nullable=True)
    # attendee_count      = Column(Integer, default=0)