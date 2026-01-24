from sqlalchemy import Column, String, DateTime, Integer
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