import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app import crud, models, schemas

@pytest.fixture(scope="function")
def db():
    # Setup in-memory DB for testing
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_create_user(db):
    user_in = schemas.UserCreate(
        email="test@example.com",
        username="testuser",
        password="password123",
        fullName="Test User"
    )
    user = crud.create_user(db, user_in)
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert hasattr(user, "id")

def test_get_user_by_email(db):
    user_in = schemas.UserCreate(
        email="test@example.com",
        username="testuser",
        password="password123",
        fullName="Test User"
    )
    crud.create_user(db, user_in)
    user = crud.get_user_by_email(db, email="test@example.com")
    assert user is not None
    assert user.email == "test@example.com"

def test_get_user_by_username(db):
    user_in = schemas.UserCreate(
        email="test@example.com",
        username="testuser",
        password="password123",
        fullName="Test User"
    )
    crud.create_user(db, user_in)
    user = crud.get_user_by_username(db, username="testuser")
    assert user is not None
    assert user.username == "testuser"

def test_create_club(db):
    club_in = schemas.ClubCreate(
        name="Test Club",
        description="A club for testing",
        favorite_genre="Sci-Fi",
        members=10
    )
    club = crud.create_club(db, club_in)
    assert club.name == "Test Club"
    assert club.description == "A club for testing"
    assert club.favorite_genre == "Sci-Fi"
    assert club.members == 10
    assert hasattr(club, "id")

def test_get_clubs(db):
    club_in1 = schemas.ClubCreate(name="Club 1", description="Desc 1")
    club_in2 = schemas.ClubCreate(name="Club 2", description="Desc 2")
    crud.create_club(db, club_in1)
    crud.create_club(db, club_in2)
    clubs = crud.get_clubs(db)
    assert len(clubs) == 2

def test_get_club_by_id(db):
    club_in = schemas.ClubCreate(name="Test Club", description="Desc")
    db_club = crud.create_club(db, club_in)
    club = crud.get_club_by_id(db, club_id=db_club.id)
    assert club is not None
    assert club.name == "Test Club"

def test_update_club(db):
    club_in = schemas.ClubCreate(name="Original Name", description="Original Desc")
    db_club = crud.create_club(db, club_in)

    update_data = schemas.ClubCreate(
        name="Updated Name",
        description="Updated Desc",
        favorite_genre="Fantasy",
        members=20
    )
    updated_club = crud.update_club(db, club=update_data, club_id=db_club.id)
    assert updated_club.name == "Updated Name"
    assert updated_club.description == "Updated Desc"
    assert updated_club.favorite_genre == "Fantasy"
    assert updated_club.members == 20

def test_delete_club(db):
    club_in = schemas.ClubCreate(name="To Delete", description="Desc")
    db_club = crud.create_club(db, club_in)
    deleted_club = crud.delete_club(db, club_id=db_club.id)
    assert deleted_club.id == db_club.id
    assert crud.get_club_by_id(db, club_id=db_club.id) is None

def test_create_book(db):
    club_in = schemas.ClubCreate(name="Club for Book", description="Desc")
    db_club = crud.create_club(db, club_in)

    book_in = schemas.BookCreate(
        club_id=db_club.id,
        title="Test Book",
        author="Test Author",
        votes=0,
        progress=0
    )
    book = crud.create_book(db, book_in)
    assert book.title == "Test Book"
    assert book.club_id == db_club.id
    assert book.author == "Test Author"

def test_get_books_by_club_id(db):
    club_in = schemas.ClubCreate(name="Club for Books", description="Desc")
    db_club = crud.create_club(db, club_in)

    book_in1 = schemas.BookCreate(club_id=db_club.id, title="Book 1", author="Author 1")
    book_in2 = schemas.BookCreate(club_id=db_club.id, title="Book 2", author="Author 2")
    crud.create_book(db, book_in1)
    crud.create_book(db, book_in2)

    books = crud.get_books_by_club_id(db, club_id=db_club.id)
    assert len(books) == 2

def test_get_book_by_id(db):
    club_in = schemas.ClubCreate(name="Club for Book By ID", description="Desc")
    db_club = crud.create_club(db, club_in)
    book_in = schemas.BookCreate(club_id=db_club.id, title="Specific Book", author="Author")
    db_book = crud.create_book(db, book_in)

    book = crud.get_book_by_id(db, book_id=db_book.id, club_id=db_club.id)
    assert book is not None
    assert book.title == "Specific Book"

