# 📝 Campaign Creation - User Data Guide

## 🎯 **What Data to Pass When Creating a Campaign**

### **API Endpoint**
```
POST /api/campaigns
Authorization: Bearer <your_token>
Content-Type: application/json
```

---

## 📋 **Required Fields**

### **1. name** (string, required)
- **Description**: Campaign name
- **Min Length**: 1 character
- **Max Length**: 255 characters
- **Example**: `"Summer Sale 2024"`

### **2. message_template** (string, required)
- **Description**: Message template with placeholders
- **Min Length**: 10 characters
- **Max Length**: 5000 characters
- **Placeholders**: Use `{variable_name}` for dynamic content
- **Example**: `"Hi {name}, check out our {discount}% off sale! Visit {link}"`

---

## 📋 **Optional Fields**

### **3. description** (string, optional)
- **Description**: Campaign description for your reference
- **Max Length**: 1000 characters
- **Default**: `null`
- **Example**: `"Promotional campaign for summer sale targeting premium customers"`

### **4. template_variables** (array of strings, optional)
- **Description**: List of variable names used in the template
- **Purpose**: Helps validate recipient data later
- **Default**: `null`
- **Example**: `["name", "discount", "link"]`

### **5. scheduled_at** (datetime, optional)
- **Description**: When to send the campaign
- **Format**: ISO 8601 datetime
- **Validation**: Must be in the future
- **Default**: `null` (means send immediately when triggered)
- **Example**: `"2024-07-01T10:00:00"`

---

## 🔐 **Automatically Added (Don't Pass These)**

The following fields are **automatically set** by the backend:

- ✅ **company_id** - From your JWT token
- ✅ **created_by** - Your user ID from JWT token
- ✅ **status** - Auto-set based on `scheduled_at`:
  - `"draft"` if `scheduled_at` is `null`
  - `"scheduled"` if `scheduled_at` is provided
- ✅ **total_recipients** - Starts at 0, updated when you add recipients
- ✅ **sent_count** - Starts at 0
- ✅ **delivered_count** - Starts at 0
- ✅ **failed_count** - Starts at 0
- ✅ **created_at** - Current timestamp
- ✅ **updated_at** - Current timestamp

---

## 📝 **Complete Request Examples**

### **Example 1: Minimal Campaign (Draft)**
```json
{
  "name": "Summer Sale 2024",
  "message_template": "Hi {name}, check out our summer sale! Visit {link}"
}
```

**Result**:
- Status: `draft`
- Can add recipients later
- Can send immediately or schedule later

---

### **Example 2: Campaign with Description**
```json
{
  "name": "Premium Customer Discount",
  "description": "Exclusive 20% discount for premium customers",
  "message_template": "Hi {name}, as a premium customer, enjoy {discount}% off! Use code: {code}"
}
```

---

### **Example 3: Campaign with Template Variables**
```json
{
  "name": "Product Launch",
  "description": "New product launch announcement",
  "message_template": "Hi {name}, {company} is launching {product}! Get {discount}% off. Visit: {link}",
  "template_variables": ["name", "company", "product", "discount", "link"]
}
```

**Benefits of specifying template_variables**:
- ✅ Documents what data recipients need
- ✅ Can validate recipient data against this list
- ✅ Helps when uploading CSV files

---

### **Example 4: Scheduled Campaign**
```json
{
  "name": "Weekend Flash Sale",
  "description": "Flash sale scheduled for Saturday morning",
  "message_template": "Hi {name}, flash sale starts now! {discount}% off everything. Shop: {link}",
  "template_variables": ["name", "discount", "link"],
  "scheduled_at": "2024-07-06T09:00:00"
}
```

**Result**:
- Status: `scheduled`
- Will automatically send at the specified time
- Can still add recipients before scheduled time

---

### **Example 5: Complex Campaign**
```json
{
  "name": "Personalized Product Recommendations",
  "description": "AI-generated personalized product recommendations based on purchase history",
  "message_template": "Hi {title} {name}, based on your interest in {category}, we recommend {product}. Special price: {price}. Order now: {link}. Questions? Reply or call {phone}.",
  "template_variables": [
    "title",
    "name", 
    "category",
    "product",
    "price",
    "link",
    "phone"
  ],
  "scheduled_at": "2024-07-10T14:30:00"
}
```

---

## 🎨 **Message Template Best Practices**

### **Good Templates** ✅

```json
{
  "message_template": "Hi {name}, {company} has a special offer for you! Get {discount}% off. Visit: {link}"
}
```
- Clear placeholders
- Professional tone
- Call to action
- Link included

### **Bad Templates** ❌

```json
{
  "message_template": "Sale!"
}
```
- Too short (min 10 chars)
- No personalization
- No value proposition

