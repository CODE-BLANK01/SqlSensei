from django.db import models
from django.conf import settings
from users.models import User
from assignments.models import Assignment

class Question(models.Model):
    QUESTION_ACCESS_TYPES = [
        ('Public', 'Public'),
        ('Private', 'Private'),
    ]

    question_id = models.AutoField(primary_key=True)
    question_title = models.CharField(max_length=255, null=False)
    topic = models.CharField(max_length=255, blank=True, null=True)
    difficulty_level = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    access_type = models.CharField(
        max_length=50, choices=QUESTION_ACCESS_TYPES, default='Public'
    )
    schema_sql = models.TextField(blank=True, null=True, help_text="SQL to create the sample tables")
    sample_data_sql = models.TextField(blank=True, null=True, help_text="SQL to insert sample data")
    expected_output = models.TextField(blank=True, null=True, help_text="Description or representation of expected output")
    
    def __str__(self):
        return self.question_title

    class Meta:
        db_table = 'Questions'

class AssignmentQuestion(models.Model):
    assignment_q_id = models.AutoField(primary_key=True)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    class Meta:
        db_table = "Assignment_Questions"  # Ensure it matches your given table name
        unique_together = ('assignment', 'question')

class QuestionAttempt(models.Model):
    attempt_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    attempt_date = models.DateTimeField(auto_now_add=True)
    attempt_number = models.IntegerField(default=1)  
    student_query = models.TextField()
    feedback = models.TextField(blank=True, null=True)
    attempt_success = models.BooleanField(default=False)
    execution_time = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Attempt {self.attempt_number} by {self.student} on {self.question}"

    class Meta:
        db_table = "Questions_Attempts"