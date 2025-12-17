from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.auth import service
from app.schemas.auth import RegisterRequest
from app.core.security import create_access_token

router = APIRouter()

@router.post("/register", response_model=RegisterRequest)
def register_new_user(db: Session = Depends(get_db), user_data: RegisterRequest = Body(...)):
    user = service.register_new_user(db, user_data)
    access_token = create_access_token(data={
        "sub": str(user.id),
        "company_id": company.id,
        "is_admin": user.is_admin,
        })
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user.to_dict(),
        "company": company.to_dict()
    }
