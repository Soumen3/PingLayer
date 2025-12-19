"""
Recipients Service

Business logic for recipient management.
"""

from typing import List, Optional
import csv
import io
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, UploadFile

from app.models.recipient import Recipient
from app.models.campaign import Campaign
from app.core.dependencies import CurrentUser
from app.schemas.recipient import (
    RecipientCreate,
    RecipientBulkCreate,
    RecipientUploadResponse
)


def get_campaign_or_404(
    db: Session,
    current_user: CurrentUser,
    campaign_id: int
) -> Campaign:
    """
    Get campaign and verify it belongs to user's company.
    
    Args:
        db: Database session
        current_user: Authenticated user
        campaign_id: Campaign ID
    
    Returns:
        Campaign object
    
    Raises:
        HTTPException: If campaign not found or doesn't belong to company
    """
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.company_id == current_user.company_id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return campaign


def add_single_recipient(
    db: Session,
    current_user: CurrentUser,
    campaign_id: int,
    recipient_data: RecipientCreate
) -> Recipient:
    """
    Add a single recipient to a campaign.
    
    Args:
        db: Database session
        current_user: Authenticated user
        campaign_id: Campaign ID
        recipient_data: Recipient data
    
    Returns:
        Created Recipient object
    
    Raises:
        HTTPException: If campaign not found or recipient already exists
    """
    # Verify campaign exists and belongs to user's company
    campaign = get_campaign_or_404(db, current_user, campaign_id)
    
    # Check if recipient already exists
    existing = db.query(Recipient).filter(
        Recipient.campaign_id == campaign_id,
        Recipient.phone_number == recipient_data.phone_number
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Recipient with phone number {recipient_data.phone_number} already exists in this campaign"
        )
    
    # Create recipient
    recipient = Recipient(
        campaign_id=campaign_id,
        phone_number=recipient_data.phone_number,
        name=recipient_data.name,
        email=recipient_data.email,
        custom_data=recipient_data.custom_data
    )
    
    db.add(recipient)
    
    # Update campaign total_recipients count
    campaign.total_recipients = db.query(Recipient).filter(
        Recipient.campaign_id == campaign_id
    ).count() + 1
    
    db.commit()
    db.refresh(recipient)
    
    return recipient


def add_bulk_recipients(
    db: Session,
    current_user: CurrentUser,
    campaign_id: int,
    bulk_data: RecipientBulkCreate
) -> RecipientUploadResponse:
    """
    Add multiple recipients to a campaign via JSON.
    
    Args:
        db: Database session
        current_user: Authenticated user
        campaign_id: Campaign ID
        bulk_data: Bulk recipient data
    
    Returns:
        RecipientUploadResponse with counts
    """
    # Verify campaign exists and belongs to user's company
    campaign = get_campaign_or_404(db, current_user, campaign_id)
    
    added_count = 0
    duplicate_count = 0
    error_count = 0
    errors = []
    
    for idx, recipient_data in enumerate(bulk_data.recipients, start=1):
        try:
            # Check for duplicate
            existing = db.query(Recipient).filter(
                Recipient.campaign_id == campaign_id,
                Recipient.phone_number == recipient_data.phone_number
            ).first()
            
            if existing:
                duplicate_count += 1
                continue
            
            # Create recipient
            recipient = Recipient(
                campaign_id=campaign_id,
                phone_number=recipient_data.phone_number,
                name=recipient_data.name,
                email=recipient_data.email,
                custom_data=recipient_data.custom_data
            )
            db.add(recipient)
            added_count += 1
            
        except Exception as e:
            error_count += 1
            errors.append(f"Recipient {idx}: {str(e)}")
    
    # Update campaign total_recipients count
    campaign.total_recipients = db.query(Recipient).filter(
        Recipient.campaign_id == campaign_id
    ).count()
    
    db.commit()
    
    return RecipientUploadResponse(
        campaign_id=campaign_id,
        added_count=added_count,
        duplicate_count=duplicate_count,
        error_count=error_count,
        errors=errors if errors else None
    )


