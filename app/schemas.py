from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from pydantic.config import ConfigDict

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    fullName: str


class UserOut(BaseModel):
    id: int
    email: str
    username: str
    fullName: Optional[str] = Field(None, alias="full_name")
    createdAt: datetime = Field(alias="created_at")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class ClubCreate(BaseModel):
    """Model for creating a new club (without ID)"""
    name: str
    description: str
    favorite_genre: str | None = None
    members: int = 0


class ClubOut(BaseModel):
    id: int
    name: str
    description: str


class BookCreate(BaseModel):
    club_id: int
    title: str
    author: str
    votes: int = 0
    progress: int = 0  # Porcentaje


class BookOut(BaseModel):
    id: int
    club_id: int
    title: str
    author: str
    votes: int = 0
    progress: int = 0  



class ReviewCreate(BaseModel):
    club_id: int
    book_id: int
    user_id: int
    rating: int
    comment: str  

class ReviewUpdate(BaseModel):
    id: int
    club_id: int
    book_id: int
    rating: int
    comment: str 

class ReviewOut(BaseModel):
    id: int
    club_id: int
    book_id: int
    user_id: int
    rating: int
    comment: str  


class MeetingCreate(BaseModel):
    bookId: int| int = None
    clubId: int| int = None
    bookTitle: str| str = None
    scheduledAt: str | None = None
    duration: int | None = None
    location: str| str = None
    locationUrl: str| str = None
    description: str| str = None
    createdBy: str | None = None
    attendeeCount: int | None = None
    status: str | None = None  # Próxima | Vencida | Cancelada
    isVirtual: bool | None = None
    virtualMeetingUrl: str| str = None


class MeetingUpdate(BaseModel):
    id: str | str = None
    bookId: str| str = None
    bookTitle: str| str = None
    scheduledAt: str | None = None
    duration: int | None = None
    location: str| str = None
    locationUrl: str| str = None
    description: str| str = None
    createdBy: str | None = None
    attendeeCount: int | None = None
    status: str | None = None  # Próxima | Vencida | Cancelada
    isVirtual: bool | None = None
    virtualMeetingUrl: str| str = None


class MeetingOut(BaseModel):
    id: str | str = None
    bookId: str| str = None
    bookTitle: str| str = None
    scheduledAt: str | None = None
    duration: int | None = None
    location: str| str = None
    locationUrl: str| str = None
    description: str| str = None
    createdBy: str | None = None
    attendeeCount: int | None = None
    status: str | None = None  # Próxima | Vencida | Cancelada
    isVirtual: bool | None = None
    virtualMeetingUrl: str| str = None    


class Config:
    from_attributes = True 