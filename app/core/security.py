"""
Security Module

Handles authentication, password hashing, and JWT token management.

Design Decisions:
- bcrypt for password hashing (industry standard, slow by design)
- JWT tokens for stateless authentication
- Token payload includes user_id and company_id for multi-tenancy
- No token refresh mechanism in Phase 1 (can add later)

Security Best Practices:
- Passwords are never stored in plain text
- JWT secret must be strong (32+ chars)
- Token expiry enforced
- Constant-time password verification (bcrypt handles this)
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

# Password hashing context
# bcrypt is intentionally slow to prevent brute-force attacks
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.
    
    Args:
        password: Plain-text password
    
    Returns:
        Hashed password string
    
    Example:
        hashed = hash_password("mypassword123")
        # Returns: $2b$12$...
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a hashed password.
    
    Args:
        plain_password: Plain-text password from user input
        hashed_password: Hashed password from database
    
    Returns:
        True if password matches, False otherwise
    
    Security:
        Uses constant-time comparison to prevent timing attacks
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Payload to encode in token (typically user_id, company_id, email)
        expires_delta: Optional custom expiration time
    
    Returns:
        Encoded JWT token string
    
    Token Payload Structure:
        {
            "sub": user_id (subject),
            "company_id": company_id,
            "email": user_email,
            "exp": expiration_timestamp,
            "iat": issued_at_timestamp
        }
    
    Example:
        token = create_access_token(
            data={"sub": "123", "company_id": "456", "email": "user@example.com"}
        )
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    # Add standard JWT claims
    to_encode.update({
        "exp": expire,  # Expiration time
        "iat": datetime.utcnow()  # Issued at time
    })
    
    # Encode token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and verify a JWT access token.
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded payload dict if valid, None if invalid/expired
    
    Validation:
        - Signature verification
        - Expiration check
        - Algorithm check
    
    Example:
        payload = decode_access_token(token)
        if payload:
            user_id = payload.get("sub")
            company_id = payload.get("company_id")
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        # Invalid token, expired, or signature mismatch
        return None


def create_user_token(user_id: int, company_id: int, email: str) -> str:
    """
    Convenience function to create a token for a user.
    
    Args:
        user_id: User's database ID
        company_id: User's company ID (for multi-tenancy)
        email: User's email
    
    Returns:
        JWT token string
    
    This is the primary function used after login/registration.
    """
    token_data = {
        "sub": str(user_id),  # Subject (user ID)
        "company_id": str(company_id),
        "email": email
    }
    return create_access_token(data=token_data)


def extract_user_from_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Extract user information from a token.
    
    Args:
        token: JWT token string
    
    Returns:
        Dict with user_id, company_id, email if valid, None otherwise
    
    Example:
        user_info = extract_user_from_token(token)
        if user_info:
            print(f"User ID: {user_info['user_id']}")
            print(f"Company ID: {user_info['company_id']}")
    """
    payload = decode_access_token(token)
    if not payload:
        return None
    
    return {
        "user_id": int(payload.get("sub")),
        "company_id": int(payload.get("company_id")),
        "email": payload.get("email")
    }


# Password validation
def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength.
    
    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    
    Args:
        password: Plain-text password to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    
    Example:
        valid, msg = validate_password_strength("weak")
        if not valid:
            raise ValueError(msg)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    
    return True, ""


if __name__ == "__main__":
    # Test password hashing
    print("=== Testing Security Module ===")
    
    password = "TestPassword123"
    hashed = hash_password(password)
    print(f"Original: {password}")
    print(f"Hashed: {hashed}")
    print(f"Verification: {verify_password(password, hashed)}")
    
    # Test JWT token
    token = create_user_token(user_id=1, company_id=1, email="test@example.com")
    print(f"\nJWT Token: {token[:50]}...")
    
    user_info = extract_user_from_token(token)
    print(f"Decoded: {user_info}")
    
    # Test password validation
    valid, msg = validate_password_strength("weak")
    print(f"\nPassword 'weak' valid: {valid}, message: {msg}")
    
    valid, msg = validate_password_strength("StrongPass123")
    print(f"Password 'StrongPass123' valid: {valid}")
