import pytest
from fastapi.testclient import TestClient
from main import app, users_db, tokens_db, clubs_db, members_db, books_db, club_books_db, book_votes_db, reading_progress_db, meetings_db, club_meetings_db, meeting_attendance_db, reviews_db, book_reviews_db

@pytest.fixture(autouse=True)
def clear_db():
    users_db.clear()
    tokens_db.clear()
    clubs_db.clear()
    members_db.clear()
    books_db.clear()
    club_books_db.clear()
    book_votes_db.clear()
    reading_progress_db.clear()
    meetings_db.clear()
    club_meetings_db.clear()
    meeting_attendance_db.clear()
    reviews_db.clear()
    book_reviews_db.clear()

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers(client):
    # Register and login a user to get headers
    user_data = {
        "email": "test@example.com",
        "password": "password123",
        "username": "testuser",
        "fullName": "Test User"
    }
    client.post("/auth/register", json=user_data)
    response = client.post("/auth/login", json={"email": "test@example.com", "password": "password123"})
    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}
