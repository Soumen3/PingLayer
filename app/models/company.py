"""
Company Model

Represents a company/tenant in the multi-tenant system.

Design Decisions:
- Each company is a separate tenant
- Company name is globally unique
- Soft delete support via is_active flag
- Subscription/plan tracking for future monetization

Relationships:
- One-to-Many with User
- One-to-Many with Campaign
- One-to-Many with Integration
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Company(Base):
    """
    Company/Tenant model for multi-tenant architecture.
    
    Each company is isolated - users and data belong to one company.
    
    Attributes:
        id: Primary key
        name: Company name (unique)
        slug: URL-friendly identifier
        description: Company description
        is_active: Soft delete flag
        plan: Subscription plan (free, pro, enterprise)
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
    """
    
    __tablename__ = "companies"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Company Info
    name = Column(String(255), unique=True, nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Contact
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Subscription (for future monetization)
    plan = Column(String(50), default="free", nullable=False)  # free, pro, enterprise
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    campaigns = relationship("Campaign", back_populates="company", cascade="all, delete-orphan")
    integrations = relationship("Integration", back_populates="company", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Company id={self.id} name={self.name} plan={self.plan}>"
    
    @property
    def user_count(self) -> int:
        """Get number of users in this company"""
        return len(self.users) if self.users else 0
    
    @property
    def campaign_count(self) -> int:
        """Get number of campaigns for this company"""
        return len(self.campaigns) if self.campaigns else 0
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "email": self.email,
            "phone": self.phone,
            "is_active": self.is_active,
            "plan": self.plan,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
