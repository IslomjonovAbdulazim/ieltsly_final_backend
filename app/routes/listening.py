from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.services.listening_service import ListeningService
from app.database import get_db

router = APIRouter()

class ListeningSubmissionRequest(BaseModel):
    user_id: int
    test_id: int

class ListeningAnswerRequest(BaseModel):
    question_number: int
    user_answers: List[str]

class ListeningAnswerResponse(BaseModel):
    question_number: int
    user_answers: List[str]
    is_correct: bool = None

class ListeningScoreResponse(BaseModel):
    submission_id: int
    correct_answers: int
    total_questions: int
    band_score: float
    percentage: float

class ListeningProgressResponse(BaseModel):
    total_questions: int
    answered_questions: int
    progress_percentage: float
    is_completed: bool
    current_section: str = None

@router.post("/submissions")
async def create_listening_submission(request: ListeningSubmissionRequest, db: Session = Depends(get_db)):
    submission = ListeningService.create_submission(
        db=db,
        user_id=request.user_id,
        test_id=request.test_id
    )
    return {"submission_id": submission.id}

@router.get("/tests/{test_id}")
async def get_listening_test(test_id: int, db: Session = Depends(get_db)):
    test = ListeningService.get_test_with_sections(db, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    return {
        "test_id": test.id,
        "title": test.title,
        "difficulty": test.difficulty,
        "sections": [
            {
                "section_id": s.id,
                "section_type": s.section_type,
                "audio_file_path": s.audio_file_path,
                "context": s.context,
                "question_packs": [
                    {
                        "pack_id": qp.id,
                        "question_start": qp.question_start,
                        "question_end": qp.question_end,
                        "questions": qp.questions_markdown,
                        "image_path": qp.image_path,
                        "order_matters": qp.order_matters
                    } for qp in s.question_packs
                ]
            } for s in test.sections
        ]
    }

@router.get("/sections/{section_id}/audio")
async def get_section_audio(section_id: int, db: Session = Depends(get_db)):
    audio_path = ListeningService.get_section_audio_path(db, section_id)
    if not audio_path:
        raise HTTPException(status_code=404, detail="Audio not found")
    
    return {"audio_file_path": audio_path}

@router.post("/submissions/{submission_id}/answers")
async def submit_listening_answer(
    submission_id: int,
    request: ListeningAnswerRequest,
    db: Session = Depends(get_db)
):
    answer = ListeningService.save_answer(
        db=db,
        submission_id=submission_id,
        question_number=request.question_number,
        user_answers=request.user_answers
    )
    
    return ListeningAnswerResponse(
        question_number=answer.question_number,
        user_answers=request.user_answers,
        is_correct=answer.is_correct
    )

@router.get("/submissions/{submission_id}/answers", response_model=List[ListeningAnswerResponse])
async def get_listening_answers(submission_id: int, db: Session = Depends(get_db)):
    from app.models.listening import ListeningSubmission
    submission = db.query(ListeningSubmission).filter(ListeningSubmission.id == submission_id).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    return [
        ListeningAnswerResponse(
            question_number=a.question_number,
            user_answers=a.user_answers,
            is_correct=a.is_correct
        ) for a in submission.answers
    ]

@router.get("/submissions/{submission_id}/progress", response_model=ListeningProgressResponse)
async def get_listening_progress(submission_id: int, db: Session = Depends(get_db)):
    progress = ListeningService.get_user_progress(db, submission_id)
    
    if not progress:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    return ListeningProgressResponse(**progress)

@router.post("/submissions/{submission_id}/grade", response_model=ListeningScoreResponse)
async def grade_listening_submission(submission_id: int, db: Session = Depends(get_db)):
    score = ListeningService.grade_submission(db, submission_id)
    
    if not score:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    return ListeningScoreResponse(
        submission_id=score.submission_id,
        correct_answers=score.correct_answers,
        total_questions=score.total_questions,
        band_score=score.band_score,
        percentage=score.percentage
    )

@router.post("/submissions/{submission_id}/complete")
async def complete_listening_submission(submission_id: int, db: Session = Depends(get_db)):
    ListeningService.complete_submission(db, submission_id)
    return {"message": "Submission completed"}

@router.get("/questions/{question_number}/pack")
async def get_question_pack(test_id: int, question_number: int, db: Session = Depends(get_db)):
    pack = ListeningService.get_question_pack_by_number(db, test_id, question_number)
    if not pack:
        raise HTTPException(status_code=404, detail="Question pack not found")
    
    return {
        "pack_id": pack.id,
        "question_start": pack.question_start,
        "question_end": pack.question_end,
        "questions": pack.questions_markdown,
        "image_path": pack.image_path
    }