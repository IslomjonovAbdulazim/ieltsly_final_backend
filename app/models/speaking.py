from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal, ROUND_HALF_UP
import random
import json


class SpeakingTest(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.IntegerField(help_text="Duration in minutes")
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced')
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class SpeakingTopic(models.Model):
    PART_CHOICES = [
        ('part1', 'Part 1 - Introduction'),
        ('part2', 'Part 2 - Individual Long Turn'),
        ('part3', 'Part 3 - Two-way Discussion')
    ]
    
    test = models.ForeignKey(SpeakingTest, on_delete=models.CASCADE, related_name='topics')
    part_type = models.CharField(max_length=10, choices=PART_CHOICES)
    topic_name = models.CharField(max_length=200, help_text="e.g., 'Work', 'Hobbies', 'Travel'")
    instructions = models.TextField(blank=True)
    preparation_time = models.IntegerField(default=0, help_text="Preparation time in seconds (mainly for Part 2)")
    target_speaking_time = models.IntegerField(help_text="Target speaking time in seconds")
    min_speaking_time = models.IntegerField(help_text="Minimum time before follow-up questions")
    
    # Follow-up rules
    max_followups = models.IntegerField(default=1, help_text="Max follow-up questions (Part 1&3: 1, Part 2: 2)")
    
    def __str__(self):
        return f"{self.get_part_type_display()} - {self.topic_name}"

    class Meta:
        ordering = ['part_type', 'topic_name']


class SpeakingQuestion(models.Model):
    topic = models.ForeignKey(SpeakingTopic, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    difficulty_weight = models.IntegerField(default=1, help_text="Weight for question selection algorithm")
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.question_text[:50]}..."

    class Meta:
        ordering = ['difficulty_weight']


class SpeakingSession(models.Model):
    STATUS_CHOICES = [
        ('started', 'Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(SpeakingTest, on_delete=models.CASCADE)
    current_topic = models.ForeignKey(SpeakingTopic, on_delete=models.SET_NULL, null=True, blank=True)
    current_question = models.ForeignKey(SpeakingQuestion, on_delete=models.SET_NULL, null=True, blank=True, help_text="Current question for resume functionality")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='started')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def get_next_question(self, topic):
        """Algorithm to select next question for a topic"""
        questions = topic.questions.filter(is_active=True)
        if not questions:
            return None
            
        # Use weighted random selection based on difficulty_weight
        weights = [q.difficulty_weight for q in questions]
        selected = random.choices(list(questions), weights=weights, k=1)[0]
        return selected

    def __str__(self):
        return f"{self.user.username} - {self.test.title} ({self.status})"

    class Meta:
        ordering = ['-started_at']


class SpeakingResponse(models.Model):
    session = models.ForeignKey(SpeakingSession, on_delete=models.CASCADE, related_name='responses')
    topic = models.ForeignKey(SpeakingTopic, on_delete=models.CASCADE)
    question = models.ForeignKey(SpeakingQuestion, on_delete=models.CASCADE, null=True, blank=True)
    question_text = models.TextField(help_text="Actual question asked (from AI or predefined)")
    audio_file_path = models.CharField(max_length=500, help_text="Path to audio file in storage")
    audio_filename = models.CharField(max_length=255, help_text="Original filename for reference")
    file_size_bytes = models.BigIntegerField(null=True, blank=True, help_text="Audio file size in bytes")
    duration_seconds = models.IntegerField(help_text="Actual speaking duration in seconds")
    
    # AI analysis fields
    transcript = models.TextField(blank=True, help_text="AI-generated transcript of the audio")
    feedback = models.TextField(blank=True, help_text="AI feedback for this specific response")
    analysis = models.JSONField(blank=True, null=True, help_text="Detailed AI analysis (grammar, pronunciation, fluency, etc.)")
    
    # AI follow-up decision fields
    ai_followup_needed = models.BooleanField(default=False, help_text="AI decision: needs follow-up")
    ai_followup_question = models.TextField(blank=True, help_text="AI-generated follow-up question")
    followup_count = models.IntegerField(default=0)
    is_followup_response = models.BooleanField(default=False, help_text="This response is to a follow-up question")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def can_have_followup(self):
        """Check if this response can have a follow-up (respects max limits)"""
        return self.followup_count < self.topic.max_followups
    
    def set_specific_analysis(self, specific_corrections):
        """
        Set detailed word/phrase specific analysis
        specific_corrections should be a list of correction objects
        """
        self.analysis = {
            "corrections": specific_corrections,
            "word_count": len(self.transcript.split()) if self.transcript else 0,
            "speaking_rate": len(self.transcript.split()) / (self.duration_seconds / 60) if self.duration_seconds > 0 and self.transcript else 0
        }
    
    def add_grammar_correction(self, user_said, correct_form, explanation, position_start, position_end):
        """Add a specific grammar correction"""
        if not self.analysis:
            self.analysis = {"corrections": []}
        if "corrections" not in self.analysis:
            self.analysis["corrections"] = []
            
        correction = {
            "type": "grammar",
            "user_said": user_said,
            "correct_form": correct_form,
            "explanation": explanation,
            "position_start": position_start,
            "position_end": position_end
        }
        self.analysis["corrections"].append(correction)
    
    def add_vocabulary_suggestion(self, user_word, better_word, explanation, position_start, position_end):
        """Add a vocabulary improvement suggestion"""
        if not self.analysis:
            self.analysis = {"corrections": []}
        if "corrections" not in self.analysis:
            self.analysis["corrections"] = []
            
        correction = {
            "type": "vocabulary",
            "user_said": user_word,
            "suggested_word": better_word,
            "explanation": explanation,
            "position_start": position_start,
            "position_end": position_end
        }
        self.analysis["corrections"].append(correction)
    
    def add_pronunciation_correction(self, user_said, correct_pronunciation, phonetic_correct, explanation, position_start, position_end):
        """Add a pronunciation correction"""
        if not self.analysis:
            self.analysis = {"corrections": []}
        if "corrections" not in self.analysis:
            self.analysis["corrections"] = []
            
        correction = {
            "type": "pronunciation",
            "user_said": user_said,
            "correct_pronunciation": correct_pronunciation,
            "phonetic_correct": phonetic_correct,
            "explanation": explanation,
            "position_start": position_start,
            "position_end": position_end
        }
        self.analysis["corrections"].append(correction)
    
    def get_corrections_by_type(self, correction_type):
        """Get corrections by type (grammar, vocabulary, pronunciation)"""
        if not self.analysis or 'corrections' not in self.analysis:
            return []
        return [c for c in self.analysis['corrections'] if c.get('type') == correction_type]
    
    def get_grammar_corrections(self):
        """Get all grammar corrections"""
        return self.get_corrections_by_type('grammar')
    
    def get_vocabulary_suggestions(self):
        """Get all vocabulary suggestions"""
        return self.get_corrections_by_type('vocabulary')
    
    def get_pronunciation_corrections(self):
        """Get all pronunciation corrections"""
        return self.get_corrections_by_type('pronunciation')
    
    def get_full_audio_path(self, base_storage_path="/storage/audio"):
        """Get full path to audio file"""
        return f"{base_storage_path}/{self.audio_file_path}"
    
    def get_audio_url(self, base_url="https://yourdomain.com/api/audio"):
        """Get URL to access audio file via FastAPI"""
        return f"{base_url}/{self.audio_file_path}"
    
    @staticmethod
    def generate_audio_path(session_id, response_count, file_extension="wav"):
        """Generate standardized audio file path"""
        return f"speaking/session_{session_id}/response_{response_count}.{file_extension}"
    
    def __str__(self):
        return f"Response to: {self.question_text[:30]}... ({self.duration_seconds}s)"

    class Meta:
        ordering = ['created_at']


class SpeakingScore(models.Model):
    session = models.OneToOneField(SpeakingSession, on_delete=models.CASCADE)
    fluency_coherence = models.DecimalField(max_digits=3, decimal_places=1)
    lexical_resource = models.DecimalField(max_digits=3, decimal_places=1)
    grammatical_range = models.DecimalField(max_digits=3, decimal_places=1)
    pronunciation = models.DecimalField(max_digits=3, decimal_places=1)
    overall_score = models.DecimalField(max_digits=3, decimal_places=1)
    feedback = models.TextField(blank=True)
    scored_at = models.DateTimeField(auto_now_add=True)
    scored_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def calculate_overall(self):
        """Calculate overall IELTS band score with proper Decimal rounding"""
        avg = (self.fluency_coherence + self.lexical_resource +
               self.grammatical_range + self.pronunciation) / Decimal('4')
        # Round to nearest 0.5 using Decimal (IELTS rule)
        return (avg * 2).quantize(Decimal('1'), rounding=ROUND_HALF_UP) / 2

    def save(self, *args, **kwargs):
        """Auto-calculate overall score before saving"""
        # Guard against null values
        if None not in [self.fluency_coherence, self.lexical_resource,
                        self.grammatical_range, self.pronunciation]:
            self.overall_score = self.calculate_overall()
        super().save(*args, **kwargs)

    @property
    def band_descriptor(self):
        """Get IELTS band descriptor for overall score"""
        if not self.overall_score:
            return "Not scored"

        descriptors = {
            Decimal('9.0'): "Expert user",
            Decimal('8.5'): "Very good user",
            Decimal('8.0'): "Very good user",
            Decimal('7.5'): "Good user",
            Decimal('7.0'): "Good user",
            Decimal('6.5'): "Competent user",
            Decimal('6.0'): "Competent user",
            Decimal('5.5'): "Modest user",
            Decimal('5.0'): "Modest user",
            Decimal('4.5'): "Limited user",
            Decimal('4.0'): "Limited user",
            Decimal('3.5'): "Extremely limited user",
            Decimal('3.0'): "Extremely limited user",
            Decimal('2.5'): "Intermittent user",
            Decimal('2.0'): "Intermittent user",
            Decimal('1.5'): "Non-user",
            Decimal('1.0'): "Non-user"
        }

        # Find the closest band score
        score = Decimal(str(self.overall_score))
        return descriptors.get(score, "Invalid score")

    def __str__(self):
        return f"Score: {self.overall_score} - {self.session}"