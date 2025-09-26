from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.auth import get_admin_user
from app.database import get_db

router = APIRouter()

# USER MANAGEMENT
@router.get("/users")
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    from app.models.user import User
    users = db.query(User).offset(skip).limit(limit).all()
    
    return [
        {
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "google_id": u.google_id,
            "target_band_score": u.target_band_score,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat(),
            "last_login": u.last_login.isoformat() if u.last_login else None
        } for u in users
    ]

@router.get("/users/{user_id}")
async def get_user_details(
    user_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    from app.models.user import User
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's test submissions count
    from app.models.speaking import SpeakingSubmission
    from app.models.reading import ReadingSubmission
    from app.models.writing import WritingSubmission
    from app.models.listening import ListeningSubmission
    
    speaking_count = db.query(SpeakingSubmission).filter(SpeakingSubmission.user_id == user_id).count()
    reading_count = db.query(ReadingSubmission).filter(ReadingSubmission.user_id == user_id).count()
    writing_count = db.query(WritingSubmission).filter(WritingSubmission.user_id == user_id).count()
    listening_count = db.query(ListeningSubmission).filter(ListeningSubmission.user_id == user_id).count()
    
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "google_id": user.google_id,
        "target_band_score": user.target_band_score,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat(),
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "test_submissions": {
            "speaking": speaking_count,
            "reading": reading_count,
            "writing": writing_count,
            "listening": listening_count,
            "total": speaking_count + reading_count + writing_count + listening_count
        }
    }

@router.put("/users/{user_id}/activate")
async def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    from app.models.user import User
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = True
    db.commit()
    return {"message": "User activated successfully"}

@router.put("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    from app.models.user import User
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = False
    db.commit()
    return {"message": "User deactivated successfully"}

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    from app.models.user import User
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Delete user and all related data will cascade
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

# STATISTICS & DASHBOARD
@router.get("/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    from app.models.user import User
    from app.models.speaking import SpeakingTest, SpeakingSubmission
    from app.models.reading import ReadingTest, ReadingSubmission
    from app.models.writing import WritingTest, WritingSubmission
    from app.models.listening import ListeningTest, ListeningSubmission
    
    # Count totals
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    
    total_speaking_tests = db.query(SpeakingTest).count()
    total_reading_tests = db.query(ReadingTest).count()
    total_writing_tests = db.query(WritingTest).count()
    total_listening_tests = db.query(ListeningTest).count()
    
    total_speaking_submissions = db.query(SpeakingSubmission).count()
    total_reading_submissions = db.query(ReadingSubmission).count()
    total_writing_submissions = db.query(WritingSubmission).count()
    total_listening_submissions = db.query(ListeningSubmission).count()
    
    completed_speaking = db.query(SpeakingSubmission).filter(SpeakingSubmission.is_completed == True).count()
    completed_reading = db.query(ReadingSubmission).filter(ReadingSubmission.is_completed == True).count()
    completed_writing = db.query(WritingSubmission).filter(WritingSubmission.is_completed == True).count()
    completed_listening = db.query(ListeningSubmission).filter(ListeningSubmission.is_completed == True).count()
    
    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "inactive": total_users - active_users
        },
        "tests": {
            "speaking": total_speaking_tests,
            "reading": total_reading_tests,
            "writing": total_writing_tests,
            "listening": total_listening_tests,
            "total": total_speaking_tests + total_reading_tests + total_writing_tests + total_listening_tests
        },
        "submissions": {
            "speaking": {
                "total": total_speaking_submissions,
                "completed": completed_speaking,
                "in_progress": total_speaking_submissions - completed_speaking
            },
            "reading": {
                "total": total_reading_submissions,
                "completed": completed_reading,
                "in_progress": total_reading_submissions - completed_reading
            },
            "writing": {
                "total": total_writing_submissions,
                "completed": completed_writing,
                "in_progress": total_writing_submissions - completed_writing
            },
            "listening": {
                "total": total_listening_submissions,
                "completed": completed_listening,
                "in_progress": total_listening_submissions - completed_listening
            },
            "totals": {
                "all_submissions": total_speaking_submissions + total_reading_submissions + total_writing_submissions + total_listening_submissions,
                "all_completed": completed_speaking + completed_reading + completed_writing + completed_listening
            }
        }
    }

