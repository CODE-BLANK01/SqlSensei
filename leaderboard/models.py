from django.db import models
from django.conf import settings
from users.models import User

class Leaderboard(models.Model):
    leaderboard_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(User,  on_delete=models.CASCADE)
    problems_solved = models.IntegerField(default=0)

    class Meta:
        db_table = 'Leaderboard'

    def __str__(self):
        return f"Leaderboard {self.leaderboard_id} - Student {self.student_id}"
