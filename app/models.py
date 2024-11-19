from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Table, Text
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class InviteStatus(enum.Enum):
    PENDING = 'PENDING'  
    ACCEPTED = 'ACCEPTED'
    DECLINED = 'DECLINED'

party_attendees = Table(
    'party_attendees',
    Base.metadata,
    Column("party_id", Integer, ForeignKey("parties.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)

party_invites = Table(
    'party_invites',
    Base.metadata,
    Column("party_id", Integer, ForeignKey("parties.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column('status', SQLAlchemyEnum(InviteStatus), default=InviteStatus.PENDING),
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False, index=True)

    # Relationship for parties created by the user
    created_parties = relationship("Party", back_populates="creator", doc="Parties created by the user.")

    # Relationship for parties the user is attending
    attending_parties = relationship("Party", secondary=party_attendees, back_populates="attendees", doc="Parties the user is attending.")


class Party(Base):
    __tablename__ = "parties"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    platform = Column(String, index=True)
    date_time = Column(DateTime, nullable=False, index=True)
    description = Column(Text)

    # Foreign key to track the creator of the party
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    creator = relationship("User", back_populates="created_parties", doc="The user who created the party.")

    # Relationship for attendees of the party
    attendees = relationship("User", secondary=party_attendees, back_populates="attending_parties", doc="Users attending the party.")

    # Relationship for invites to the party
    invites = relationship("User", secondary=party_invites, doc="Users invited to the party.")