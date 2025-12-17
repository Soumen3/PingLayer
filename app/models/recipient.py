"""
Recipient Model

Represents a recipient in a campaign.

Design Decisions:
- Recipients are tied to a specific campaign
- Phone number validation
- Custom data per recipient (for template variables)
- Status tracking per recipient

Relationships:
- Many-to-One with Campaign
- One-to-Many with MessageLog
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Recipient(Base):
    """
    Recipient model for campaign recipients.
    
    Each recipient represents a phone number that will receive a campaign message.
    
    Attributes:
        id: Primary key
        campaign_id: Foreign key to Campaign
        phone_number: WhatsApp phone number (E.164 format)
        name: Recipient name (optional)
        custom_data: JSON field for template variables (e.g., {name: "John", company: "Acme"})
        created_at: Timestamp of creation
    """
    
    __tablename__ = "recipients"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Campaign relationship
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Recipient Info
    phone_number = Column(String(20), nullable=False, index=True)  # E.164 format: +1234567890
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    
    # Custom data for template variables
    # Example: {"first_name": "John", "company": "Acme Corp", "discount": "20%"}
    custom_data = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="recipients")
    message_logs = relationship("MessageLog", back_populates="recipient", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        # Prevent duplicate phone numbers in same campaign
        UniqueConstraint("campaign_id", "phone_number", name="uq_recipient_campaign_phone"),
    )
    
    def __repr__(self):
        return f"<Recipient id={self.id} phone={self.phone_number} campaign_id={self.campaign_id}>"
    
    @property
    def formatted_phone(self) -> str:
        """Get formatted phone number for display"""
        # Simple formatting - can be enhanced
        if self.phone_number.startswith("+"):
            return self.phone_number
        return f"+{self.phone_number}"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "campaign_id": self.campaign_id,
            "phone_number": self.phone_number,
            "name": self.name,
            "email": self.email,
            "custom_data": self.custom_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
