import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base
from main import app, get_db
from app import models

# Setup in-memory DB for testing
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_db():
    async with TestingSessionLocal() as db:
        yield db

@pytest.fixture(autouse=True)
def override_db_dependency():
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)

@pytest.fixture
async def prepare_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_auth_flow(prepare_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Register User
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "securepassword123",
            "fullName": "Test User"
        }
        response = await client.post("/auth/register", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert "id" in data

        # 2. Verify Password is Hashed in DB
        async with TestingSessionLocal() as db:
            result = await db.execute(select(models.User).filter(models.User.email == "test@example.com"))
            db_user = result.scalars().first()
            assert db_user is not None
            assert db_user.hashed_password != "securepassword123"
            assert db_user.hashed_password.startswith("$2") # bcrypt prefix

        # 3. Login Success
        login_data = {
            "username": "testuser",
            "password": "securepassword123"
        }
        response = await client.post("/token", data=login_data)
        assert response.status_code == 200
        token_data = response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"

        # 4. Login Fails - Wrong Password
        login_data_wrong = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        response = await client.post("/token", data=login_data_wrong)
        assert response.status_code == 401

        # 5. Login Fails - Wrong Username
        login_data_wrong_user = {
            "username": "wronguser",
            "password": "securepassword123"
        }
        response = await client.post("/token", data=login_data_wrong_user)
        assert response.status_code == 401
