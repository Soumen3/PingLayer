"""
Integration Model

Stores WhatsApp Business API credentials and configuration.

Design Decisions:
- One integration per company (for now)
- Encrypted API credentials
- Connection status tracking
- Support for multiple providers (WhatsApp, future: Telegram, SMS)

Relationships:
- Many-to-One with Company
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class IntegrationType(str, enum.Enum):
    """Integration type enum"""
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    SMS = "sms"


class IntegrationStatus(str, enum.Enum):
    """Integration status enum"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


class Integration(Base):
    """
    Integration model for third-party API connections.
    
    Stores credentials and configuration for WhatsApp Business API
    and other messaging platforms.
    
    Attributes:
        id: Primary key
        company_id: Foreign key to Company
        type: Integration type (whatsapp, telegram, sms)
        status: Connection status (active, inactive, error)
        name: Integration name/label
        api_key: API key/token (encrypted in production)
        api_secret: API secret (encrypted in production)
        phone_number_id: WhatsApp phone number ID
        business_account_id: WhatsApp business account ID
        config: Additional JSON configuration
        last_sync_at: Last successful sync timestamp
        error_message: Last error message
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
    """
    
    __tablename__ = "integrations"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Company relationship
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Integration Type
    type = Column(
        SQLEnum(IntegrationType, name="integration_type_enum", create_type=True),
        nullable=False,
        index=True
    )
    
    # Status
    status = Column(
        SQLEnum(IntegrationStatus, name="integration_status_enum", create_type=True),
        default=IntegrationStatus.INACTIVE,
        nullable=False
    )
    
    # Identification
    name = Column(String(255), nullable=False)
    
    # Credentials (should be encrypted in production)
    api_key = Column(Text, nullable=True)
    api_secret = Column(Text, nullable=True)
    
    # WhatsApp-specific fields
    phone_number_id = Column(String(255), nullable=True)
    business_account_id = Column(String(255), nullable=True)
    
    # Additional configuration
    config = Column(JSON, nullable=True)
    
    # Sync tracking
    last_sync_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="integrations")
    
    def __repr__(self):
        return f"<Integration id={self.id} type={self.type} company_id={self.company_id} status={self.status}>"
    
    @property
    def is_active(self) -> bool:
        """Check if integration is active"""
        return self.status == IntegrationStatus.ACTIVE
    
    @property
    def is_whatsapp(self) -> bool:
        """Check if this is a WhatsApp integration"""
        return self.type == IntegrationType.WHATSAPP
    
    def to_dict(self, include_secrets: bool = False):
        """
        Convert to dictionary.
        
        Args:
            include_secrets: Whether to include API credentials (default: False)
        """
        data = {
            "id": self.id,
            "company_id": self.company_id,
            "type": self.type.value if self.type else None,
            "status": self.status.value if self.status else None,
            "name": self.name,
            "phone_number_id": self.phone_number_id,
            "business_account_id": self.business_account_id,
            "last_sync_at": self.last_sync_at.isoformat() if self.last_sync_at else None,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_secrets:
            data["api_key"] = self.api_key
            data["api_secret"] = self.api_secret
            data["config"] = self.config
        
        return data
