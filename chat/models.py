from django.db import models
from django.conf import settings
from courses.models import Course
from users.models import User


class Message(models.Model):
    id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='received_messages')
    message_content = models.TextField()
    message_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender.Full_Name} to {self.receiver.Full_Name} on {self.message_date}"
    
    class Meta:
        db_table = 'Messages'