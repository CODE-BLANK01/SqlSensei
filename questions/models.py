from django.db import models
from django.conf import settings

class Question(models.Model):
    ACCESS_CHOICES = [
        ('public', 'Public'),
        ('course', 'Course Only'),
        ('private', 'Private'),
    ]

    title = models.CharField(max_length=255)
    topic = models.CharField(max_length=100)
    difficulty_level = models.CharField(max_length=50)
    description = models.TextField()
    access_type = models.CharField(max_length=20, choices=ACCESS_CHOICES)
    created_date = models.DateField(auto_now_add=True)
    creator = models.ForeignKey('users.User', on_delete=models.CASCADE)