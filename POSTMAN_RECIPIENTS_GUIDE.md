# 📮 Postman Guide - Adding Recipients

## 🎯 **Complete Step-by-Step Guide**

---

## 📋 **Prerequisites**

1. ✅ You have a campaign created (campaign ID)
2. ✅ You have an authentication token (from login/register)
3. ✅ Server is running at `http://localhost:8000`

---

## 🔐 **Step 1: Get Your Token**

First, login to get your authentication token:

### **Login Request**

**Method**: `POST`  
**URL**: `http://localhost:8000/api/auth/login`

**Headers**:
```
Content-Type: application/json
```

**Body** (select `raw` and `JSON`):
```json
{
  "email": "your@email.com",
  "password": "YourPassword123!"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": { ... }
}
```

**⚠️ COPY THE `access_token` - you'll need it for all recipient requests!**

---

## 📝 **Method 1: Add Single Recipient**

### **Postman Setup**

1. **Create New Request**
   - Click "New" → "Request"
   - Name: `Add Single Recipient`
   - Save to your collection

2. **Set Method & URL**
   - Method: `POST`
   - URL: `http://localhost:8000/api/campaigns/1/recipients`
   - (Replace `1` with your actual campaign ID)

3. **Set Headers**
   - Click **Headers** tab
   - Add these headers:

| Key | Value |
|-----|-------|
| `Content-Type` | `application/json` |
| `Authorization` | `Bearer YOUR_TOKEN_HERE` |

⚠️ Replace `YOUR_TOKEN_HERE` with your actual token from Step 1!

4. **Set Body**
   - Click **Body** tab
   - Select `raw`
   - Select `JSON` from the dropdown (right side)
   - Paste this JSON:

```json
{
  "phone_number": "+919382532340",
  "name": "Soumen Das",
  "email": "soumen@example.com"
}
```

5. **Send Request**
   - Click **Send** button
   - Check the response!

### **Expected Response** (201 Created):
```json
{
  "id": 1,
  "campaign_id": 1,
  "phone_number": "+919382532340",
  "name": "Soumen Das",
  "email": "soumen@example.com",
  "custom_data": null,
  "created_at": "2025-12-19T15:16:36.123456"
}
```

---

## 📦 **Method 2: Add Multiple Recipients (Bulk JSON)**

### **Postman Setup**

1. **Create New Request**
   - Name: `Add Bulk Recipients`

2. **Set Method & URL**
   - Method: `POST`
   - URL: `http://localhost:8000/api/campaigns/1/recipients/bulk`

3. **Set Headers**

| Key | Value |
|-----|-------|
| `Content-Type` | `application/json` |
| `Authorization` | `Bearer YOUR_TOKEN_HERE` |

4. **Set Body**
   - Click **Body** tab
   - Select `raw`
   - Select `JSON`
   - Paste this:

```json
{
  "recipients": [
    {
      "phone_number": "+919382532340",
      "name": "Soumen Das",
      "email": "soumen@example.com"
    },
    {
      "phone_number": "+911234567890",
      "name": "John Doe",
      "email": "john@example.com"
    },
    {
      "phone_number": "+919876543210",
      "name": "Jane Smith",
      "email": "jane@example.com"
    }
  ]
}
```

5. **Send Request**

### **Expected Response** (200 OK):
```json
{
  "campaign_id": 1,
  "added_count": 3,
  "duplicate_count": 0,
  "error_count": 0,
  "errors": null
}
```

---

## 📄 **Method 3: Upload CSV File**

### **Step A: Create CSV File**

Create a file named `recipients.csv` with this content:

```csv
phone_number,name,email,company,discount
+919382532340,Soumen Das,soumen@example.com,Tech Corp,20
+911234567890,John Doe,john@example.com,Acme Inc,15
+919876543210,Jane Smith,jane@example.com,Beta LLC,25
```

**Save this file** to your computer (e.g., Desktop).

### **Step B: Postman Setup**

1. **Create New Request**
   - Name: `Upload Recipients CSV`

2. **Set Method & URL**
   - Method: `POST`
   - URL: `http://localhost:8000/api/campaigns/1/recipients/upload`

3. **Set Headers**
   - Click **Headers** tab
   - Add ONLY this header:

| Key | Value |
|-----|-------|
| `Authorization` | `Bearer YOUR_TOKEN_HERE` |

⚠️ **DO NOT** add `Content-Type` header - Postman will set it automatically!

4. **Set Body**
   - Click **Body** tab
   - Select `form-data` (NOT raw!)
   - Add a new field:
     - **Key**: `file`
     - **Type**: Change from "Text" to "File" (click dropdown on right)
     - **Value**: Click "Select Files" and choose your `recipients.csv`

**Visual Guide**:
```
┌─────────────────────────────────────────┐
│ Body Tab                                │
├─────────────────────────────────────────┤
│ ( ) none  ( ) form-data  ( ) raw       │
│           (•) ← Select this             │
├─────────────────────────────────────────┤
│ KEY          │ VALUE         │ TYPE     │
├──────────────┼───────────────┼──────────┤
│ file         │ Select Files  │ File ▼   │
│              │ recipients.csv│          │
└─────────────────────────────────────────┘
```

5. **Send Request**

### **Expected Response** (200 OK):
```json
{
  "campaign_id": 1,
  "added_count": 3,
  "duplicate_count": 0,
  "error_count": 0,
  "errors": null
}
```

