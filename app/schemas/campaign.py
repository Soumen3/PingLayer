"""
Campaign Schemas

Pydantic schemas for campaign-related API requests and responses.

Schemas:
- CampaignCreate: Create a new campaign
- CampaignUpdate: Update an existing campaign
- CampaignResponse: Campaign data in API responses
- CampaignListResponse: List of campaigns with pagination
- CampaignStats: Campaign statistics
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from enum import Enum

from app.models.campaign import CampaignStatus


# ============================================================================
# CREATE SCHEMAS
# ============================================================================

class CampaignCreate(BaseModel):
    """
    Schema for creating a new campaign.
    
    Example:
        {
            "name": "Summer Sale 2024",
            "description": "Promotional campaign for summer sale",
            "message_template": "Hi {name}, check out our summer sale! Visit {link}",
            "template_variables": ["name", "link"],
            "scheduled_at": "2024-07-01T10:00:00"
        }
    """
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Campaign name",
        examples=["Summer Sale 2024"]
    )
    
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Campaign description",
        examples=["Promotional campaign for summer sale"]
    )
    
    message_template: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Message template with placeholders like {name}, {company}",
        examples=["Hi {name}, check out our summer sale! Visit {link}"]
    )
    
    template_variables: Optional[List[str]] = Field(
        None,
        description="List of variable names used in template",
        examples=[["name", "link", "company"]]
    )
    
    scheduled_at: Optional[datetime] = Field(
        None,
        description="When to send the campaign (None = send immediately)",
        examples=["2024-07-01T10:00:00"]
    )
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate campaign name"""
        if not v or not v.strip():
            raise ValueError("Campaign name cannot be empty")
        return v.strip()
    
    @field_validator('message_template')
    @classmethod
    def validate_message_template(cls, v: str) -> str:
        """Validate message template"""
        if not v or not v.strip():
            raise ValueError("Message template cannot be empty")
        if len(v.strip()) < 10:
            raise ValueError("Message template must be at least 10 characters")
        return v.strip()
    
    @field_validator('scheduled_at')
    @classmethod
    def validate_scheduled_at(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Validate scheduled time is in the future"""
        if v and v < datetime.utcnow():
            raise ValueError("Scheduled time must be in the future")
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Summer Sale 2024",
                "description": "Promotional campaign for summer sale",
                "message_template": "Hi {name}, check out our summer sale! Visit {link}",
                "template_variables": ["name", "link"],
                "scheduled_at": "2024-07-01T10:00:00"
            }
        }
    }


# ============================================================================
# UPDATE SCHEMAS
# ============================================================================

class CampaignUpdate(BaseModel):
    """
    Schema for updating an existing campaign.
    
    All fields are optional - only provided fields will be updated.
    Note: Can only update campaigns in DRAFT or SCHEDULED status.
    """
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Campaign name"
    )
    
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Campaign description"
    )
    
    message_template: Optional[str] = Field(
        None,
        min_length=1,
        max_length=5000,
        description="Message template"
    )
    
    template_variables: Optional[List[str]] = Field(
        None,
        description="Template variables"
    )
    
    scheduled_at: Optional[datetime] = Field(
        None,
        description="Scheduled send time"
    )
    
    status: Optional[CampaignStatus] = Field(
        None,
        description="Campaign status (limited transitions allowed)"
    )
    
    @field_validator('scheduled_at')
    @classmethod
    def validate_scheduled_at(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Validate scheduled time is in the future"""
        if v and v < datetime.utcnow():
            raise ValueError("Scheduled time must be in the future")
        return v


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class CampaignStats(BaseModel):
    """Campaign statistics"""
    total_recipients: int = Field(0, description="Total number of recipients")
    sent_count: int = Field(0, description="Number of messages sent")
    delivered_count: int = Field(0, description="Number of messages delivered")
    failed_count: int = Field(0, description="Number of messages failed")
    success_rate: float = Field(0.0, description="Success rate percentage")
    progress_percentage: float = Field(0.0, description="Sending progress percentage")


class CampaignResponse(BaseModel):
    """
    Schema for campaign in API responses.
    
    This is what the API returns when you create, update, or retrieve a campaign.
    """
    id: int = Field(..., description="Campaign ID")
    name: str = Field(..., description="Campaign name")
    description: Optional[str] = Field(None, description="Campaign description")
    
    company_id: int = Field(..., description="Company ID (tenant)")
    created_by: Optional[int] = Field(None, description="User ID who created this campaign")
    
    status: CampaignStatus = Field(..., description="Campaign status")
    
    message_template: str = Field(..., description="Message template")
    template_variables: Optional[List[str]] = Field(None, description="Template variables")
    
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled send time")
    started_at: Optional[datetime] = Field(None, description="When sending started")
    completed_at: Optional[datetime] = Field(None, description="When sending completed")
    
    # Statistics
    stats: CampaignStats = Field(..., description="Campaign statistics")
    
    # Computed properties
    is_editable: bool = Field(..., description="Whether campaign can be edited")
    is_sendable: bool = Field(..., description="Whether campaign can be sent")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "Summer Sale 2024",
                "description": "Promotional campaign",
                "company_id": 1,
                "created_by": 1,
                "status": "draft",
                "message_template": "Hi {name}, check out our sale!",
                "template_variables": ["name"],
                "scheduled_at": None,
                "started_at": None,
                "completed_at": None,
                "stats": {
                    "total_recipients": 100,
                    "sent_count": 0,
                    "delivered_count": 0,
                    "failed_count": 0,
                    "success_rate": 0.0,
                    "progress_percentage": 0.0
                },
                "is_editable": True,
                "is_sendable": True,
                "created_at": "2024-07-01T10:00:00",
                "updated_at": "2024-07-01T10:00:00"
            }
        }
    }


