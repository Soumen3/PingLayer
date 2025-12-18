# 📥 Recipient Data - Complete Guide

## 🎯 **Three Ways to Add Recipients**

### **1. CSV File Upload** (Recommended for Bulk)
### **2. Bulk JSON** (Programmatic)
### **3. Single Recipient** (Manual Entry)

---

## 📄 **Method 1: CSV File Upload**

### **CSV Format**

**Required Column**:
- `phone_number` - Phone with country code (e.g., +1234567890)

**Optional Columns**:
- `name` - Recipient name
- Any other columns → Becomes `custom_data` for template variables

### **Example CSV File**

```csv
phone_number,name,company,link,discount
+1234567890,John Doe,Acme Corp,https://example.com/john,20%
+9876543210,Jane Smith,Beta Inc,https://example.com/jane,15%
+1122334455,Bob Wilson,Gamma LLC,https://example.com/bob,25%
```

### **API Endpoint**

```python
POST /api/campaigns/{campaign_id}/recipients/upload
Content-Type: multipart/form-data

# Form data:
file: recipients.csv
```

### **Example with Python requests**

```python
import requests

url = "http://localhost:8000/api/campaigns/1/recipients/upload"
headers = {"Authorization": "Bearer YOUR_TOKEN"}

with open("recipients.csv", "rb") as f:
    files = {"file": ("recipients.csv", f, "text/csv")}
    response = requests.post(url, headers=headers, files=files)

print(response.json())
# {
#   "campaign_id": 1,
#   "added_count": 98,
#   "duplicate_count": 2,
#   "error_count": 0
# }
```

### **Example with cURL**

```bash
curl -X POST \
  http://localhost:8000/api/campaigns/1/recipients/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@recipients.csv"
```

### **Router Implementation**

```python
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import csv
import io

router = APIRouter()

@router.post("/{campaign_id}/recipients/upload")
async def upload_recipients(
    campaign_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Upload recipients from CSV file.
    
    CSV Format:
    - Required: phone_number
    - Optional: name, and any custom fields
    """
    # Verify campaign exists and belongs to user's company
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.company_id == current_user.company_id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Read CSV file
    contents = await file.read()
    csv_data = contents.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(csv_data))
    
    added_count = 0
    duplicate_count = 0
    error_count = 0
    errors = []
    
    for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (header is row 1)
        try:
            # Validate required field
            if 'phone_number' not in row or not row['phone_number']:
                errors.append(f"Row {row_num}: Missing phone_number")
                error_count += 1
                continue
            
            phone_number = row['phone_number'].strip()
            name = row.get('name', '').strip() or None
            
            # Get custom data (all columns except phone_number and name)
            custom_data = {}
            for key, value in row.items():
                if key not in ['phone_number', 'name'] and value:
                    custom_data[key] = value.strip()
            
            # Check if recipient already exists
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
                custom_data=custom_data if custom_data else None
            )
            db.add(recipient)
            added_count += 1
            
        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")
            error_count += 1
    
    # Update campaign total_recipients
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
```

---

## 📦 **Method 2: Bulk JSON**

### **API Endpoint**

```python
POST /api/campaigns/{campaign_id}/recipients/bulk
Content-Type: application/json
```

### **Request Body**

```json
{
  "recipients": [
    {
      "phone_number": "+1234567890",
      "name": "John Doe",
      "custom_data": {
        "company": "Acme Corp",
        "link": "https://example.com/john",
        "discount": "20%"
      }
    },
    {
      "phone_number": "+9876543210",
      "name": "Jane Smith",
      "custom_data": {
        "company": "Beta Inc",
        "link": "https://example.com/jane",
        "discount": "15%"
      }
    }
  ]
}
```

### **Router Implementation**

