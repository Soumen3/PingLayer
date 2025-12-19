# ✅ Recipients Module - Complete!

## 🎯 **What Was Created**

1. ✅ **`app/modules/recipients/service.py`** - Business logic
   - Add single recipient
   - Add bulk recipients (JSON)
   - Upload CSV file
   - List recipients (paginated)
   - Get recipient by ID
   - Delete recipient
   - Delete all recipients

2. ✅ **`app/modules/recipients/router.py`** - API endpoints
   - All CRUD operations
   - CSV upload endpoint
   - Proper validation and error handling

3. ✅ **`app/modules/recipients/__init__.py`** - Module initialization

4. ✅ **`app/main.py`** - Router registered

---

## 📋 **Available Endpoints**

### **1. Add Single Recipient**
```
POST /api/campaigns/{campaign_id}/recipients
```

**Body**:
```json
{
  "phone_number": "+1234567890",
  "name": "John Doe",
  "custom_data": {
    "company": "Acme Corp",
    "discount": "20",
    "link": "https://example.com"
  }
}
```

---

### **2. Add Bulk Recipients (JSON)**
```
POST /api/campaigns/{campaign_id}/recipients/bulk
```

**Body**:
```json
{
  "recipients": [
    {
      "phone_number": "+1234567890",
      "name": "John Doe",
      "custom_data": {"discount": "20"}
    },
    {
      "phone_number": "+9876543210",
      "name": "Jane Smith",
      "custom_data": {"discount": "15"}
    }
  ]
}
```

**Response**:
```json
{
  "campaign_id": 1,
  "added_count": 98,
  "duplicate_count": 2,
  "error_count": 0,
  "errors": null
}
```

---

### **3. Upload CSV File**
```
POST /api/campaigns/{campaign_id}/recipients/upload
Content-Type: multipart/form-data
```

**Form Data**:
- `file`: CSV file

**CSV Format**:
```csv
phone_number,name,company,discount,link
+1234567890,John Doe,Acme Corp,20,https://example.com/john
+9876543210,Jane Smith,Beta Inc,15,https://example.com/jane
```

**Response**:
```json
{
  "campaign_id": 1,
  "added_count": 2,
  "duplicate_count": 0,
  "error_count": 0,
  "errors": null
}
```

---

### **4. List Recipients**
```
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
      "custom_data": {"discount": "20"},
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

### **5. Get Single Recipient**
```
GET /api/campaigns/{campaign_id}/recipients/{recipient_id}
```

---

### **6. Delete Recipient**
```
DELETE /api/campaigns/{campaign_id}/recipients/{recipient_id}
```

---

### **7. Delete All Recipients**
```
DELETE /api/campaigns/{campaign_id}/recipients
```

**Response**:
```json
{
  "message": "Deleted 100 recipient(s)",
  "count": 100
}
```

---

## 🎯 **Complete Workflow Example**

### **Step 1: Create a Campaign**
```bash
POST /api/campaigns
{
  "name": "Summer Sale",
  "message_template": "Hi {name}, get {discount}% off!"
}

Response: { "id": 1, ... }
```

### **Step 2: Add Recipients via CSV**
```bash
POST /api/campaigns/1/recipients/upload
File: recipients.csv

Response: {
  "added_count": 100,
  "duplicate_count": 0,
  "error_count": 0
}
```

### **Step 3: View Recipients**
```bash
GET /api/campaigns/1/recipients?page=1&page_size=10

Response: {
  "recipients": [...],
  "total": 100,
  "page": 1
}
```

### **Step 4: Send Campaign**
```bash
POST /api/campaigns/1/send

Response: {
  "status": "sending",
  "total_recipients": 100
}
```

---

## 📝 **Postman Examples**

### **Upload CSV File**

1. **Method**: `POST`
2. **URL**: `http://localhost:8000/api/campaigns/1/recipients/upload`
3. **Headers**:
   ```
   Authorization: Bearer YOUR_TOKEN
   ```
4. **Body**: Select `form-data`
   - Key: `file` (change type to `File`)
   - Value: Select your CSV file
5. **Send**

---

### **Add Bulk Recipients**

1. **Method**: `POST`
2. **URL**: `http://localhost:8000/api/campaigns/1/recipients/bulk`
3. **Headers**:
   ```
   Content-Type: application/json
   Authorization: Bearer YOUR_TOKEN
   ```
