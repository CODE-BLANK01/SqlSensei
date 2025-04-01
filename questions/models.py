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