import pytest
from httpx import AsyncClient, ASGITransport
from main import app, get_current_user
from app import crud, models, schemas

# Mock user for auth bypass
async def mock_get_current_user():
    return models.User(id=1, username="testuser", email="test@example.com")

@pytest.fixture
async def client():
    app.dependency_overrides[get_current_user] = mock_get_current_user
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_item_not_found_exception(client):
    # Try to get a non-existent club
    response = await client.get("/clubs/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Club with id 999999 not found"

@pytest.mark.asyncio
async def test_item_not_found_book_in_club(client):
    # Try to get a non-existent book
    # Assuming club 1 exists or we simulate it, but crud raises exception immediately if query fails.
    # The crud logic for get_book_by_id checks specific IDs.
    response = await client.get("/clubs/1/books/999999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_update_non_existent_item(client):
    # Try to update non-existent club
    response = await client.put("/clubs/999999", json={
        "name": "New Name",
        "description": "Desc",
        "favorite_genre": "Genre",
        "members": 10
    })
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_non_existent_item(client):
    # Try to delete non-existent club
    response = await client.delete("/clubs/999999")
    assert response.status_code == 404
