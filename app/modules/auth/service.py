from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.models.user import User
from app.models.company import Company
from app.core.security import hash_password, verify_password, create_access_token, validate_password_strength
from app.schemas.user import UserCreate, UserLogin

def register_new_user(db: Session, user_data: UserCreate):

    pw_validation = validate_password_strength(user_data.password)
    if not pw_validation[0]:
        raise HTTPException(status_code=400, detail=pw_validation[1])
    
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    existing_company = db.query(Company).filter(Company.name == user_data.company_name).first()
    if existing_company:
        raise HTTPException(status_code=400, detail="Company name already taken")
    
    try:
        company = Company(
            name=user_data.company_name,
            slug=user_data.company_name.lower().replace(" ", "-").replace("_", "-")
        )
        db.add(company)
        db.flush()  # Get company.id without committing
        
        user = User(
            full_name=user_data.full_name,
            email=user_data.email,
            hashed_password=hash_password(user_data.password), 
            company_id=company.id
        )
        db.add(user)
        
        db.commit()
        
        db.refresh(user)
        db.refresh(company)
        
        return user
        
    except IntegrityError as e:
        db.rollback()
        # Handle unique constraint violations
        if "email" in str(e).lower():
            raise HTTPException(status_code=400, detail="Email already registered")
        elif "slug" in str(e).lower() or "name" in str(e).lower():
            raise HTTPException(status_code=400, detail="Company name already taken")
        else:
            raise HTTPException(status_code=400, detail="Registration failed due to data conflict")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


def login_user(db: Session, user_data: UserLogin):

    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive. Please contact support.")
    
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Load company relationship
    db.refresh(user)
    
    return user