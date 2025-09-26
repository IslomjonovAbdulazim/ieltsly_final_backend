from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.auth import get_admin_user
from app.database import get_db
from app.models.writing import WritingTest, WritingTask

router = APIRouter()

# REQUEST MODELS
class CreateWritingTestRequest(BaseModel):
    title: str
    test_type: str  # "Academic" or "General"
    difficulty: str
    description: str = None

class UpdateWritingTestRequest(BaseModel):
    title: str = None
    test_type: str = None
    difficulty: str = None
    description: str = None

class CreateWritingTaskRequest(BaseModel):
    test_id: int
    task_number: int
    task_type: str
    prompt_markdown: str
    min_words: int
    max_words: int = None
    time_limit_minutes: int = 60

class UpdateWritingTaskRequest(BaseModel):
    task_type: str = None
    prompt_markdown: str = None
    min_words: int = None
    max_words: int = None
    time_limit_minutes: int = None

# CREATE OPERATIONS
@router.post("/tests")
async def create_writing_test(
    request: CreateWritingTestRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    test = WritingTest(
        title=request.title,
        test_type=request.test_type,
        difficulty=request.difficulty,
        description=request.description
    )
    db.add(test)
    db.commit()
    db.refresh(test)
    return {"test_id": test.id, "message": "Writing test created successfully"}

@router.post("/tasks")
async def create_writing_task(
    request: CreateWritingTaskRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    task = WritingTask(
        test_id=request.test_id,
        task_number=request.task_number,
        task_type=request.task_type,
        prompt_markdown=request.prompt_markdown,
        min_words=request.min_words,
        max_words=request.max_words,
        time_limit_minutes=request.time_limit_minutes
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return {"task_id": task.id, "message": "Writing task created successfully"}

# READ OPERATIONS
@router.get("/tests")
async def get_all_writing_tests(
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    tests = db.query(WritingTest).all()
    return [
        {
            "id": t.id,
            "title": t.title,
            "test_type": t.test_type,
            "difficulty": t.difficulty,
            "description": t.description,
            "created_at": t.created_at.isoformat()
        } for t in tests
    ]

@router.get("/tests/{test_id}")
async def get_writing_test_details(
    test_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    test = db.query(WritingTest).filter(WritingTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Writing test not found")
    
    tasks = db.query(WritingTask).filter(WritingTask.test_id == test_id).all()
    
    return {
        "id": test.id,
        "title": test.title,
        "test_type": test.test_type,
        "difficulty": test.difficulty,
        "description": test.description,
        "created_at": test.created_at.isoformat(),
        "tasks": [
            {
                "id": t.id,
                "task_number": t.task_number,
                "task_type": t.task_type,
                "prompt_markdown": t.prompt_markdown,
                "min_words": t.min_words,
                "max_words": t.max_words,
                "time_limit_minutes": t.time_limit_minutes
            } for t in tasks
        ]
    }

@router.get("/tasks/{task_id}")
async def get_writing_task(
    task_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    task = db.query(WritingTask).filter(WritingTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Writing task not found")
    
    return {
        "id": task.id,
        "test_id": task.test_id,
        "task_number": task.task_number,
        "task_type": task.task_type,
        "prompt_markdown": task.prompt_markdown,
        "min_words": task.min_words,
        "max_words": task.max_words,
        "time_limit_minutes": task.time_limit_minutes
    }

# UPDATE OPERATIONS
@router.put("/tests/{test_id}")
async def update_writing_test(
    test_id: int,
    request: UpdateWritingTestRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    test = db.query(WritingTest).filter(WritingTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Writing test not found")
    
    if request.title is not None:
        test.title = request.title
    if request.test_type is not None:
        test.test_type = request.test_type
    if request.difficulty is not None:
        test.difficulty = request.difficulty
    if request.description is not None:
        test.description = request.description
    
    db.commit()
    return {"message": "Writing test updated successfully"}

@router.put("/tasks/{task_id}")
async def update_writing_task(
    task_id: int,
    request: UpdateWritingTaskRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    task = db.query(WritingTask).filter(WritingTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Writing task not found")
    
    if request.task_type is not None:
        task.task_type = request.task_type
    if request.prompt_markdown is not None:
        task.prompt_markdown = request.prompt_markdown
    if request.min_words is not None:
        task.min_words = request.min_words
    if request.max_words is not None:
        task.max_words = request.max_words
    if request.time_limit_minutes is not None:
        task.time_limit_minutes = request.time_limit_minutes
    
    db.commit()
    return {"message": "Writing task updated successfully"}

# DELETE OPERATIONS
@router.delete("/tests/{test_id}")
async def delete_writing_test(
    test_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    test = db.query(WritingTest).filter(WritingTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Writing test not found")
    
    db.delete(test)
    db.commit()
    return {"message": "Writing test deleted successfully"}

@router.delete("/tasks/{task_id}")
async def delete_writing_task(
    task_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    task = db.query(WritingTask).filter(WritingTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Writing task not found")
    
    db.delete(task)
    db.commit()
    return {"message": "Writing task deleted successfully"}