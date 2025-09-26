from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.auth import get_admin_user
from app.database import get_db
from app.models.listening import ListeningTest, ListeningSection, ListeningQuestionPack

router = APIRouter()

# REQUEST MODELS
class CreateListeningTestRequest(BaseModel):
    title: str
    difficulty: str
    description: str = None

class UpdateListeningTestRequest(BaseModel):
    title: str = None
    difficulty: str = None
    description: str = None

class CreateListeningSectionRequest(BaseModel):
    test_id: int
    section_type: str
    audio_file_path: str
    context: str = None

class UpdateListeningSectionRequest(BaseModel):
    section_type: str = None
    audio_file_path: str = None
    context: str = None

class CreateListeningQuestionPackRequest(BaseModel):
    section_id: int
    question_start: int
    question_end: int
    questions_markdown: str
    correct_answers: str  # JSON string
    image_path: str = None
    order_matters: bool = True

class UpdateListeningQuestionPackRequest(BaseModel):
    questions_markdown: str = None
    correct_answers: str = None
    image_path: str = None
    order_matters: bool = None

# CREATE OPERATIONS
@router.post("/tests")
async def create_listening_test(
    request: CreateListeningTestRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    test = ListeningTest(
        title=request.title,
        difficulty=request.difficulty,
        description=request.description
    )
    db.add(test)
    db.commit()
    db.refresh(test)
    return {"test_id": test.id, "message": "Listening test created successfully"}

@router.post("/sections")
async def create_listening_section(
    request: CreateListeningSectionRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    section = ListeningSection(
        test_id=request.test_id,
        section_type=request.section_type,
        audio_file_path=request.audio_file_path,
        context=request.context
    )
    db.add(section)
    db.commit()
    db.refresh(section)
    return {"section_id": section.id, "message": "Listening section created successfully"}

@router.post("/question-packs")
async def create_listening_question_pack(
    request: CreateListeningQuestionPackRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    pack = ListeningQuestionPack(
        section_id=request.section_id,
        question_start=request.question_start,
        question_end=request.question_end,
        questions_markdown=request.questions_markdown,
        correct_answers=request.correct_answers,
        image_path=request.image_path,
        order_matters=request.order_matters
    )
    db.add(pack)
    db.commit()
    db.refresh(pack)
    return {"pack_id": pack.id, "message": "Listening question pack created successfully"}

# READ OPERATIONS
@router.get("/tests")
async def get_all_listening_tests(
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    tests = db.query(ListeningTest).all()
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
async def get_listening_test_details(
    test_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    test = db.query(ListeningTest).filter(ListeningTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Listening test not found")
    
    sections = db.query(ListeningSection).filter(ListeningSection.test_id == test_id).all()
    
    return {
        "id": test.id,
        "title": test.title,
        "difficulty": test.difficulty,
        "description": test.description,
        "created_at": test.created_at.isoformat(),
        "sections": [
            {
                "id": s.id,
                "section_type": s.section_type,
                "audio_file_path": s.audio_file_path,
                "context": s.context,
                "question_packs": [
                    {
                        "id": qp.id,
                        "question_start": qp.question_start,
                        "question_end": qp.question_end,
                        "questions_markdown": qp.questions_markdown,
                        "correct_answers": qp.correct_answers,
                        "image_path": qp.image_path,
                        "order_matters": qp.order_matters
                    } for qp in s.question_packs
                ]
            } for s in sections
        ]
    }

@router.get("/sections/{section_id}")
async def get_listening_section(
    section_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    section = db.query(ListeningSection).filter(ListeningSection.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Listening section not found")
    
    return {
        "id": section.id,
        "test_id": section.test_id,
        "section_type": section.section_type,
        "audio_file_path": section.audio_file_path,
        "context": section.context,
        "question_packs": [
            {
                "id": qp.id,
                "question_start": qp.question_start,
                "question_end": qp.question_end,
                "questions_markdown": qp.questions_markdown,
                "correct_answers": qp.correct_answers,
                "image_path": qp.image_path,
                "order_matters": qp.order_matters
            } for qp in section.question_packs
        ]
    }

@router.get("/question-packs/{pack_id}")
async def get_listening_question_pack(
    pack_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    pack = db.query(ListeningQuestionPack).filter(ListeningQuestionPack.id == pack_id).first()
    if not pack:
        raise HTTPException(status_code=404, detail="Listening question pack not found")
    
    return {
        "id": pack.id,
        "section_id": pack.section_id,
        "question_start": pack.question_start,
        "question_end": pack.question_end,
        "questions_markdown": pack.questions_markdown,
        "correct_answers": pack.correct_answers,
        "image_path": pack.image_path,
        "order_matters": pack.order_matters
    }

# UPDATE OPERATIONS
@router.put("/tests/{test_id}")
async def update_listening_test(
    test_id: int,
    request: UpdateListeningTestRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    test = db.query(ListeningTest).filter(ListeningTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Listening test not found")
    
    if request.title is not None:
        test.title = request.title
    if request.difficulty is not None:
        test.difficulty = request.difficulty
    if request.description is not None:
        test.description = request.description
    
    db.commit()
    return {"message": "Listening test updated successfully"}

@router.put("/sections/{section_id}")
async def update_listening_section(
    section_id: int,
    request: UpdateListeningSectionRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    section = db.query(ListeningSection).filter(ListeningSection.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Listening section not found")
    
    if request.section_type is not None:
        section.section_type = request.section_type
    if request.audio_file_path is not None:
        section.audio_file_path = request.audio_file_path
    if request.context is not None:
        section.context = request.context
    
    db.commit()
    return {"message": "Listening section updated successfully"}

@router.put("/question-packs/{pack_id}")
async def update_listening_question_pack(
    pack_id: int,
    request: UpdateListeningQuestionPackRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    pack = db.query(ListeningQuestionPack).filter(ListeningQuestionPack.id == pack_id).first()
    if not pack:
        raise HTTPException(status_code=404, detail="Listening question pack not found")
    
    if request.questions_markdown is not None:
        pack.questions_markdown = request.questions_markdown
    if request.correct_answers is not None:
        pack.correct_answers = request.correct_answers
    if request.image_path is not None:
        pack.image_path = request.image_path
    if request.order_matters is not None:
        pack.order_matters = request.order_matters
    
    db.commit()
    return {"message": "Listening question pack updated successfully"}

# DELETE OPERATIONS
@router.delete("/tests/{test_id}")
async def delete_listening_test(
    test_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    test = db.query(ListeningTest).filter(ListeningTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Listening test not found")
    
    db.delete(test)
    db.commit()
    return {"message": "Listening test deleted successfully"}

@router.delete("/sections/{section_id}")
async def delete_listening_section(
    section_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    section = db.query(ListeningSection).filter(ListeningSection.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Listening section not found")
    
    db.delete(section)
    db.commit()
    return {"message": "Listening section deleted successfully"}

@router.delete("/question-packs/{pack_id}")
async def delete_listening_question_pack(
    pack_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    pack = db.query(ListeningQuestionPack).filter(ListeningQuestionPack.id == pack_id).first()
    if not pack:
        raise HTTPException(status_code=404, detail="Listening question pack not found")
    
    db.delete(pack)
    db.commit()
    return {"message": "Listening question pack deleted successfully"}