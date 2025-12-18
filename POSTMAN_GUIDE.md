# 📮 Postman Guide - PingLayer API

## 🎯 **Complete Step-by-Step Guide for Postman**

---

## 📋 **Table of Contents**
1. [Initial Setup](#initial-setup)
2. [Register a User](#step-1-register-a-user)
3. [Login to Get Token](#step-2-login-to-get-token)
4. [Create a Campaign](#step-3-create-a-campaign)
5. [List Campaigns](#step-4-list-campaigns)
6. [Get Campaign by ID](#step-5-get-campaign-by-id)
7. [Update Campaign](#step-6-update-campaign)
8. [Add Recipients](#step-7-add-recipients)
9. [Send Campaign](#step-8-send-campaign)

---

## 🔧 **Initial Setup**

### **Base URL**
```
http://localhost:8000
```

### **Create a New Collection**
1. Open Postman
2. Click "New" → "Collection"
3. Name it: `PingLayer API`
4. Save

---

## 📝 **Step 1: Register a User**

### **Request Details**
- **Method**: `POST`
- **URL**: `http://localhost:8000/api/auth/register`
- **Headers**: 
  ```
  Content-Type: application/json
  ```
- **Body**: Select `raw` and `JSON`

### **Body (JSON)**
```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "company_name": "Acme Corp"
}
```

### **Postman Steps**
1. Click "New" → "Request"
2. Name: `Register User`
3. Select method: `POST`
4. Enter URL: `http://localhost:8000/api/auth/register`
5. Go to **Headers** tab:
   - Key: `Content-Type`
   - Value: `application/json`
6. Go to **Body** tab:
   - Select `raw`
   - Select `JSON` from dropdown
   - Paste the JSON above
7. Click **Send**

### **Expected Response** (200 OK)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "john@example.com",
    "full_name": "John Doe",
    "company_id": 1,
    "is_active": true,
    "is_admin": true
  },
  "company": {
    "id": 1,
    "name": "Acme Corp",
    "slug": "acme-corp"
  }
}
```

### **⚠️ IMPORTANT: Save the Token!**
Copy the `access_token` value - you'll need it for all other requests!

---

## 🔐 **Step 2: Login to Get Token**

### **Request Details**
- **Method**: `POST`
- **URL**: `http://localhost:8000/api/auth/login`
- **Headers**: 
  ```
  Content-Type: application/json
  ```
- **Body**: Select `raw` and `JSON`

### **Body (JSON)**
```json
{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

### **Expected Response** (200 OK)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": { ... },
  "company": { ... }
}
```

---

## 📝 **Step 3: Create a Campaign**

### **Request Details**
- **Method**: `POST`
- **URL**: `http://localhost:8000/api/campaigns`
- **Headers**: 
  ```
  Content-Type: application/json
  Authorization: Bearer YOUR_TOKEN_HERE
  ```
- **Body**: Select `raw` and `JSON`

### **Postman Steps**

#### **1. Set Headers**
Go to **Headers** tab and add:

| Key | Value |
|-----|-------|
| `Content-Type` | `application/json` |
| `Authorization` | `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |

⚠️ **Important**: Replace `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` with your actual token from Step 1!

#### **2. Set Body**
Go to **Body** tab:
- Select `raw`
- Select `JSON` from dropdown
- Paste one of the examples below

### **Body Examples**

#### **Example 1: Minimal Campaign**
```json
{
  "name": "Summer Sale 2024",
  "message_template": "Hi {name}, check out our summer sale! Visit {link}"
}
```

#### **Example 2: With Description**
```json
{
  "name": "Weekend Flash Sale",
  "description": "Flash sale for premium customers",
  "message_template": "Hi {name}, get {discount}% off! Shop now: {link}"
}
```

#### **Example 3: With Template Variables**
```json
{
  "name": "Product Launch",
  "description": "New product launch announcement",
  "message_template": "Hi {name}, {company} is launching {product}! Get {discount}% off. Visit: {link}",
  "template_variables": ["name", "company", "product", "discount", "link"]
}
```

#### **Example 4: Scheduled Campaign**
```json
{
  "name": "Scheduled Sale",
  "description": "Sale scheduled for next week",
  "message_template": "Hi {name}, our sale starts now! {discount}% off. Visit: {link}",
  "template_variables": ["name", "discount", "link"],
  "scheduled_at": "2024-12-25T10:00:00"
}
```

### **Expected Response** (201 Created)
```json
{
  "id": 1,
  "name": "Summer Sale 2024",
  "description": null,
  "company_id": 1,
  "created_by": 1,
  "status": "draft",
  "message_template": "Hi {name}, check out our summer sale! Visit {link}",
  "template_variables": null,
  "scheduled_at": null,
  "started_at": null,
  "completed_at": null,
  "stats": {
    "total_recipients": 0,
    "sent_count": 0,
    "delivered_count": 0,
    "failed_count": 0,
    "success_rate": 0.0,
    "progress_percentage": 0.0
  },
  "is_editable": true,
  "is_sendable": false,
  "created_at": "2024-07-01T10:00:00",
  "updated_at": "2024-07-01T10:00:00"
}
```

---

## 📋 **Step 4: List Campaigns**

### **Request Details**
- **Method**: `GET`
- **URL**: `http://localhost:8000/api/campaigns`
- **Headers**: 
  ```
  Authorization: Bearer YOUR_TOKEN_HERE
  ```

### **Postman Steps**
1. Method: `GET`
2. URL: `http://localhost:8000/api/campaigns`
3. **Headers** tab:
   - Key: `Authorization`
   - Value: `Bearer YOUR_TOKEN_HERE`
4. Click **Send**

### **Optional Query Parameters**
You can filter by status:
```
http://localhost:8000/api/campaigns?status=draft
http://localhost:8000/api/campaigns?status=scheduled
http://localhost:8000/api/campaigns?status=completed
```

### **Expected Response** (200 OK)
```json
[
  {
    "id": 1,
    "name": "Summer Sale 2024",
    "status": "draft",
    ...
  },
  {
    "id": 2,
    "name": "Weekend Flash Sale",
    "status": "scheduled",
    ...
  }
]
```

---

## 🔍 **Step 5: Get Campaign by ID**

### **Request Details**
- **Method**: `GET`
- **URL**: `http://localhost:8000/api/campaigns/1`
- **Headers**: 
  ```
  Authorization: Bearer YOUR_TOKEN_HERE
  ```

### **Postman Steps**
1. Method: `GET`
2. URL: `http://localhost:8000/api/campaigns/1` (replace `1` with your campaign ID)
3. **Headers** tab:
   - Key: `Authorization`
   - Value: `Bearer YOUR_TOKEN_HERE`
4. Click **Send**

---

## ✏️ **Step 6: Update Campaign**

### **Request Details**
- **Method**: `PATCH`
- **URL**: `http://localhost:8000/api/campaigns/1`
- **Headers**: 
  ```
  Content-Type: application/json
  Authorization: Bearer YOUR_TOKEN_HERE
  ```
- **Body**: Select `raw` and `JSON`

### **Body (JSON)** - All fields optional!
```json
{
  "name": "Updated Campaign Name",
  "description": "Updated description",
  "message_template": "Updated message with {placeholders}"
}
```

**Note**: You can update only the fields you want to change!

---

## 👥 **Step 7: Add Recipients**

### **Option A: Add Single Recipient**

#### **Request Details**
- **Method**: `POST`
- **URL**: `http://localhost:8000/api/campaigns/1/recipients`
- **Headers**: 
  ```
  Content-Type: application/json
  Authorization: Bearer YOUR_TOKEN_HERE
  ```

#### **Body (JSON)**
```json
{
  "phone_number": "+1234567890",
  "name": "John Doe",
  "custom_data": {
    "discount": "20",
    "link": "https://example.com/john"
  }
}
```

### **Option B: Add Multiple Recipients (Bulk)**

#### **Request Details**
- **Method**: `POST`
- **URL**: `http://localhost:8000/api/campaigns/1/recipients/bulk`
- **Headers**: 
  ```
  Content-Type: application/json
  Authorization: Bearer YOUR_TOKEN_HERE
  ```

#### **Body (JSON)**
```json
{
  "recipients": [
    {
      "phone_number": "+1234567890",
      "name": "John Doe",
      "custom_data": {
        "discount": "20",
        "link": "https://example.com/john"
      }
    },
    {
      "phone_number": "+9876543210",
      "name": "Jane Smith",
      "custom_data": {
        "discount": "15",
        "link": "https://example.com/jane"
      }
    }
  ]
}
```

### **Option C: Upload CSV File**

#### **Request Details**
- **Method**: `POST`
- **URL**: `http://localhost:8000/api/campaigns/1/recipients/upload`
- **Headers**: 
  ```
  Authorization: Bearer YOUR_TOKEN_HERE
  ```
- **Body**: Select `form-data`

#### **Postman Steps**
1. Go to **Body** tab
2. Select `form-data`
3. Add a field:
   - Key: `file` (change type to `File` using dropdown)
   - Value: Click "Select Files" and choose your CSV file
4. Click **Send**

#### **CSV File Format**
```csv
phone_number,name,discount,link
+1234567890,John Doe,20,https://example.com/john
+9876543210,Jane Smith,15,https://example.com/jane
```

---

## 🚀 **Step 8: Send Campaign**

### **Request Details**
- **Method**: `POST`
- **URL**: `http://localhost:8000/api/campaigns/1/send`
- **Headers**: 
  ```
  Authorization: Bearer YOUR_TOKEN_HERE
  ```
- **Body**: None needed

### **Postman Steps**
1. Method: `POST`
2. URL: `http://localhost:8000/api/campaigns/1/send`
3. **Headers** tab:
   - Key: `Authorization`
   - Value: `Bearer YOUR_TOKEN_HERE`
4. **Body**: Select `none`
5. Click **Send**

### **Expected Response** (200 OK)
```json
{
  "campaign_id": 1,
  "status": "sending",
  "message": "Campaign queued for sending",
  "total_recipients": 100
}
```

---

## 🎯 **Quick Reference: All Endpoints**

| Action | Method | URL | Auth Required |
|--------|--------|-----|---------------|
| Register | POST | `/api/auth/register` | ❌ No |
| Login | POST | `/api/auth/login` | ❌ No |
| Create Campaign | POST | `/api/campaigns` | ✅ Yes |
| List Campaigns | GET | `/api/campaigns` | ✅ Yes |
| Get Campaign | GET | `/api/campaigns/{id}` | ✅ Yes |
| Update Campaign | PATCH | `/api/campaigns/{id}` | ✅ Yes |
| Delete Campaign | DELETE | `/api/campaigns/{id}` | ✅ Yes |
| Send Campaign | POST | `/api/campaigns/{id}/send` | ✅ Yes |
| Cancel Campaign | POST | `/api/campaigns/{id}/cancel` | ✅ Yes |

---

## 🔐 **Setting Up Authorization in Postman**

### **Method 1: Manual (Per Request)**
For each request, go to **Headers** tab and add:
```
Key: Authorization
Value: Bearer YOUR_TOKEN_HERE
```

### **Method 2: Collection-Level (Recommended)**
1. Click on your collection name (`PingLayer API`)
2. Go to **Authorization** tab
3. Type: Select `Bearer Token`
4. Token: Paste your token
5. Save

Now all requests in this collection will automatically use this token!

### **Method 3: Environment Variable (Best)**
1. Click the eye icon (top right) → "Add"
2. Create new environment: `PingLayer Local`
3. Add variable:
   - Variable: `auth_token`
   - Initial Value: (leave empty)
   - Current Value: `YOUR_TOKEN_HERE`
4. Save

In your requests, use:
```
Authorization: Bearer {{auth_token}}
```

---

## 💡 **Pro Tips**

### **1. Save Requests**
Save each request in your collection for reuse!

### **2. Use Tests to Auto-Save Token**
In the **Tests** tab of your login/register request, add:
```javascript
var jsonData = pm.response.json();
pm.environment.set("auth_token", jsonData.access_token);
```

Now the token is automatically saved after login!

### **3. Check Response Status**
- ✅ 200/201 = Success
- ❌ 400 = Bad Request (check your data)
- ❌ 401 = Unauthorized (check your token)
- ❌ 404 = Not Found
- ❌ 422 = Validation Error (check required fields)

### **4. Pretty Print JSON**
Click the "Pretty" button in the response to format JSON nicely.

---

## 🐛 **Common Errors & Solutions**

### **Error: 401 Unauthorized**
```json
{
  "detail": "Invalid or expired token"
}
```
**Solution**: Get a new token by logging in again.

### **Error: 422 Validation Error**
```json
{
  "detail": "Validation error",
  "errors": [
    {
      "field": "name",
      "message": "field required"
    }
  ]
}
```
**Solution**: Check that you're sending all required fields.

### **Error: 404 Not Found**
```json
{
  "detail": "Campaign not found"
}
```
**Solution**: Check the campaign ID exists and belongs to your company.

---

## 📦 **Postman Collection Export**

Want to import a ready-made collection? Create a file `PingLayer.postman_collection.json`:

```json
{
  "info": {
    "name": "PingLayer API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Auth",
      "item": [
        {
          "name": "Register",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"full_name\": \"John Doe\",\n  \"email\": \"john@example.com\",\n  \"password\": \"SecurePass123!\",\n  \"company_name\": \"Acme Corp\"\n}"
            },
            "url": {
              "raw": "http://localhost:8000/api/auth/register",
              "protocol": "http",
              "host": ["localhost"],
              "port": "8000",
              "path": ["api", "auth", "register"]
            }
          }
        },
        {
          "name": "Login",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"email\": \"john@example.com\",\n  \"password\": \"SecurePass123!\"\n}"
            },
            "url": {
              "raw": "http://localhost:8000/api/auth/login",
              "protocol": "http",
              "host": ["localhost"],
              "port": "8000",
              "path": ["api", "auth", "login"]
            }
          }
        }
      ]
    },
    {
      "name": "Campaigns",
      "item": [
        {
          "name": "Create Campaign",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              },
              {
                "key": "Authorization",
                "value": "Bearer {{auth_token}}"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"name\": \"Summer Sale 2024\",\n  \"message_template\": \"Hi {name}, check out our sale!\"\n}"
            },
            "url": {
              "raw": "http://localhost:8000/api/campaigns",
              "protocol": "http",
              "host": ["localhost"],
              "port": "8000",
              "path": ["api", "campaigns"]
            }
          }
        },
        {
          "name": "List Campaigns",
          "request": {
            "method": "GET",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{auth_token}}"
              }
            ],
            "url": {
              "raw": "http://localhost:8000/api/campaigns",
              "protocol": "http",
              "host": ["localhost"],
              "port": "8000",
              "path": ["api", "campaigns"]
            }
          }
        }
      ]
    }
  ]
}
```

Import this in Postman: File → Import → Choose file

---

**You're all set! Happy testing! 🚀**
