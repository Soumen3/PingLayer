# ✅ Email Support Added to Recipients

## 🎯 **What Was Updated**

Added email field support to the recipients module so users can now include email addresses when adding recipients.

---

## 📝 **Files Modified**

1. ✅ **`app/schemas/recipient.py`**
   - Added `email` field to `RecipientCreate` schema
   - Added `email` field to `RecipientResponse` schema
   - Added email validation

2. ✅ **`app/modules/recipients/service.py`**
   - Updated `add_single_recipient()` to save email
   - Updated `add_bulk_recipients()` to save email
   - Updated `upload_recipients_csv()` to parse email from CSV

3. ✅ **`app/models/recipient.py`** (already had email field)
   - No changes needed - model already supported email

---

## 📋 **How to Use**

### **1. Add Single Recipient with Email**

```json
POST /api/campaigns/1/recipients
{
  "phone_number": "+919382532340",
  "name": "Soumen",
  "email": "soumen@example.com"
}
```

**Response**:
```json
{
  "id": 1,
  "campaign_id": 1,
  "phone_number": "+919382532340",
  "name": "Soumen",
  "email": "soumen@example.com",
  "custom_data": null,
  "created_at": "2025-12-18T06:54:20"
}
```

---

### **2. Bulk Recipients with Email**

```json
POST /api/campaigns/1/recipients/bulk
{
  "recipients": [
    {
      "phone_number": "+1234567890",
      "name": "John Doe",
      "email": "john@example.com"
    },
    {
      "phone_number": "+9876543210",
      "name": "Jane Smith",
      "email": "jane@example.com"
    }
  ]
}
```

---

### **3. CSV Upload with Email**

**CSV File** (`recipients.csv`):
```csv
phone_number,name,email,company,discount
+1234567890,John Doe,john@example.com,Acme Corp,20
+9876543210,Jane Smith,jane@example.com,Beta Inc,15
```

**Upload**:
```
POST /api/campaigns/1/recipients/upload
Content-Type: multipart/form-data
file: recipients.csv
```

**What happens**:
- `phone_number` → Required field
- `name` → Optional, saved to name field
- `email` → Optional, saved to email field
- `company`, `discount` → Saved to custom_data

---

## ✅ **Email Validation**

The email field is validated:

```python
✅ "john@example.com"           # Valid
✅ "user.name@company.co.uk"    # Valid
✅ "test+tag@gmail.com"         # Valid
❌ "invalid-email"              # Invalid
❌ "missing@domain"             # Invalid
❌ "@example.com"               # Invalid
```

**Validation Rules**:
- Basic email format check
- Automatically converted to lowercase
- Optional field (can be null)

---

## 📊 **Complete Example**

### **Request**:
```json
POST /api/campaigns/1/recipients
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "phone_number": "+919382532340",
  "name": "Soumen Das",
  "email": "soumen@company.com",
  "custom_data": {
    "company": "Tech Corp",
    "position": "Developer",
    "discount": "25%"
  }
}
```

### **Response**:
```json
{
  "id": 1,
  "campaign_id": 1,
  "phone_number": "+919382532340",
  "name": "Soumen Das",
  "email": "soumen@company.com",
  "custom_data": {
    "company": "Tech Corp",
    "position": "Developer",
    "discount": "25%"
  },
  "created_at": "2025-12-18T12:54:20.123456"
}
```

---

## 🎨 **Use Cases**

### **1. Email Notifications**
Store email for sending email notifications alongside WhatsApp messages.

### **2. User Identification**
Use email as an additional identifier for recipients.

### **3. Multi-Channel Campaigns**
Support both WhatsApp and email campaigns with the same recipient list.

### **4. Data Enrichment**
Collect more information about recipients for better targeting.

---

## 📝 **Field Summary**

| Field | Required | Type | Description | Example |
|-------|----------|------|-------------|---------|
| `phone_number` | ✅ Yes | string | Phone with country code | `"+919382532340"` |
| `name` | ❌ No | string | Recipient name | `"Soumen Das"` |
| `email` | ❌ No | string | Email address | `"soumen@example.com"` |
| `custom_data` | ❌ No | object | Template variables | `{"company": "Tech"}` |

---

## 🔄 **CSV Format Updated**

### **Old Format** (still works):
```csv
phone_number,name,company,discount
+1234567890,John Doe,Acme Corp,20
```

### **New Format** (with email):
```csv
phone_number,name,email,company,discount
+1234567890,John Doe,john@example.com,Acme Corp,20
+9876543210,Jane Smith,jane@example.com,Beta Inc,15
```

**Note**: Email column is optional. If not provided, email will be null.

---

## ✨ **Benefits**

1. ✅ **Flexible** - Email is optional, doesn't break existing code
2. ✅ **Validated** - Automatic email format validation
3. ✅ **Normalized** - Emails converted to lowercase
4. ✅ **CSV Support** - Works with CSV uploads
5. ✅ **Backward Compatible** - Existing recipients without email still work

---

## 🧪 **Testing**

### **Test 1: Add with Email**
```bash
curl -X POST http://localhost:8000/api/campaigns/1/recipients \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+919382532340",
    "name": "Soumen",
    "email": "soumen@example.com"
  }'
```

### **Test 2: Add without Email**
```bash
curl -X POST http://localhost:8000/api/campaigns/1/recipients \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+919382532340",
    "name": "Soumen"
  }'
```

Both should work! ✅

---

**Email support is now fully integrated! 🎉**

Test it at: http://localhost:8000/docs
