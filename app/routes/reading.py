from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.services.reading_service import ReadingService
from app.database import get_db

router = APIRouter()

class ReadingSubmissionRequest(BaseModel):
    user_id: int
    test_id: int

class ReadingAnswerRequest(BaseModel):
    question_number: int
    user_answers: List[str]

class ReadingAnswerResponse(BaseModel):
    question_number: int
    user_answers: List[str]
    is_correct: bool = None

class ReadingScoreResponse(BaseModel):
    submission_id: int
    correct_answers: int
    total_questions: int
    band_score: float
    percentage: float

class ReadingProgressResponse(BaseModel):
    total_questions: int
    answered_questions: int
    progress_percentage: float
    is_completed: bool

@router.post("/submissions")
async def create_reading_submission(request: ReadingSubmissionRequest, db: Session = Depends(get_db)):
    submission = ReadingService.create_submission(
        db=db,
        user_id=request.user_id,
        test_id=request.test_id
    )
    return {"submission_id": submission.id}

@router.get("/tests/{test_id}")
async def get_reading_test(test_id: int, db: Session = Depends(get_db)):
    test = ReadingService.get_test_with_passages(db, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    return {
        "test_id": test.id,
        "title": test.title,
        "difficulty": test.difficulty,
        "passages": [
            {
                "passage_id": p.id,
                "title": p.title,
                "content": p.content_markdown,
                "question_packs": [
                    {
                        "pack_id": qp.id,
                        "question_start": qp.question_start,
                        "question_end": qp.question_end,
                        "questions": qp.questions_markdown,
                        "order_matters": qp.order_matters
                    } for qp in p.question_packs
                ]
            } for p in test.passages
        ]
    }

@router.post("/submissions/{submission_id}/answers")
async def submit_reading_answer(
    submission_id: int,
    request: ReadingAnswerRequest,
    db: Session = Depends(get_db)
):
    answer = ReadingService.save_answer(
        db=db,
        submission_id=submission_id,
        question_number=request.question_number,
        user_answers=request.user_answers
    )
    
    return ReadingAnswerResponse(
        question_number=answer.question_number,
        user_answers=request.user_answers,
        is_correct=answer.is_correct
    )

@router.get("/submissions/{submission_id}/answers", response_model=List[ReadingAnswerResponse])
async def get_reading_answers(submission_id: int, db: Session = Depends(get_db)):
    from app.models.reading import ReadingSubmission
    submission = db.query(ReadingSubmission).filter(ReadingSubmission.id == submission_id).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    return [
        ReadingAnswerResponse(
            question_number=a.question_number,
            user_answers=a.user_answers,
            is_correct=a.is_correct
        ) for a in submission.answers
    ]

@router.get("/submissions/{submission_id}/progress", response_model=ReadingProgressResponse)
async def get_reading_progress(submission_id: int, db: Session = Depends(get_db)):
    progress = ReadingService.get_user_progress(db, submission_id)
    
    if not progress:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    return ReadingProgressResponse(**progress)

@router.post("/submissions/{submission_id}/grade", response_model=ReadingScoreResponse)
async def grade_reading_submission(submission_id: int, db: Session = Depends(get_db)):
    score = ReadingService.grade_submission(db, submission_id)
    
    if not score:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    return ReadingScoreResponse(
        submission_id=score.submission_id,
        correct_answers=score.correct_answers,
        total_questions=score.total_questions,
        band_score=score.band_score,
        percentage=score.percentage
    )

@router.post("/submissions/{submission_id}/complete")
async def complete_reading_submission(submission_id: int, db: Session = Depends(get_db)):
    ReadingService.complete_submission(db, submission_id)
    return {"message": "Submission completed"}