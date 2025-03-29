from django.db import models
from users.models import User
from courses.models import Course

class Assignment(models.Model):
    assignment_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    assignment_title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    deadline = models.DateTimeField()
    release_date = models.DateTimeField(auto_now_add=True)
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.assignment_title

    class Meta:
        db_table = 'Assignments'


class AssignmentSubmission(models.Model):  # ✅ THIS IS WHAT YOU NEED
    submission_id = models.AutoField(primary_key=True)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    submission_date = models.DateTimeField(auto_now_add=True)
    submission_status = models.CharField(max_length=50)
    review_status = models.CharField(max_length=50, blank=True, null=True)
    score = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.student} - {self.assignment}"

    class Meta:
        db_table = 'AssignmentSubmissions'
