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




# CREATE
# ALL
# DETAIL
# UPDATE
# DELETE