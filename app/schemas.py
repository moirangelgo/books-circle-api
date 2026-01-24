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
    book_id: int
    user_id: int
    rating: int
    comment: str  


class ReviewOut(BaseModel):
    id: int
    book_id: int
    user_id: int
    rating: int
    comment: str  

class Config:
    from_attributes = True 