4. **Body**: Select `raw` and `JSON`
   ```json
   {
     "recipients": [
       {
         "phone_number": "+1234567890",
         "name": "John Doe",
         "custom_data": {"discount": "20"}
       }
     ]
   }
   ```
5. **Send**

---

## ✨ **Key Features**

### **1. Automatic Duplicate Detection**
- Checks phone number per campaign
- Skips duplicates automatically
- Returns count in response

### **2. CSV Upload**
- Required: `phone_number` column
- Optional: `name` column
- All other columns → `custom_data`
- Validates file format
- Detailed error reporting

### **3. Custom Data**
- Any extra fields become template variables
- Used in message personalization
- Flexible JSON structure

### **4. Pagination**
- Default: 50 items per page
- Max: 100 items per page
- Returns total count and pages

### **5. Multi-Tenant Security**
- All operations verify campaign ownership
- Company-level isolation
- No cross-company access

---

## 🔍 **Validation Rules**

### **Phone Number**
```python
✅ "+1234567890"           # Valid
✅ "+91 9876543210"        # Spaces removed automatically
✅ "+1-234-567-8900"       # Dashes removed
❌ "1234567890"            # Missing +
❌ "+123"                  # Too short
❌ "invalid"               # Not a number
```

### **Bulk Upload**
```python
✅ 1-10,000 recipients     # Valid
❌ 10,001+ recipients      # Too many (split into batches)
```

### **CSV File**
```python
✅ .csv extension          # Valid
❌ .xlsx, .txt, etc.       # Invalid
✅ phone_number column     # Required
❌ Missing phone_number    # Error
```

---

## 🐛 **Error Handling**

### **Campaign Not Found**
```json
{
  "detail": "Campaign not found"
}
```
**Status**: 404

### **Duplicate Recipient**
```json
{
  "detail": "Recipient with phone number +1234567890 already exists in this campaign"
}
```
**Status**: 400

### **Invalid CSV**
```json
{
  "detail": "CSV must have a 'phone_number' column"
}
```
**Status**: 400

### **CSV Row Errors**
```json
{
  "campaign_id": 1,
  "added_count": 98,
  "error_count": 2,
  "errors": [
    "Row 5: Missing phone_number",
    "Row 12: Invalid phone number format"
  ]
}
```
**Status**: 200 (partial success)

---

## 📊 **Response Examples**

### **Success - Single Recipient**
```json
{
  "id": 1,
  "campaign_id": 1,
  "phone_number": "+1234567890",
  "name": "John Doe",
  "custom_data": {
    "company": "Acme Corp",
    "discount": "20"
  },
  "created_at": "2024-07-01T10:00:00"
}
```

### **Success - Bulk Upload**
```json
{
  "campaign_id": 1,
  "added_count": 100,
  "duplicate_count": 5,
  "error_count": 0,
  "errors": null
}
```

### **Partial Success - With Errors**
```json
{
  "campaign_id": 1,
  "added_count": 95,
  "duplicate_count": 3,
  "error_count": 2,
  "errors": [
    "Row 10: Missing phone_number",
    "Row 25: Invalid phone number format"
  ]
}
```

---

## 🎯 **Quick Reference**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/campaigns/{id}/recipients` | POST | Add single recipient |
| `/api/campaigns/{id}/recipients/bulk` | POST | Add multiple (JSON) |
| `/api/campaigns/{id}/recipients/upload` | POST | Upload CSV file |
| `/api/campaigns/{id}/recipients` | GET | List recipients |
| `/api/campaigns/{id}/recipients/{rid}` | GET | Get one recipient |
| `/api/campaigns/{id}/recipients/{rid}` | DELETE | Delete one |
| `/api/campaigns/{id}/recipients` | DELETE | Delete all |

---

## 📚 **Related Documentation**

- **Schemas**: `app/schemas/recipient.py`
- **Models**: `app/models/recipient.py`
- **Service**: `app/modules/recipients/service.py`
- **Router**: `app/modules/recipients/router.py`
- **Guide**: `RECIPIENT_DATA_GUIDE.md`

---

**Recipients module is complete and ready to use! 🎉**

Test it at: http://localhost:8000/docs
