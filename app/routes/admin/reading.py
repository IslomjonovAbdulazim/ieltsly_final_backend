from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.auth import get_admin_user
from app.database import get_db
from app.models.reading import ReadingTest, ReadingPassage, ReadingQuestionPack

router = APIRouter()

# REQUEST MODELS
class CreateReadingTestRequest(BaseModel):
    title: str
    difficulty: str
    description: str = None

class UpdateReadingTestRequest(BaseModel):
    title: str = None
    difficulty: str = None
    description: str = None

class CreateReadingPassageRequest(BaseModel):
    test_id: int
    title: str
    content_markdown: str

class UpdateReadingPassageRequest(BaseModel):
    title: str = None
    content_markdown: str = None

class CreateReadingQuestionPackRequest(BaseModel):
    passage_id: int
    question_start: int
    question_end: int
    questions_markdown: str
    correct_answers: str  # JSON string
    order_matters: bool = True

class UpdateReadingQuestionPackRequest(BaseModel):
    questions_markdown: str = None
    correct_answers: str = None
    order_matters: bool = None

# CREATE OPERATIONS
@router.post("/tests")
async def create_reading_test(
    request: CreateReadingTestRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    test = ReadingTest(
        title=request.title,
        difficulty=request.difficulty,
        description=request.description
    )
    db.add(test)
    db.commit()
    db.refresh(test)
    return {"test_id": test.id, "message": "Reading test created successfully"}

@router.post("/passages")
async def create_reading_passage(
    request: CreateReadingPassageRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    passage = ReadingPassage(
        test_id=request.test_id,
        title=request.title,
        content_markdown=request.content_markdown
    )
    db.add(passage)
    db.commit()
    db.refresh(passage)
    return {"passage_id": passage.id, "message": "Reading passage created successfully"}

@router.post("/question-packs")
async def create_reading_question_pack(
    request: CreateReadingQuestionPackRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    pack = ReadingQuestionPack(
        passage_id=request.passage_id,
        question_start=request.question_start,
        question_end=request.question_end,
        questions_markdown=request.questions_markdown,
        correct_answers=request.correct_answers,
        order_matters=request.order_matters
    )
    db.add(pack)
    db.commit()
    db.refresh(pack)
    return {"pack_id": pack.id, "message": "Reading question pack created successfully"}

# READ OPERATIONS
@router.get("/tests")
async def get_all_reading_tests(
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    tests = db.query(ReadingTest).all()
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
async def get_reading_test_details(
    test_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    test = db.query(ReadingTest).filter(ReadingTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Reading test not found")
    
    passages = db.query(ReadingPassage).filter(ReadingPassage.test_id == test_id).all()
    
    return {
        "id": test.id,
        "title": test.title,
        "difficulty": test.difficulty,
        "description": test.description,
        "created_at": test.created_at.isoformat(),
        "passages": [
            {
                "id": p.id,
                "title": p.title,
                "content_markdown": p.content_markdown,
                "question_packs": [
                    {
                        "id": qp.id,
                        "question_start": qp.question_start,
                        "question_end": qp.question_end,
                        "questions_markdown": qp.questions_markdown,
                        "correct_answers": qp.correct_answers,
                        "order_matters": qp.order_matters
                    } for qp in p.question_packs
                ]
            } for p in passages
        ]
    }

@router.get("/passages/{passage_id}")
async def get_reading_passage(
    passage_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    passage = db.query(ReadingPassage).filter(ReadingPassage.id == passage_id).first()
    if not passage:
        raise HTTPException(status_code=404, detail="Reading passage not found")
    
    return {
        "id": passage.id,
        "test_id": passage.test_id,
        "title": passage.title,
        "content_markdown": passage.content_markdown,
        "question_packs": [
            {
                "id": qp.id,
                "question_start": qp.question_start,
                "question_end": qp.question_end,
                "questions_markdown": qp.questions_markdown,
                "correct_answers": qp.correct_answers,
                "order_matters": qp.order_matters
            } for qp in passage.question_packs
        ]
    }

@router.get("/question-packs/{pack_id}")
async def get_reading_question_pack(
    pack_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    pack = db.query(ReadingQuestionPack).filter(ReadingQuestionPack.id == pack_id).first()
    if not pack:
        raise HTTPException(status_code=404, detail="Reading question pack not found")
    
    return {
        "id": pack.id,
        "passage_id": pack.passage_id,
        "question_start": pack.question_start,
        "question_end": pack.question_end,
        "questions_markdown": pack.questions_markdown,
        "correct_answers": pack.correct_answers,
        "order_matters": pack.order_matters
    }

# UPDATE OPERATIONS
@router.put("/tests/{test_id}")
async def update_reading_test(
    test_id: int,
    request: UpdateReadingTestRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    test = db.query(ReadingTest).filter(ReadingTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Reading test not found")
    
    if request.title is not None:
        test.title = request.title
    if request.difficulty is not None:
        test.difficulty = request.difficulty
    if request.description is not None:
        test.description = request.description
    
    db.commit()
    return {"message": "Reading test updated successfully"}

@router.put("/passages/{passage_id}")
async def update_reading_passage(
    passage_id: int,
    request: UpdateReadingPassageRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    passage = db.query(ReadingPassage).filter(ReadingPassage.id == passage_id).first()
    if not passage:
        raise HTTPException(status_code=404, detail="Reading passage not found")
    
    if request.title is not None:
        passage.title = request.title
    if request.content_markdown is not None:
        passage.content_markdown = request.content_markdown
    
    db.commit()
    return {"message": "Reading passage updated successfully"}

@router.put("/question-packs/{pack_id}")
async def update_reading_question_pack(
    pack_id: int,
    request: UpdateReadingQuestionPackRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    pack = db.query(ReadingQuestionPack).filter(ReadingQuestionPack.id == pack_id).first()
    if not pack:
        raise HTTPException(status_code=404, detail="Reading question pack not found")
    
    if request.questions_markdown is not None:
        pack.questions_markdown = request.questions_markdown
    if request.correct_answers is not None:
        pack.correct_answers = request.correct_answers
    if request.order_matters is not None:
        pack.order_matters = request.order_matters
    
    db.commit()
    return {"message": "Reading question pack updated successfully"}

# DELETE OPERATIONS
@router.delete("/tests/{test_id}")
async def delete_reading_test(
    test_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    test = db.query(ReadingTest).filter(ReadingTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Reading test not found")
    
    db.delete(test)
    db.commit()
    return {"message": "Reading test deleted successfully"}

@router.delete("/passages/{passage_id}")
async def delete_reading_passage(
    passage_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    passage = db.query(ReadingPassage).filter(ReadingPassage.id == passage_id).first()
    if not passage:
        raise HTTPException(status_code=404, detail="Reading passage not found")
    
    db.delete(passage)
    db.commit()
    return {"message": "Reading passage deleted successfully"}

@router.delete("/question-packs/{pack_id}")
async def delete_reading_question_pack(
    pack_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    pack = db.query(ReadingQuestionPack).filter(ReadingQuestionPack.id == pack_id).first()
    if not pack:
        raise HTTPException(status_code=404, detail="Reading question pack not found")
    
    db.delete(pack)
    db.commit()
    return {"message": "Reading question pack deleted successfully"}