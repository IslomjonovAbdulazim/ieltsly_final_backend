import json
import random
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models.speaking import SpeakingTest, SpeakingTopic, SpeakingQuestion, SpeakingSession, SpeakingResponse, SpeakingScore


class SpeakingService:
    
    @staticmethod
    def create_session(db: Session, user_id: int, test_id: int) -> SpeakingSession:
        """Create a new speaking session for user"""
        session = SpeakingSession(
            user_id=user_id,
            test_id=test_id,
            status="started"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    
    @staticmethod
    def get_next_question(db: Session, session_id: int, topic_id: int) -> Optional[SpeakingQuestion]:
        """Get next question for a topic using weighted selection"""
        topic = db.query(SpeakingTopic).filter(SpeakingTopic.id == topic_id).first()
        if not topic:
            return None
            
        questions = db.query(SpeakingQuestion).filter(
            SpeakingQuestion.topic_id == topic_id,
            SpeakingQuestion.is_active == True
        ).all()
        
        if not questions:
            return None
            
        # Weighted random selection
        weights = [q.difficulty_weight for q in questions]
        selected = random.choices(questions, weights=weights, k=1)[0]
        
        # Update session with current question
        session = db.query(SpeakingSession).filter(SpeakingSession.id == session_id).first()
        if session:
            session.current_question_id = selected.id
            session.current_topic_id = topic_id
            session.status = "in_progress"
            db.commit()
        
        return selected
    
    @staticmethod
    def save_response(db: Session, session_id: int, topic_id: int, question_id: int, 
                     question_text: str, audio_path: str, duration: int) -> SpeakingResponse:
        """Save user's audio response"""
        response = SpeakingResponse(
            session_id=session_id,
            topic_id=topic_id,
            question_id=question_id,
            question_text=question_text,
            audio_file_path=audio_path,
            duration_seconds=duration
        )
        db.add(response)
        db.commit()
        db.refresh(response)
        return response
    
    @staticmethod
    def analyze_response_with_ai(response: SpeakingResponse, ai_client) -> Dict:
        """Send response to AI for analysis and get feedback"""
        prompt = SPEAKING_ANALYSIS_PROMPT.format(
            question=response.question_text,
            duration=response.duration_seconds,
            audio_file=response.audio_file_path
        )
        
        # This would call your AI service (OpenAI, Anthropic, etc.)
        ai_response = ai_client.analyze_speaking(prompt, response.audio_file_path)
        
        return ai_response
    
    @staticmethod
    def update_response_with_analysis(db: Session, response_id: int, 
                                    transcript: str, feedback: str, analysis: Dict,
                                    followup_needed: bool = False, followup_question: str = "") -> None:
        """Update response with AI analysis results"""
        response = db.query(SpeakingResponse).filter(SpeakingResponse.id == response_id).first()
        if response:
            response.transcript = transcript
            response.feedback = feedback
            response.analysis = json.dumps(analysis)
            response.ai_followup_needed = followup_needed
            response.ai_followup_question = followup_question
            db.commit()
    
    @staticmethod
    def should_ask_followup(response: SpeakingResponse, topic: SpeakingTopic) -> bool:
        """Determine if follow-up question is needed based on topic rules"""
        if not response.ai_followup_needed:
            return False
            
        # Count existing follow-ups for this topic in the session
        followup_count = len([r for r in response.session.responses 
                            if r.topic_id == topic.id and r.ai_followup_needed])
        
        return followup_count < topic.max_followups
    
    @staticmethod
    def calculate_final_score(db: Session, session_id: int) -> SpeakingScore:
        """Calculate final IELTS speaking score from all responses"""
        session = db.query(SpeakingSession).filter(SpeakingSession.id == session_id).first()
        responses = session.responses
        
        # Aggregate scores from all responses (this would use AI analysis)
        # For now, placeholder logic
        avg_fluency = 6.5
        avg_lexical = 6.0
        avg_grammar = 6.5
        avg_pronunciation = 6.0
        
        score = SpeakingScore(
            session_id=session_id,
            fluency_coherence=avg_fluency,
            lexical_resource=avg_lexical,
            grammatical_range=avg_grammar,
            pronunciation=avg_pronunciation
        )
        
        # Auto-calculate overall score
        score.overall_score = score.calculate_overall()
        
        db.add(score)
        db.commit()
        db.refresh(score)
        return score


# =============================================================================
# AI PROMPTS FOR SPEAKING ANALYSIS
# =============================================================================

SPEAKING_ANALYSIS_PROMPT = """
You are an IELTS Speaking examiner. Analyze this speaking response and provide detailed feedback.

QUESTION: {question}
DURATION: {duration} seconds
AUDIO FILE: {audio_file}

Please provide analysis in this JSON format:
{{
    "transcript": "exact words spoken by candidate",
    "corrections": [
        {{
            "type": "grammar",
            "user_said": "I are going",
            "correct_form": "I am going",
            "explanation": "Use 'am' with 'I'",
            "position_start": 0,
            "position_end": 10
        }},
        {{
            "type": "vocabulary",
            "user_said": "good",
            "suggested_word": "excellent",
            "explanation": "More precise word choice",
            "position_start": 25,
            "position_end": 29
        }},
        {{
            "type": "pronunciation",
            "user_said": "sink",
            "correct_pronunciation": "think",
            "phonetic_correct": "/θɪŋk/",
            "explanation": "Use 'th' sound, not 's'",
            "position_start": 15,
            "position_end": 19
        }}
    ],
    "scores": {{
        "fluency_coherence": 6.5,
        "lexical_resource": 6.0,
        "grammatical_range": 6.5,
        "pronunciation": 6.0
    }},
    "followup_needed": true,
    "followup_question": "Can you tell me more about that?",
    "overall_feedback": "Good response but work on grammar accuracy"
}}

Focus on:
1. Grammar errors with specific corrections
2. Vocabulary improvements with better alternatives
3. Pronunciation issues with phonetic guidance
4. Whether follow-up is needed based on response quality
5. IELTS band scores (1-9) for each criterion
"""

SPEAKING_FOLLOWUP_PROMPT = """
Based on the user's previous response, generate an appropriate follow-up question.

PREVIOUS QUESTION: {previous_question}
USER'S RESPONSE: {user_response}
PART TYPE: {part_type} (part1, part2, part3)

Generate a natural follow-up question that:
- Explores the topic deeper
- Is appropriate for the IELTS part
- Encourages extended response
- Feels conversational

Return just the follow-up question text.
"""