from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.auth import get_admin_user
from app.database import get_db
from app.models.speaking import SpeakingTest, SpeakingQuestion

router = APIRouter()

# REQUEST MODELS
class CreateSpeakingTestRequest(BaseModel):
    title: str
    difficulty: str
    description: str = None

class UpdateSpeakingTestRequest(BaseModel):
    title: str = None
    difficulty: str = None
    description: str = None

class CreateSpeakingQuestionRequest(BaseModel):
    test_id: int
    question_number: int
    prompt: str
    preparation_time: int = 15
    response_time: int = 60

class UpdateSpeakingQuestionRequest(BaseModel):
    prompt: str = None
    preparation_time: int = None
    response_time: int = None

# CREATE OPERATIONS
@router.post("/tests")
async def create_speaking_test(
    request: CreateSpeakingTestRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    test = SpeakingTest(
        title=request.title,
        difficulty=request.difficulty,
        description=request.description
    )
    db.add(test)
    db.commit()
    db.refresh(test)
    return {"test_id": test.id, "message": "Speaking test created successfully"}

@router.post("/questions")
async def create_speaking_question(
    request: CreateSpeakingQuestionRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    question = SpeakingQuestion(
        test_id=request.test_id,
        question_number=request.question_number,
        prompt=request.prompt,
        preparation_time=request.preparation_time,
        response_time=request.response_time
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return {"question_id": question.id, "message": "Speaking question created successfully"}

# READ OPERATIONS
@router.get("/tests")
async def get_all_speaking_tests(
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    tests = db.query(SpeakingTest).all()
    return [
        {
            "id": t.id,
            "title": t.title,
            "difficulty": t.difficulty,
            "description": t.description,
            "created_at": t.created_at.isoformat()
        } for t in tests
    ]

@router.get("/tests/{test_id}")
async def get_speaking_test_details(
    test_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    test = db.query(SpeakingTest).filter(SpeakingTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Speaking test not found")
    
    questions = db.query(SpeakingQuestion).filter(SpeakingQuestion.test_id == test_id).all()
    
    return {
        "id": test.id,
        "title": test.title,
        "difficulty": test.difficulty,
        "description": test.description,
        "created_at": test.created_at.isoformat(),
        "questions": [
            {
                "id": q.id,
                "question_number": q.question_number,
                "prompt": q.prompt,
                "preparation_time": q.preparation_time,
                "response_time": q.response_time
            } for q in questions
        ]
    }

@router.get("/questions/{question_id}")
async def get_speaking_question(
    question_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    question = db.query(SpeakingQuestion).filter(SpeakingQuestion.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Speaking question not found")
    
    return {
        "id": question.id,
        "test_id": question.test_id,
        "question_number": question.question_number,
        "prompt": question.prompt,
        "preparation_time": question.preparation_time,
        "response_time": question.response_time
    }

# UPDATE OPERATIONS
@router.put("/tests/{test_id}")
async def update_speaking_test(
    test_id: int,
    request: UpdateSpeakingTestRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    test = db.query(SpeakingTest).filter(SpeakingTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Speaking test not found")
    
    if request.title is not None:
        test.title = request.title
    if request.difficulty is not None:
        test.difficulty = request.difficulty
    if request.description is not None:
        test.description = request.description
    
    db.commit()
    return {"message": "Speaking test updated successfully"}

@router.put("/questions/{question_id}")
async def update_speaking_question(
    question_id: int,
    request: UpdateSpeakingQuestionRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    question = db.query(SpeakingQuestion).filter(SpeakingQuestion.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Speaking question not found")
    
    if request.prompt is not None:
        question.prompt = request.prompt
    if request.preparation_time is not None:
        question.preparation_time = request.preparation_time
    if request.response_time is not None:
        question.response_time = request.response_time
    
    db.commit()
    return {"message": "Speaking question updated successfully"}

# DELETE OPERATIONS
@router.delete("/tests/{test_id}")
async def delete_speaking_test(
    test_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    test = db.query(SpeakingTest).filter(SpeakingTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Speaking test not found")
    
    db.delete(test)
    db.commit()
    return {"message": "Speaking test deleted successfully"}

@router.delete("/questions/{question_id}")
async def delete_speaking_question(
    question_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    question = db.query(SpeakingQuestion).filter(SpeakingQuestion.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Speaking question not found")
    
    db.delete(question)
    db.commit()
    return {"message": "Speaking question deleted successfully"}