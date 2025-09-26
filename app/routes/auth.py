from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.services.user_service import AuthService
from app.database import get_db

router = APIRouter()

class GoogleLoginRequest(BaseModel):
    email: str
    google_id: str
    full_name: str = None
    picture: str = None

class AppleLoginRequest(BaseModel):
    email: str
    apple_id: str
    full_name: str = None

class AuthResponse(BaseModel):
    user_id: int
    email: str
    full_name: str = None
    google_id: str = None
    apple_id: str = None
    target_band_score: str = None

@router.post("/google", response_model=AuthResponse)
async def login_with_google(request: GoogleLoginRequest, db: Session = Depends(get_db)):
    try:
        user = AuthService.login_with_google(
            db=db,
            email=request.email,
            google_id=request.google_id,
            full_name=request.full_name,
            picture=request.picture
        )
        return AuthResponse(
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            google_id=user.google_id,
            apple_id=user.apple_id,
            target_band_score=user.target_band_score
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/apple", response_model=AuthResponse)
async def login_with_apple(request: AppleLoginRequest, db: Session = Depends(get_db)):
    try:
        user = AuthService.login_with_apple(
            db=db,
            email=request.email,
            apple_id=request.apple_id,
            full_name=request.full_name
        )
        return AuthResponse(
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            google_id=user.google_id,
            apple_id=user.apple_id,
            target_band_score=user.target_band_score
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))