```python
@router.post("/{campaign_id}/recipients/bulk")
def add_recipients_bulk(
    campaign_id: int,
    data: RecipientBulkCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Add multiple recipients via JSON"""
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.company_id == current_user.company_id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    added_count = 0
    duplicate_count = 0
    
    for recipient_data in data.recipients:
        # Check for duplicates
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
            custom_data=recipient_data.custom_data
        )
        db.add(recipient)
        added_count += 1
    
    # Update campaign total
    campaign.total_recipients = db.query(Recipient).filter(
        Recipient.campaign_id == campaign_id
    ).count()
    
    db.commit()
    
    return RecipientUploadResponse(
        campaign_id=campaign_id,
        added_count=added_count,
        duplicate_count=duplicate_count,
        error_count=0
    )
```

---

## 👤 **Method 3: Single Recipient**

### **API Endpoint**

```python
POST /api/campaigns/{campaign_id}/recipients
Content-Type: application/json
```

### **Request Body**

```json
{
  "phone_number": "+1234567890",
  "name": "John Doe",
  "custom_data": {
    "company": "Acme Corp",
    "link": "https://example.com/offer"
  }
}
```

### **Router Implementation**

```python
@router.post("/{campaign_id}/recipients")
def add_recipient(
    campaign_id: int,
    recipient_data: RecipientCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Add a single recipient"""
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.company_id == current_user.company_id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Check for duplicate
    existing = db.query(Recipient).filter(
        Recipient.campaign_id == campaign_id,
        Recipient.phone_number == recipient_data.phone_number
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Recipient already exists")
    
    # Create recipient
    recipient = Recipient(
        campaign_id=campaign_id,
        phone_number=recipient_data.phone_number,
        name=recipient_data.name,
        custom_data=recipient_data.custom_data
    )
    db.add(recipient)
    
    # Update campaign total
    campaign.total_recipients += 1
    
    db.commit()
    db.refresh(recipient)
    
    return RecipientResponse.from_orm(recipient)
```

---

## 🔍 **Get Recipients**

### **List All Recipients for a Campaign**

```python
GET /api/campaigns/{campaign_id}/recipients?page=1&page_size=50
```

**Response**:
```json
{
  "recipients": [
    {
      "id": 1,
      "campaign_id": 1,
      "phone_number": "+1234567890",
      "name": "John Doe",
      "custom_data": {
        "company": "Acme Corp"
      },
      "created_at": "2024-07-01T10:00:00"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 50,
  "total_pages": 2
}
```

---

## 📊 **How Custom Data Works**

### **In CSV**:
```csv
phone_number,name,company,link,discount
+1234567890,John,Acme,https://...,20%
```

### **Becomes**:
```json
{
  "phone_number": "+1234567890",
  "name": "John",
  "custom_data": {
    "company": "Acme",
    "link": "https://...",
    "discount": "20%"
  }
}
```

### **Used in Template**:
```
Message Template:
"Hi {name}, {company} has a {discount} discount! Visit {link}"

Rendered Message:
"Hi John, Acme has a 20% discount! Visit https://..."
```

---

## ✅ **Phone Number Validation**

### **Valid Formats**:
- ✅ `+1234567890` (with country code)
- ✅ `+91 9876543210` (spaces removed automatically)
- ✅ `+1-234-567-8900` (dashes removed)

### **Invalid Formats**:
- ❌ `1234567890` (missing +)
- ❌ `+123` (too short)
- ❌ `+12345678901234567890` (too long)

---

## 🎯 **Complete Flow Example**

```python
# 1. Create campaign
campaign = create_campaign(...)

# 2. Upload recipients via CSV
upload_recipients_csv(campaign.id, "recipients.csv")

# 3. Campaign now has recipients
campaign.total_recipients  # 100

# 4. Send campaign
send_campaign(campaign.id)

# 5. Messages sent with personalized data
# Each recipient gets message with their custom_data
```

---

## 📝 **Summary**

| Method | Use Case | Max Recipients | Format |
|--------|----------|----------------|--------|
| **CSV Upload** | Bulk import from Excel/Sheets | Unlimited | CSV file |
| **Bulk JSON** | Programmatic/API integration | 10,000/request | JSON array |
| **Single** | Manual entry/testing | 1 | JSON object |

**Recommended**: Use **CSV Upload** for most cases - it's the easiest for users!

---

**Recipient schemas and examples are ready! 🎉**
