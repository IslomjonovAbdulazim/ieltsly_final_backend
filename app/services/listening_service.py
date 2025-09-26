import json
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models.listening import ListeningTest, ListeningSection, ListeningQuestionPack, ListeningSubmission, ListeningAnswer, ListeningScore


class ListeningService:
    
    @staticmethod
    def create_submission(db: Session, user_id: int, test_id: int) -> ListeningSubmission:
        """Create a new listening submission for user"""
        submission = ListeningSubmission(
            user_id=user_id,
            test_id=test_id
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
        return submission
    
    @staticmethod
    def get_test_with_sections(db: Session, test_id: int) -> Optional[ListeningTest]:
        """Get listening test with all sections and question packs"""
        return db.query(ListeningTest).filter(ListeningTest.id == test_id).first()
    
    @staticmethod
    def get_section_audio_path(db: Session, section_id: int) -> Optional[str]:
        """Get audio file path for a section"""
        section = db.query(ListeningSection).filter(ListeningSection.id == section_id).first()
        return section.audio_file_path if section else None
    
    @staticmethod
    def save_answer(db: Session, submission_id: int, question_number: int, user_answers: List[str]) -> ListeningAnswer:
        """Save user's answer for a specific question"""
        answer = ListeningAnswer(
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
    def grade_submission(db: Session, submission_id: int) -> ListeningScore:
        """Grade entire listening submission"""
        submission = db.query(ListeningSubmission).filter(ListeningSubmission.id == submission_id).first()
        if not submission:
            return None
            
        test = db.query(ListeningTest).filter(ListeningTest.id == submission.test_id).first()
        answers = submission.answers
        
        correct_count = 0
        total_questions = 0
        section_scores = {}
        
        # Grade by section
        for section in test.sections:
            section_correct = 0
            section_total = 0
            
            for question_pack in section.question_packs:
                correct_answers_dict = json.loads(question_pack.correct_answers)
                
                # Check each question in the pack
                for q_num in range(question_pack.question_start, question_pack.question_end + 1):
                    section_total += 1
                    total_questions += 1
                    
                    # Find user's answer for this question
                    user_answer = next((a for a in answers if a.question_number == q_num), None)
                    
                    if user_answer:
                        user_ans_list = json.loads(user_answer.user_answers)
                        correct_ans_list = correct_answers_dict.get(str(q_num), [])
                        
                        is_correct = ListeningService.check_answer_correctness(
                            user_ans_list, correct_ans_list, question_pack.order_matters
                        )
                        
                        # Update answer correctness
                        user_answer.is_correct = is_correct
                        if is_correct:
                            section_correct += 1
                            correct_count += 1
            
            # Store section score
            section_scores[section.section_type] = {
                "correct": section_correct,
                "total": section_total,
                "percentage": (section_correct / section_total * 100) if section_total > 0 else 0
            }
        
        # Calculate band score
        percentage = (correct_count / total_questions * 100) if total_questions > 0 else 0
        band_score = ListeningService.calculate_band_score(correct_count, total_questions)
        
        score = ListeningScore(
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
        """Calculate IELTS band score based on correct answers (Listening scale)"""
        if total_questions == 0:
            return 0.0
            
        percentage = correct_answers / total_questions
        
        # IELTS Listening band score conversion (for 40 questions)
        if percentage >= 0.975:  # 39-40/40
            return 9.0
        elif percentage >= 0.9:  # 36-38/40
            return 8.5
        elif percentage >= 0.825:  # 33-35/40
            return 8.0
        elif percentage >= 0.75:  # 30-32/40
            return 7.5
        elif percentage >= 0.675:  # 27-29/40
            return 7.0
        elif percentage >= 0.6:  # 24-26/40
            return 6.5
        elif percentage >= 0.525:  # 21-23/40
            return 6.0
        elif percentage >= 0.45:  # 18-20/40
            return 5.5
        elif percentage >= 0.375:  # 15-17/40
            return 5.0
        elif percentage >= 0.3:  # 12-14/40
            return 4.5
        elif percentage >= 0.225:  # 9-11/40
            return 4.0
        elif percentage >= 0.15:  # 6-8/40
            return 3.5
        else:  # 0-5/40
            return 3.0
    
    @staticmethod
    def complete_submission(db: Session, submission_id: int) -> None:
        """Mark submission as completed"""
        submission = db.query(ListeningSubmission).filter(ListeningSubmission.id == submission_id).first()
        if submission:
            submission.is_completed = True
            from datetime import datetime
            submission.submitted_at = datetime.utcnow()
            db.commit()
    
    @staticmethod
    def get_question_pack_by_number(db: Session, test_id: int, question_number: int) -> Optional[ListeningQuestionPack]:
        """Find which question pack contains a specific question number"""
        test = db.query(ListeningTest).filter(ListeningTest.id == test_id).first()
        if not test:
            return None
            
        for section in test.sections:
            for pack in section.question_packs:
                if pack.question_start <= question_number <= pack.question_end:
                    return pack
        
        return None
    
    @staticmethod
    def get_user_progress(db: Session, submission_id: int) -> Dict:
        """Get user's current progress in the test"""
        submission = db.query(ListeningSubmission).filter(ListeningSubmission.id == submission_id).first()
        if not submission:
            return {}
            
        test = db.query(ListeningTest).filter(ListeningTest.id == submission.test_id).first()
        answers = submission.answers
        
        # Calculate total questions
        total_questions = 0
        for section in test.sections:
            for pack in section.question_packs:
                total_questions += (pack.question_end - pack.question_start + 1)
        
        answered_questions = len(answers)
        
        return {
            "total_questions": total_questions,
            "answered_questions": answered_questions,
            "progress_percentage": (answered_questions / total_questions * 100) if total_questions > 0 else 0,
            "is_completed": submission.is_completed,
            "current_section": ListeningService.get_current_section(answers, test)
        }
    
    @staticmethod
    def get_current_section(answers: List[ListeningAnswer], test: ListeningTest) -> Optional[str]:
        """Determine which section user is currently on based on answered questions"""
        if not answers:
            return test.sections[0].section_type if test.sections else None
            
        # Get highest answered question number
        max_question = max(answer.question_number for answer in answers)
        
        # Find which section this question belongs to
        for section in test.sections:
            for pack in section.question_packs:
                if pack.question_start <= max_question <= pack.question_end:
                    # Check if this section is complete
                    section_questions = []
                    for p in section.question_packs:
                        section_questions.extend(range(p.question_start, p.question_end + 1))
                    
                    answered_in_section = [a.question_number for a in answers if a.question_number in section_questions]
                    
                    if len(answered_in_section) < len(section_questions):
                        return section.section_type
                    else:
                        # Section complete, move to next
                        continue
        
        return None


# =============================================================================
# LISTENING TEST UTILITIES
# =============================================================================

class ListeningTestUtils:
    
    @staticmethod
    def validate_answer_format(user_answers: List[str], question_pack: ListeningQuestionPack, question_number: int) -> bool:
        """Validate that user answers are in correct format"""
        if not user_answers:
            return False
            
        # Check if question exists in pack
        if not (question_pack.question_start <= question_number <= question_pack.question_end):
            return False
            
        # Basic validation - answers should be non-empty strings
        return all(isinstance(ans, str) and ans.strip() for ans in user_answers)
    
    @staticmethod
    def handle_common_spelling_variations(answer: str) -> List[str]:
        """Generate common spelling variations for listening answers"""
        variations = [answer]
        
        # Common variations
        answer_lower = answer.lower()
        
        # British vs American spellings
        if 'colour' in answer_lower:
            variations.append(answer.replace('colour', 'color').replace('Colour', 'Color'))
        if 'color' in answer_lower:
            variations.append(answer.replace('color', 'colour').replace('Color', 'Colour'))
        
        if 'centre' in answer_lower:
            variations.append(answer.replace('centre', 'center').replace('Centre', 'Center'))
        if 'center' in answer_lower:
            variations.append(answer.replace('center', 'centre').replace('Center', 'Centre'))
        
        # Capitalization variations
        variations.extend([answer.lower(), answer.upper(), answer.capitalize()])
        
        return list(set(variations))  # Remove duplicates
    
    @staticmethod
    def get_audio_file_info(audio_path: str) -> Dict:
        """Get information about audio file (would use actual audio processing)"""
        return {
            "path": audio_path,
            "duration": "10:30",  # Placeholder
            "format": "mp3",
            "size": "15.2 MB"
        }