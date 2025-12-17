from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.models.user import User
from app.models.company import Company
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.user import UserCreate

def register_new_user(db: Session, user_data: UserCreate):
    try:
        user_email = db.query(User).filter(User.email == user_data.email).first()
        if user_email:
            raise HTTPException(status_code=400, detail="Email already exists")
    
        user = User(
            full_name=user_data.full_name,
            email=user_data.email,
            password=hash_password(user_data.password),
            company_name=user_data.company_name
        )

        company = Company(
            name=user_data.company_name,
            slug=user_data.company_name.lower().replace(" ", "-")
        )

        user.company = company
        company.users.append(user)
        db.add(company)
        db.add(user)

        try:
            db.commit()
            return user
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        db.refresh(user)
        db.refresh(company)


    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))