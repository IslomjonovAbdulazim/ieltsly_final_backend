from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.services.writing_service import WritingService
from app.database import get_db

router = APIRouter()

class WritingSubmissionRequest(BaseModel):
    user_id: int
    test_id: int

class WritingTaskSubmissionRequest(BaseModel):
    task_number: int
    user_text: str

class WritingTaskResponse(BaseModel):
    task_id: int
    task_number: int
    user_text: str
    word_count: int
    analysis: str = None
    detailed_feedback: str = None

class WritingScoreResponse(BaseModel):
    submission_id: int
    task_achievement: float
    coherence_cohesion: float
    lexical_resource: float
    grammatical_accuracy: float
    overall_band: float
    detailed_feedback: str = None

@router.post("/submissions")
async def create_writing_submission(request: WritingSubmissionRequest, db: Session = Depends(get_db)):
    submission = WritingService.create_submission(
        db=db,
        user_id=request.user_id,
        test_id=request.test_id
    )
    return {"submission_id": submission.id}

@router.get("/tests/{test_id}")
async def get_writing_test(test_id: int, db: Session = Depends(get_db)):
    test = WritingService.get_test_with_tasks(db, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    return {
        "test_id": test.id,
        "title": test.title,
        "test_type": test.test_type,
        "difficulty": test.difficulty,
        "tasks": [
            {
                "task_id": t.id,
                "task_number": t.task_number,
                "task_type": t.task_type,
                "prompt": t.prompt_markdown,
                "min_words": t.min_words,
                "max_words": t.max_words,
                "time_limit": t.time_limit_minutes
            } for t in test.tasks
        ]
    }

@router.post("/submissions/{submission_id}/tasks")
async def submit_writing_task(
    submission_id: int,
    request: WritingTaskSubmissionRequest,
    db: Session = Depends(get_db)
):
    response = WritingService.save_task_response(
        db=db,
        submission_id=submission_id,
        task_number=request.task_number,
        user_text=request.user_text
    )
    
    return WritingTaskResponse(
        task_id=response.id,
        task_number=response.task_number,
        user_text=response.user_text,
        word_count=response.word_count,
        analysis=response.analysis,
        detailed_feedback=response.detailed_feedback
    )

@router.get("/submissions/{submission_id}/tasks", response_model=List[WritingTaskResponse])
async def get_writing_tasks(submission_id: int, db: Session = Depends(get_db)):
    tasks = WritingService.get_task_responses_by_submission(db, submission_id)
    return [
        WritingTaskResponse(
            task_id=t.id,
            task_number=t.task_number,
            user_text=t.user_text,
            word_count=t.word_count,
            analysis=t.analysis,
            detailed_feedback=t.detailed_feedback
        ) for t in tasks
    ]

@router.post("/submissions/{submission_id}/analyze")
async def analyze_writing_submission(submission_id: int, db: Session = Depends(get_db)):
    result = WritingService.analyze_submission(db, submission_id)
    return {"message": "Analysis completed", "analyzed_tasks": len(result)}

@router.post("/submissions/{submission_id}/score", response_model=WritingScoreResponse)
async def score_writing_submission(submission_id: int, db: Session = Depends(get_db)):
    score = WritingService.calculate_score(db, submission_id)
    
    if not score:
        raise HTTPException(status_code=404, detail="Submission not found or not ready for scoring")
    
    return WritingScoreResponse(
        submission_id=score.submission_id,
        task_achievement=score.task_achievement,
        coherence_cohesion=score.coherence_cohesion,
        lexical_resource=score.lexical_resource,
        grammatical_accuracy=score.grammatical_accuracy,
        overall_band=score.overall_band,
        detailed_feedback=score.detailed_feedback
    )

@router.post("/submissions/{submission_id}/complete")
async def complete_writing_submission(submission_id: int, db: Session = Depends(get_db)):
    WritingService.complete_submission(db, submission_id)
    return {"message": "Submission completed"}

@router.get("/submissions/{submission_id}/word-count")
async def get_word_count(submission_id: int, task_number: int, db: Session = Depends(get_db)):
    word_count = WritingService.get_word_count(db, submission_id, task_number)
    return {"task_number": task_number, "word_count": word_count}