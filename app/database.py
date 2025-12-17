"""
Database Module

This module handles SQLAlchemy database setup, session management, and base model.

Design Decisions:
- Using SQLAlchemy 2.0 async-compatible style (but sync for simplicity in Phase 1)
- Session-per-request pattern via dependency injection
- Declarative Base for all ORM models
- Connection pooling configured for production use
- Automatic session cleanup via context manager

Multi-tenant Consideration:
- All queries should filter by company_id (enforced in dependencies)
- No cross-company data leakage
"""

from typing import Generator
from sqlalchemy import create_engine, event, MetaData, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import QueuePool
from app.config import settings

# Naming convention for constraints (helps with Alembic migrations)
# This ensures consistent naming across different databases
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

# Declarative Base for all ORM models
Base = declarative_base(metadata=metadata)


# Database Engine Configuration
def create_db_engine():
    """
    Create and configure SQLAlchemy engine.
    
    Configuration:
    - QueuePool for connection pooling (production-ready)
    - pool_pre_ping ensures connections are alive before use
    - echo=True in development for SQL debugging
    """
    return create_engine(
        settings.database_url,
        echo=settings.db_echo,  # Log SQL queries in development
        poolclass=QueuePool,
        pool_size=5,  # Number of connections to maintain
        max_overflow=10,  # Max connections beyond pool_size
        pool_pre_ping=True,  # Verify connections before using
        pool_recycle=3600,  # Recycle connections after 1 hour
    )


# Create engine instance
engine = create_db_engine()


# Session Factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Prevent lazy-loading issues after commit
)


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI.
    
    Usage in routes:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    
    This ensures:
    - One session per request
    - Automatic session cleanup
    - Proper transaction handling
    - Exception safety (rollback on error)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database - create all tables.
    
    This function is idempotent - safe to run multiple times.
    It only creates tables that don't already exist.
    
    NOTE: In production, use Alembic migrations instead.
    This is useful for:
    - Local development setup
    - Testing
    - Quick prototyping
    
    Usage:
        from app.database import init_db
        init_db()
    """
    from sqlalchemy import inspect
    
    # Import all models here to ensure they're registered with Base
    from app.models import (
        user, company, campaign, recipient, 
        message_log, smart_link, click_event, integration
    )
    
    # Check which tables already exist
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    # Get tables that need to be created
    all_tables = Base.metadata.tables.keys()
    tables_to_create = [t for t in all_tables if t not in existing_tables]
    
    if tables_to_create:
        print(f"📋 Creating {len(tables_to_create)} table(s): {', '.join(tables_to_create)}")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
    else:
        print("✅ All database tables already exist")


def drop_db() -> None:
    """
    Drop all database tables.
    
    ⚠️ DANGER: This will delete all data!
    Only use in development/testing.
    """
    if settings.is_production:
        raise RuntimeError("Cannot drop database in production!")
    
    Base.metadata.drop_all(bind=engine)
    print("⚠️ All database tables dropped")


# Event Listeners for PostgreSQL optimizations
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """
    Set PostgreSQL-specific optimizations on connection.
    
    This can be used to set session-level parameters like:
    - statement_timeout
    - lock_timeout
    - etc.
    """
    # Example: Set statement timeout to 30 seconds
    # cursor = dbapi_conn.cursor()
    # cursor.execute("SET statement_timeout = 30000")
    # cursor.close()
    pass


class DatabaseSession:
    """
    Context manager for database sessions outside of FastAPI requests.
    
    Usage in background workers or scripts:
        with DatabaseSession() as db:
            user = db.query(User).first()
            print(user.email)
    """
    
    def __init__(self):
        self.db: Session = None
    
    def __enter__(self) -> Session:
        self.db = SessionLocal()
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Rollback on exception
            self.db.rollback()
        self.db.close()


# Health check function
def check_db_connection() -> bool:
    """
    Check if database connection is healthy.
    
    Returns:
        bool: True if connection is successful, False otherwise
    
    Usage in health endpoint:
        @app.get("/health")
        def health():
            return {"db": check_db_connection()}
    """
    try:
        with DatabaseSession() as db:
            db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


if __name__ == "__main__":
    # Test database connection
    print("Testing database connection...")
    if check_db_connection():
        print("✅ Database connection successful")
    else:
        print("❌ Database connection failed")
