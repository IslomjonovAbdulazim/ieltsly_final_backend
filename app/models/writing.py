from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class WritingTest(Base):
    __tablename__ = "writing_tests"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    test_type = Column(String(50), default="Academic")  # Academic or General
    difficulty = Column(String(50), default="Intermediate")  # Easy, Intermediate, Hard
    duration = Column(Integer, default=60)  # Duration in minutes
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tasks = relationship("WritingTask", back_populates="test")

    def __str__(self):
        return self.title


class WritingTask(Base):
    __tablename__ = "writing_tasks"
    
    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey("writing_tests.id"))
    task_type = Column(String(20))  # task1_academic, task1_general, task2
    title = Column(String(200), nullable=False)
    prompt = Column(Text, nullable=False)  # Task description/question
    instructions = Column(Text)
    image_path = Column(String(500), nullable=True)  # For charts/graphs in Task 1
    min_words = Column(Integer)  # Minimum word count
    suggested_time = Column(Integer)  # Suggested time in minutes
    order = Column(Integer)
    
    # Relationships
    test = relationship("WritingTest", back_populates="tasks")

    def __str__(self):
        return f"{self.task_type}: {self.title}"


class WritingSubmission(Base):
    __tablename__ = "writing_submissions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    test_id = Column(Integer, ForeignKey("writing_tests.id"))
    started_at = Column(DateTime, default=datetime.utcnow)
    submitted_at = Column(DateTime, nullable=True)
    is_completed = Column(Boolean, default=False)
    
    # Relationships
    responses = relationship("WritingResponse", back_populates="submission")

    def __str__(self):
        return f"Submission {self.id} - User {self.user_id}"


class WritingResponse(Base):
    __tablename__ = "writing_responses"
    
    id = Column(Integer, primary_key=True)
    submission_id = Column(Integer, ForeignKey("writing_submissions.id"))
    task_id = Column(Integer, ForeignKey("writing_tasks.id"))
    content = Column(Text, nullable=False)  # User's written response
    word_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    submission = relationship("WritingSubmission", back_populates="responses")

    def __str__(self):
        return f"Response to Task {self.task_id} ({self.word_count} words)"


class WritingScore(Base):
    __tablename__ = "writing_scores"
    
    id = Column(Integer, primary_key=True)
    submission_id = Column(Integer, ForeignKey("writing_submissions.id"))
    task_achievement = Column(Numeric(3, 1))  # Task 1: Task Achievement, Task 2: Task Response
    coherence_cohesion = Column(Numeric(3, 1))
    lexical_resource = Column(Numeric(3, 1))
    grammatical_range = Column(Numeric(3, 1))
    overall_score = Column(Numeric(3, 1))
    feedback = Column(Text)
    detailed_feedback = Column(Text)  # JSON string with detailed analysis
    scored_at = Column(DateTime, default=datetime.utcnow)

    def __str__(self):
        return f"Score: {self.overall_score}"


# =============================================================================
# WRITING FEEDBACK STRUCTURE
# =============================================================================
"""
Writing detailed_feedback stored as JSON string:

{
  "task_scores": {
    "task1": {
      "task_achievement": 7.0,
      "coherence_cohesion": 6.5,
      "lexical_resource": 7.0,
      "grammatical_range": 6.0,
      "feedback": "Good data description but lacks clear overview."
    },
    "task2": {
      "task_achievement": 6.5,
      "coherence_cohesion": 7.0,
      "lexical_resource": 6.0,
      "grammatical_range": 6.5,
      "feedback": "Clear argument but needs more examples."
    }
  },
  "corrections": [
    {
      "type": "grammar",
      "original": "There is many people",
      "corrected": "There are many people",
      "explanation": "Use 'are' with plural noun",
      "position": 45
    },
    {
      "type": "vocabulary",
      "original": "very good",
      "suggested": "excellent",
      "explanation": "More precise word choice",
      "position": 123
    }
  ],
  "strengths": ["Clear structure", "Good examples"],
  "improvements": ["Grammar accuracy", "Vocabulary range"]
}

Usage:
import json
feedback_data = json.loads(score.detailed_feedback)
corrections = feedback_data.get("corrections", [])
strengths = feedback_data.get("strengths", [])
"""