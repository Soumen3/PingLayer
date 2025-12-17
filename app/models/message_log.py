"""
Message Log Model

Tracks individual message sending attempts and status.

Design Decisions:
- One log entry per message sent
- Status tracking (pending, sent, delivered, failed, read)
- WhatsApp message ID tracking
- Error logging
- Delivery timestamp tracking

Relationships:
- Many-to-One with Campaign
- Many-to-One with Recipient
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class MessageStatus(str, enum.Enum):
    """Message delivery status enum"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class MessageLog(Base):
    """
    Message log model for tracking individual message delivery.
    
    Each log entry represents one message sent to one recipient.
    
    Attributes:
        id: Primary key
        campaign_id: Foreign key to Campaign
        recipient_id: Foreign key to Recipient
        phone_number: Recipient phone number (denormalized for quick access)
        status: Message status (pending, sent, delivered, failed, read)
        message_content: Actual message sent (after template rendering)
        whatsapp_message_id: WhatsApp API message ID
        error_message: Error details if failed
        sent_at: When message was sent
        delivered_at: When message was delivered
        read_at: When message was read
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
    """
    
    __tablename__ = "message_logs"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Relationships
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    recipient_id = Column(Integer, ForeignKey("recipients.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Recipient Info (denormalized for performance)
    phone_number = Column(String(20), nullable=False, index=True)
    
    # Status
    status = Column(
        SQLEnum(MessageStatus, name="message_status_enum", create_type=True),
        default=MessageStatus.PENDING,
        nullable=False,
        index=True
    )
    
    # Message Content
    message_content = Column(Text, nullable=False)
    
    # WhatsApp API Response
    whatsapp_message_id = Column(String(255), nullable=True, index=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="message_logs")
    recipient = relationship("Recipient", back_populates="message_logs")
    
    # Indexes for common queries
    __table_args__ = (
        Index("ix_message_logs_campaign_status", "campaign_id", "status"),
        Index("ix_message_logs_created_at", "created_at"),
    )
    
    def __repr__(self):
        return f"<MessageLog id={self.id} phone={self.phone_number} status={self.status}>"
    
    @property
    def is_successful(self) -> bool:
        """Check if message was successfully delivered"""
        return self.status in [MessageStatus.DELIVERED, MessageStatus.READ]
    
    @property
    def is_failed(self) -> bool:
        """Check if message failed"""
        return self.status == MessageStatus.FAILED
    
    @property
    def delivery_time_seconds(self) -> float:
        """Calculate delivery time in seconds"""
        if self.sent_at and self.delivered_at:
            delta = self.delivered_at - self.sent_at
            return delta.total_seconds()
        return 0.0
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "campaign_id": self.campaign_id,
            "recipient_id": self.recipient_id,
            "phone_number": self.phone_number,
            "status": self.status.value if self.status else None,
            "message_content": self.message_content,
            "whatsapp_message_id": self.whatsapp_message_id,
            "error_message": self.error_message,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "delivered_at": self.delivered_at.isoformat() if self.delivered_at else None,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