---

## 🔍 **Validation Rules**

### **Campaign Name**
```python
✅ "Summer Sale 2024"           # Valid
✅ "Q4 Promotion"                # Valid
❌ ""                            # Too short
❌ "   "                         # Only whitespace
❌ "A" * 300                     # Too long (max 255)
```

### **Message Template**
```python
✅ "Hi {name}, check this out!"  # Valid (>10 chars)
❌ "Hi there"                    # Too short (<10 chars)
❌ ""                            # Empty
❌ "A" * 6000                    # Too long (max 5000)
```

### **Scheduled Time**
```python
✅ "2024-12-25T10:00:00"         # Future date
❌ "2023-01-01T10:00:00"         # Past date
❌ "invalid-date"                # Invalid format
```

---

## 📊 **Complete Flow Example**

### **Step 1: Create Campaign**
```bash
curl -X POST http://localhost:8000/api/campaigns \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Summer Sale 2024",
    "description": "Promotional campaign",
    "message_template": "Hi {name}, get {discount}% off! Visit {link}",
    "template_variables": ["name", "discount", "link"]
  }'
```

**Response**:
```json
{
  "id": 1,
  "name": "Summer Sale 2024",
  "description": "Promotional campaign",
  "company_id": 1,
  "created_by": 1,
  "status": "draft",
  "message_template": "Hi {name}, get {discount}% off! Visit {link}",
  "template_variables": ["name", "discount", "link"],
  "scheduled_at": null,
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

### **Step 2: Add Recipients**
```bash
# Upload CSV with columns: phone_number, name, discount, link
curl -X POST http://localhost:8000/api/campaigns/1/recipients/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@recipients.csv"
```

### **Step 3: Send Campaign**
```bash
curl -X POST http://localhost:8000/api/campaigns/1/send \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🎯 **Quick Reference Table**

| Field | Required | Type | Example | Notes |
|-------|----------|------|---------|-------|
| `name` | ✅ Yes | string | "Summer Sale" | 1-255 chars |
| `message_template` | ✅ Yes | string | "Hi {name}..." | 10-5000 chars |
| `description` | ❌ No | string | "Promo campaign" | Max 1000 chars |
| `template_variables` | ❌ No | array | ["name", "link"] | List of variables |
| `scheduled_at` | ❌ No | datetime | "2024-07-01T10:00:00" | Must be future |

---

## 🧪 **Testing with Swagger UI**

1. Go to http://localhost:8000/docs
2. Click on **POST /api/campaigns**
3. Click **"Try it out"**
4. Paste this example:

```json
{
  "name": "Test Campaign",
  "message_template": "Hi {name}, this is a test message!"
}
```

5. Click **Execute**
6. Check the response!

---

## 💡 **Pro Tips**

### **1. Start Simple**
```json
{
  "name": "My First Campaign",
  "message_template": "Hi {name}, welcome to our service!"
}
```

### **2. Add Complexity Gradually**
```json
{
  "name": "My Second Campaign",
  "description": "With more details",
  "message_template": "Hi {name}, check out {product} at {link}",
  "template_variables": ["name", "product", "link"]
}
```

### **3. Schedule for Later**
```json
{
  "name": "Scheduled Campaign",
  "message_template": "Hi {name}, sale starts now!",
  "scheduled_at": "2024-07-15T09:00:00"
}
```

---

## ❓ **Common Questions**

### **Q: Do I need to add recipients when creating the campaign?**
**A:** No! Create the campaign first, then add recipients later.

### **Q: Can I edit the campaign after creation?**
**A:** Yes, but only if status is `draft` or `scheduled`.

### **Q: What if I don't specify template_variables?**
**A:** It's optional. The system will still work, but it's good practice to specify them.

### **Q: Can I create a campaign without scheduling it?**
**A:** Yes! Leave `scheduled_at` as `null` and it will be a draft. Send it manually later.

### **Q: What happens if scheduled_at is in the past?**
**A:** Validation error! It must be in the future.

---

## 📚 **Summary**

**Minimum Required Data**:
```json
{
  "name": "Campaign Name",
  "message_template": "Your message with {placeholders}"
}
```

**Recommended Data**:
```json
{
  "name": "Campaign Name",
  "description": "What this campaign is about",
  "message_template": "Hi {name}, your personalized message here!",
  "template_variables": ["name", "other", "variables"]
}
```

**Full Data (Scheduled)**:
```json
{
  "name": "Campaign Name",
  "description": "Campaign description",
  "message_template": "Message with {placeholders}",
  "template_variables": ["list", "of", "variables"],
  "scheduled_at": "2024-12-25T10:00:00"
}
```

---

**That's all you need to create a campaign! 🚀**
