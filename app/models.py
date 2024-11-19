from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Table
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from app.database import Base
import datetime
import enum

class InviteStatus(enum.Enum):
    PENDING = 'PENDING'  
    ACCEPTED = 'ACCEPTED'
    DECLINED = 'DECLINED'

party_attendees = Table(
    'party_attendees',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('party_id', Integer, ForeignKey('parties.id'))
)

party_invites = Table(
    'party_invites',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('party_id', Integer, ForeignKey('parties.id')),
    Column('status', SQLAlchemyEnum(InviteStatus), default=InviteStatus.PENDING),
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_parties = relationship("Party", back_populates="creator")
    attending_parties = relationship("Party", secondary=party_attendees, back_populates="attendees")
    is_admin = Column(Boolean, default=False) 

class Party(Base):
    __tablename__ = "parties"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    platform = Column(String)
    date_time = Column(DateTime)
    description = Column(String)
    creator_id = Column(Integer, ForeignKey("users.id"))
    creator = relationship("User", back_populates="created_parties")
    attendees = relationship("User", secondary=party_attendees, back_populates="attending_parties")