class CampaignListItem(BaseModel):
    """Simplified campaign info for list views"""
    id: int
    name: str
    status: CampaignStatus
    total_recipients: int
    sent_count: int
    delivered_count: int
    success_rate: float
    progress_percentage: float
    scheduled_at: Optional[datetime]
    created_at: datetime
    
    model_config = {"from_attributes": True}


class CampaignListResponse(BaseModel):
    """Response for campaign list endpoint with pagination"""
    campaigns: List[CampaignListItem] = Field(..., description="List of campaigns")
    total: int = Field(..., description="Total number of campaigns")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "campaigns": [
                    {
                        "id": 1,
                        "name": "Summer Sale 2024",
                        "status": "completed",
                        "total_recipients": 100,
                        "sent_count": 100,
                        "delivered_count": 95,
                        "success_rate": 95.0,
                        "progress_percentage": 100.0,
                        "scheduled_at": None,
                        "created_at": "2024-07-01T10:00:00"
                    }
                ],
                "total": 1,
                "page": 1,
                "page_size": 10,
                "total_pages": 1
            }
        }
    }


# ============================================================================
# ACTION SCHEMAS
# ============================================================================

class CampaignSendRequest(BaseModel):
    """Request to send a campaign"""
    send_immediately: bool = Field(
        True,
        description="Send immediately or use scheduled_at time"
    )
    
    override_scheduled_at: Optional[datetime] = Field(
        None,
        description="Override the scheduled time (if send_immediately is False)"
    )


class CampaignSendResponse(BaseModel):
    """Response after initiating campaign send"""
    campaign_id: int = Field(..., description="Campaign ID")
    status: CampaignStatus = Field(..., description="New campaign status")
    message: str = Field(..., description="Status message")
    estimated_completion: Optional[datetime] = Field(
        None,
        description="Estimated completion time"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "campaign_id": 1,
                "status": "sending",
                "message": "Campaign sending started",
                "estimated_completion": "2024-07-01T11:00:00"
            }
        }
    }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def campaign_to_response(campaign) -> CampaignResponse:
    """
    Convert Campaign ORM model to CampaignResponse schema.
    
    Args:
        campaign: Campaign ORM model instance
    
    Returns:
        CampaignResponse schema
    """
    return CampaignResponse(
        id=campaign.id,
        name=campaign.name,
        description=campaign.description,
        company_id=campaign.company_id,
        created_by=campaign.created_by,
        status=campaign.status,
        message_template=campaign.message_template,
        template_variables=campaign.template_variables,
        scheduled_at=campaign.scheduled_at,
        started_at=campaign.started_at,
        completed_at=campaign.completed_at,
        stats=CampaignStats(
            total_recipients=campaign.total_recipients,
            sent_count=campaign.sent_count,
            delivered_count=campaign.delivered_count,
            failed_count=campaign.failed_count,
            success_rate=campaign.success_rate,
            progress_percentage=campaign.progress_percentage
        ),
        is_editable=campaign.is_editable,
        is_sendable=campaign.is_sendable,
        created_at=campaign.created_at,
        updated_at=campaign.updated_at
    )
