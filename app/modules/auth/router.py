from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.auth import service
from app.schemas.user import UserCreate, UserLogin
from app.core.security import create_access_token
from fastapi import Body
from app.core.logging import logger

router = APIRouter()

@router.post("/register")
def register_new_user(db: Session = Depends(get_db), user_data: UserCreate = Body(...)):
    logger.info("Registering new user: %s", user_data)
    user = service.register_new_user(db, user_data)
    access_token = create_access_token(data={
        "sub": str(user.id),
        "company_id": user.company_id,
        "is_admin": user.is_admin,
        })
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user.to_dict(),
        "company": user.company.to_dict()
    }

@router.post("/login")
def login_user(db: Session = Depends(get_db), user_data: UserLogin = Body(...)):
    user = service.login_user(db, user_data)
    access_token = create_access_token(data={
        "sub": str(user.id),
        "company_id": user.company_id,
        "is_admin": user.is_admin,
        })
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user.to_dict(),
        "company": user.company.to_dict()
    }
