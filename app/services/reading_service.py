import json
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models.reading import ReadingTest, ReadingPassage, ReadingQuestionPack, ReadingSubmission, ReadingAnswer, ReadingScore


class ReadingService:
    
    @staticmethod
    def create_submission(db: Session, user_id: int, test_id: int) -> ReadingSubmission:
        """Create a new reading submission for user"""
        submission = ReadingSubmission(
            user_id=user_id,
            test_id=test_id
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
        return submission
    
    @staticmethod
    def get_test_with_passages(db: Session, test_id: int) -> Optional[ReadingTest]:
        """Get reading test with all passages and question packs"""
        return db.query(ReadingTest).filter(ReadingTest.id == test_id).first()
    
    @staticmethod
    def save_answer(db: Session, submission_id: int, question_number: int, user_answers: List[str]) -> ReadingAnswer:
        """Save user's answer for a specific question"""
        answer = ReadingAnswer(
            submission_id=submission_id,
            question_number=question_number,
            user_answers=json.dumps(user_answers)
        )
        db.add(answer)
        db.commit()
        db.refresh(answer)
        return answer
    
    @staticmethod
    def check_answer_correctness(user_answers: List[str], correct_answers: List[str], order_matters: bool = True) -> bool:
        """Check if user answers match correct answers"""
        # Normalize answers (lowercase, strip whitespace)
        user_normalized = [str(ans).lower().strip() for ans in user_answers]
        correct_normalized = [str(ans).lower().strip() for ans in correct_answers]
        
        if order_matters:
            # Strict order: answers must match exactly in order
            return user_normalized == correct_normalized
        else:
            # Flexible order: answers can be in any order
            return set(user_normalized) == set(correct_normalized)
    
    @staticmethod
    def grade_submission(db: Session, submission_id: int) -> ReadingScore:
        """Grade entire reading submission"""
        submission = db.query(ReadingSubmission).filter(ReadingSubmission.id == submission_id).first()
        if not submission:
            return None
            
        test = db.query(ReadingTest).filter(ReadingTest.id == submission.test_id).first()
        answers = submission.answers
        
        correct_count = 0
        total_questions = 0
        
        # Get all question packs for the test
        for passage in test.passages:
            for question_pack in passage.question_packs:
                correct_answers_dict = json.loads(question_pack.correct_answers)
                
                # Check each question in the pack
                for q_num in range(question_pack.question_start, question_pack.question_end + 1):
                    total_questions += 1
                    
                    # Find user's answer for this question
                    user_answer = next((a for a in answers if a.question_number == q_num), None)
                    
                    if user_answer:
                        user_ans_list = json.loads(user_answer.user_answers)
                        correct_ans_list = correct_answers_dict.get(str(q_num), [])
                        
                        is_correct = ReadingService.check_answer_correctness(
                            user_ans_list, correct_ans_list, question_pack.order_matters
                        )
                        
                        # Update answer correctness
                        user_answer.is_correct = is_correct
                        if is_correct:
                            correct_count += 1
        
        # Calculate band score (IELTS Reading band scale)
        percentage = (correct_count / total_questions * 100) if total_questions > 0 else 0
        band_score = ReadingService.calculate_band_score(correct_count, total_questions)
        
        score = ReadingScore(
            submission_id=submission_id,
            correct_answers=correct_count,
            total_questions=total_questions,
            band_score=band_score,
            percentage=percentage
        )
        
        db.add(score)
        db.commit()
        db.refresh(score)
        return score
    
    @staticmethod
    def calculate_band_score(correct_answers: int, total_questions: int) -> float:
        """Calculate IELTS band score based on correct answers (Academic Reading scale)"""
        if total_questions == 0:
            return 0.0
            
        percentage = correct_answers / total_questions
        
        # IELTS Academic Reading band score conversion (approximate)
        if percentage >= 0.9:  # 36-40/40
            return 9.0
        elif percentage >= 0.825:  # 33-35/40
            return 8.5
        elif percentage >= 0.75:  # 30-32/40
            return 8.0
        elif percentage >= 0.675:  # 27-29/40
            return 7.5
        elif percentage >= 0.6:  # 24-26/40
            return 7.0
        elif percentage >= 0.525:  # 21-23/40
            return 6.5
        elif percentage >= 0.45:  # 18-20/40
            return 6.0
        elif percentage >= 0.375:  # 15-17/40
            return 5.5
        elif percentage >= 0.3:  # 12-14/40
            return 5.0
        elif percentage >= 0.225:  # 9-11/40
            return 4.5
        elif percentage >= 0.15:  # 6-8/40
            return 4.0
        elif percentage >= 0.075:  # 3-5/40
            return 3.5
        else:  # 0-2/40
            return 3.0
    
    @staticmethod
    def complete_submission(db: Session, submission_id: int) -> None:
        """Mark submission as completed"""
        submission = db.query(ReadingSubmission).filter(ReadingSubmission.id == submission_id).first()
        if submission:
            submission.is_completed = True
            from datetime import datetime
            submission.submitted_at = datetime.utcnow()
            db.commit()
    
    @staticmethod
    def get_question_pack_by_number(db: Session, test_id: int, question_number: int) -> Optional[ReadingQuestionPack]:
        """Find which question pack contains a specific question number"""
        test = db.query(ReadingTest).filter(ReadingTest.id == test_id).first()
        if not test:
            return None
            
        for passage in test.passages:
            for pack in passage.question_packs:
                if pack.question_start <= question_number <= pack.question_end:
                    return pack
        
        return None
    
    @staticmethod
    def get_user_progress(db: Session, submission_id: int) -> Dict:
        """Get user's current progress in the test"""
        submission = db.query(ReadingSubmission).filter(ReadingSubmission.id == submission_id).first()
        if not submission:
            return {}
            
        test = db.query(ReadingTest).filter(ReadingTest.id == submission.test_id).first()
        answers = submission.answers
        
        # Calculate total questions
        total_questions = 0
        for passage in test.passages:
            for pack in passage.question_packs:
                total_questions += (pack.question_end - pack.question_start + 1)
        
        answered_questions = len(answers)
        
        return {
            "total_questions": total_questions,
            "answered_questions": answered_questions,
            "progress_percentage": (answered_questions / total_questions * 100) if total_questions > 0 else 0,
            "is_completed": submission.is_completed
        }


# =============================================================================
# READING TEST UTILITIES
# =============================================================================

class ReadingTestUtils:
    
    @staticmethod
    def validate_answer_format(user_answers: List[str], question_pack: ReadingQuestionPack, question_number: int) -> bool:
        """Validate that user answers are in correct format"""
        if not user_answers:
            return False
            
        # Check if question exists in pack
        if not (question_pack.question_start <= question_number <= question_pack.question_end):
            return False
            
        # Basic validation - answers should be non-empty strings
        return all(isinstance(ans, str) and ans.strip() for ans in user_answers)
    
    @staticmethod
    def get_alternative_answers(correct_answers: List[str]) -> List[str]:
        """Get all possible alternative spellings/forms for answers"""
        alternatives = []
        for answer in correct_answers:
            alternatives.append(answer)
            # Add common variations
            alternatives.append(answer.lower())
            alternatives.append(answer.upper()) 
            alternatives.append(answer.capitalize())
        
        return list(set(alternatives))  # Remove duplicates