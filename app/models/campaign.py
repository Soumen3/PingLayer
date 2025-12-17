"""
Campaign Model

Represents a WhatsApp campaign.

Design Decisions:
- Campaigns belong to a company (multi-tenant)
- Created by a specific user
- Status tracking (draft, scheduled, sending, completed, failed)
- Template-based messaging
- Scheduled sending support

Relationships:
- Many-to-One with Company
- Many-to-One with User (creator)
- One-to-Many with Recipient
- One-to-Many with MessageLog
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class CampaignStatus(str, enum.Enum):
    """Campaign status enum"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENDING = "sending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Campaign(Base):
    """
    Campaign model for WhatsApp bulk messaging.
    
    A campaign represents a bulk WhatsApp message sent to multiple recipients.
    
    Attributes:
        id: Primary key
        name: Campaign name
        company_id: Foreign key to Company
        created_by: Foreign key to User who created this
        status: Campaign status (draft, scheduled, sending, completed, failed)
        message_template: Message template with placeholders
        scheduled_at: When to send (None = send immediately)
        started_at: When sending actually started
        completed_at: When sending completed
        total_recipients: Total number of recipients
        sent_count: Number of messages sent
        delivered_count: Number of messages delivered
        failed_count: Number of messages failed
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
    """
    
    __tablename__ = "campaigns"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Campaign Info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Multi-tenant
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Status
    status = Column(
        SQLEnum(CampaignStatus, name="campaign_status_enum", create_type=True),
        default=CampaignStatus.DRAFT,
        nullable=False,
        index=True
    )
    
    # Message Content
    message_template = Column(Text, nullable=False)
    # Variables for template (e.g., {name}, {company})
    template_variables = Column(JSON, nullable=True)
    
    # Scheduling
    scheduled_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Statistics
    total_recipients = Column(Integer, default=0, nullable=False)
    sent_count = Column(Integer, default=0, nullable=False)
    delivered_count = Column(Integer, default=0, nullable=False)
    failed_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="campaigns")
    created_by_user = relationship("User", back_populates="campaigns")
    recipients = relationship("Recipient", back_populates="campaign", cascade="all, delete-orphan")
    message_logs = relationship("MessageLog", back_populates="campaign", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Campaign id={self.id} name={self.name} status={self.status} company_id={self.company_id}>"
    
    @property
    def is_editable(self) -> bool:
        """Check if campaign can be edited"""
        return self.status in [CampaignStatus.DRAFT, CampaignStatus.SCHEDULED]
    
    @property
    def is_sendable(self) -> bool:
        """Check if campaign can be sent"""
        return self.status == CampaignStatus.DRAFT and self.total_recipients > 0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate (delivered / sent)"""
        if self.sent_count == 0:
            return 0.0
        return (self.delivered_count / self.sent_count) * 100
    
    @property
    def progress_percentage(self) -> float:
        """Calculate sending progress"""
        if self.total_recipients == 0:
            return 0.0
        return (self.sent_count / self.total_recipients) * 100
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "company_id": self.company_id,
            "created_by": self.created_by,
            "status": self.status.value if self.status else None,
            "message_template": self.message_template,
            "template_variables": self.template_variables,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "total_recipients": self.total_recipients,
            "sent_count": self.sent_count,
            "delivered_count": self.delivered_count,
            "failed_count": self.failed_count,
            "success_rate": self.success_rate,
            "progress_percentage": self.progress_percentage,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
