# 📋 Campaign Schemas - Quick Reference

## ✅ Created Files

1. **`app/schemas/campaign.py`** - Complete campaign schemas
2. **`app/schemas/__init__.py`** - Package exports

---

## 📦 Available Schemas

### **1. CampaignCreate**
**Purpose**: Create a new campaign

**Fields**:
- `name` (required) - Campaign name (1-255 chars)
- `description` (optional) - Campaign description (max 1000 chars)
- `message_template` (required) - Message with placeholders like `{name}`
- `template_variables` (optional) - List of variable names
- `scheduled_at` (optional) - When to send (None = immediate)

**Validation**:
- ✅ Name cannot be empty
- ✅ Message template min 10 characters
- ✅ Scheduled time must be in future

**Example**:
```json
{
  "name": "Summer Sale 2024",
  "description": "Promotional campaign for summer sale",
  "message_template": "Hi {name}, check out our summer sale! Visit {link}",
  "template_variables": ["name", "link"],
  "scheduled_at": "2024-07-01T10:00:00"
}
```

---

### **2. CampaignUpdate**
**Purpose**: Update an existing campaign

**Fields**: All optional
- `name`
- `description`
- `message_template`
- `template_variables`
- `scheduled_at`
- `status`

**Note**: Can only update campaigns in DRAFT or SCHEDULED status

---

### **3. CampaignResponse**
**Purpose**: Campaign data in API responses

**Includes**:
- All campaign fields
- `stats` object with:
  - `total_recipients`
  - `sent_count`
  - `delivered_count`
  - `failed_count`
  - `success_rate`
  - `progress_percentage`
- Computed properties:
  - `is_editable`
  - `is_sendable`

**Example**:
```json
{
  "id": 1,
  "name": "Summer Sale 2024",
  "status": "draft",
  "message_template": "Hi {name}!",
  "stats": {
    "total_recipients": 100,
    "sent_count": 0,
    "delivered_count": 0,
    "failed_count": 0,
    "success_rate": 0.0,
    "progress_percentage": 0.0
  },
  "is_editable": true,
  "is_sendable": true,
  "created_at": "2024-07-01T10:00:00"
}
```

---

### **4. CampaignListResponse**
**Purpose**: Paginated list of campaigns

**Fields**:
- `campaigns` - Array of simplified campaign objects
- `total` - Total count
- `page` - Current page
- `page_size` - Items per page
- `total_pages` - Total pages

---

### **5. CampaignSendRequest**
**Purpose**: Request to send a campaign

**Fields**:
- `send_immediately` (default: true)
- `override_scheduled_at` (optional)

---

### **6. CampaignSendResponse**
**Purpose**: Response after initiating send

**Fields**:
- `campaign_id`
- `status`
- `message`
- `estimated_completion`

---

## 🎯 Campaign Status Enum

```python
class CampaignStatus(str, Enum):
    DRAFT = "draft"           # Being created
    SCHEDULED = "scheduled"   # Scheduled for future
    SENDING = "sending"       # Currently sending
    COMPLETED = "completed"   # All sent
    FAILED = "failed"         # Send failed
    CANCELLED = "cancelled"   # User cancelled
```

---

## 🔧 Helper Functions

### **campaign_to_response(campaign)**
Converts Campaign ORM model to CampaignResponse schema

**Usage**:
```python
from app.schemas.campaign import campaign_to_response

# In your route
campaign = db.query(Campaign).first()
response = campaign_to_response(campaign)
return response
```

---

## 📝 Usage Examples

### **Import Schemas**
```python
from app.schemas.campaign import (
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
    CampaignListResponse,
    campaign_to_response
)

# Or import from package
from app.schemas import CampaignCreate, CampaignResponse
```

### **In FastAPI Routes**
```python
from fastapi import APIRouter, Depends
from app.schemas import CampaignCreate, CampaignResponse

router = APIRouter()

@router.post("/campaigns", response_model=CampaignResponse)
def create_campaign(
    campaign_data: CampaignCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    # Create campaign
    campaign = Campaign(
        name=campaign_data.name,
        description=campaign_data.description,
        message_template=campaign_data.message_template,
        company_id=current_user.company_id,
        created_by=current_user.user_id
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    
    # Convert to response
    return campaign_to_response(campaign)
```

---

## ✅ Validation Rules

### **Campaign Name**
- ✅ Required
- ✅ 1-255 characters
- ✅ Cannot be empty or whitespace only

### **Message Template**
- ✅ Required
- ✅ Minimum 10 characters
- ✅ Maximum 5000 characters
- ✅ Can contain placeholders: `{name}`, `{company}`, etc.

### **Scheduled Time**
- ✅ Optional
- ✅ Must be in the future (if provided)
- ✅ None = send immediately

### **Template Variables**
- ✅ Optional
- ✅ Array of strings
- ✅ Should match placeholders in message_template

---

## 🎨 Template Variable Examples

### **Simple Template**
```json
{
  "message_template": "Hi {name}, welcome to {company}!",
  "template_variables": ["name", "company"]
}
```

### **With Links**
```json
{
  "message_template": "Hi {name}, check out {link} for exclusive offers!",
  "template_variables": ["name", "link"]
}
```

### **Complex Template**
```json
{
  "message_template": "Dear {title} {name}, your order #{order_id} from {company} is ready. Track: {tracking_link}",
  "template_variables": ["title", "name", "order_id", "company", "tracking_link"]
}
```

---

## 🚀 Next Steps

1. **Create Campaign Router** (`app/modules/campaigns/router.py`)
2. **Create Campaign Service** (`app/modules/campaigns/service.py`)
3. **Implement Endpoints**:
   - `POST /api/campaigns` - Create campaign
   - `GET /api/campaigns` - List campaigns
   - `GET /api/campaigns/{id}` - Get campaign
   - `PATCH /api/campaigns/{id}` - Update campaign
   - `DELETE /api/campaigns/{id}` - Delete campaign
   - `POST /api/campaigns/{id}/send` - Send campaign

---

## 📚 Related Files

- **Model**: `app/models/campaign.py`
- **Schemas**: `app/schemas/campaign.py`
- **Router**: `app/modules/campaigns/router.py` (to create)
- **Service**: `app/modules/campaigns/service.py` (to create)

---

**Campaign schemas are ready to use! 🎉**
