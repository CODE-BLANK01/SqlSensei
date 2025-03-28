from django.db import models
from django.conf import settings


class Leaderboard(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    week = models.CharField(max_length=50)
    problems_solved = models.IntegerField()
    score = models.FloatField()

    def __str__(self):
        return f"{self.student} - Week {self.week} - Score {self.score}"


class ParticipationStreak(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    streak_count = models.IntegerField()

    def __str__(self):
        return f"{self.student} - Streak: {self.streak_count}"
