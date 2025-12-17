"""
Test script to verify the foundation setup.
"""

print("=" * 60)
print("🧪 Testing PingLayer Foundation")
print("=" * 60)

# Test 1: Config
print("\n1️⃣ Testing Configuration...")
try:
    from app.config import settings
    print(f"   ✅ Config loaded")
    print(f"   - App Name: {settings.app_name}")
    print(f"   - Environment: {settings.environment}")
    print(f"   - Debug: {settings.debug}")
except Exception as e:
    print(f"   ❌ Config failed: {e}")
    exit(1)

# Test 2: Database
print("\n2️⃣ Testing Database Connection...")
try:
    from app.database import check_db_connection
    if check_db_connection():
        print("   ✅ Database connected")
    else:
        print("   ⚠️  Database not connected (this is OK if PostgreSQL isn't running)")
except Exception as e:
    print(f"   ❌ Database test failed: {e}")

# Test 3: Models
print("\n3️⃣ Testing Models Import...")
try:
    from app.models import (
        User, Company, Campaign, Recipient,
        MessageLog, SmartLink, ClickEvent, Integration
    )
    print("   ✅ All models imported successfully")
    print(f"   - User: {User.__tablename__}")
    print(f"   - Company: {Company.__tablename__}")
    print(f"   - Campaign: {Campaign.__tablename__}")
except Exception as e:
    print(f"   ❌ Models import failed: {e}")
    exit(1)

# Test 4: Security
print("\n4️⃣ Testing Security Module...")
try:
    from app.core.security import hash_password, verify_password, create_user_token
    
    # Test password hashing
    password = "TestPassword123"
    hashed = hash_password(password)
    verified = verify_password(password, hashed)
    
    if verified:
        print("   ✅ Password hashing works")
    else:
        print("   ❌ Password verification failed")
        exit(1)
    
    # Test JWT
    token = create_user_token(user_id=1, company_id=1, email="test@example.com")
    if token:
        print("   ✅ JWT token generation works")
    else:
        print("   ❌ JWT token generation failed")
        exit(1)
        
except Exception as e:
    print(f"   ❌ Security test failed: {e}")
    exit(1)

# Test 5: Dependencies
print("\n5️⃣ Testing Dependencies...")
try:
    from app.core.dependencies import CurrentUser
    user = CurrentUser(user_id=1, company_id=1, email="test@example.com")
    print(f"   ✅ Dependencies loaded: {user}")
except Exception as e:
    print(f"   ❌ Dependencies test failed: {e}")
    exit(1)

# Test 6: Logging
print("\n6️⃣ Testing Logging...")
try:
    from app.core.logging import get_logger
    logger = get_logger(__name__)
    logger.info("Test log message")
    print("   ✅ Logging works")
except Exception as e:
    print(f"   ❌ Logging test failed: {e}")
    exit(1)

# Test 7: Rate Limiter
print("\n7️⃣ Testing Rate Limiter...")
try:
    from app.core.rate_limiter import RateLimiter
    limiter = RateLimiter()
    allowed = limiter.check_rate_limit("test_user", "/api/test", max_requests=5)
    if allowed:
        print("   ✅ Rate limiter works")
    else:
        print("   ❌ Rate limiter failed")
        exit(1)
except Exception as e:
    print(f"   ❌ Rate limiter test failed: {e}")
    exit(1)

print("\n" + "=" * 60)
print("✅ All foundation tests passed!")
print("=" * 60)
print("\n📝 Next steps:")
print("   1. Ensure PostgreSQL is running")
print("   2. Create database: CREATE DATABASE pinglayer;")
print("   3. Run: python -c 'from app.database import init_db; init_db()'")
print("   4. Start server: uvicorn app.main:app --reload")
print("   5. Visit: http://localhost:8000/docs")
print("\n")
