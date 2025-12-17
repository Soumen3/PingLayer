"""
Click Event Model

Tracks individual clicks on smart links with analytics data.

Design Decisions:
- One event per click
- IP-based unique visitor tracking
- User agent parsing for device/browser info
- GeoIP for location tracking
- Referrer tracking

Relationships:
- Many-to-One with SmartLink
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base


class ClickEvent(Base):
    """
    Click event model for smart link analytics.
    
    Each click on a smart link creates one event with analytics data.
    
    Attributes:
        id: Primary key
        smart_link_id: Foreign key to SmartLink
        ip_address: Visitor IP address (for unique tracking)
        user_agent: Browser user agent string
        device_type: Device type (mobile, desktop, tablet)
        browser: Browser name
        os: Operating system
        country: Country code (from GeoIP)
        city: City name (from GeoIP)
        referrer: HTTP referrer
        clicked_at: Timestamp of click
    """
    
    __tablename__ = "click_events"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Smart link relationship
    smart_link_id = Column(Integer, ForeignKey("smart_links.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Visitor Info
    ip_address = Column(String(45), nullable=True, index=True)  # IPv6 max length
    user_agent = Column(String(500), nullable=True)
    
    # Device Info (parsed from user agent)
    device_type = Column(String(50), nullable=True)  # mobile, desktop, tablet
    browser = Column(String(100), nullable=True)
    os = Column(String(100), nullable=True)
    
    # Location Info (from GeoIP)
    country = Column(String(2), nullable=True)  # ISO country code
    city = Column(String(255), nullable=True)
    
    # Referrer
    referrer = Column(String(500), nullable=True)
    
    # Timestamp
    clicked_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    smart_link = relationship("SmartLink", back_populates="click_events")
    
    # Indexes for analytics queries
    __table_args__ = (
        Index("ix_click_events_link_clicked", "smart_link_id", "clicked_at"),
        Index("ix_click_events_country", "country"),
        Index("ix_click_events_device", "device_type"),
    )
    
    def __repr__(self):
        return f"<ClickEvent id={self.id} link_id={self.smart_link_id} ip={self.ip_address}>"
    
    @property
    def is_mobile(self) -> bool:
        """Check if click was from mobile device"""
        return self.device_type == "mobile"
    
    @property
    def is_desktop(self) -> bool:
        """Check if click was from desktop"""
        return self.device_type == "desktop"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "smart_link_id": self.smart_link_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "device_type": self.device_type,
            "browser": self.browser,
            "os": self.os,
            "country": self.country,
            "city": self.city,
            "referrer": self.referrer,
            "clicked_at": self.clicked_at.isoformat() if self.clicked_at else None,
        }
