from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.auth import get_admin_user
from app.database import get_db
from app.models.speaking import SpeakingTest, SpeakingQuestion
from app.models.reading import ReadingTest, ReadingPassage, ReadingQuestionPack
from app.models.writing import WritingTest, WritingTask
from app.models.listening import ListeningTest, ListeningSection, ListeningQuestionPack

router = APIRouter()

# Speaking Test Admin
class CreateSpeakingTestRequest(BaseModel):
    title: str
    difficulty: str
    description: str = None

class CreateSpeakingQuestionRequest(BaseModel):
    test_id: int
    question_number: int
    prompt: str
    preparation_time: int = 15
    response_time: int = 60

@router.post("/speaking/tests")
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
    return {"test_id": test.id, "message": "Speaking test created"}

@router.post("/speaking/questions")
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
    return {"question_id": question.id, "message": "Speaking question created"}

# Reading Test Admin
class CreateReadingTestRequest(BaseModel):
    title: str
    difficulty: str
    description: str = None

class CreateReadingPassageRequest(BaseModel):
    test_id: int
    title: str
    content_markdown: str

class CreateReadingQuestionPackRequest(BaseModel):
    passage_id: int
    question_start: int
    question_end: int
    questions_markdown: str
    correct_answers: str  # JSON string
    order_matters: bool = True

@router.post("/reading/tests")
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
    return {"test_id": test.id, "message": "Reading test created"}

@router.post("/reading/passages")
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
    return {"passage_id": passage.id, "message": "Reading passage created"}

@router.post("/reading/question-packs")
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
    return {"pack_id": pack.id, "message": "Question pack created"}

# Writing Test Admin
class CreateWritingTestRequest(BaseModel):
    title: str
    test_type: str  # "Academic" or "General"
    difficulty: str
    description: str = None

class CreateWritingTaskRequest(BaseModel):
    test_id: int
    task_number: int
    task_type: str
    prompt_markdown: str
    min_words: int
    max_words: int = None
    time_limit_minutes: int = 60

@router.post("/writing/tests")
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
    return {"test_id": test.id, "message": "Writing test created"}

@router.post("/writing/tasks")
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
    return {"task_id": task.id, "message": "Writing task created"}

# Listening Test Admin
class CreateListeningTestRequest(BaseModel):
    title: str
    difficulty: str
    description: str = None

class CreateListeningSectionRequest(BaseModel):
    test_id: int
    section_type: str
    audio_file_path: str
    context: str = None

class CreateListeningQuestionPackRequest(BaseModel):
    section_id: int
    question_start: int
    question_end: int
    questions_markdown: str
    correct_answers: str  # JSON string
    image_path: str = None
    order_matters: bool = True

@router.post("/listening/tests")
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
    return {"test_id": test.id, "message": "Listening test created"}

@router.post("/listening/sections")
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
    return {"section_id": section.id, "message": "Listening section created"}

@router.post("/listening/question-packs")
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
    return {"pack_id": pack.id, "message": "Question pack created"}

# READ OPERATIONS

