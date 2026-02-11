import pytest
from httpx import AsyncClient, ASGITransport
from app.core.rate_limit import limiter
from main import app

@pytest.fixture
async def client():
    # Use ASGITransport to test the app directly
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_health_rate_limit(client):
    # Hit the health endpoint 5 times (allowed)
    for _ in range(5):
        response = await client.get("/health")
        assert response.status_code == 200

    # The 6th request should fail with 429
    response = await client.get("/health")
    assert response.status_code == 429

@pytest.mark.asyncio
async def test_auth_rate_limit(client):
    # Reset limiter for this test (optional, depends on shared state but good practice)
    # SlowAPI in-memory storage might persist across tests if not cleared.
    # For now, let's just test a different endpoint or assume isolation.
    # We'll use /token endpoint.
    
    # Hit /token 5 times. We expect 401 because we aren't sending valid creds,
    # but the rate limiter should still count these requests.
    for _ in range(5):
        response = await client.post("/token", data={"username": "foo", "password": "bar"})
        # 422 if form data missing, 401 if invalid. 
        # But we want to fail rate limit, so status doesn't matter as long as it's not 429 yet.
        assert response.status_code != 429

    # 6th request -> 429
    response = await client.post("/token", data={"username": "foo", "password": "bar"})
    assert response.status_code == 429
