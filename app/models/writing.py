from django.db import models
from django.contrib.auth.models import User


class WritingTest(models.Model):
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


class WritingTask(models.Model):
    TASK_TYPES = [
        ('task1_academic', 'Task 1 - Academic (Graph/Chart/Diagram)'),
        ('task1_general', 'Task 1 - General Training (Letter)'),
        ('task2', 'Task 2 - Essay')
    ]

    test = models.ForeignKey(WritingTest, on_delete=models.CASCADE, related_name='tasks')
    task_type = models.CharField(max_length=20, choices=TASK_TYPES)
    title = models.CharField(max_length=200)
    prompt = models.TextField()
    instructions = models.TextField()
    image = models.ImageField(upload_to='writing_tasks/', null=True, blank=True)
    min_words = models.PositiveIntegerField()
    max_words = models.PositiveIntegerField(null=True, blank=True)
    suggested_time = models.PositiveIntegerField(help_text="Suggested time in minutes")
    order = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.title} - {self.get_task_type_display()}"

    class Meta:
        ordering = ['order']


class WritingSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(WritingTest, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    time_spent = models.DurationField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.test.title}"

    class Meta:
        ordering = ['-started_at']


class WritingResponse(models.Model):
    submission = models.ForeignKey(WritingSubmission, on_delete=models.CASCADE, related_name='responses')
    task = models.ForeignKey(WritingTask, on_delete=models.CASCADE)
    content = models.TextField()
    word_count = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.word_count:
            self.word_count = len(self.content.split())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Response to {self.task.title}"

    class Meta:
        unique_together = ['submission', 'task']


class WritingScore(models.Model):
    submission = models.OneToOneField(WritingSubmission, on_delete=models.CASCADE)
    task_achievement = models.DecimalField(max_digits=3, decimal_places=1, help_text="Task 1: Task Achievement, Task 2: Task Response")
    coherence_cohesion = models.DecimalField(max_digits=3, decimal_places=1)
    lexical_resource = models.DecimalField(max_digits=3, decimal_places=1)
    grammatical_range = models.DecimalField(max_digits=3, decimal_places=1)
    overall_score = models.DecimalField(max_digits=3, decimal_places=1)
    feedback = models.TextField(blank=True)
    detailed_feedback = models.JSONField(blank=True, null=True, help_text="Detailed feedback for each criterion")
    scored_at = models.DateTimeField(auto_now_add=True)
    scored_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Score: {self.overall_score} - {self.submission}"


class WritingTaskScore(models.Model):
    score = models.ForeignKey(WritingScore, on_delete=models.CASCADE, related_name='task_scores')
    task = models.ForeignKey(WritingTask, on_delete=models.CASCADE)
    task_achievement = models.DecimalField(max_digits=3, decimal_places=1)
    coherence_cohesion = models.DecimalField(max_digits=3, decimal_places=1)
    lexical_resource = models.DecimalField(max_digits=3, decimal_places=1)
    grammatical_range = models.DecimalField(max_digits=3, decimal_places=1)
    task_score = models.DecimalField(max_digits=3, decimal_places=1)
    feedback = models.TextField(blank=True)

    def __str__(self):
        return f"Task Score: {self.task_score} - {self.task.title}"

    class Meta:
        unique_together = ['score', 'task']