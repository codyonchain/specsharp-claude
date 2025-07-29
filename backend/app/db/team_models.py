from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

# Association table for team memberships
team_members = Table('team_members', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('team_id', Integer, ForeignKey('teams.id'), primary_key=True),
    Column('role', String, default='member'),  # 'admin' or 'member'
    Column('joined_at', DateTime(timezone=True), server_default=func.now())
)


class Team(Base):
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)  # URL-friendly identifier
    
    # Subscription details
    subscription_status = Column(String, default="trial")  # trial, active, cancelled, expired
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
    subscription_started_at = Column(DateTime(timezone=True), nullable=True)
    subscription_ends_at = Column(DateTime(timezone=True), nullable=True)
    
    # Seat management
    seats_included = Column(Integer, default=3)  # Base plan includes 3 seats
    additional_seats = Column(Integer, default=0)  # Extra seats purchased
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Owner
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    owner = relationship("User", foreign_keys=[owner_id], back_populates="owned_teams")
    members = relationship("User", secondary=team_members, back_populates="teams")
    projects = relationship("Project", back_populates="team")
    invitations = relationship("TeamInvitation", back_populates="team")
    
    @property
    def total_seats(self):
        """Total seats available (base + additional)"""
        return self.seats_included + self.additional_seats
    
    @property
    def seats_used(self):
        """Number of seats currently in use"""
        return len(self.members)
    
    @property
    def seats_available(self):
        """Number of seats still available"""
        return self.total_seats - self.seats_used


class TeamInvitation(Base):
    __tablename__ = "team_invitations"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    email = Column(String, nullable=False, index=True)
    role = Column(String, default='member')  # 'admin' or 'member'
    
    # Invitation details
    token = Column(String, unique=True, index=True, nullable=False)
    invited_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Status tracking
    status = Column(String, default='pending')  # pending, accepted, expired, cancelled
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    # Relationships
    team = relationship("Team", back_populates="invitations")
    invited_by = relationship("User", foreign_keys=[invited_by_id])