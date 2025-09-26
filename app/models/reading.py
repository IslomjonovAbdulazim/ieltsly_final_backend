from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class ReadingTest(Base):
    __tablename__ = "reading_tests"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    difficulty = Column(String(50), default="Intermediate")  # Easy, Intermediate, Hard
    duration = Column(Integer, default=60)  # Duration in minutes
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    passages = relationship("ReadingPassage", back_populates="test")

    def __str__(self):
        return self.title


class ReadingPassage(Base):
    __tablename__ = "reading_passages"
    
    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey("reading_tests.id"))
    title = Column(String(200), nullable=False)
    content_markdown = Column(Text, nullable=False)  # Passage in markdown
    order = Column(Integer)
    
    # Relationships
    test = relationship("ReadingTest", back_populates="passages")
    question_packs = relationship("ReadingQuestionPack", back_populates="passage")

    def __str__(self):
        return f"Passage {self.order}: {self.title}"


class ReadingQuestionPack(Base):
    __tablename__ = "reading_question_packs"
    
    id = Column(Integer, primary_key=True)
    passage_id = Column(Integer, ForeignKey("reading_passages.id"))
    title = Column(String(200))  # "Questions 1-5", "Questions 6-10"
    question_start = Column(Integer)  # Starting question number
    question_end = Column(Integer)    # Ending question number
    questions_markdown = Column(Text)  # All questions in markdown
    correct_answers = Column(Text)     # JSON string: {"1": ["London"], "2": ["Paris", "France"]}
    order_matters = Column(Boolean, default=True)  # Strict vs flexible order
    order = Column(Integer)
    
    # Relationships
    passage = relationship("ReadingPassage", back_populates="question_packs")

    def __str__(self):
        return f"{self.title} - {self.passage.title}"


class ReadingSubmission(Base):
    __tablename__ = "reading_submissions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    test_id = Column(Integer, ForeignKey("reading_tests.id"))
    started_at = Column(DateTime, default=datetime.utcnow)
    submitted_at = Column(DateTime, nullable=True)
    is_completed = Column(Boolean, default=False)
    
    # Relationships
    answers = relationship("ReadingAnswer", back_populates="submission")

    def __str__(self):
        return f"Submission {self.id} - User {self.user_id}"


class ReadingAnswer(Base):
    __tablename__ = "reading_answers"
    
    id = Column(Integer, primary_key=True)
    submission_id = Column(Integer, ForeignKey("reading_submissions.id"))
    question_number = Column(Integer)
    user_answers = Column(Text)  # JSON string: ["London"] or ["Paris", "France"]
    is_correct = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    submission = relationship("ReadingSubmission", back_populates="answers")

    def __str__(self):
        return f"Answer to Q{self.question_number}"


class ReadingScore(Base):
    __tablename__ = "reading_scores"
    
    id = Column(Integer, primary_key=True)
    submission_id = Column(Integer, ForeignKey("reading_submissions.id"))
    correct_answers = Column(Integer)
    total_questions = Column(Integer)
    band_score = Column(Numeric(3, 1))
    percentage = Column(Numeric(5, 2))
    calculated_at = Column(DateTime, default=datetime.utcnow)

    def __str__(self):
        return f"Score: {self.band_score}"


# =============================================================================
# ANSWER STORAGE STRUCTURE
# =============================================================================
"""
Reading answers are stored as JSON strings in user_answers field:

Single answer: '["London"]'
Multiple answers: '["Paris", "France"]'
Alternative spellings handled in correct_answers: '["Color", "Colour"]'

Question pack correct_answers structure:
{
  "1": ["London"],
  "2": ["Paris", "France"], 
  "3": ["TRUE"],
  "4": ["Color", "Colour"]
}

Usage:
import json
user_ans = json.loads(answer.user_answers)
correct_ans = json.loads(question_pack.correct_answers)
"""