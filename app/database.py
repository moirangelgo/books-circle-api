from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base 
from sqlalchemy.orm import sessionmaker

# SQLALCHEMY_DATABASE_URL = "postgresql://admin:123@localhost:5433/bookcircle"
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///database.db"

# SQLALCHEMY_DATABASE_URL = "postgresql://Admin:kaisql@localhost:5432/bookcircle"
engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()
