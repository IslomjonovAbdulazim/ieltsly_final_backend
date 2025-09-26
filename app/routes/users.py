from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.services.user_service import UserService
from app.models.user import User
from app.auth import get_current_user
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

class TestHistoryResponse(BaseModel):
    test_id: int
    test_type: str  # "speaking", "reading", "writing", "listening"
    test_title: str
    submission_id: int
    submitted_at: str
    is_completed: bool
    band_score: float = None

@router.get("/profile", response_model=UserResponse)
async def get_my_profile(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin cannot access user profile")
    
    return UserResponse(
        user_id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        target_band_score=current_user.target_band_score,
        display_name=current_user.display_name
    )

@router.put("/profile", response_model=UserResponse)
async def update_my_profile(
    request: UpdateProfileRequest, 
    current_user = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    if current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin cannot update user profile")
    
    user = UserService.update_profile(
        db=db,
        user_id=current_user.id,
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

@router.get("/history", response_model=List[TestHistoryResponse])
async def get_test_history(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin cannot access user history")
    
    # Get test history from all skills
    from app.models.speaking import SpeakingSubmission, SpeakingTest, SpeakingScore
    from app.models.reading import ReadingSubmission, ReadingTest, ReadingScore
    from app.models.writing import WritingSubmission, WritingTest, WritingScore
    from app.models.listening import ListeningSubmission, ListeningTest, ListeningScore
    
    history = []
    
    # Speaking submissions
    speaking_submissions = db.query(SpeakingSubmission).filter(
        SpeakingSubmission.user_id == current_user.id
    ).all()
    
    for sub in speaking_submissions:
        test = db.query(SpeakingTest).filter(SpeakingTest.id == sub.test_id).first()
        score = db.query(SpeakingScore).filter(SpeakingScore.submission_id == sub.id).first()
        
        history.append(TestHistoryResponse(
            test_id=test.id if test else 0,
            test_type="speaking",
            test_title=test.title if test else "Unknown Test",
            submission_id=sub.id,
            submitted_at=sub.submitted_at.isoformat() if sub.submitted_at else sub.created_at.isoformat(),
            is_completed=sub.is_completed,
            band_score=score.overall_band if score else None
        ))
    
    # Reading submissions
    reading_submissions = db.query(ReadingSubmission).filter(
        ReadingSubmission.user_id == current_user.id
    ).all()
    
    for sub in reading_submissions:
        test = db.query(ReadingTest).filter(ReadingTest.id == sub.test_id).first()
        score = db.query(ReadingScore).filter(ReadingScore.submission_id == sub.id).first()
        
        history.append(TestHistoryResponse(
            test_id=test.id if test else 0,
            test_type="reading",
            test_title=test.title if test else "Unknown Test",
            submission_id=sub.id,
            submitted_at=sub.submitted_at.isoformat() if sub.submitted_at else sub.created_at.isoformat(),
            is_completed=sub.is_completed,
            band_score=score.band_score if score else None
        ))
    
    # Writing submissions
    writing_submissions = db.query(WritingSubmission).filter(
        WritingSubmission.user_id == current_user.id
    ).all()
    
    for sub in writing_submissions:
        test = db.query(WritingTest).filter(WritingTest.id == sub.test_id).first()
        score = db.query(WritingScore).filter(WritingScore.submission_id == sub.id).first()
        
        history.append(TestHistoryResponse(
            test_id=test.id if test else 0,
            test_type="writing",
            test_title=test.title if test else "Unknown Test",
            submission_id=sub.id,
            submitted_at=sub.submitted_at.isoformat() if sub.submitted_at else sub.created_at.isoformat(),
            is_completed=sub.is_completed,
            band_score=score.overall_band if score else None
        ))
    
    # Listening submissions
    listening_submissions = db.query(ListeningSubmission).filter(
        ListeningSubmission.user_id == current_user.id
    ).all()
    
    for sub in listening_submissions:
        test = db.query(ListeningTest).filter(ListeningTest.id == sub.test_id).first()
        score = db.query(ListeningScore).filter(ListeningScore.submission_id == sub.id).first()
        
        history.append(TestHistoryResponse(
            test_id=test.id if test else 0,
            test_type="listening",
            test_title=test.title if test else "Unknown Test",
            submission_id=sub.id,
            submitted_at=sub.submitted_at.isoformat() if sub.submitted_at else sub.created_at.isoformat(),
            is_completed=sub.is_completed,
            band_score=score.band_score if score else None
        ))
    
    # Sort by submission date (newest first)
    history.sort(key=lambda x: x.submitted_at, reverse=True)
    
    return history