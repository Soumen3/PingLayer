"""
Models Package

Exports all SQLAlchemy ORM models.

Import all models here to ensure they're registered with SQLAlchemy Base
before creating tables or running migrations.
"""

from app.models.user import User
from app.models.company import Company
from app.models.campaign import Campaign, CampaignStatus
from app.models.recipient import Recipient
from app.models.message_log import MessageLog, MessageStatus
from app.models.smart_link import SmartLink
from app.models.click_event import ClickEvent
from app.models.integration import Integration, IntegrationType, IntegrationStatus

__all__ = [
    # Models
    "User",
    "Company",
    "Campaign",
    "Recipient",
    "MessageLog",
    "SmartLink",
    "ClickEvent",
    "Integration",
    # Enums
    "CampaignStatus",
    "MessageStatus",
    "IntegrationType",
    "IntegrationStatus",
]
