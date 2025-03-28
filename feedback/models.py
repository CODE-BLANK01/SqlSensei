from django.db import models
from django.conf import settings
from assignments.models import AssignmentSubmission


class Feedback(models.Model):
    submission = models.ForeignKey(AssignmentSubmission, on_delete=models.CASCADE)
    llm_feedback = models.TextField()
    instructor_feedback = models.TextField()
    date_provided = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.submission}"


class Evaluation(models.Model):
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE)
    rating = models.IntegerField()
    evaluation_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Evaluation {self.rating} on {self.evaluation_date}"