def test_add_votes_by_book_id(db):
    club_in = schemas.ClubCreate(name="Club for Votes", description="Desc")
    db_club = crud.create_club(db, club_in)
    book_in = schemas.BookCreate(club_id=db_club.id, title="Vote Book", author="Author", votes=0)
    db_book = crud.create_book(db, book_in)

    new_votes = crud.add_votes_by_book_id(db, book_id=db_book.id, club_id=db_club.id)
    assert new_votes == 1
    assert crud.get_book_by_id(db, book_id=db_book.id, club_id=db_club.id).votes == 1

def test_delete_votes_by_book_id(db):
    club_in = schemas.ClubCreate(name="Club for Unvotes", description="Desc")
    db_club = crud.create_club(db, club_in)
    book_in = schemas.BookCreate(club_id=db_club.id, title="Unvote Book", author="Author", votes=5)
    db_book = crud.create_book(db, book_in)

    new_votes = crud.delete_votes_by_book_id(db, book_id=db_book.id, club_id=db_club.id)
    assert new_votes == 4
    assert crud.get_book_by_id(db, book_id=db_book.id, club_id=db_club.id).votes == 4

def test_get_book_progress(db):
    club_in = schemas.ClubCreate(name="Club for Progress", description="Desc")
    db_club = crud.create_club(db, club_in)
    book_in = schemas.BookCreate(club_id=db_club.id, title="Progress Book", author="Author", progress=50)
    db_book = crud.create_book(db, book_in)

    progress = crud.get_book_progress(db, book_id=db_book.id, club_id=db_club.id)
    assert progress == 50

def test_update_book_progress(db):
    club_in = schemas.ClubCreate(name="Club for Update Progress", description="Desc")
    db_club = crud.create_club(db, club_in)
    book_in = schemas.BookCreate(club_id=db_club.id, title="Update Progress Book", author="Author", progress=10)
    db_book = crud.create_book(db, book_in)

    updated_book = crud.update_book_progress(db, book_id=db_book.id, club_id=db_club.id, progress=75)
    assert updated_book.progress == 75

def test_create_review(db):
    user_in = schemas.UserCreate(email="reviewer@example.com", username="reviewer", password="pass", fullName="Reviewer")
    db_user = crud.create_user(db, user_in)
    club_in = schemas.ClubCreate(name="Club for Review", description="Desc")
    db_club = crud.create_club(db, club_in)
    book_in = schemas.BookCreate(club_id=db_club.id, title="Review Book", author="Author")
    db_book = crud.create_book(db, book_in)

    review_in = schemas.ReviewCreate(
        club_id=db_club.id,
        book_id=db_book.id,
        user_id=db_user.id,
        rating=5,
        comment="Great book!"
    )
    review = crud.create_review(db, review_in)
    assert review.rating == 5
    assert review.comment == "Great book!"
    assert review.user_id == db_user.id

def test_get_reviews_by_book_id(db):
    user_in = schemas.UserCreate(email="reviewer2@example.com", username="reviewer2", password="pass", fullName="Reviewer 2")
    db_user = crud.create_user(db, user_in)
    club_in = schemas.ClubCreate(name="Club for Reviews", description="Desc")
    db_club = crud.create_club(db, club_in)
    book_in = schemas.BookCreate(club_id=db_club.id, title="Multi Review Book", author="Author")
    db_book = crud.create_book(db, book_in)

    review_in1 = schemas.ReviewCreate(club_id=db_club.id, book_id=db_book.id, user_id=db_user.id, rating=4, comment="Good")
    review_in2 = schemas.ReviewCreate(club_id=db_club.id, book_id=db_book.id, user_id=db_user.id, rating=5, comment="Better")
    crud.create_review(db, review_in1)
    crud.create_review(db, review_in2)

    reviews = crud.get_reviews_by_book_id(db, book_id=db_book.id, club_id=db_club.id)
    assert len(reviews) == 2

def test_update_review(db):
    user_in = schemas.UserCreate(email="reviewer3@example.com", username="reviewer3", password="pass", fullName="Reviewer 3")
    db_user = crud.create_user(db, user_in)
    club_in = schemas.ClubCreate(name="Club for Update Review", description="Desc")
    db_club = crud.create_club(db, club_in)
    book_in = schemas.BookCreate(club_id=db_club.id, title="Update Review Book", author="Author")
    db_book = crud.create_book(db, book_in)

    review_in = schemas.ReviewCreate(club_id=db_club.id, book_id=db_book.id, user_id=db_user.id, rating=3, comment="Original")
    db_review = crud.create_review(db, review_in)

    update_data = schemas.ReviewUpdate(
        id=db_review.id,
        club_id=db_club.id,
        book_id=db_book.id,
        rating=1,
        comment="Updated"
    )
    updated_review = crud.update_review(db, update_data)
    assert updated_review.rating == 1
    assert updated_review.comment == "Updated"