async def upload_recipients_csv(
    db: Session,
    current_user: CurrentUser,
    campaign_id: int,
    file: UploadFile
) -> RecipientUploadResponse:
    """
    Upload recipients from CSV file.
    
    CSV Format:
    - Required column: phone_number
    - Optional columns: name, email
    - All other columns become custom_data
    
    Args:
        db: Database session
        current_user: Authenticated user
        campaign_id: Campaign ID
        file: Uploaded CSV file
    
    Returns:
        RecipientUploadResponse with counts and errors
    """
    # Verify campaign exists and belongs to user's company
    campaign = get_campaign_or_404(db, current_user, campaign_id)
    
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="File must be a CSV file"
        )
    
    # Read CSV file
    try:
        contents = await file.read()
        csv_data = contents.decode('utf-8')
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to read CSV file: {str(e)}"
        )
    
    # Parse CSV
    csv_reader = csv.DictReader(io.StringIO(csv_data))
    
    # Validate required column
    if 'phone_number' not in csv_reader.fieldnames:
        raise HTTPException(
            status_code=400,
            detail="CSV must have a 'phone_number' column"
        )
    
    added_count = 0
    duplicate_count = 0
    error_count = 0
    errors = []
    
    for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (header is row 1)
        try:
            # Validate phone_number
            phone_number = row.get('phone_number', '').strip()
            if not phone_number:
                errors.append(f"Row {row_num}: Missing phone_number")
                error_count += 1
                continue
            
            # Get name and email
            name = row.get('name', '').strip() or None
            email = row.get('email', '').strip() or None
            
            # Get custom data (all columns except phone_number, name, and email)
            custom_data = {}
            for key, value in row.items():
                if key not in ['phone_number', 'name', 'email'] and value and value.strip():
                    custom_data[key] = value.strip()
            
            # Check for duplicate
            existing = db.query(Recipient).filter(
                Recipient.campaign_id == campaign_id,
                Recipient.phone_number == phone_number
            ).first()
            
            if existing:
                duplicate_count += 1
                continue
            
            # Create recipient
            recipient = Recipient(
                campaign_id=campaign_id,
                phone_number=phone_number,
                name=name,
                email=email,
                custom_data=custom_data if custom_data else None
            )
            db.add(recipient)
            added_count += 1
            
        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")
            error_count += 1
    
    # Update campaign total_recipients count
    campaign.total_recipients = db.query(Recipient).filter(
        Recipient.campaign_id == campaign_id
    ).count()
    
    db.commit()
    
    return RecipientUploadResponse(
        campaign_id=campaign_id,
        added_count=added_count,
        duplicate_count=duplicate_count,
        error_count=error_count,
        errors=errors if errors else None
    )


def list_recipients(
    db: Session,
    current_user: CurrentUser,
    campaign_id: int,
    skip: int = 0,
    limit: int = 50
) -> tuple[List[Recipient], int]:
    """
    List recipients for a campaign with pagination.
    
    Args:
        db: Database session
        current_user: Authenticated user
        campaign_id: Campaign ID
        skip: Number of records to skip
        limit: Maximum number of records to return
    
    Returns:
        Tuple of (recipients list, total count)
    """
    # Verify campaign exists and belongs to user's company
    campaign = get_campaign_or_404(db, current_user, campaign_id)
    
    # Get total count
    total = db.query(Recipient).filter(
        Recipient.campaign_id == campaign_id
    ).count()
    
    # Get paginated recipients
    recipients = db.query(Recipient).filter(
        Recipient.campaign_id == campaign_id
    ).offset(skip).limit(limit).all()
    
    return recipients, total


def get_recipient_by_id(
    db: Session,
    current_user: CurrentUser,
    campaign_id: int,
    recipient_id: int
) -> Optional[Recipient]:
    """
    Get a specific recipient.
    
    Args:
        db: Database session
        current_user: Authenticated user
        campaign_id: Campaign ID
        recipient_id: Recipient ID
    
    Returns:
        Recipient object or None
    """
    # Verify campaign exists and belongs to user's company
    campaign = get_campaign_or_404(db, current_user, campaign_id)
    
    return db.query(Recipient).filter(
        Recipient.id == recipient_id,
        Recipient.campaign_id == campaign_id
    ).first()


def delete_recipient(
    db: Session,
    current_user: CurrentUser,
    campaign_id: int,
    recipient_id: int
) -> bool:
    """
    Delete a recipient from a campaign.
    
    Args:
        db: Database session
        current_user: Authenticated user
        campaign_id: Campaign ID
        recipient_id: Recipient ID
    
    Returns:
        True if deleted, False if not found
    """
    recipient = get_recipient_by_id(db, current_user, campaign_id, recipient_id)
    
    if not recipient:
        return False
    
    db.delete(recipient)
    
    # Update campaign total_recipients count
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if campaign:
        campaign.total_recipients = db.query(Recipient).filter(
            Recipient.campaign_id == campaign_id
        ).count() - 1
    
    db.commit()
    
    return True


def delete_all_recipients(
    db: Session,
    current_user: CurrentUser,
    campaign_id: int
) -> int:
    """
    Delete all recipients from a campaign.
    
    Args:
        db: Database session
        current_user: Authenticated user
        campaign_id: Campaign ID
    
    Returns:
        Number of recipients deleted
    """
    # Verify campaign exists and belongs to user's company
    campaign = get_campaign_or_404(db, current_user, campaign_id)
    
    # Count recipients
    count = db.query(Recipient).filter(
        Recipient.campaign_id == campaign_id
    ).count()
    
    # Delete all recipients
    db.query(Recipient).filter(
        Recipient.campaign_id == campaign_id
    ).delete()
    
    # Update campaign total_recipients count
    campaign.total_recipients = 0
    
    db.commit()
    
    return count