@router.get("/tests/all")
async def get_all_tests(
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
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

@router.get("/speaking/tests/{test_id}")
async def get_speaking_test_details(
    test_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    test = db.query(SpeakingTest).filter(SpeakingTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    from app.models.speaking import SpeakingQuestion
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

@router.get("/reading/tests/{test_id}")
async def get_reading_test_details(
    test_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    test = db.query(ReadingTest).filter(ReadingTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    from app.models.reading import ReadingPassage
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

@router.get("/writing/tests/{test_id}")
async def get_writing_test_details(
    test_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    test = db.query(WritingTest).filter(WritingTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    from app.models.writing import WritingTask
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

@router.get("/listening/tests/{test_id}")
async def get_listening_test_details(
    test_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    test = db.query(ListeningTest).filter(ListeningTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    from app.models.listening import ListeningSection
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

# UPDATE OPERATIONS

class UpdateSpeakingTestRequest(BaseModel):
    title: str = None
    difficulty: str = None
    description: str = None

class UpdateSpeakingQuestionRequest(BaseModel):
    prompt: str = None
    preparation_time: int = None
    response_time: int = None

class UpdateReadingTestRequest(BaseModel):
    title: str = None
    difficulty: str = None
    description: str = None

class UpdateReadingPassageRequest(BaseModel):
    title: str = None
    content_markdown: str = None

class UpdateReadingQuestionPackRequest(BaseModel):
    questions_markdown: str = None
    correct_answers: str = None
    order_matters: bool = None

class UpdateWritingTestRequest(BaseModel):
    title: str = None
    test_type: str = None
    difficulty: str = None
    description: str = None

class UpdateWritingTaskRequest(BaseModel):
    task_type: str = None
    prompt_markdown: str = None
    min_words: int = None
    max_words: int = None
    time_limit_minutes: int = None

class UpdateListeningTestRequest(BaseModel):
    title: str = None
    difficulty: str = None
    description: str = None

class UpdateListeningSectionRequest(BaseModel):
    section_type: str = None
    audio_file_path: str = None
    context: str = None

class UpdateListeningQuestionPackRequest(BaseModel):
    questions_markdown: str = None
    correct_answers: str = None
    image_path: str = None
    order_matters: bool = None

@router.put("/speaking/tests/{test_id}")
async def update_speaking_test(
    test_id: int,
    request: UpdateSpeakingTestRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    test = db.query(SpeakingTest).filter(SpeakingTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    if request.title is not None:
        test.title = request.title
    if request.difficulty is not None:
        test.difficulty = request.difficulty
    if request.description is not None:
        test.description = request.description
    
    db.commit()
    return {"message": "Speaking test updated successfully"}

@router.put("/speaking/questions/{question_id}")
async def update_speaking_question(
    question_id: int,
    request: UpdateSpeakingQuestionRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    question = db.query(SpeakingQuestion).filter(SpeakingQuestion.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    if request.prompt is not None:
        question.prompt = request.prompt
    if request.preparation_time is not None:
        question.preparation_time = request.preparation_time
    if request.response_time is not None:
        question.response_time = request.response_time
    
    db.commit()
    return {"message": "Speaking question updated successfully"}

@router.put("/reading/tests/{test_id}")
async def update_reading_test(
    test_id: int,
    request: UpdateReadingTestRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    test = db.query(ReadingTest).filter(ReadingTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    if request.title is not None:
        test.title = request.title
    if request.difficulty is not None:
        test.difficulty = request.difficulty
    if request.description is not None:
        test.description = request.description
    
    db.commit()
    return {"message": "Reading test updated successfully"}

@router.put("/reading/passages/{passage_id}")
async def update_reading_passage(
    passage_id: int,
    request: UpdateReadingPassageRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    passage = db.query(ReadingPassage).filter(ReadingPassage.id == passage_id).first()
    if not passage:
        raise HTTPException(status_code=404, detail="Passage not found")
    
    if request.title is not None:
        passage.title = request.title
    if request.content_markdown is not None:
        passage.content_markdown = request.content_markdown
    
    db.commit()
    return {"message": "Reading passage updated successfully"}

@router.put("/reading/question-packs/{pack_id}")
async def update_reading_question_pack(
    pack_id: int,
    request: UpdateReadingQuestionPackRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    pack = db.query(ReadingQuestionPack).filter(ReadingQuestionPack.id == pack_id).first()
    if not pack:
        raise HTTPException(status_code=404, detail="Question pack not found")
    
    if request.questions_markdown is not None:
        pack.questions_markdown = request.questions_markdown
    if request.correct_answers is not None:
        pack.correct_answers = request.correct_answers
    if request.order_matters is not None:
        pack.order_matters = request.order_matters
    
    db.commit()
    return {"message": "Question pack updated successfully"}

@router.put("/writing/tests/{test_id}")
async def update_writing_test(
    test_id: int,
    request: UpdateWritingTestRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    test = db.query(WritingTest).filter(WritingTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
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

@router.put("/writing/tasks/{task_id}")
async def update_writing_task(
    task_id: int,
    request: UpdateWritingTaskRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    task = db.query(WritingTask).filter(WritingTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
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

@router.put("/listening/tests/{test_id}")
async def update_listening_test(
    test_id: int,
    request: UpdateListeningTestRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    test = db.query(ListeningTest).filter(ListeningTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    if request.title is not None:
        test.title = request.title
    if request.difficulty is not None:
        test.difficulty = request.difficulty
    if request.description is not None:
        test.description = request.description
    
    db.commit()
    return {"message": "Listening test updated successfully"}

@router.put("/listening/sections/{section_id}")
async def update_listening_section(
    section_id: int,
    request: UpdateListeningSectionRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    section = db.query(ListeningSection).filter(ListeningSection.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    
    if request.section_type is not None:
        section.section_type = request.section_type
    if request.audio_file_path is not None:
        section.audio_file_path = request.audio_file_path
    if request.context is not None:
        section.context = request.context
    
    db.commit()
    return {"message": "Listening section updated successfully"}

@router.put("/listening/question-packs/{pack_id}")
async def update_listening_question_pack(
    pack_id: int,
    request: UpdateListeningQuestionPackRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    pack = db.query(ListeningQuestionPack).filter(ListeningQuestionPack.id == pack_id).first()
    if not pack:
        raise HTTPException(status_code=404, detail="Question pack not found")
    
    if request.questions_markdown is not None:
        pack.questions_markdown = request.questions_markdown
    if request.correct_answers is not None:
        pack.correct_answers = request.correct_answers
    if request.image_path is not None:
        pack.image_path = request.image_path
    if request.order_matters is not None:
        pack.order_matters = request.order_matters
    
    db.commit()
    return {"message": "Question pack updated successfully"}

# Delete endpoints
@router.delete("/tests/{skill}/{test_id}")
async def delete_test(
    skill: str,
    test_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    model_map = {
        "speaking": SpeakingTest,
        "reading": ReadingTest,
        "writing": WritingTest,
        "listening": ListeningTest
    }
    
    if skill not in model_map:
        raise HTTPException(status_code=400, detail="Invalid skill type")
    
    test = db.query(model_map[skill]).filter(model_map[skill].id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    db.delete(test)
    db.commit()
    return {"message": f"{skill.capitalize()} test deleted successfully"}

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

@router.get("/dashboard/stats")
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

# ADDITIONAL DELETE ENDPOINTS FOR GRANULAR CONTROL

@router.delete("/speaking/questions/{question_id}")
async def delete_speaking_question(
    question_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    from app.models.speaking import SpeakingQuestion
    question = db.query(SpeakingQuestion).filter(SpeakingQuestion.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    db.delete(question)
    db.commit()
    return {"message": "Speaking question deleted successfully"}

@router.delete("/reading/passages/{passage_id}")
async def delete_reading_passage(
    passage_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    passage = db.query(ReadingPassage).filter(ReadingPassage.id == passage_id).first()
    if not passage:
        raise HTTPException(status_code=404, detail="Passage not found")
    
    db.delete(passage)
    db.commit()
    return {"message": "Reading passage deleted successfully"}

@router.delete("/reading/question-packs/{pack_id}")
async def delete_reading_question_pack(
    pack_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    pack = db.query(ReadingQuestionPack).filter(ReadingQuestionPack.id == pack_id).first()
    if not pack:
        raise HTTPException(status_code=404, detail="Question pack not found")
    
    db.delete(pack)
    db.commit()
    return {"message": "Question pack deleted successfully"}

@router.delete("/writing/tasks/{task_id}")
async def delete_writing_task(
    task_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    from app.models.writing import WritingTask
    task = db.query(WritingTask).filter(WritingTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    return {"message": "Writing task deleted successfully"}

@router.delete("/listening/sections/{section_id}")
async def delete_listening_section(
    section_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    from app.models.listening import ListeningSection
    section = db.query(ListeningSection).filter(ListeningSection.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    
    db.delete(section)
    db.commit()
    return {"message": "Listening section deleted successfully"}

@router.delete("/listening/question-packs/{pack_id}")
async def delete_listening_question_pack(
    pack_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    from app.models.listening import ListeningQuestionPack
    pack = db.query(ListeningQuestionPack).filter(ListeningQuestionPack.id == pack_id).first()
    if not pack:
        raise HTTPException(status_code=404, detail="Question pack not found")
    
    db.delete(pack)
    db.commit()
    return {"message": "Question pack deleted successfully"}