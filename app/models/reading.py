from django.db import models
from django.contrib.auth.models import User
import json


class ReadingTest(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.IntegerField(default=60, help_text="Duration in minutes")
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


class ReadingPassage(models.Model):
    test = models.ForeignKey(ReadingTest, on_delete=models.CASCADE, related_name='passages')
    title = models.CharField(max_length=200)
    content_markdown = models.TextField(help_text="Passage content in markdown format")
    order = models.PositiveIntegerField()
    word_count = models.PositiveIntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.word_count and self.content_markdown:
            # Remove markdown formatting for word count
            import re
            plain_text = re.sub(r'[#*_`\[\]()]', '', self.content_markdown)
            self.word_count = len(plain_text.split())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Passage {self.order}: {self.title}"

    class Meta:
        ordering = ['order']


class ReadingQuestionPack(models.Model):
    passage = models.ForeignKey(ReadingPassage, on_delete=models.CASCADE, related_name='question_packs')
    title = models.CharField(max_length=200, help_text="e.g., 'Questions 1-5', 'Questions 6-10'")
    question_start = models.PositiveIntegerField(help_text="Starting question number")
    question_end = models.PositiveIntegerField(help_text="Ending question number")
    questions_markdown = models.TextField(help_text="All questions content in markdown format")
    correct_answers = models.JSONField(help_text="Object with question numbers as keys and alternative answers as values")
    order_matters = models.BooleanField(default=True, help_text="True for strict order (1. Book, 2. Lamp), False for flexible order (matching tasks)")
    order = models.PositiveIntegerField()

    def set_correct_answers_for_question(self, question_num, answers):
        """
        Helper method to set correct answers with alternatives for a specific question
        answers can be: "Color" or ["Color", "Colour"] for alternatives
        """
        if not self.correct_answers:
            self.correct_answers = {}
        
        if isinstance(answers, list):
            self.correct_answers[str(question_num)] = answers
        else:
            self.correct_answers[str(question_num)] = [answers]

    def get_correct_answers_for_question(self, question_num):
        """Helper method to get all correct answer alternatives for a specific question"""
        if not self.correct_answers:
            return []
        return self.correct_answers.get(str(question_num), [])

    def get_question_range(self):
        """Get list of question numbers in this pack"""
        return list(range(self.question_start, self.question_end + 1))

    def check_answer_correctness(self, question_num, user_answers):
        """
        Check if user answers are correct for a specific question
        Handles both alternative spellings and order sensitivity
        """
        correct_answers = self.get_correct_answers_for_question(question_num)
        if not correct_answers:
            return False

        # Normalize user answers
        if isinstance(user_answers, str):
            user_answers = [user_answers]
        
        user_normalized = [str(ans).lower().strip() for ans in user_answers]
        correct_normalized = [str(ans).lower().strip() for ans in correct_answers]

        if self.order_matters:
            # Strict order: user answers must match correct answers in exact order
            return user_normalized == correct_normalized
        else:
            # Flexible order: user answers can be in any order but must match
            return set(user_normalized) == set(correct_normalized)

    def __str__(self):
        return f"{self.title} - {self.passage.title}"

    class Meta:
        ordering = ['order']
        unique_together = ['passage', 'question_start', 'question_end']


class ReadingSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(ReadingTest, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    time_spent = models.DurationField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.test.title}"

    class Meta:
        ordering = ['-started_at']


class ReadingAnswer(models.Model):
    submission = models.ForeignKey(ReadingSubmission, on_delete=models.CASCADE, related_name='answers')
    question_number = models.PositiveIntegerField()
    user_answers = models.JSONField(help_text="Array of user's answers")
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_user_answers(self, answers_list):
        """Helper method to set user answers"""
        if isinstance(answers_list, list):
            self.user_answers = answers_list
        else:
            self.user_answers = [answers_list]

    def get_user_answers(self):
        """Helper method to get user answers as list"""
        return self.user_answers if isinstance(self.user_answers, list) else [self.user_answers]

    def check_correctness_with_pack(self, question_pack):
        """Check correctness using the question pack's logic"""
        user_answers = self.get_user_answers()
        self.is_correct = question_pack.check_answer_correctness(self.question_number, user_answers)
        return self.is_correct

    def __str__(self):
        return f"Answer to Q{self.question_number} - {self.user_answers}"

    class Meta:
        unique_together = ['submission', 'question_number']


class ReadingScore(models.Model):
    submission = models.OneToOneField(ReadingSubmission, on_delete=models.CASCADE)
    correct_answers = models.PositiveIntegerField()
    total_questions = models.PositiveIntegerField()
    band_score = models.DecimalField(max_digits=3, decimal_places=1)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    feedback = models.TextField(blank=True)
    calculated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Score: {self.band_score} - {self.submission}"