@router.get("/submissions/recent")
async def get_recent_submissions(
    limit: int = 20,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    from app.models.user import User
    from app.models.speaking import SpeakingSubmission, SpeakingTest
    from app.models.reading import ReadingSubmission, ReadingTest
    from app.models.writing import WritingSubmission, WritingTest
    from app.models.listening import ListeningSubmission, ListeningTest
    
    recent_submissions = []
    
    # Get recent speaking submissions
    speaking_subs = db.query(SpeakingSubmission).order_by(SpeakingSubmission.created_at.desc()).limit(limit//4).all()
    for sub in speaking_subs:
        user = db.query(User).filter(User.id == sub.user_id).first()
        test = db.query(SpeakingTest).filter(SpeakingTest.id == sub.test_id).first()
        recent_submissions.append({
            "id": sub.id,
            "type": "speaking",
            "user_email": user.email if user else "Unknown",
            "test_title": test.title if test else "Unknown Test",
            "is_completed": sub.is_completed,
            "created_at": sub.created_at.isoformat(),
            "submitted_at": sub.submitted_at.isoformat() if sub.submitted_at else None
        })
    
    # Get recent reading submissions
    reading_subs = db.query(ReadingSubmission).order_by(ReadingSubmission.created_at.desc()).limit(limit//4).all()
    for sub in reading_subs:
        user = db.query(User).filter(User.id == sub.user_id).first()
        test = db.query(ReadingTest).filter(ReadingTest.id == sub.test_id).first()
        recent_submissions.append({
            "id": sub.id,
            "type": "reading",
            "user_email": user.email if user else "Unknown",
            "test_title": test.title if test else "Unknown Test",
            "is_completed": sub.is_completed,
            "created_at": sub.created_at.isoformat(),
            "submitted_at": sub.submitted_at.isoformat() if sub.submitted_at else None
        })
    
    # Get recent writing submissions
    writing_subs = db.query(WritingSubmission).order_by(WritingSubmission.created_at.desc()).limit(limit//4).all()
    for sub in writing_subs:
        user = db.query(User).filter(User.id == sub.user_id).first()
        test = db.query(WritingTest).filter(WritingTest.id == sub.test_id).first()
        recent_submissions.append({
            "id": sub.id,
            "type": "writing",
            "user_email": user.email if user else "Unknown",
            "test_title": test.title if test else "Unknown Test",
            "is_completed": sub.is_completed,
            "created_at": sub.created_at.isoformat(),
            "submitted_at": sub.submitted_at.isoformat() if sub.submitted_at else None
        })
    
    # Get recent listening submissions
    listening_subs = db.query(ListeningSubmission).order_by(ListeningSubmission.created_at.desc()).limit(limit//4).all()
    for sub in listening_subs:
        user = db.query(User).filter(User.id == sub.user_id).first()
        test = db.query(ListeningTest).filter(ListeningTest.id == sub.test_id).first()
        recent_submissions.append({
            "id": sub.id,
            "type": "listening",
            "user_email": user.email if user else "Unknown",
            "test_title": test.title if test else "Unknown Test",
            "is_completed": sub.is_completed,
            "created_at": sub.created_at.isoformat(),
            "submitted_at": sub.submitted_at.isoformat() if sub.submitted_at else None
        })
    
    # Sort by creation date (newest first)
    recent_submissions.sort(key=lambda x: x["created_at"], reverse=True)
    
    return recent_submissions[:limit]

# OVERVIEW - ALL TESTS
@router.get("/tests/overview")
async def get_all_tests_overview(
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    from app.models.speaking import SpeakingTest
    from app.models.reading import ReadingTest
    from app.models.writing import WritingTest
    from app.models.listening import ListeningTest
    
    speaking_tests = db.query(SpeakingTest).all()
    reading_tests = db.query(ReadingTest).all()
    writing_tests = db.query(WritingTest).all()
    listening_tests = db.query(ListeningTest).all()
    
    return {
        "speaking": [{"id": t.id, "title": t.title, "difficulty": t.difficulty, "created_at": t.created_at.isoformat()} for t in speaking_tests],
        "reading": [{"id": t.id, "title": t.title, "difficulty": t.difficulty, "created_at": t.created_at.isoformat()} for t in reading_tests],
        "writing": [{"id": t.id, "title": t.title, "test_type": t.test_type, "difficulty": t.difficulty, "created_at": t.created_at.isoformat()} for t in writing_tests],
        "listening": [{"id": t.id, "title": t.title, "difficulty": t.difficulty, "created_at": t.created_at.isoformat()} for t in listening_tests]
    }