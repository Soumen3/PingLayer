# ✅ Alembic Setup Complete!

## 🎯 **What Was Done**

1. ✅ **Configured `alembic/env.py`**
   - Imports all your models
   - Uses DATABASE_URL from `.env`
   - Detects schema changes automatically

2. ✅ **Updated `alembic.ini`**
   - Configured for PostgreSQL
   - Uses settings from environment

3. ✅ **Created `ALEMBIC_GUIDE.md`**
   - Complete usage guide
   - Examples and best practices

---

## 🚀 **Next Steps - Run These Commands**

### **1. Activate Virtual Environment**

```powershell
# If not already activated
& c:/Users/user/Desktop/PingLayer/backend/.venv/Scripts/Activate.ps1
```

### **2. Install Alembic (if not installed)**

```powershell
pip install alembic
```

### **3. Create Initial Migration**

```powershell
cd backend
alembic revision --autogenerate -m "Initial migration - create all tables"
```

**This will**:
- Scan all your models (User, Company, Campaign, etc.)
- Generate a migration file
- Save it in `alembic/versions/`

### **4. Review the Migration**

Check the generated file in `alembic/versions/` to ensure it looks correct.

### **5. Apply the Migration**

```powershell
alembic upgrade head
```

**This will**:
- Create all tables in your database
- Set up the alembic_version table

### **6. Verify**

```powershell
alembic current
```

Should show the current migration version.

---

## 📋 **Quick Command Reference**

```powershell
# Create migration after model changes
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history
```

---

## 🎓 **How It Works**

### **Before (Manual Table Creation)**
```python
# You had to run this manually
from app.database import init_db
init_db()
```

### **After (With Alembic)**
```powershell
# Alembic manages everything
alembic upgrade head
```

**Benefits**:
- ✅ Version control for database schema
- ✅ Easy rollbacks
- ✅ Team collaboration
- ✅ Production-safe migrations
- ✅ Automatic change detection

---

## 📊 **What Alembic Will Manage**

All your tables:
- ✅ companies
- ✅ users
- ✅ campaigns
- ✅ recipients
- ✅ message_logs
- ✅ smart_links
- ✅ click_events
- ✅ integrations

Plus:
- ✅ Indexes
- ✅ Foreign keys
- ✅ Constraints
- ✅ Column types
- ✅ Default values

---

## 🔄 **Typical Workflow**

### **1. Modify Model**
```python
# app/models/user.py
class User(Base):
    # Add new field
    phone_number = Column(String(20), nullable=True)
```

### **2. Generate Migration**
```powershell
alembic revision --autogenerate -m "Add phone_number to users"
```

### **3. Review**
Check `alembic/versions/abc123_add_phone_number_to_users.py`

### **4. Apply**
```powershell
alembic upgrade head
```

### **5. Done!**
Database is updated ✅

---

## ⚠️ **Important Notes**

### **Database Must Exist**
Alembic manages tables, not the database itself. Ensure `pinglayer` database exists:

```sql
-- If needed, create database first
CREATE DATABASE pinglayer;
```

### **Environment Variables**
Alembic uses your `.env` file:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/pinglayer
```

### **First Time Setup**
If you already have tables (created with `init_db()`), you have two options:

**Option A: Start Fresh**
```powershell
# Drop all tables
# Then run
alembic upgrade head
```

**Option B: Stamp Current State**
```powershell
# Mark database as already migrated
alembic stamp head
```

---

## 🎯 **Summary**

**Alembic is configured and ready!**

To start using it:

```powershell
# 1. Activate venv (if needed)
& .venv/Scripts/Activate.ps1

# 2. Create initial migration
alembic revision --autogenerate -m "Initial migration"

# 3. Apply it
alembic upgrade head

# 4. Verify
alembic current
```

**Check `ALEMBIC_GUIDE.md` for complete documentation!** 📚

---

**Your database migrations are now professional-grade! 🚀**
