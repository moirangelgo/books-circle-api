from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Boolean
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    id          = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email       = Column(String, unique=True, index=True, nullable=False)
    username    = Column(String, unique=True, index=True, nullable=False)
    age         = Column(Integer, nullable=False, default=18)
    age2        = Column(Integer, nullable=False, default=18)
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


class Book(Base):
    __tablename__ = "libros"
    id             = Column(Integer, primary_key=True, index=True, autoincrement=True)
    club_id        = Column(Integer, ForeignKey("clubes.id"), nullable=False)
    title          = Column(String, nullable=False)
    author         = Column(String)
    votes          = Column(Integer, default=0)
    progress       = Column(Integer, default=0)  # Porcentaje    
    created_date   = Column(DateTime(timezone=True), server_default=func.now())


class Review(Base):
    __tablename__ = "reviews"
    id           = Column(Integer, primary_key=True, index=True, autoincrement=True)
    book_id      = Column(Integer, ForeignKey("libros.id"), nullable=False)
    club_id      = Column(Integer, ForeignKey("clubes.id"), nullable=False)
    user_id      = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating       = Column(Integer, default=0)
    comment      = Column(String)
    created_date = Column(DateTime(timezone=True), server_default=func.now())


class Testing(Base):
    __tablename__ = "testing"
    id           = Column(Integer, primary_key=True, index=True, autoincrement=True)
    comment      = Column(String)
    book_id      = Column(Integer, ForeignKey("libros.id"), nullable=False)


class Meeting(Base):
    __tablename__ = "meetings"
    id                = Column(Integer, primary_key=True, index=True, autoincrement=True)
    book_id           = Column(Integer, ForeignKey("libros.id"), nullable=False)
    club_id           = Column(Integer, ForeignKey("clubes.id"), nullable=False)
    book_title        = Column(String)
    scheduled_at      = Column(DateTime(timezone=True))
    duration          = Column(Integer, default=0)
    location          = Column(String)
    locationUrl       = Column(String)
    description       = Column(String)
    createdBy         = Column(String)
    attendeeCount     = Column(Integer)
    status            = Column(String)
    isVirtual         = Column(Boolean)
    virtualMeetingUrl = Column(String)


class MeetingAttendance(Base):
    __tablename__ = "meeting_attendance"
    id         = Column(Integer, primary_key=True, index=True, autoincrement=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    status     = Column(String, default='SI')

