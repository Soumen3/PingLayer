"""
User Model

Represents a user in the system.

Design Decisions:
- Users belong to a company (multi-tenant)
- Email is unique per company (not globally unique)
- Password is hashed using bcrypt
- Soft delete support via is_active flag
- Role-based access (is_admin flag)

Relationships:
- Many-to-One with Company
- One-to-Many with Campaign (user creates campaigns)
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    """
    User model for authentication and authorization.
    
    Attributes:
        id: Primary key
        email: User's email (unique per company)
        hashed_password: Bcrypt hashed password
        full_name: User's full name
        company_id: Foreign key to Company
        is_active: Soft delete flag
        is_admin: Admin role flag
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
    """
    
    __tablename__ = "users"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Authentication
    email = Column(String(255), nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile
    full_name = Column(String(255), nullable=False)
    
    # Multi-tenant relationship
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Flags
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="users")
    campaigns = relationship("Campaign", back_populates="created_by_user", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        # Email is unique per company (not globally unique)
        UniqueConstraint("email", "company_id", name="uq_user_email_company"),
    )
    
    def __repr__(self):
        return f"<User id={self.id} email={self.email} company_id={self.company_id}>"
    
    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated (active)"""
        return self.is_active
    
    def to_dict(self):
        """Convert to dictionary (exclude password)"""
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "company_id": self.company_id,
            "is_active": self.is_active,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
