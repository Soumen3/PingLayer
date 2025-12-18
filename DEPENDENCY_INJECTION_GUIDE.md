# 🔧 FastAPI Dependency Injection - How It Works

## ❓ **Your Question**
> `get_current_user` takes two arguments, how will they be passed?

## ✅ **Answer: FastAPI Handles It Automatically!**

### **The Dependency Function**
```python
# In app/core/dependencies.py
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),  # ← Auto-injected
    db: Session = Depends(get_db)  # ← Auto-injected
) -> CurrentUser:
    # Extract token, validate, return CurrentUser
    ...
```

### **How FastAPI Works**

When you use `Depends(get_current_user)` in a route:

```python
@router.get("/campaigns")
def list_campaigns(
    current_user: CurrentUser = Depends(get_current_user),  # ← You only specify this
    db: Session = Depends(get_db)
):
    # FastAPI automatically:
    # 1. Calls security() to get credentials from Authorization header
    # 2. Calls get_db() to get database session
    # 3. Passes both to get_current_user(credentials, db)
    # 4. Returns CurrentUser object to your route
    pass
```

---

## 🎯 **Dependency Chain**

```
Your Route
    ↓
Depends(get_current_user)
    ↓
├─ Depends(security) → Gets Authorization header
└─ Depends(get_db) → Gets database session
    ↓
get_current_user(credentials, db)
    ↓
Returns CurrentUser object
    ↓
Injected into your route
```

---

## 📝 **Correct Usage in Your Router**

### **✅ CORRECT - Using CurrentUser**
```python
from app.core.dependencies import get_current_user, CurrentUser

@router.post("/campaigns")
def create_campaign(
    campaign: CampaignCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)  # ← Returns CurrentUser object
):
    # Access user info
    user_id = current_user.user_id
    company_id = current_user.company_id
    email = current_user.email
    
    # Create campaign
    db_campaign = Campaign(
        name=campaign.name,
        company_id=current_user.company_id,  # ← Use company_id from token
        created_by=current_user.user_id
    )
    db.add(db_campaign)
    db.commit()
    return db_campaign
```

### **❌ WRONG - Importing User model**
```python
from app.schemas.user import User  # ❌ Wrong! This is a schema, not what you need

@router.post("/campaigns")
def create_campaign(
    user: User = Depends(get_current_user)  # ❌ Wrong type annotation
):
    # This won't work correctly
    pass
```

---

## 🔧 **Fix Your Router**

### **Current Issues in Your Code**

1. **Wrong import**: `from app.schemas.user import User`
   - Should be: `from app.core.dependencies import CurrentUser`

2. **Wrong type annotation**: `user: User`
   - Should be: `current_user: CurrentUser`

3. **Missing imports**: `Optional` and `List`

### **Fixed Router Code**

```python
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
from app.core.dependencies import get_current_user, CurrentUser  # ← Correct import
from app.models.campaign import CampaignStatus

router = APIRouter()


@router.post("/campaigns", response_model=CampaignResponse)
def create_campaign(
    campaign: CampaignCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)  # ← Correct type
):
    """Create a new campaign"""
    logger.info(f"Creating campaign: {campaign.name} for user {current_user.user_id}")
    
    db_campaign = service.create_campaign(db, campaign, current_user)
    return campaign_to_response(db_campaign)


@router.get("/campaigns", response_model=List[CampaignResponse])
def list_campaigns(
    status: Optional[CampaignStatus] = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)  # ← Correct type
):
    """List all campaigns for the current user's company"""
    logger.info(f"Listing campaigns for user {current_user.user_id}")
    
    campaigns = service.list_campaigns(db, current_user, status)
    return [campaign_to_response(c) for c in campaigns]


@router.get("/campaigns/{campaign_id}", response_model=CampaignResponse)
def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)  # ← Correct type
):
    """Get a specific campaign"""
    logger.info(f"Getting campaign {campaign_id}")
    
    campaign = service.get_campaign_by_id(db, current_user, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return campaign_to_response(campaign)


@router.patch("/campaigns/{campaign_id}", response_model=CampaignResponse)
def update_campaign(
    campaign_id: int,
    campaign: CampaignUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)  # ← Correct type
):
    """Update a campaign"""
    logger.info(f"Updating campaign {campaign_id}")
    
    db_campaign = service.update_campaign(db, current_user, campaign_id, campaign)
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return campaign_to_response(db_campaign)


@router.post("/campaigns/{campaign_id}/send")
def send_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)  # ← Correct type
):
    """Send a campaign"""
    logger.info(f"Sending campaign {campaign_id}")
    
    result = service.send_campaign(db, current_user, campaign_id)
    if not result:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return result


@router.post("/campaigns/{campaign_id}/cancel")
def cancel_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)  # ← Correct type
):
    """Cancel a campaign"""
    logger.info(f"Canceling campaign {campaign_id}")
    
    result = service.cancel_campaign(db, current_user, campaign_id)
    if not result:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return result
```

---

## 🎓 **Understanding CurrentUser**

### **What is CurrentUser?**
It's a simple class that holds authenticated user info:

```python
class CurrentUser:
    def __init__(self, user_id: int, company_id: int, email: str):
        self.user_id = user_id
        self.company_id = company_id
        self.email = email
```

### **How to Use It**
```python
def my_route(current_user: CurrentUser = Depends(get_current_user)):
    # Access properties
    print(current_user.user_id)      # 1
    print(current_user.company_id)   # 1
    print(current_user.email)        # "user@example.com"
```

---

## 🔐 **Authentication Flow**

```
1. Client sends request with header:
   Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

2. FastAPI calls Depends(security)
   → Extracts token from header

3. FastAPI calls Depends(get_db)
   → Gets database session

4. FastAPI calls get_current_user(credentials, db)
   → Validates token
   → Checks user exists
   → Returns CurrentUser object

5. FastAPI injects CurrentUser into your route
   → You can use current_user.user_id, etc.
```

---

## ✅ **Summary**

| What | How |
|------|-----|
| **Dependencies** | FastAPI handles them automatically |
| **Correct Import** | `from app.core.dependencies import CurrentUser` |
| **Correct Type** | `current_user: CurrentUser` |
| **Access User ID** | `current_user.user_id` |
| **Access Company ID** | `current_user.company_id` |
| **Access Email** | `current_user.email` |

**You don't need to pass the arguments manually - FastAPI's dependency injection does it for you!** 🎉
