import json
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models.writing import WritingTest, WritingTask, WritingSubmission, WritingResponse, WritingScore


class WritingService:
    
    @staticmethod
    def create_submission(db: Session, user_id: int, test_id: int) -> WritingSubmission:
        """Create a new writing submission for user"""
        submission = WritingSubmission(
            user_id=user_id,
            test_id=test_id
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
        return submission
    
    @staticmethod
    def save_response(db: Session, submission_id: int, task_id: int, content: str) -> WritingResponse:
        """Save user's written response for a task"""
        word_count = len(content.split())
        
        response = WritingResponse(
            submission_id=submission_id,
            task_id=task_id,
            content=content,
            word_count=word_count
        )
        db.add(response)
        db.commit()
        db.refresh(response)
        return response
    
    @staticmethod
    def get_tasks_by_test(db: Session, test_id: int) -> List[WritingTask]:
        """Get all writing tasks for a test"""
        return db.query(WritingTask).filter(
            WritingTask.test_id == test_id
        ).order_by(WritingTask.order).all()
    
    @staticmethod
    def analyze_writing_with_ai(response: WritingResponse, task: WritingTask, ai_client) -> Dict:
        """Send writing response to AI for analysis"""
        prompt = WRITING_ANALYSIS_PROMPT.format(
            task_type=task.task_type,
            task_prompt=task.prompt,
            min_words=task.min_words,
            user_response=response.content,
            word_count=response.word_count
        )
        
        # This would call your AI service
        ai_response = ai_client.analyze_writing(prompt)
        
        return ai_response
    
    @staticmethod
    def calculate_score(db: Session, submission_id: int, ai_analysis: Dict) -> WritingScore:
        """Calculate IELTS writing score from AI analysis"""
        score = WritingScore(
            submission_id=submission_id,
            task_achievement=ai_analysis.get('task_achievement', 6.0),
            coherence_cohesion=ai_analysis.get('coherence_cohesion', 6.0),
            lexical_resource=ai_analysis.get('lexical_resource', 6.0),
            grammatical_range=ai_analysis.get('grammatical_range', 6.0),
            feedback=ai_analysis.get('overall_feedback', ''),
            detailed_feedback=json.dumps(ai_analysis.get('detailed_feedback', {}))
        )
        
        # Calculate overall score (average of 4 criteria)
        total = (score.task_achievement + score.coherence_cohesion + 
                score.lexical_resource + score.grammatical_range)
        score.overall_score = round(total / 4 * 2) / 2  # Round to nearest 0.5
        
        db.add(score)
        db.commit()
        db.refresh(score)
        return score
    
    @staticmethod
    def get_submission_with_responses(db: Session, submission_id: int) -> Optional[WritingSubmission]:
        """Get submission with all responses"""
        return db.query(WritingSubmission).filter(
            WritingSubmission.id == submission_id
        ).first()
    
    @staticmethod
    def complete_submission(db: Session, submission_id: int) -> None:
        """Mark submission as completed"""
        submission = db.query(WritingSubmission).filter(
            WritingSubmission.id == submission_id
        ).first()
        
        if submission:
            submission.is_completed = True
            from datetime import datetime
            submission.submitted_at = datetime.utcnow()
            db.commit()


# =============================================================================
# AI PROMPTS FOR WRITING ANALYSIS
# =============================================================================

WRITING_ANALYSIS_PROMPT = """
You are an IELTS Writing examiner. Analyze this writing response according to IELTS criteria.

TASK TYPE: {task_type}
TASK PROMPT: {task_prompt}
MINIMUM WORDS: {min_words}
USER'S RESPONSE: {user_response}
WORD COUNT: {word_count}

Provide detailed analysis in this JSON format:
{{
    "task_achievement": 6.5,
    "coherence_cohesion": 6.0,
    "lexical_resource": 7.0,
    "grammatical_range": 6.5,
    "overall_feedback": "Good response with clear structure but needs better task focus",
    "detailed_feedback": {{
        "strengths": [
            "Clear introduction and conclusion",
            "Good use of linking words",
            "Relevant examples provided"
        ],
        "improvements": [
            "Address all parts of the task more fully",
            "Improve paragraph cohesion",
            "Use more varied vocabulary"
        ],
        "corrections": [
            {{
                "type": "grammar",
                "original": "There is many reasons",
                "corrected": "There are many reasons",
                "explanation": "Use 'are' with plural noun",
                "position": 145
            }},
            {{
                "type": "vocabulary",
                "original": "very important",
                "suggested": "crucial",
                "explanation": "More precise and academic",
                "position": 67
            }},
            {{
                "type": "coherence",
                "issue": "Unclear pronoun reference in paragraph 2",
                "suggestion": "Specify what 'this' refers to",
                "position": 234
            }}
        ],
        "task_specific": {{
            "task_coverage": "Partially addresses the task",
            "position_clarity": "Position is clear but could be stronger",
            "supporting_ideas": "Some relevant ideas but need development",
            "word_count_assessment": "Meets minimum requirement"
        }}
    }}
}}

SCORING CRITERIA:
- Task Achievement/Response (1-9): How well does it answer the question?
- Coherence and Cohesion (1-9): Is it well-organized and connected?
- Lexical Resource (1-9): Vocabulary range and accuracy?
- Grammatical Range and Accuracy (1-9): Grammar variety and correctness?

Focus on:
1. Whether all parts of the task are addressed
2. Clear position and well-supported arguments (Task 2)
3. Accurate data description (Task 1)
4. Logical organization and linking
5. Vocabulary appropriateness and range
6. Grammar accuracy and complexity
7. Specific corrections with explanations
"""

TASK1_ACADEMIC_PROMPT = """
Analyze this IELTS Academic Writing Task 1 response:

TASK: {task_prompt}
RESPONSE: {user_response}
WORD COUNT: {word_count}

Focus on:
- Overview statement (key trends/main features)
- Accurate data description
- Appropriate selection of key information
- Clear comparison and contrast
- Formal tone and language
- No personal opinion (objective description only)

Provide band scores and specific feedback for Task 1 Academic requirements.
"""

TASK1_GENERAL_PROMPT = """
Analyze this IELTS General Training Writing Task 1 response:

TASK: {task_prompt} 
RESPONSE: {user_response}
WORD COUNT: {word_count}

Focus on:
- Appropriate tone (formal/informal/semi-formal)
- Clear purpose achievement
- All bullet points addressed
- Proper letter format
- Appropriate opening and closing
- Consistent tone throughout

Provide band scores and specific feedback for Task 1 General Training requirements.
"""

TASK2_PROMPT = """
Analyze this IELTS Writing Task 2 essay response:

TASK: {task_prompt}
RESPONSE: {user_response} 
WORD COUNT: {word_count}

Focus on:
- Clear position/opinion stated
- All parts of question addressed
- Well-developed arguments with examples
- Logical progression of ideas
- Strong introduction and conclusion
- Academic tone and style
- Balanced discussion (if required)

Provide band scores and specific feedback for Task 2 essay requirements.
"""