---

## 🎨 **Advanced: With Custom Data**

### **Example with Custom Template Variables**

```json
{
  "phone_number": "+919382532340",
  "name": "Soumen Das",
  "email": "soumen@example.com",
  "custom_data": {
    "company": "Tech Corp",
    "position": "Developer",
    "discount": "25%",
    "link": "https://example.com/offer/soumen"
  }
}
```

**Use Case**: These custom fields can be used in your message template:
```
"Hi {name}, {company} has a special {discount} discount for you! Visit {link}"
```

---

## 🔍 **Troubleshooting**

### **Error: 401 Unauthorized**
```json
{
  "detail": "Invalid or expired token"
}
```

**Solution**: 
1. Login again to get a fresh token
2. Make sure you're using `Bearer YOUR_TOKEN` (with space after Bearer)
3. Check that token is copied completely

---

### **Error: 400 Bad Request - Duplicate**
```json
{
  "detail": "Recipient with phone number +919382532340 already exists in this campaign"
}
```

**Solution**: This phone number is already in the campaign. Use a different number or delete the existing recipient first.

---

### **Error: 404 Not Found**
```json
{
  "detail": "Campaign not found"
}
```

**Solution**: 
1. Check the campaign ID in the URL
2. Make sure the campaign belongs to your company
3. Create a campaign first if needed

---

### **Error: 422 Validation Error**
```json
{
  "detail": [
    {
      "loc": ["body", "phone_number"],
      "msg": "Phone number must start with + and country code",
      "type": "value_error"
    }
  ]
}
```

**Solution**: Phone number must:
- Start with `+`
- Include country code
- Be 10-15 digits
- Example: `+919382532340`

---

## 📊 **Complete Example Workflow**

### **1. Login**
```
POST http://localhost:8000/api/auth/login
Body: { "email": "...", "password": "..." }
→ Copy access_token
```

### **2. Create Campaign**
```
POST http://localhost:8000/api/campaigns
Headers: Authorization: Bearer TOKEN
Body: { "name": "Summer Sale", "message_template": "Hi {name}!" }
→ Note campaign ID (e.g., 1)
```

### **3. Add Recipients**
```
POST http://localhost:8000/api/campaigns/1/recipients
Headers: Authorization: Bearer TOKEN
Body: { "phone_number": "+919382532340", "name": "Soumen" }
→ Recipient added!
```

### **4. Verify Recipients**
```
GET http://localhost:8000/api/campaigns/1/recipients
Headers: Authorization: Bearer TOKEN
→ See all recipients
```

---

## 💡 **Pro Tips**

### **Tip 1: Save Token as Environment Variable**

1. Click the eye icon (👁️) in top right
2. Click "Add" to create new environment
3. Name: `PingLayer Local`
4. Add variable:
   - Variable: `auth_token`
   - Value: `YOUR_TOKEN_HERE`
5. Save

Now use `{{auth_token}}` in your requests:
```
Authorization: Bearer {{auth_token}}
```

### **Tip 2: Auto-Save Token After Login**

In your login request, go to **Tests** tab and add:
```javascript
var jsonData = pm.response.json();
pm.environment.set("auth_token", jsonData.access_token);
```

Now the token is automatically saved after login!

### **Tip 3: Save Campaign ID**

After creating a campaign, in **Tests** tab:
```javascript
var jsonData = pm.response.json();
pm.environment.set("campaign_id", jsonData.id);
```

Then use in URLs:
```
http://localhost:8000/api/campaigns/{{campaign_id}}/recipients
```

---

## 📝 **Quick Reference**

### **Single Recipient**
```
POST /api/campaigns/{id}/recipients
Headers: Authorization: Bearer TOKEN, Content-Type: application/json
Body: { "phone_number": "+91...", "name": "...", "email": "..." }
```

### **Bulk Recipients**
```
POST /api/campaigns/{id}/recipients/bulk
Headers: Authorization: Bearer TOKEN, Content-Type: application/json
Body: { "recipients": [...] }
```

### **CSV Upload**
```
POST /api/campaigns/{id}/recipients/upload
Headers: Authorization: Bearer TOKEN
Body: form-data with file field
```

---

## 🎯 **Field Reference**

| Field | Required | Format | Example |
|-------|----------|--------|---------|
| `phone_number` | ✅ Yes | `+` + country code + number | `"+919382532340"` |
| `name` | ❌ No | Any string | `"Soumen Das"` |
| `email` | ❌ No | Valid email | `"soumen@example.com"` |
| `custom_data` | ❌ No | JSON object | `{"company": "Tech"}` |

---

## 🎬 **Video Tutorial Steps**

1. ✅ Open Postman
2. ✅ Create new request
3. ✅ Set method to POST
4. ✅ Enter URL: `http://localhost:8000/api/campaigns/1/recipients`
5. ✅ Add Headers:
   - `Content-Type: application/json`
   - `Authorization: Bearer YOUR_TOKEN`
6. ✅ Go to Body tab
7. ✅ Select `raw` and `JSON`
8. ✅ Paste JSON data
9. ✅ Click Send
10. ✅ Check response!

---

**You're all set! Start adding recipients! 🚀**

Need help? Check the Swagger docs at: http://localhost:8000/docs
