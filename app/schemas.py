from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
class UserBase(BaseModel):
    """
    Base schema for user-related data.
    Includes common fields like username and email.
    """
    username: str
    email: EmailStr

class UserCreate(UserBase):
    """
    Schema for creating a new user.
    Extends UserBase with a password field.
    """
    password: str

class UserUpdate(BaseModel):
    """
    Schema for updating user profile details.
    All fields are optional to allow partial updates.
    """
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class User(UserBase):
    """
    Schema representing a user in the system.
    Includes additional fields like user ID and admin status.
    """
    id: int
    is_admin: bool = False

    class Config:
        orm_mode = True

class PartyBase(BaseModel):
    """
    Base schema for party-related data.
    Includes common fields like title, platform, date, and description.
    """
    title: str
    platform: str
    date_time: datetime
    description: str

class PartyCreate(PartyBase):
    """
    Schema for creating a new party.
    Extends PartyBase with invite emails.
    """
    invite_emails: List[EmailStr]

class PartyUpdate(BaseModel):
    """
    Schema for updating party details.
    All fields are optional to allow partial updates.
    """
    title: Optional[str] = None
    platform: Optional[str] = None
    date_time: Optional[datetime] = None
    description: Optional[str] = None

class Party(PartyBase):
    """
    Schema representing a party in the system.
    Includes additional fields like party ID, creator ID, and attendees.
    """
    id: int
    creator_id: int
    attendees: List[User]

    class Config:
        orm_mode = True

class Invite(BaseModel):
    """
    Schema to represent an invitation to a party.
    Includes the party ID and the status of the invitation.
    """
    party_id: int
    status: str  # Could be "pending", "accepted", or "declined"

    class Config:
        orm_mode = True

class Token(BaseModel):
    """
    Schema for authentication token responses.
    Includes the access token and token type.
    """
    access_token: str
    token_type: str