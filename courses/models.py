from django.db import models
from users.models import User

class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_title = models.CharField(max_length=255)
    course_description = models.TextField(blank=True, null=True)
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    course_token = models.CharField(max_length=50, unique=True)
    course_start_date = models.DateField(null=True, blank=True)
    course_end_date = models.DateField(null=True, blank=True)
    enrollment_status = models.BooleanField(default=True)

    def __str__(self):
        return self.course_title

    class Meta:
        db_table = 'Courses'

class CourseEnrollment(models.Model):

    ENROLLMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Denied', 'Denied'),
        ('Dropped', 'Dropped'),
    ]
    
    enrollment_id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column='student_id')
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, db_column='course_id')
    enrollment_date = models.DateTimeField(auto_now_add=True)
    enrollment_status = models.CharField(max_length=50, choices=ENROLLMENT_STATUS_CHOICES, default='Pending')
    approval_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('student_id', 'course_id') 
        db_table = 'Course_Enrollments'

    def __str__(self):
        return f"{self.student_id.username} -> {self.course_id.course_title} ({self.enrollment_status})"