"""
Campaign Router

API endpoints for campaign management.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.campaigns import service
from app.schemas.campaign import (
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
    CampaignListResponse,
    campaign_to_response
)
from app.core.logging import logger
from app.core.dependencies import get_current_user, CurrentUser
from app.models.campaign import CampaignStatus

router = APIRouter()


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
def create_campaign(
    campaign: CampaignCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Create a new campaign.
    
    - **name**: Campaign name (required)
    - **message_template**: Message template with placeholders
    - **scheduled_at**: Optional scheduled send time
    """
    logger.info(f"Creating campaign: {campaign.name} for user {current_user.user_id}")
    
    db_campaign = service.create_campaign(db, campaign, current_user)
    return campaign_to_response(db_campaign)


@router.get("", response_model=List[CampaignResponse])
def list_campaigns(
    status: Optional[CampaignStatus] = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    List all campaigns for the current user's company.
    
    - **status**: Optional filter by campaign status
    """
    logger.info(f"Listing campaigns for user {current_user.user_id}")
    
    campaigns = service.list_campaigns(db, current_user, status)
    return [campaign_to_response(c) for c in campaigns]


@router.get("/{campaign_id}", response_model=CampaignResponse)
def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Get a specific campaign by ID"""
    logger.info(f"Getting campaign {campaign_id}")
    
    campaign = service.get_campaign_by_id(db, current_user, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return campaign_to_response(campaign)


@router.patch("/{campaign_id}", response_model=CampaignResponse)
def update_campaign(
    campaign_id: int,
    campaign: CampaignUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Update a campaign.
    
    Note: Can only update campaigns in DRAFT or SCHEDULED status.
    """
    logger.info(f"Updating campaign {campaign_id}")
    
    db_campaign = service.update_campaign(db, current_user, campaign_id, campaign)
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return campaign_to_response(db_campaign)


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Delete a campaign"""
    logger.info(f"Deleting campaign {campaign_id}")
    
    success = service.delete_campaign(db, current_user, campaign_id)
    if not success:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return None


@router.post("/{campaign_id}/send")
def send_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Send a campaign.
    
    This will queue the campaign for sending to all recipients.
    """
    logger.info(f"Sending campaign {campaign_id}")
    
    result = service.send_campaign(db, current_user, campaign_id)
    if not result:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return result


@router.post("/{campaign_id}/cancel")
def cancel_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Cancel a campaign that is scheduled or sending"""
    logger.info(f"Canceling campaign {campaign_id}")
    
    result = service.cancel_campaign(db, current_user, campaign_id)
    if not result:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return result
