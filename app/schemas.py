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
    name: str
    description: str

class Config:
    from_attributes = True 