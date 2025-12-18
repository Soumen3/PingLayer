"""
Campaign Service

Business logic for campaign operations.
"""

from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.models.campaign import Campaign, CampaignStatus
from app.core.dependencies import CurrentUser
from app.schemas.campaign import CampaignCreate, CampaignUpdate


def create_campaign(
    db: Session,
    campaign_data: CampaignCreate,
    current_user: CurrentUser
) -> Campaign:
    """
    Create a new campaign.
    
    Args:
        db: Database session
        campaign_data: Campaign creation data
        current_user: Authenticated user context
    
    Returns:
        Created Campaign object
    """
    # Determine initial status
    status = CampaignStatus.SCHEDULED if campaign_data.scheduled_at else CampaignStatus.DRAFT
    
    try:
        db_campaign = Campaign(
            name=campaign_data.name,
            description=campaign_data.description,
            message_template=campaign_data.message_template,
            template_variables=campaign_data.template_variables,
            scheduled_at=campaign_data.scheduled_at,
            status=status,
            company_id=current_user.company_id,  # Multi-tenant isolation
            created_by=current_user.user_id
        )
        
        db.add(db_campaign)
        db.commit()
        db.refresh(db_campaign)
        
        return db_campaign
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to create campaign: {str(e)}")


def list_campaigns(
    db: Session,
    current_user: CurrentUser,
    status: Optional[CampaignStatus] = None
) -> List[Campaign]:
    """
    List all campaigns for the user's company.
    
    Args:
        db: Database session
        current_user: Authenticated user context
        status: Optional status filter
    
    Returns:
        List of Campaign objects
    """
    # Query campaigns for user's company (multi-tenant isolation)
    query = db.query(Campaign).filter(
        Campaign.company_id == current_user.company_id
    )
    
    # Apply status filter if provided
    if status:
        query = query.filter(Campaign.status == status)
    
    # Order by most recent first
    query = query.order_by(Campaign.created_at.desc())
    
    return query.all()


def get_campaign_by_id(
    db: Session,
    current_user: CurrentUser,
    campaign_id: int
) -> Optional[Campaign]:
    """
    Get a campaign by ID.
    
    Args:
        db: Database session
        current_user: Authenticated user context
        campaign_id: Campaign ID
    
    Returns:
        Campaign object or None if not found
    """
    return db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.company_id == current_user.company_id  # Multi-tenant isolation
    ).first()


def update_campaign(
    db: Session,
    current_user: CurrentUser,
    campaign_id: int,
    campaign_data: CampaignUpdate
) -> Optional[Campaign]:
    """
    Update a campaign.
    
    Args:
        db: Database session
        current_user: Authenticated user context
        campaign_id: Campaign ID
        campaign_data: Update data
    
    Returns:
        Updated Campaign object or None if not found
    
    Raises:
        HTTPException: If campaign cannot be edited
    """
    # Get campaign
    db_campaign = get_campaign_by_id(db, current_user, campaign_id)
    if not db_campaign:
        return None
    
    # Check if campaign is editable
    if not db_campaign.is_editable:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot edit campaign in {db_campaign.status.value} status"
        )
    
    # Update fields (only non-None values)
    update_data = campaign_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_campaign, key, value)
    
    # Update timestamp
    db_campaign.updated_at = datetime.utcnow()
    
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    
    return db_campaign


def delete_campaign(
    db: Session,
    current_user: CurrentUser,
    campaign_id: int
) -> bool:
    """
    Delete a campaign.
    
    Args:
        db: Database session
        current_user: Authenticated user context
        campaign_id: Campaign ID
    
    Returns:
        True if deleted, False if not found
    
    Raises:
        HTTPException: If campaign cannot be deleted
    """
    db_campaign = get_campaign_by_id(db, current_user, campaign_id)
    if not db_campaign:
        return False
    
    # Check if campaign can be deleted
    if db_campaign.status in [CampaignStatus.SENDING]:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete campaign while sending"
        )
    
    db.delete(db_campaign)
    db.commit()
    
    return True


def send_campaign(
    db: Session,
    current_user: CurrentUser,
    campaign_id: int
) -> dict:
    """
    Send a campaign.
    
    Args:
        db: Database session
        current_user: Authenticated user context
        campaign_id: Campaign ID
    
    Returns:
        Status dict
    
    Raises:
        HTTPException: If campaign cannot be sent
    """
    db_campaign = get_campaign_by_id(db, current_user, campaign_id)
    if not db_campaign:
        return None
    
    # Check if campaign can be sent
    if not db_campaign.is_sendable:
        raise HTTPException(
            status_code=400,
            detail=f"Campaign cannot be sent. Status: {db_campaign.status.value}, Recipients: {db_campaign.total_recipients}"
        )
    
    # Update status
    db_campaign.status = CampaignStatus.SENDING
    db_campaign.started_at = datetime.utcnow()
    
    db.add(db_campaign)
    db.commit()
    
    # TODO: Queue campaign for background processing
    # This would typically:
    # 1. Add to Redis queue
    # 2. Background worker picks it up
    # 3. Sends messages to all recipients
    # 4. Updates message_logs
    # 5. Updates campaign stats
    
    return {
        "campaign_id": campaign_id,
        "status": "sending",
        "message": "Campaign queued for sending",
        "total_recipients": db_campaign.total_recipients
    }


def cancel_campaign(
    db: Session,
    current_user: CurrentUser,
    campaign_id: int
) -> dict:
    """
    Cancel a campaign.
    
    Args:
        db: Database session
        current_user: Authenticated user context
        campaign_id: Campaign ID
    
    Returns:
        Status dict
    
    Raises:
        HTTPException: If campaign cannot be cancelled
    """
    db_campaign = get_campaign_by_id(db, current_user, campaign_id)
    if not db_campaign:
        return None
    
    # Check if campaign can be cancelled
    if db_campaign.status in [CampaignStatus.COMPLETED, CampaignStatus.CANCELLED]:
        raise HTTPException(
            status_code=400,
            detail=f"Campaign is already {db_campaign.status.value}"
        )
    
    # Update status
    db_campaign.status = CampaignStatus.CANCELLED
    db_campaign.updated_at = datetime.utcnow()
    
    db.add(db_campaign)
    db.commit()
    
    return {
        "campaign_id": campaign_id,
        "status": "cancelled",
        "message": "Campaign cancelled successfully"
    }