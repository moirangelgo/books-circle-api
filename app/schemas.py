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

    model_config = ConfigDict(from_attributes=True)

class Meeting(BaseModel):
    id: int
    bookId: Optional[str] = Field(None, alias="book_id")
    bookTitle: Optional[str] = Field(None, alias="book_title")
    scheduledAt: datetime = Field(alias="scheduled_at")
    duration: int
    location: Optional[str] = None
    locationUrl: Optional[str] = Field(None, alias="location_url")
    description: Optional[str] = None
    createdBy: Optional[int] = Field(None, alias="created_by")
    attendeeCount: int = Field(0, alias="attendee_count")
    status: str
    isVirtual: bool = Field(False, alias="is_virtual")
    virtualMeetingUrl: Optional[str] = Field(None, alias="virtual_meeting_url")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class MeetingDetail(Meeting):
    attendees: list[dict] = [] 