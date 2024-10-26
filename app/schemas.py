from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class User(UserBase):
    id: int
    
    class Config:
        orm_mode = True

class PartyBase(BaseModel):
    title: str
    platform: str
    date_time: datetime
    description: str

class PartyCreate(PartyBase):
    invite_emails: List[EmailStr]

class PartyUpdate(BaseModel):
    title: Optional[str] = None
    platform: Optional[str] = None
    date_time: Optional[datetime] = None
    description: Optional[str] = None

class Party(PartyBase):
    id: int
    creator_id: int
    attendees: List[User]
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str