from sqlalchemy import create_engine 
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.orm import sessionmaker

# SQLALCHEMY_DATABASE_URL = "postgresql://admin:123@localhost:5433/bookcircle"
# SQLALCHEMY_DATABASE_URL = "sqlite:///database.db"

SQLALCHEMY_DATABASE_URL = "postgresql://Admin:kaisql@localhost:5432/bookcircle"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