def test_delete_review(db):
    user_in = schemas.UserCreate(email="reviewer4@example.com", username="reviewer4", password="pass", fullName="Reviewer 4")
    db_user = crud.create_user(db, user_in)
    club_in = schemas.ClubCreate(name="Club for Delete Review", description="Desc")
    db_club = crud.create_club(db, club_in)
    book_in = schemas.BookCreate(club_id=db_club.id, title="Delete Review Book", author="Author")
    db_book = crud.create_book(db, book_in)

    review_in = schemas.ReviewCreate(club_id=db_club.id, book_id=db_book.id, user_id=db_user.id, rating=3, comment="To Delete")
    db_review = crud.create_review(db, review_in)

    deleted_review = crud.delete_review(db, review_id=db_review.id)
    assert deleted_review.id == db_review.id
    assert len(crud.get_reviews_by_book_id(db, book_id=db_book.id, club_id=db_club.id)) == 0

def test_create_meeting(db):
    club_in = schemas.ClubCreate(name="Club for Meeting", description="Desc")
    db_club = crud.create_club(db, club_in)
    book_in = schemas.BookCreate(club_id=db_club.id, title="Meeting Book", author="Author")
    db_book = crud.create_book(db, book_in)

    meeting_in = schemas.MeetingCreate(
        id=1,
        bookId=db_book.id,
        clubId=db_club.id,
        bookTitle="Meeting Book",
        scheduledAt="2023-12-31T23:59:59",
        duration=60,
        location="Online",
        status="Próxima"
    )
    meeting = crud.create_meeting(db, meeting_in)
    assert meeting.book_id == db_book.id
    assert meeting.club_id == db_club.id
    assert meeting.location == "Online"

def test_get_meetings_by_club_id(db):
    club_in = schemas.ClubCreate(name="Club for Meetings", description="Desc")
    db_club = crud.create_club(db, club_in)
    book_in = schemas.BookCreate(club_id=db_club.id, title="Meeting Book", author="Author")
    db_book = crud.create_book(db, book_in)

    meeting_in = schemas.MeetingCreate(id=1, bookId=db_book.id, clubId=db_club.id, location="Here")
    crud.create_meeting(db, meeting_in)

    meetings = crud.get_meetings_by_club_id(db, club_id=db_club.id)
    assert len(meetings) == 1

def test_get_meetings_by_id(db):
    club_in = schemas.ClubCreate(name="Club for Meeting ID", description="Desc")
    db_club = crud.create_club(db, club_in)
    book_in = schemas.BookCreate(club_id=db_club.id, title="Meeting Book", author="Author")
    db_book = crud.create_book(db, book_in)

    meeting_in = schemas.MeetingCreate(id=10, bookId=db_book.id, clubId=db_club.id, location="There")
    db_meeting = crud.create_meeting(db, meeting_in)

    meeting = crud.get_meetings_by_id(db, meeting_id=db_meeting.id)
    assert meeting is not None
    assert meeting.location == "There"

def test_delete_meeting(db):
    club_in = schemas.ClubCreate(name="Club for Delete Meeting", description="Desc")
    db_club = crud.create_club(db, club_in)
    book_in = schemas.BookCreate(club_id=db_club.id, title="Meeting Book", author="Author")
    db_book = crud.create_book(db, book_in)

    meeting_in = schemas.MeetingCreate(id=20, bookId=db_book.id, clubId=db_club.id, location="Gone")
    db_meeting = crud.create_meeting(db, meeting_in)

    deleted_meeting = crud.delete_meeting(db, club_id=db_club.id, meeting_id=db_meeting.id)
    assert deleted_meeting.id == db_meeting.id
    assert crud.get_meetings_by_id(db, meeting_id=db_meeting.id) is None

def test_create_attendance_meeting(db):
    user_in = schemas.UserCreate(email="attendee@example.com", username="attendee", password="pass", fullName="Attendee")
    db_user = crud.create_user(db, user_in)
    club_in = schemas.ClubCreate(name="Club for Attendance", description="Desc")
    db_club = crud.create_club(db, club_in)
    book_in = schemas.BookCreate(club_id=db_club.id, title="Meeting Book", author="Author")
    db_book = crud.create_book(db, book_in)
    meeting_in = schemas.MeetingCreate(id=30, bookId=db_book.id, clubId=db_club.id, location="Place")
    db_meeting = crud.create_meeting(db, meeting_in)

    attendance_in = schemas.MeetingAttendanceCreate(
        user_id=db_user.id,
        status=schemas.AttendanceValue.SI
    )
    attendance = crud.create_attendance_meeting(db, meeting_id=db_meeting.id, meeting=attendance_in)
    assert attendance.meeting_id == db_meeting.id
    assert attendance.user_id == db_user.id
    assert attendance.status == "SI"
