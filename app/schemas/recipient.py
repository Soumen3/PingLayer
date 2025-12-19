"""
Recipient Schemas

Pydantic schemas for recipient-related API requests and responses.

Recipients can be added to campaigns via:
1. CSV file upload
2. Manual entry (single recipient)
3. Bulk JSON data
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, EmailStr
import re


# ============================================================================
# CREATE SCHEMAS
# ============================================================================

class RecipientCreate(BaseModel):
    """
    Schema for adding a single recipient to a campaign.
    
    Example:
        {
            "phone_number": "+1234567890",
            "name": "John Doe",
            "email": "john@example.com",
            "custom_data": {
                "company": "Acme Corp",
                "link": "https://example.com/offer"
            }
        }
    """
    phone_number: str = Field(
        ...,
        min_length=10,
        max_length=20,
        description="Phone number with country code",
        examples=["+1234567890", "+919876543210"]
    )
    
    name: Optional[str] = Field(
        None,
        max_length=255,
        description="Recipient name",
        examples=["John Doe"]
    )
    
    email: Optional[str] = Field(
        None,
        max_length=255,
        description="Recipient email address",
        examples=["john@example.com"]
    )
    
    custom_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Custom data for template variables (e.g., {name}, {company}, {link})",
        examples=[{"company": "Acme Corp", "link": "https://example.com"}]
    )
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        """Validate phone number format"""
        # Remove spaces, dashes, parentheses
        cleaned = re.sub(r'[\s\-\(\)]', '', v)
        
        # Must start with + and contain only digits after that
        if not re.match(r'^\+\d{10,15}$', cleaned):
            raise ValueError(
                "Phone number must start with + and country code, "
                "followed by 10-15 digits (e.g., +1234567890)"
            )
        
        return cleaned
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """Validate email format"""
        if v is None:
            return v
        
        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError("Invalid email format")
        
        return v.lower()  # Normalize to lowercase
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "phone_number": "+1234567890",
                "name": "John Doe",
                "email": "john@example.com",
                "custom_data": {
                    "company": "Acme Corp",
                    "link": "https://example.com/offer",
                    "discount": "20%"
                }
            }
        }
    }


class RecipientBulkCreate(BaseModel):
    """
    Schema for adding multiple recipients at once via JSON.
    
    Example:
        {
            "recipients": [
                {
                    "phone_number": "+1234567890",
                    "name": "John Doe",
                    "email": "john@example.com",
                    "custom_data": {"company": "Acme"}
                },
                {
                    "phone_number": "+9876543210",
                    "name": "Jane Smith",
                    "email": "jane@example.com",
                    "custom_data": {"company": "Beta Inc"}
                }
            ]
        }
    """
    recipients: List[RecipientCreate] = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="List of recipients (max 10,000 per request)"
    )
    
    @field_validator('recipients')
    @classmethod
    def validate_recipients(cls, v: List[RecipientCreate]) -> List[RecipientCreate]:
        """Validate recipient list"""
        if len(v) > 10000:
            raise ValueError("Maximum 10,000 recipients per request")
        
        # Check for duplicate phone numbers
        phone_numbers = [r.phone_number for r in v]
        if len(phone_numbers) != len(set(phone_numbers)):
            raise ValueError("Duplicate phone numbers found in the list")
        
        return v


class RecipientCSVUpload(BaseModel):
    """
    Schema for CSV upload response.
    
    The CSV file should have these columns:
    - phone_number (required)
    - name (optional)
    - Any other columns will be treated as custom_data
    
    Example CSV:
        phone_number,name,company,link
        +1234567890,John Doe,Acme Corp,https://example.com/john
        +9876543210,Jane Smith,Beta Inc,https://example.com/jane
    """
    pass  # File upload handled separately


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class RecipientResponse(BaseModel):
    """
    Schema for recipient in API responses.
    """
    id: int = Field(..., description="Recipient ID")
    campaign_id: int = Field(..., description="Campaign ID")
    phone_number: str = Field(..., description="Phone number")
    name: Optional[str] = Field(None, description="Recipient name")
    email: Optional[str] = Field(None, description="Recipient email")
    custom_data: Optional[Dict[str, Any]] = Field(None, description="Custom template data")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "campaign_id": 1,
                "phone_number": "+1234567890",
                "name": "John Doe",
                "email": "john@example.com",
                "custom_data": {
                    "company": "Acme Corp",
                    "link": "https://example.com"
                },
                "created_at": "2024-07-01T10:00:00"
            }
        }
    }


class RecipientListResponse(BaseModel):
    """Response for recipient list endpoint"""
    recipients: List[RecipientResponse] = Field(..., description="List of recipients")
    total: int = Field(..., description="Total number of recipients")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total pages")


class RecipientUploadResponse(BaseModel):
    """Response after uploading recipients"""
    campaign_id: int = Field(..., description="Campaign ID")
    added_count: int = Field(..., description="Number of recipients added")
    duplicate_count: int = Field(0, description="Number of duplicates skipped")
    error_count: int = Field(0, description="Number of errors")
    errors: Optional[List[str]] = Field(None, description="List of error messages")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "campaign_id": 1,
                "added_count": 98,
                "duplicate_count": 2,
                "error_count": 0,
                "errors": []
            }
        }
    }


# ============================================================================
# CSV PARSING HELPER
# ============================================================================

class CSVRecipientRow(BaseModel):
    """
    Schema for a single row from CSV file.
    
    Required columns:
    - phone_number
    
    Optional columns:
    - name
    - Any other columns become custom_data
    """
    phone_number: str
    name: Optional[str] = None
    
    # Additional fields will be captured in custom_data
    class Config:
        extra = "allow"  # Allow extra fields
    
    def to_recipient_create(self) -> RecipientCreate:
        """Convert CSV row to RecipientCreate"""
        # Get all extra fields as custom_data
        custom_data = {}
        for key, value in self.__dict__.items():
            if key not in ['phone_number', 'name'] and value is not None:
                custom_data[key] = value
        
        return RecipientCreate(
            phone_number=self.phone_number,
            name=self.name,
            custom_data=custom_data if custom_data else None
        )
