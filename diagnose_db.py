"""
Database Connection Diagnostic Script

This script helps identify why the database connection is failing.
"""

import sys
import os

print("=" * 70)
print("🔍 PingLayer Database Connection Diagnostic")
print("=" * 70)

# Test 1: Check if .env file exists
print("\n1️⃣ Checking .env file...")
if os.path.exists(".env"):
    print("   ✅ .env file found")
else:
    print("   ❌ .env file NOT found")
    print("   → Copy .env.example to .env")
    sys.exit(1)

# Test 2: Load configuration
print("\n2️⃣ Loading configuration...")
try:
    from app.config import settings
    print("   ✅ Configuration loaded")
    print(f"   - Database URL: {settings.database_url}")
except Exception as e:
    print(f"   ❌ Configuration failed: {e}")
    sys.exit(1)

# Test 3: Check PostgreSQL connection
print("\n3️⃣ Testing PostgreSQL connection...")
try:
    import psycopg2
    from urllib.parse import urlparse
    
    # Parse database URL
    result = urlparse(settings.database_url)
    username = result.username
    password = result.password
    database = result.path[1:]
    hostname = result.hostname
    port = result.port
    
    print(f"   - Host: {hostname}")
    print(f"   - Port: {port}")
    print(f"   - Database: {database}")
    print(f"   - Username: {username}")
    
    # Try to connect
    conn = psycopg2.connect(
        host=hostname,
        port=port,
        user=username,
        password=password,
        database=database
    )
    conn.close()
    print("   ✅ PostgreSQL connection successful!")
    
except ImportError:
    print("   ❌ psycopg2 not installed")
    print("   → Run: pip install psycopg2-binary")
    sys.exit(1)
    
except psycopg2.OperationalError as e:
    error_msg = str(e)
    print(f"   ❌ Connection failed: {error_msg}")
    
    if "could not connect to server" in error_msg:
        print("\n   💡 Possible causes:")
        print("      1. PostgreSQL service is not running")
        print("      2. Wrong host or port")
        print("\n   🔧 Solutions:")
        print("      - Start PostgreSQL service:")
        print("        • Windows: services.msc → postgresql-x64-XX → Start")
        print("        • Or run: Get-Service postgresql* | Start-Service")
        
    elif "password authentication failed" in error_msg:
        print("\n   💡 Possible cause:")
        print("      - Wrong password in .env file")
        print("\n   🔧 Solution:")
        print("      - Update DATABASE_URL in .env with correct password")
        
    elif "database" in error_msg and "does not exist" in error_msg:
        print("\n   💡 Possible cause:")
        print("      - Database 'pinglayer' doesn't exist")
        print("\n   🔧 Solution:")
        print("      - Create database:")
        print("        psql -U postgres")
        print("        CREATE DATABASE pinglayer;")
        print("        \\q")
    
    sys.exit(1)
    
except Exception as e:
    print(f"   ❌ Unexpected error: {e}")
    sys.exit(1)

# Test 4: Check SQLAlchemy connection
print("\n4️⃣ Testing SQLAlchemy connection...")
try:
    from app.database import check_db_connection
    if check_db_connection():
        print("   ✅ SQLAlchemy connection successful!")
    else:
        print("   ❌ SQLAlchemy connection failed")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ SQLAlchemy test failed: {e}")
    sys.exit(1)

# Test 5: Check if tables exist
print("\n5️⃣ Checking database tables...")
try:
    from app.database import engine
    from sqlalchemy import inspect
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if tables:
        print(f"   ✅ Found {len(tables)} tables:")
        for table in tables:
            print(f"      - {table}")
    else:
        print("   ⚠️  No tables found")
        print("\n   💡 You need to initialize the database:")
        print("      python -c \"from app.database import init_db; init_db()\"")
        
except Exception as e:
    print(f"   ❌ Table check failed: {e}")

# Success!
print("\n" + "=" * 70)
print("✅ All diagnostic tests passed!")
print("=" * 70)
print("\n📝 Next steps:")
print("   1. If tables are missing, run:")
print("      python -c \"from app.database import init_db; init_db()\"")
print("   2. Restart your server:")
print("      uvicorn app.main:app --reload")
print("\n")
