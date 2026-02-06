import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base
from main import app, get_db
from app import models, schemas
from app.core import security

# Setup in-memory DB
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
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
async def test_protected_routes(prepare_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Setup Data: Register and Login to get Token
        user_data = {"email": "secure@example.com", "username": "secureuser", "password": "password", "fullName": "Secure User"}
        await client.post("/auth/register", json=user_data)
        
        login_res = await client.post("/token", data={"username": "secureuser", "password": "password"})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Test Protected Route WITHOUT Token (Should Fail)
        res_no_token = await client.get("/clubs")
        assert res_no_token.status_code == 401
        assert res_no_token.json()["detail"] == "Not authenticated"

        # 3. Test Protected Route WITH Token (Should Succeed - initially empty list)
        res_with_token = await client.get("/clubs", headers=headers)
        assert res_with_token.status_code == 200
        assert res_with_token.json() == []

        # 4. Create Club (Protected)
        club_data = {"name": "Test Club", "description": "desc"}
        res_create = await client.post("/clubs", json=club_data, headers=headers)
        assert res_create.status_code == 201
        
        # 5. Verify Club Created
        res_list = await client.get("/clubs", headers=headers)
        assert len(res_list.json()) == 1
