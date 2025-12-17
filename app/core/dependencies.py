"""
Dependencies Module

FastAPI dependencies for authentication and multi-tenant context.

Design Decisions:
- JWT-based authentication via Bearer token
- Every authenticated request extracts user_id and company_id
- Multi-tenant isolation enforced at dependency level
- Clear separation between optional and required auth

Multi-Tenant Security:
- All queries MUST filter by company_id
- No cross-company data access
- company_id extracted from JWT token (not request params)
"""

from typing import Optional, Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import extract_user_from_token

# HTTP Bearer token scheme
security = HTTPBearer()


class CurrentUser:
    """
    Current authenticated user context.
    
    This object is injected into route handlers via dependency injection.
    It contains all information about the authenticated user.
    
    Attributes:
        user_id: Database ID of the user
        company_id: Company ID (for multi-tenant isolation)
        email: User's email address
    """
    
    def __init__(self, user_id: int, company_id: int, email: str):
        self.user_id = user_id
        self.company_id = company_id
        self.email = email
    
    def __repr__(self):
        return f"<CurrentUser user_id={self.user_id} company_id={self.company_id} email={self.email}>"


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> CurrentUser:
    """
    Dependency to get current authenticated user from JWT token.
    
    This is the primary authentication dependency used in protected routes.
    
    Args:
        credentials: Bearer token from Authorization header
        db: Database session
    
    Returns:
        CurrentUser object with user_id, company_id, email
    
    Raises:
        HTTPException 401: If token is invalid or expired
        HTTPException 404: If user not found in database
    
    Usage:
        @router.get("/protected")
        def protected_route(current_user: CurrentUser = Depends(get_current_user)):
            return {"user_id": current_user.user_id}
    """
    # Extract token from Authorization header
    token = credentials.credentials
    
    # Decode and validate token
    user_info = extract_user_from_token(token)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify user exists in database
    from app.models.user import User
    user = db.query(User).filter(User.id == user_info["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Return current user context
    return CurrentUser(
        user_id=user_info["user_id"],
        company_id=user_info["company_id"],
        email=user_info["email"]
    )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[CurrentUser]:
    """
    Optional authentication dependency.
    
    Returns CurrentUser if token is provided and valid, None otherwise.
    Does not raise exception if token is missing.
    
    Usage:
        @router.get("/public-or-private")
        def route(current_user: Optional[CurrentUser] = Depends(get_current_user_optional)):
            if current_user:
                return {"message": f"Hello {current_user.email}"}
            return {"message": "Hello guest"}
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


def get_company_context(current_user: CurrentUser = Depends(get_current_user)) -> int:
    """
    Dependency to get company_id for multi-tenant queries.
    
    This is a convenience dependency that extracts just the company_id.
    Use this when you only need company_id, not full user context.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        company_id (int)
    
    Usage:
        @router.get("/campaigns")
        def get_campaigns(
            company_id: int = Depends(get_company_context),
            db: Session = Depends(get_db)
        ):
            return db.query(Campaign).filter(Campaign.company_id == company_id).all()
    """
    return current_user.company_id


def require_admin(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """
    Dependency to require admin role.
    
    Raises:
        HTTPException 403: If user is not an admin
    
    Usage:
        @router.delete("/users/{user_id}")
        def delete_user(
            user_id: int,
            current_user: CurrentUser = Depends(require_admin)
        ):
            # Only admins can reach here
            pass
    """
    from app.models.user import User
    from app.database import SessionLocal
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == current_user.user_id).first()
        if not user or not user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        return current_user
    finally:
        db.close()


# Type aliases for cleaner route signatures
CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]
OptionalUserDep = Annotated[Optional[CurrentUser], Depends(get_current_user_optional)]
CompanyContextDep = Annotated[int, Depends(get_company_context)]
AdminUserDep = Annotated[CurrentUser, Depends(require_admin)]


if __name__ == "__main__":
    print("Dependencies module loaded")
    print("Available dependencies:")
    print("- get_current_user: Required authentication")
    print("- get_current_user_optional: Optional authentication")
    print("- get_company_context: Extract company_id")
    print("- require_admin: Admin-only access")
