from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.services.user_service import AuthService
from app.auth import create_access_token, verify_admin_credentials
from app.database import get_db
from datetime import timedelta

router = APIRouter()

class GoogleLoginRequest(BaseModel):
    email: str
    google_id: str
    full_name: str = None
    picture: str = None

class AdminLoginRequest(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    email: str
    full_name: str = None
    google_id: str = None
    target_band_score: str = None
    is_admin: bool = False

@router.post("/admin/login", response_model=AuthResponse)
async def admin_login(request: AdminLoginRequest):
    if not verify_admin_credentials(request.email, request.password):
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    
    access_token_expires = timedelta(minutes=60)  # Admin tokens last longer
    access_token = create_access_token(
        data={"sub": 0, "type": "admin", "email": request.email},
        expires_delta=access_token_expires
    )
    
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=0,
        email=request.email,
        full_name="Admin",
        is_admin=True
    )

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
        
        # Create JWT token for user
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user.id, "type": "user"},
            expires_delta=access_token_expires
        )
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            google_id=user.google_id,
            target_band_score=user.target_band_score,
            is_admin=False
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))