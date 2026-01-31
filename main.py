from fastapi import FastAPI, HTTPException, status, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timedelta, timezone
from typing import Optional, List
import uuid
import secrets

# Inicializar la aplicación FastAPI
app = FastAPI(
    title="BookCircle API",
    description="API REST para la gestión de clubes de lectura",
    version="1.0.0"
)

security = HTTPBearer()

# ============= MODELOS (Schemas) =============

# --- Auth ---
class RegisterInput(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    username: str = Field(..., min_length=3, max_length=30)
    fullName: str = Field(..., min_length=2, max_length=100)

class LoginInput(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: str
    email: EmailStr
    username: str
    fullName: str
    avatarUrl: Optional[str] = None
    createdAt: datetime

# --- Clubs ---
class ClubInput(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    theme: str
    isPrivate: bool = False

class Club(BaseModel):
    id: str
    name: str
    description: str
    theme: str
    isPrivate: bool
    memberCount: int = 0
    createdBy: str
    createdAt: datetime

# --- Members ---
class Member(BaseModel):
    userId: str
    username: str
    fullName: str
    role: str # admin | member
    joinedAt: datetime
    booksRead: int = 0

# --- Books ---
class BookInput(BaseModel):
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    isbn: Optional[str] = None
    description: Optional[str] = None
    coverUrl: Optional[str] = None
    totalPages: Optional[int] = None

class Book(BaseModel):
    id: str
    title: str
    author: str
    isbn: Optional[str] = None
    description: Optional[str] = None
    coverUrl: Optional[str] = None
    status: str = "proposed" # proposed | reading | completed
    proposedBy: str
    proposedAt: datetime
    votes: int = 0
    startedAt: Optional[datetime] = None
    completedAt: Optional[datetime] = None
    totalPages: Optional[int] = None

class ReadingProgressInput(BaseModel):
    currentPage: int = Field(..., ge=0)
    status: str = "reading" # not-started | reading | completed

class ReadingProgress(BaseModel):
    userId: str
    bookId: str
    currentPage: int
    totalPages: int
    percentage: float
    lastUpdated: datetime
    status: str

# --- Meetings ---
class MeetingInput(BaseModel):
    bookId: Optional[str] = None
    scheduledAt: datetime
    duration: int = Field(..., ge=15, le=480)
    location: Optional[str] = None
    locationUrl: Optional[str] = None
    description: Optional[str] = None
    isVirtual: bool = False
    virtualMeetingUrl: Optional[str] = None

class Meeting(BaseModel):
    id: str
    bookId: Optional[str] = None
    bookTitle: Optional[str] = None
    scheduledAt: datetime
    duration: int
    location: Optional[str] = None
    locationUrl: Optional[str] = None
    description: Optional[str] = None
    createdBy: str
    attendeeCount: int = 0
    status: str = "upcoming" # upcoming | past | cancelled
    isVirtual: bool = False
    virtualMeetingUrl: Optional[str] = None

class AttendanceInput(BaseModel):
    status: str # attending | not-attending | maybe
    note: Optional[str] = None

class Attendance(BaseModel):
    userId: str
    meetingId: str
    status: str
    note: Optional[str] = None
    updatedAt: datetime

# --- Reviews ---
class ReviewInput(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    title: str = Field(..., min_length=3, max_length=100)
    content: str = Field(..., min_length=50, max_length=2000)

class Review(BaseModel):
    id: str
    userId: str
    username: str
    rating: int
    title: str
    content: str
    createdAt: datetime
    updatedAt: Optional[datetime] = None
    likesCount: int = 0

# --- Pagination ---
class PaginationMeta(BaseModel):
    total: int
    limit: int
    offset: int
    hasMore: bool

class ClubsResponse(BaseModel):
    data: List[Club]
    meta: PaginationMeta

class MembersResponse(BaseModel):
    data: List[Member]
    meta: PaginationMeta

class BooksResponse(BaseModel):
    data: List[Book]
    meta: PaginationMeta

class MeetingsResponse(BaseModel):
    data: List[Meeting]
    meta: PaginationMeta

class ReviewsResponse(BaseModel):
    data: List[Review]
    meta: PaginationMeta

# ============= BASE DE DATOS EN MEMORIA =============

users_db: dict[str, dict] = {}
tokens_db: dict[str, dict] = {}
clubs_db: dict[str, dict] = {}
members_db: dict[str, list[dict]] = {} # clubId -> list of members
books_db: dict[str, dict] = {} # bookId -> book
club_books_db: dict[str, list[str]] = {} # clubId -> list of bookIds
book_votes_db: dict[str, set[str]] = {} # bookId -> set of userIds
reading_progress_db: dict[str, dict] = {} # (userId, bookId) -> progress
meetings_db: dict[str, dict] = {} # meetingId -> meeting
club_meetings_db: dict[str, list[str]] = {} # clubId -> list of meetingIds
meeting_attendance_db: dict[str, dict] = {} # (userId, meetingId) -> attendance
reviews_db: dict[str, dict] = {} # reviewId -> review
book_reviews_db: dict[str, list[str]] = {} # bookId -> list of reviewIds

# ============= UTILIDADES =============

def generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def get_current_user(auth: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = auth.credentials
    if token not in tokens_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticación inválido o expirado",
        )
    token_data = tokens_db[token]
    if token_data["expires_at"] < datetime.now(timezone.utc):
        del tokens_db[token]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticación inválido o expirado",
        )
    user_id = token_data["user_id"]
    return users_db[user_id]

# ============= ENDPOINTS AUTH =============

@app.post("/auth/register", tags=["Auth"], status_code=status.HTTP_201_CREATED)
def register_user(payload: RegisterInput):
    for u in users_db.values():
        if u["email"] == payload.email or u["username"] == payload.username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El email o username ya está registrado",
            )

    user_id = generate_id("usr")
    now = datetime.now(timezone.utc)
    user_record = {
        "id": user_id,
        "email": payload.email,
        "username": payload.username,
        "fullName": payload.fullName,
        "avatarUrl": None,
        "createdAt": now,
        "password": payload.password,
    }
    users_db[user_id] = user_record

    token = secrets.token_urlsafe(32)
    tokens_db[token] = {
        "user_id": user_id,
        "expires_at": now + timedelta(days=1),
    }

    return {
        "user": User(**user_record),
        "token": token,
    }

@app.post("/auth/login", tags=["Auth"])
def login_user(payload: LoginInput):
    user = None
    for u in users_db.values():
        if u["email"] == payload.email:
            user = u
            break

    if user is None or user["password"] != payload.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    token = secrets.token_urlsafe(32)
    expires_in = 86400
    tokens_db[token] = {
        "user_id": user["id"],
        "expires_at": datetime.now(timezone.utc) + timedelta(seconds=expires_in),
    }

    return {
        "user": User(**user),
        "token": token,
        "expiresIn": expires_in,
    }

# ============= ENDPOINTS CLUBS =============

@app.get("/clubs", response_model=ClubsResponse, tags=["Clubs"])
def list_clubs(
    limit: int = 20,
    offset: int = 0,
    theme: Optional[str] = None,
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    all_clubs = list(clubs_db.values())
    if theme:
        all_clubs = [c for c in all_clubs if c["theme"] == theme]
    if search:
        search = search.lower()
        all_clubs = [c for c in all_clubs if search in c["name"].lower() or search in c["description"].lower()]

    paged_clubs = all_clubs[offset : offset + limit]
    return {
        "data": [Club(**c) for c in paged_clubs],
        "meta": {
            "total": len(all_clubs),
            "limit": limit,
            "offset": offset,
            "hasMore": len(all_clubs) > offset + limit
        }
    }

@app.post("/clubs", response_model=Club, status_code=status.HTTP_201_CREATED, tags=["Clubs"])
def create_club(payload: ClubInput, current_user: dict = Depends(get_current_user)):
    club_id = generate_id("clb")
    now = datetime.now(timezone.utc)
    club_record = {
        "id": club_id,
        "name": payload.name,
        "description": payload.description,
        "theme": payload.theme,
        "isPrivate": payload.isPrivate,
        "memberCount": 1,
        "createdBy": current_user["id"],
        "createdAt": now
    }
    clubs_db[club_id] = club_record

    # Add creator as admin member
    member_record = {
        "userId": current_user["id"],
        "username": current_user["username"],
        "fullName": current_user["fullName"],
        "role": "admin",
        "joinedAt": now,
        "booksRead": 0
    }
    members_db[club_id] = [member_record]

    return Club(**club_record)

@app.get("/clubs/{clubId}", tags=["Clubs"])
def get_club_by_id(clubId: str, current_user: dict = Depends(get_current_user)):
    if clubId not in clubs_db:
        raise HTTPException(status_code=404, detail="Club no encontrado")
    return clubs_db[clubId] # Simplify, match Swagger's ClubDetail would need more info

@app.put("/clubs/{clubId}", response_model=Club, tags=["Clubs"])
def update_club(clubId: str, payload: ClubInput, current_user: dict = Depends(get_current_user)):
    if clubId not in clubs_db:
        raise HTTPException(status_code=404, detail="Club no encontrado")

    club = clubs_db[clubId]
    if club["createdBy"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para editar este club")

    club.update({
        "name": payload.name,
        "description": payload.description,
        "theme": payload.theme,
        "isPrivate": payload.isPrivate
    })
    return Club(**club)

@app.delete("/clubs/{clubId}", status_code=status.HTTP_204_NO_CONTENT, tags=["Clubs"])
def delete_club(clubId: str, current_user: dict = Depends(get_current_user)):
    if clubId not in clubs_db:
        raise HTTPException(status_code=404, detail="Club no encontrado")

    club = clubs_db[clubId]
    if club["createdBy"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para eliminar este club")

    del clubs_db[clubId]
    if clubId in members_db: del members_db[clubId]
    return

# ============= ENDPOINTS MEMBERS =============

@app.get("/clubs/{clubId}/members", response_model=MembersResponse, tags=["Members"])
def list_club_members(clubId: str, current_user: dict = Depends(get_current_user)):
    if clubId not in clubs_db:
        raise HTTPException(status_code=404, detail="Club no encontrado")
    members = members_db.get(clubId, [])
    return {
        "data": members,
        "meta": {"total": len(members), "limit": 20, "offset": 0, "hasMore": False}
    }

@app.post("/clubs/{clubId}/members", status_code=status.HTTP_201_CREATED, tags=["Members"])
def join_club(clubId: str, current_user: dict = Depends(get_current_user)):
    if clubId not in clubs_db:
        raise HTTPException(status_code=404, detail="Club no encontrado")

    members = members_db.get(clubId, [])
    if any(m["userId"] == current_user["id"] for m in members):
        raise HTTPException(status_code=409, detail="El usuario ya es miembro del club")

    new_member = {
        "userId": current_user["id"],
        "username": current_user["username"],
        "fullName": current_user["fullName"],
        "role": "member",
        "joinedAt": datetime.now(timezone.utc),
        "booksRead": 0
    }
    members.append(new_member)
    members_db[clubId] = members
    clubs_db[clubId]["memberCount"] = len(members)
    
    return new_member

@app.delete("/clubs/{clubId}/members/{userId}", status_code=status.HTTP_204_NO_CONTENT, tags=["Members"])
def leave_club(clubId: str, userId: str, current_user: dict = Depends(get_current_user)):
    if clubId not in clubs_db:
        raise HTTPException(status_code=404, detail="Club no encontrado")

    members = members_db.get(clubId, [])
    # Check if current user is either the one leaving or an admin
    is_admin = any(m["userId"] == current_user["id"] and m["role"] == "admin" for m in members)
    if current_user["id"] != userId and not is_admin:
        raise HTTPException(status_code=403, detail="No tienes permisos para remover a este miembro")

    new_members = [m for m in members if m["userId"] != userId]
    if len(new_members) == len(members):
        raise HTTPException(status_code=404, detail="Miembro no encontrado")

    members_db[clubId] = new_members
    clubs_db[clubId]["memberCount"] = len(new_members)
    return

# ============= ENDPOINTS BOOKS =============

@app.get("/clubs/{clubId}/books", response_model=BooksResponse, tags=["Books"])
def list_club_books(clubId: str, status: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    if clubId not in clubs_db:
        raise HTTPException(status_code=404, detail="Club no encontrado")

    book_ids = club_books_db.get(clubId, [])
    books = [books_db[bid] for bid in book_ids]
    if status:
        books = [b for b in books if b["status"] == status]

    return {
        "data": books,
        "meta": {"total": len(books), "limit": 20, "offset": 0, "hasMore": False}
    }

@app.post("/clubs/{clubId}/books", status_code=status.HTTP_201_CREATED, tags=["Books"])
def propose_book(clubId: str, payload: BookInput, current_user: dict = Depends(get_current_user)):
    if clubId not in clubs_db:
        raise HTTPException(status_code=404, detail="Club no encontrado")

    book_id = generate_id("bk")
    book_record = {
        "id": book_id,
        "title": payload.title,
        "author": payload.author,
        "isbn": payload.isbn,
        "description": payload.description,
        "coverUrl": payload.coverUrl,
        "status": "proposed",
        "proposedBy": current_user["id"],
        "proposedAt": datetime.now(timezone.utc),
        "votes": 1,
        "totalPages": payload.totalPages
    }
    books_db[book_id] = book_record

    if clubId not in club_books_db: club_books_db[clubId] = []
    club_books_db[clubId].append(book_id)

    # Auto-vote by proposer
    book_votes_db[book_id] = {current_user["id"]}

    return book_record

@app.get("/clubs/{clubId}/books/{bookId}", tags=["Books"])
def get_book_by_id(clubId: str, bookId: str, current_user: dict = Depends(get_current_user)):
    if bookId not in books_db:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return books_db[bookId]

@app.post("/clubs/{clubId}/books/{bookId}/votes", status_code=status.HTTP_201_CREATED, tags=["Books"])
def vote_for_book(clubId: str, bookId: str, current_user: dict = Depends(get_current_user)):
    if bookId not in books_db:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    votes = book_votes_db.get(bookId, set())
    if current_user["id"] in votes:
        raise HTTPException(status_code=409, detail="El usuario ya votó por este libro")

    votes.add(current_user["id"])
    book_votes_db[bookId] = votes
    books_db[bookId]["votes"] = len(votes)

    return {"bookId": bookId, "userId": current_user["id"], "votedAt": datetime.now(timezone.utc), "totalVotes": len(votes)}

@app.delete("/clubs/{clubId}/books/{bookId}/votes", status_code=status.HTTP_204_NO_CONTENT, tags=["Books"])
def remove_vote(clubId: str, bookId: str, current_user: dict = Depends(get_current_user)):
    if bookId not in books_db:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    votes = book_votes_db.get(bookId, set())
    if current_user["id"] not in votes:
        raise HTTPException(status_code=404, detail="Voto no encontrado")

    votes.remove(current_user["id"])
    book_votes_db[bookId] = votes
    books_db[bookId]["votes"] = len(votes)
    return

@app.get("/clubs/{clubId}/books/{bookId}/progress", tags=["Books"])
def get_reading_progress(clubId: str, bookId: str, current_user: dict = Depends(get_current_user)):
    progress_key = (current_user["id"], bookId)
    if progress_key not in reading_progress_db:
        raise HTTPException(status_code=404, detail="Progreso no encontrado")
    return reading_progress_db[progress_key]

@app.put("/clubs/{clubId}/books/{bookId}/progress", tags=["Books"])
def update_reading_progress(clubId: str, bookId: str, payload: ReadingProgressInput, current_user: dict = Depends(get_current_user)):
    if bookId not in books_db:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    book = books_db[bookId]
    total_pages = book.get("totalPages") or 100 # Default if unknown

    percentage = (payload.currentPage / total_pages) * 100

    progress_record = {
        "userId": current_user["id"],
        "bookId": bookId,
        "currentPage": payload.currentPage,
        "totalPages": total_pages,
        "percentage": min(percentage, 100.0),
        "lastUpdated": datetime.now(timezone.utc),
        "status": payload.status
    }
    reading_progress_db[(current_user["id"], bookId)] = progress_record
    return progress_record

# ============= ENDPOINTS MEETINGS =============

@app.get("/clubs/{clubId}/meetings", response_model=MeetingsResponse, tags=["Meetings"])
def list_meetings(clubId: str, status: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    if clubId not in clubs_db:
        raise HTTPException(status_code=404, detail="Club no encontrado")

    meeting_ids = club_meetings_db.get(clubId, [])
    meetings = [meetings_db[mid] for mid in meeting_ids]
    if status:
        meetings = [m for m in meetings if m["status"] == status]

    return {
        "data": meetings,
        "meta": {"total": len(meetings), "limit": 20, "offset": 0, "hasMore": False}
    }

@app.post("/clubs/{clubId}/meetings", status_code=status.HTTP_201_CREATED, tags=["Meetings"])
def create_meeting(clubId: str, payload: MeetingInput, current_user: dict = Depends(get_current_user)):
    if clubId not in clubs_db:
        raise HTTPException(status_code=404, detail="Club no encontrado")

    meeting_id = generate_id("mtg")
    book_title = None
    if payload.bookId and payload.bookId in books_db:
        book_title = books_db[payload.bookId]["title"]

    meeting_record = {
        "id": meeting_id,
        "bookId": payload.bookId,
        "bookTitle": book_title,
        "scheduledAt": payload.scheduledAt,
        "duration": payload.duration,
        "location": payload.location,
        "locationUrl": payload.locationUrl,
        "description": payload.description,
        "createdBy": current_user["id"],
        "attendeeCount": 0,
        "status": "upcoming",
        "isVirtual": payload.isVirtual,
        "virtualMeetingUrl": payload.virtualMeetingUrl
    }
    meetings_db[meeting_id] = meeting_record

    if clubId not in club_meetings_db: club_meetings_db[clubId] = []
    club_meetings_db[clubId].append(meeting_id)

    return meeting_record

@app.get("/clubs/{clubId}/meetings/{meetingId}", tags=["Meetings"])
def get_meeting_by_id(clubId: str, meetingId: str, current_user: dict = Depends(get_current_user)):
    if meetingId not in meetings_db:
        raise HTTPException(status_code=404, detail="Reunión no encontrada")
    return meetings_db[meetingId]

@app.put("/clubs/{clubId}/meetings/{meetingId}", tags=["Meetings"])
def update_meeting(clubId: str, meetingId: str, payload: MeetingInput, current_user: dict = Depends(get_current_user)):
    if meetingId not in meetings_db:
        raise HTTPException(status_code=404, detail="Reunión no encontrada")

    meeting = meetings_db[meetingId]
    if meeting["createdBy"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para editar esta reunión")

    book_title = meeting["bookTitle"]
    if payload.bookId and payload.bookId != meeting["bookId"] and payload.bookId in books_db:
        book_title = books_db[payload.bookId]["title"]

    meeting.update({
        "bookId": payload.bookId,
        "bookTitle": book_title,
        "scheduledAt": payload.scheduledAt,
        "duration": payload.duration,
        "location": payload.location,
        "locationUrl": payload.locationUrl,
        "description": payload.description,
        "isVirtual": payload.isVirtual,
        "virtualMeetingUrl": payload.virtualMeetingUrl
    })
    return meeting

@app.delete("/clubs/{clubId}/meetings/{meetingId}", status_code=status.HTTP_204_NO_CONTENT, tags=["Meetings"])
def cancel_meeting(clubId: str, meetingId: str, current_user: dict = Depends(get_current_user)):
    if meetingId not in meetings_db:
        raise HTTPException(status_code=404, detail="Reunión no encontrada")
    
    meeting = meetings_db[meetingId]
    if meeting["createdBy"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para cancelar esta reunión")

    meeting["status"] = "cancelled"
    return

@app.put("/clubs/{clubId}/meetings/{meetingId}/attendance", tags=["Meetings"])
def update_attendance(clubId: str, meetingId: str, payload: AttendanceInput, current_user: dict = Depends(get_current_user)):
    if meetingId not in meetings_db:
        raise HTTPException(status_code=404, detail="Reunión no encontrada")

    attendance_key = (current_user["id"], meetingId)
    old_status = None
    if attendance_key in meeting_attendance_db:
        old_status = meeting_attendance_db[attendance_key]["status"]

    attendance_record = {
        "userId": current_user["id"],
        "meetingId": meetingId,
        "status": payload.status,
        "note": payload.note,
        "updatedAt": datetime.now(timezone.utc)
    }
    meeting_attendance_db[attendance_key] = attendance_record

    # Update attendeeCount based on transitions
    if payload.status == "attending" and old_status != "attending":
        meetings_db[meetingId]["attendeeCount"] += 1
    elif payload.status != "attending" and old_status == "attending":
        meetings_db[meetingId]["attendeeCount"] -= 1

    return attendance_record

# ============= ENDPOINTS REVIEWS =============

@app.get("/clubs/{clubId}/books/{bookId}/reviews", response_model=ReviewsResponse, tags=["Reviews"])
def list_reviews(clubId: str, bookId: str, current_user: dict = Depends(get_current_user)):
    review_ids = book_reviews_db.get(bookId, [])
    reviews = [reviews_db[rid] for rid in review_ids]
    return {
        "data": reviews,
        "meta": {"total": len(reviews), "limit": 20, "offset": 0, "hasMore": False}
    }

@app.post("/clubs/{clubId}/books/{bookId}/reviews", status_code=status.HTTP_201_CREATED, tags=["Reviews"])
def create_review(clubId: str, bookId: str, payload: ReviewInput, current_user: dict = Depends(get_current_user)):
    if bookId not in books_db:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    review_ids = book_reviews_db.get(bookId, [])
    if any(reviews_db[rid]["userId"] == current_user["id"] for rid in review_ids):
        raise HTTPException(status_code=409, detail="El usuario ya tiene una reseña para este libro")

    review_id = generate_id("rev")
    review_record = {
        "id": review_id,
        "userId": current_user["id"],
        "username": current_user["username"],
        "rating": payload.rating,
        "title": payload.title,
        "content": payload.content,
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": None,
        "likesCount": 0
    }
    reviews_db[review_id] = review_record

    if bookId not in book_reviews_db: book_reviews_db[bookId] = []
    book_reviews_db[bookId].append(review_id)

    return review_record

@app.put("/clubs/{clubId}/books/{bookId}/reviews/{reviewId}", tags=["Reviews"])
def update_review(clubId: str, bookId: str, reviewId: str, payload: ReviewInput, current_user: dict = Depends(get_current_user)):
    if reviewId not in reviews_db:
        raise HTTPException(status_code=404, detail="Reseña no encontrada")

    review = reviews_db[reviewId]
    if review["userId"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para editar esta reseña")

    review.update({
        "rating": payload.rating,
        "title": payload.title,
        "content": payload.content,
        "updatedAt": datetime.now(timezone.utc)
    })
    return review

@app.delete("/clubs/{clubId}/books/{bookId}/reviews/{reviewId}", status_code=status.HTTP_204_NO_CONTENT, tags=["Reviews"])
def delete_review(clubId: str, bookId: str, reviewId: str, current_user: dict = Depends(get_current_user)):
    if reviewId not in reviews_db:
        raise HTTPException(status_code=404, detail="Reseña no encontrada")

    review = reviews_db[reviewId]
    if review["userId"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para eliminar esta reseña")

    del reviews_db[reviewId]
    if bookId in book_reviews_db:
        book_reviews_db[bookId] = [rid for rid in book_reviews_db[bookId] if rid != reviewId]
    return

@app.get("/")
def root():
    return {"mensaje": "Bienvenido a la API de Clubes de Lectura", "documentacion": "/docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
