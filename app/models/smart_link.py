"""
Smart Link Model

Represents a trackable smart link embedded in campaign messages.

Design Decisions:
- Short URL generation for WhatsApp messages
- Click tracking with analytics
- Multiple links per campaign support
- Expiration support (optional)

Relationships:
- Many-to-One with Campaign
- One-to-Many with ClickEvent
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
import secrets
from app.database import Base


def generate_short_code(length: int = 8) -> str:
    """Generate a random short code for smart links"""
    return secrets.token_urlsafe(length)[:length]


class SmartLink(Base):
    """
    Smart link model for trackable URLs in campaigns.
    
    Smart links are short URLs that redirect to the actual destination
    while tracking clicks, location, device, etc.
    
    Attributes:
        id: Primary key
        campaign_id: Foreign key to Campaign
        short_code: Unique short code for the link (e.g., "abc123")
        destination_url: Original URL to redirect to
        title: Link title/description
        is_active: Whether link is active
        expires_at: Optional expiration datetime
        click_count: Total number of clicks
        unique_click_count: Number of unique clicks (by IP)
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
    """
    
    __tablename__ = "smart_links"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Campaign relationship
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Short URL
    short_code = Column(String(50), unique=True, nullable=False, index=True, default=generate_short_code)
    
    # Destination
    destination_url = Column(Text, nullable=False)
    title = Column(String(255), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    
    # Analytics
    click_count = Column(Integer, default=0, nullable=False)
    unique_click_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    campaign = relationship("Campaign")
    click_events = relationship("ClickEvent", back_populates="smart_link", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("ix_smart_links_campaign_active", "campaign_id", "is_active"),
    )
    
    def __repr__(self):
        return f"<SmartLink id={self.id} code={self.short_code} clicks={self.click_count}>"
    
    @property
    def is_expired(self) -> bool:
        """Check if link has expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_accessible(self) -> bool:
        """Check if link can be accessed"""
        return self.is_active and not self.is_expired
    
    @property
    def short_url(self) -> str:
        """Get full short URL"""
        from app.config import settings
        return f"{settings.smart_link_base_url}/{self.short_code}"
    
    @property
    def click_through_rate(self) -> float:
        """Calculate CTR (clicks / campaign recipients)"""
        if not self.campaign or self.campaign.total_recipients == 0:
            return 0.0
        return (self.click_count / self.campaign.total_recipients) * 100
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "campaign_id": self.campaign_id,
            "short_code": self.short_code,
            "short_url": self.short_url,
            "destination_url": self.destination_url,
            "title": self.title,
            "is_active": self.is_active,
            "is_expired": self.is_expired,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "click_count": self.click_count,
            "unique_click_count": self.unique_click_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
