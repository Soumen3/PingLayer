"""
Schemas Package

Pydantic schemas for API request/response validation.

This package contains all Pydantic models used for:
- Request validation
- Response serialization
- API documentation (OpenAPI/Swagger)

Modules:
- user: User authentication and profile schemas
- campaign: Campaign management schemas
- recipient: Recipient schemas
- smart_link: Smart link schemas (to be implemented)
- analytics: Analytics schemas (to be implemented)
"""

# User schemas
from app.schemas.user import (
    UserCreate,
    UserLogin,
)

# Campaign schemas
from app.schemas.campaign import (
    CampaignStatus,
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
    CampaignListItem,
    CampaignListResponse,
    CampaignStats,
    CampaignSendRequest,
    CampaignSendResponse,
    campaign_to_response,
)

# Recipient schemas
from app.schemas.recipient import (
    RecipientCreate,
    RecipientBulkCreate,
    RecipientResponse,
    RecipientListResponse,
    RecipientUploadResponse,
)

__all__ = [
    # User
    "UserCreate",
    "UserLogin",
    
    # Campaign
    "CampaignStatus",
    "CampaignCreate",
    "CampaignUpdate",
    "CampaignResponse",
    "CampaignListItem",
    "CampaignListResponse",
    "CampaignStats",
    "CampaignSendRequest",
    "CampaignSendResponse",
    "campaign_to_response",
    
    # Recipient
    "RecipientCreate",
    "RecipientBulkCreate",
    "RecipientResponse",
    "RecipientListResponse",
    "RecipientUploadResponse",
]
