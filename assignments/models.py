from django.db import models
from django.conf import settings
from courses.models import Course
from questions.models import Question


class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    deadline = models.DateField()
    release_date = models.DateField()
    questions = models.ManyToManyField(Question)

    def __str__(self):
        return f"{self.title} - {self.course.title}"


class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    submission_date = models.DateField()
    submission_status = models.CharField(max_length=50)
    review_status = models.CharField(max_length=50)
    score = models.FloatField()

    def __str__(self):
        return f"Submission by {self.student} for {self.assignment.title}"
