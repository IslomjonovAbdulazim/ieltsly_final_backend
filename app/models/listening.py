from django.db import models
from django.contrib.auth.models import User
import json


class ListeningTest(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.IntegerField(default=30, help_text="Duration in minutes")
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


class ListeningSection(models.Model):
    SECTION_TYPES = [
        ('section1', 'Section 1 - Social/Survival'),
        ('section2', 'Section 2 - Social/General Interest'),
        ('section3', 'Section 3 - Educational/Training'),
        ('section4', 'Section 4 - Academic')
    ]

    test = models.ForeignKey(ListeningTest, on_delete=models.CASCADE, related_name='sections')
    section_type = models.CharField(max_length=15, choices=SECTION_TYPES)
    title = models.CharField(max_length=200)
    audio_file = models.FileField(upload_to='listening_audio/')
    transcript = models.TextField(blank=True)
    instructions = models.TextField()
    order = models.PositiveIntegerField()
    duration = models.DurationField(help_text="Audio duration")

    def __str__(self):
        return f"{self.get_section_type_display()}: {self.title}"

    class Meta:
        ordering = ['order']


class ListeningQuestionPack(models.Model):
    section = models.ForeignKey(ListeningSection, on_delete=models.CASCADE, related_name='question_packs')
    title = models.CharField(max_length=200, help_text="e.g., 'Questions 1-5', 'Questions 6-10'")
    question_start = models.PositiveIntegerField(help_text="Starting question number")
    question_end = models.PositiveIntegerField(help_text="Ending question number")
    questions_markdown = models.TextField(help_text="All questions content in markdown format")
    image = models.ImageField(upload_to='listening_question_images/', null=True, blank=True, help_text="Image for map/diagram/plan labelling questions")
    correct_answers = models.JSONField(help_text="Object with question numbers as keys and alternative answers as values")
    order_matters = models.BooleanField(default=True, help_text="True for strict order, False for flexible order (matching tasks)")
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
        return f"{self.title} - {self.section.title}"

    class Meta:
        ordering = ['order']
        unique_together = ['section', 'question_start', 'question_end']


class ListeningSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(ListeningTest, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    time_spent = models.DurationField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.test.title}"

    class Meta:
        ordering = ['-started_at']


class ListeningAnswer(models.Model):
    submission = models.ForeignKey(ListeningSubmission, on_delete=models.CASCADE, related_name='answers')
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


class ListeningScore(models.Model):
    submission = models.OneToOneField(ListeningSubmission, on_delete=models.CASCADE)
    correct_answers = models.PositiveIntegerField()
    total_questions = models.PositiveIntegerField()
    band_score = models.DecimalField(max_digits=3, decimal_places=1)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    section_scores = models.JSONField(blank=True, null=True, help_text="Scores breakdown by section")
    feedback = models.TextField(blank=True)
    calculated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Score: {self.band_score} - {self.submission}"