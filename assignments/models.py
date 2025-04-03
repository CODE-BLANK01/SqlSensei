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


class AssignmentSubmission(models.Model):
    submission_id = models.AutoField(primary_key=True)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    submission_date = models.DateTimeField(auto_now_add=True)
    submitted_answer = models.FileField(upload_to='submissions/%Y/%m/%d/')
    submission_status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Submitted', 'Submitted'), ('Late', 'Late')])
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    review_status = models.CharField(max_length=50, choices=[('Graded', 'Graded'), ('Not Graded', 'Not Graded')])

    def __str__(self):
        return f"Submission by {self.student} for {self.assignment.title}"
    
    class Meta:
        db_table = 'Assignment_Submissions'
