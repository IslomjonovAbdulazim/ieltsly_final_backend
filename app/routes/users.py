from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.services.user_service import UserService
from app.database import get_db

router = APIRouter()

class UpdateProfileRequest(BaseModel):
    full_name: str = None
    target_band_score: str = None

class UserResponse(BaseModel):
    user_id: int
    email: str
    full_name: str = None
    target_band_score: str = None
    display_name: str

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        target_band_score=user.target_band_score,
        display_name=user.display_name
    )

@router.put("/{user_id}", response_model=UserResponse)
async def update_user_profile(user_id: int, request: UpdateProfileRequest, db: Session = Depends(get_db)):
    user = UserService.update_profile(
        db=db,
        user_id=user_id,
        full_name=request.full_name,
        target_score=request.target_band_score
    )
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        target_band_score=user.target_band_score,
        display_name=user.display_name
    )