from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom User Model for Students & Instructors
class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('instructor', 'Instructor'),
    )
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='active')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.full_name} ({self.role})"


class InstructorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    about_me = models.TextField(blank=True, null=True)
    average_feedback = models.FloatField(default=0.0)

    def __str__(self):
        return f"Instructor Profile: {self.user.full_name}"


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    grade_level = models.CharField(max_length=20)
    last_active_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Student Profile: {self.user.full_name}"


class ParticipationStreak(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    streak_count = models.PositiveIntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.user.full_name} - {self.streak_count} days"
