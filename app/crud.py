# app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=user.password,
        full_name=user.fullName
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_clubs(db: Session):
    # SELECT * FROM CLUBES
    return db.query(models.Club).all()


def create_club(db: Session, club: schemas.ClubCreate):
    db_club = models.Club(
        name=club.name,
        description=club.description,
        favorite_genre=club.favorite_genre,
        members=club.members
    )
    db.add(db_club)
    db.commit()
    db.refresh(db_club)
    return db_club


def update_club(db: Session, club: schemas.ClubCreate, club_id: int):
    db_club = db.query(models.Club).filter(models.Club.id == club_id).first()
    if not db_club:
        return None
    db_club.name = club.name
    db_club.description = club.description
    db_club.favorite_genre = club.favorite_genre
    db_club.members = club.members
    db.add(db_club)
    db.commit()
    db.refresh(db_club)
    return db_club


def get_club_by_id(db: Session, club_id: int):
    return db.query(models.Club).filter(models.Club.id == club_id).first()


def delete_club(db: Session, club_id: int):
    db_club = db.query(models.Club).filter(models.Club.id == club_id).first()
    if not db_club:
        return None
    db.delete(db_club)
    db.commit()
    return db_club


## BOOKS
def get_books_by_club_id(db: Session, club_id: int):
    # SELECT * FROM LIBROS WHERE CLUB_ID = club_id
    return db.query(models.Book).filter(models.Book.club_id == club_id).all()


def create_book(db: Session, book: schemas.BookCreate):
    try:
        db_book = models.Book(
            club_id=book.club_id,
            title=book.title,
            author=book.author,
            votes=book.votes,
            progress=book.progress
        )
        db.add(db_book) 
        db.commit()
        db.refresh(db_book)
        return db_book

    except Exception as e:
        return None


def get_book_by_id(db: Session, book_id: int, club_id: int):
    return db.query(models.Book).filter(models.Book.id == book_id, models.Book.club_id == club_id).first()


def add_votes_by_book_id(db: Session, book_id: int, club_id: int):
    book = db.query(models.Book).filter(models.Book.id == book_id, models.Book.club_id == club_id).first()
    votes = book.votes
    book.votes = votes + 1
    db.add(book)
    db.commit()
    db.refresh(book)
    return book.votes


def delete_votes_by_book_id(db: Session, book_id: int, club_id: int):
    book = db.query(models.Book).filter(models.Book.id == book_id, models.Book.club_id == club_id).first()
    votes = book.votes
    book.votes = votes - 1
    db.add(book)
    db.commit()
    db.refresh(book)
    return book.votes

#Funcioens faltantes Books 
def get_book_progress(db: Session, book_id: int, club_id: int):
    book = db.query(models.Book).filter(models.Book.id == book_id, models.Book.club_id == club_id).first()
    if book:
        return book.progress
    return None

def update_book_progress(db: Session, book_id: int, club_id: int, progress: int):
    book = db.query(models.Book).filter(models.Book.id == book_id, models.Book.club_id == club_id).first()
    if book:
        book.progress = max(0, min(100, progress))
        db.commit()
        db.refresh(book)
        return book
    return None



# =========REVIEWS ============
def get_reviews_by_book_id(db: Session, book_id: int, club_id: int):
    return db.query(models.Review).filter(models.Review.book_id == book_id, models.Review.club_id == club_id).all()


def create_review(db: Session, review: schemas.ReviewCreate):
    try:
        db_review = models.Review(
            club_id=review.club_id,
            book_id=review.book_id,
            user_id=review.user_id,
            rating=review.rating,
            comment=review.comment
        )
        db.add(db_review) 
        db.commit()
        db.refresh(db_review)
        return db_review

    except Exception as e:
        return None


def update_review(db: Session, review: schemas.ReviewUpdate):
    try:
        db_review = db.query(models.Review).filter(models.Review.id == review.id, models.Review.club_id == review.club_id, models.Review.book_id == review.book_id).first()
        if not db_review:
            return None

        db_review.rating = review.rating
        db_review.comment = review.comment
        db.add(db_review) 
        db.commit()
        db.refresh(db_review)
        return db_review

    except Exception as e:
        return None


def delete_review(db: Session, review_id: int):
    try:
        db_review = db.query(models.Review).filter(models.Review.id == review_id).first()
        if not db_review:
            return None
        db.delete(db_review)
        db.commit()
        return db_review

    except Exception as e:
        return None

# =========MEETINGS ============
def get_meetings_by_club_id(db: Session, club_id: int):
    return db.query(models.Meeting).filter(models.Meeting.club_id == club_id).all()


def get_meetings_by_id(db: Session, meeting_id: int):
    return db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()


def create_meeting(db: Session, meeting: schemas.MeetingCreate):
    try:
        db_meeting = models.Meeting(
            id = meeting.id,
            book_id = meeting.bookId,
            club_id = meeting.clubId,
            book_title = meeting.bookTitle,
            scheduled_at = meeting.scheduledAt,
            duration = meeting.duration,
            location = meeting.location,
            locationUrl = meeting.locationUrl,
            description = meeting.description,
            createdBy = meeting.createdBy,
            attendeeCount = meeting.attendeeCount,
            status = meeting.status,
            isVirtual = meeting.isVirtual,
            virtualMeetingUrl  = meeting.virtualMeetingUrl,
        )
        db.add(db_meeting) 
        db.commit()
        db.refresh(db_meeting)
        return db_meeting

    except Exception as e:
        return None


