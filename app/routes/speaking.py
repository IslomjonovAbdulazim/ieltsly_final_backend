from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.services.speaking_service import SpeakingService
from app.database import get_db

router = APIRouter()

class SpeakingSubmissionRequest(BaseModel):
    user_id: int
    test_id: int

class SpeakingAnswerRequest(BaseModel):
    question_number: int
    transcript: str = None

class SpeakingResponse(BaseModel):
    response_id: int
    question_number: int
    audio_file_path: str = None
    transcript: str = None
    analysis: str = None
    ai_followup_needed: bool = False

class SpeakingScoreResponse(BaseModel):
    submission_id: int
    fluency_coherence: float
    lexical_resource: float
    grammatical_accuracy: float
    pronunciation: float
    overall_band: float

@router.post("/submissions")
async def create_speaking_submission(request: SpeakingSubmissionRequest, db: Session = Depends(get_db)):
    submission = SpeakingService.create_submission(
        db=db,
        user_id=request.user_id,
        test_id=request.test_id
    )
    return {"submission_id": submission.id}

@router.post("/submissions/{submission_id}/responses")
async def submit_speaking_response(
    submission_id: int,
    question_number: int,
    audio_file: UploadFile = File(...),
    transcript: str = None,
    db: Session = Depends(get_db)
):
    # Save audio file (implement file storage logic)
    audio_path = f"audio/speaking/{submission_id}_{question_number}.mp3"
    
    response = SpeakingService.save_response(
        db=db,
        submission_id=submission_id,
        question_number=question_number,
        audio_file_path=audio_path,
        transcript=transcript
    )
    
    return SpeakingResponse(
        response_id=response.id,
        question_number=response.question_number,
        audio_file_path=response.audio_file_path,
        transcript=response.transcript,
        analysis=response.analysis,
        ai_followup_needed=response.ai_followup_needed
    )

@router.get("/submissions/{submission_id}/responses", response_model=List[SpeakingResponse])
async def get_speaking_responses(submission_id: int, db: Session = Depends(get_db)):
    responses = SpeakingService.get_responses_by_submission(db, submission_id)
    return [
        SpeakingResponse(
            response_id=r.id,
            question_number=r.question_number,
            audio_file_path=r.audio_file_path,
            transcript=r.transcript,
            analysis=r.analysis,
            ai_followup_needed=r.ai_followup_needed
        ) for r in responses
    ]

@router.post("/submissions/{submission_id}/analyze")
async def analyze_speaking_submission(submission_id: int, db: Session = Depends(get_db)):
    # Trigger AI analysis
    result = SpeakingService.analyze_submission(db, submission_id)
    return {"message": "Analysis completed", "analyzed_responses": len(result)}

@router.post("/submissions/{submission_id}/score", response_model=SpeakingScoreResponse)
async def score_speaking_submission(submission_id: int, db: Session = Depends(get_db)):
    score = SpeakingService.calculate_score(db, submission_id)
    
    if not score:
        raise HTTPException(status_code=404, detail="Submission not found or not ready for scoring")
    
    return SpeakingScoreResponse(
        submission_id=score.submission_id,
        fluency_coherence=score.fluency_coherence,
        lexical_resource=score.lexical_resource,
        grammatical_accuracy=score.grammatical_accuracy,
        pronunciation=score.pronunciation,
        overall_band=score.overall_band
    )

@router.post("/submissions/{submission_id}/complete")
async def complete_speaking_submission(submission_id: int, db: Session = Depends(get_db)):
    SpeakingService.complete_submission(db, submission_id)
    return {"message": "Submission completed"}