from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
import random
from .base import Base


class SpeakingTest(Base):
    __tablename__ = "speaking_tests"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    difficulty = Column(String(50), default="Intermediate")  # Easy, Intermediate, Hard
    duration = Column(Integer)  # Duration in minutes
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    topics = relationship("SpeakingTopic", back_populates="test")

    def __str__(self):
        return self.title


class SpeakingTopic(Base):
    __tablename__ = "speaking_topics"
    
    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey("speaking_tests.id"))
    part_type = Column(String(10))  # part1, part2, part3
    topic_name = Column(String(200))  # Work, Hobbies, Travel
    target_speaking_time = Column(Integer)  # Target time in seconds
    min_speaking_time = Column(Integer)  # Min time before follow-up
    max_followups = Column(Integer, default=1)  # Part 1&3: 1, Part 2: 2
    
    # Relationships
    test = relationship("SpeakingTest", back_populates="topics")
    questions = relationship("SpeakingQuestion", back_populates="topic")

    def __str__(self):
        return f"{self.part_type} - {self.topic_name}"


class SpeakingQuestion(Base):
    __tablename__ = "speaking_questions"
    
    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey("speaking_topics.id"))
    question_text = Column(Text, nullable=False)
    difficulty_weight = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    topic = relationship("SpeakingTopic", back_populates="questions")

    def __str__(self):
        return f"{self.question_text[:50]}..."


class SpeakingSession(Base):
    __tablename__ = "speaking_sessions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    test_id = Column(Integer, ForeignKey("speaking_tests.id"))
    current_topic_id = Column(Integer, ForeignKey("speaking_topics.id"), nullable=True)
    current_question_id = Column(Integer, ForeignKey("speaking_questions.id"), nullable=True)
    status = Column(String(20), default="started")  # started, in_progress, completed
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    responses = relationship("SpeakingResponse", back_populates="session")

    def get_next_question(self, topic):
        """Select next question using weighted random"""
        questions = [q for q in topic.questions if q.is_active]
        if not questions:
            return None
        weights = [q.difficulty_weight for q in questions]
        return random.choices(questions, weights=weights, k=1)[0]

    def __str__(self):
        return f"Session {self.id} - {self.status}"


class SpeakingResponse(Base):
    __tablename__ = "speaking_responses"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("speaking_sessions.id"))
    topic_id = Column(Integer, ForeignKey("speaking_topics.id"))
    question_id = Column(Integer, ForeignKey("speaking_questions.id"), nullable=True)
    question_text = Column(Text)  # Actual question (predefined or AI-generated)
    
    # Audio storage
    audio_file_path = Column(String(500))  # Path to audio file
    duration_seconds = Column(Integer)
    
    # AI analysis
    transcript = Column(Text)
    feedback = Column(Text)
    analysis = Column(Text)  # JSON string for corrections
    
    # Follow-up logic
    ai_followup_needed = Column(Boolean, default=False)
    ai_followup_question = Column(Text)
    is_followup_response = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("SpeakingSession", back_populates="responses")

    def can_have_followup(self, max_followups):
        """Check if can have follow-up based on topic rules"""
        followup_count = len([r for r in self.session.responses 
                            if r.topic_id == self.topic_id and r.ai_followup_needed])
        return followup_count < max_followups

    @staticmethod
    def generate_audio_path(session_id, response_count, extension="wav"):
        """Generate audio file path"""
        return f"speaking/session_{session_id}/response_{response_count}.{extension}"

    def __str__(self):
        return f"Response: {self.question_text[:30]}... ({self.duration_seconds}s)"


class SpeakingScore(Base):
    __tablename__ = "speaking_scores"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("speaking_sessions.id"))
    fluency_coherence = Column(Numeric(3, 1))
    lexical_resource = Column(Numeric(3, 1))
    grammatical_range = Column(Numeric(3, 1))
    pronunciation = Column(Numeric(3, 1))
    overall_score = Column(Numeric(3, 1))
    feedback = Column(Text)
    scored_at = Column(DateTime, default=datetime.utcnow)

    def calculate_overall(self):
        """Calculate IELTS overall score with proper rounding"""
        if None in [self.fluency_coherence, self.lexical_resource, 
                   self.grammatical_range, self.pronunciation]:
            return None
            
        avg = (self.fluency_coherence + self.lexical_resource + 
               self.grammatical_range + self.pronunciation) / Decimal('4')
        return (avg * 2).quantize(Decimal('1'), rounding=ROUND_HALF_UP) / 2

    @property
    def band_descriptor(self):
        """Get IELTS band description"""
        if not self.overall_score:
            return "Not scored"
        
        score = float(self.overall_score)
        if score >= 8.5: return "Very good user"
        elif score >= 7.5: return "Good user"
        elif score >= 6.5: return "Competent user"
        elif score >= 5.5: return "Modest user"
        elif score >= 4.5: return "Limited user"
        elif score >= 3.5: return "Extremely limited user"
        else: return "Non-user"

    def __str__(self):
        return f"Score: {self.overall_score}"


# =============================================================================
# ANALYSIS STORAGE STRUCTURE
# =============================================================================
"""
The 'analysis' field in SpeakingResponse stores JSON string with this structure:

{
  "corrections": [
    {
      "type": "grammar",
      "user_said": "I are enjoying",
      "correct_form": "I am enjoying", 
      "explanation": "Use 'am' with 'I', not 'are'",
      "position_start": 25,
      "position_end": 38
    },
    {
      "type": "vocabulary",
      "user_said": "good",
      "suggested_word": "rewarding",
      "explanation": "More specific word for work satisfaction",
      "position_start": 65,
      "position_end": 69
    },
    {
      "type": "pronunciation", 
      "user_said": "office",
      "correct_pronunciation": "/ˈɔːfɪs/",
      "explanation": "You said 'ofis' - remember the 'f' sound",
      "position_start": 15,
      "position_end": 21
    }
  ],
  "word_count": 12,
  "speaking_rate": 145,
  "overall_quality": "good"
}

Usage:
import json
analysis_data = json.loads(response.analysis)
corrections = analysis_data["corrections"]
grammar_errors = [c for c in corrections if c["type"] == "grammar"]
"""