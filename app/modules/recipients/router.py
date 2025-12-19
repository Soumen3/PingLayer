"""
Recipients Router

API endpoints for recipient management.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.recipients import service
from app.schemas.recipient import (
    RecipientCreate,
    RecipientBulkCreate,
    RecipientResponse,
    RecipientListResponse,
    RecipientUploadResponse
)
from app.core.logging import logger
from app.core.dependencies import get_current_user, CurrentUser

router = APIRouter()


@router.post(
    "/campaigns/{campaign_id}/recipients",
    response_model=RecipientResponse,
    status_code=status.HTTP_201_CREATED
)
def add_recipient(
    campaign_id: int,
    recipient_data: RecipientCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Add a single recipient to a campaign.
    
    - **phone_number**: Phone number with country code (e.g., +1234567890)
    - **name**: Optional recipient name
    - **custom_data**: Optional custom data for template variables
    """
    logger.info(f"Adding recipient to campaign {campaign_id}")
    
    recipient = service.add_single_recipient(
        db, current_user, campaign_id, recipient_data
    )
    
    return RecipientResponse.model_validate(recipient)


@router.post(
    "/campaigns/{campaign_id}/recipients/bulk",
    response_model=RecipientUploadResponse
)
def add_recipients_bulk(
    campaign_id: int,
    bulk_data: RecipientBulkCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Add multiple recipients to a campaign via JSON.
    
    Maximum 10,000 recipients per request.
    Duplicates are automatically skipped.
    """
    logger.info(f"Adding {len(bulk_data.recipients)} recipients to campaign {campaign_id}")
    
    return service.add_bulk_recipients(db, current_user, campaign_id, bulk_data)


@router.post(
    "/campaigns/{campaign_id}/recipients/upload",
    response_model=RecipientUploadResponse
)
async def upload_recipients_csv(
    campaign_id: int,
    file: UploadFile = File(..., description="CSV file with recipients"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Upload recipients from a CSV file.
    
    **CSV Format**:
    - Required column: `phone_number`
    - Optional column: `name`
    - All other columns become `custom_data` for template variables
    
    **Example CSV**:
    ```
    phone_number,name,company,discount,link
    +1234567890,John Doe,Acme Corp,20,https://example.com/john
    +9876543210,Jane Smith,Beta Inc,15,https://example.com/jane
    ```
    
    **Returns**:
    - Number of recipients added
    - Number of duplicates skipped
    - Number of errors
    - List of error messages (if any)
    """
    logger.info(f"Uploading CSV file to campaign {campaign_id}: {file.filename}")
    
    return await service.upload_recipients_csv(
        db, current_user, campaign_id, file
    )


@router.get(
    "/campaigns/{campaign_id}/recipients",
    response_model=RecipientListResponse
)
def list_recipients(
    campaign_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    List all recipients for a campaign with pagination.
    
    - **page**: Page number (starts at 1)
    - **page_size**: Number of items per page (1-100)
    """
    logger.info(f"Listing recipients for campaign {campaign_id}, page {page}")
    
    skip = (page - 1) * page_size
    recipients, total = service.list_recipients(
        db, current_user, campaign_id, skip, page_size
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return RecipientListResponse(
        recipients=[RecipientResponse.model_validate(r) for r in recipients],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get(
    "/campaigns/{campaign_id}/recipients/{recipient_id}",
    response_model=RecipientResponse
)
def get_recipient(
    campaign_id: int,
    recipient_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Get a specific recipient by ID"""
    logger.info(f"Getting recipient {recipient_id} from campaign {campaign_id}")
    
    recipient = service.get_recipient_by_id(
        db, current_user, campaign_id, recipient_id
    )
    
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    
    return RecipientResponse.model_validate(recipient)


@router.delete(
    "/campaigns/{campaign_id}/recipients/{recipient_id}",
    status_code=status.HTTP_200_OK
)
def delete_recipient(
    campaign_id: int,
    recipient_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Delete a specific recipient from a campaign"""
    logger.info(f"Deleting recipient {recipient_id} from campaign {campaign_id}")
    
    success = service.delete_recipient(
        db, current_user, campaign_id, recipient_id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Recipient not found")
    
    return {
        "message": "Recipient deleted successfully"
    }


@router.delete(
    "/campaigns/{campaign_id}/recipients",
    status_code=status.HTTP_200_OK
)
def delete_all_recipients(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Delete all recipients from a campaign.
    
    **Warning**: This action cannot be undone!
    """
    logger.info(f"Deleting all recipients from campaign {campaign_id}")
    
    count = service.delete_all_recipients(db, current_user, campaign_id)
    
    return {
        "message": f"Deleted {count} recipient(s)",
        "count": count
    }
