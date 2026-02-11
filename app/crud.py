# app/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from . import models, schemas
from app.core import security
from datetime import datetime

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(models.User).filter(models.User.email == email))
    return result.scalars().first()


async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(models.User).filter(models.User.username == username))
    return result.scalars().first()


async def create_user(db: AsyncSession, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        full_name=user.fullName
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_clubs(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Club).offset(skip).limit(limit))
    return result.scalars().all()


async def create_club(db: AsyncSession, club: schemas.ClubCreate):
    db_club = models.Club(
        name=club.name,
        description=club.description,
        favorite_genre=club.favorite_genre,
        members=club.members
    )
    db.add(db_club)
    await db.commit()
    await db.refresh(db_club)
    return db_club


async def update_club(db: AsyncSession, club: schemas.ClubCreate, club_id: int):
    result = await db.execute(select(models.Club).filter(models.Club.id == club_id))
    db_club = result.scalars().first()
    if not db_club:
        return None
    db_club.name = club.name
    db_club.description = club.description
    db_club.favorite_genre = club.favorite_genre
    db_club.members = club.members
    db.add(db_club)
    await db.commit()
    await db.refresh(db_club)
    return db_club


async def get_club_by_id(db: AsyncSession, club_id: int):
    result = await db.execute(select(models.Club).filter(models.Club.id == club_id))
    return result.scalars().first()


async def delete_club(db: AsyncSession, club_id: int):
    result = await db.execute(select(models.Club).filter(models.Club.id == club_id))
    db_club = result.scalars().first()
    if not db_club:
        return None
    await db.delete(db_club)
    await db.commit()
    return db_club


## BOOKS
async def get_books_by_club_id(db: AsyncSession, club_id: int, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Book).filter(models.Book.club_id == club_id).offset(skip).limit(limit))
    return result.scalars().all()


async def create_book(db: AsyncSession, book: schemas.BookCreate):
    try:
        db_book = models.Book(
            club_id=book.club_id,
            title=book.title,
            author=book.author,
            votes=book.votes,
            progress=book.progress
        )
        db.add(db_book) 
        await db.commit()
        await db.refresh(db_book)
        return db_book

    except Exception as e:
        return None


async def get_book_by_id(db: AsyncSession, book_id: int, club_id: int):
    result = await db.execute(select(models.Book).filter(models.Book.id == book_id, models.Book.club_id == club_id))
    return result.scalars().first()


async def add_votes_by_book_id(db: AsyncSession, book_id: int, club_id: int):
    result = await db.execute(select(models.Book).filter(models.Book.id == book_id, models.Book.club_id == club_id))
    book = result.scalars().first()
    if not book:
        return None
    votes = book.votes
    book.votes = votes + 1
    db.add(book)
    await db.commit()
    await db.refresh(book)
    return book.votes


async def delete_votes_by_book_id(db: AsyncSession, book_id: int, club_id: int):
    result = await db.execute(select(models.Book).filter(models.Book.id == book_id, models.Book.club_id == club_id))
    book = result.scalars().first()
    if not book:
        return None
    votes = book.votes
    book.votes = votes - 1
    db.add(book)
    await db.commit()
    await db.refresh(book)
    return book.votes


#Funcioens faltantes Books 
async def get_book_progress(db: AsyncSession, book_id: int, club_id: int):
    result = await db.execute(select(models.Book).filter(models.Book.id == book_id, models.Book.club_id == club_id))
    book = result.scalars().first()
    if book:
        return book.progress
    return None


async def update_book_progress(db: AsyncSession, book_id: int, club_id: int, progress: int):
    result = await db.execute(select(models.Book).filter(models.Book.id == book_id, models.Book.club_id == club_id))
    book = result.scalars().first()
    if book:
        book.progress = max(0, min(100, progress))
        await db.commit()
        await db.refresh(book)
        return book
    return None



# =========REVIEWS ============
async def get_reviews_by_book_id(db: AsyncSession, book_id: int, club_id: int):
    result = await db.execute(select(models.Review).filter(models.Review.book_id == book_id, models.Review.club_id == club_id))
    return result.scalars().all()


async def create_review(db: AsyncSession, review: schemas.ReviewCreate):
    try:
        db_review = models.Review(
            club_id=review.club_id,
            book_id=review.book_id,
            user_id=review.user_id,
            rating=review.rating,
            comment=review.comment
        )
        db.add(db_review) 
        await db.commit()
        await db.refresh(db_review)
        return db_review

    except Exception as e:
        return None


async def update_review(db: AsyncSession, review: schemas.ReviewUpdate):
    try:
        result = await db.execute(select(models.Review).filter(models.Review.id == review.id, models.Review.club_id == review.club_id, models.Review.book_id == review.book_id))
        db_review = result.scalars().first()
        if not db_review:
            return None

        db_review.rating = review.rating
        db_review.comment = review.comment
        db.add(db_review) 
        await db.commit()
        await db.refresh(db_review)
        return db_review

    except Exception as e:
        return None


async def delete_review(db: AsyncSession, review_id: int):
    try:
        result = await db.execute(select(models.Review).filter(models.Review.id == review_id))
        db_review = result.scalars().first()
        if not db_review:
            return None
        await db.delete(db_review)
        await db.commit()
        return db_review

    except Exception as e:
        return None


# =========MEETINGS ============
async def get_meetings_by_club_id(db: AsyncSession, club_id: int):
    result = await db.execute(select(models.Meeting).filter(models.Meeting.club_id == club_id))
    return result.scalars().all()


async def get_meetings_by_id(db: AsyncSession, meeting_id: int):
    result = await db.execute(select(models.Meeting).filter(models.Meeting.id == meeting_id))
    return result.scalars().first()


async def create_meeting(db: AsyncSession, meeting: schemas.MeetingCreate):
    try:
        scheduled_at = meeting.scheduledAt
        if isinstance(scheduled_at, str):
            try:
                scheduled_at = datetime.fromisoformat(scheduled_at)
            except ValueError:
                pass

        db_meeting = models.Meeting(
            book_id = meeting.bookId,
            club_id = meeting.clubId,
            book_title = meeting.bookTitle,
            scheduled_at = scheduled_at,
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
        await db.commit()
        await db.refresh(db_meeting)
        return db_meeting

    except Exception as e:
        return None
    
# = = = = = Implementación DELETE CLUBS = = = = = 
async def delete_meeting(db: AsyncSession, club_id: int, meeting_id: int):
    try:
        result = await db.execute(select(models.Meeting).filter(
            models.Meeting.id == meeting_id,
            models.Meeting.club_id == club_id
        ))
        db_meeting = result.scalars().first()

        if db_meeting:
            await db.delete(db_meeting)
            await db.commit()
            return db_meeting  # para confirmar
        return None 
    
    except Exception as e:
        return None # En caso no exista

# =========MEETINGS ATTENDANCE============

async def create_attendance_meeting(db: AsyncSession, meeting_id, meeting: schemas.MeetingAttendanceCreate):
    try:
        db_attendance = models.MeetingAttendance(
            meeting_id = meeting_id,
            user_id = meeting.user_id,
            status = meeting.status
        )

        db.add(db_attendance) 
        await db.commit()
        await db.refresh(db_attendance)
        return db_attendance

    except Exception as e:
        return None
