from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class ListeningTest(Base):
    __tablename__ = "listening_tests"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    difficulty = Column(String(50), default="Intermediate")  # Easy, Intermediate, Hard
    duration = Column(Integer, default=30)  # Duration in minutes
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    sections = relationship("ListeningSection", back_populates="test")

    def __str__(self):
        return self.title


class ListeningSection(Base):
    __tablename__ = "listening_sections"
    
    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey("listening_tests.id"))
    section_type = Column(String(15))  # section1, section2, section3, section4
    title = Column(String(200), nullable=False)
    audio_file_path = Column(String(500))  # Path to audio file
    transcript = Column(Text)  # Optional transcript
    instructions = Column(Text)
    order = Column(Integer)
    
    # Relationships
    test = relationship("ListeningTest", back_populates="sections")
    question_packs = relationship("ListeningQuestionPack", back_populates="section")

    def __str__(self):
        return f"{self.section_type}: {self.title}"


class ListeningQuestionPack(Base):
    __tablename__ = "listening_question_packs"
    
    id = Column(Integer, primary_key=True)
    section_id = Column(Integer, ForeignKey("listening_sections.id"))
    title = Column(String(200))  # "Questions 1-5", "Questions 6-10"
    question_start = Column(Integer)  # Starting question number
    question_end = Column(Integer)    # Ending question number
    questions_markdown = Column(Text)  # All questions in markdown
    image_path = Column(String(500), nullable=True)  # Path to map/diagram image
    correct_answers = Column(Text)     # JSON string: {"1": ["London"], "2": ["Paris", "France"]}
    order_matters = Column(Boolean, default=True)  # Strict vs flexible order
    order = Column(Integer)
    
    # Relationships
    section = relationship("ListeningSection", back_populates="question_packs")

    def __str__(self):
        return f"{self.title} - {self.section.title}"


class ListeningSubmission(Base):
    __tablename__ = "listening_submissions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    test_id = Column(Integer, ForeignKey("listening_tests.id"))
    started_at = Column(DateTime, default=datetime.utcnow)
    submitted_at = Column(DateTime, nullable=True)
    is_completed = Column(Boolean, default=False)
    
    # Relationships
    answers = relationship("ListeningAnswer", back_populates="submission")

    def __str__(self):
        return f"Submission {self.id} - User {self.user_id}"


class ListeningAnswer(Base):
    __tablename__ = "listening_answers"
    
    id = Column(Integer, primary_key=True)
    submission_id = Column(Integer, ForeignKey("listening_submissions.id"))
    question_number = Column(Integer)
    user_answers = Column(Text)  # JSON string: ["London"] or ["Paris", "France"]
    is_correct = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    submission = relationship("ListeningSubmission", back_populates="answers")

    def __str__(self):
        return f"Answer to Q{self.question_number}"


class ListeningScore(Base):
    __tablename__ = "listening_scores"
    
    id = Column(Integer, primary_key=True)
    submission_id = Column(Integer, ForeignKey("listening_submissions.id"))
    correct_answers = Column(Integer)
    total_questions = Column(Integer)
    band_score = Column(Numeric(3, 1))
    percentage = Column(Numeric(5, 2))
    calculated_at = Column(DateTime, default=datetime.utcnow)

    def __str__(self):
        return f"Score: {self.band_score}"


# =============================================================================
# AUDIO & ANSWER STORAGE STRUCTURE
# =============================================================================
"""
Audio files stored as paths in audio_file_path and image_path fields:
- audio_file_path: "listening/section1/audio.mp3"
- image_path: "listening/images/map_diagram.png"

Answer storage same as reading:
user_answers: '["London"]' or '["Paris", "France"]'

Question pack correct_answers:
{
  "1": ["London"],
  "2": ["Paris", "France"], 
  "3": ["Library", "library"],
  "4": ["B"]
}

Usage:
import json
user_ans = json.loads(answer.user_answers)
correct_ans = json.loads(question_pack.correct_answers)
"""