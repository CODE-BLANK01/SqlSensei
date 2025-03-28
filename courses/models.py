from django.db import models
from django.conf import settings


class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    enrollment_status = models.CharField(max_length=50)
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    enrollment_date = models.DateField(auto_now_add=True)
    approval_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.student} - {self.course}"


class CourseCertificate(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    completion_id = models.CharField(max_length=100)
    issued_date = models.DateField()
    certificate_link = models.URLField()

    def __str__(self):
        return f"Certificate for {self.student} - {self.course}"


class CourseStatistics(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    total_enrolled_students = models.IntegerField()
    total_completed_assignments = models.IntegerField()
    average_grade = models.FloatField()
    average_time_to_complete = models.FloatField()

    def __str__(self):
        return f"Stats for {self.course}"
